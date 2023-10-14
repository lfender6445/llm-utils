import re
import pprint
import subprocess
import socket
import errno
import time
import argparse
# import readline
import openai
import os
import datetime

from llama import Llama
from commands import Commands


def language_prompt(lang):
    return f"You are an experienced {lang} engineer who provides full and robust code solutions wrapped in triple backticks. You do not omit any code for brevity"


custom_prompts = {
    "py": language_prompt("python"),
    "ruby": language_prompt("ruby"),
    "ts": language_prompt("typescript"),
    "js": language_prompt("javascript"),
    "fullstack": language_prompt("node + typescript + javascript"),
}

import time

def rate_limit(seconds=5):
    def decorator(func):
        ## NOTE: array used instead of value to for scoping issues
        last_called = [0]

        def wrapper(*args, **kwargs):
            current_time = time.time()
            if current_time - last_called[0] < seconds:
                print("\n\nThis programs call rate limit was exceeded. Adding shortd delay out of caution...\n")
                time.sleep(4)
            last_called[0] = current_time
            return func(*args, **kwargs)

        return wrapper

    return decorator

class ToStruct(object):
    def __init__(self, initial_data):
        for key in initial_data:
            setattr(self, key, initial_data[key])


class MockResponse:
    def __init__(self):
        content = ""
        with open("./mock_response_multiple.txt", "r") as file:
            contents = file.read()
            for line in contents:
                content += line
        content = ToStruct(
            {
                "content": content,
            }
        )
        message = ToStruct({"message": content})
        self.latency = "mock latency"
        self.choices = [message]
        self.usage = {"prompt_tokens": 10, "total_tokens": 30}
        self.model = "mock model"
        self.eval_count = 0


