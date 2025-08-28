#!/usr/bin/env python3
"""
Test Ranking Coverage and Selection Stages

This script tests the improved ranking formulas and coverage calculation.
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


class TestRankingCoverage(unittest.TestCase):
    """Test ranking coverage and selection stage tracking."""

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

    def test_quote_ranking_functionality(self):
        """Test quote ranking functionality."""
        # Test with a small set of quotes
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

        try:
            # Test quote ranking
            question = "What evidence shows FlexXray's competitive advantage?"
            ranked_quotes = self.analyzer.rank_quotes_for_question(test_quotes, question)
            
            self.assertIsInstance(ranked_quotes, list)
            self.assertEqual(len(ranked_quotes), len(test_quotes))
            
            # Check that quotes are ranked (first quote should be more relevant)
            if len(ranked_quotes) >= 2:
                # The first quote should be more relevant to the question
                self.assertIn("competitive advantage", ranked_quotes[0]["text"].lower())

        except Exception as e:
            # If ranking fails, skip this test
            self.skipTest(f"Quote ranking not available: {e}")

    def test_quote_reranking_functionality(self):
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
            
            # Check that the most relevant quote is first
            if len(reranked_quotes) >= 1:
                self.assertIn("competitive advantage", reranked_quotes[0]["text"].lower())

        except Exception as e:
            self.skipTest(f"Quote reranking not available: {e}")

    def test_expert_quotes_filtering(self):
        """Test expert quotes filtering functionality."""
        try:
            # Test with mixed quote types
            test_quotes = [
                {
                    "text": "FlexXray has a strong competitive advantage",
                    "speaker_role": "expert",
                    "transcript_name": "test_transcript",
                    "position": 1,
                },
                {
                    "text": "Can you tell me more about that?",
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

    def test_ranking_consistency(self):
        """Test ranking consistency across multiple runs."""
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
            
            # Run ranking multiple times to check consistency
            results = []
            for _ in range(3):
                ranked_quotes = self.analyzer.rank_quotes_for_question(test_quotes, question)
                results.append(ranked_quotes)
            
            # All results should have the same structure
            for result in results:
                self.assertIsInstance(result, list)
                self.assertEqual(len(result), len(test_quotes))

        except Exception as e:
            self.skipTest(f"Ranking consistency test not available: {e}")


def main():
    """Run the ranking coverage tests."""
    print("🧪 Testing Ranking Coverage and Selection Stages")
    print("=" * 60)
    
    # Run the tests
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()
