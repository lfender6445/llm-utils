import os
import subprocess
from replace_text import ReplaceText


def language_prompt(lang):
    return f"You are an experienced {lang} engineer who provides full and robust code solutions wrapped in triple backticks. You do not omit any code for brevity"


custom_prompts = {
    "py": language_prompt("python"),
    "ruby": language_prompt("ruby"),
    "ts": language_prompt("typescript"),
    "js": language_prompt("javascript"),
    "fullstack": language_prompt("node + typescript + javascript"),
}


class Commands:
    def __init__(self, chatbot_instance):
        self.chatbot_instance = chatbot_instance

    def _get_ext(self, filename):
        if filename:
            ext = os.path.splitext(filename)[1][1:]
            return ext
        else:
            return "txt"

    def replace_code_block(self, replacement_text, filename):
        replacer = ReplaceText(filename)
        replacer.replace_between_comments(replacement_text, split=True)

    def create_file(self, codeblock, default_filename):
        out = self.chatbot_instance.input_with_arrows(
            f"❓ What is the filename you want to create? Press enter to use {default_filename}\n"
        )
        name = out or default_filename
        with open(name, "w") as file:
            file.write(codeblock)
            print(f"File {name} saved\n\n")

    def overwrite_file(self, codeblock, file_map):
        print("Files by index: ", file_map, "\n")
        out = self.chatbot_instance.input_with_arrows(
            f"❓ What is the file index you want to overwrite? "
        )
        file_match = file_map[int(out)]
        if file_match:
            with open(f"{file_match}", "a+") as file:
                ext = self._get_ext(file_match)
                file.write(f"{self.chatbot_instance.markers[ext]}\n")
                file.write(codeblock)
                print(f"✅ Appended to {file_match} successfully")

    def replace_file(self, codeblock, file_map):
        print("Files by index: ", file_map, "\n")
        selection = self.chatbot_instance.input_with_arrows(
            f"❓ What is the file index? "
        )
        file_match = file_map[int(selection)]
        name = file_match or f"{self.chatbot_instance.timestamp}.txt"
        self.replace_code_block(replacement_text=codeblock, filename=name)

    def append_file(self, codeblock, file_map, use_comments):
        print("Files by index: ", file_map, "\n")
        if bool(file_map):
            selection = self.chatbot_instance.input_with_arrows(
                "❓ What is the file index? "
            )
            file_match = file_map[int(selection)]
            if file_match:
                with open(f"{file_match}", "a+") as file:
                    ext = self._get_ext(file_match)
                    file.write(self.chatbot_instance.markers[ext])
                    if use_comments:
                        file.write("'''\n")
                    file.write(f"{codeblock}\n")
                    if use_comments:
                        file.write("\n'''\n")
                    print(f"\n✅ Appended to {file_match} successfully\n")
        else:
            print("Skipping operation, no file index")

    def help_text(self, codeblock, position):
        return f"""❓ Add Code Block? {position}

{codeblock}

💻 File System Operations:

- Type 'a' to append
- Type 'ac' to append within python comments
- Type 'cf' for create file
- Type 'n' for next code block eval
- Type 's' for skipping all evaluations
- Type 'c' for copy to clipboard
- Type 'r' for replace
- Type 'O' for overwrite

❗ Your choice: """

    def code_eval(self, result):
        chatbot_instance = self.chatbot_instance

        if not chatbot_instance.skip_file_edits_for_next_query:
            # NOTE: extractions only work for LEFT ALIGNED BACKTICKS without space
            file_map = {
                index: value
                for index, value in enumerate(chatbot_instance.args.files or [])
            }
            extractions = chatbot_instance.extract_code_blocks(result)
            count = len(extractions)
            print(f"Detected {count} codeblock(s)")
            print(chatbot_instance.delimiter)
            for index, codeblock in enumerate(extractions):
                position = f"Codeblock {index + 1} of {count}"
                out = chatbot_instance.input_with_arrows(
                    self.help_text(codeblock, position)
                )
                print(chatbot_instance.delimiter)
                if out == "c":
                    subprocess.run("pbcopy", text=True, input=codeblock)
                    continue
                if out == "n":
                    continue
                if out == "s":
                    return
                if out == "cf":
                    predicted_ext = self._get_ext(chatbot_instance.args.files[0])
                    default = f"{chatbot_instance.timestamp}.{predicted_ext}"
                    self.create_file(codeblock, default)
                if out == "o":
                    self.overwrite_file(codeblock, file_map)
                if out == "r":
                    self.replace_file(codeblock, file_map)
                if out == "a" or out == "ac":
                    use_comments = out[-1] == "c"
                    self.append_file(codeblock, file_map, use_comments)
            # print(chatbot_instance.delimiter)
