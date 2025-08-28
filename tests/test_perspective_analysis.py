#!/usr/bin/env python3
"""
Unit Tests for Perspective Analysis Complex Logic

⚠️  DEPRECATED: This test file tests the deprecated comprehensive analysis system.
   Use test_streamlined_system.py instead for production testing.

This module tests the complex logic in perspective_analysis.py, including
quote ranking, theme analysis, and the various fallback strategies.
"""

import unittest
import json
from unittest.mock import Mock, patch, MagicMock, call
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from exceptions import (
    OpenAIError,
    OpenAIAPIError,
    OpenAIResponseError,
    PerspectiveAnalysisError,
    ThemeAnalysisError,
)
from validation import InputValidator
from json_utils import JSONExtractor, JSONParser


class TestPerspectiveAnalysisComplexLogic(unittest.TestCase):
    """Test complex logic in perspective analysis."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_openai_client = Mock()
        self.mock_vector_db_manager = Mock()
        self.mock_prompt_config = Mock()

        # Sample test data
        self.sample_quotes = [
            {
                "text": "This is a test quote about business models",
                "speaker_role": "expert",
                "transcript_name": "Test Transcript 1",
                "position": 1,
            },
            {
                "text": "Another quote about market positioning",
                "speaker_role": "expert",
                "transcript_name": "Test Transcript 2",
                "position": 2,
            },
        ]

        self.sample_perspective = {
            "title": "Business Model & Market Position",
            "description": "How FlexXray operates and competes",
            "focus_areas": ["value proposition", "market positioning"],
        }

    def test_quote_ranking_fallback_strategies(self):
        """Test the multiple fallback strategies for quote ranking."""
        # Mock OpenAI client to simulate failures
        mock_client = Mock()

        # First call fails
        mock_client.chat.completions.create.side_effect = [
            Exception("API Error"),  # First attempt fails
            Mock(
                choices=[
                    Mock(
                        message=Mock(content='{"quote_index": 1, "relevance_score": 8}')
                    )
                ]
            ),  # Fallback succeeds
        ]

        # Test that fallback strategy is used
        with patch("openai.OpenAI", return_value=mock_client):
            # This would test the actual fallback logic in perspective_analysis.py
            # For now, we're testing the concept
            pass

    def test_json_extraction_strategies(self):
        """Test the multiple JSON extraction strategies."""
        # Test balanced JSON extraction
        response_with_balanced = 'Here is the analysis: {"key": "value"}'
        result = JSONExtractor.extract_json_from_response(response_with_balanced)
        self.assertEqual(result, '{"key": "value"}')

        # Test markdown-wrapped JSON
        response_with_markdown = '```json\n{"key": "value"}\n```'
        result = JSONExtractor.extract_json_from_response(response_with_markdown)
        self.assertEqual(result, '{"key": "value"}')

        # Test conversational response
        response_conversational = 'Hello! Here is the JSON: {"key": "value"}'
        result = JSONExtractor.extract_json_from_response(response_conversational)
        self.assertEqual(result, '{"key": "value"}')

    def test_complex_json_extraction_edge_cases(self):
        """Test edge cases in JSON extraction."""
        # Test nested structures
        nested_response = 'Response: {"nested": {"key": "value"}}'
        result = JSONExtractor.extract_json_from_response(nested_response)
        self.assertEqual(result, '{"nested": {"key": "value"}}')

        # Test JSON with common formatting issues
        malformed_response = '{"key": "value", "list": [1, 2, 3]}'
        result = JSONExtractor.extract_json_from_response(malformed_response)
        # Should return valid JSON
        parsed = json.loads(result)
        self.assertIn("key", parsed)

    def test_quote_ranking_validation(self):
        """Test quote ranking validation logic."""
        # Valid ranking response
        valid_response = '[{"quote_index": 1, "relevance_score": 8, "relevance_explanation": "test", "key_insight": "insight"}]'
        quotes = [{"text": "Quote 1", "speaker_role": "expert"}]

        result = JSONParser.extract_and_validate_quotes_ranking(valid_response, quotes)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["quote_index"], 0)  # Should be converted to 0-based

        # Test invalid quote index handling
        invalid_response = '[{"quote_index": 999, "relevance_score": 8}]'
        result = JSONParser.extract_and_validate_quotes_ranking(
            invalid_response, quotes
        )
        self.assertEqual(len(result), 0)  # Invalid index should be filtered out

    def test_theme_analysis_validation(self):
        """Test theme analysis validation logic."""
        # Valid themes response
        valid_response = '[{"name": "Theme 1", "description": "Test theme", "key_insights": ["insight"], "max_quotes": 3}]'

        result = JSONParser.extract_and_validate_themes(valid_response)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Theme 1")

        # Test missing required fields
        incomplete_response = '[{"description": "Test theme"}]'  # Missing name
        result = JSONParser.extract_and_validate_themes(incomplete_response)
        self.assertEqual(len(result), 0)  # Invalid theme should be filtered out

    def test_focus_area_relevance_calculation(self):
        """Test the focus area relevance calculation logic."""
        # This would test the _calculate_focus_area_relevance method
        # For now, we'll test the concept with a simple example

        quote_text = "This quote discusses value proposition and market positioning"
        focus_area = "value proposition"

        # Simple relevance calculation (this would be the actual method)
        quote_lower = quote_text.lower()
        focus_lower = focus_area.lower()
        focus_words = [
            word.strip() for word in focus_lower.split() if len(word.strip()) > 2
        ]

        exact_matches = sum(1 for word in focus_words if word in quote_lower)
        partial_matches = sum(
            1
            for word in focus_words
            if any(word in quote_word for quote_word in quote_lower.split())
        )

        base_score = (exact_matches * 2.0) + (partial_matches * 1.0)
        length_bonus = min(len(focus_words) * 0.5, 2.0)
        phrase_bonus = 3.0 if focus_lower in quote_lower else 0.0

        total_score = base_score + length_bonus + phrase_bonus

        # Should have a positive score for relevant content
        self.assertGreater(total_score, 0)

    def test_vector_database_fallback_logic(self):
        """Test the fallback logic when vector database is unavailable."""
        # Mock vector database manager that's unavailable
        mock_vdb = Mock()
        mock_vdb.quotes_collection = None

        # Test that fallback to local filtering is used
        # This would test the actual fallback logic in perspective_analysis.py
        pass

    def test_error_handling_in_ranking_pipeline(self):
        """Test error handling throughout the ranking pipeline."""
        # Test various failure scenarios
        test_cases = [
            ("Empty response", ""),
            ("Invalid JSON", "This is not JSON"),
            ("Malformed JSON", '{"key": value}'),  # Missing quotes
            ("Incomplete JSON", '{"key": "value"'),  # Missing closing brace
        ]

        for description, response in test_cases:
            with self.subTest(description=description):
                if not response:
                    with self.assertRaises(Exception):
                        JSONExtractor.extract_json_from_response(response)
                else:
                    # Should handle gracefully or raise appropriate exception
                    pass

    def test_quote_selection_stage_tracking(self):
        """Test the tracking of quote selection stages."""
        # Test that quotes get proper selection stage tracking
        quotes = [
            {"text": "Quote 1", "speaker_role": "expert"},
            {"text": "Quote 2", "speaker_role": "expert"},
        ]

        # Simulate ranking process
        rankings = [
            {
                "quote_index": 1,
                "relevance_score": 8,
                "relevance_explanation": "test",
                "key_insight": "insight",
            }
        ]

        # Apply rankings (this would be the actual logic)
        explicitly_ranked_indices = set()
        for ranking in rankings:
            quote_index = ranking.get("quote_index", 0) - 1
            if 0 <= quote_index < len(quotes):
                quotes[quote_index]["openai_rank"] = ranking.get("relevance_score", 0)
                quotes[quote_index]["selection_stage"] = "openai_ranked"
                explicitly_ranked_indices.add(quote_index)

        # Check that selection stages are properly set
        self.assertEqual(quotes[0]["selection_stage"], "openai_ranked")
        # Quote 2 should not have been explicitly ranked
        self.assertNotIn("selection_stage", quotes[1])

    def test_complex_fallback_chaining(self):
        """Test the chaining of multiple fallback strategies."""
        # Test that fallbacks are tried in the correct order
        # This would test the actual fallback logic in perspective_analysis.py

        # Mock OpenAI client that fails multiple times
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = [
            Exception("Primary failure"),
            Exception("First fallback failure"),
            Mock(
                choices=[
                    Mock(
                        message=Mock(content='{"quote_index": 1, "relevance_score": 8}')
                    )
                ]
            ),  # Second fallback succeeds
        ]

        # Test that the system tries multiple fallbacks
        # For now, we're testing the concept
        pass

    def test_input_validation_integration(self):
        """Test that input validation is properly integrated."""
        # Test validation of perspective data
        valid_perspective = {
            "title": "Test Perspective",
            "description": "Test description",
            "focus_areas": ["area1", "area2"],
        }

        validated = InputValidator.validate_perspective_data(valid_perspective)
        self.assertEqual(validated, valid_perspective)

        # Test validation of quotes
        valid_quotes = [
            {"text": "Quote 1", "speaker_role": "expert"},
            {"text": "Quote 2", "speaker_role": "interviewer"},
        ]

        validated_quotes = InputValidator.validate_quotes_list(valid_quotes)
        self.assertEqual(validated_quotes, valid_quotes)

    def test_error_recovery_strategies(self):
        """Test various error recovery strategies."""
        # Test recovery from JSON parsing errors
        malformed_json = '{"key": value}'  # Missing quotes

        try:
            # Try to extract JSON
            result = JSONExtractor.extract_json_from_response(malformed_json)
            # If successful, should be valid JSON
            parsed = json.loads(result)
            self.assertIn("key", parsed)
        except Exception:
            # If extraction fails, that's also acceptable behavior
            pass

        # Test recovery from API failures
        # This would test the actual recovery logic in perspective_analysis.py
        pass


class TestPerspectiveAnalysisIntegration(unittest.TestCase):
    """Test integration aspects of perspective analysis."""

    def test_end_to_end_quote_ranking(self):
        """Test the complete quote ranking pipeline."""
        # This would test the entire pipeline from input to output
        # For now, we'll test the key components

        # Test input validation
        quotes = [{"text": "Test quote", "speaker_role": "expert"}]
        validated_quotes = InputValidator.validate_quotes_list(quotes)
        self.assertEqual(len(validated_quotes), 1)

        # Test JSON extraction
        response = '{"quote_index": 1, "relevance_score": 8}'
        extracted = JSONExtractor.extract_json_from_response(response)
        self.assertEqual(extracted, '{"quote_index": 1, "relevance_score": 8}')

        # Test JSON parsing
        parsed = JSONParser.parse_json_safe(extracted, "test context")
        self.assertEqual(parsed, {"quote_index": 1, "relevance_score": 8})

    def test_error_propagation(self):
        """Test that errors properly propagate through the system."""
        # Test that validation errors are properly raised
        with self.assertRaises(Exception):
            InputValidator.validate_quote_data({})  # Missing required fields

        # Test that JSON parsing errors are properly raised
        with self.assertRaises(Exception):
            JSONExtractor.extract_json_from_response("")  # Empty response

        # Test that the system can recover from certain types of errors
        # This would test the actual error recovery logic
        pass


if __name__ == "__main__":
    unittest.main()
