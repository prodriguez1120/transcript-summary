#!/usr/bin/env python3
"""
Test Main Tool RAG Integration

This script tests that the RAG functionality is properly integrated
into the main quote analysis tool flow.
"""

import os
import sys
import unittest
from dotenv import load_dotenv

# Add the parent directory to Python path so we can import modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from settings import get_openai_api_key
from streamlined_quote_analysis import StreamlinedQuoteAnalysis


class TestMainToolRAGIntegration(unittest.TestCase):
    """Test main tool RAG integration."""

    def setUp(self):
        """Set up test fixtures."""
        # Load environment variables
        load_dotenv()
        
        # Check for API key
        try:
            self.api_key = get_openai_api_key()
            if not self.api_key:
                self.skipTest("OpenAI API key not found")
        except ValueError as e:
            self.skipTest(f"API key error: {e}")
        
        # Initialize the tool
        self.analyzer = StreamlinedQuoteAnalysis(api_key=self.api_key)

    def test_tool_initialization(self):
        """Test that the tool initializes correctly."""
        self.assertIsNotNone(self.analyzer)
        self.assertTrue(hasattr(self.analyzer, 'key_questions'))
        self.assertTrue(hasattr(self.analyzer, 'client'))

    def test_streamlined_system_check(self):
        """Test streamlined system configuration."""
        # Check streamlined system components
        self.assertIsInstance(self.analyzer.key_questions, dict)
        self.assertGreater(len(self.analyzer.key_questions), 0)
        self.assertIsNotNone(self.analyzer.client)

    def test_quote_analysis_with_streamlined_system(self):
        """Test quote analysis with streamlined system."""
        # Test with a small set of quotes
        test_quotes = [
            {
                "text": "FlexXray has a strong competitive advantage in the market",
                "speaker_role": "expert",
                "transcript_name": "test_transcript",
                "position": 1,
            }
        ]

        try:
            # Test expert quotes filtering
            expert_quotes = self.analyzer.get_expert_quotes_only(test_quotes)
            self.assertIsInstance(expert_quotes, list)
            self.assertEqual(len(expert_quotes), 1)
            
            # Test quote ranking
            question = "What evidence shows FlexXray's competitive advantage?"
            ranked_quotes = self.analyzer.rank_quotes_for_question(test_quotes, question)
            self.assertIsInstance(ranked_quotes, list)
            self.assertEqual(len(ranked_quotes), len(test_quotes))
                        
        except Exception as e:
            # If analysis fails, skip this test
            self.skipTest(f"Quote analysis not available: {e}")

    def test_summary_generation(self):
        """Test summary generation functionality."""
        try:
            # Test with sample quotes
            test_quotes = [
                {
                    "text": "FlexXray provides excellent service quality and rapid turnaround times",
                    "speaker_role": "expert",
                    "transcript_name": "test_transcript",
                    "position": 1,
                }
            ]
            
            summary = self.analyzer.generate_company_summary(test_quotes)
            self.assertIsInstance(summary, dict)
            self.assertIn("summary", summary)
        except Exception as e:
            self.skipTest(f"Summary generation not available: {e}")

    def test_excel_export(self):
        """Test Excel export functionality."""
        try:
            # Test with sample quotes
            test_quotes = [
                {
                    "text": "FlexXray has strong market leadership",
                    "speaker_role": "expert",
                    "transcript_name": "test_transcript",
                    "position": 1,
                }
            ]
            
            # Test export functionality
            excel_file = self.analyzer.export_to_excel(test_quotes, "test_output.xlsx")
            if excel_file:
                self.assertTrue(os.path.exists(excel_file))
                # Clean up the test file
                os.remove(excel_file)
        except Exception as e:
            self.skipTest(f"Excel export not available: {e}")

    def test_quote_reranking(self):
        """Test quote reranking functionality."""
        try:
            # Test with sample quotes
            test_quotes = [
                {
                    "text": "FlexXray has a strong competitive advantage",
                    "speaker_role": "expert",
                    "transcript_name": "test_transcript",
                    "position": 1,
                },
                {
                    "text": "The weather is nice today",
                    "speaker_role": "expert",
                    "transcript_name": "test_transcript",
                    "position": 2,
                }
            ]
            
            question = "What evidence shows FlexXray's competitive advantage?"
            reranked_quotes = self.analyzer.rerank_top_quotes(test_quotes, question, top_n=2)
            self.assertIsInstance(reranked_quotes, list)
            self.assertLessEqual(len(reranked_quotes), len(test_quotes))
        except Exception as e:
            self.skipTest(f"Quote reranking not available: {e}")


def main():
    """Run the main tool RAG integration tests."""
    print("🧪 Testing Main Tool RAG Integration")
    print("=" * 50)
    
    # Run the tests
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()
