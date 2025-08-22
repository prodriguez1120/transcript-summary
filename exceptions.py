#!/usr/bin/env python3
"""
Custom Exception Classes for FlexXray Transcript Summarizer

This module provides a hierarchy of custom exceptions for better error handling
and more specific error reporting throughout the application.
"""

class FlexXrayError(Exception):
    """Base exception class for all FlexXray application errors."""
    
    def __init__(self, message: str, details: str | None = None, original_error: Exception | None = None):
        self.message = message
        self.details = details
        self.original_error = original_error
        super().__init__(self.message)
    
    def __str__(self):
        error_str = self.message
        if self.details:
            error_str += f" - Details: {self.details}"
        if self.original_error:
            error_str += f" - Original Error: {str(self.original_error)}"
        return error_str


# Configuration and Environment Errors
class ConfigurationError(FlexXrayError):
    """Raised when there are configuration-related issues."""
    pass


class EnvironmentError(FlexXrayError):
    """Raised when environment variables or system configuration is invalid."""
    pass


# OpenAI API Errors
class OpenAIError(FlexXrayError):
    """Base exception for OpenAI API related errors."""
    pass


class OpenAIAPIError(OpenAIError):
    """Raised when OpenAI API calls fail."""
    pass


class OpenAIResponseError(OpenAIError):
    """Raised when OpenAI response is invalid or cannot be parsed."""
    pass


class OpenAIQuotaError(OpenAIError):
    """Raised when OpenAI API quota is exceeded."""
    pass


# Document Processing Errors
class DocumentProcessingError(FlexXrayError):
    """Base exception for document processing errors."""
    pass


class DocumentReadError(DocumentProcessingError):
    """Raised when a document cannot be read or opened."""
    pass


class DocumentParseError(DocumentProcessingError):
    """Raised when document content cannot be parsed."""
    pass


class DocumentFormatError(DocumentProcessingError):
    """Raised when document format is unsupported or invalid."""
    pass


class DocumentValidationError(DocumentProcessingError):
    """Raised when document validation fails."""
    pass


# Quote Processing Errors
class QuoteProcessingError(FlexXrayError):
    """Base exception for quote processing errors."""
    pass


class QuoteExtractionError(QuoteProcessingError):
    """Raised when quotes cannot be extracted from text."""
    pass


class QuoteValidationError(QuoteProcessingError):
    """Raised when quote data is invalid or malformed."""
    pass


class QuoteRankingError(QuoteProcessingError):
    """Raised when quote ranking fails."""
    pass


# Vector Database Errors
class VectorDatabaseError(FlexXrayError):
    """Base exception for vector database operations."""
    pass


class ChromaDBConnectionError(VectorDatabaseError):
    """Raised when ChromaDB connection fails."""
    pass


class ChromaDBInitializationError(VectorDatabaseError):
    """Raised when ChromaDB initialization fails."""
    pass


class QuoteStorageError(VectorDatabaseError):
    """Raised when quote storage operations fail."""
    pass


class SearchError(VectorDatabaseError):
    """Raised when search operations fail."""
    pass


class DataValidationError(VectorDatabaseError):
    """Raised when data validation fails."""
    pass


# Analysis Errors
class AnalysisError(FlexXrayError):
    """Base exception for analysis operations."""
    pass


class PerspectiveAnalysisError(AnalysisError):
    """Raised when perspective analysis fails."""
    pass


class ThemeAnalysisError(AnalysisError):
    """Raised when theme analysis fails."""
    pass


class JSONParsingError(AnalysisError):
    """Raised when JSON parsing fails."""
    pass


# Export Errors
class ExportError(FlexXrayError):
    """Base exception for export operations."""
    pass


class FileExportError(ExportError):
    """Raised when file export fails."""
    pass


class ExcelExportError(ExportError):
    """Raised when Excel export fails."""
    pass


class WordExportError(ExportError):
    """Raised when Word document export fails."""
    pass


# Validation Errors
class ValidationError(FlexXrayError):
    """Base exception for validation errors."""
    pass


class InputValidationError(ValidationError):
    """Raised when input data validation fails."""
    pass


class DataIntegrityError(ValidationError):
    """Raised when data integrity checks fail."""
    pass


# Utility function to wrap exceptions with context
def wrap_exception(exception: Exception, context: str, details: str | None = None) -> FlexXrayError:
    """Wrap an existing exception with FlexXray context."""
    if isinstance(exception, FlexXrayError):
        return exception
    
    # Map common exceptions to appropriate FlexXray exceptions
    if isinstance(exception, (ValueError, TypeError)):
        return InputValidationError(f"Invalid input in {context}", details, exception)
    elif isinstance(exception, (FileNotFoundError, PermissionError)):
        return DocumentReadError(f"File operation failed in {context}", details, exception)
    elif isinstance(exception, (ValueError, TypeError)):
        return InputValidationError(f"Invalid input in {context}", details, exception)
    elif isinstance(exception, (FileNotFoundError, PermissionError)):
        return DocumentReadError(f"File operation failed in {context}", details, exception)
    elif "JSONDecodeError" in str(type(exception)):
        return JSONParsingError(f"JSON parsing failed in {context}", details, exception)
    elif isinstance(exception, (ConnectionError, TimeoutError)):
        return ChromaDBConnectionError(f"Connection failed in {context}", details, exception)
    else:
        return FlexXrayError(f"Unexpected error in {context}", details, exception)
