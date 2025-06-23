"""
CSV Metadata Extraction for CSViper
"""

import os
import csv
import json
from typing import Dict, Any, List
from .column_normalizer import ColumnNormalizer


class CSVMetadataExtractor:
    """
    Extracts metadata from CSV files including column information and data analysis.
    """
    
    @staticmethod
    def fromFileToMetadata(full_path_to_csv_file: str, output_dir: str = None) -> Dict[str, Any]:
        """
        Extract metadata from a CSV file and optionally save to JSON.
        
        Args:
            full_path_to_csv_file (str): Absolute path to the local CSV file
            output_dir (str, optional): Directory to save metadata JSON file
            
        Returns:
            Dict[str, Any]: Metadata dictionary containing file info, columns, and analysis
            
        Raises:
            FileNotFoundError: If the CSV file does not exist
            ValueError: If the CSV file is invalid or has inconsistent structure
        """
        # File validation
        if not os.path.isfile(full_path_to_csv_file):
            raise FileNotFoundError(f"CSV file not found: {full_path_to_csv_file}")
        
        if not os.access(full_path_to_csv_file, os.R_OK):
            raise ValueError(f"CSV file is not readable: {full_path_to_csv_file}")
        
        print(f"Analyzing CSV file: {os.path.basename(full_path_to_csv_file)}")
        
        # Get basic file info
        file_size = os.path.getsize(full_path_to_csv_file)
        filename = os.path.basename(full_path_to_csv_file)
        filename_without_ext = os.path.splitext(filename)[0]
        
        # Detect CSV format using csv.Sniffer
        delimiter, quote_char = CSVMetadataExtractor._detect_csv_format(full_path_to_csv_file)
        
        # Extract and normalize column names
        original_columns, normalized_columns = CSVMetadataExtractor._extract_column_names(
            full_path_to_csv_file, delimiter, quote_char
        )
        
        # Create column mapping by position to handle duplicate original names
        column_mapping = {}
        for i, (orig, norm) in enumerate(zip(original_columns, normalized_columns)):
            # Use position-based key for duplicates
            key = f"{orig} (column {i+1})" if original_columns.count(orig) > 1 else orig
            column_mapping[key] = norm
        
        # Analyze column widths
        max_lengths = CSVMetadataExtractor._analyze_column_widths(
            full_path_to_csv_file, delimiter, quote_char, original_columns, normalized_columns
        )
        
        # Build metadata dictionary
        metadata = {
            "filename": filename,
            "filename_without_extension": filename_without_ext,
            "full_path": full_path_to_csv_file,
            "file_size_bytes": file_size,
            "delimiter": delimiter,
            "quote_character": quote_char,
            "original_column_names": original_columns,
            "normalized_column_names": normalized_columns,
            "column_name_mapping": column_mapping,
            "max_column_lengths": max_lengths,
            "total_columns": len(original_columns)
        }
        
        # Save metadata to JSON file if output directory is specified
        if output_dir:
            CSVMetadataExtractor._save_metadata_json(metadata, output_dir, filename_without_ext)
        
        return metadata
    
    @staticmethod
    def _detect_csv_format(file_path: str) -> tuple:
        """
        Detect CSV delimiter and quote character using csv.Sniffer.
        
        Args:
            file_path (str): Path to CSV file
            
        Returns:
            tuple: (delimiter, quote_char)
            
        Raises:
            ValueError: If CSV format cannot be detected
        """
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                # Read a sample of the file for sniffing
                sample = csvfile.read(8192)
                csvfile.seek(0)
                
                # Use csv.Sniffer to detect format
                sniffer = csv.Sniffer()
                dialect = sniffer.sniff(sample)
                
                # Verify the dialect works by trying to read the first few lines
                reader = csv.reader(csvfile, dialect)
                header = next(reader)
                first_row = next(reader, None)
                
                if not header:
                    raise ValueError("CSV file appears to be empty")
                
                if first_row is None:
                    raise ValueError("CSV file contains only a header row, no data")
                
                return dialect.delimiter, dialect.quotechar
                
        except (csv.Error, UnicodeDecodeError) as e:
            raise ValueError(f"Unable to detect CSV format: {e}")
        except StopIteration:
            raise ValueError("CSV file does not contain sufficient data")
    
    @staticmethod
    def _extract_column_names(file_path: str, delimiter: str, quote_char: str) -> tuple:
        """
        Extract and normalize column names from CSV header.
        
        Args:
            file_path (str): Path to CSV file
            delimiter (str): CSV delimiter
            quote_char (str): CSV quote character
            
        Returns:
            tuple: (original_columns, normalized_column_mapping)
        """
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=delimiter, quotechar=quote_char)
            original_columns = next(reader)
        
        # Normalize column names
        normalized_columns = ColumnNormalizer.rename_column_list(original_columns)
        
        return original_columns, normalized_columns
    
    @staticmethod
    def _analyze_column_widths(file_path: str, delimiter: str, quote_char: str, 
                             original_columns: List[str], normalized_columns: List[str]) -> Dict[str, int]:
        """
        Analyze maximum string length for each column in the CSV file.
        
        Args:
            file_path (str): Path to CSV file
            delimiter (str): CSV delimiter
            quote_char (str): CSV quote character
            original_columns (List[str]): Original column names
            normalized_columns (List[str]): List of normalized column names
            
        Returns:
            Dict[str, int]: Maximum length for each normalized column name
            
        Raises:
            ValueError: If rows have inconsistent column counts
        """
        max_lengths = {norm_col: 0 for norm_col in normalized_columns}
        expected_column_count = len(original_columns)
        
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=delimiter, quotechar=quote_char)
            
            # Skip header row
            next(reader)
            
            row_number = 1
            for row in reader:
                row_number += 1
                
                # Check column count consistency
                if len(row) != expected_column_count:
                    raise ValueError(
                        f"Inconsistent column count at row {row_number}: "
                        f"Expected {expected_column_count} columns, found {len(row)}"
                    )
                
                # Update maximum lengths
                for i, value in enumerate(row):
                    normalized_col = normalized_columns[i]
                    max_lengths[normalized_col] = max(max_lengths[normalized_col], len(str(value)))
        
        return max_lengths
    
    @staticmethod
    def _save_metadata_json(metadata: Dict[str, Any], output_dir: str, filename_base: str) -> None:
        """
        Save metadata to JSON file.
        
        Args:
            metadata (Dict[str, Any]): Metadata dictionary
            output_dir (str): Output directory
            filename_base (str): Base filename (without extension)
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Create JSON filename
        json_filename = f"{filename_base}.metadata.json"
        json_path = os.path.join(output_dir, json_filename)
        
        # Save metadata to JSON file
        with open(json_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(metadata, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"Metadata saved to: {json_path}")
