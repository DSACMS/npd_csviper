#!/usr/bin/env python3
"""
Automated New Import Script Generator

This script automates the instructions found in AI_Instruction/HowToDoANewImport.md 
It accepts two arguments: 
--input_dir - the input directory to read csv files from
--parent_output_dir - the parent directory of the new import directories that will be created by the script

The script will read all of the csv files in the import_dir and then repeat the following loop for each one: 

* Ask user: Do you want to import this csv? (if no skip to the next csv)
* Ask user: What is the directory name of this import (this will be the name of the directory that is created for this csv input under parent_output_dir and will contain all further outputs)
* Ask user: What is the schema you would like to output this to: 
* Ask user: What is the table you would like to output this to: 
* creates the new output subdirectory under parent_output_dir
* Run the 3 npd_csviper steps (see data_import_scripts/compile_clia_pos.py for an example) into the new 
* print the additional lines that should be added to data_import_scripts/data_file_locations.env to a new file called "add_to_data_file_locations.txt" and put it in the new sub-directory
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Optional


def find_csv_files(input_dir: str) -> List[Path]:
    """
    Find all CSV files in the input directory (non-recursive).
    
    Args:
        input_dir: Directory to search for CSV files
        
    Returns:
        List of Path objects for CSV files found
    """
    input_path = Path(input_dir)
    
    if not input_path.exists():
        print(f"Error: Input directory '{input_dir}' does not exist")
        sys.exit(1)
    
    if not input_path.is_dir():
        print(f"Error: '{input_dir}' is not a directory")
        sys.exit(1)
    
    csv_files = list(input_path.glob("*.csv"))
    
    if not csv_files:
        print(f"Warning: No CSV files found in '{input_dir}'")
    
    return sorted(csv_files)


def generate_env_prefix(directory_name: str) -> str:
    """
    Generate environment variable prefix from directory name.
    Converts to SCREAMING_SNAKE_CASE.
    
    Args:
        directory_name: The directory name for the import
        
    Returns:
        Uppercase environment variable prefix
    """
    # Replace hyphens and spaces with underscores, then uppercase
    prefix = directory_name.replace("-", "_").replace(" ", "_").upper()
    return prefix


def ask_user_questions(csv_file: Path) -> Optional[Dict[str, str]]:
    """
    Ask user interactive questions about the CSV import.
    
    Args:
        csv_file: Path to the CSV file
        
    Returns:
        Dictionary with user responses, or None if user skips this CSV
    """
    print(f"\n{'='*60}")
    print(f"CSV File: {csv_file.name}")
    print(f"Full Path: {csv_file}")
    print(f"{'='*60}")
    
    # Ask if user wants to import this CSV
    while True:
        response = input("Do you want to import this CSV? [y/n]: ").strip().lower()
        if response in ['y', 'yes']:
            break
        elif response in ['n', 'no']:
            print("Skipping this CSV file.\n")
            return None
        else:
            print("Please enter 'y' or 'n'")
    
    # Ask for directory name
    while True:
        directory_name = input("What is the directory name for this import? ").strip()
        if directory_name:
            break
        print("Directory name cannot be empty. Please try again.")
    
    # Ask for schema name
    while True:
        schema_name = input("What is the schema name for this table? ").strip()
        if schema_name:
            break
        print("Schema name cannot be empty. Please try again.")
    
    # Ask for table name
    while True:
        table_name = input("What is the table name? ").strip()
        if table_name:
            break
        print("Table name cannot be empty. Please try again.")
    
    return {
        'directory_name': directory_name,
        'schema_name': schema_name,
        'table_name': table_name
    }


def run_npd_csviper_steps(csv_path: Path, output_dir: Path) -> bool:
    """
    Run the 3 npd_csviper compilation steps.
    
    Args:
        csv_path: Path to the CSV file
        output_dir: Output directory for generated files
        
    Returns:
        True if all steps succeeded, False otherwise
    """
    # Calculate metadata path
    csv_filename = csv_path.stem  # filename without extension
    metadata_path = output_dir / f"{csv_filename}.metadata.json"
    
    # Define the 3 npd_csviper commands
    commands = [
        # Step 1: Extract metadata
        [
            "npd_csviper", "extract-metadata",
            f"--from_csv={csv_path}",
            f"--output_dir={output_dir}"
        ],
        # Step 2: Build SQL
        [
            "npd_csviper", "build-sql",
            f"--from_metadata_json={metadata_path}",
            f"--output_dir={output_dir}"
        ],
        # Step 3: Build import script
        [
            "npd_csviper", "build-import-script",
            f"--from_resource_dir={output_dir}",
            f"--output_dir={output_dir}",
            "--overwrite_previous"
        ]
    ]
    
    # Execute each command
    for i, cmd in enumerate(commands, 1):
        print(f"\nRunning step {i}/3: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"✓ Step {i} completed successfully")
            if result.stdout:
                print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"✗ Step {i} failed with error:")
            print(e.stderr)
            return False
        except FileNotFoundError:
            print(f"✗ Error: 'npd_csviper' command not found. Is it installed?")
            print("Install with: pip install npd_csviper")
            return False
    
    return True


def calculate_relative_csv_path(csv_path: Path, parent_output_dir: Path) -> str:
    """
    Calculate the relative path from data_import_scripts/ to the CSV file.
    
    Args:
        csv_path: Absolute or relative path to CSV file
        parent_output_dir: Parent output directory (typically data_import_scripts/)
        
    Returns:
        Relative path string suitable for data_file_locations.env
    """
    try:
        # Try to calculate relative path
        csv_abs = csv_path.resolve()
        output_abs = parent_output_dir.resolve()
        rel_path = os.path.relpath(csv_abs, output_abs)
        return rel_path
    except ValueError:
        # If on different drives (Windows), use absolute path
        return str(csv_path)


def generate_env_entries(
    directory_name: str,
    csv_path: Path,
    schema_name: str,
    table_name: str,
    parent_output_dir: Path
) -> str:
    """
    Generate environment variable entries for data_file_locations.env.
    
    Args:
        directory_name: Directory name for the import
        csv_path: Path to the CSV file
        schema_name: Database schema name
        table_name: Database table name
        parent_output_dir: Parent output directory
        
    Returns:
        String containing environment variable entries
    """
    env_prefix = generate_env_prefix(directory_name)
    csv_filename = csv_path.stem  # filename without extension
    
    # Calculate relative CSV path
    relative_csv_path = calculate_relative_csv_path(csv_path, parent_output_dir)
    
    # Generate the environment variable entries
    entries = f"""# {directory_name} import
{env_prefix}_CSV={relative_csv_path}
{env_prefix}_DIR=./{directory_name}/
{env_prefix}_SCHEMA={schema_name}
{env_prefix}_TABLE={table_name}
{env_prefix}_METADATA=./{directory_name}/{csv_filename}.metadata.json
"""
    
    return entries


def process_csv_file(
    csv_file: Path,
    parent_output_dir: Path
) -> bool:
    """
    Process a single CSV file through the complete import workflow.
    
    Args:
        csv_file: Path to the CSV file
        parent_output_dir: Parent directory for output
        
    Returns:
        True if processing succeeded, False otherwise
    """
    # Ask user questions
    user_input = ask_user_questions(csv_file)
    if user_input is None:
        return True  # User chose to skip, not an error
    
    directory_name = user_input['directory_name']
    schema_name = user_input['schema_name']
    table_name = user_input['table_name']
    
    # Create output directory
    output_dir = parent_output_dir / directory_name
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n✓ Created output directory: {output_dir}")
    except Exception as e:
        print(f"✗ Error creating output directory: {e}")
        return False
    
    # Run npd_csviper steps
    print(f"\nRunning npd_csviper compilation steps...")
    if not run_npd_csviper_steps(csv_file, output_dir):
        print(f"✗ Failed to compile import for {csv_file.name}")
        return False
    
    # Generate environment variable entries
    env_entries = generate_env_entries(
        directory_name,
        csv_file,
        schema_name,
        table_name,
        parent_output_dir
    )
    
    # Write to add_to_data_file_locations.txt
    env_file = output_dir / "add_to_data_file_locations.txt"
    try:
        with open(env_file, 'w') as f:
            f.write(env_entries)
        print(f"\n✓ Generated environment variables in: {env_file}")
        print("\nEnvironment variable entries:")
        print("-" * 60)
        print(env_entries)
        print("-" * 60)
    except Exception as e:
        print(f"✗ Error writing environment file: {e}")
        return False
    
    print(f"\n✓ Successfully completed import setup for {csv_file.name}")
    return True


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Automate new data import setup using npd_csviper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  python make_new_import.py --input_dir ../local_data/new_data --parent_output_dir ../data_import_scripts

This will:
  1. Find all CSV files in the input directory
  2. Interactively prompt for import details
  3. Run npd_csviper to generate import infrastructure
  4. Create environment variable entries for data_file_locations.env
        """
    )
    
    parser.add_argument(
        '--input_dir',
        required=True,
        help='Directory containing CSV files to import'
    )
    
    parser.add_argument(
        '--parent_output_dir',
        required=True,
        help='Parent directory where import subdirectories will be created (typically data_import_scripts/)'
    )
    
    args = parser.parse_args()
    
    # Convert to Path objects
    input_dir = Path(args.input_dir)
    parent_output_dir = Path(args.parent_output_dir)
    
    # Ensure parent output directory exists
    if not parent_output_dir.exists():
        print(f"Creating parent output directory: {parent_output_dir}")
        parent_output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find CSV files
    print(f"Scanning for CSV files in: {input_dir}")
    csv_files = find_csv_files(str(input_dir))
    
    if not csv_files:
        print("No CSV files found. Exiting.")
        sys.exit(0)
    
    print(f"Found {len(csv_files)} CSV file(s)")
    
    # Process each CSV file
    successes = 0
    failures = 0
    skipped = 0
    
    for csv_file in csv_files:
        result = process_csv_file(csv_file, parent_output_dir)
        if result:
            successes += 1
        else:
            failures += 1
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total CSV files processed: {len(csv_files)}")
    print(f"Successfully processed: {successes}")
    print(f"Failed: {failures}")
    print("\nNext steps:")
    print("1. Review the generated add_to_data_file_locations.txt files")
    print("2. Manually add the entries to data_import_scripts/data_file_locations.env")
    print("3. Test the imports by running the generated go.postgresql.py scripts")
    print("="*60)
    
    sys.exit(0 if failures == 0 else 1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
