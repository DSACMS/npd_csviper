# make_new_import.py - Automated Import Setup Tool

## Overview

The `make_new_import.py` script automates the process of setting up new data imports for the npd_Puffin project. It follows the manual instructions documented in `AI_Instruction/HowToDoANewImport.md` but automates the repetitive steps.

## What It Does

For each CSV file in a specified input directory, the script:

1. **Prompts the user** for import configuration (directory name, schema, table name)
2. **Checks** if the target directory already exists and prompts for overwrite confirmation
3. **Creates** the necessary directory structure
4. **Runs** the three npd_csviper compilation steps (with `--no-csv-lint` flag):
   - `extract-metadata` - Analyzes the CSV and creates metadata JSON
   - `build-sql` - Generates SQL table creation scripts
   - `build-import-script` - Creates the import execution script (go.postgresql.py)
5. **Generates** environment variable entries for `data_file_locations.env`
6. **Saves** the environment variables to `add_to_data_file_locations.txt` in each import directory

## Prerequisites

- Python 3.7+
- `npd_csviper` installed and available in PATH
  ```bash
  pip install npd_csviper
  ```

## Usage

### Basic Command

```bash
python misc_scripts/make_new_import.py \
  --input_dir ../local_data/your_data_directory \
  --parent_output_dir data_import_scripts
```

### Arguments

- `--input_dir` (required): Directory containing CSV files to import
- `--parent_output_dir` (required): Parent directory where import subdirectories will be created (typically `data_import_scripts/`)

### Interactive Prompts

For each CSV file found, you'll be asked:

1. **"Do you want to import this CSV? [y/n]"**
   - Enter `y` or `yes` to proceed
   - Enter `n` or `no` to skip this file

2. **"What is the directory name for this import?"**
   - This becomes the subdirectory name under `parent_output_dir`
   - Example: `my_new_import`
   - **If the directory already exists**, you'll be prompted with:
     - **"Do you want to overwrite its contents? [y/N]"**
     - Default is **No** - just press Enter to skip and preserve the existing directory
     - Type `y` to proceed with overwriting the existing directory

3. **"What is the schema name for this table?"**
   - Database schema where the table will be created
   - Example: `my_data_bronze` (consider using `_bronze`, `_silver`, or `_gold` suffixes)

4. **"What is the table name?"**
   - Name of the database table
   - Example: `my_data_table`

## Example Workflow

```bash
# Navigate to the misc_scripts directory
cd misc_scripts

# Run the script
python make_new_import.py \
  --input_dir ../local_data/new_medicare_data \
  --parent_output_dir ../data_import_scripts
```

### Example Session

```
Scanning for CSV files in: ../local_data/new_medicare_data
Found 2 CSV file(s)

============================================================
CSV File: provider_data_2025.csv
Full Path: /path/to/local_data/new_medicare_data/provider_data_2025.csv
============================================================
Do you want to import this CSV? [y/n]: y
What is the directory name for this import? medicare_provider_2025
What is the schema name for this table? medicare_bronze
What is the table name? provider_2025

✓ Created output directory: ../data_import_scripts/medicare_provider_2025

Running npd_csviper compilation steps...

Running step 1/3: npd_csviper extract-metadata --from_csv=...
✓ Step 1 completed successfully

Running step 2/3: npd_csviper build-sql --from_metadata_json=...
✓ Step 2 completed successfully

Running step 3/3: npd_csviper build-import-script --from_resource_dir=...
✓ Step 3 completed successfully

✓ Generated environment variables in: ../data_import_scripts/medicare_provider_2025/add_to_data_file_locations.txt

Environment variable entries:
------------------------------------------------------------
# medicare_provider_2025 import
MEDICARE_PROVIDER_2025_CSV=../local_data/new_medicare_data/provider_data_2025.csv
MEDICARE_PROVIDER_2025_DIR=./medicare_provider_2025/
MEDICARE_PROVIDER_2025_SCHEMA=medicare_bronze
MEDICARE_PROVIDER_2025_TABLE=provider_2025
MEDICARE_PROVIDER_2025_METADATA=./medicare_provider_2025/provider_data_2025.metadata.json
------------------------------------------------------------

✓ Successfully completed import setup for provider_data_2025.csv
```

## Output Structure

After running, you'll have:

```
data_import_scripts/
└── your_import_name/
    ├── your_csv_file.metadata.json          # CSV metadata
    ├── create_table_postgres.sql            # Table creation SQL
    ├── import_data_postgres.sql             # Data import SQL
    ├── go.postgresql.py                     # Import execution script
    └── add_to_data_file_locations.txt       # Environment variables to add
```

