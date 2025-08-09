import pytest
import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from npd_csviper.csv_linter import CSVLinter
from npd_csviper.exceptions import CSVLintError, CSVLinterNotFound

# Mark all tests in this module as requiring csvlint
pytestmark = pytest.mark.skipif(not CSVLinter.is_csvlint_installed(), reason="csvlint is not installed")

INVALID_CSV_DIR = "test_data/invalid_csv_files"
VALID_CSV_DIR = "test_data/should_work_just_fine"

# Get a list of all invalid csv files, excluding non-csv files
invalid_csv_files = [
    os.path.join(INVALID_CSV_DIR, f)
    for f in os.listdir(INVALID_CSV_DIR)
    if f.endswith(".csv") and f not in ["extra_header.csv", "missing_header.csv"]
]

# Get a list of all valid csv files
valid_csv_files = [
    os.path.join(VALID_CSV_DIR, f)
    for f in os.listdir(VALID_CSV_DIR)
    if f.endswith(".csv")
]

# TODO These should not be caught by the csvlint but they should be caught by the compiler. 
valid_csv_files.extend([
    os.path.join(INVALID_CSV_DIR, "extra_header.csv"),
    os.path.join(INVALID_CSV_DIR, "missing_header.csv")
])


@pytest.mark.parametrize("csv_file", invalid_csv_files)
def test_lint_invalid_csv_files(csv_file):
    """
    Test that lint_csv_file raises CSVLintError for invalid CSV files.
    """
    with pytest.raises(CSVLintError):
        CSVLinter.lint_csv_file(csv_file_path=csv_file)


@pytest.mark.parametrize("csv_file", valid_csv_files)
def test_lint_valid_csv_files(csv_file):
    """
    Test that lint_csv_file runs without error for valid CSV files.
    """
    try:
        CSVLinter.lint_csv_file(csv_file_path=csv_file)
    except (CSVLintError, CSVLinterNotFound) as e:
        pytest.fail(f"lint_csv_file raised an unexpected exception: {e}")
