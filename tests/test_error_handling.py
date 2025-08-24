

#!/usr/bin/env python3
"""
Unit Tests for Error Handling and Validation

This module tests the custom exception classes, validation logic, and error handling
strategies implemented in the FlexXray application.
"""

import unittest
import json
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from exceptions import (
    FlexXrayError, InputValidationError, QuoteValidationError, 
    OpenAIError, JSONParsingError, ConfigurationError, DocumentValidationError, wrap_exception
)
from validation import (
    InputValidator, DocumentValidator, ConfigurationValidator
)
from json_utils import JSONExtractor, JSONParser


class TestCustomExceptions(unittest.TestCase):
    """Test custom exception classes."""
    
    def test_flexxray_error_base_class(self):
        """Test base FlexXrayError class."""
        error = FlexXrayError("Test error")
        self.assertEqual(str(error), "Test error")
        self.assertIsInstance(error, Exception)
    
    def test_flexxray_error_with_details(self):
        """Test FlexXrayError with details."""
        error = FlexXrayError("Test error", "Additional details")
        self.assertIn("Additional details", str(error))
    
    def test_flexxray_error_with_original_error(self):
        """Test FlexXrayError with original error."""
        original = ValueError("Original error")
        error = FlexXrayError("Test error", "Details", original)
        self.assertIn("Original Error: Original error", str(error))
    
    def test_exception_hierarchy(self):
        """Test exception class hierarchy."""
        self.assertTrue(issubclass(InputValidationError, FlexXrayError))
        self.assertTrue(issubclass(QuoteValidationError, FlexXrayError))
        self.assertTrue(issubclass(OpenAIError, FlexXrayError))
        self.assertTrue(issubclass(JSONParsingError, FlexXrayError))


class TestWrapException(unittest.TestCase):
    """Test the wrap_exception utility function."""
    
    def test_wrap_flexxray_exception(self):
        """Test wrapping an existing FlexXray exception."""
        original = InputValidationError("Original")
        wrapped = wrap_exception(original, "test context")
        self.assertIs(wrapped, original)
    
    def test_wrap_value_error(self):
        """Test wrapping a ValueError."""
        original = ValueError("Invalid input")
        wrapped = wrap_exception(original, "test context")
        self.assertIsInstance(wrapped, InputValidationError)
        self.assertIn("test context", str(wrapped))
    
    def test_wrap_file_not_found_error(self):
        """Test wrapping a FileNotFoundError."""
        original = FileNotFoundError("File not found")
        wrapped = wrap_exception(original, "test context")
        self.assertIsInstance(wrapped, FlexXrayError)


