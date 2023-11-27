import unittest
import os

class QuietTestResult(unittest.TextTestResult):
    def addSuccess(self, test):
        pass

    def printErrors(self):
        self.printErrorList('ERROR', self.errors)
        self.printErrorList('FAIL', self.failures)

if __name__ == "__main__":
    # Define the directory containing tests
    test_dir = os.path.join(os.path.dirname(__file__), 'tests')
    
    # Discover and run tests
    suite = unittest.TestLoader().discover(start_dir=test_dir, pattern="test_*.py")
    runner = unittest.TextTestRunner(resultclass=QuietTestResult)
    runner.run(suite)
