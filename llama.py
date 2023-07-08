import subprocess
import os


class Llama:
    def __init__(self, prompt):
        self.prompt = prompt
        self.model = "llama"
        self.home = os.getenv("HOME")
        self.delim = "------"

    def prompt_instruct(self, instruction):
        return f"""Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Response:
"""

    def prompt_reflect(self):
        return """You are a you curious man making small talk with another woman on the elevator. Here is an example dialogue:

MAN: How is your day going?
WOMAN: My day is going well. 
MAN: That is fantastic news. My day is also going well.
WOMAN: I am so glad to hear that. 
MAN: 

Please continue the dialog as MAN. When WOMAN asks a question, man should answer. When WOMAN makes a statement, MAN should respond with a question.
  """

    def prompt_begin_reflect_answer(self):
        return """You are a you woman making small talk with another man on the elevator. Here is an example dialogue
MAN: How is your day going?
WOMAN: My day is going well. 
MAN: That is fantastic news. My day is also going well.
WOMAN: 

Please continue the dialog as WOMAN. When MAN asks a question, WOMAN should answer. When MAN makes a statement, WOMAN should respond with a question of their own.
  """

    def exec(self):
        print(self.delim)
        print("🦙 <Llama>\n")
        cwd = os.getcwd()
        os.chdir(cwd)
        cmd = [
            f"{self.home}/dalai/alpaca/main",
            "--seed -1",
            "--threads 4",
            "--n_predict 400",
            f"--model {self.home}/dalai/alpaca/models/7B/ggml-model-q4_0.bin",
            "--top_k 40",
            "--top_p 0.9",
            "--temp 0.8",
            "--repeat_last_n 64",
            "--repeat_penalty 1.3",
            f'-p "{self.prompt}"',
        ]
        single = " ".join(cmd)
        print("Executing: \n", single)
        p = subprocess.Popen(single, shell=True)
        exit_code = p.wait()
        print("exit code: ", exit_code)
        print("🦙  </Llama>\n")
        print(self.delim)

    def reflect(self):
        print("luke")
        return self.exec(self.prompt_reflect())


def main():
    print("running llama")
    Llama("").reflect()


if __name__ == "__main__":
    main()