## Next Steps After Running

1. **Review** the generated `add_to_data_file_locations.txt` file in each import directory

2. **Manually add** the environment variable entries to `data_import_scripts/data_file_locations.env`:
   ```bash
   # Copy the contents of add_to_data_file_locations.txt
   cat data_import_scripts/your_import_name/add_to_data_file_locations.txt >> data_import_scripts/data_file_locations.env
   ```

3. **Test** the import by running the generated script:
   ```bash
   cd data_import_scripts/your_import_name
   python go.postgresql.py --help
   ```

4. **Create a compile script** (optional) for reproducibility:
   ```bash
   # See compile_clia_pos.py or compile_nucc.py as examples
   ```

## Environment Variable Naming Convention

The script automatically generates environment variable names from your directory name:

- Directory: `my_new_import` → Prefix: `MY_NEW_IMPORT_`
- Directory: `clia-pos` → Prefix: `CLIA_POS_`

Generated variables:
- `{PREFIX}_CSV` - Path to the CSV file
- `{PREFIX}_DIR` - Path to the import directory
- `{PREFIX}_SCHEMA` - Database schema name
- `{PREFIX}_TABLE` - Database table name
- `{PREFIX}_METADATA` - Path to metadata JSON

## Schema Naming Conventions

Consider these common schema naming patterns used in the project:

- `{name}_bronze` - Raw, unprocessed data (landing zone)
- `{name}_silver` - Cleaned, validated data
- `{name}_gold` - Aggregated, business-ready data
- `dctnry_bronze/silver/gold` - Dictionary/reference data
- `lantern_bronze` - External lantern data
- `pecos_bronze` - PECOS enrollment data

## Troubleshooting

### "npd_csviper command not found"

Install npd_csviper:
```bash
pip install npd_csviper
```

### "No CSV files found"

Verify:
- The input directory path is correct
- The directory contains `.csv` files (case-sensitive)
- You have read permissions for the directory

### CSV Processing Fails

Check:
- CSV file is well-formed (no encoding issues)
- CSV file is not empty
- CSV has a header row

### Permission Errors

Ensure you have write permissions for the parent_output_dir:
```bash
ls -la data_import_scripts/
```

## Related Documentation

- `AI_Instruction/HowToDoANewImport.md` - Manual import instructions
- `AI_Instruction/PlainerflowTools.md` - npd_plainerflow framework guide
- `data_import_scripts/compile_clia_pos.py` - Example compile script
- `data_import_scripts/compile_nucc.py` - Example compile script with multiple files

## Script Internals

### Key Functions

- `find_csv_files()` - Discovers CSV files in input directory
- `ask_user_questions()` - Interactive prompts for configuration
- `run_npd_csviper_steps()` - Executes the 3 compilation steps
- `generate_env_entries()` - Creates environment variable text
- `process_csv_file()` - Main workflow orchestration

### Exit Codes

- `0` - Success (all files processed successfully)
- `1` - Failure (one or more files failed to process)

## Contributing

When modifying this script:

1. Follow the existing code style
2. Update this README if changing functionality
3. Test with various CSV file types
4. Consider edge cases (empty files, special characters, etc.)

## Directory Overwrite Example

When running the script on an existing import directory, you'll see:

```
CSV File: provider_data_2025.csv
Full Path: /path/to/local_data/new_medicare_data/provider_data_2025.csv
Do you want to import this CSV? [y/n]: y
What is the directory name for this import? medicare_provider_2025

⚠️  Directory 'medicare_provider_2025' already exists at: ../data_import_scripts/medicare_provider_2025
Do you want to overwrite its contents? [y/N] (default: N): 
Skipping this CSV file to preserve existing directory.
```

Simply pressing Enter (or typing 'n') will skip the file and preserve your existing work. Type 'y' only if you want to regenerate the import files.

## Version History

- v1.1.0 (2025-01-21) - Overwrite protection and linting improvements
  - Added directory existence check with overwrite confirmation
  - Default to preserving existing directories (press Enter to skip)
  - Added `--no-csv-lint` flag to all npd_csviper commands
  - Improved user experience for re-running imports
  
- v1.0.0 (2025-01-21) - Initial implementation
  - Automated CSV discovery and processing
  - Interactive configuration prompts
  - npd_csviper integration
  - Environment variable generation
