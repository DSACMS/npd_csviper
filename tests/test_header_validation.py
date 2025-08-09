import pytest
import os
import shutil
import subprocess

# Define test directories
TEST_OUTPUT_DIR = "test_output/header_test"
INVALID_HEADER_CSVS = [
    "test_data/invalid_csv_files/extra_header.csv",
    "test_data/invalid_csv_files/missing_header.csv"
]

@pytest.fixture(scope="module")
def setup_teardown():
    """
    Set up the test environment by creating a clean output directory,
    and clean up afterward.
    """
    # Setup: create a clean output directory
    if os.path.exists(TEST_OUTPUT_DIR):
        shutil.rmtree(TEST_OUTPUT_DIR)
    os.makedirs(TEST_OUTPUT_DIR)

    yield

    # Teardown: remove the output directory
    shutil.rmtree(TEST_OUTPUT_DIR)


@pytest.mark.parametrize("invalid_csv", INVALID_HEADER_CSVS)
def test_full_compile_fails_on_inconsistent_columns(invalid_csv, setup_teardown):
    """
    Test that full-compile fails when the CSV has inconsistent column counts.
    """
    result = subprocess.run(
        [
            "python3",
            "-m",
            "npd_csviper",
            "full-compile",
            "--from_csv",
            invalid_csv,
            "--output_dir",
            TEST_OUTPUT_DIR,
            "--overwrite_previous",
            "--no-csv-lint"
        ],
        capture_output=True,
        text=True
    )
    
    assert result.returncode != 0
    assert "Inconsistent column count" in result.stdout
