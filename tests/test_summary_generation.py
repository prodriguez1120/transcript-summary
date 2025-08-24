#!/usr/bin/env python3
"""
Unit tests for SummaryGenerator module
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import sys
import os

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from summary_generation import SummaryGenerator


class TestSummaryGenerator(unittest.TestCase):
    """Test cases for SummaryGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock OpenAI client
        self.mock_client = Mock()
        self.mock_response = Mock()
        self.mock_choice = Mock()
        self.mock_message = Mock()
        
        # Set up the mock chain
        self.mock_client.chat.completions.create.return_value = self.mock_response
        self.mock_response.choices = [self.mock_choice]
        self.mock_choice.message = self.mock_message
        
        # Mock prompt config
        self.mock_prompt_config = Mock()
        self.mock_prompt_config.get_prompt_parameters.return_value = {
            "model": "gpt-4",
            "temperature": 0.3,
            "max_tokens": 3000
        }
        self.mock_prompt_config.get_system_message.return_value = "You are an expert analyst."
        self.mock_prompt_config.get_prompt_template.return_value = "Analyze: {quotes_list}"
        
        # Initialize the generator
        self.generator = SummaryGenerator(self.mock_client, self.mock_prompt_config)
        
        # Sample quotes for testing
        self.sample_quotes = [
            {
                "text": "FlexXray provides excellent service quality.",
                "speaker_role": "expert",
                "transcript_name": "John Doe - Acme Corp - Manager.docx"
            },
            {
                "text": "The technology is very innovative.",
                "speaker_role": "expert",
                "transcript_name": "Jane Smith - Tech Corp - Engineer.docx"
            }
        ]
    
    def test_init(self):
        """Test SummaryGenerator initialization."""
        self.assertEqual(self.generator.client, self.mock_client)
        self.assertEqual(self.generator.prompt_config, self.mock_prompt_config)
    
    def test_generate_company_summary_direct_success(self):
        """Test successful direct summary generation."""
        # Mock response content
        self.mock_message.content = json.dumps({
            "key_takeaways": [
                {
                    "theme": "Service Quality",
                    "quotes": [
                        {"quote": "Excellent service", "speaker": "John", "document": "Doc1"}
                    ]
                }
            ],
            "strengths": [],
            "weaknesses": []
        })
        
        result = self.generator.generate_company_summary_direct(self.sample_quotes)
        
        # Verify OpenAI was called
        self.mock_client.chat.completions.create.assert_called_once()
        
        # Verify result structure
        self.assertIn("key_takeaways", result)
        self.assertIn("strengths", result)
        self.assertIn("weaknesses", result)
        self.assertEqual(result["total_quotes_analyzed"], 2)
    
    def test_generate_company_summary_direct_empty_quotes(self):
        """Test direct summary generation with empty quotes."""
        result = self.generator.generate_company_summary_direct([])
        self.assertEqual(result, {})
    
    def test_generate_company_summary_direct_empty_response(self):
        """Test direct summary generation with empty OpenAI response."""
        self.mock_message.content = ""
        
        result = self.generator.generate_company_summary_direct(self.sample_quotes)
        
        self.assertEqual(result, {})
    
    def test_generate_company_summary_direct_exception(self):
        """Test direct summary generation with exception."""
        self.mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        result = self.generator.generate_company_summary_direct(self.sample_quotes)
        
        self.assertEqual(result, {})
    
    def test_generate_company_summary_with_batching(self):
        """Test batch summary generation."""
        # Mock response content for batches
        self.mock_message.content = json.dumps({
            "key_takeaways": [{"theme": "Test", "quotes": []}],
            "strengths": [],
            "weaknesses": []
        })
        
        result = self.generator.generate_company_summary_with_batching(self.sample_quotes, batch_size=1)
        
        # Should process 2 quotes in 2 batches
        self.assertIn("batch_processing_used", result)
        self.assertEqual(result["total_batches"], 2)
        self.assertEqual(result["total_quotes_analyzed"], 2)
    
    def test_generate_company_summary_with_batching_empty_quotes(self):
        """Test batch summary generation with empty quotes."""
        result = self.generator.generate_company_summary_with_batching([], batch_size=25)
        self.assertEqual(result, {})
    
    def test_create_structured_data_model(self):
        """Test structured data model creation."""
        model = self.generator._create_structured_data_model()
        
        self.assertIn("key_takeaways", model)
        self.assertIn("strengths", model)
        self.assertIn("weaknesses", model)
        self.assertIn("generation_timestamp", model)
        self.assertIn("template_version", model)
        self.assertTrue(model["data_structure_validated"])
    
    def test_create_summary_prompt(self):
        """Test summary prompt creation."""
        prompt = self.generator._create_summary_prompt(self.sample_quotes)
        
        self.assertIn("FlexXray provides excellent service quality", prompt)
        self.assertIn("The technology is very innovative", prompt)
        self.assertIn("John Doe (Expert)", prompt)
        self.assertIn("Jane Smith (Expert)", prompt)
    
    def test_create_summary_prompt_limit_quotes(self):
        """Test that prompt limits quotes to 30."""
        # Create 35 quotes
        many_quotes = [{"text": f"Quote {i}", "speaker_role": "expert", "transcript_name": "test.docx"} 
                       for i in range(35)]
        
        prompt = self.generator._create_summary_prompt(many_quotes)
        
        # Should only include first 30 quotes
        self.assertIn("Quote 1", prompt)
        self.assertIn("Quote 30", prompt)
        self.assertNotIn("Quote 31", prompt)
    
    def test_create_summary_prompt_template_error_fallback(self):
        """Test prompt creation with template error fallback."""
        # Mock template error
        self.mock_prompt_config.get_prompt_template.side_effect = Exception("Template error")
        
        prompt = self.generator._create_summary_prompt(self.sample_quotes)
        
        # Should use fallback prompt
        self.assertIn("business intelligence analyst", prompt)
        self.assertIn("FlexXray provides excellent service quality", prompt)
    
    def test_extract_json_from_response_triple_backticks(self):
        """Test JSON extraction from triple backticks."""
        response_text = '```json\n{"key": "value"}\n```'
        result = self.generator._extract_json_from_response(response_text)
        
        self.assertEqual(result, '{"key": "value"}')
    
    def test_extract_json_from_response_single_backticks(self):
        """Test JSON extraction from single backticks."""
        response_text = '```{"key": "value"}```'
        result = self.generator._extract_json_from_response(response_text)
        
        self.assertEqual(result, '{"key": "value"}')
    
    def test_extract_json_from_response_curly_braces(self):
        """Test JSON extraction from curly braces."""
        response_text = 'Some text {"key": "value"} more text'
        result = self.generator._extract_json_from_response(response_text)
        
        self.assertEqual(result, '{"key": "value"}')
    
    def test_extract_json_from_response_no_json(self):
        """Test JSON extraction when no JSON found."""
        response_text = 'Just plain text without JSON'
        result = self.generator._extract_json_from_response(response_text)
        
        self.assertEqual(result, response_text)
    
    def test_consolidate_key_takeaways(self):
        """Test key takeaways consolidation."""
        takeaways = [
            {"theme": "Theme1", "quotes": [{"quote": "Q1"}, {"quote": "Q2"}]},
            {"theme": "Theme2", "quotes": [{"quote": "Q3"}, {"quote": "Q4"}, {"quote": "Q5"}]}
        ]
        
        result = self.generator._consolidate_key_takeaways(takeaways)
        
        # Should have 2 themes
        self.assertEqual(len(result), 2)
        
        # First theme should have 3 quotes (padded)
        theme1 = next(t for t in result if t["theme"] == "Theme1")
        self.assertEqual(len(theme1["quotes"]), 3)
        
        # Second theme should have 3 quotes (trimmed)
        theme2 = next(t for t in result if t["theme"] == "Theme2")
        self.assertEqual(len(theme2["quotes"]), 3)
    
    def test_consolidate_strengths(self):
        """Test strengths consolidation."""
        strengths = [
            {"theme": "Strength1", "quotes": [{"quote": "Q1"}]},
            {"theme": "Strength2", "quotes": [{"quote": "Q2"}, {"quote": "Q3"}, {"quote": "Q4"}]}
        ]
        
        result = self.generator._consolidate_strengths(strengths)
        
        # Should have 2 themes
        self.assertEqual(len(result), 2)
        
        # First theme should have 2 quotes (padded)
        strength1 = next(s for s in result if s["theme"] == "Strength1")
        self.assertEqual(len(strength1["quotes"]), 2)
        
        # Second theme should have 2 quotes (trimmed)
        strength2 = next(s for s in result if s["theme"] == "Strength2")
        self.assertEqual(len(strength2["quotes"]), 2)
    
    def test_consolidate_weaknesses(self):
        """Test weaknesses consolidation."""
        weaknesses = [
            {"theme": "Weakness1", "quotes": []},
            {"theme": "Weakness2", "quotes": [{"quote": "Q1"}]}
        ]
        
        result = self.generator._consolidate_weaknesses(weaknesses)
        
        # Should have 2 themes
        self.assertEqual(len(result), 2)
        
        # Both themes should have 2 quotes (padded)
        for weakness in result:
            self.assertEqual(len(weakness["quotes"]), 2)
    
    def test_validate_and_fix_key_takeaways(self):
        """Test key takeaways validation and fixing."""
        takeaways = [
            {
                "theme": "Test Theme",
                "quotes": [
                    {"quote": "Quote 1", "speaker": "Speaker 1", "document": "Doc 1"},
                    {"quote": "Quote 2", "speaker": "Speaker 2", "document": "Doc 2"}
                ]
            }
        ]
        
        result = self.generator._validate_and_fix_key_takeaways(takeaways, self.sample_quotes)
        
        # Should have 1 theme
        self.assertEqual(len(result), 1)
        
        # Should have 3 supporting quotes (padded)
        theme = result[0]
        self.assertEqual(len(theme["supporting_quotes"]), 3)
        self.assertEqual(theme["insight"], "Test Theme")
    
    def test_validate_and_fix_strengths(self):
        """Test strengths validation and fixing."""
        strengths = [
            {
                "theme": "Test Strength",
                "quotes": [{"quote": "Quote 1", "speaker": "Speaker 1", "document": "Doc 1"}]
            }
        ]
        
        result = self.generator._validate_and_fix_strengths(strengths, self.sample_quotes)
        
        # Should have 1 theme
        self.assertEqual(len(result), 1)
        
        # Should have 2 supporting quotes (padded)
        strength = result[0]
        self.assertEqual(len(strength["supporting_quotes"]), 2)
        self.assertEqual(strength["insight"], "Test Strength")
    
    def test_validate_and_fix_weaknesses(self):
        """Test weaknesses validation and fixing."""
        weaknesses = [
            {
                "theme": "Test Weakness",
                "quotes": []
            }
        ]
        
        result = self.generator._validate_and_fix_weaknesses(weaknesses, self.sample_quotes)
        
        # Should have 1 theme
        self.assertEqual(len(result), 1)
        
        # Should have 2 supporting quotes (padded)
        weakness = result[0]
        self.assertEqual(len(weakness["supporting_quotes"]), 2)
        self.assertEqual(weakness["insight"], "Test Weakness")
    
    def test_parse_summary_response_success(self):
        """Test successful summary response parsing."""
        response_text = json.dumps({
            "key_takeaways": [
                {
                    "theme": "Theme 1",
                    "quotes": [
                        {"quote": "Q1", "speaker": "S1", "document": "D1"},
                        {"quote": "Q2", "speaker": "S2", "document": "D2"},
                        {"quote": "Q3", "speaker": "S3", "document": "D3"}
                    ]
                }
            ],
            "strengths": [],
            "weaknesses": []
        })
        
        result = self.generator._parse_summary_response(response_text, self.sample_quotes)
        
        self.assertIn("key_takeaways", result)
        self.assertEqual(len(result["key_takeaways"]), 1)
        self.assertEqual(result["total_quotes_analyzed"], 2)
    
    def test_parse_summary_response_empty(self):
        """Test parsing empty response."""
        result = self.generator._parse_summary_response("", self.sample_quotes)
        
        self.assertIn("key_takeaways", result)
        self.assertEqual(result["total_quotes_analyzed"], 2)
    
    def test_parse_summary_response_json_error(self):
        """Test parsing response with JSON error."""
        result = self.generator._parse_summary_response("invalid json", self.sample_quotes)
        
        self.assertIn("key_takeaways", result)
        self.assertEqual(result["total_quotes_analyzed"], 2)


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)
