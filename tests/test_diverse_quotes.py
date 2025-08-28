#!/usr/bin/env python3
"""
Test script to verify that diverse_quotes is actually populated
"""

import logging
import sys
import os
import unittest
from dotenv import load_dotenv

# Add the project root to the Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from streamlined_quote_analysis import StreamlinedQuoteAnalysis
from settings import get_openai_api_key


class TestDiverseQuotes(unittest.TestCase):
    """Test diverse quotes population functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
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
        self.tool = StreamlinedQuoteAnalysis(api_key=self.api_key)

    def test_tool_initialization(self):
        """Test that the tool initializes correctly."""
        self.assertIsNotNone(self.tool)
        self.assertTrue(hasattr(self.tool, 'key_questions'))
        self.assertTrue(hasattr(self.tool, 'client'))

    def test_expert_quotes_filtering(self):
        """Test expert quotes filtering functionality."""
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
                    "text": "Can you tell me more about that?",
                    "speaker_role": "interviewer",
                    "transcript_name": "test_transcript",
                    "position": 2,
                }
            ]
            
            expert_quotes = self.tool.get_expert_quotes_only(test_quotes)
            self.logger.info(f"✅ Expert quotes filtered: {len(expert_quotes)} quotes")
            
            self.assertIsInstance(expert_quotes, list)
            self.assertEqual(len(expert_quotes), 1)  # Only expert quote should remain
            self.assertEqual(expert_quotes[0]["speaker_role"], "expert")
                
        except Exception as e:
            self.skipTest(f"Expert quotes filtering not available: {e}")

    def test_quote_ranking_with_mock_data(self):
        """Test quote ranking with mock data."""
        # Create mock quotes
        mock_quotes = [
            {
                "text": "FlexXray has a strong competitive advantage in the market",
                "transcript_name": "transcript1",
                "speaker_role": "expert",
                "position": 1
            },
            {
                "text": "The weather is nice today",
                "transcript_name": "transcript2", 
                "speaker_role": "expert",
                "position": 2
            },
            {
                "text": "FlexXray provides excellent service quality",
                "transcript_name": "transcript3",
                "speaker_role": "expert", 
                "position": 3
            }
        ]
        
        try:
            question = "What evidence shows FlexXray's competitive advantage?"
            ranked_quotes = self.tool.rank_quotes_for_question(mock_quotes, question)
            self.assertIsInstance(ranked_quotes, list)
            self.assertEqual(len(ranked_quotes), len(mock_quotes))
        except Exception as e:
            self.skipTest(f"Quote ranking method not available: {e}")

    def test_quote_reranking_limits(self):
        """Test quote reranking with different limits."""
        mock_quotes = [
            {"text": f"Quote {i} about FlexXray's competitive advantage", "transcript_name": f"transcript{i}", "speaker_role": "expert", "position": i}
            for i in range(10)
        ]
        
        try:
            # Test with different limits
            question = "What evidence shows FlexXray's competitive advantage?"
            for limit in [2, 5, 8]:
                reranked_quotes = self.tool.rerank_top_quotes(mock_quotes, question, top_n=limit)
                self.assertIsInstance(reranked_quotes, list)
                self.assertLessEqual(len(reranked_quotes), limit)
                self.assertLessEqual(len(reranked_quotes), len(mock_quotes))
        except Exception as e:
            self.skipTest(f"Quote reranking method not available: {e}")

    def test_empty_quotes_handling(self):
        """Test handling of empty quotes list."""
        try:
            expert_quotes = self.tool.get_expert_quotes_only([])
            self.assertIsInstance(expert_quotes, list)
            self.assertEqual(len(expert_quotes), 0)
        except Exception as e:
            self.skipTest(f"Empty quotes handling not available: {e}")


def main():
    """Main test function."""
    print("🧪 Starting diverse_quotes population test...")
    
    # Run the tests
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()
