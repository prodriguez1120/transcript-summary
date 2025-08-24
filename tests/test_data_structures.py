#!/usr/bin/env python3
"""
Unit tests for DataStructureManager module
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_structures import DataStructureManager


class TestDataStructureManager(unittest.TestCase):
    """Test cases for DataStructureManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = DataStructureManager()
        
        # Sample sections for testing
        self.sample_sections = {
            "key_takeaways": [
                {"insight": "Market leadership", "supporting_quotes": [{"quote": "Q1"}]},
                {"insight": "Technology advantage", "supporting_quotes": [{"quote": "Q2"}]}
            ],
            "strengths": [
                {"insight": "Proprietary technology", "supporting_quotes": [{"quote": "Q3"}]}
            ],
            "weaknesses": [
                {"insight": "Market size limitation", "supporting_quotes": [{"quote": "Q4"}]}
            ]
        }
    
    def test_init(self):
        """Test DataStructureManager initialization."""
        self.assertEqual(self.manager.max_takeaways, 3)
        self.assertEqual(self.manager.max_strengths, 2)
        self.assertEqual(self.manager.max_weaknesses, 2)
    
    def test_create_structured_data_model(self):
        """Test structured data model creation."""
        model = self.manager.create_structured_data_model()
        
        self.assertIn("key_takeaways", model)
        self.assertIn("strengths", model)
        self.assertIn("weaknesses", model)
        self.assertIn("generation_timestamp", model)
        self.assertIn("template_version", model)
        self.assertTrue(model["data_structure_validated"])
        self.assertEqual(model["template_version"], "2.0")
    
    def test_parse_all_sections_basic(self):
        """Test basic section parsing."""
        response_text = """
Key Takeaways:
1. Market leadership position
- "We are the market leader" - John Doe, CEO from Company A
- "Strong competitive advantage" - Jane Smith, Manager from Company B

Strengths:
• Proprietary technology
- "Our technology is unique" - Tech Lead from Company A

Weaknesses:
- Market size constraints
- "Limited market opportunity" - Analyst from Company C
"""
        
        result = self.manager.parse_all_sections(response_text, [])
        
        self.assertIn("key_takeaways", result)
        self.assertIn("strengths", result)
        self.assertIn("weaknesses", result)
        self.assertGreater(len(result["key_takeaways"]), 0)
    
    def test_parse_quote_line_with_quotes_and_from(self):
        """Test quote line parsing with quotes and 'from'."""
        line = '- "This is a quote" - John Doe, CEO from Company A'
        result = self.manager._parse_quote_line(line)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["text"], "This is a quote")
        self.assertEqual(result["speaker_info"], "John Doe, CEO")
        self.assertEqual(result["transcript_name"], "Company A")
    
    def test_parse_quote_line_with_quotes_no_from(self):
        """Test quote line parsing with quotes but no 'from'."""
        line = '- "This is a quote" - John Doe, CEO'
        result = self.manager._parse_quote_line(line)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["text"], "This is a quote")
        self.assertEqual(result["speaker_info"], "John Doe, CEO")
        self.assertEqual(result["transcript_name"], "Unknown")
    
    def test_parse_quote_line_no_quotes_with_from(self):
        """Test quote line parsing without quotes but with 'from'."""
        line = '- This is a quote - John Doe, CEO from Company A'
        result = self.manager._parse_quote_line(line)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["text"], "This is a quote")
        self.assertEqual(result["speaker_info"], "John Doe, CEO")
        self.assertEqual(result["transcript_name"], "Company A")
    
    def test_parse_quote_line_no_quotes_no_from(self):
        """Test quote line parsing without quotes and without 'from'."""
        line = '- This is a quote - John Doe, CEO'
        result = self.manager._parse_quote_line(line)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["text"], "This is a quote")
        self.assertEqual(result["speaker_info"], "John Doe, CEO")
        self.assertEqual(result["transcript_name"], "Unknown")
    
    def test_parse_quote_line_invalid(self):
        """Test quote line parsing with invalid format."""
        line = 'Invalid line format'
        result = self.manager._parse_quote_line(line)
        
        self.assertIsNone(result)
    
    def test_determine_current_section_key_takeaways(self):
        """Test section determination for key takeaways."""
        line = "Key Takeaways:"
        current_section = None
        sections = {"key_takeaways": [], "strengths": [], "weaknesses": []}
        
        result = self.manager._determine_current_section(line, current_section, sections)
        
        self.assertEqual(result, "key_takeaways")
    
    def test_determine_current_section_strengths(self):
        """Test section determination for strengths."""
        line = "Strengths:"
        current_section = "key_takeaways"
        sections = {"key_takeaways": [{"insight": "Test"}], "strengths": [], "weaknesses": []}
        
        result = self.manager._determine_current_section(line, current_section, sections)
        
        self.assertEqual(result, "strengths")
    
    def test_determine_current_section_weaknesses(self):
        """Test section determination for weaknesses."""
        line = "Weaknesses:"
        current_section = "strengths"
        sections = {"key_takeaways": [{"insight": "Test"}], "strengths": [{"insight": "Test"}], "weaknesses": []}
        
        result = self.manager._determine_current_section(line, current_section, sections)
        
        self.assertEqual(result, "weaknesses")
    
    def test_determine_current_section_strengths_not_ready(self):
        """Test section determination when strengths section is not ready."""
        line = "Strengths:"
        current_section = "key_takeaways"
        sections = {"key_takeaways": [], "strengths": [], "weaknesses": []}
        
        result = self.manager._determine_current_section(line, current_section, sections)
        
        # Should stay in key_takeaways until we have 3 takeaways
        self.assertEqual(result, "key_takeaways")
    
    def test_determine_current_section_weaknesses_not_ready(self):
        """Test section determination when weaknesses section is not ready."""
        line = "Weaknesses:"
        current_section = "strengths"
        sections = {"key_takeaways": [{"insight": "Test"}], "strengths": [], "weaknesses": []}
        
        result = self.manager._determine_current_section(line, current_section, sections)
        
        # Should stay in strengths until we have 2 strengths
        self.assertEqual(result, "strengths")
    
    def test_enforce_correct_structure(self):
        """Test structure enforcement."""
        sections = {
            "key_takeaways": [{"insight": "KT1"}, {"insight": "KT2"}],
            "strengths": [{"insight": "S1"}, {"insight": "S2"}, {"insight": "S3"}],
            "weaknesses": [{"insight": "W1"}, {"insight": "W2"}, {"insight": "W3"}]
        }
        
        result = self.manager._enforce_correct_structure(sections)
        
        # Should have exactly 3 key takeaways, 2 strengths, 2 weaknesses
        self.assertEqual(len(result["key_takeaways"]), 3)
        self.assertEqual(len(result["strengths"]), 2)
        self.assertEqual(len(result["weaknesses"]), 2)
    
    def test_redistribute_by_content(self):
        """Test content-based redistribution."""
        sections = {
            "key_takeaways": [
                {"insight": "Technology advantage"},
                {"insight": "Market leadership"},
                {"insight": "Risk factors"},
                {"insight": "Growth potential"}
            ],
            "strengths": [{"insight": "Existing strength"}],
            "weaknesses": [{"insight": "Existing weakness"}]
        }
        
        self.manager._redistribute_by_content(sections)
        
        # Technology advantage should move to strengths
        # Risk factors should move to weaknesses
        self.assertLessEqual(len(sections["key_takeaways"]), 3)
        self.assertLessEqual(len(sections["strengths"]), 2)
        self.assertLessEqual(len(sections["weaknesses"]), 2)
    
    def test_duplicate_insights_if_needed(self):
        """Test insight duplication when needed."""
        sections = {
            "key_takeaways": [{"insight": "KT1"}],
            "strengths": [{"insight": "S1"}],
            "weaknesses": [{"insight": "W1"}]
        }
        
        self.manager._duplicate_insights_if_needed(sections)
        
        # Should have 3 key takeaways, 2 strengths, 2 weaknesses
        self.assertEqual(len(sections["key_takeaways"]), 3)
        self.assertEqual(len(sections["strengths"]), 2)
        self.assertEqual(len(sections["weaknesses"]), 2)
    
    def test_find_supporting_quotes(self):
        """Test finding supporting quotes for an insight."""
        insight = "Market leadership and competitive advantage"
        available_quotes = [
            {"text": "We are the market leader in this space"},
            {"text": "Our competitive advantage is technology"},
            {"text": "The weather is nice today"},
            {"text": "Market leadership comes from innovation"}
        ]
        
        result = self.manager.find_supporting_quotes(insight, available_quotes, max_quotes=2)
        
        # Should find quotes related to market leadership and competitive advantage
        self.assertLessEqual(len(result), 2)
        self.assertGreater(len(result), 0)
        
        # First quote should be most relevant
        first_quote = result[0]
        self.assertIn("market leader", first_quote["text"].lower())
    
    def test_filter_questions_from_takeaways(self):
        """Test filtering questions from takeaways."""
        takeaways = [
            {"insight": "Market leadership is strong"},
            {"insight": "What do you think about this?"},
            {"insight": "Technology advantage is clear"},
            {"insight": "How do you feel about the strategy?"}
        ]
        
        result = self.manager.filter_questions_from_takeaways(takeaways)
        
        # Should filter out questions
        self.assertEqual(len(result), 2)
        self.assertIn("Market leadership is strong", result[0]["insight"])
        self.assertIn("Technology advantage is clear", result[2]["insight"])
    
    def test_is_question_question_mark(self):
        """Test question detection with question mark."""
        self.assertTrue(self.manager._is_question("What is this?"))
        self.assertFalse(self.manager._is_question("This is a statement."))
    
    def test_is_question_interrogative_patterns(self):
        """Test question detection with interrogative patterns."""
        self.assertTrue(self.manager._is_question("What do you think about this?"))
        self.assertTrue(self.manager._is_question("How do you feel about the strategy?"))
        self.assertFalse(self.manager._is_question("What we need is innovation"))
    
    def test_validate_quote_structure_complete(self):
        """Test quote structure validation with complete quote."""
        quote = {
            "text": "Test quote",
            "transcript_name": "test.docx",
            "relevance_score": 0.8
        }
        
        result = self.manager.validate_quote_structure(quote)
        
        self.assertIn("id", result)
        self.assertIn("speaker_info", result)
        self.assertIn("sentiment", result)
        self.assertIn("theme", result)
        self.assertIn("date", result)
        self.assertIn("speaker_role", result)
        self.assertEqual(result["relevance_score"], 0.8)
    
    def test_validate_quote_structure_missing_relevance_score(self):
        """Test quote structure validation with missing relevance score."""
        quote = {"text": "Test quote"}
        result = self.manager.validate_quote_structure(quote)
        
        self.assertEqual(result["relevance_score"], 0.0)
    
    def test_validate_quote_structure_invalid_relevance_score(self):
        """Test quote structure validation with invalid relevance score."""
        quote = {"text": "Test quote", "relevance_score": "invalid"}
        result = self.manager.validate_quote_structure(quote)
        
        self.assertEqual(result["relevance_score"], 0.0)
    
    def test_get_structure_statistics(self):
        """Test structure statistics calculation."""
        stats = self.manager.get_structure_statistics(self.sample_sections)
        
        self.assertEqual(stats["key_takeaways_count"], 2)
        self.assertEqual(stats["strengths_count"], 1)
        self.assertEqual(stats["weaknesses_count"], 1)
        self.assertEqual(stats["total_insights"], 4)
        self.assertFalse(stats["structure_compliant"])  # Not compliant (need 3,2,2)
    
    def test_get_structure_statistics_compliant(self):
        """Test structure statistics with compliant structure."""
        compliant_sections = {
            "key_takeaways": [{"insight": "KT1"}, {"insight": "KT2"}, {"insight": "KT3"}],
            "strengths": [{"insight": "S1"}, {"insight": "S2"}],
            "weaknesses": [{"insight": "W1"}, {"insight": "W2"}]
        }
        
        stats = self.manager.get_structure_statistics(compliant_sections)
        
        self.assertTrue(stats["structure_compliant"])
        self.assertEqual(stats["key_takeaways_count"], 3)
        self.assertEqual(stats["strengths_count"], 2)
        self.assertEqual(stats["weaknesses_count"], 2)
    
    def test_save_current_insight(self):
        """Test saving current insight to sections."""
        sections = {"key_takeaways": [], "strengths": [], "weaknesses": []}
        current_section = "key_takeaways"
        current_insight = "Test insight"
        current_quotes = [{"quote": "Test quote"}]
        
        self.manager._save_current_insight(sections, current_section, current_insight, current_quotes)
        
        self.assertEqual(len(sections["key_takeaways"]), 1)
        self.assertEqual(sections["key_takeaways"][0]["insight"], "Test insight")
        self.assertEqual(sections["key_takeaways"][0]["supporting_quotes"], current_quotes)
    
    def test_save_current_insight_no_insight(self):
        """Test saving current insight with no insight."""
        sections = {"key_takeaways": [], "strengths": [], "weaknesses": []}
        current_section = "key_takeaways"
        current_insight = ""
        current_quotes = [{"quote": "Test quote"}]
        
        self.manager._save_current_insight(sections, current_section, current_insight, current_quotes)
        
        # Should not save anything
        self.assertEqual(len(sections["key_takeaways"]), 0)
    
    def test_save_current_insight_no_quotes(self):
        """Test saving current insight with no quotes."""
        sections = {"key_takeaways": [], "strengths": [], "weaknesses": []}
        current_section = "key_takeaways"
        current_insight = "Test insight"
        current_quotes = []
        
        self.manager._save_current_insight(sections, current_section, current_insight, current_quotes)
        
        # Should not save anything
        self.assertEqual(len(sections["key_takeaways"]), 0)


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)
