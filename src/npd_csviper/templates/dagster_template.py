"""
Dagster PostgreSQL Import Script Template for npd_CSViper

This template generates Dagster asset scripts that can import CSV data
into PostgreSQL databases using pre-generated SQL scripts.
"""

import os


def generate_postgresql_script(*, csv_file_path, import_key, timestamp):
    """
    Generate Dagster asset script content using the dagster template.
    
    Args:
        csv_file_path (str): Full path to the original CSV file
        import_key (str): Import key derived from output directory name
        timestamp (str): Timestamp for when the script was generated
        
    Returns:
        str: Complete Python script content
    """
    
    # Calculate derived values from csv_file_path
    filename = os.path.basename(csv_file_path)
    csv_basename = os.path.splitext(filename)[0]
    
    script_content = f'''"""
{import_key} Dagster Import
==================

Based on the 'dagster' Import Script Template for npd_CSViper

Original CSV: {filename}
Generated on: {timestamp}
"""
from dagster import asset, materialize

from resources import get_resources
from resources.csv_import import CSVImport
from resources.fsclient import FSClient


@asset(group_name="{import_key}", key_prefix=["bronze", "{import_key}"])
def bronze_{import_key}(fsclient: FSClient):
    importer = CSVImport(fsclient)
    importer.load(
        json_filename='{csv_basename}.metadata.json',
        sql_filename='{csv_basename}.create_table_postgres.sql',
        csv_file='{csv_file_path}',
        db_schema_name='bronze_{import_key}',
        table_name='REPLACE_ME',
    )

if __name__ == '__main__':
    result = materialize(
        assets=[bronze_{import_key}],
        resources=get_resources()
    )
'''
    
    return script_content
