#!/usr/bin/env python3
"""
PostgreSQL Import Script Generator for npd_CSViper

Generates standalone Python scripts (go.postgresql.py) that can import CSV data
into PostgreSQL databases using the metadata and SQL files from previous stages.
"""

import os
import importlib.util
from .base_import_script_generator import BaseImportScriptGenerator


class PostgreSQLImportScriptGenerator(BaseImportScriptGenerator):
    """
    Generates standalone Python import scripts for PostgreSQL CSV data loading.
    """
    
    @staticmethod
    def fromResourceDirToScript(resource_dir, output_dir=None, overwrite_previous=False, script_template='dagster'):
        """
        Generate a go.postgresql.py script from resource directory containing metadata and SQL files.
        
        Args:
            resource_dir (str): Directory containing metadata.json and SQL files
            output_dir (str): Output directory for go.postgresql.py (defaults to resource_dir)
            overwrite_previous (bool): Whether to overwrite existing go.postgresql.py file
            script_template (str): Name of the template to use (default: 'dagster')
            
        Returns:
            str: Path to the generated go.postgresql.py file
            
        Raises:
            FileNotFoundError: If required files are not found
            ValueError: If metadata is invalid
        """
        return BaseImportScriptGenerator.fromResourceDirToScript(
            resource_dir, output_dir, overwrite_previous, 'postgresql', PostgreSQLImportScriptGenerator, script_template
        )
    
    @staticmethod
    def _validate_sql_files(resource_dir, metadata):
        """Validate that required PostgreSQL SQL files exist."""
        csv_basename = os.path.splitext(metadata['filename'])[0]
        
        required_files = [
            f"{csv_basename}.create_table_postgres.sql",
            f"{csv_basename}.import_data_postgres.sql"
        ]
        
        missing_files = []
        for filename in required_files:
            filepath = os.path.join(resource_dir, filename)
            if not os.path.exists(filepath):
                missing_files.append(filename)
        
        if missing_files:
            raise FileNotFoundError(f"Missing required PostgreSQL SQL files: {', '.join(missing_files)}")
    
    @staticmethod
    def _generate_script_content(metadata, script_template='dagster', output_dir=None):
        """
        Generate the content of the go.postgresql.py script using the specified template.
        
        Args:
            metadata (dict): CSV metadata containing filename, columns, etc.
            script_template (str): Name of the template to use (default: 'dagster')
            output_dir (str): Output directory path to derive import_key from
            
        Returns:
            str: Complete Python script content
            
        Raises:
            FileNotFoundError: If template file is not found
            ImportError: If template module cannot be loaded
            AttributeError: If template function is not found
        """
        timestamp = BaseImportScriptGenerator._get_timestamp()
        
        # Derive import_key from output directory
        if output_dir:
            import_key = os.path.basename(os.path.abspath(output_dir))
        else:
            import_key = "REPLACE_ME"
        
        # Use full filename from metadata as csv_file_path
        csv_file_path = metadata['filename']
        
        # Load the template module
        template_module = PostgreSQLImportScriptGenerator._load_template(script_template)
        
        # Generate script content using the template
        return template_module.generate_postgresql_script(
            csv_file_path=csv_file_path,
            import_key=import_key,
            timestamp=timestamp
        )
    @staticmethod
    def _load_template(template_name):
        """
        Load a template module by name.
        
        Args:
            template_name (str): Name of the template (e.g., 'default')
            
        Returns:
            module: The loaded template module
            
        Raises:
            FileNotFoundError: If template file is not found
            ImportError: If template module cannot be loaded
        """
        # Get the path to the templates directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        templates_dir = os.path.join(current_dir, 'templates')
        template_filename = f"{template_name}_template.py"
        template_path = os.path.join(templates_dir, template_filename)
        
        if not os.path.exists(template_path):
            raise FileNotFoundError(
                f"Template file not found: {template_path}. "
                f"Available templates can be found in {templates_dir}"
            )
        
        # Load the module dynamically
        spec = importlib.util.spec_from_file_location(
            f"npd_csviper.templates.{template_name}_template", 
            template_path
        )
        
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load template module from {template_path}")
        
        template_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(template_module)
        
        # Verify the template has the required function
        if not hasattr(template_module, 'generate_postgresql_script'):
            raise AttributeError(
                f"Template module {template_name}_template.py must contain a "
                "'generate_postgresql_script' function"
            )
        
        return template_module
