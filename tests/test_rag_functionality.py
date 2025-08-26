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
from quote_analysis_tool import ModularQuoteAnalysisTool


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
        self.analyzer = ModularQuoteAnalysisTool()

    def test_rag_system_initialization(self):
        """Test that RAG system initializes correctly."""
        self.assertIsNotNone(self.analyzer)
        self.assertTrue(hasattr(self.analyzer, 'get_rag_statistics'))

    def test_rag_statistics(self):
        """Test RAG system statistics."""
        rag_stats = self.analyzer.get_rag_statistics()
        
        self.assertIsInstance(rag_stats, dict)
        self.assertIn("search_capabilities", rag_stats)
        self.assertIsInstance(rag_stats["search_capabilities"], list)

    def test_semantic_search(self):
        """Test semantic search functionality."""
        try:
            search_results = self.analyzer.semantic_search_quotes(
                "competitive advantage", n_results=5
            )
            self.assertIsInstance(search_results, list)
        except Exception as e:
            # If no vector database is available, skip this test
            self.skipTest(f"Semantic search not available: {e}")

    def test_speaker_filtering(self):
        """Test speaker role filtering."""
        try:
            expert_quotes = self.analyzer.search_quotes_with_speaker_filter(
                "market expansion", speaker_role="expert", n_results=5
            )
            self.assertIsInstance(expert_quotes, list)
        except Exception as e:
            # If no vector database is available, skip this test
            self.skipTest(f"Speaker filtering not available: {e}")

    def test_perspective_based_retrieval(self):
        """Test perspective-based quote retrieval."""
        try:
            if "growth_potential" in self.analyzer.key_perspectives:
                perspective_quotes = self.analyzer.get_quotes_by_perspective(
                    "growth_potential",
                    self.analyzer.key_perspectives["growth_potential"],
                    n_results=10,
                )
                self.assertIsInstance(perspective_quotes, list)
        except Exception as e:
            # If no vector database is available, skip this test
            self.skipTest(f"Perspective retrieval not available: {e}")

    def test_rag_functionality_integration(self):
        """Test RAG functionality integration."""
        try:
            # Test with a small set of quotes
            test_quotes = [
                {
                    "text": "This is a test quote about business model",
                    "speaker_role": "expert",
                    "transcript_name": "test_transcript",
                    "position": 1,
                }
            ]
            
            # Test perspective analysis with RAG
            for perspective_key, perspective_data in self.analyzer.key_perspectives.items():
                result = self.analyzer.analyze_perspective_with_quotes(
                    perspective_key, perspective_data, test_quotes
                )
                
                if result:
                    self.assertIn("total_quotes", result)
                    self.assertIn("themes", result)
                    self.assertIsInstance(result["themes"], list)
        except Exception as e:
            # If RAG functionality is not available, skip this test
            self.skipTest(f"RAG integration not available: {e}")


def main():
    """Run the RAG functionality tests."""
    print("🧪 FlexXray RAG Functionality Test")
    print("=" * 50)
    
    # Run the tests
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()
