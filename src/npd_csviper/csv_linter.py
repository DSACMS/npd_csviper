#!/usr/bin/env python3
"""
This module provides a class to lint CSV files using the csvlint tool.
"""

import subprocess
import shutil
from .exceptions import CSVLinterNotFound, CSVLintError

class CSVLinter:
    """
    A class to lint CSV files using the csvlint tool.
    """

    @staticmethod
    def is_csvlint_installed():
        """
        Check if the csvlint command-line tool is installed.
        """
        return shutil.which("csvlint") is not None

    @staticmethod
    def lint_csv_file(*, csv_file_path: str):
        """
        Lint a CSV file using the csvlint command-line tool.
        """
        if not CSVLinter.is_csvlint_installed():
            raise CSVLinterNotFound("csvlint is not installed. Please install it from https://github.com/Data-Liberation-Front/csvlint.rb")

        try:
            process = subprocess.run(
                ["csvlint", csv_file_path],
                capture_output=True,
                text=True,
                check=True
            )
            output = process.stdout
            if "INVALID" in output:
                raise CSVLintError(f"CSV file is invalid: {output}")

            warnings_to_treat_as_errors = [
                ":empty_column_name",
                ":duplicate_column_name",
                ":title_row"
            ]

            for warning in warnings_to_treat_as_errors:
                if warning in output:
                    raise CSVLintError(f"CSV file has a critical warning that is treated as an error: {warning}")

        except subprocess.CalledProcessError as e:
            output = e.stdout
            if "INVALID" in output:
                raise CSVLintError(f"CSV file is invalid: {output}")

            warnings_to_treat_as_errors = [
                ":empty_column_name",
                ":duplicate_column_name",
                ":title_row"
            ]

            for warning in warnings_to_treat_as_errors:
                if warning in output:
                    raise CSVLintError(f"CSV file has a critical warning that is treated as an error: {warning}")
            
            # If it's not an error we care about, we can ignore it.
            # The command can exit with a non-zero status for warnings we don't care about.
            pass
