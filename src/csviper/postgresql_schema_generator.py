"""
PostgreSQL Schema Generator for CSViper
"""

import os
import json
import hashlib
import glob
from typing import Dict, Any, List


class PostgreSQLSchemaGenerator:
    """
    Generates PostgreSQL-specific SQL scripts from CSV metadata.
    """
    
    @staticmethod
    def fromMetadataToSQL(metadata_json_path: str, output_dir: str, overwrite_previous: bool = False) -> Dict[str, str]:
        """
        Generate PostgreSQL SQL scripts from metadata JSON file.
        
        Args:
            metadata_json_path (str): Path to the metadata JSON file
            output_dir (str): Output directory for SQL files
            overwrite_previous (bool): Whether to overwrite existing files
            
        Returns:
            Dict[str, str]: Dictionary with paths to generated SQL files
            
        Raises:
            FileNotFoundError: If metadata JSON file does not exist
            ValueError: If metadata JSON is invalid
        """
        # Validate metadata file
        if not os.path.isfile(metadata_json_path):
            raise FileNotFoundError(f"Metadata JSON file not found: {metadata_json_path}")
        
        # Load metadata
        with open(metadata_json_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # Validate required metadata fields
        required_fields = ['filename_without_extension', 'normalized_column_names', 'max_column_lengths']
        for field in required_fields:
            if field not in metadata:
                raise ValueError(f"Required metadata field missing: {field}")
        
        print(f"Generating PostgreSQL SQL for: {metadata['filename_without_extension']}")
        
        # Create cache directory for CREATE TABLE SQL
        cache_dir = os.path.join(output_dir, 'cache_create_table_sql')
        os.makedirs(cache_dir, exist_ok=True)
        
        # Generate MD5 hash for column structure caching
        column_names_str = ','.join([col.lower() for col in metadata['normalized_column_names']])
        column_md5_hash = hashlib.md5(column_names_str.encode()).hexdigest()
        
        # Check for cached CREATE TABLE SQL
        create_table_sql = PostgreSQLSchemaGenerator._get_or_create_table_sql(
            metadata, cache_dir, column_md5_hash, overwrite_previous
        )
        
        # Generate data import SQL with caching
        import_sql = PostgreSQLSchemaGenerator._get_or_create_import_sql(
            metadata, output_dir, column_md5_hash, overwrite_previous
        )
        
        # Write SQL files to output directory
        filename_base = metadata['filename_without_extension']
        
        create_table_file = os.path.join(output_dir, f"{filename_base}.create_table_postgres.sql")
        import_data_file = os.path.join(output_dir, f"{filename_base}.import_data_postgres.sql")
        
        # Write CREATE TABLE SQL
        with open(create_table_file, 'w', encoding='utf-8') as f:
            f.write(create_table_sql)
        
        # Write IMPORT DATA SQL
        with open(import_data_file, 'w', encoding='utf-8') as f:
            f.write(import_sql)
        
        print(f"Generated PostgreSQL CREATE TABLE SQL: {create_table_file}")
        print(f"Generated PostgreSQL IMPORT DATA SQL: {import_data_file}")
        
        return {
            'create_table_sql': create_table_file,
            'import_data_sql': import_data_file
        }
    
    @staticmethod
    def _get_or_create_table_sql(metadata: Dict[str, Any], cache_dir: str, 
                                column_md5_hash: str, overwrite_previous: bool) -> str:
        """
        Get CREATE TABLE SQL from cache or generate new one.
        
        Args:
            metadata (Dict[str, Any]): CSV metadata
            cache_dir (str): Cache directory path
            column_md5_hash (str): MD5 hash of column structure
            overwrite_previous (bool): Whether to overwrite existing cache
            
        Returns:
            str: CREATE TABLE SQL statement
        """
        # Look for cached CREATE TABLE SQL
        cache_pattern = os.path.join(cache_dir, f"{column_md5_hash}.*.postgres.sql")
        cache_files = glob.glob(cache_pattern)
        
        if cache_files and not overwrite_previous:
            # Use cached version
            cache_file = cache_files[0]
            print(f"Using cached PostgreSQL CREATE TABLE SQL: {os.path.basename(cache_file)}")
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                return f.read()
        
        # Generate new CREATE TABLE SQL
        print("Generating new PostgreSQL CREATE TABLE SQL...")
        
        sql_parts = []
        
        # CREATE DATABASE statement (PostgreSQL uses CREATE DATABASE)
        sql_parts.append("CREATE DATABASE REPLACE_ME_DB_NAME;")
        sql_parts.append("")
        
        # DROP TABLE statement
        sql_parts.append("DROP TABLE IF EXISTS REPLACE_ME_DB_NAME.REPLACE_ME_TABLE_NAME;")
        sql_parts.append("")
        
        # CREATE TABLE statement
        create_table_sql = "CREATE TABLE REPLACE_ME_DB_NAME.REPLACE_ME_TABLE_NAME (\n"
        
        column_definitions = []
        for col_name in metadata['normalized_column_names']:
            # Add 1 to max length to ensure there's room for the data
            varchar_length = metadata['max_column_lengths'][col_name] + 1
            column_definitions.append(f"    \"{col_name}\" VARCHAR({varchar_length})")
        
        create_table_sql += ",\n".join(column_definitions)
        create_table_sql += "\n);"
        
        sql_parts.append(create_table_sql)
        
        full_sql = "\n".join(sql_parts)
        
        # Cache the generated SQL
        filename_base = metadata.get('filename_without_extension', 'unknown')
        cache_file = os.path.join(cache_dir, f"{column_md5_hash}.create_table.{filename_base}.postgres.sql")
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            f.write(full_sql)
        
        print(f"Cached PostgreSQL CREATE TABLE SQL: {os.path.basename(cache_file)}")
        
        return full_sql
    
    @staticmethod
    def _get_or_create_import_sql(metadata: Dict[str, Any], output_dir: str, 
                                 column_md5_hash: str, overwrite_previous: bool) -> str:
        """
        Get IMPORT DATA SQL from cache or generate new one.
        
        Args:
            metadata (Dict[str, Any]): CSV metadata
            output_dir (str): Output directory path
            column_md5_hash (str): MD5 hash of column structure
            overwrite_previous (bool): Whether to overwrite existing cache
            
        Returns:
            str: IMPORT DATA SQL statement
        """
        # Create cache directory for import data SQL
        cache_dir = os.path.join(output_dir, 'cache_import_data_sql')
        os.makedirs(cache_dir, exist_ok=True)
        
        # Look for cached IMPORT DATA SQL
        cache_pattern = os.path.join(cache_dir, f"{column_md5_hash}.*.postgres.sql")
        cache_files = glob.glob(cache_pattern)
        
        if cache_files and not overwrite_previous:
            # Use cached version
            cache_file = cache_files[0]
            print(f"Using cached PostgreSQL IMPORT DATA SQL: {os.path.basename(cache_file)}")
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                return f.read()
        
        # Generate new IMPORT DATA SQL
        print("Generating new PostgreSQL IMPORT DATA SQL...")
        
        import_sql = PostgreSQLSchemaGenerator._generate_import_sql(metadata)
        
        # Cache the generated SQL
        filename_base = metadata.get('filename_without_extension', 'unknown')
        cache_file = os.path.join(cache_dir, f"{column_md5_hash}.import_data.{filename_base}.postgres.sql")
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            f.write(import_sql)
        
        print(f"Cached PostgreSQL IMPORT DATA SQL: {os.path.basename(cache_file)}")
        
        return import_sql
    
    @staticmethod
    def _generate_import_sql(metadata: Dict[str, Any]) -> str:
        """
        Generate PostgreSQL COPY SQL statement.
        
        Args:
            metadata (Dict[str, Any]): CSV metadata
            
        Returns:
            str: COPY SQL statement
        """
        delimiter = metadata.get('delimiter', ',')
        quote_char = metadata.get('quote_character', '"')
        
        # Build COPY statement
        sql_parts = []
        
        sql_parts.append("\\COPY REPLACE_ME_DB_NAME.REPLACE_ME_TABLE_NAME FROM 'REPLACE_ME_CSV_FULL_PATH'")
        sql_parts.append("WITH (")
        sql_parts.append("    FORMAT csv,")
        sql_parts.append("    HEADER true,")
        sql_parts.append(f"    DELIMITER '{delimiter}',")
        sql_parts.append(f"    QUOTE '{quote_char}',")
        sql_parts.append("    NULL '',")
        sql_parts.append("    ENCODING 'UTF8'")
        sql_parts.append(");")
        
        return "\n".join(sql_parts)
