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

    def test_quote_ranker_initialization(self):
        """Test Quote Ranker initialization."""
        try:
            from quote_ranking import QuoteRanker
            quote_ranker = QuoteRanker(self.api_key)
            self.assertIsNotNone(quote_ranker)
        except ImportError:
            self.skipTest("quote_ranking module not available")

    def test_theme_analyzer_initialization(self):
        """Test Theme Analyzer initialization."""
        try:
            from theme_analysis import ThemeAnalyzer
            theme_analyzer = ThemeAnalyzer(self.api_key)
            self.assertIsNotNone(theme_analyzer)
        except ImportError:
            self.skipTest("theme_analysis module not available")

    def test_batch_manager_initialization(self):
        """Test Batch Manager initialization."""
        try:
            from batch_manager import BatchManager, BatchConfig
            
            batch_config = BatchConfig(
                batch_size=15,
                batch_delay=1.0,
                failure_delay=2.0,
                max_retries=2
            )
            batch_manager = BatchManager(batch_config)
            self.assertIsNotNone(batch_manager)
        except ImportError:
            self.skipTest("batch_manager module not available")

    def test_perspective_analyzer_initialization(self):
        """Test Refactored Perspective Analyzer initialization."""
        try:
            from perspective_analysis_refactored import PerspectiveAnalyzer
            perspective_analyzer = PerspectiveAnalyzer(self.api_key)
            self.assertIsNotNone(perspective_analyzer)
        except ImportError:
            self.skipTest("perspective_analysis_refactored module not available")

    def test_batch_manager_functionality(self):
        """Test batch manager functionality."""
        try:
            from batch_manager import BatchManager, BatchConfig
            
            # Create batch manager
            config = BatchConfig(
                batch_size=10,
                batch_delay=0.1,  # Fast for testing
                failure_delay=0.5,
                max_retries=2
            )
            batch_manager = BatchManager(config)
            
            # Test configuration
            batch_manager.configure_batch_processing(batch_size=12, max_retries=3)
            
            # Test validation
            validation = batch_manager.validate_configuration()
            self.assertIsInstance(validation, dict)
            self.assertIn("valid", validation)
            
            # Test statistics
            stats = batch_manager.get_batch_processing_stats()
            self.assertIsInstance(stats, dict)
            self.assertIn("configuration", stats)
            self.assertIn("performance", stats)
            
        except ImportError:
            self.skipTest("batch_manager module not available")

    def test_quote_ranker_functionality(self):
        """Test quote ranker functionality."""
        try:
            from quote_ranking import QuoteRanker
            
            # Create quote ranker
            quote_ranker = QuoteRanker("test_key")
            
            # Test statistics method
            empty_stats = quote_ranker.get_ranking_statistics([])
            self.assertIsInstance(empty_stats, dict)
            self.assertIn("total_quotes", empty_stats)
            
            # Test with mock data
            mock_quotes = [
                {"text": "Test quote 1", "selection_stage": "openai_ranked"},
                {"text": "Test quote 2", "selection_stage": "openai_failed"},
            ]
            
            mock_stats = quote_ranker.get_ranking_statistics(mock_quotes)
            self.assertIsInstance(mock_stats, dict)
            self.assertIn("total_quotes", mock_stats)
            self.assertIn("successful_rankings", mock_stats)
            self.assertIn("failed_rankings", mock_stats)
            
        except ImportError:
            self.skipTest("quote_ranking module not available")

    def test_theme_analyzer_functionality(self):
        """Test theme analyzer functionality."""
        try:
            from theme_analysis import ThemeAnalyzer
            
            # Create theme analyzer
            theme_analyzer = ThemeAnalyzer("test_key")
            
            # Test theme statistics method
            empty_stats = theme_analyzer.get_theme_statistics([])
            self.assertIsInstance(empty_stats, dict)
            self.assertIn("total_themes", empty_stats)
            
            # Test with mock data
            mock_themes = [
                {
                    "name": "Test Theme 1",
                    "confidence_score": 0.8,
                    "max_quotes": 4,
                    "cross_transcript_insights": ["insight1"]
                },
                {
                    "name": "Test Theme 2", 
                    "confidence_score": 0.9,
                    "max_quotes": 3,
                    "cross_transcript_insights": []
                }
            ]
            
            mock_stats = theme_analyzer.get_theme_statistics(mock_themes)
            self.assertIsInstance(mock_stats, dict)
            self.assertIn("total_themes", mock_stats)
            self.assertIn("average_confidence", mock_stats)
            self.assertIn("cross_transcript_coverage", mock_stats)
            
        except ImportError:
            self.skipTest("theme_analysis module not available")

    def test_integration(self):
        """Test the integration between all components."""
        try:
            from perspective_analysis_refactored import PerspectiveAnalyzer
            
            # Create perspective analyzer
            perspective_analyzer = PerspectiveAnalyzer("test_key")
            
            # Test batch configuration
            perspective_analyzer.configure_batch_processing(
                batch_size=25,
                batch_delay=2.0,
                max_retries=4
            )
            
            # Test batch metrics
            batch_metrics = perspective_analyzer.get_batch_processing_metrics()
            self.assertIsInstance(batch_metrics, dict)
            self.assertIn("configuration", batch_metrics)
            
            # Test configuration validation
            validation = perspective_analyzer.validate_batch_configuration()
            self.assertIsInstance(validation, dict)
            self.assertIn("valid", validation)
            
        except ImportError:
            self.skipTest("perspective_analysis_refactored module not available")


def main():
    """Run all modular perspective analysis tests."""
    print("🚀 Modular Perspective Analysis System Test")
    print("=" * 60)
    
    # Run the tests
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()
