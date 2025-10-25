"""
test_data Dagster Import
==================

Based on the 'dagster' Import Script Template for npd_CSViper

Original CSV: test_data.csv
Generated on: 2025-10-25 15:32:26
"""
from dagster import asset, materialize

from resources import get_resources
from resources.csv_import import CSVImport
from resources.fsclient import FSClient


@asset(group_name="test_data", key_prefix=["bronze", "test_data"])
def bronze_test_data(fsclient: FSClient):
    importer = CSVImport(fsclient)
    importer.load(
        json_filename='test_data.metadata.json',
        sql_filename='test_data.create_table_postgres.sql',
        csv_file='test_data.csv',
        db_schema_name='bronze_test_data',
        table_name='REPLACE_ME',
    )

if __name__ == '__main__':
    result = materialize(
        assets=[bronze_test_data],
        resources=get_resources()
    )
