#!/usr/bin/env python3
"""
Unit tests for complex logic in quote_analysis_tool.py

This module tests the complex parsing and validation logic that handles:
- OpenAI response parsing (JSON and text formats)
- Data structure validation and correction
- Quote processing and categorization
"""

import unittest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import List, Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the classes we want to test
from quote_analysis_tool import ModularQuoteAnalysisTool


class TestComplexLogic(unittest.TestCase):
    """Test complex logic in quote analysis tool."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tool = ModularQuoteAnalysisTool()
        self.sample_quotes = [
            {
                'text': 'FlexXray provides excellent foreign material detection services.',
                'speaker_role': 'expert',
                'transcript_name': 'Test Transcript 1',
                'position': 1
            },
            {
                'text': 'The turnaround time is very fast.',
                'speaker_role': 'expert',
                'transcript_name': 'Test Transcript 2',
                'position': 2
            }
        ]
    
    def test_parse_json_response_with_markers(self):
        """Test parsing JSON response with markdown markers."""
        json_response = '''Here is the analysis:

```json
{
    "key_takeaways": [
        {
            "theme": "Market Leadership",
            "quotes": [
                {
                    "quote": "FlexXray is the market leader",
                    "speaker": "John Doe",
                    "document": "Transcript 1"
                }
            ]
        }
    ],
    "strengths": [
        {
            "theme": "Fast Turnaround",
            "quotes": [
                {
                    "quote": "Very fast service",
                    "speaker": "Jane Smith",
                    "document": "Transcript 2"
                }
            ]
        }
    ],
    "weaknesses": []
}
```'''
        
        result = self.tool._parse_summary_response(json_response, self.sample_quotes)
        
        self.assertIn('key_takeaways', result)
        self.assertIn('strengths', result)
        self.assertIn('weaknesses', result)
        self.assertEqual(len(result['key_takeaways']), 1)
        self.assertEqual(len(result['strengths']), 1)
        self.assertEqual(len(result['weaknesses']), 0)
        self.assertEqual(result['key_takeaways'][0]['insight'], 'Market Leadership')
        self.assertEqual(result['strengths'][0]['insight'], 'Fast Turnaround')
    
    def test_parse_json_response_without_markers(self):
        """Test parsing JSON response without markdown markers."""
        json_response = '''{
            "key_takeaways": [
                {
                    "theme": "Technology Advantage",
                    "quotes": [
                        {
                            "quote": "Proprietary technology",
                            "speaker": "Tech Expert",
                            "document": "Transcript 3"
                        }
                    ]
                }
            ],
            "strengths": [],
            "weaknesses": []
        }'''
        
        result = self.tool._parse_summary_response(json_response, self.sample_quotes)
        
        self.assertEqual(len(result['key_takeaways']), 1)
        self.assertEqual(result['key_takeaways'][0]['insight'], 'Technology Advantage')
    
    def test_parse_text_response_fallback(self):
        """Test fallback to text parsing when JSON fails."""
        text_response = '''Key Takeaways:
1. Market Leadership - FlexXray dominates the market
   - "We are the number one provider" - CEO from Company Overview
   - "Market leader in detection" - Manager from Industry Analysis

Strengths:
1. Fast Turnaround
   - "24-hour service" - Operations from Service Details
   - "Quick response time" - Customer from Testimonials

Weaknesses:
1. Limited Market Size
   - "Small TAM" - Analyst from Market Research'''
        
        result = self.tool._parse_summary_response(text_response, self.sample_quotes)
        
        self.assertIn('key_takeaways', result)
        self.assertIn('strengths', result)
        self.assertIn('weaknesses', result)
    
    def test_validate_and_supplement_takeaways(self):
        """Test validation and supplementation of takeaways."""
        incomplete_takeaways = [
            {
                'insight': 'Market Leadership',
                'supporting_quotes': [{'text': 'We are number one', 'transcript_name': 'Test'}]
            }
        ]
        
        # Test with 3 available quotes
        validated = self.tool._validate_and_supplement_takeaways(
            incomplete_takeaways, self.sample_quotes
        )
        
        self.assertGreaterEqual(len(validated), 1)
        self.assertEqual(validated[0]['insight'], 'Market Leadership')
    
    def test_parse_all_sections_with_complex_format(self):
        """Test parsing sections with complex formatting."""
        complex_response = '''Key Takeaways:
1. Market Leadership - FlexXray is the dominant player
   - "Market leader in detection" - CEO from Company Overview
   - "Number one provider" - Manager from Industry Analysis

2. Technology Advantage - Proprietary solutions
   - "Unique technology" - CTO from Tech Overview
   - "Patented methods" - Engineer from Development

3. Customer Focus - Strong relationships
   - "Customer satisfaction" - Sales from Customer Success

Strengths:
1. Fast Turnaround
   - "24-hour service" - Operations from Service Details

2. Quality Assurance
   - "99.9% accuracy" - QA from Quality Report

Weaknesses:
1. Market Limitations
   - "Small TAM" - Analyst from Market Research

2. Seasonal Variations
   - "Cyclical demand" - Finance from Financial Report'''
        
        sections = self.tool._parse_all_sections(complex_response, self.sample_quotes)
        
        self.assertEqual(len(sections['key_takeaways']), 3)
        self.assertEqual(len(sections['strengths']), 2)
        self.assertEqual(len(sections['weaknesses']), 2)
    
    def test_quote_citation_parsing(self):
        """Test parsing of different quote citation formats."""
        response_with_citations = '''Key Takeaways:
1. Market Leadership
   - "We are the market leader" - John Doe, CEO from Company Overview
   - "Number one position" - Jane Smith, Manager from Industry Analysis
   - Market dominance - Analyst from Market Report'''
        
        sections = self.tool._parse_all_sections(response_with_citations, self.sample_quotes)
        
        self.assertEqual(len(sections['key_takeaways']), 1)
        takeaway = sections['key_takeaways'][0]
        self.assertEqual(len(takeaway['supporting_quotes']), 3)
        
        # Check first quote format
        first_quote = takeaway['supporting_quotes'][0]
        self.assertEqual(first_quote['text'], 'We are the market leader')
        self.assertEqual(first_quote['speaker_info'], 'John Doe, CEO')
        self.assertEqual(first_quote['transcript_name'], 'Company Overview')
    
    def test_section_transition_logic(self):
        """Test the logic for transitioning between sections."""
        response_with_transitions = '''Key Takeaways:
1. First takeaway
   - "Quote 1" - Speaker from Transcript

2. Second takeaway
   - "Quote 2" - Speaker from Transcript

3. Third takeaway
   - "Quote 3" - Speaker from Transcript

Strengths:
1. First strength
   - "Quote 4" - Speaker from Transcript

2. Second strength
   - "Quote 5" - Speaker from Transcript

Weaknesses:
1. First weakness
   - "Quote 6" - Speaker from Transcript

2. Second weakness
   - "Quote 7" - Speaker from Transcript'''
        
        sections = self.tool._parse_all_sections(response_with_transitions, self.sample_quotes)
        
        # Should have exactly 3 takeaways, 2 strengths, 2 weaknesses
        self.assertEqual(len(sections['key_takeaways']), 3)
        self.assertEqual(len(sections['strengths']), 2)
        self.assertEqual(len(sections['weaknesses']), 2)
    
    def test_error_handling_in_json_parsing(self):
        """Test error handling when JSON parsing fails."""
        malformed_json = '''Here is the analysis:

```json
{
    "key_takeaways": [
        {
            "theme": "Market Leadership",
            "quotes": [
                {
                    "quote": "We are the leader",
                    "speaker": "CEO"
                }
            ]
        }
    ],
    "strengths": [
        {
            "theme": "Fast Service",
            "quotes": [
                {
                    "quote": "24-hour turnaround",
                    "speaker": "Operations"
                }
            ]
        }
    ]
}'''
        
        # This should trigger the text parsing fallback
        result = self.tool._parse_summary_response(malformed_json, self.sample_quotes)
        
        # Should still return a valid structure
        self.assertIn('key_takeaways', result)
        self.assertIn('strengths', result)
    
    def test_empty_response_handling(self):
        """Test handling of empty or minimal responses."""
        empty_response = ""
        result = self.tool._parse_summary_response(empty_response, self.sample_quotes)
        
        # Should return structured data model even for empty responses
        self.assertIn('key_takeaways', result)
        self.assertIn('strengths', result)
        self.assertIn('weaknesses', result)
        self.assertIn('generation_timestamp', result)
        self.assertIn('template_version', result)
        self.assertIn('data_structure_validated', result)
        
        # All sections should be empty lists
        self.assertEqual(result['key_takeaways'], [])
        self.assertEqual(result['strengths'], [])
        self.assertEqual(result['weaknesses'], [])
    
    def test_quote_metadata_preservation(self):
        """Test that quote metadata is properly preserved during parsing."""
        response_with_metadata = '''Key Takeaways:
1. Market Leadership
   - "We dominate the market" - John Doe, CEO from Company Overview
   - "Number one position" - Jane Smith, Manager from Industry Analysis'''
        
        sections = self.tool._parse_all_sections(response_with_metadata, self.sample_quotes)
        
        takeaway = sections['key_takeaways'][0]
        quotes = takeaway['supporting_quotes']
        
        self.assertEqual(len(quotes), 2)
        
        # Check metadata preservation
        first_quote = quotes[0]
        self.assertIn('text', first_quote)
        self.assertIn('speaker_info', first_quote)
        self.assertIn('transcript_name', first_quote)
        
        self.assertEqual(first_quote['text'], 'We dominate the market')
        self.assertEqual(first_quote['speaker_info'], 'John Doe, CEO')
        self.assertEqual(first_quote['transcript_name'], 'Company Overview')


class TestDataStructureValidation(unittest.TestCase):
    """Test data structure validation logic."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tool = ModularQuoteAnalysisTool()
    
    def test_structure_enforcement(self):
        """Test enforcement of 3+2+2 structure."""
        sections = {
            'key_takeaways': [
                {'insight': 'Takeaway 1', 'supporting_quotes': []},
                {'insight': 'Takeaway 2', 'supporting_quotes': []}
            ],
            'strengths': [
                {'insight': 'Strength 1', 'supporting_quotes': []},
                {'insight': 'Strength 2', 'supporting_quotes': []},
                {'insight': 'Strength 3', 'supporting_quotes': []}
            ],
            'weaknesses': [
                {'insight': 'Weakness 1', 'supporting_quotes': []}
            ]
        }
        
        # This should trigger structure correction
        corrected = self.tool._enforce_correct_structure(sections)
        
        self.assertEqual(len(corrected['key_takeaways']), 3)
        self.assertEqual(len(corrected['strengths']), 2)
        self.assertEqual(len(corrected['weaknesses']), 2)


if __name__ == '__main__':
    unittest.main()