class TestInputValidator(unittest.TestCase):
    """Test InputValidator class."""
    
    def test_validate_file_path_valid(self):
        """Test valid file path validation."""
        with patch('os.path.exists', return_value=True):
            result = InputValidator.validate_file_path("/valid/path.txt")
            self.assertEqual(result, "/valid/path.txt")
    
    def test_validate_file_path_invalid_type(self):
        """Test file path validation with invalid type."""
        with self.assertRaises(InputValidationError):
            InputValidator.validate_file_path(None)
    
    def test_validate_file_path_empty(self):
        """Test file path validation with empty string."""
        with self.assertRaises(InputValidationError):
            InputValidator.validate_file_path("")
    
    def test_validate_file_path_not_exists(self):
        """Test file path validation when file doesn't exist."""
        with patch('os.path.exists', return_value=False):
            with self.assertRaises(InputValidationError):
                InputValidator.validate_file_path("/nonexistent/path.txt")
    
    def test_validate_file_path_with_extensions(self):
        """Test file path validation with allowed extensions."""
        with patch('os.path.exists', return_value=True):
            result = InputValidator.validate_file_path(
                "/path/file.txt", 
                allowed_extensions=['.txt', '.docx']
            )
            self.assertEqual(result, "/path/file.txt")
    
    def test_validate_file_path_invalid_extension(self):
        """Test file path validation with invalid extension."""
        with patch('os.path.exists', return_value=True):
            with self.assertRaises(InputValidationError):
                InputValidator.validate_file_path(
                    "/path/file.pdf", 
                    allowed_extensions=['.txt', '.docx']
                )
    
    def test_validate_api_key_valid(self):
        """Test valid API key validation."""
        result = InputValidator.validate_api_key("sk-1234567890abcdef")
        self.assertEqual(result, "sk-1234567890abcdef")
    
    def test_validate_api_key_invalid_format(self):
        """Test API key validation with invalid format."""
        with self.assertRaises(InputValidationError):
            InputValidator.validate_api_key("invalid-key")
    
    def test_validate_api_key_too_short(self):
        """Test API key validation with too short key."""
        with self.assertRaises(InputValidationError):
            InputValidator.validate_api_key("sk-123")
    
    def test_validate_text_content_valid(self):
        """Test valid text content validation."""
        result = InputValidator.validate_text_content("Valid text content")
        self.assertEqual(result, "Valid text content")
    
    def test_validate_text_content_too_short(self):
        """Test text content validation with too short text."""
        with self.assertRaises(InputValidationError):
            InputValidator.validate_text_content("Hi", min_length=10)
    
    def test_validate_text_content_too_long(self):
        """Test text content validation with too long text."""
        long_text = "a" * 1001
        with self.assertRaises(InputValidationError):
            InputValidator.validate_text_content(long_text, max_length=1000)
    
    def test_validate_quote_data_valid(self):
        """Test valid quote data validation."""
        quote = {
            'text': 'Valid quote text',
            'speaker_role': 'expert',
            'transcript_name': 'Test Transcript'
        }
        result = InputValidator.validate_quote_data(quote)
        self.assertEqual(result, quote)
    
    def test_validate_quote_data_missing_required_field(self):
        """Test quote validation with missing required field."""
        quote = {'text': 'Valid quote text'}  # Missing speaker_role
        with self.assertRaises(QuoteValidationError):
            InputValidator.validate_quote_data(quote)
    
    def test_validate_quote_data_invalid_speaker_role(self):
        """Test quote validation with invalid speaker role."""
        quote = {
            'text': 'Valid quote text',
            'speaker_role': 'invalid_role'
        }
        with self.assertRaises(QuoteValidationError):
            InputValidator.validate_quote_data(quote)
    
    def test_validate_quotes_list_valid(self):
        """Test valid quotes list validation."""
        quotes = [
            {'text': 'Quote 1', 'speaker_role': 'expert'},
            {'text': 'Quote 2', 'speaker_role': 'interviewer'}
        ]
        result = InputValidator.validate_quotes_list(quotes)
        self.assertEqual(result, quotes)
    
    def test_validate_quotes_list_empty(self):
        """Test quotes list validation with empty list."""
        result = InputValidator.validate_quotes_list([])
        self.assertEqual(result, [])
    
    def test_validate_quotes_list_invalid_quote(self):
        """Test quotes list validation with invalid quote."""
        quotes = [
            {'text': 'Valid quote', 'speaker_role': 'expert'},
            {'text': 'Invalid quote'}  # Missing speaker_role
        ]
        with self.assertRaises(QuoteValidationError):
            InputValidator.validate_quotes_list(quotes)
    
    def test_validate_perspective_data_valid(self):
        """Test valid perspective data validation."""
        perspective = {
            'title': 'Test Perspective',
            'description': 'Test description',
            'focus_areas': ['area1', 'area2']
        }
        result = InputValidator.validate_perspective_data(perspective)
        self.assertEqual(result, perspective)
    
    def test_validate_perspective_data_missing_field(self):
        """Test perspective validation with missing field."""
        perspective = {
            'title': 'Test Perspective',
            'description': 'Test description'
            # Missing focus_areas
        }
        with self.assertRaises(InputValidationError):
            InputValidator.validate_perspective_data(perspective)
    
    def test_validate_search_parameters_valid(self):
        """Test valid search parameters validation."""
        result = InputValidator.validate_search_parameters("test query", 10)
        self.assertEqual(result, ("test query", 10, None))
    
    def test_validate_search_parameters_invalid_n_results(self):
        """Test search parameters validation with invalid n_results."""
        with self.assertRaises(InputValidationError):
            InputValidator.validate_search_parameters("test query", 0)
    
    def test_validate_search_parameters_too_many_results(self):
        """Test search parameters validation with too many results."""
        with self.assertRaises(InputValidationError):
            InputValidator.validate_search_parameters("test query", 101)
    
    def test_validate_batch_size_valid(self):
        """Test valid batch size validation."""
        result = InputValidator.validate_batch_size(100)
        self.assertEqual(result, 100)
    
    def test_validate_batch_size_invalid(self):
        """Test batch size validation with invalid value."""
        with self.assertRaises(InputValidationError):
            InputValidator.validate_batch_size(0)
    
    def test_validate_batch_size_too_large(self):
        """Test batch size validation with too large value."""
        with self.assertRaises(InputValidationError):
            InputValidator.validate_batch_size(1001)
    
    def test_validate_model_parameters_valid(self):
        """Test valid model parameters validation."""
        result = InputValidator.validate_model_parameters("gpt-4", 0.5, 1000)
        self.assertEqual(result, ("gpt-4", 0.5, 1000))
    
    def test_validate_model_parameters_invalid_model(self):
        """Test model parameters validation with invalid model."""
        with self.assertRaises(InputValidationError):
            InputValidator.validate_model_parameters("invalid-model", 0.5, 1000)
    
    def test_validate_model_parameters_invalid_temperature(self):
        """Test model parameters validation with invalid temperature."""
        with self.assertRaises(InputValidationError):
            InputValidator.validate_model_parameters("gpt-4", 2.5, 1000)
    
    def test_validate_model_parameters_invalid_max_tokens(self):
        """Test model parameters validation with invalid max_tokens."""
        with self.assertRaises(InputValidationError):
            InputValidator.validate_model_parameters("gpt-4", 0.5, 0)


