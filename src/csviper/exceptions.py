"""
Custom exceptions for CSViper with specific error categories.
"""


class CSViperError(Exception):
    """Base exception for all CSViper errors."""
    
    def __init__(self, message: str, stage: str | None = None):
        super().__init__(message)
        self.stage = stage or "Unknown"
        self.message = message
    
    def __str__(self):
        return f"{self.stage}: {self.message}"


class CSVFileError(CSViperError):
    """Errors related to CSV file access and validation."""
    
    def __init__(self, message: str, file_path: str | None = None):
        super().__init__(message, "CSV File Error")
        self.file_path = file_path


class CSVParsingError(CSViperError):
    """Errors related to CSV parsing and format detection."""
    
    def __init__(self, message: str, file_path: str | None = None, line_number: int | None = None):
        super().__init__(message, "CSV Parsing Error")
        self.file_path = file_path
        self.line_number = line_number


class CSVEncodingError(CSViperError):
    """Errors related to CSV file encoding issues."""
    
    def __init__(self, message: str, file_path: str | None = None, encoding: str | None = None):
        super().__init__(message, "CSV Encoding Error")
        self.file_path = file_path
        self.encoding = encoding


class CSVValidationError(CSViperError):
    """Errors related to CSV data validation."""
    
    def __init__(self, message: str, file_path: str | None = None, line_number: int | None = None):
        super().__init__(message, "CSV Validation Error")
        self.file_path = file_path
        self.line_number = line_number


class MetadataError(CSViperError):
    """Errors related to metadata extraction and processing."""
    
    def __init__(self, message: str):
        super().__init__(message, "Metadata Error")


class SQLGenerationError(CSViperError):
    """Errors related to SQL script generation."""
    
    def __init__(self, message: str, db_type: str | None = None):
        super().__init__(message, "SQL Generation Error")
        self.db_type = db_type


class ImportScriptError(CSViperError):
    """Errors related to import script generation."""
    
    def __init__(self, message: str, db_type: str | None = None):
        super().__init__(message, "Import Script Error")
        self.db_type = db_type


class FileSystemError(CSViperError):
    """Errors related to file system operations."""
    
    def __init__(self, message: str, operation: str | None = None):
        super().__init__(message, "File System Error")
        self.operation = operation


class CacheError(CSViperError):
    """Errors related to caching operations."""
    
    def __init__(self, message: str):
        super().__init__(message, "Cache Error")
