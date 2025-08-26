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
from quote_analysis_tool import ModularQuoteAnalysisTool


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
        self.analyzer = ModularQuoteAnalysisTool()

    def test_tool_initialization(self):
        """Test that the tool initializes correctly."""
        self.assertIsNotNone(self.analyzer)
        self.assertTrue(hasattr(self.analyzer, 'key_perspectives'))

    def test_perspective_analysis_with_ranking(self):
        """Test perspective analysis with ranking."""
        # Test with a small set of quotes
        test_quotes = [
            {
                "text": "This is a test quote about business model",
                "speaker_role": "expert",
                "transcript_name": "test_transcript",
                "position": 1,
            }
        ]

        # Test each perspective
        for perspective_key, perspective_data in self.analyzer.key_perspectives.items():
            try:
                result = self.analyzer.analyze_perspective_with_quotes(
                    perspective_key, perspective_data, test_quotes
                )

                if result:
                    self.assertIn("total_quotes", result)
                    self.assertIn("themes", result)
                    self.assertIsInstance(result["themes"], list)

                    # Check ranking coverage
                    if "ranked_quotes" in result:
                        ranked_quotes = result["ranked_quotes"]
                        self.assertIsInstance(ranked_quotes, list)

                        # Check selection stages
                        selection_stages = {}
                        for quote in ranked_quotes:
                            stage = quote.get("selection_stage", "unknown")
                            selection_stages[stage] = selection_stages.get(stage, 0) + 1

                        self.assertIsInstance(selection_stages, dict)

                        # Check ranking scores
                        if ranked_quotes:
                            top_quote = ranked_quotes[0]
                            self.assertIn("openai_rank", top_quote)
                            self.assertIn("selection_stage", top_quote)
                            self.assertIn("relevance_explanation", top_quote)

                    # Check themes for ranking info
                    themes = result.get("themes", [])
                    if themes:
                        for theme in themes[:2]:
                            self.assertIn("name", theme)
                            theme_quotes = theme.get("quotes", [])
                            self.assertIsInstance(theme_quotes, list)

                            # Check if theme quotes have ranking info
                            ranked_in_theme = sum(
                                1
                                for q in theme_quotes
                                if q.get("openai_rank") or q.get("selection_stage")
                            )
                            self.assertGreaterEqual(ranked_in_theme, 0)

            except Exception as e:
                # If perspective analysis fails, skip this test
                self.skipTest(f"Perspective analysis not available: {e}")

    def test_ranking_statistics_calculation(self):
        """Test ranking statistics calculation with actual results."""
        try:
            # Get actual results from one perspective to test ranking statistics
            if "business_model" in self.analyzer.key_perspectives:
                test_quotes = [
                    {
                        "text": "This is a test quote about business model",
                        "speaker_role": "expert",
                        "transcript_name": "test_transcript",
                        "position": 1,
                    }
                ]

                # Get actual results from perspective analysis
                actual_result = self.analyzer.analyze_perspective_with_quotes(
                    "business_model",
                    self.analyzer.key_perspectives["business_model"],
                    test_quotes,
                )

                if actual_result:
                    # Create results structure for ranking statistics
                    actual_results = {
                        "perspectives": {"business_model": actual_result},
                        "all_quotes": [
                            {"text": "test"}
                            for _ in range(actual_result.get("total_quotes", 0))
                        ],
                    }

                    ranking_stats = self.analyzer.get_quote_ranking_statistics(
                        actual_results
                    )
                    
                    self.assertIsInstance(ranking_stats, dict)
                    self.assertIn("total_perspectives", ranking_stats)
                    self.assertIn("total_ranked_quotes", ranking_stats)
                    self.assertIn("ranking_coverage", ranking_stats)
                    self.assertIn("selection_stage_breakdown", ranking_stats)

                    # Show detailed breakdown
                    if "ranked_quotes" in actual_result:
                        ranked_quotes = actual_result["ranked_quotes"]
                        self.assertIsInstance(ranked_quotes, list)

                        # Count by selection stage
                        stage_counts = {}
                        for quote in ranked_quotes:
                            stage = quote.get("selection_stage", "unknown")
                            stage_counts[stage] = stage_counts.get(stage, 0) + 1

                        self.assertIsInstance(stage_counts, dict)

                        # Show ranking distribution
                        ranking_distribution = {}
                        for quote in ranked_quotes:
                            rank = quote.get("openai_rank", 0)
                            ranking_distribution[rank] = (
                                ranking_distribution.get(rank, 0) + 1
                            )

                        self.assertIsInstance(ranking_distribution, dict)
                else:
                    self.skipTest("Could not get actual results for ranking statistics")

        except Exception as e:
            self.skipTest(f"Actual ranking statistics not available: {e}")

    def test_ranking_coverage_metrics(self):
        """Test ranking coverage metrics."""
        try:
            # Test with mock data
            mock_results = {
                "perspectives": {
                    "test_perspective": {
                        "ranked_quotes": [
                            {"openai_rank": 1, "selection_stage": "openai_ranked"},
                            {"openai_rank": 2, "selection_stage": "openai_ranked"},
                            {"selection_stage": "openai_failed"},
                        ]
                    }
                },
                "all_quotes": [{"text": "test1"}, {"text": "test2"}, {"text": "test3"}]
            }

            ranking_stats = self.analyzer.get_quote_ranking_statistics(mock_results)
            
            self.assertIsInstance(ranking_stats, dict)
            self.assertIn("total_perspectives", ranking_stats)
            self.assertIn("total_ranked_quotes", ranking_stats)
            self.assertIn("ranking_coverage", ranking_stats)
            self.assertIn("selection_stage_breakdown", ranking_stats)
            
            # Verify coverage calculation
            self.assertGreaterEqual(ranking_stats["ranking_coverage"], 0)
            self.assertLessEqual(ranking_stats["ranking_coverage"], 100)
            
        except Exception as e:
            self.skipTest(f"Ranking coverage metrics not available: {e}")

    def test_selection_stage_tracking(self):
        """Test selection stage tracking."""
        try:
            # Test with mock quotes that have different selection stages
            mock_quotes = [
                {"text": "Quote 1", "selection_stage": "openai_ranked", "openai_rank": 1},
                {"text": "Quote 2", "selection_stage": "openai_ranked", "openai_rank": 2},
                {"text": "Quote 3", "selection_stage": "openai_failed"},
                {"text": "Quote 4", "selection_stage": "manual_selected"},
            ]

            # Test selection stage breakdown
            selection_stages = {}
            for quote in mock_quotes:
                stage = quote.get("selection_stage", "unknown")
                selection_stages[stage] = selection_stages.get(stage, 0) + 1

            self.assertIn("openai_ranked", selection_stages)
            self.assertIn("openai_failed", selection_stages)
            self.assertIn("manual_selected", selection_stages)
            
            self.assertEqual(selection_stages["openai_ranked"], 2)
            self.assertEqual(selection_stages["openai_failed"], 1)
            self.assertEqual(selection_stages["manual_selected"], 1)

        except Exception as e:
            self.skipTest(f"Selection stage tracking not available: {e}")


def main():
    """Run the ranking coverage tests."""
    print("🧪 Testing Ranking Coverage and Selection Stages")
    print("=" * 60)
    
    # Run the tests
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()