class TestDocumentValidator(unittest.TestCase):
    """Test DocumentValidator class."""
    
    def test_validate_document_format_valid(self):
        """Test valid document format validation."""
        with patch('os.path.exists', return_value=True):
            result = DocumentValidator.validate_document_format("/path/file.docx")
            self.assertEqual(result, "/path/file.docx")
    
    def test_validate_document_format_invalid_extension(self):
        """Test document format validation with invalid extension."""
        with patch('os.path.exists', return_value=True):
            with self.assertRaises(InputValidationError):
                DocumentValidator.validate_document_format("/path/file.xyz")
    
    def test_validate_transcript_name_valid(self):
        """Test valid transcript name validation."""
        result = DocumentValidator.validate_transcript_name("Valid Transcript Name")
        self.assertEqual(result, "Valid Transcript Name")
    
    def test_validate_transcript_name_too_short(self):
        """Test transcript name validation with too short name."""
        with self.assertRaises(DocumentValidationError):
            DocumentValidator.validate_transcript_name("Hi")
    
    def test_validate_transcript_name_with_extension(self):
        """Test transcript name validation with file extension."""
        result = DocumentValidator.validate_transcript_name("Transcript.docx")
        self.assertEqual(result, "Transcript")


class TestConfigurationValidator(unittest.TestCase):
    """Test ConfigurationValidator class."""
    
    def test_validate_prompt_config_valid(self):
        """Test valid prompt config validation."""
        config = {
            'system_messages': {'test': 'message'},
            'quote_ranking': {'template': 'test'},
            'theme_identification': {'template': 'test'}
        }
        result = ConfigurationValidator.validate_prompt_config(config)
        self.assertEqual(result, config)
    
    def test_validate_prompt_config_missing_section(self):
        """Test prompt config validation with missing section."""
        config = {
            'system_messages': {'test': 'message'},
            'quote_ranking': {'template': 'test'}
            # Missing theme_identification
        }
        with self.assertRaises(ConfigurationError):
            ConfigurationValidator.validate_prompt_config(config)
    
    def test_validate_environment_config_valid(self):
        """Test valid environment config validation."""
        config = {'OPENAI_API_KEY': 'sk-test123'}
        result = ConfigurationValidator.validate_environment_config(config)
        self.assertEqual(result, config)
    
    def test_validate_environment_config_missing_key(self):
        """Test environment config validation with missing key."""
        config = {}  # Missing OPENAI_API_KEY
        with self.assertRaises(ConfigurationError):
            ConfigurationValidator.validate_environment_config(config)


