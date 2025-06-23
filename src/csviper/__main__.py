#!/usr/bin/env python3
"""
CSViper CLI - Main entry point
"""

import os
import sys
import click
from .metadata_extractor import CSVMetadataExtractor


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """
    CSViper - CSV to SQL import tool
    
    Analyzes CSV files and generates SQL scripts and Python import programs
    for loading data into relational databases (MySQL and PostgreSQL).
    """
    pass


@cli.command()
@click.option('--from_csv', required=True, type=click.Path(exists=True), 
              help='Path to the CSV file to analyze')
@click.option('--output_dir', type=click.Path(), 
              help='Output directory (defaults to CSV filename without extension)')
@click.option('--overwrite_previous', is_flag=True, default=False,
              help='Overwrite existing output files')
def extract_metadata(from_csv, output_dir, overwrite_previous):
    """
    Extract metadata from a CSV file.
    
    Analyzes the CSV file structure, normalizes column names, and determines
    maximum column widths. Saves results to a metadata JSON file.
    """
    try:
        # Convert to absolute path
        csv_path = os.path.abspath(from_csv)
        
        # Determine output directory if not specified
        if not output_dir:
            csv_basename = os.path.basename(csv_path)
            output_dir = os.path.splitext(csv_basename)[0]
        
        output_dir = os.path.abspath(output_dir)
        
        # Check if output directory exists and handle overwrite logic
        if os.path.exists(output_dir) and not overwrite_previous:
            metadata_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(csv_path))[0]}.metadata.json")
            if os.path.exists(metadata_file):
                click.echo(f"Error: Metadata file already exists: {metadata_file}")
                click.echo("Use --overwrite_previous to overwrite existing files")
                sys.exit(1)
        
        click.echo(f"Extracting metadata from: {csv_path}")
        click.echo(f"Output directory: {output_dir}")
        
        # Extract metadata
        metadata = CSVMetadataExtractor.fromFileToMetadata(csv_path, output_dir)
        
        click.echo(f"✓ Successfully extracted metadata for {metadata['total_columns']} columns")
        click.echo(f"✓ File size: {metadata['file_size_bytes']:,} bytes")
        click.echo(f"✓ Delimiter: '{metadata['delimiter']}'")
        click.echo(f"✓ Quote character: '{metadata['quote_character']}'")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--from_metadata_json', required=True, type=click.Path(exists=True),
              help='Path to the metadata JSON file')
@click.option('--output_dir', type=click.Path(),
              help='Output directory (defaults to metadata file directory)')
@click.option('--overwrite_previous', is_flag=True, default=False,
              help='Overwrite existing output files')
def build_sql(from_metadata_json, output_dir, overwrite_previous):
    """
    Generate SQL scripts from metadata JSON file.
    
    Creates CREATE TABLE and data import SQL scripts for both MySQL and PostgreSQL
    based on the metadata extracted from a CSV file.
    """
    try:
        from .mysql_schema_generator import MySQLSchemaGenerator
        from .postgresql_schema_generator import PostgreSQLSchemaGenerator
        
        # Convert to absolute path
        metadata_path = os.path.abspath(from_metadata_json)
        
        # Determine output directory if not specified
        if not output_dir:
            output_dir = os.path.dirname(metadata_path)
        
        output_dir = os.path.abspath(output_dir)
        
        click.echo(f"Generating SQL scripts from: {metadata_path}")
        click.echo(f"Output directory: {output_dir}")
        
        # Generate MySQL SQL scripts
        click.echo("\n--- Generating MySQL SQL scripts ---")
        mysql_files = MySQLSchemaGenerator.fromMetadataToSQL(
            metadata_path, output_dir, overwrite_previous
        )
        
        # Generate PostgreSQL SQL scripts
        click.echo("\n--- Generating PostgreSQL SQL scripts ---")
        postgres_files = PostgreSQLSchemaGenerator.fromMetadataToSQL(
            metadata_path, output_dir, overwrite_previous
        )
        
        click.echo(f"\n✓ Successfully generated SQL scripts:")
        click.echo(f"  MySQL CREATE TABLE: {os.path.basename(mysql_files['create_table_sql'])}")
        click.echo(f"  MySQL IMPORT DATA: {os.path.basename(mysql_files['import_data_sql'])}")
        click.echo(f"  PostgreSQL CREATE TABLE: {os.path.basename(postgres_files['create_table_sql'])}")
        click.echo(f"  PostgreSQL IMPORT DATA: {os.path.basename(postgres_files['import_data_sql'])}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--from_resource_dir', required=True, type=click.Path(exists=True),
              help='Directory containing metadata and SQL files from previous stages')
@click.option('--output_dir', type=click.Path(),
              help='Output directory (defaults to resource directory)')
@click.option('--overwrite_previous', is_flag=True, default=False,
              help='Overwrite existing output files')
def build_import_script(from_resource_dir, output_dir, overwrite_previous):
    """
    Generate Python import script from resource directory.
    
    Creates a standalone Python script (go.py) that can be used to import
    CSV data into a database using the generated SQL scripts.
    """
    click.echo("build_import_script command - Not yet implemented")
    # TODO: Implement script generation phase


if __name__ == '__main__':
    cli()
