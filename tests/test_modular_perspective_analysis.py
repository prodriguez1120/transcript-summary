#!/usr/bin/env python3
"""
Test Modular Perspective Analysis System

This script demonstrates how the new modular components work together:
- quote_ranking.py: OpenAI-driven ranking & scoring
- theme_analysis.py: Thematic clustering and cross-transcript insights  
- batch_manager.py: Batching, token handling, and retries
- perspective_analysis_refactored.py: Integration layer
"""

import os
import sys
import unittest
from dotenv import load_dotenv

# Add the parent directory to Python path so we can import modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from settings import get_openai_api_key


class TestModularPerspectiveAnalysis(unittest.TestCase):
    """Test modular perspective analysis components."""

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

    def test_streamlined_analyzer_initialization(self):
        """Test Streamlined Analyzer initialization."""
        try:
            from streamlined_quote_analysis import StreamlinedQuoteAnalysis
            analyzer = StreamlinedQuoteAnalysis(api_key=self.api_key)
            self.assertIsNotNone(analyzer)
            self.assertTrue(hasattr(analyzer, 'key_questions'))
        except ImportError:
            self.skipTest("streamlined_quote_analysis module not available")

    def test_quote_ranking_functionality(self):
        """Test quote ranking functionality."""
        try:
            from streamlined_quote_analysis import StreamlinedQuoteAnalysis
            analyzer = StreamlinedQuoteAnalysis(api_key=self.api_key)
            
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
            ranked_quotes = analyzer.rank_quotes_for_question(test_quotes, question)
            self.assertIsInstance(ranked_quotes, list)
            self.assertEqual(len(ranked_quotes), len(test_quotes))
        except ImportError:
            self.skipTest("streamlined_quote_analysis module not available")

    def test_expert_quotes_filtering(self):
        """Test expert quotes filtering functionality."""
        try:
            from streamlined_quote_analysis import StreamlinedQuoteAnalysis
            analyzer = StreamlinedQuoteAnalysis(api_key=self.api_key)
            
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
            
            expert_quotes = analyzer.get_expert_quotes_only(test_quotes)
            self.assertIsInstance(expert_quotes, list)
            self.assertEqual(len(expert_quotes), 1)  # Only expert quote should remain
            self.assertEqual(expert_quotes[0]["speaker_role"], "expert")
        except ImportError:
            self.skipTest("streamlined_quote_analysis module not available")

    def test_summary_generation(self):
        """Test summary generation functionality."""
        try:
            from streamlined_quote_analysis import StreamlinedQuoteAnalysis
            analyzer = StreamlinedQuoteAnalysis(api_key=self.api_key)
            
            # Test with sample quotes
            test_quotes = [
                {
                    "text": "FlexXray provides excellent service quality and rapid turnaround times",
                    "speaker_role": "expert",
                    "transcript_name": "test_transcript",
                    "position": 1,
                }
            ]
            
            summary = analyzer.generate_company_summary(test_quotes)
            self.assertIsInstance(summary, dict)
            self.assertIn("key_takeaways", summary)
        except ImportError:
            self.skipTest("streamlined_quote_analysis module not available")

    def test_quote_reranking_functionality(self):
        """Test quote reranking functionality."""
        try:
            from streamlined_quote_analysis import StreamlinedQuoteAnalysis
            analyzer = StreamlinedQuoteAnalysis(api_key=self.api_key)
            
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
            reranked_quotes = analyzer.rerank_top_quotes(test_quotes, question, top_n=2)
            self.assertIsInstance(reranked_quotes, list)
            self.assertLessEqual(len(reranked_quotes), len(test_quotes))
        except ImportError:
            self.skipTest("streamlined_quote_analysis module not available")

    def test_excel_export_functionality(self):
        """Test Excel export functionality."""
        try:
            from streamlined_quote_analysis import StreamlinedQuoteAnalysis
            analyzer = StreamlinedQuoteAnalysis(api_key=self.api_key)
            
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
            excel_file = analyzer.export_to_excel(test_quotes, "test_output.xlsx")
            if excel_file:
                self.assertTrue(os.path.exists(excel_file))
                # Clean up the test file
                os.remove(excel_file)
        except ImportError:
            self.skipTest("streamlined_quote_analysis module not available")

    def test_integration(self):
        """Test the integration between all streamlined components."""
        try:
            from streamlined_quote_analysis import StreamlinedQuoteAnalysis
            analyzer = StreamlinedQuoteAnalysis(api_key=self.api_key)
            
            # Test key questions configuration
            self.assertIsInstance(analyzer.key_questions, dict)
            self.assertGreater(len(analyzer.key_questions), 0)
            
            # Test with sample quotes
            test_quotes = [
                {
                    "text": "FlexXray provides excellent service quality and rapid turnaround times",
                    "speaker_role": "expert",
                    "transcript_name": "test_transcript",
                    "position": 1,
                }
            ]
            
            # Test expert filtering
            expert_quotes = analyzer.get_expert_quotes_only(test_quotes)
            self.assertIsInstance(expert_quotes, list)
            
            # Test ranking
            question = "What evidence shows FlexXray's competitive advantage?"
            ranked_quotes = analyzer.rank_quotes_for_question(expert_quotes, question)
            self.assertIsInstance(ranked_quotes, list)
            
            # Test summary generation
            summary = analyzer.generate_company_summary(expert_quotes)
            self.assertIsInstance(summary, dict)
            self.assertIn("key_takeaways", summary)
            
        except ImportError:
            self.skipTest("streamlined_quote_analysis module not available")


def main():
    """Run all modular perspective analysis tests."""
    print("🚀 Modular Perspective Analysis System Test")
    print("=" * 60)
    
    # Run the tests
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()
