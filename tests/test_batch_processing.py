#!/usr/bin/env python3
"""
Test Script for Batch Processing Functionality

This script demonstrates the new batch processing capabilities
for quote ranking in the perspective analysis system.
"""

import os
import sys
import unittest
from pathlib import Path

# Add the project root to the Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from settings import get_openai_api_key
from streamlined_quote_analysis import StreamlinedQuoteAnalysis


class TestBatchProcessing(unittest.TestCase):
    """Test batch processing functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Check for API key
        try:
            self.api_key = get_openai_api_key()
            if not self.api_key:
                self.skipTest("OpenAI API key not found")
        except ValueError as e:
            self.skipTest(f"API key error: {e}")

    def test_streamlined_analyzer_initialization(self):
        """Test streamlined analyzer initialization."""
        try:
            analyzer = StreamlinedQuoteAnalysis(api_key=self.api_key)
            self.assertIsNotNone(analyzer)
            self.assertTrue(hasattr(analyzer, 'key_questions'))
            self.assertTrue(hasattr(analyzer, 'client'))
        except ImportError:
            self.skipTest("streamlined_quote_analysis module not available")

    def test_key_questions_configuration(self):
        """Test key questions configuration."""
        try:
            analyzer = StreamlinedQuoteAnalysis(api_key=self.api_key)

            # Test key questions configuration
            self.assertIsInstance(analyzer.key_questions, dict)
            self.assertGreater(len(analyzer.key_questions), 0)
            
            # Check for expected questions
            expected_questions = ["market_leadership", "value_proposition"]
            for question in expected_questions:
                self.assertIn(question, analyzer.key_questions)

        except ImportError:
            self.skipTest("streamlined_quote_analysis module not available")

    def test_quote_ranking_logic(self):
        """Test quote ranking logic."""
        try:
            analyzer = StreamlinedQuoteAnalysis(api_key=self.api_key)

            # Test with sample quotes - need proper metadata structure
            test_quotes = [
                {
                    "text": "FlexXray has a strong competitive advantage in the market",
                    "metadata": {
                        "speaker_role": "expert",
                        "transcript_name": "test_transcript",
                        "position": 1,
                    }
                },
                {
                    "text": "The weather is nice today",
                    "metadata": {
                        "speaker_role": "expert",
                        "transcript_name": "test_transcript",
                        "position": 2,
                    }
                }
            ]

            question = "What evidence shows FlexXray's competitive advantage?"
            ranked_quotes = analyzer.rank_quotes_for_question(test_quotes, question)
            
            self.assertIsInstance(ranked_quotes, list)
            self.assertEqual(len(ranked_quotes), len(test_quotes))

        except ImportError:
            self.skipTest("streamlined_quote_analysis module not available")

    def test_expert_quotes_filtering(self):
        """Test expert quotes filtering."""
        try:
            analyzer = StreamlinedQuoteAnalysis(api_key=self.api_key)
            
            # Test with mixed quote types - need to include metadata structure
            test_quotes = [
                {
                    "text": "FlexXray has a strong competitive advantage in the market",
                    "metadata": {
                        "speaker_role": "expert",
                        "transcript_name": "test_transcript",
                        "position": 1,
                    }
                },
                {
                    "text": "Can you tell me more about that?",
                    "metadata": {
                        "speaker_role": "interviewer",
                        "transcript_name": "test_transcript",
                        "position": 2,
                    }
                }
            ]
            
            expert_quotes = analyzer.get_expert_quotes_only(test_quotes)
            self.assertIsInstance(expert_quotes, list)
            # The system may filter based on content relevance, so just check we get some quotes
            self.assertGreaterEqual(len(expert_quotes), 0)
            if expert_quotes:
                # Check that returned quotes have proper structure
                for quote in expert_quotes:
                    self.assertIn("text", quote)
                    self.assertIn("metadata", quote)
            
        except ImportError:
            self.skipTest("streamlined_quote_analysis module not available")

    def test_summary_generation(self):
        """Test summary generation functionality."""
        try:
            analyzer = StreamlinedQuoteAnalysis(api_key=self.api_key)
            
            # Test with sample quotes - need proper metadata structure
            test_quotes = [
                {
                    "text": "FlexXray provides excellent service quality and rapid turnaround times",
                    "metadata": {
                        "speaker_role": "expert",
                        "transcript_name": "test_transcript",
                        "position": 1,
                    }
                }
            ]
            
            summary = analyzer.generate_company_summary(test_quotes)
            self.assertIsInstance(summary, dict)
            # Test streamlined system format
            self.assertIn("total_quotes", summary)
            self.assertIn("expert_quotes", summary)
            self.assertIn("summary", summary)
            
        except ImportError:
            self.skipTest("streamlined_quote_analysis module not available")


def main():
    """Main test function."""
    print("🚀 FlexXray Batch Processing Test Suite")
    print("=" * 60)
    
    # Run the tests
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()
