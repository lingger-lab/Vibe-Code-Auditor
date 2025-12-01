"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    # Cleanup
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


@pytest.fixture
def sample_python_file(temp_project_dir):
    """Create a sample Python file for testing."""
    file_path = temp_project_dir / "sample.py"
    file_path.write_text("""
def hello_world():
    print("Hello, World!")

class SampleClass:
    def __init__(self):
        self.value = 42
""")
    return file_path


@pytest.fixture
def sample_project(temp_project_dir):
    """Create a sample project with multiple files."""
    # Python files
    (temp_project_dir / "main.py").write_text("""
def main():
    print("Main function")

if __name__ == "__main__":
    main()
""")

    (temp_project_dir / "utils.py").write_text("""
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b
""")

    # Create subdirectory
    sub_dir = temp_project_dir / "module"
    sub_dir.mkdir()

    (sub_dir / "__init__.py").write_text("")
    (sub_dir / "helpers.py").write_text("""
def helper_function():
    return "Helper"
""")

    # Create requirements.txt
    (temp_project_dir / "requirements.txt").write_text("""
pytest==7.4.3
requests==2.31.0
""")

    return temp_project_dir


@pytest.fixture
def mock_analysis_results():
    """Mock analysis results for testing reporters."""
    return {
        'mode': 'deployment',
        'languages': ['python'],
        'issues': [
            {
                'tool': 'pylint',
                'file': 'test.py',
                'line': 10,
                'severity': 'warning',
                'message': 'Test warning',
                'symbol': 'test-symbol',
                'message_id': 'W001'
            },
            {
                'tool': 'pylint',
                'file': 'test.py',
                'line': 20,
                'severity': 'info',
                'message': 'Test info',
                'symbol': 'test-info',
                'message_id': 'I001'
            }
        ],
        'summary': {
            'total_issues': 2,
            'by_severity': {
                'critical': 0,
                'warning': 1,
                'info': 1
            }
        }
    }


@pytest.fixture
def mock_ai_results():
    """Mock AI analysis results for testing."""
    return {
        'mode': 'deployment',
        'issues': [
            {
                'severity': 'critical',
                'title': 'Security Issue',
                'details': ['SQL injection vulnerability detected']
            }
        ],
        'summary': {
            'total_issues': 1,
            'by_severity': {
                'critical': 1,
                'warning': 0,
                'info': 0
            }
        }
    }
