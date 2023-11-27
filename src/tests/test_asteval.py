import unittest
from tools.asteval import AstEval

class TestAstEval(unittest.TestCase):

    def test_evaluation(self):
        """Test the evaluation of a simple expression."""
        args = {'expression': '2 + 3'}
        expected_result = 5
        actual_result = AstEval.run(args, None)
        self.assertEqual(actual_result, f'{{"result": {expected_result}}}')

    def test_invalid_expression(self):
        """Test the handling of an invalid expression."""
        args = {'expression': '2 +'}
        actual_result = AstEval.run(args, None)
        self.assertIn('error', actual_result)

if __name__ == '__main__':
    unittest.main()
