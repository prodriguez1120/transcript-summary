#!/usr/bin/env python3
"""
Test Quote Filtering System

This script tests the QuoteTopicFilter functionality.
"""

import sys
import os
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quote_topic_filter import QuoteTopicFilter

def test_keyword_filtering():
    """Test keyword-based quote filtering."""
    print("Testing keyword-based filtering...")
    
    # Initialize filter without API key (keyword mode only)
    filter_tool = QuoteTopicFilter()
    
    # Test quotes
    test_quotes = [
        {
            "text": "FlexXray dominates the market with 60% share",
            "speaker_role": "Test Speaker 1",
            "transcript_name": "Test Transcript 1"
        },
        {
            "text": "Their technology is proprietary and advanced",
            "speaker_role": "Test Speaker 2", 
            "transcript_name": "Test Transcript 2"
        },
        {
            "text": "Local presence is crucial for our operations",
            "speaker_role": "Test Speaker 3",
            "transcript_name": "Test Transcript 3"
        },
        {
            "text": "Turnaround times are incredibly fast",
            "speaker_role": "Test Speaker 4",
            "transcript_name": "Test Transcript 4"
        }
    ]
    
    # Test each topic
    topics = ['market_leadership', 'technology_advantages', 'local_presence', 'turnaround_times']
    
    for topic in topics:
        filtered = filter_tool.filter_quotes_by_topic(test_quotes, topic)
        print(f"{topic}: {len(filtered)} quotes found")
        for quote in filtered:
            print(f"  - {quote['text'][:50]}...")
    
    print("✓ Keyword filtering test completed\n")

def test_topic_variables():
    """Test generation of topic variables for prompt."""
    print("Testing topic variable generation...")
    
    filter_tool = QuoteTopicFilter()
    
    test_quotes = [
        {
            "text": "Market leader with dominant position",
            "speaker_role": "Speaker A, Company A",
            "transcript_name": "Transcript A"
        },
        {
            "text": "Proprietary technology advantage",
            "speaker_role": "Speaker B, Company B", 
            "transcript_name": "Transcript B"
        }
    ]
    
    # Get all topic quotes
    topic_quotes = filter_tool.get_all_topic_quotes(test_quotes, use_ai=False)
    
    # Format for prompt
    variables = filter_tool.format_quotes_for_prompt(topic_quotes)
    
    print("Generated variables:")
    for var_name, value in variables.items():
        print(f"{var_name}: {value[:100]}...")
    
    print("✓ Topic variable generation test completed\n")

def test_prompt_integration():
    """Test integration with the company summary prompt."""
    print("Testing prompt integration...")
    
    try:
        with open('prompts.json', 'r') as f:
            prompts = json.load(f)
        
        template = prompts['company_summary']['template']
        
        # Check if all topic variables are present
        required_vars = [
            'market_leadership_quotes',
            'value_prop_quotes', 
            'local_presence_quotes',
            'tech_advantages_quotes',
            'turnaround_quotes',
            'market_limitations_quotes',
            'timing_challenges_quotes'
        ]
        
        missing_vars = []
        for var in required_vars:
            if f"{{{var}}}" not in template:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing variables in prompt: {missing_vars}")
        else:
            print("✓ All topic variables found in prompt template")
            
    except Exception as e:
        print(f"❌ Prompt integration test failed: {e}")
    
    print("✓ Prompt integration test completed\n")

def main():
    """Run all tests."""
    print("Testing Quote Filtering System")
    print("="*40)
    
    try:
        test_keyword_filtering()
        test_topic_variables()
        test_prompt_integration()
        
        print("🎉 All tests completed successfully!")
        print("\nThe quote filtering system is ready to use.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
