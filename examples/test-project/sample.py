"""Sample Python file for testing."""

def calculate_total(items):
    total = 0
    for item in items:
        total = total + item
    return total

def unused_function():
    """This function is never called."""
    pass

class SampleClass:
    def __init__(self, name):
        self.name = name

    def get_name(self):
        return self.name
