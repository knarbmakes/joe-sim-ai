import unittest
import json
from tools.bash import RunBashCommand

class TestRunBashCommand(unittest.TestCase):

    def test_echo_command(self):
        """Test the execution of a simple echo command."""
        args = {'command': 'echo "Hello, World!"'}
        expected_output = "Hello, World!"
        actual_result = RunBashCommand.run(args, None)
        actual_result_dict = json.loads(actual_result)
        self.assertEqual(actual_result_dict.get('output').strip(), expected_output)

    def test_awk_grep_echo_command(self):
        """Test the execution of a combined awk, grep, and echo command."""
        args = {'command': 'echo -e "one\ntwo\nthree" | grep "wo" | awk "{print $1}"'}
        expected_output = "two"
        actual_result = RunBashCommand.run(args, None)
        actual_result_dict = json.loads(actual_result)
        self.assertEqual(actual_result_dict.get('output').strip(), expected_output)

    def test_invalid_command(self):
        """Test the execution of an invalid command."""
        args = {'command': 'eccho "This is an invalid command"'}
        actual_result = RunBashCommand.run(args, None)
        actual_result_dict = json.loads(actual_result)
        self.assertNotEqual(actual_result_dict.get('status'), 0)

    def test_invalid_arguments(self):
        """Test with invalid arguments."""
        args = {'invalid_key': 'echo "This should fail"'}
        actual_result = RunBashCommand.run(args, None)
        print('actual_result', actual_result)
        self.assertIn('error', actual_result)

    def test_command_timeout(self):
        """Test a command that should time out."""
        args = {'command': 'sleep 10', 'timeout': 0.1}
        actual_result = RunBashCommand.run(args, None)
        self.assertIn('Command timed out', actual_result)

    def test_max_output_length(self):
        """Test the truncation of output longer than MAX_OUTPUT_LENGTH."""
        bash_command = "i=0; while [ $i -lt " + str(RunBashCommand.MAX_OUTPUT_LENGTH + 100) + " ]; do echo -n 'x'; i=$((i+1)); done"
        args = {'command': bash_command}
        actual_result = RunBashCommand.run(args, None)
        actual_result_dict = json.loads(actual_result)
        self.assertTrue(actual_result_dict.get('truncated'))
        # Checking if the output is truncated to MAX_OUTPUT_LENGTH
        self.assertEqual(len(actual_result_dict.get('output')), RunBashCommand.MAX_OUTPUT_LENGTH)

    def test_max_input_length(self):
        """Test the handling of command longer than MAX_INPUT_LENGTH."""
        long_string = "echo '" + "x" * (RunBashCommand.MAX_INPUT_LENGTH + 100) + "'"
        args = {'command': long_string}
        actual_result = RunBashCommand.run(args, None)
        self.assertIn('error', actual_result)

if __name__ == '__main__':
    unittest.main()
