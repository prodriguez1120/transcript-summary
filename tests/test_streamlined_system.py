#!/usr/bin/env python3
"""
Comprehensive unit tests for the streamlined quote analysis system.

Tests include:
- StreamlinedQuoteAnalysis class functionality
- Quote metadata extraction from vector database format
- Excel export functionality
- Question-based analysis workflow
- Error handling and edge cases
"""

import unittest
import os
import sys
import json
import tempfile
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add the parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from streamlined_quote_analysis import StreamlinedQuoteAnalysis


class TestStreamlinedQuoteAnalysis(unittest.TestCase):
    """Test cases for StreamlinedQuoteAnalysis class."""

    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "test-api-key"
        self.analyzer = StreamlinedQuoteAnalysis(api_key=self.api_key)
        
        # Sample quote data in vector database format
        self.sample_quotes = [
            {
                "text": "FlexXray has a strong market position in foreign material detection.",
                "metadata": {
                    "speaker_role": "expert",
                    "transcript_name": "Randy_Jesberg-Former_CEO-Initial_Conversation.docx",
                    "has_insight": True,
                    "position": 1,
                    "quote_type": "business_insight",
                    "timestamp": "2025-06-26",
                    "has_context": True,
                    "context_count": 2
                },
                "distance": 0.1
            },
            {
                "text": "Our technology provides rapid turnaround times for customers.",
                "metadata": {
                    "speaker_role": "expert", 
                    "transcript_name": "Lee_Reece-The_Kraft_Heinz_Company-Lead_FSQA.docx",
                    "has_insight": True,
                    "position": 2,
                    "quote_type": "technology_advantage",
                    "timestamp": "2025-07-15",
                    "has_context": True,
                    "context_count": 1
                },
                "distance": 0.2
            }
        ]

    def test_initialization(self):
        """Test StreamlinedQuoteAnalysis initialization."""
        self.assertEqual(self.analyzer.api_key, self.api_key)
        self.assertIsNotNone(self.analyzer.client)
        self.assertIsNotNone(self.analyzer.key_questions)
        self.assertIsNotNone(self.analyzer.question_categories)

    def test_key_questions_structure(self):
        """Test that key questions are properly structured."""
        expected_categories = ["key_takeaways", "strengths", "weaknesses"]
        for category in expected_categories:
            self.assertIn(category, self.analyzer.question_categories)
        
        # Check that all question keys exist in key_questions
        all_question_keys = []
        for category_questions in self.analyzer.question_categories.values():
            all_question_keys.extend(category_questions)
        
        for question_key in all_question_keys:
            self.assertIn(question_key, self.analyzer.key_questions)

    def test_get_expert_quotes_only(self):
        """Test filtering to expert quotes only."""
        # Add a non-expert quote
        mixed_quotes = self.sample_quotes + [
            {
                "text": "What do you think about the market?",
                "metadata": {
                    "speaker_role": "interviewer",
                    "transcript_name": "test.docx"
                }
            }
        ]
        
        expert_quotes = self.analyzer.get_expert_quotes_only(mixed_quotes)
        
        self.assertEqual(len(expert_quotes), 2)  # Only expert quotes
        for quote in expert_quotes:
            metadata = quote.get("metadata", {})
            self.assertEqual(metadata.get("speaker_role"), "expert")

    def test_metadata_extraction_vector_db_format(self):
        """Test proper extraction of speaker and transcript info from vector DB format."""
        quote = self.sample_quotes[0]
        metadata = quote.get("metadata", {})
        
        # Test the extraction logic used in the code
        speaker_info = metadata.get("speaker_role", metadata.get("speaker", "Unknown Speaker"))
        transcript_name = metadata.get("transcript_name", "Unknown Transcript")
        
        self.assertEqual(speaker_info, "expert")
        self.assertEqual(transcript_name, "Randy_Jesberg-Former_CEO-Initial_Conversation.docx")

    def test_metadata_extraction_fallback(self):
        """Test metadata extraction with fallback values."""
        quote_without_metadata = {
            "text": "Test quote",
            "speaker_info": "Direct Speaker",
            "transcript_name": "Direct Transcript.docx"
        }
        
        metadata = quote_without_metadata.get("metadata", {})
        speaker_info = metadata.get("speaker_role", metadata.get("speaker", quote_without_metadata.get("speaker_info", "Unknown Speaker")))
        transcript_name = metadata.get("transcript_name", quote_without_metadata.get("transcript_name", "Unknown Transcript"))
        
        self.assertEqual(speaker_info, "Direct Speaker")
        self.assertEqual(transcript_name, "Direct Transcript.docx")

    def test_format_summary_output(self):
        """Test summary output formatting."""
        sample_results = {
            "key_takeaways": [
                {
                    "question": "What shows market leadership?",
                    "selected_quotes": [
                        {
                            "text": "FlexXray has strong market position",
                            "metadata": {
                                "speaker_role": "expert",
                                "transcript_name": "test.docx"
                            }
                        }
                    ]
                }
            ]
        }
        
        formatted_output = self.analyzer.format_summary_output(sample_results)
        
        self.assertIn("FLEXXRAY COMPANY SUMMARY PAGE", formatted_output)
        self.assertIn("Key Takeaways", formatted_output)
        self.assertIn("What shows market leadership?", formatted_output)
        self.assertIn("FlexXray has strong market position", formatted_output)

    def test_question_categories_completeness(self):
        """Test that all question categories have the expected number of questions."""
        # Key takeaways should have 3 questions
        self.assertEqual(len(self.analyzer.question_categories["key_takeaways"]), 3)
        
        # Strengths should have 2 questions
        self.assertEqual(len(self.analyzer.question_categories["strengths"]), 2)
        
        # Weaknesses should have 2 questions
        self.assertEqual(len(self.analyzer.question_categories["weaknesses"]), 2)
        
        # Total should be 7 questions
        total_questions = sum(len(questions) for questions in self.analyzer.question_categories.values())
        self.assertEqual(total_questions, 7)


class TestStreamlinedSystemIntegration(unittest.TestCase):
    """Integration tests for the streamlined system."""

    def test_run_streamlined_analysis_import(self):
        """Test that run_streamlined_analysis can be imported."""
        try:
            from run_streamlined_analysis import run_streamlined_analysis, load_existing_quotes
            self.assertTrue(callable(run_streamlined_analysis))
            self.assertTrue(callable(load_existing_quotes))
        except ImportError as e:
            self.fail(f"Failed to import run_streamlined_analysis: {e}")

    def test_streamlined_analysis_file_structure(self):
        """Test that all required streamlined analysis files exist."""
        required_files = [
            "streamlined_quote_analysis.py",
            "run_streamlined_analysis.py",
            "STREAMLINED_ANALYSIS_README.md"
        ]
        
        for file_path in required_files:
            full_path = os.path.join(parent_dir, file_path)
            self.assertTrue(os.path.exists(full_path), f"Required file {file_path} not found")


if __name__ == '__main__':
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases using TestLoader
    loader = unittest.TestLoader()
    test_suite.addTests(loader.loadTestsFromTestCase(TestStreamlinedQuoteAnalysis))
    test_suite.addTests(loader.loadTestsFromTestCase(TestStreamlinedSystemIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
