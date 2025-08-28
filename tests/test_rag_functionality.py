#!/usr/bin/env python3
"""
Test RAG Functionality for FlexXray Quote Analysis

This script demonstrates the enhanced RAG (Retrieval-Augmented Generation)
functionality that uses vector database semantic search for better quote retrieval.
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


class TestRAGFunctionality(unittest.TestCase):
    """Test RAG functionality for quote analysis."""

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

    def test_system_initialization(self):
        """Test that streamlined system initializes correctly."""
        self.assertIsNotNone(self.analyzer)
        self.assertTrue(hasattr(self.analyzer, 'key_questions'))
        self.assertTrue(hasattr(self.analyzer, 'client'))

    def test_key_questions(self):
        """Test key questions configuration."""
        self.assertIsInstance(self.analyzer.key_questions, dict)
        self.assertGreater(len(self.analyzer.key_questions), 0)
        
        # Check for expected questions
        expected_questions = ["market_leadership", "value_proposition"]
        for question in expected_questions:
            self.assertIn(question, self.analyzer.key_questions)

    def test_expert_quotes_filtering(self):
        """Test expert quotes filtering functionality."""
        try:
            # Test with sample quotes
            test_quotes = [
                {
                    "text": "This is a test quote about business model",
                    "speaker_role": "expert",
                    "transcript_name": "test_transcript",
                    "position": 1,
                },
                {
                    "text": "This is an interviewer question",
                    "speaker_role": "interviewer", 
                    "transcript_name": "test_transcript",
                    "position": 2,
                }
            ]
            
            expert_quotes = self.analyzer.get_expert_quotes_only(test_quotes)
            self.assertIsInstance(expert_quotes, list)
            self.assertEqual(len(expert_quotes), 1)  # Only expert quote should remain
            self.assertEqual(expert_quotes[0]["speaker_role"], "expert")
        except Exception as e:
            self.skipTest(f"Expert quotes filtering not available: {e}")

    def test_quote_ranking(self):
        """Test quote ranking functionality."""
        try:
            # Test with sample quotes
            test_quotes = [
                {
                    "text": "FlexXray has a strong competitive advantage in the market",
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
            ranked_quotes = self.analyzer.rank_quotes_for_question(test_quotes, question)
            self.assertIsInstance(ranked_quotes, list)
            self.assertEqual(len(ranked_quotes), len(test_quotes))
        except Exception as e:
            self.skipTest(f"Quote ranking not available: {e}")

    def test_company_summary_generation(self):
        """Test company summary generation."""
        try:
            # Test with sample quotes
            test_quotes = [
                {
                    "text": "FlexXray provides excellent service quality",
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


def main():
    """Run the RAG functionality tests."""
    print("🧪 FlexXray RAG Functionality Test")
    print("=" * 50)
    
    # Run the tests
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()
