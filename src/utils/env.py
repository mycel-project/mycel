import os

def is_testing():
    return "PYTEST_CURRENT_TEST" in os.environ
