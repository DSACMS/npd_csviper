# npd_csviper

npd_csviper is a command-line tool that automates the process of analyzing CSV files and generating SQL scripts and Python programs to load the data into PostgreSQL databases. 
It is designed to allow AI tools to reliably accomplish this task without incurring substantial data pipeline debt. 

This is *not* a project that imports CSV files. It is a project that generates programs which import CSV files.

## Approach and Purpose

Importing CSV files is a simple chore initially, but maintaining CSV imports over time is much more difficult. 
As CSV files envitably change, simple scripts continue to function, despite underlying data changes that should be accounted for.
This project is designed to enable AI code-gen tools to successfully create CSV data imports, data expectations, documentation and post-processing in a manner convenient for human validation.

When a CSV file is imported into the database, without attention to how the underlying data might have changed, this introduces a pernicous form of technical debt
alled Data Pipeline Debt, which was a term coined by the 
[2018 version of an article](https://web.archive.org/web/20201027032456/https://greatexpectations.io/blog/down-with-pipeline-debt-introducing-great-expectations/) from the [Great Expectations](https://greatexpectations.io/) project. (The [later edition of the same article](https://greatexpectations.io/blog/down-with-pipeline-debt-introducing-great-expectations/) is worth reading too, but the first version articulates the problem more concisely).
An interesting tidbit is that the Great Expectations project was founded by a team of Health IT developers, who were experiencing the same unreasonable data environment that we have here at CMS. 

A proper CSV import process does not create Data Pipeline Debt by: 

* For all features, tries to Fail safely. Rather than importing data that might be a problem or that does not pass expectations, the code will fail in a way that forces users to pay attention when a given CSV file changes underneath them. 
* Ensuring that data expectation tests are always designed and run alongside the data import and that those expectation tests: 
* Ensure that column lengths are not changing. This requires that columns are given +1 the data size they need to see if the underlying data ever fills the last character (it should not)
* Addresses character set inconsistencies up-front
* Seperates the parameters for data import from the execution of that data import so the import parameters can be modifies as a seperate code-based
* Allows for AI tools to auto-generation of import code, based on CSV contents, but subsequent code generation should not trample any person-tweaked code.
* Supports importing to remote databases
* Auto-creates database safe column names and maintains the mapping between the database safe column names and the database names.
* Fails safely if the column names change.
* Fails safely if the column names are added.
* Provides support for post-processing scripts and raw-sql


It supports PostgreSQL and is designed for scenarios where the database is hosted remotely while the CSV file resides on the local machine.

## Features

- **CSV Analysis**: Automatically detects CSV format (delimiter, quote character) and analyzes column structure
- **Column Normalization**: Converts column names to SQL-safe identifiers with intelligent duplicate handling
- **Modular Design**: Four-phase approach allows for flexible workflow management
- **Standalone Scripts**: Generates self-contained Python import scripts for easy deployment
- **Intelligent File Discovery**: Invoker system automatically finds and processes the latest matching data files
- **Pattern-Based Matching**: Uses glob patterns to handle timestamped or versioned file naming conventions
- **Full Compilation Workflow**: Single command to process CSV files from analysis to ready-to-run import scripts

## Installation

### Prerequisites

- Python 3.8 or higher
- `csvlint` command-line tool. See [Installation Instructions](https://github.com/Data-Liberation-Front/csvlint.rb).
  - On macOS with Homebrew: `brew install ruby && gem install bundler csvlint`

### From Source (Development)

1. Clone the repository:

```bash
git clone https://github.com/ftrotter/npd_csviper.git
cd npd_csviper
```

2. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Install in development mode:

```bash
pip install -e .
```

### From PyPI (Coming Soon)

```bash
pip install npd_csviper
```

## Usage

npd_csviper operates in four phases that can be run together or separately:

### Phase 1: Extract Metadata

Analyze a CSV file and extract column information:

```bash
python -m npd_csviper extract_metadata --from_csv=data.csv --output_dir=./output/
```

Options:

- `--from_csv`: Path to the CSV file to analyze (required)
- `--output_dir`: Output directory (defaults to CSV filename without extension)
- `--overwrite_previous`: Overwrite existing output files

### Phase 2: Generate SQL Scripts

Generate CREATE TABLE and data import SQL scripts:

```bash
python -m npd_csviper build_sql --from_metadata_json=output/data.metadata.json --output_dir=./output/
```

### Phase 3: Generate Import Script

Create a standalone Python script for data import:

```bash
python -m npd_csviper build_import_script --from_resource_dir=./output/ --output_dir=./output/
```

### Phase 4: Invoke Compiled Scripts (New!)

Execute compiled import scripts with automatic file discovery:

```bash
python -m npd_csviper invoke-compiled-script --run_import_from=./output/ --import_data_from_dir=./data_directory/ --database_type=postgresql
```

Options:

- `--run_import_from`: Directory containing compiled npd_csviper scripts and metadata (required)
- `--import_data_from_dir`: Directory to search for data files (required)
- `--database_type`: Database type - 'postgresql' (required)

### Running All Phases Together

```bash
python -m npd_csviper full_compile --from_csv=data.csv --output_dir=./output/ --overwrite_previous
```

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Virtual environment (recommended)
- `csvlint` command-line tool. See [Installation Instructions](https://github.com/Data-Liberation-Front/csvlint.rb).
  - On macOS with Homebrew: `brew install ruby && gem install bundler csvlint`

### Setting up the Development Environment

1. Clone the repository and navigate to the project directory
2. Source the virtual environment setup script:

```bash
source source_me_to_get_venv.sh
```

3. Install development dependencies:

```bash
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/
```

### Linting

```bash
flake8 src/
```

## Project Structure

```tree
npd_csviper/
├── src/npd_csviper/
│   ├── __init__.py                          # Package initialization
│   ├── __main__.py                          # CLI entry point
│   ├── column_normalizer.py                 # Column name normalization utilities
│   ├── metadata_extractor.py                # CSV analysis and metadata extraction
│   ├── postgresql_schema_generator.py       # PostgreSQL SQL generation
│   ├── postgresql_import_script_generator.py # PostgreSQL import script generation
│   ├── import_executor.py                   # Shared import execution logic
│   └── script_invoker.py                    # Script execution and file discovery
├── tests/                                   # Test files
├── AI_Instructions/                         # Development documentation
├── pyproject.toml                          # Package configuration
├── requirements.txt                         # Project dependencies
└── README.md                                # This file
```

## Output Files

npd_csviper generates several files during processing:

### Phase 1 Output

- `{filename}.metadata.json`: Contains CSV structure analysis, normalized column names, and column width information

### Phase 2 Output

- `{filename}.create_table_postgres.sql`: PostgreSQL CREATE TABLE script
- `{filename}.import_data_postgres.sql`: PostgreSQL data import script

### Phase 3 Output

- `go.postgresql.py`: Standalone Python script for PostgreSQL database import

## Example Workflow

### Option 1: Full Compilation (Recommended)

Run all phases at once:

```bash
python -m npd_csviper full_compile --from_csv=sales_data.csv --output_dir=./sales_data/
```

### Option 2: Step-by-Step Process

1. **Analyze your CSV file**:

```bash
python -m npd_csviper extract_metadata --from_csv=sales_data.csv
```

2. **Review the generated metadata** in `sales_data/sales_data.metadata.json`

3. **Generate SQL scripts**:

```bash
python -m npd_csviper build_sql --from_metadata_json=sales_data/sales_data.metadata.json
```

4. **Create import scripts**:

```bash
python -m npd_csviper build_import_script --from_resource_dir=sales_data/
```

5. **Use the invoker system to import data**:

```bash
python -m npd_csviper invoke-compiled-script --run_import_from=./sales_data/ --import_data_from_dir=./data/ --database_type=postgresql
```

## The Invoker System

The invoker system is npd_csviper's intelligent file discovery and execution engine. It automatically finds the most recent data file matching your original CSV pattern and executes the appropriate import script.

### How It Works

1. **File Pattern Matching**: npd_csviper stores a glob pattern in the metadata file (e.g., `sales_data_*.csv`) that matches files with similar naming conventions
2. **Automatic Discovery**: The invoker searches your data directory for files matching this pattern
3. **Latest File Selection**: It automatically selects the most recently modified file
4. **User Confirmation**: Shows you the selected file and asks for confirmation before proceeding
5. **Script Execution**: Runs the PostgreSQL database import script (`go.postgresql.py`)

### Example Invoker Usage

If you have a directory with multiple data files:

```
data/
├── sales_data_2024-01.csv
├── sales_data_2024-02.csv
├── sales_data_2024-03.csv
└── other_data.csv
```

And compiled scripts in:

```
sales_data/
├── sales_data.metadata.json
├── go.postgresql.py
└── ...
```

Running the invoker:

```bash
python -m npd_csviper invoke-compiled-script --run_import_from=./sales_data/ --import_data_from_dir=./data/ --database_type=postgresql
```

Will automatically:
- Find all files matching `sales_data_*.csv`
- Select `sales_data_2024-03.csv` (most recent)
- Ask for your confirmation
- Execute `go.postgresql.py` with the selected file

### Benefits

- **No manual file specification**: Automatically finds the latest data file
- **Pattern-based matching**: Works with timestamped or versioned files
- **Safety confirmation**: Always asks before proceeding
- **Flexible search**: Supports both recursive and non-recursive directory searching
- **PostgreSQL focused**: Optimized for PostgreSQL database imports

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Roadmap

- [x] Phase 1: CSV metadata extraction and column normalization
- [x] Phase 2: SQL script generation for PostgreSQL
- [x] Phase 3: Python import script generation
- [x] Phase 4: Invoker system with automatic file discovery
- [x] Full compilation workflow
- [ ] Enhanced error handling and validation
- [ ] Progress bars for large file processing
- [ ] Configuration file support
- [ ] Additional database backend support
- [ ] Web interface for easier usage
- [ ] Docker containerization

## Support

For questions, issues, or contributions, please visit the [GitHub repository](https://github.com/ftrotter/npd_csviper).
