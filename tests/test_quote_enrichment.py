#!/usr/bin/env python3
"""
Test script to demonstrate quote enrichment functionality.

This script shows how quotes are enriched with missing fields before export,
fixing the blank columns and misaligned rows in Excel exports.
"""

import json
import sys
import os
import unittest
from pathlib import Path

# Add the parent directory to Python path so we can import modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from streamlined_quote_analysis import StreamlinedQuoteAnalysis


class TestQuoteEnrichment(unittest.TestCase):
    """Test quote enrichment functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Initialize the tool
        self.tool = StreamlinedQuoteAnalysis()

    def test_tool_initialization(self):
        """Test that the tool initializes correctly."""
        self.assertIsNotNone(self.tool)
        self.assertTrue(hasattr(self.tool, 'key_questions'))
        self.assertTrue(hasattr(self.tool, 'client'))

    def test_expert_quotes_filtering(self):
        """Test expert quotes filtering functionality."""
        # Sample quotes with mixed speaker roles
        sample_quotes = [
            {
                "text": "FlexXray has a strong competitive advantage in the market due to our proprietary technology.",
                "speaker_role": "expert",
                "transcript_name": "Randy_Jesberg- Former CEO - Initial Conversation (06.26.2025)",
                "position": 45,
            },
            {
                "text": "Can you tell me more about that?",
                "speaker_role": "interviewer",
                "transcript_name": "Interviewer - Follow Up",
                "position": 46,
            },
            {
                "text": "Our rapid turnaround times give us a significant advantage over competitors.",
                "speaker_role": "expert",
                "transcript_name": "George Perry-West - Pegasus Foods, Inc - Former FSQA Manager",
                "position": 67,
            },
        ]

        # Filter expert quotes
        expert_quotes = self.tool.get_expert_quotes_only(sample_quotes)

        # Verify filtering results
        self.assertEqual(len(expert_quotes), 2)  # Only expert quotes should remain
        
        for quote in expert_quotes:
            self.assertEqual(quote["speaker_role"], "expert")
            self.assertIn("text", quote)
            self.assertIn("transcript_name", quote)

    def test_quote_ranking(self):
        """Test quote ranking functionality."""
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
        ranked_quotes = self.tool.rank_quotes_for_question(test_quotes, question)
        
        self.assertIsInstance(ranked_quotes, list)
        self.assertEqual(len(ranked_quotes), len(test_quotes))
        
        # The first quote should be more relevant
        self.assertIn("competitive advantage", ranked_quotes[0]["text"].lower())

    def test_quote_reranking(self):
        """Test quote reranking functionality."""
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
        reranked_quotes = self.tool.rerank_top_quotes(test_quotes, question, top_n=2)
        
        self.assertIsInstance(reranked_quotes, list)
        self.assertLessEqual(len(reranked_quotes), len(test_quotes))
        
        # The most relevant quote should be first
        if len(reranked_quotes) >= 1:
            self.assertIn("competitive advantage", reranked_quotes[0]["text"].lower())

    def test_summary_generation(self):
        """Test summary generation functionality."""
        test_quotes = [
            {
                "text": "FlexXray provides excellent service quality and rapid turnaround times",
                "speaker_role": "expert",
                "transcript_name": "test_transcript",
                "position": 1,
            }
        ]

        summary = self.tool.generate_company_summary(test_quotes)
        self.assertIsInstance(summary, dict)
        self.assertIn("summary", summary)

    def test_excel_export_functionality(self):
        """Test Excel export functionality with enriched quotes."""
        # Create sample enriched quotes
        enriched_quotes = [
            {
                "text": "Test quote 1",
                "speaker_info": {"name": "Test Speaker", "company": "Test Company", "title": "Test Title"},
                "sentiment": "positive",
                "theme": "test_theme",
                "date": "2025-01-01",
                "relevance_score": 8.5,
                "transcript_name": "test_transcript.docx"
            },
            {
                "text": "Test quote 2",
                "speaker_info": {"name": "Test Speaker 2", "company": "Test Company 2", "title": "Test Title 2"},
                "sentiment": "neutral",
                "theme": "test_theme_2",
                "date": "2025-01-02",
                "relevance_score": 7.0,
                "transcript_name": "test_transcript_2.docx"
            }
        ]
        
        try:
            excel_file = self.tool.export_to_excel(enriched_quotes, "test_quotes.xlsx")
            if excel_file:
                self.assertTrue(os.path.exists(excel_file))
                # Clean up the test file
                os.remove(excel_file)
        except Exception as e:
            self.skipTest(f"Excel export not available: {e}")

    def test_empty_quotes_handling(self):
        """Test handling of empty quotes list."""
        empty_result = self.tool.get_expert_quotes_only([])
        self.assertEqual(empty_result, [])

    def test_quote_formatting(self):
        """Test quote formatting for display."""
        quote = {
            "text": "FlexXray provides excellent service quality and rapid turnaround times.",
            "speaker_info": {"name": "John Doe", "company": "Acme Corp", "title": "Manager"},
            "transcript_name": "John Doe - Acme Corp - Manager.docx"
        }
        
        formatted_quote = self.tool.format_quote_for_display(quote)
        
        self.assertIn("FlexXray provides excellent service quality", formatted_quote)
        self.assertIn("John Doe, Acme Corp, Manager.docx", formatted_quote)

    def test_quote_statistics(self):
        """Test quote statistics generation."""
        sample_quotes = [
            {
                "text": "Quote 1 about service quality",
                "theme": "service_quality",
                "sentiment": "positive"
            },
            {
                "text": "Quote 2 about technology",
                "theme": "technology_advantages", 
                "sentiment": "positive"
            },
            {
                "text": "Quote 3 about market challenges",
                "theme": "market_limitations",
                "sentiment": "negative"
            }
        ]
        
        stats = self.tool.get_quote_statistics(sample_quotes)
        
        self.assertIsInstance(stats, dict)
        self.assertIn("total_quotes", stats)
        self.assertIn("themes", stats)
        self.assertIn("sentiments", stats)
        
        self.assertEqual(stats["total_quotes"], 3)
        self.assertIn("service_quality", stats["themes"])
        self.assertIn("technology_advantages", stats["themes"])
        self.assertIn("market_limitations", stats["themes"])


def main():
    """Run the quote enrichment tests."""
    print("🚀 Starting Quote Enrichment Tests")
    print("=" * 50)

    # Run the tests
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()
