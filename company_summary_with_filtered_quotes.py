#!/usr/bin/env python3
"""
Company Summary with Pre-filtered Quotes

This script demonstrates how to use the QuoteTopicFilter to create
a company summary with pre-filtered quotes by topic.
"""

import json
import os
from dotenv import load_dotenv
from quote_topic_filter import QuoteTopicFilter
from quote_analysis_core import QuoteAnalysisTool

# Load environment variables
load_dotenv()

def load_prompts():
    """Load prompts from prompts.json."""
    try:
        with open('prompts.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: prompts.json not found")
        return None

def create_company_summary_with_filtered_quotes(quotes: list, use_ai_filtering: bool = True):
    """Create company summary using pre-filtered quotes by topic."""
    
    # Initialize quote topic filter
    topic_filter = QuoteTopicFilter(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Get quotes filtered by topic
    print("Filtering quotes by topic...")
    topic_quotes = topic_filter.get_all_topic_quotes(quotes, use_ai=use_ai_filtering)
    
    # Format quotes for prompt variables
    prompt_variables = topic_filter.format_quotes_for_prompt(topic_quotes)
    
    # Load prompts
    prompts = load_prompts()
    if not prompts:
        return None
    
    # Get company summary template
    template = prompts['company_summary']['template']
    
    # Replace all topic variables in the template
    for variable, value in prompt_variables.items():
        template = template.replace(f"{{{variable}}}", value)
    
    print("\n" + "="*60)
    print("COMPANY SUMMARY PROMPT WITH PRE-FILTERED QUOTES")
    print("="*60)
    print(template)
    
    return template, prompt_variables

def demo_with_sample_quotes():
    """Demonstrate the system with sample quotes."""
    
    # Sample quotes for demonstration
    sample_quotes = [
        {
            "text": "FlexXray is the dominant player in the foreign material inspection market with over 60% market share.",
            "speaker_role": "George Perry-West, Former FSQA Manager, Pegasus Foods",
            "transcript_name": "George Perry-West - Pegasus Foods Interview"
        },
        {
            "text": "Their proprietary x-ray technology gives them a significant advantage over competitors.",
            "speaker_role": "Lee Reece, Lead FSQA, The Kraft Heinz Company",
            "transcript_name": "Lee Reece - Kraft Heinz Interview"
        },
        {
            "text": "The local presence and rapid turnaround times are what make them indispensable to our operations.",
            "speaker_role": "Cheryl Bertics, Former Manager, FlexXray Services",
            "transcript_name": "Cheryl Bertics - FlexXray Services Interview"
        },
        {
            "text": "Insourcing this capability would require massive capital investment and years of development.",
            "speaker_role": "Eli Dantas, General Manager, Cargill Inc",
            "transcript_name": "Eli Dantas - Cargill Interview"
        },
        {
            "text": "The market is limited by the number of food processing facilities that need this service.",
            "speaker_role": "Peter Poteres, Former Director FSQA, Sara Lee",
            "transcript_name": "Peter Poteres - Sara Lee Interview"
        },
        {
            "text": "Their response time is incredible - we get results within hours, not days.",
            "speaker_role": "Randy Jesberg, Former CEO, Food Processing Co",
            "transcript_name": "Randy Jesberg - CEO Interview"
        },
        {
            "text": "The timing of contamination events is completely unpredictable, making their service essential.",
            "speaker_role": "Industry Expert, Food Safety Consultant",
            "transcript_name": "Industry Expert Interview"
        }
    ]
    
    print("DEMONSTRATION: Company Summary with Pre-filtered Quotes")
    print("="*60)
    
    # Create summary with AI filtering
    template, variables = create_company_summary_with_filtered_quotes(sample_quotes, use_ai_filtering=True)
    
    print("\n" + "="*60)
    print("TOPIC QUOTE VARIABLES GENERATED:")
    print("="*60)
    
    for topic, quotes in variables.items():
        print(f"\n{topic.upper()}:")
        print("-" * 40)
        print(quotes)
    
    return template, variables

def main():
    """Main function to run the demonstration."""
    print("FlexXray Company Summary with Pre-filtered Quotes")
    print("="*60)
    
    # Check if OpenAI API key is available
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Warning: OPENAI_API_KEY not found. AI filtering will be disabled.")
        print("Using keyword-based filtering instead.")
    
    # Run demonstration
    template, variables = demo_with_sample_quotes()
    
    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    print("1. Use the generated template with your OpenAI API call")
    print("2. The template now contains pre-filtered quotes for each topic")
    print("3. AI will select the most relevant quotes from each topic pool")
    print("4. Results will be more focused and consistent")
    
    return template, variables

if __name__ == "__main__":
    main()
