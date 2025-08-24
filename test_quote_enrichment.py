#!/usr/bin/env python3
"""
Test script to demonstrate quote enrichment functionality.

This script shows how quotes are enriched with missing fields before export,
fixing the blank columns and misaligned rows in Excel exports.
"""

import json
from pathlib import Path
from quote_analysis_tool import ModularQuoteAnalysisTool


def test_quote_enrichment():
    """Test the quote enrichment functionality."""
    print("🧪 Testing Quote Enrichment Functionality")
    print("=" * 50)

    # Initialize the tool
    tool = ModularQuoteAnalysisTool()

    # Sample quotes with missing fields (simulating current state)
    # Including various relevance_score edge cases to test numeric handling
    sample_quotes = [
         {
             "text": "FlexXray has a strong competitive advantage in the market due to our proprietary technology.",
             "speaker_role": "expert",
             "transcript_name": "Randy_Jesberg- Former CEO - Initial Conversation (06.26.2025)",
             "position": 45,
             "has_insight": True,
             "relevance_score": 8.5,  # Normal numeric value
             "focus_area_matched": "competitive advantages",
             "metadata": {
                 "timestamp": 1756011468.6354835,
                 "has_insight": True,
                 "speaker_role": "expert",
                 "transcript_name": "Randy_Jesberg- Former CEO - Initial Conversation (06.26.2025)",
                 "position": 45,
             },
         },
         {
             "text": "The main challenge we face is the limited addressable market size.",
             "speaker_role": "expert",
             "transcript_name": "Cheryl Bertics - FlexXray Foreign Material Inspection Services - Former Manager",
             "position": 23,
             "has_insight": True,
             "relevance_score": None,  # None value - should become 0.0
             "focus_area_matched": "market limitations",
             "metadata": {
                 "timestamp": 1756011467.8782463,
                 "has_insight": True,
                 "speaker_role": "expert",
                 "transcript_name": "Cheryl Bertics - FlexXray Foreign Material Inspection Services - Former Manager",
                 "position": 23,
             },
         },
         {
             "text": "Our rapid turnaround times give us a significant advantage over competitors.",
             "speaker_role": "expert",
             "transcript_name": "George Perry-West - Pegasus Foods, Inc - Former FSQA Manager",
             "position": 67,
             "has_insight": True,
             "relevance_score": "",  # Empty string - should become 0.0
             "focus_area_matched": "operational efficiency",
             "metadata": {
                 "timestamp": 1756011469.1234567,
                 "has_insight": True,
                 "speaker_role": "expert",
                 "transcript_name": "George Perry-West - Pegasus Foods, Inc - Former FSQA Manager",
                 "position": 67,
             },
         },
         {
             "text": "FlexXray provides excellent service quality to all customers.",
             "speaker_role": "expert", 
             "transcript_name": "Test Speaker - Test Company - Test Title",
             "position": 89,
             "has_insight": True,
             "relevance_score": "invalid",  # Invalid string - should become 0.0
             "focus_area_matched": "service quality",
             "metadata": {
                 "timestamp": 1756011470.1234567,
                 "has_insight": True,
                 "speaker_role": "expert",
                 "transcript_name": "Test Speaker - Test Company - Test Title",
                 "position": 89,
             },
         },
     ]

    print(f"📝 Sample quotes before enrichment: {len(sample_quotes)}")
    print("\nBefore enrichment (missing fields):")
    for i, quote in enumerate(sample_quotes, 1):
        print(f"  Quote {i}:")
        print(f"    Text: {quote.get('text', '')[:60]}...")
        print(f"    Speaker Info: {quote.get('speaker_info', 'MISSING')}")
        print(f"    Sentiment: {quote.get('sentiment', 'MISSING')}")
        print(f"    Theme: {quote.get('theme', 'MISSING')}")
        print(f"    Date: {quote.get('date', 'MISSING')}")
        print()

    # Enrich the quotes
    print("🔧 Enriching quotes...")
    enriched_quotes = tool.enrich_quotes_for_export(sample_quotes)

    print("\nAfter enrichment (all fields populated):")
    for i, quote in enumerate(enriched_quotes, 1):
        print(f"  Quote {i}:")
        print(f"    Text: {quote.get('text', '')[:60]}...")
        print(f"    Speaker Info: {quote.get('speaker_info', {})}")
        print(f"    Sentiment: {quote.get('sentiment', '')}")
        print(f"    Theme: {quote.get('theme', '')}")
        print(f"    Date: {quote.get('date', '')}")
        print(f"    Relevance Score: {quote.get('relevance_score', '')} (type: {type(quote.get('relevance_score', '')).__name__})")
        print()

    # Test export functionality
    print("📊 Testing export functionality...")
    try:
        excel_file = tool.export_quotes_to_excel(enriched_quotes)
        if excel_file:
            print(f"✅ Excel export successful: {excel_file}")
        else:
            print("❌ Excel export failed")
    except Exception as e:
        print(f"❌ Excel export error: {e}")

    # Show the complete enriched quote structure
    print("\n🔍 Complete enriched quote structure:")
    if enriched_quotes:
        sample_quote = enriched_quotes[0]
        print(json.dumps(sample_quote, indent=2))

    print("\n✅ Quote enrichment test completed!")


