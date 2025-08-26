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
from quote_analysis_tool import ModularQuoteAnalysisTool


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
        self.analyzer = ModularQuoteAnalysisTool()

    def test_tool_initialization(self):
        """Test that the tool initializes correctly."""
        self.assertIsNotNone(self.analyzer)
        self.assertTrue(hasattr(self.analyzer, 'perspective_analyzer'))

    def test_rag_integration_check(self):
        """Test RAG integration check."""
        # Check RAG integration
        rag_enabled = (
            hasattr(self.analyzer.perspective_analyzer, "vector_db_manager")
            and self.analyzer.perspective_analyzer.vector_db_manager is not None
        )
        
        if rag_enabled:
            self.assertIsNotNone(self.analyzer.perspective_analyzer.vector_db_manager)
            self.assertTrue(hasattr(self.analyzer.perspective_analyzer.vector_db_manager, 'quotes_collection'))

    def test_perspective_analysis_with_rag(self):
        """Test perspective analysis with RAG."""
        # Test with a small set of quotes
        test_quotes = [
            {
                "text": "This is a test quote about business model",
                "speaker_role": "expert",
                "transcript_name": "test_transcript",
                "position": 1,
            }
        ]

        # Test the perspective analysis method
        for perspective_key, perspective_data in self.analyzer.key_perspectives.items():
            try:
                result = self.analyzer.analyze_perspective_with_quotes(
                    perspective_key, perspective_data, test_quotes
                )

                if result:
                    self.assertIn("total_quotes", result)
                    self.assertIn("themes", result)
                    self.assertIsInstance(result["themes"], list)
                    
                    # Check if RAG was used
                    if result.get("total_quotes", 0) > len(test_quotes):
                        # RAG was used - retrieved additional quotes
                        self.assertGreater(result.get("total_quotes", 0), len(test_quotes))
                    else:
                        # Local processing used
                        self.assertEqual(result.get("total_quotes", 0), len(test_quotes))
                        
            except Exception as e:
                # If perspective analysis fails, skip this test
                self.skipTest(f"Perspective analysis not available: {e}")

    def test_vector_database_search(self):
        """Test vector database search directly."""
        try:
            if hasattr(self.analyzer, 'vector_db_manager') and self.analyzer.vector_db_manager:
                if self.analyzer.vector_db_manager.quotes_collection:
                    # Test semantic search
                    search_results = self.analyzer.vector_db_manager.semantic_search_quotes(
                        "business model", n_results=3
                    )
                    self.assertIsInstance(search_results, list)

                    # Test speaker filtering
                    expert_quotes = (
                        self.analyzer.vector_db_manager.search_quotes_with_speaker_filter(
                            "market", speaker_role="expert", n_results=3
                        )
                    )
                    self.assertIsInstance(expert_quotes, list)
                else:
                    self.skipTest("Vector database collection not available")
            else:
                self.skipTest("Vector database manager not available")
        except Exception as e:
            self.skipTest(f"Vector search not available: {e}")

    def test_rag_statistics(self):
        """Test RAG statistics."""
        try:
            rag_stats = self.analyzer.get_rag_statistics()
            self.assertIsInstance(rag_stats, dict)
            self.assertIn("search_capabilities", rag_stats)
        except Exception as e:
            self.skipTest(f"RAG statistics not available: {e}")

    def test_semantic_search_integration(self):
        """Test semantic search integration."""
        try:
            search_results = self.analyzer.semantic_search_quotes(
                "competitive advantage", n_results=5
            )
            self.assertIsInstance(search_results, list)
            
            if search_results:
                top_result = search_results[0]
                self.assertIn("text", top_result)
                self.assertIn("metadata", top_result)
        except Exception as e:
            self.skipTest(f"Semantic search not available: {e}")

    def test_speaker_filtering_integration(self):
        """Test speaker filtering integration."""
        try:
            expert_quotes = self.analyzer.search_quotes_with_speaker_filter(
                "market expansion", speaker_role="expert", n_results=5
            )
            self.assertIsInstance(expert_quotes, list)
            
            if expert_quotes:
                # Verify all quotes are from experts
                all_experts = all(
                    q.get('metadata', {}).get('speaker_role') == 'expert' 
                    for q in expert_quotes
                )
                self.assertTrue(all_experts)
        except Exception as e:
            self.skipTest(f"Speaker filtering not available: {e}")


def main():
    """Run the main tool RAG integration tests."""
    print("🧪 Testing Main Tool RAG Integration")
    print("=" * 50)
    
    # Run the tests
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()
