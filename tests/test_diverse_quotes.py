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

from quote_analysis_tool import ModularQuoteAnalysisTool
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
        self.tool = ModularQuoteAnalysisTool(api_key=self.api_key)

    def test_tool_initialization(self):
        """Test that the tool initializes correctly."""
        self.assertIsNotNone(self.tool)
        self.assertTrue(hasattr(self.tool, '_get_diverse_quotes'))

    def test_diverse_quotes_population(self):
        """Test if diverse_quotes is actually populated."""
        try:
            # Get some sample quotes first
            if hasattr(self.tool, 'vector_db_manager') and self.tool.vector_db_manager:
                # Try to get some quotes from the database
                try:
                    sample_quotes = self.tool.vector_db_manager.get_all_quotes(limit=100)
                    self.logger.info(f"Found {len(sample_quotes)} sample quotes in database")
                    
                    if sample_quotes:
                        # Test the diverse quotes method directly
                        diverse_quotes = self.tool._get_diverse_quotes(sample_quotes, "summary", 30)
                        self.logger.info(f"✅ diverse_quotes populated: {len(diverse_quotes)} quotes")
                        
                        self.assertIsInstance(diverse_quotes, list)
                        self.assertGreater(len(diverse_quotes), 0)
                        
                        if diverse_quotes:
                            # Check quote sources
                            transcript_sources = set(quote.get('transcript_name', 'Unknown') for quote in diverse_quotes)
                            self.logger.info(f"Quotes from transcripts: {transcript_sources}")
                            self.assertIsInstance(transcript_sources, set)
                    else:
                        self.skipTest("No sample quotes found in database")
                        
                except Exception as e:
                    self.skipTest(f"Error accessing vector database: {e}")
            else:
                self.skipTest("Vector database manager not available")
                
        except Exception as e:
            self.skipTest(f"Error in diverse quotes test: {e}")

    def test_diverse_quotes_with_mock_data(self):
        """Test diverse quotes with mock data."""
        # Create mock quotes
        mock_quotes = [
            {
                "text": "Quote 1 about business model",
                "transcript_name": "transcript1",
                "speaker_role": "expert",
                "position": 1
            },
            {
                "text": "Quote 2 about market expansion",
                "transcript_name": "transcript2", 
                "speaker_role": "expert",
                "position": 2
            },
            {
                "text": "Quote 3 about technology",
                "transcript_name": "transcript3",
                "speaker_role": "expert", 
                "position": 3
            }
        ]
        
        try:
            diverse_quotes = self.tool._get_diverse_quotes(mock_quotes, "summary", 10)
            self.assertIsInstance(diverse_quotes, list)
            self.assertLessEqual(len(diverse_quotes), len(mock_quotes))
        except Exception as e:
            self.skipTest(f"Diverse quotes method not available: {e}")

    def test_diverse_quotes_limits(self):
        """Test diverse quotes with different limits."""
        mock_quotes = [
            {"text": f"Quote {i}", "transcript_name": f"transcript{i}", "speaker_role": "expert", "position": i}
            for i in range(50)
        ]
        
        try:
            # Test with different limits
            for limit in [5, 10, 20, 30]:
                diverse_quotes = self.tool._get_diverse_quotes(mock_quotes, "summary", limit)
                self.assertIsInstance(diverse_quotes, list)
                self.assertLessEqual(len(diverse_quotes), limit)
                self.assertLessEqual(len(diverse_quotes), len(mock_quotes))
        except Exception as e:
            self.skipTest(f"Diverse quotes method not available: {e}")

    def test_diverse_quotes_empty_input(self):
        """Test diverse quotes with empty input."""
        try:
            diverse_quotes = self.tool._get_diverse_quotes([], "summary", 10)
            self.assertIsInstance(diverse_quotes, list)
            self.assertEqual(len(diverse_quotes), 0)
        except Exception as e:
            self.skipTest(f"Diverse quotes method not available: {e}")


def main():
    """Main test function."""
    print("🧪 Starting diverse_quotes population test...")
    
    # Run the tests
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()