class Chatbot:
    def __init__(self):
        self._bootstrap()
        self.skip_file_edits_for_next_query = False
        self.delimiter = "============\n"
        self.prompt = ""
        self.cost = ""
        self.running_total = 0
        self.markers = {
            "py": "##### >>>> BOT\n",
            "ts": "///// >>>> BOT\n",
            "tsx": "///// >>>> BOT\n",
            "js": "///// >>>> BOT\n",
        }
        self.send_count = 0
        self.messages = [
            {"role": "system", "content": self.system_prompt},
        ]
        self.eval_count = 0
        self.log_filename = f"{self.home}/source/llm-utils/logs/{self.timestamp}.md"
        # readline.parse_and_bind("set editing-mode vi")

    def _bootstrap(self):
        self.args = self._parse_arguments()
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("MODEL") or "gpt-3.5-turbo"
        self.home = os.getenv("HOME")
        self.timestamp = self._get_timestamp()
        self.system_prompt = self._get_sys_prompt()
        print(f"📝 {self.system_prompt}")
        print(self.help())

    def help(self):
        if (self.args.skip_fs):
            return "ℹ️  Skipping file ops\n"
        return "ℹ️  You can skip file operations by prefixing your prompt with `!` or with the --skip_fs option \n"

    # https://pythex.org/
    def _get_sys_prompt(self):
        prompt = ""
        if self.args.ext:
            prompt = custom_prompts[self.args.ext]
            if self.args.system_prompt:
                prompt += " " + self.args.system_prompt
        else:
            prompt = self.args.system_prompt
        return prompt or "You are a helpful chatbot"

    def _get_timestamp(self):
        # Get the current date and time
        now = datetime.datetime.now()

        # Format the date and time as a string with underscores separating different elements
        return now.strftime("%Y_%m_%d_%H_%M_%S")

    def _parse_arguments(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--mock",
            action="store_true",
            help="save money, avoid an api request, test script ops",
        )
        parser.add_argument(
            "--skip-logs",
            action="store_true",
            help="skip logging to disk",
        )
        parser.add_argument(
            "--llama",
            action="store_true",
            help="add llama response",
        )
        parser.add_argument(
            "--prompt",
            type=str,
            help="Supply and skip initial prompt",
        )
        parser.add_argument(
            "--speech",
            action="store_true",
            help="convert result to speech using tts.py",
        )
        parser.add_argument(
            "--system-prompt",
            type=str,
            help="system prompt. appended to existing ext prompts if present",
        )
        parser.add_argument(
            "--ext", type=str, help="Language specific prompts. file path"
        )


        parser.add_argument(
            "--verbose", action="store_true", help="Print additional info about cost and debug"
        )
        parser.add_argument(
            "--skip_fs", action="store_true", help="Disable fs operations for session"
        )
        parser.add_argument(
            "-f",
            "--files",
            action="append",
            type=str,
            help="List of filenames `-f foo.ts -f bar.ts`",
        )

        return parser.parse_args()

    def _log(self, msg, allow_print=True):
        if allow_print:
            print(msg)

        if not self.args.skip_logs:
            os.makedirs(os.path.dirname(self.log_filename), exist_ok=True)
            with open(self.log_filename, "a+") as myfile:
                myfile.write(msg)

    def stats(self, start, end, response):
        latency = end - start
        if self.args.verbose:
            print(f"# USAGE: \n")
            print(f"{response.usage}")
            print(f"- Latency: {latency}")
            print(f"- Model: {response.model}")
        prompt_cost = (response.usage["prompt_tokens"] / 1000) * 0.03
        completion_cost = (response.usage["total_tokens"] / 1000) * 0.06
        total_cost = prompt_cost + completion_cost
        self.running_total += total_cost
        self.cost = f"- Cost: {total_cost}\n- Total: {self.running_total}"
        if self.args.verbose:
            print(self.delimiter)
            print(self.cost)
            print(self.delimiter)

    @rate_limit(seconds=5)
    def chat(self):
        result = ""
        start = time.time()
        if self.args.mock:
            response = MockResponse()
        else:
            success = False

            while not success:
                try:
                    response = openai.ChatCompletion.create(
                        model=self.model, messages=self.messages
                    )

                    success = True
                except Exception as api_err:
                    subprocess.run("pbcopy", text=True, input=self.prompt)

                    print('An OpenAI API error occurred, last prompt has been copied to clipboard. Recoving prompt...\n' )

                    # pprint.pprint(dir(api_err))
                    pprint.pprint(api_err)
                    # pprint.pprint(dir(api_err.err))

                    should_try_again = input('\nWould you like to try again? y or n: ')
                    if should_try_again == 'y' or should_try_again == 'Y':
                        success = False
                    else:
                        raise api_err
                    # if e.errno != errno.ECONNRESET:
                    #     self._log('Connection reset, retrying: \n')
                    # Error communicating with OpenAI: ('Connection aborted.', OSError("(54, 'ECONNRESET')"))

        end = time.time()
        for choice in getattr(response, "choices", []):
            result += choice.message.content
        self.stats(start, end, response)
        self.messages.append({"role": "assistant", "content": result})
        self._log(f"🌸\n\n{result}\n")
        return result

    def _send(self):
        self.timestamp = self._get_timestamp()
        self._log(f"\n{self.timestamp} \n")
        self._log(self.delimiter)
        if self.args.llama and self.prompt:
            Llama(self.prompt).exec()
        result = self.chat()
        self.send_count += 1
        commands = Commands(self)
        commands.code_eval(result)
        if self.args.speech:
            self._tts(result)

    def _tts(self, result):
        subprocess.call(["python", "tts.py", "--text", result])

    def input_with_arrows(self, prompt):
        line = input(prompt)
        return line

    def files_prompt(self):
        # Get file contents and add them to the nprompt
        prompt = ""
        file_contents = []
        if self.args.files:
            for file_path in self.args.files:
                try:
                    with open(file_path, "r") as file:
                        content = f"# {file_path}\n{file.read().strip()}"
                        if content:
                            file_contents.append(content)
                except FileNotFoundError:
                    print(f"File '{file_path}' not found")

        if file_contents:
            prompt += "\n\nGiven this document:"
            for content in file_contents:
                prompt += f"\n\n{content}"

        if self.args.prompt:
            prompt += f"\n\n{prompt}"
        else:
            input = self.input_with_arrows("🌱 Prompt: ")
            prompt += input
        return prompt

    def extract_code_blocks(self, content):
        # Regular expression to match code blocks with triple backticks
        code_block_pattern = re.compile(
            r"```(?:[^`\n]*)\n([\s\S]*?)\n```", re.MULTILINE
        )
        code_blocks = code_block_pattern.findall(content)
        return code_blocks

    def process(self):
        files_added = False
        prompt = ""
        if self.eval_count == 0:
            if self.args.prompt:
                prompt = self.args.prompt
            show_input = not prompt
        else:
            show_input = True

        if not self.args.files and show_input:
            prompt = self.input_with_arrows("🌱 Prompt: ")

            if (not prompt):
                print('\nRejecting blank line, please supply prompt...\n')
                self.process()

            if prompt[0] == "!" or self.args.skip_fs:
                self.skip_file_edits_for_next_query = True
            else:
                self.skip_file_edits_for_next_query = False
        if self.args.files:
            if not files_added:
                print(f"🗂️  Loading into ctx: {self.args.files}\n")
                prompt = self.files_prompt()
                self.messages.append({"role": "user", "content": prompt})
                files_added = True

        if prompt == 'exit' or prompt == 'quit':
            exit(0)
        self.prompt = prompt
        self._log(f"\nPrompt: {prompt}", False)
        self.messages.append({"role": "user", "content": prompt})
        self._send()
        self.eval_count += 1
        print(f"✅ You have completed {self.send_count} requests for this session\n")
        print(f"✅ {self.cost}\n")

    def start(self):
        """
        Starts the chatbot loop, allowing the user to enter prompts and receive responses.
        If files are specified as arguments by the user, their contents are loaded into the conversation thread.
        Recognizes special user commands (e.g., 'exit', 'quit', '!') for program control.

        Loop structure:
        1. If files are specified, load their contents into the conversation thread.
        2. Prompt the user for input.
        3. Check if the provided input is a special command (e.g., 'exit', 'quit', '!'). If so, execute the command.
        4. Otherwise, send the user prompt to the GPT model and receive the response.
        5. Print the response and log the conversation.
        """
        while True:
            self.process()

def main():
    Chatbot().start()

if __name__ == "__main__":
    main()
