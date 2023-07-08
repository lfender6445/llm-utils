import unittest
import unittest.mock as mock
from conversate import Chatbot
from commands import Commands


extraction = "print('test')"

example_codeblock = f"""```
{extraction}
```"""

example_codeblock_2 = f"```{extraction}```"


class TestCommandsCodeEval(unittest.TestCase):
    def setUp(self):
        self.chatbot = Chatbot()
        self.commands = Commands(self.chatbot)
        self.chatbot.skip_file_edits_for_next_query = False
        # Mock input_with_arrows method
        self.chatbot.input_with_arrows = mock.Mock()

    def test_code_eval_calls_overwrite_file_o(self):
        # Set up the input mocks
        self.chatbot.input_with_arrows = mock.MagicMock(return_value="o")

        # Set up the overwrite_file method with a MagicMock to track when it is called
        self.commands.overwrite_file = mock.MagicMock()

        # Call code_eval with a sample codeblock and empty value mapping (for simplicity)
        value_mapping = {}
        self.commands.code_eval(example_codeblock)

        # Assert that overwrite_file was called once with the expected arguments
        self.commands.overwrite_file.assert_called_once_with(extraction, value_mapping)


if __name__ == "__main__":
    unittest.main()
