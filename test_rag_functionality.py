#!/usr/bin/env python3
"""
Test RAG Functionality for FlexXray Quote Analysis

This script demonstrates the enhanced RAG (Retrieval-Augmented Generation)
functionality that uses vector database semantic search for better quote retrieval.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from quote_analysis_tool import ModularQuoteAnalysisTool


def main():
    """Test the RAG functionality."""
    print("🧪 FlexXray RAG Functionality Test")
    print("=" * 50)

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Please set OPENAI_API_KEY environment variable")
        return

    try:
        # Initialize the tool
        print("🔧 Initializing Quote Analysis Tool...")
        analyzer = ModularQuoteAnalysisTool()
        print("✅ Tool initialized successfully")

        # Get RAG statistics
        print("\n📊 RAG System Statistics:")
        rag_stats = analyzer.get_rag_statistics()

        for key, value in rag_stats.items():
            if key == "search_capabilities":
                print(f"  {key}: {', '.join(value)}")
            else:
                print(f"  {key}: {value}")

        # Test RAG functionality
        print("\n🧪 Testing RAG Functionality...")

        # Test multiple perspectives
        perspectives_to_test = ["business_model", "growth_potential", "risk_factors"]

        for perspective in perspectives_to_test:
            print(f"\n{'='*60}")
            test_result = analyzer.test_rag_functionality(perspective)

            if test_result:
                print(f"\n✅ RAG Test for '{perspective}' Completed Successfully!")
                print(f"📈 Perspective: {test_result.get('title', 'Unknown')}")
                print(f"📊 Quotes Analyzed: {test_result.get('total_quotes', 0)}")
                print(f"🎭 Themes Found: {len(test_result.get('themes', []))}")

                # Show sample themes
                themes = test_result.get("themes", [])
                if themes:
                    print(f"\n🎯 Sample Themes for {perspective}:")
                    for i, theme in enumerate(themes[:2]):
                        print(f"  {i+1}. {theme.get('theme_name', 'Unknown')}")
                        print(f"     Relevance: {theme.get('theme_relevance', 0):.2f}")
                        print(f"     Quote count: {len(theme.get('quotes', []))}")
            else:
                print(f"\n❌ RAG Test for '{perspective}' Failed")

        # Test additional RAG capabilities
        print(f"\n{'='*60}")
        print("🔍 Testing Additional RAG Capabilities...")

        # Test semantic search
        print("\n1. Testing Semantic Search...")
        try:
            search_results = analyzer.semantic_search_quotes(
                "competitive advantage", n_results=5
            )
            print(
                f"   Found {len(search_results)} quotes about 'competitive advantage'"
            )
            if search_results:
                top_result = search_results[0]
                print(f"   Top result: '{top_result.get('text', '')[:80]}...'")
                print(
                    f"   Source: {top_result.get('metadata', {}).get('transcript_name', 'Unknown')}"
                )
        except Exception as e:
            print(f"   ❌ Semantic search error: {e}")

        # Test speaker filtering
        print("\n2. Testing Speaker Role Filtering...")
        try:
            expert_quotes = analyzer.search_quotes_with_speaker_filter(
                "market expansion", speaker_role="expert", n_results=5
            )
            print(
                f"   Found {len(expert_quotes)} expert quotes about 'market expansion'"
            )
            if expert_quotes:
                print(
                    f"   All quotes from experts: {all(q.get('metadata', {}).get('speaker_role') == 'expert' for q in expert_quotes)}"
                )
        except Exception as e:
            print(f"   ❌ Speaker filtering error: {e}")

        # Test perspective-based retrieval
        print("\n3. Testing Perspective-Based Retrieval...")
        try:
            perspective_quotes = analyzer.get_quotes_by_perspective(
                "growth_potential",
                analyzer.key_perspectives["growth_potential"],
                n_results=10,
            )
            print(
                f"   Found {len(perspective_quotes)} quotes for growth potential perspective"
            )
        except Exception as e:
            print(f"   ❌ Perspective retrieval error: {e}")

    except Exception as e:
        print(f"❌ Error during RAG testing: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
