"""
test_dagster_nppes Dagster Import
==================

Based on the 'dagster' Import Script Template for npd_CSViper

Original CSV: customers.csv
Generated on: 2025-10-25 15:29:11
"""
from dagster import asset, materialize

from resources import get_resources
from resources.csv_import import CSVImport
from resources.fsclient import FSClient


@asset(group_name="test_dagster_nppes", key_prefix=["bronze", "test_dagster_nppes"])
def bronze_test_dagster_nppes(fsclient: FSClient):
    importer = CSVImport(fsclient)
    importer.load(
        json_filename='customers.metadata.json',
        sql_filename='customers.create_table_postgres.sql',
        csv_file='customers.csv',
        db_schema_name='bronze_test_dagster_nppes',
        table_name='REPLACE_ME',
    )

if __name__ == '__main__':
    result = materialize(
        assets=[bronze_test_dagster_nppes],
        resources=get_resources()
    )