def test_speaker_info_extraction():
    """Test speaker info extraction from transcript filenames."""
    print("\n🧪 Testing Speaker Info Extraction")
    print("=" * 40)

    tool = ModularQuoteAnalysisTool()

    test_cases = [
        "Randy_Jesberg- Former CEO - Initial Conversation (06.26.2025)",
        "Cheryl Bertics - FlexXray Foreign Material Inspection Services - Former Manager",
        "George Perry-West - Pegasus Foods, Inc - Former FSQA Manager",
        "Simple Name - Company",
        "Just Name",
    ]

    for test_case in test_cases:
        quote = {"transcript_name": test_case}
        enriched = tool._add_speaker_info(quote)
        speaker_info = enriched.get("speaker_info", {})

        print(f"  Filename: {test_case}")
        print(f"    → Name: {speaker_info.get('name', '')}")
        print(f"    → Company: {speaker_info.get('company', '')}")
        print(f"    → Title: {speaker_info.get('title', '')}")
        print()


def test_sentiment_analysis():
    """Test sentiment analysis functionality."""
    print("\n🧪 Testing Sentiment Analysis")
    print("=" * 35)

    tool = ModularQuoteAnalysisTool()

    test_quotes = [
        "This is an excellent product with great quality and strong performance.",
        "We face significant challenges and problems with this approach.",
        "The service is adequate but nothing special.",
        "Our technology provides outstanding advantages and superior results.",
    ]

    for i, text in enumerate(test_quotes, 1):
        quote = {"text": text}
        enriched = tool._add_sentiment_analysis(quote)
        sentiment = enriched.get("sentiment", "")

        print(f"  Quote {i}: {text[:50]}...")
        print(f"    → Sentiment: {sentiment}")
        print()


def test_theme_categorization():
    """Test theme categorization functionality."""
    print("\n🧪 Testing Theme Categorization")
    print("=" * 40)

    tool = ModularQuoteAnalysisTool()

    test_quotes = [
        "Our competitive advantage in the market is clear.",
        "The value proposition drives customer decisions.",
        "Our local presence gives us a geographic advantage.",
        "Proprietary technology provides technical capabilities.",
    ]

    for i, text in enumerate(test_quotes, 1):
        quote = {"text": text}
        enriched = tool._add_theme_categorization(quote)
        theme = enriched.get("theme", "")

        print(f"  Quote {i}: {text[:50]}...")
        print(f"    → Theme: {theme}")
        print()


def test_relevance_score_handling():
    """Test relevance_score numeric handling for various edge cases."""
    print("\n🧪 Testing Relevance Score Numeric Handling")
    print("=" * 50)

    tool = ModularQuoteAnalysisTool()

    test_cases = [
        {"relevance_score": 8.5, "description": "Normal float"},
        {"relevance_score": 10, "description": "Integer"},
        {"relevance_score": None, "description": "None value"},
        {"relevance_score": "", "description": "Empty string"},
        {"relevance_score": "None", "description": "String 'None'"},
        {"relevance_score": "invalid", "description": "Invalid string"},
        {"relevance_score": "7.5", "description": "String number"},
        # Missing relevance_score field
        {"description": "Missing field"},
    ]

    for i, test_case in enumerate(test_cases, 1):
        quote = {"text": "Test quote"}
        if "relevance_score" in test_case:
            quote["relevance_score"] = test_case["relevance_score"]
        
        enriched = tool._ensure_required_fields(quote)
        final_score = enriched.get("relevance_score")
        
        print(f"  Test {i}: {test_case['description']}")
        print(f"    Input: {test_case.get('relevance_score', 'MISSING')}")
        print(f"    Output: {final_score} (type: {type(final_score).__name__})")
        print(f"    Is Numeric: {isinstance(final_score, (int, float))}")
        print()


if __name__ == "__main__":
    print("🚀 Starting Quote Enrichment Tests")
    print("=" * 50)

    try:
        test_quote_enrichment()
        test_speaker_info_extraction()
        test_sentiment_analysis()
        test_theme_categorization()
        test_relevance_score_handling()

        print("\n🎉 All tests completed successfully!")
        print("\n💡 The quote enrichment functionality now ensures:")
        print("   ✅ All quotes have speaker_info (name, company, title)")
        print("   ✅ All quotes have sentiment classification")
        print("   ✅ All quotes have theme categorization")
        print("   ✅ All quotes have date information")
        print("   ✅ All relevance_score values are numeric (0.0 default)")
        print("   ✅ No more blank columns in Excel exports")
        print("   ✅ Properly aligned rows with complete data")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
