"""
REPLACEME Dagster Import
==================

Based on the 'dagster' Import Script Template for npd_CSViper

"""
from dagster import asset, materialize

from resources import get_resources
from resources.csv_import import CSVImport
from resources.fsclient import FSClient


@asset(group_name="nppes_main", key_prefix=["bronze", "nppes"])
def bronze_nppes_main(fsclient: FSClient):
    importer = CSVImport(fsclient)
    importer.load(
        json_filename='npidata_pfile_20050523-20250608.metadata.json',
        sql_filename='npidata_pfile_20050523-20250608.create_table_postgres.sql',
        csv_file='nppes/npidata_pfile_20050523-20250810.csv',
        db_schema_name='bronze_nppes',
        table_name='main_file',
    )

if __name__ == '__main__':
    result = materialize(
        assets=[bronze_nppes_main],
        resources=get_resources()
    )
