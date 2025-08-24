#!/usr/bin/env python3
"""
Unit tests for QuoteProcessor module
"""

import unittest
from unittest.mock import patch, Mock
from datetime import datetime
import sys
import os

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from quote_processing import QuoteProcessor


class TestQuoteProcessor(unittest.TestCase):
    """Test cases for QuoteProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = QuoteProcessor()
        
        # Sample quote data for testing
        self.sample_quote = {
            "text": "FlexXray provides excellent service quality and rapid turnaround times.",
            "transcript_name": "John Doe - Acme Corp - Manager.docx",
            "speaker_role": "expert",
            "relevance_score": 0.85
        }
        
        self.complex_quote = {
            "text": "The market leadership position and competitive advantages are clear.",
            "transcript_name": "Jane Smith - Former CEO - Follow Up (07.22.2025).docx",
            "speaker_role": "expert",
            "focus_area_matched": "competitive advantages"
        }
    
    def test_init(self):
        """Test QuoteProcessor initialization."""
        self.assertIsInstance(self.processor.theme_keywords, dict)
        self.assertIn("market_leadership", self.processor.theme_keywords)
        self.assertIn("technology_advantages", self.processor.theme_keywords)
        self.assertEqual(len(self.processor.theme_keywords), 10)
    
    def test_add_speaker_info_three_parts(self):
        """Test speaker info extraction with three-part filename."""
        quote = {"transcript_name": "John Doe - Acme Corp - Manager.docx"}
        result = self.processor._add_speaker_info(quote)
        
        self.assertEqual(result["speaker_info"]["name"], "John Doe")
        self.assertEqual(result["speaker_info"]["company"], "Acme Corp")
        self.assertEqual(result["speaker_info"]["title"], "Manager.docx")
    
    def test_add_speaker_info_two_parts(self):
        """Test speaker info extraction with two-part filename."""
        quote = {"transcript_name": "Jane Smith - Acme Corp"}
        result = self.processor._add_speaker_info(quote)
        
        self.assertEqual(result["speaker_info"]["name"], "Jane Smith")
        self.assertEqual(result["speaker_info"]["company"], "Acme Corp")
        self.assertEqual(result["speaker_info"]["title"], "")
    
    def test_add_speaker_info_one_part(self):
        """Test speaker info extraction with one-part filename."""
        quote = {"transcript_name": "John Doe"}
        result = self.processor._add_speaker_info(quote)
        
        self.assertEqual(result["speaker_info"]["name"], "John Doe")
        self.assertEqual(result["speaker_info"]["company"], "")
        self.assertEqual(result["speaker_info"]["title"], "")
    
    def test_add_speaker_info_former_title(self):
        """Test speaker info extraction with 'Former' in company field."""
        quote = {"transcript_name": "John Doe - Former CEO - Manager.docx"}
        result = self.processor._add_speaker_info(quote)
        
        self.assertEqual(result["speaker_info"]["name"], "John Doe")
        self.assertEqual(result["speaker_info"]["company"], "")
        self.assertEqual(result["speaker_info"]["title"], "Former CEO - Manager.docx")
    
    def test_add_speaker_info_randy_jesberg_case(self):
        """Test special handling for Randy_Jesberg case."""
        quote = {"transcript_name": "Randy_Jesberg - Former CEO - Follow Up (07.22.2025).docx"}
        result = self.processor._add_speaker_info(quote)
        
        self.assertEqual(result["speaker_info"]["name"], "Randy_Jesberg - Former CEO")
        self.assertEqual(result["speaker_info"]["company"], "")
        self.assertEqual(result["speaker_info"]["title"], "")
    
    def test_add_speaker_info_conversation_identifier(self):
        """Test handling of conversation identifiers in company field."""
        quote = {"transcript_name": "John Doe - Initial Conversation - Manager.docx"}
        result = self.processor._add_speaker_info(quote)
        
        self.assertEqual(result["speaker_info"]["name"], "John Doe")
        self.assertEqual(result["speaker_info"]["company"], "")
        self.assertEqual(result["speaker_info"]["title"], "Initial Conversation - Manager.docx")
    
    def test_add_sentiment_analysis(self):
        """Test sentiment analysis addition."""
        quote = {"text": "This is a test quote"}
        result = self.processor._add_sentiment_analysis(quote)
        
        self.assertEqual(result["sentiment"], "neutral")
    
    def test_add_theme_categorization_market_leadership(self):
        """Test theme categorization for market leadership."""
        quote = {"text": "The market position and competitive advantages are strong"}
        result = self.processor._add_theme_categorization(quote)
        
        self.assertEqual(result["theme"], "market_leadership")
    
    def test_add_theme_categorization_technology(self):
        """Test theme categorization for technology advantages."""
        quote = {"text": "The proprietary technology and innovation capabilities are excellent"}
        result = self.processor._add_theme_categorization(quote)
        
        self.assertEqual(result["theme"], "technology_advantages")
    
    def test_add_theme_categorization_from_focus_area(self):
        """Test theme categorization from focus area."""
        quote = {
            "text": "Some generic text",
            "focus_area_matched": "competitive advantages"
        }
        result = self.processor._add_theme_categorization(quote)
        
        self.assertEqual(result["theme"], "market_leadership")
    
    def test_add_theme_categorization_general_fallback(self):
        """Test theme categorization fallback to general."""
        quote = {"text": "Some completely unrelated text"}
        result = self.processor._add_theme_categorization(quote)
        
        self.assertEqual(result["theme"], "general")
    
    def test_add_date_information_from_filename_dot_format(self):
        """Test date extraction from filename with dot format."""
        quote = {"transcript_name": "John Doe - Follow Up (07.22.2025).docx"}
        result = self.processor._add_date_information(quote)
        
        self.assertEqual(result["date"], "2025-07-22")
    
    def test_add_date_information_from_filename_dash_format(self):
        """Test date extraction from filename with dash format."""
        quote = {"transcript_name": "John Doe - Follow Up (2025-07-22).docx"}
        result = self.processor._add_date_information(quote)
        
        self.assertEqual(result["date"], "2025-07-22")
    
    def test_add_date_information_from_filename_slash_format(self):
        """Test date extraction from filename with slash format."""
        quote = {"transcript_name": "John Doe - Follow Up (07/22/2025).docx"}
        result = self.processor._add_date_information(quote)
        
        self.assertEqual(result["date"], "2025-07-22")
    
    def test_add_date_information_from_metadata_timestamp(self):
        """Test date extraction from metadata timestamp."""
        quote = {
            "transcript_name": "John Doe.docx",
            "metadata": {"timestamp": 1640995200}  # 2022-01-01
        }
        result = self.processor._add_date_information(quote)
        
        # The timestamp 1640995200 corresponds to 2022-01-01 00:00:00 UTC
        # but may be different in local timezone, so we'll check it's a valid date
        self.assertIsInstance(result["date"], str)
        self.assertRegex(result["date"], r"^\d{4}-\d{2}-\d{2}$")
        # Verify it's a reasonable date (not too far from expected)
        # The timestamp could be 2021-12-31 or 2022-01-01 depending on timezone
        self.assertIn(result["date"], ["2021-12-31", "2022-01-01"])
    
    def test_add_date_information_fallback_to_current(self):
        """Test date extraction fallback to current date."""
        quote = {"transcript_name": "John Doe.docx"}
        
        with patch('quote_processing.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 1, 1)
            result = self.processor._add_date_information(quote)
        
        self.assertEqual(result["date"], "2025-01-01")
    
    def test_ensure_required_fields_complete(self):
        """Test ensuring required fields with complete quote."""
        quote = {
            "text": "Test quote",
            "transcript_name": "test.docx",
            "relevance_score": 0.8
        }
        result = self.processor._ensure_required_fields(quote)
        
        self.assertIn("id", result)
        self.assertIn("speaker_info", result)
        self.assertIn("sentiment", result)
        self.assertIn("theme", result)
        self.assertIn("date", result)
        self.assertIn("speaker_role", result)
        self.assertEqual(result["relevance_score"], 0.8)
    
    def test_ensure_required_fields_missing_relevance_score(self):
        """Test ensuring required fields with missing relevance score."""
        quote = {"text": "Test quote"}
        result = self.processor._ensure_required_fields(quote)
        
        self.assertEqual(result["relevance_score"], 0.0)
    
    def test_ensure_required_fields_string_relevance_score(self):
        """Test ensuring required fields with string relevance score."""
        quote = {"text": "Test quote", "relevance_score": "0.8"}
        result = self.processor._ensure_required_fields(quote)
        
        self.assertEqual(result["relevance_score"], 0.8)
    
    def test_ensure_required_fields_invalid_relevance_score(self):
        """Test ensuring required fields with invalid relevance score."""
        quote = {"text": "Test quote", "relevance_score": "invalid"}
        result = self.processor._ensure_required_fields(quote)
        
        self.assertEqual(result["relevance_score"], 0.0)
    
    def test_enrich_quotes_for_export(self):
        """Test complete quote enrichment process."""
        quotes = [self.sample_quote.copy()]
        result = self.processor.enrich_quotes_for_export(quotes)
        
        self.assertEqual(len(result), 1)
        enriched_quote = result[0]
        
        # Check that all required fields are present
        self.assertIn("speaker_info", enriched_quote)
        self.assertIn("sentiment", enriched_quote)
        self.assertIn("theme", enriched_quote)
        self.assertIn("date", enriched_quote)
        self.assertIn("id", enriched_quote)
        
        # Check specific values
        self.assertEqual(enriched_quote["sentiment"], "neutral")
        self.assertEqual(enriched_quote["theme"], "service_quality")
        self.assertEqual(enriched_quote["speaker_info"]["name"], "John Doe")
        self.assertEqual(enriched_quote["speaker_info"]["company"], "Acme Corp")
    
    def test_enrich_quotes_for_export_empty_list(self):
        """Test quote enrichment with empty list."""
        result = self.processor.enrich_quotes_for_export([])
        
        self.assertEqual(result, [])
    
    def test_format_quote_for_display_complete(self):
        """Test quote formatting with complete information."""
        quote = {
            "text": "Test quote text",
            "speaker_info": {"name": "John Doe", "company": "Acme Corp", "title": "Manager"},
            "transcript_name": "test.docx"
        }
        result = self.processor.format_quote_for_display(quote)
        
        expected = '"Test quote text" - John Doe, Acme Corp, Manager from test.docx'
        self.assertEqual(result, expected)
    
    def test_format_quote_for_display_partial_info(self):
        """Test quote formatting with partial speaker information."""
        quote = {
            "text": "Test quote text",
            "speaker_info": {"name": "John Doe", "company": "", "title": ""},
            "transcript_name": "test.docx"
        }
        result = self.processor.format_quote_for_display(quote)
        
        expected = '"Test quote text" - John Doe from test.docx'
        self.assertEqual(result, expected)
    
    def test_format_quote_for_display_no_transcript(self):
        """Test quote formatting without transcript name."""
        quote = {
            "text": "Test quote text",
            "speaker_info": {"name": "John Doe", "company": "Acme Corp", "title": "Manager"},
            "transcript_name": "Unknown"
        }
        result = self.processor.format_quote_for_display(quote)
        
        expected = '"Test quote text" - John Doe, Acme Corp, Manager'
        self.assertEqual(result, expected)
    
    def test_format_quote_for_display_empty_quote(self):
        """Test quote formatting with empty quote."""
        result = self.processor.format_quote_for_display({})
        
        self.assertEqual(result, "")
    
    def test_get_quote_statistics_empty_list(self):
        """Test statistics calculation with empty quote list."""
        result = self.processor.get_quote_statistics([])
        
        expected = {
            "total_quotes": 0,
            "themes": {},
            "speaker_roles": {},
            "transcripts": {},
            "average_length": 0
        }
        self.assertEqual(result, expected)
    
    def test_get_quote_statistics_with_quotes(self):
        """Test statistics calculation with actual quotes."""
        quotes = [
            {
                "text": "First quote about market leadership",
                "theme": "market_leadership",
                "speaker_role": "expert",
                "transcript_name": "transcript1.docx"
            },
            {
                "text": "Second quote about technology",
                "theme": "technology_advantages",
                "speaker_role": "expert",
                "transcript_name": "transcript2.docx"
            }
        ]
        
        result = self.processor.get_quote_statistics(quotes)
        
        self.assertEqual(result["total_quotes"], 2)
        self.assertEqual(result["themes"]["market_leadership"], 1)
        self.assertEqual(result["themes"]["technology_advantages"], 1)
        self.assertEqual(result["speaker_roles"]["expert"], 2)
        self.assertEqual(result["transcripts"]["transcript1.docx"], 1)
        self.assertEqual(result["transcripts"]["transcript2.docx"], 1)
        self.assertGreater(result["average_length"], 0)
    
    def test_get_quote_statistics_missing_fields(self):
        """Test statistics calculation with quotes missing some fields."""
        quotes = [
            {"text": "Quote with missing fields"},
            {"text": "Another quote", "theme": "market_leadership"}
        ]
        
        result = self.processor.get_quote_statistics(quotes)
        
        self.assertEqual(result["total_quotes"], 2)
        self.assertEqual(result["themes"]["unknown"], 1)
        self.assertEqual(result["themes"]["market_leadership"], 1)
        self.assertEqual(result["speaker_roles"]["unknown"], 2)
        self.assertEqual(result["transcripts"]["unknown"], 2)


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)
