#!/usr/bin/env python3
"""
Test script to demonstrate the new speaker role identification and filtering functionality
in the FlexXray Quote Analysis Tool.
"""

from quote_analysis_tool import QuoteAnalysisTool
import os

def test_speaker_role_identification():
    """Test the speaker role identification functionality."""
    print("Testing Speaker Role Identification")
    print("=" * 50)
    
    # Initialize the tool
    try:
        analyzer = QuoteAnalysisTool()
        print("✓ Quote analysis tool initialized successfully")
    except Exception as e:
        print(f"✗ Error initializing tool: {e}")
        return
    
    # Test sentences with different speaker roles
    test_sentences = [
        # Interviewer sentences (should be identified as "interviewer")
        "Interviewer: Can you tell me about your experience with FlexXray?",
        "Q: What do you think about their pricing model?",
        "I: How does their technology compare to competitors?",
        "So, what's your overall assessment of the company?",
        "Can you describe the inspection process?",
        "What about their customer service?",
        "Let me ask you about their market position.",
        "That's interesting. Tell me more about that.",
        "Thank you for your time today.",
        
        # Expert sentences (should be identified as "expert")
        "I think FlexXray has a strong value proposition in the market.",
        "Our company has been using their services for three years now.",
        "We've seen significant cost savings with their approach.",
        "The technology they use is quite advanced for this industry.",
        "Customers really appreciate their portal interface.",
        "We started working with them when we needed better inspection capabilities.",
        "Their equipment is custom-configured for different materials.",
        "The service quality has been consistently high.",
        "We've grown our business alongside their expansion.",
        "Their pricing model works well for mid-market companies.",
        
        # Mixed or unclear sentences
        "The market is evolving rapidly.",
        "Technology continues to advance.",
        "Customer needs are changing.",
        "Competition is increasing in this space."
    ]
    
    print("\nTesting Speaker Role Identification:")
    print("-" * 40)
    
    interviewer_count = 0
    expert_count = 0
    
    for i, sentence in enumerate(test_sentences, 1):
        role = analyzer._identify_speaker_role(sentence)
        if role == "interviewer":
            interviewer_count += 1
            marker = "👤"
        else:
            expert_count += 1
            marker = "💼"
        
        print(f"{i:2d}. {marker} {role:12} | {sentence[:60]}{'...' if len(sentence) > 60 else ''}")
    
    print(f"\nResults:")
    print(f"  Interviewer sentences: {interviewer_count}")
    print(f"  Expert sentences: {expert_count}")
    print(f"  Total sentences: {len(test_sentences)}")

