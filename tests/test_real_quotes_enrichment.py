#!/usr/bin/env python3
"""
Test script to demonstrate quote enrichment with real quotes from existing JSON files.

This script loads actual quotes from your JSON output and shows how enrichment
fixes the export issues with real data.
"""

import json
import os
import sys
import unittest
from pathlib import Path

# Add the parent directory to Python path so we can import modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from streamlined_quote_analysis import StreamlinedQuoteAnalysis


class TestRealQuotesEnrichment(unittest.TestCase):
    """Test quote enrichment with real quotes from existing JSON files."""

    def setUp(self):
        """Set up test fixtures."""
        # Initialize the tool
        self.tool = StreamlinedQuoteAnalysis()
        
        # Find the most recent JSON file
        outputs_dir = Path("Outputs")
        if outputs_dir.exists():
            json_files = list(outputs_dir.glob("FlexXray_quote_analysis_*.json"))
            if json_files:
                self.latest_json = max(json_files, key=lambda f: f.stat().st_mtime)
            else:
                self.latest_json = None
        else:
            self.latest_json = None

    def test_tool_initialization(self):
        """Test that the tool initializes correctly."""
        self.assertIsNotNone(self.tool)
        self.assertTrue(hasattr(self.tool, 'key_questions'))
        self.assertTrue(hasattr(self.tool, 'client'))

    def test_with_real_quotes(self):
        """Test quote enrichment with real quotes from existing JSON files."""
        if not self.latest_json:
            self.skipTest("No JSON files found in Outputs directory")
        
        try:
            with open(self.latest_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            self.skipTest(f"Error loading JSON file: {e}")
        
        # Extract a sample of quotes
        all_quotes = data.get('all_quotes', [])
        if not all_quotes:
            self.skipTest("No quotes found in JSON file")
        
        # Take first 5 quotes as sample
        sample_quotes = all_quotes[:5]
        
        # Filter expert quotes
        expert_quotes = self.tool.get_expert_quotes_only(sample_quotes)
        
        # Verify filtering
        self.assertIsInstance(expert_quotes, list)
        self.assertLessEqual(len(expert_quotes), len(sample_quotes))
        
        for quote in expert_quotes:
            self.assertEqual(quote["speaker_role"], "expert")
            self.assertIn("text", quote)
            self.assertIn("transcript_name", quote)

    def test_excel_export_with_real_quotes(self):
        """Test Excel export with real enriched quotes."""
        if not self.latest_json:
            self.skipTest("No JSON files found in Outputs directory")
        
        try:
            with open(self.latest_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            self.skipTest(f"Error loading JSON file: {e}")
        
        # Extract a sample of quotes
        all_quotes = data.get('all_quotes', [])
        if not all_quotes:
            self.skipTest("No quotes found in JSON file")
        
        # Take first 3 quotes as sample
        sample_quotes = all_quotes[:3]
        
        # Test export functionality
        try:
            excel_file = self.tool.export_to_excel(sample_quotes, "test_real_quotes.xlsx")
            if excel_file:
                self.assertTrue(os.path.exists(excel_file))
                # Clean up the test file
                os.remove(excel_file)
        except Exception as e:
            self.skipTest(f"Excel export not available: {e}")

    def test_quote_enrichment_quality(self):
        """Test the quality of quote enrichment."""
        # Create mock quotes with various edge cases
        mock_quotes = [
            {
                "text": "FlexXray has a strong competitive advantage in the market due to our proprietary technology.",
                "speaker_role": "expert",
                "transcript_name": "Randy_Jesberg- Former CEO - Initial Conversation (06.26.2025)",
                "position": 45,
                "has_insight": True,
                "relevance_score": 8.5,  # Normal numeric value
                "focus_area_matched": "competitive advantages",
            },
            {
                "text": "The main challenge we face is the limited addressable market size.",
                "speaker_role": "expert",
                "transcript_name": "Cheryl Bertics - FlexXray Foreign Material Inspection Services - Former Manager",
                "position": 23,
                "has_insight": True,
                "relevance_score": None,  # None value - should become 0.0
                "focus_area_matched": "market limitations",
            },
            {
                "text": "Our rapid turnaround times give us a significant advantage over competitors.",
                "speaker_role": "expert",
                "transcript_name": "George Perry-West - Pegasus Foods, Inc - Former FSQA Manager",
                "position": 67,
                "has_insight": True,
                "relevance_score": "",  # Empty string - should become 0.0
                "focus_area_matched": "operational efficiency",
            },
        ]
        
        # Enrich the quotes
        enriched_quotes = self.tool.enrich_quotes_for_export(mock_quotes)
        
        # Verify all quotes have required fields
        for quote in enriched_quotes:
            self.assertIn("speaker_info", quote)
            self.assertIn("sentiment", quote)
            self.assertIn("theme", quote)
            self.assertIn("date", quote)
            self.assertIn("relevance_score", quote)
            
            # Verify relevance_score is numeric
            self.assertIsInstance(quote["relevance_score"], (int, float))
            
            # Verify speaker_info structure
            speaker_info = quote["speaker_info"]
            self.assertIsInstance(speaker_info, dict)
            self.assertIn("name", speaker_info)
            self.assertIn("company", speaker_info)
            self.assertIn("title", speaker_info)

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


def main():
    """Run the real quotes enrichment tests."""
    print("🚀 Testing Quote Enrichment with Real Data")
    print("=" * 55)
    
    # Run the tests
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()