class TestJSONExtractor(unittest.TestCase):
    """Test JSONExtractor class."""
    
    def test_extract_json_from_response_simple_json(self):
        """Test extracting simple JSON from response."""
        response = '{"key": "value"}'
        result = JSONExtractor.extract_json_from_response(response)
        self.assertEqual(result, '{"key": "value"}')
    
    def test_extract_json_from_response_with_markdown(self):
        """Test extracting JSON from markdown-wrapped response."""
        response = '```json\n{"key": "value"}\n```'
        result = JSONExtractor.extract_json_from_response(response)
        self.assertEqual(result, '{"key": "value"}')
    
    def test_extract_json_from_response_with_conversation(self):
        """Test extracting JSON from conversational response."""
        response = 'Hello! Here is the JSON: {"key": "value"}'
        result = JSONExtractor.extract_json_from_response(response)
        self.assertEqual(result, '{"key": "value"}')
    
    def test_extract_json_from_response_empty(self):
        """Test extracting JSON from empty response."""
        with self.assertRaises(JSONParsingError):
            JSONExtractor.extract_json_from_response("")
    
    def test_extract_json_from_response_no_json(self):
        """Test extracting JSON from response with no JSON."""
        with self.assertRaises(JSONParsingError):
            JSONExtractor.extract_json_from_response("No JSON here")
    
    def test_extract_json_from_response_nested_structure(self):
        """Test extracting nested JSON structure."""
        response = 'Here is the response: {"nested": {"key": "value"}}'
        result = JSONExtractor.extract_json_from_response(response)
        self.assertEqual(result, '{"nested": {"key": "value"}}')
    
    def test_extract_json_from_response_with_fixes(self):
        """Test extracting JSON that needs common fixes."""
        response = '{"key": "value", "list": [1, 2, 3]}'  # Valid JSON
        result = JSONExtractor.extract_json_from_response(response)
        # Should return valid JSON
        parsed = json.loads(result)
        self.assertIn('key', parsed)
        self.assertIn('list', parsed)


class TestJSONParser(unittest.TestCase):
    """Test JSONParser class."""
    
    def test_parse_json_safe_valid(self):
        """Test safe JSON parsing with valid JSON."""
        result = JSONParser.parse_json_safe('{"key": "value"}', "test context")
        self.assertEqual(result, {"key": "value"})
    
    def test_parse_json_safe_invalid(self):
        """Test safe JSON parsing with invalid JSON."""
        with self.assertRaises(JSONParsingError):
            JSONParser.parse_json_safe('{"key": value}', "test context")
    
    def test_validate_json_structure_valid(self):
        """Test JSON structure validation with valid structure."""
        data = {"key": "value"}
        result = JSONParser.validate_json_structure(data, dict, "test context")
        self.assertEqual(result, data)
    
    def test_validate_json_structure_invalid(self):
        """Test JSON structure validation with invalid structure."""
        data = "not a dict"
        with self.assertRaises(JSONParsingError):
            JSONParser.validate_json_structure(data, dict, "test context")
    
    def test_extract_and_validate_quotes_ranking_valid(self):
        """Test quote ranking extraction and validation with valid data."""
        response = '[{"quote_index": 1, "relevance_score": 8, "relevance_explanation": "test", "key_insight": "insight"}]'
        quotes = [{"text": "Quote 1", "speaker_role": "expert"}]
        
        result = JSONParser.extract_and_validate_quotes_ranking(response, quotes)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['quote_index'], 0)  # Should be converted to 0-based
        self.assertEqual(result[0]['relevance_score'], 8)
    
    def test_extract_and_validate_quotes_ranking_invalid_index(self):
        """Test quote ranking extraction with invalid quote index."""
        response = '[{"quote_index": 999, "relevance_score": 8}]'
        quotes = [{"text": "Quote 1", "speaker_role": "expert"}]
        
        result = JSONParser.extract_and_validate_quotes_ranking(response, quotes)
        self.assertEqual(len(result), 0)  # Invalid index should be filtered out
    
    def test_extract_and_validate_themes_valid(self):
        """Test themes extraction and validation with valid data."""
        response = '[{"name": "Theme 1", "description": "Test theme", "key_insights": ["insight"], "max_quotes": 3}]'
        
        result = JSONParser.extract_and_validate_themes(response)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], "Theme 1")
        self.assertEqual(result[0]['max_quotes'], 3)
    
    def test_extract_and_validate_themes_missing_name(self):
        """Test themes extraction with missing name field."""
        response = '[{"description": "Test theme"}]'  # Missing name
        
        result = JSONParser.extract_and_validate_themes(response)
        self.assertEqual(len(result), 0)  # Invalid theme should be filtered out


if __name__ == '__main__':
    unittest.main()