def test_speaker_role_filtering():
    """Test the speaker role filtering functionality."""
    print("\n\nTesting Speaker Role Filtering & Context Preservation")
    print("=" * 60)
    
    # Initialize the tool
    try:
        analyzer = QuoteAnalysisTool()
        print("✓ Quote analysis tool initialized successfully")
    except Exception as e:
        print(f"✗ Error initializing tool: {e}")
        return
    
    # Create sample quotes with different speaker roles and context
    sample_quotes = [
        {
            "id": "test_1",
            "quote": "I think FlexXray has a strong value proposition in the market.",
            "transcript_name": "Test Transcript",
            "speaker_role": "expert",
            "interviewer_context": [
                {"sentence": "What's your overall assessment of FlexXray's market position?", "is_question": True}
            ],
            "has_context": True,
            "context_count": 1
        },
        {
            "id": "test_2", 
            "quote": "Can you tell me about your experience with FlexXray?",
            "transcript_name": "Test Transcript",
            "speaker_role": "interviewer"
        },
        {
            "id": "test_3",
            "quote": "Our company has been using their services for three years now.",
            "transcript_name": "Test Transcript", 
            "speaker_role": "expert",
            "interviewer_context": [
                {"sentence": "How long have you been working with them?", "is_question": True}
            ],
            "has_context": True,
            "context_count": 1
        },
        {
            "id": "test_4",
            "quote": "What do you think about their pricing model?",
            "transcript_name": "Test Transcript",
            "speaker_role": "interviewer"
        },
        {
            "id": "test_5",
            "quote": "We've seen significant cost savings with their approach.",
            "transcript_name": "Test Transcript",
            "speaker_role": "expert",
            "interviewer_context": [
                {"sentence": "What about their pricing model?", "is_question": True},
                {"sentence": "Have you seen any financial benefits?", "is_question": True}
            ],
            "has_context": True,
            "context_count": 2
        }
    ]
    
    print("\nSample Quotes:")
    print("-" * 20)
    for i, quote in enumerate(sample_quotes, 1):
        role = quote.get('speaker_role', 'unknown')
        marker = "👤" if role == "interviewer" else "💼"
        context_info = f" [+{quote.get('context_count', 0)} context]" if quote.get('has_context') else ""
        print(f"{i}. {marker} {role:12} | {quote['quote'][:50]}{'...' if len(quote['quote']) > 50 else ''}{context_info}")
    
    # Test filtering methods
    print("\nFiltering Results:")
    print("-" * 20)
    
    # Filter for expert quotes only
    expert_quotes = analyzer.get_expert_quotes_only(sample_quotes)
    print(f"Expert quotes only: {len(expert_quotes)} quotes")
    for quote in expert_quotes:
        context_info = f" [+{quote.get('context_count', 0)} context]" if quote.get('has_context') else ""
        print(f"  • {quote['quote'][:40]}{'...' if len(quote['quote']) > 40 else ''}{context_info}")
    
    # Filter for quotes with context
    quotes_with_context = analyzer.get_quotes_with_context(sample_quotes)
    print(f"\nQuotes with context: {len(quotes_with_context)} quotes")
    for quote in quotes_with_context:
        print(f"  • {quote['quote'][:40]}{'...' if len(quote['quote']) > 40 else ''} [+{quote.get('context_count', 0)}]")
    
    # Test context formatting
    print(f"\nContext Formatting Examples:")
    print("-" * 30)
    for quote in quotes_with_context[:2]:  # Show first 2 examples
        formatted = analyzer.format_quote_with_context(quote)
        print(f"Quote ID: {quote['id']}")
        print(formatted)
        print()
    
    # Get statistics
    stats = analyzer.get_speaker_role_statistics(sample_quotes)
    print(f"Speaker Role & Context Statistics:")
    print(f"  Total quotes: {stats['total_quotes']}")
    print(f"  Expert quotes: {stats['expert_quotes']} ({stats['expert_percentage']:.1f}%)")
    print(f"  Interviewer quotes: {stats['interviewer_quotes']} ({stats['interviewer_percentage']:.1f}%)")
    print(f"  Quotes with context: {stats['quotes_with_context']} ({stats['context_percentage']:.1f}%)")
    print(f"  Average context per quote: {stats['average_context_per_quote']:.1f} sentences")

def main():
    """Main test function."""
    print("FlexXray Quote Analysis Tool - Speaker Role Testing")
    print("=" * 60)
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  OPENAI_API_KEY not set. Some functionality may be limited.")
        print("   Set the environment variable to test full functionality.\n")
    
    # Run tests
    test_speaker_role_identification()
    test_speaker_role_filtering()
    
    print("\n" + "=" * 60)
    print("Testing Complete!")
    print("\nKey Features Added:")
    print("• Speaker role identification (expert vs interviewer)")
    print("• Automatic filtering of interviewer quotes")
    print("• Context preservation - interviewer questions linked to expert responses")
    print("• Speaker role metadata in ChromaDB storage")
    print("• Filtering methods for different speaker roles")
    print("• Context formatting and display methods")
    print("• Enhanced statistics including context information")
    print("• Flexible quote retrieval with context options")

if __name__ == "__main__":
    main()
