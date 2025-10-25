"""
final_test_dagster Dagster Import
==================

Based on the 'dagster' Import Script Template for npd_CSViper

Original CSV: customers.csv
Generated on: 2025-10-25 15:29:41
"""
from dagster import asset, materialize

from resources import get_resources
from resources.csv_import import CSVImport
from resources.fsclient import FSClient


@asset(group_name="final_test_dagster", key_prefix=["bronze", "final_test_dagster"])
def bronze_final_test_dagster(fsclient: FSClient):
    importer = CSVImport(fsclient)
    importer.load(
        json_filename='customers.metadata.json',
        sql_filename='customers.create_table_postgres.sql',
        csv_file='customers.csv',
        db_schema_name='bronze_final_test_dagster',
        table_name='REPLACE_ME',
    )

if __name__ == '__main__':
    result = materialize(
        assets=[bronze_final_test_dagster],
        resources=get_resources()
    )
