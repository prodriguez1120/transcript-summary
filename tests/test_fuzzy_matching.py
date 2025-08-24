#!/usr/bin/env python3
"""
Test script for fuzzy matching capabilities in FlexXray transcript analysis.

This script demonstrates:
- Fuzzy topic matching with synonyms
- Enhanced speaker role identification
- Insight detection with confidence scoring
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

try:
    from fuzzy_matching import FuzzyMatcher
    from quote_extraction import QuoteExtractor
    from quote_topic_filter import QuoteTopicFilter
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all required packages are installed:")
    print("pip install fuzzywuzzy python-Levenshtein sentence-transformers")
    sys.exit(1)


def test_fuzzy_topic_matching():
    """Test fuzzy topic matching capabilities."""
    print("=== Testing Fuzzy Topic Matching ===\n")

    fuzzy_matcher = FuzzyMatcher()

    # Test quotes with various phrasings
    test_quotes = [
        {"text": "We are the market leader in foreign material inspection services."},
        {"text": "Our company dominates the industry with proprietary technology."},
        {"text": "We have a strong value proposition that customers appreciate."},
        {"text": "The local presence gives us a competitive advantage."},
        {"text": "Our turnaround times are incredibly fast."},
        {"text": "The market size is somewhat limited for our services."},
        {"text": "Timing can be unpredictable in this business."},
        {"text": "We offer cutting-edge tech solutions."},
        {"text": "Our regional footprint covers the entire Midwest."},
        {"text": "The ROI on our services is excellent."},
    ]

    # Test different topics
    topics = {
        "market_leadership": ["market leader", "market dominance", "industry leader"],
        "value_proposition": ["value proposition", "ROI", "competitive advantage"],
        "local_presence": [
            "local presence",
            "regional footprint",
            "geographic coverage",
        ],
        "technology_advantages": ["technology", "proprietary tech", "innovation"],
        "turnaround_times": ["turnaround", "speed", "fast service"],
        "market_limitations": ["market size", "limited market", "TAM"],
        "timing_challenges": ["timing", "unpredictable", "volatility"],
    }

    for topic, patterns in topics.items():
        print(f"Topic: {topic}")
        print(f"Patterns: {patterns}")

        for i, quote in enumerate(test_quotes):
            is_match, confidence, best_pattern = fuzzy_matcher.fuzzy_topic_match(
                quote["text"], patterns
            )

            if is_match:
                print(f"  ✓ Quote {i+1}: '{quote['text'][:50]}...'")
                print(f"    Confidence: {confidence:.1f}%, Pattern: '{best_pattern}'")
            else:
                print(f"  ✗ Quote {i+1}: '{quote['text'][:50]}...' (No match)")
        print()


def test_fuzzy_speaker_identification():
    """Test fuzzy speaker role identification."""
    print("=== Testing Fuzzy Speaker Identification ===\n")

    fuzzy_matcher = FuzzyMatcher()

    # Test sentences with various speaking patterns
    test_sentences = [
        "So, tell me about your experience with FlexXray.",
        "We have been in business for over 20 years.",
        "Can you elaborate on your technology advantages?",
        "Our customers really value our local presence.",
        "What do you think about market competition?",
        "We provide the fastest turnaround times in the industry.",
        "How do you handle unpredictable timing issues?",
        "Our proprietary technology sets us apart.",
        "That's very interesting, can you explain more?",
        "We focus on quality and customer satisfaction.",
    ]

    # Define patterns
    interviewer_patterns = [
        "tell me about",
        "can you elaborate",
        "what do you think",
        "how do you handle",
        "that's interesting",
        "explain more",
    ]

    expert_patterns = [
        "we have been",
        "our customers",
        "we provide",
        "we focus",
        "our technology",
        "our proprietary",
        "our local presence",
    ]

    for i, sentence in enumerate(test_sentences):
        speaker_role, confidence = fuzzy_matcher.fuzzy_speaker_identification(
            sentence, interviewer_patterns, expert_patterns
        )

        print(f"Sentence {i+1}: '{sentence}'")
        print(f"  Identified as: {speaker_role} (confidence: {confidence:.1f}%)")
        print()


def test_fuzzy_insight_detection():
    """Test fuzzy insight detection."""
    print("=== Testing Fuzzy Insight Detection ===\n")

    fuzzy_matcher = FuzzyMatcher()

    # Test sentences with various insight levels
    test_sentences = [
        "We have a strong competitive advantage in the market.",
        "The weather is nice today.",
        "Our technology provides significant value to customers.",
        "I like coffee in the morning.",
        "Market growth has been consistent over the past year.",
        "The sky is blue.",
        "Customer satisfaction scores are at an all-time high.",
        "We need to improve our processes.",
        "The food tastes good.",
        "Revenue increased by 25% last quarter.",
    ]

    insight_patterns = [
        "competitive advantage",
        "technology",
        "value",
        "market growth",
        "customer satisfaction",
        "improve",
        "revenue",
        "business",
    ]

    for i, sentence in enumerate(test_sentences):
        has_insight, confidence, matched_patterns = (
            fuzzy_matcher.fuzzy_insight_detection(sentence, insight_patterns)
        )

        print(f"Sentence {i+1}: '{sentence}'")
        print(f"  Has insight: {has_insight}")
        if has_insight:
            print(f"  Confidence: {confidence:.1f}%")
            print(f"  Matched patterns: {matched_patterns}")
        print()


def test_enhanced_quote_filtering():
    """Test enhanced quote filtering with fuzzy matching."""
    print("=== Testing Enhanced Quote Filtering ===\n")

    quote_filter = QuoteTopicFilter(use_fuzzy=True)

    # Test quotes
    test_quotes = [
        {
            "text": "We are the market leader in foreign material inspection services.",
            "speaker_role": "expert",
        },
        {
            "text": "Our company dominates the industry with proprietary technology.",
            "speaker_role": "expert",
        },
        {
            "text": "We have a strong value proposition that customers appreciate.",
            "speaker_role": "expert",
        },
        {
            "text": "The local presence gives us a competitive advantage.",
            "speaker_role": "expert",
        },
        {"text": "Our turnaround times are incredibly fast.", "speaker_role": "expert"},
        {
            "text": "The market size is somewhat limited for our services.",
            "speaker_role": "expert",
        },
        {
            "text": "Timing can be unpredictable in this business.",
            "speaker_role": "expert",
        },
    ]

    # Test filtering by different topics
    topics = [
        "market_leadership",
        "value_proposition",
        "local_presence",
        "technology_advantages",
    ]

    for topic in topics:
        print(f"Filtering quotes for topic: {topic}")
        filtered_quotes = quote_filter.filter_quotes_by_topic(test_quotes, topic)

        print(f"  Found {len(filtered_quotes)} relevant quotes:")
        for quote in filtered_quotes:
            print(f"    - '{quote['text'][:60]}...'")
            if "fuzzy_match" in quote:
                match_info = quote["fuzzy_match"]
                print(
                    f"      Confidence: {match_info['confidence']:.1f}%, Method: {match_info['matching_method']}"
                )
        print()


def main():
    """Run all fuzzy matching tests."""
    print("FlexXray Fuzzy Matching Test Suite\n")
    print("=" * 50)

    try:
        test_fuzzy_topic_matching()
        test_fuzzy_speaker_identification()
        test_fuzzy_insight_detection()
        test_enhanced_quote_filtering()

        print("=" * 50)
        print("All tests completed successfully!")
        print("\nFuzzy matching capabilities are now integrated into:")
        print("- Quote extraction with enhanced speaker identification")
        print("- Topic filtering with synonym matching")
        print("- Insight detection with confidence scoring")
        print("- Enhanced quote relevance assessment")

    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
