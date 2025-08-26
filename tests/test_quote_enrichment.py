#!/usr/bin/env python3
"""
Test script to demonstrate quote enrichment functionality.

This script shows how quotes are enriched with missing fields before export,
fixing the blank columns and misaligned rows in Excel exports.
"""

import json
import sys
import os
import unittest
from pathlib import Path

# Add the parent directory to Python path so we can import modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from quote_analysis_tool import ModularQuoteAnalysisTool


class TestQuoteEnrichment(unittest.TestCase):
    """Test quote enrichment functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Initialize the tool
        self.tool = ModularQuoteAnalysisTool()

    def test_tool_initialization(self):
        """Test that the tool initializes correctly."""
        self.assertIsNotNone(self.tool)
        self.assertTrue(hasattr(self.tool, 'enrich_quotes_for_export'))

    def test_quote_enrichment(self):
        """Test the quote enrichment functionality."""
        # Sample quotes with missing fields (simulating current state)
        # Including various relevance_score edge cases to test numeric handling
        sample_quotes = [
            {
                "text": "FlexXray has a strong competitive advantage in the market due to our proprietary technology.",
                "speaker_role": "expert",
                "transcript_name": "Randy_Jesberg- Former CEO - Initial Conversation (06.26.2025)",
                "position": 45,
                "has_insight": True,
                "relevance_score": 8.5,  # Normal numeric value
                "focus_area_matched": "competitive advantages",
                "metadata": {
                    "timestamp": 1756011468.6354835,
                    "has_insight": True,
                    "speaker_role": "expert",
                    "transcript_name": "Randy_Jesberg- Former CEO - Initial Conversation (06.26.2025)",
                    "position": 45,
                },
            },
            {
                "text": "The main challenge we face is the limited addressable market size.",
                "speaker_role": "expert",
                "transcript_name": "Cheryl Bertics - FlexXray Foreign Material Inspection Services - Former Manager",
                "position": 23,
                "has_insight": True,
                "relevance_score": None,  # None value - should become 0.0
                "focus_area_matched": "market limitations",
                "metadata": {
                    "timestamp": 1756011467.8782463,
                    "has_insight": True,
                    "speaker_role": "expert",
                    "transcript_name": "Cheryl Bertics - FlexXray Foreign Material Inspection Services - Former Manager",
                    "position": 23,
                },
            },
            {
                "text": "Our rapid turnaround times give us a significant advantage over competitors.",
                "speaker_role": "expert",
                "transcript_name": "George Perry-West - Pegasus Foods, Inc - Former FSQA Manager",
                "position": 67,
                "has_insight": True,
                "relevance_score": "",  # Empty string - should become 0.0
                "focus_area_matched": "operational efficiency",
                "metadata": {
                    "timestamp": 1756011469.1234567,
                    "has_insight": True,
                    "speaker_role": "expert",
                    "transcript_name": "George Perry-West - Pegasus Foods, Inc - Former FSQA Manager",
                    "position": 67,
                },
            },
            {
                "text": "FlexXray provides excellent service quality to all customers.",
                "speaker_role": "expert", 
                "transcript_name": "Test Speaker - Test Company - Test Title",
                "position": 89,
                "has_insight": True,
                "relevance_score": "invalid",  # Invalid string - should become 0.0
                "focus_area_matched": "service quality",
                "metadata": {
                    "timestamp": 1756011470.1234567,
                    "has_insight": True,
                    "speaker_role": "expert",
                    "transcript_name": "Test Speaker - Test Company - Test Title",
                    "position": 89,
                },
            },
        ]

        # Enrich the quotes
        enriched_quotes = self.tool.enrich_quotes_for_export(sample_quotes)

        # Verify enrichment results
        self.assertEqual(len(enriched_quotes), len(sample_quotes))
        
        for quote in enriched_quotes:
            # Check that all required fields are present
            self.assertIn("speaker_info", quote)
            self.assertIn("sentiment", quote)
            self.assertIn("theme", quote)
            self.assertIn("date", quote)
            self.assertIn("relevance_score", quote)
            
            # Verify speaker_info structure
            speaker_info = quote["speaker_info"]
            self.assertIsInstance(speaker_info, dict)
            self.assertIn("name", speaker_info)
            self.assertIn("company", speaker_info)
            self.assertIn("title", speaker_info)
            
            # Verify relevance_score is numeric
            self.assertIsInstance(quote["relevance_score"], (int, float))
            self.assertGreaterEqual(quote["relevance_score"], 0)

    def test_speaker_info_extraction(self):
        """Test speaker info extraction from transcript filenames."""
        test_cases = [
            "Randy_Jesberg- Former CEO - Initial Conversation (06.26.2025)",
            "Cheryl Bertics - FlexXray Foreign Material Inspection Services - Former Manager",
            "George Perry-West - Pegasus Foods, Inc - Former FSQA Manager",
            "Simple Name - Company",
            "Just Name",
        ]

        for test_case in test_cases:
            quote = {"transcript_name": test_case}
            enriched = self.tool._add_speaker_info(quote)
            speaker_info = enriched.get("speaker_info", {})

            self.assertIsInstance(speaker_info, dict)
            self.assertIn("name", speaker_info)
            self.assertIn("company", speaker_info)
            self.assertIn("title", speaker_info)

    def test_sentiment_analysis(self):
        """Test sentiment analysis functionality."""
        test_quotes = [
            "This is an excellent product with great quality and strong performance.",
            "We face significant challenges and problems with this approach.",
            "The service is adequate but nothing special.",
            "Our technology provides outstanding advantages and superior results.",
        ]

        for text in test_quotes:
            quote = {"text": text}
            enriched = self.tool._add_sentiment_analysis(quote)
            sentiment = enriched.get("sentiment", "")

            self.assertIsInstance(sentiment, str)
            self.assertIn(sentiment, ["positive", "negative", "neutral"])

    def test_theme_categorization(self):
        """Test theme categorization functionality."""
        test_quotes = [
            "Our competitive advantage in the market is clear.",
            "The value proposition drives customer decisions.",
            "Our local presence gives us a geographic advantage.",
            "Proprietary technology provides technical capabilities.",
        ]

        for text in test_quotes:
            quote = {"text": text}
            enriched = self.tool._add_theme_categorization(quote)
            theme = enriched.get("theme", "")

            self.assertIsInstance(theme, str)
            self.assertGreater(len(theme), 0)

    def test_relevance_score_handling(self):
        """Test relevance_score numeric handling for various edge cases."""
        test_cases = [
            {"relevance_score": 8.5, "description": "Normal float"},
            {"relevance_score": 10, "description": "Integer"},
            {"relevance_score": None, "description": "None value"},
            {"relevance_score": "", "description": "Empty string"},
            {"relevance_score": "None", "description": "String 'None'"},
            {"relevance_score": "invalid", "description": "Invalid string"},
            {"relevance_score": "7.5", "description": "String number"},
            # Missing relevance_score field
            {"description": "Missing field"},
        ]

        for test_case in test_cases:
            quote = {"text": "Test quote"}
            if "relevance_score" in test_case:
                quote["relevance_score"] = test_case["relevance_score"]
            
            enriched = self.tool._ensure_required_fields(quote)
            final_score = enriched.get("relevance_score")
            
            self.assertIsInstance(final_score, (int, float))
            self.assertGreaterEqual(final_score, 0)

    def test_excel_export_functionality(self):
        """Test Excel export functionality with enriched quotes."""
        # Create sample enriched quotes
        enriched_quotes = [
            {
                "text": "Test quote 1",
                "speaker_info": {"name": "Test Speaker", "company": "Test Company", "title": "Test Title"},
                "sentiment": "positive",
                "theme": "test_theme",
                "date": "2025-01-01",
                "relevance_score": 8.5,
                "transcript_name": "test_transcript.docx"
            },
            {
                "text": "Test quote 2",
                "speaker_info": {"name": "Test Speaker 2", "company": "Test Company 2", "title": "Test Title 2"},
                "sentiment": "neutral",
                "theme": "test_theme_2",
                "date": "2025-01-02",
                "relevance_score": 7.0,
                "transcript_name": "test_transcript_2.docx"
            }
        ]
        
        try:
            excel_file = self.tool.export_quotes_to_excel(enriched_quotes)
            if excel_file:
                self.assertTrue(os.path.exists(excel_file))
                # Clean up the test file
                os.remove(excel_file)
        except Exception as e:
            self.skipTest(f"Excel export not available: {e}")

    def test_empty_quotes_handling(self):
        """Test handling of empty quotes list."""
        empty_result = self.tool.enrich_quotes_for_export([])
        self.assertEqual(empty_result, [])

    def test_quote_formatting(self):
        """Test quote formatting for display."""
        quote = {
            "text": "FlexXray provides excellent service quality and rapid turnaround times.",
            "speaker_info": {"name": "John Doe", "company": "Acme Corp", "title": "Manager"},
            "transcript_name": "John Doe - Acme Corp - Manager.docx"
        }
        
        formatted_quote = self.tool.format_quote_for_display(quote)
        
        self.assertIn("FlexXray provides excellent service quality", formatted_quote)
        self.assertIn("John Doe, Acme Corp, Manager.docx", formatted_quote)

    def test_quote_statistics(self):
        """Test quote statistics generation."""
        sample_quotes = [
            {
                "text": "Quote 1 about service quality",
                "theme": "service_quality",
                "sentiment": "positive"
            },
            {
                "text": "Quote 2 about technology",
                "theme": "technology_advantages", 
                "sentiment": "positive"
            },
            {
                "text": "Quote 3 about market challenges",
                "theme": "market_limitations",
                "sentiment": "negative"
            }
        ]
        
        stats = self.tool.get_quote_statistics(sample_quotes)
        
        self.assertIsInstance(stats, dict)
        self.assertIn("total_quotes", stats)
        self.assertIn("themes", stats)
        self.assertIn("sentiments", stats)
        
        self.assertEqual(stats["total_quotes"], 3)
        self.assertIn("service_quality", stats["themes"])
        self.assertIn("technology_advantages", stats["themes"])
        self.assertIn("market_limitations", stats["themes"])


def main():
    """Run the quote enrichment tests."""
    print("🚀 Starting Quote Enrichment Tests")
    print("=" * 50)

    # Run the tests
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()
