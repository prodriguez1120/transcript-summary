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

    def test_perspective_analyzer_initialization(self):
        """Test perspective analyzer initialization."""
        try:
            from perspective_analysis import PerspectiveAnalyzer
            analyzer = PerspectiveAnalyzer(self.api_key)
            self.assertIsNotNone(analyzer)
        except ImportError:
            self.skipTest("perspective_analysis module not available")

    def test_batch_processing_configuration(self):
        """Test batch processing configuration and parameters."""
        try:
            from perspective_analysis import PerspectiveAnalyzer
            
            # Initialize perspective analyzer
            analyzer = PerspectiveAnalyzer(self.api_key)

            # Test default configuration
            metrics = analyzer.get_batch_processing_metrics()
            config = metrics["configuration"]
            
            self.assertIsInstance(config, dict)
            self.assertIn("batch_size", config)
            self.assertIn("batch_delay", config)
            self.assertIn("failure_delay", config)
            self.assertIn("max_quotes_per_perspective", config)
            self.assertIn("batch_processing_enabled", config)

            # Test configuration updates
            analyzer.configure_batch_processing(
                batch_size=15, batch_delay=2.0, failure_delay=5.0, max_quotes=300
            )

            # Verify updates
            updated_metrics = analyzer.get_batch_processing_metrics()
            updated_config = updated_metrics["configuration"]
            
            self.assertEqual(updated_config["batch_size"], 15)
            self.assertEqual(updated_config["batch_delay"], 2.0)
            self.assertEqual(updated_config["failure_delay"], 5.0)
            self.assertEqual(updated_config["max_quotes_per_perspective"], 300)

            # Test performance metrics
            performance = updated_metrics["performance"]
            self.assertIsInstance(performance, dict)
            self.assertIn("estimated_quotes_per_minute", performance)
            self.assertIn("recommended_batch_size", performance)

            # Test optimization tips
            optimization_tips = updated_metrics["optimization_tips"]
            self.assertIsInstance(optimization_tips, list)

        except ImportError:
            self.skipTest("perspective_analysis module not available")

    def test_batch_processing_logic(self):
        """Test batch processing logic without making actual API calls."""
        try:
            from perspective_analysis import PerspectiveAnalyzer
            
            # Initialize perspective analyzer
            analyzer = PerspectiveAnalyzer(self.api_key)

            # Test focus area expansion
            test_focus_areas = [
                "market position",
                "customer satisfaction",
                "technology innovation",
            ]
            expanded_areas = analyzer._expand_focus_areas(test_focus_areas)
            
            self.assertIsInstance(expanded_areas, list)
            self.assertGreaterEqual(len(expanded_areas), len(test_focus_areas))

            # Test relevance scoring
            test_quotes = [
                "Our market position is strong in the healthcare sector",
                "Customer satisfaction scores have improved by 25%",
                "We're investing heavily in technology innovation",
                "The weather is nice today",
                "Our business strategy focuses on growth and expansion",
            ]

            for quote in test_quotes:
                score = analyzer._calculate_focus_area_relevance(quote, "market position")
                self.assertIsInstance(score, (int, float))
                self.assertGreaterEqual(score, 0)

        except ImportError:
            self.skipTest("perspective_analysis module not available")

    def test_batch_configuration_validation(self):
        """Test batch configuration validation."""
        try:
            from perspective_analysis import PerspectiveAnalyzer
            
            analyzer = PerspectiveAnalyzer(self.api_key)
            
            # Test valid configuration
            analyzer.configure_batch_processing(
                batch_size=10,
                batch_delay=1.0,
                failure_delay=2.0,
                max_quotes=100
            )
            
            metrics = analyzer.get_batch_processing_metrics()
            self.assertIsInstance(metrics, dict)
            self.assertIn("configuration", metrics)
            self.assertIn("performance", metrics)
            
        except ImportError:
            self.skipTest("perspective_analysis module not available")

    def test_batch_processing_statistics(self):
        """Test batch processing statistics."""
        try:
            from perspective_analysis import PerspectiveAnalyzer
            
            analyzer = PerspectiveAnalyzer(self.api_key)
            
            # Configure batch processing
            analyzer.configure_batch_processing(
                batch_size=20,
                batch_delay=1.5,
                max_quotes=200
            )
            
            # Get statistics
            stats = analyzer.get_batch_processing_metrics()
            
            self.assertIsInstance(stats, dict)
            self.assertIn("configuration", stats)
            self.assertIn("performance", stats)
            self.assertIn("optimization_tips", stats)
            
            # Verify configuration values
            config = stats["configuration"]
            self.assertEqual(config["batch_size"], 20)
            self.assertEqual(config["batch_delay"], 1.5)
            self.assertEqual(config["max_quotes_per_perspective"], 200)
            
        except ImportError:
            self.skipTest("perspective_analysis module not available")


def main():
    """Main test function."""
    print("🚀 FlexXray Batch Processing Test Suite")
    print("=" * 60)
    
    # Run the tests
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()
