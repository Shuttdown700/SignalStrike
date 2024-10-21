import unittest

# ANSI color codes for text
RESET = "\033[0m"
GREEN = "\033[32m"
RED = "\033[31m"

class ColoredTextTestResult(unittest.TextTestResult):
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.success_count = 0
        self.failure_count = 0

    def addSuccess(self, test):
        super().addSuccess(test)
        self.success_count += 1
        print(f"\n{GREEN}Test passed: {str(test).split()[0]}{RESET}")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.failure_count += 1
        print(f"{RED}Test failed: {test}{RESET}")

    def addError(self, test, err):
        super().addError(test, err)
        self.failure_count += 1
        print(f"{RED}Test errored: {test}{RESET}")

    def stop(self):
        print("Stopping test execution...")
        super().stop()
        # Print the results summary here
        self.printResults()

    def printResults(self):
        total_tests = self.success_count + self.failure_count
        if total_tests > 0:
            success_percentage = (self.success_count / total_tests) * 100
        else:
            success_percentage = 0
        print(f"\n{GREEN}Total Tests: {total_tests}{RESET}")
        print(f"{GREEN}Successful Tests: {self.success_count}{RESET}")
        print(f"{RED}Failed Tests: {self.failure_count}{RESET}")
        print(f"{GREEN}Success Percentage: {success_percentage:.2f}%{RESET}")

class ColoredTextTestRunner(unittest.TextTestRunner):
    resultclass = ColoredTextTestResult
    def run(self, test):
        # Call the original run method
        result = super().run(test)
        # Call printResults after running the tests
        result.printResults()  # Ensure results are printed
        return result
