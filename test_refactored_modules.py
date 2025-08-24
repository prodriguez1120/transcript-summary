#!/usr/bin/env python3
"""
Comprehensive test for all refactored modules working together
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import json

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from quote_processing import QuoteProcessor
from summary_generation import SummaryGenerator
from data_structures import DataStructureManager


class TestRefactoredModulesIntegration(unittest.TestCase):
    """Test that all refactored modules work together correctly."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.quote_processor = QuoteProcessor()
        self.data_structure_manager = DataStructureManager()
        
        # Mock OpenAI client and prompt config for summary generator
        self.mock_client = Mock()
        self.mock_prompt_config = Mock()
        self.mock_prompt_config.get_prompt_parameters.return_value = {
            "model": "gpt-4",
            "temperature": 0.3,
            "max_tokens": 3000
        }
        self.mock_prompt_config.get_system_message.return_value = "You are an expert analyst."
        self.mock_prompt_config.get_prompt_template.return_value = "Analyze: {quotes_list}"
        
        self.summary_generator = SummaryGenerator(self.mock_client, self.mock_prompt_config)
        
        # Sample data for testing
        self.sample_quotes = [
            {
                "text": "FlexXray provides excellent service quality and rapid turnaround times.",
                "transcript_name": "John Doe - Acme Corp - Manager.docx",
                "speaker_role": "expert",
                "relevance_score": 0.85
            },
            {
                "text": "The market leadership position and competitive advantages are clear.",
                "transcript_name": "Jane Smith - Former CEO - Follow Up (07.22.2025).docx",
                "speaker_role": "expert",
                "focus_area_matched": "competitive advantages"
            },
            {
                "text": "Technology innovation drives our success.",
                "transcript_name": "Tech Lead - Innovation Corp - Engineer.docx",
                "speaker_role": "expert",
                "relevance_score": 0.9
            }
        ]
    
    def test_quote_processing_integration(self):
        """Test that QuoteProcessor works correctly with sample data."""
        # Test quote enrichment
        enriched_quotes = self.quote_processor.enrich_quotes_for_export(self.sample_quotes)
        
        self.assertEqual(len(enriched_quotes), 3)
        
        # Check first quote
        first_quote = enriched_quotes[0]
        self.assertIn("speaker_info", first_quote)
        self.assertEqual(first_quote["speaker_info"]["name"], "John Doe")
        self.assertEqual(first_quote["speaker_info"]["company"], "Acme Corp")
        self.assertEqual(first_quote["theme"], "service_quality")
        self.assertEqual(first_quote["sentiment"], "neutral")
        
        # Check second quote (Randy_Jesberg case)
        second_quote = enriched_quotes[1]
        self.assertEqual(second_quote["speaker_info"]["name"], "Jane Smith - Former CEO")
        self.assertEqual(second_quote["date"], "2025-07-22")
        
        # Check third quote
        third_quote = enriched_quotes[2]
        self.assertEqual(third_quote["theme"], "technology_advantages")
    
    def test_data_structures_integration(self):
        """Test that DataStructureManager works correctly with sample data."""
        # Test structured data model creation
        model = self.data_structure_manager.create_structured_data_model()
        
        self.assertIn("key_takeaways", model)
        self.assertIn("strengths", model)
        self.assertIn("weaknesses", model)
        self.assertEqual(model["template_version"], "2.0")
        
        # Test quote structure validation
        for quote in self.sample_quotes:
            validated_quote = self.data_structure_manager.validate_quote_structure(quote)
            self.assertIn("id", validated_quote)
            self.assertIn("speaker_info", validated_quote)
            self.assertIn("sentiment", validated_quote)
            self.assertIn("theme", validated_quote)
            self.assertIn("date", validated_quote)
            self.assertIn("speaker_role", validated_quote)
    
    def test_summary_generation_integration(self):
        """Test that SummaryGenerator works correctly with sample data."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        
        self.mock_client.chat.completions.create.return_value = mock_response
        mock_response.choices = [mock_choice]
        mock_choice.message = mock_message
        
        # Mock successful response
        mock_message.content = json.dumps({
            "key_takeaways": [
                {
                    "theme": "Service Quality",
                    "quotes": [
                        {"quote": "Excellent service", "speaker": "John", "document": "Doc1"},
                        {"quote": "Rapid turnaround", "speaker": "John", "document": "Doc1"},
                        {"quote": "Customer satisfaction", "speaker": "John", "document": "Doc1"}
                    ]
                }
            ],
            "strengths": [
                {
                    "theme": "Technology Innovation",
                    "quotes": [
                        {"quote": "Innovation drives success", "speaker": "Tech Lead", "document": "Doc3"},
                        {"quote": "Proprietary technology", "speaker": "Tech Lead", "document": "Doc3"}
                    ]
                }
            ],
            "weaknesses": [
                {
                    "theme": "Market Constraints",
                    "quotes": [
                        {"quote": "Limited market size", "speaker": "Analyst", "document": "Doc2"},
                        {"quote": "Growth challenges", "speaker": "Analyst", "document": "Doc2"}
                    ]
                }
            ]
        })
        
        # Test summary generation
        result = self.summary_generator.generate_company_summary_direct(self.sample_quotes)
        
        # Verify OpenAI was called
        self.mock_client.chat.completions.create.assert_called_once()
        
        # Verify result structure
        self.assertIn("key_takeaways", result)
        self.assertIn("strengths", result)
        self.assertIn("weaknesses", result)
        self.assertEqual(result["total_quotes_analyzed"], 3)
        
        # Verify key takeaways have exactly 3 quotes
        key_takeaway = result["key_takeaways"][0]
        self.assertEqual(len(key_takeaway["supporting_quotes"]), 3)
        
        # Verify strengths have exactly 2 quotes
        strength = result["strengths"][0]
        self.assertEqual(len(strength["supporting_quotes"]), 2)
        
        # Verify weaknesses have exactly 2 quotes
        weakness = result["weaknesses"][0]
        self.assertEqual(len(weakness["supporting_quotes"]), 2)
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow using all modules."""
        # 1. Process quotes through QuoteProcessor
        enriched_quotes = self.quote_processor.enrich_quotes_for_export(self.sample_quotes)
        
        # 2. Validate quote structures through DataStructureManager
        validated_quotes = []
        for quote in enriched_quotes:
            validated_quote = self.data_structure_manager.validate_quote_structure(quote)
            validated_quotes.append(validated_quote)
        
        # 3. Generate summary through SummaryGenerator
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        
        self.mock_client.chat.completions.create.return_value = mock_response
        mock_response.choices = [mock_choice]
        mock_choice.message = mock_message
        
        # Mock a simple response
        mock_message.content = json.dumps({
            "key_takeaways": [
                {
                    "theme": "Test Theme",
                    "quotes": [
                        {"quote": "Test quote 1", "speaker": "Test", "document": "Test"},
                        {"quote": "Test quote 2", "speaker": "Test", "document": "Test"},
                        {"quote": "Test quote 3", "speaker": "Test", "document": "Test"}
                    ]
                }
            ],
            "strengths": [],
            "weaknesses": []
        })
        
        summary = self.summary_generator.generate_company_summary_direct(validated_quotes)
        
        # 4. Verify the complete workflow
        self.assertIsNotNone(summary)
        self.assertIn("key_takeaways", summary)
        self.assertIn("strengths", summary)
        self.assertIn("weaknesses", summary)
        self.assertEqual(summary["total_quotes_analyzed"], 3)
        
        # 5. Test statistics
        stats = self.data_structure_manager.get_structure_statistics(summary)
        self.assertIn("key_takeaways_count", stats)
        self.assertIn("structure_compliant", stats)
    
    def test_error_handling_integration(self):
        """Test error handling across all modules."""
        # Test with empty quotes
        empty_result = self.quote_processor.enrich_quotes_for_export([])
        self.assertEqual(empty_result, [])
        
        # Test with empty quotes in summary generator
        empty_summary = self.summary_generator.generate_company_summary_direct([])
        self.assertEqual(empty_summary, {})
        
        # Test with empty quotes in data structure manager
        empty_stats = self.data_structure_manager.get_structure_statistics({})
        self.assertEqual(empty_stats["total_insights"], 0)
        self.assertFalse(empty_stats["structure_compliant"])
    
    def test_quote_formatting_integration(self):
        """Test quote formatting functionality across modules."""
        # Test quote formatting
        formatted_quote = self.quote_processor.format_quote_for_display(self.sample_quotes[0])
        
        self.assertIn("FlexXray provides excellent service quality", formatted_quote)
        self.assertIn("John Doe, Acme Corp, Manager.docx", formatted_quote)
        
        # Test quote statistics
        stats = self.quote_processor.get_quote_statistics(self.sample_quotes)
        
        self.assertEqual(stats["total_quotes"], 3)
        self.assertIn("service_quality", stats["themes"])
        self.assertIn("technology_advantages", stats["themes"])
    
    def test_batch_processing_integration(self):
        """Test batch processing functionality."""
        # Create more quotes for batch testing
        many_quotes = []
        for i in range(50):
            quote = {
                "text": f"Quote {i} about market leadership and technology",
                "transcript_name": f"Speaker_{i} - Company_{i} - Title_{i}.docx",
                "speaker_role": "expert",
                "relevance_score": 0.8
            }
            many_quotes.append(quote)
        
        # Test batch processing
        result = self.summary_generator.generate_company_summary_with_batching(many_quotes, batch_size=10)
        
        # Should have batch processing info
        self.assertIn("batch_processing_used", result)
        self.assertEqual(result["total_quotes_analyzed"], 50)
        self.assertGreater(result["total_batches"], 1)


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)
