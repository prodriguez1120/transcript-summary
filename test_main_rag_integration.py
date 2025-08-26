#!/usr/bin/env python3
"""
Test Main Tool RAG Integration

This script tests that the RAG functionality is properly integrated
into the main quote analysis tool flow.
"""

import os
import sys
from dotenv import load_dotenv
from settings import get_openai_api_key

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from quote_analysis_tool import ModularQuoteAnalysisTool


def test_main_tool_rag():
    """Test that RAG is working in the main tool flow."""
    print("🧪 Testing Main Tool RAG Integration")
    print("=" * 50)

    # Check for API key
    try:
        api_key = get_openai_api_key()
        if not api_key:
            print("❌ OpenAI API key not found")
            return
    except ValueError as e:
        print(f"❌ {e}")
        return

    try:
        # Initialize the tool
        print("🔧 Initializing Quote Analysis Tool...")
        analyzer = ModularQuoteAnalysisTool()
        print("✅ Tool initialized successfully")

        # Check RAG integration
        print("\n🔍 Checking RAG Integration...")
        rag_enabled = (
            hasattr(analyzer.perspective_analyzer, "vector_db_manager")
            and analyzer.perspective_analyzer.vector_db_manager is not None
        )
        print(f"  RAG Integration: {'✅ Enabled' if rag_enabled else '❌ Disabled'}")

        if rag_enabled:
            print(
                f"  Vector DB Manager: {type(analyzer.perspective_analyzer.vector_db_manager).__name__}"
            )
            print(
                f"  Quotes Collection: {'✅ Available' if analyzer.perspective_analyzer.vector_db_manager.quotes_collection else '❌ Not Available'}"
            )

        # Test perspective analysis with RAG
        print("\n🧪 Testing Perspective Analysis with RAG...")

        # Test with a small set of quotes to see RAG in action
        test_quotes = [
            {
                "text": "This is a test quote about business model",
                "speaker_role": "expert",
                "transcript_name": "test_transcript",
                "position": 1,
            }
        ]

        # Test the perspective analysis method
        for perspective_key, perspective_data in analyzer.key_perspectives.items():
            print(f"\n📋 Testing: {perspective_data['title']}")
            print(f"🎯 Focus Areas: {', '.join(perspective_data['focus_areas'])}")

            try:
                # This should now use RAG if vector database has quotes
                result = analyzer.analyze_perspective_with_quotes(
                    perspective_key, perspective_data, test_quotes
                )

                if result:
                    print(f"  ✅ Analysis completed")
                    print(f"  📊 Quotes analyzed: {result.get('total_quotes', 0)}")
                    print(f"  🎭 Themes found: {len(result.get('themes', []))}")

                    # Check if RAG was used
                    if result.get("total_quotes", 0) > len(test_quotes):
                        print(
                            f"  🔍 RAG detected: Retrieved {result.get('total_quotes', 0)} quotes from vector DB"
                        )
                    else:
                        print(
                            f"  📝 Local processing: Used {len(test_quotes)} provided quotes"
                        )
                else:
                    print(f"  ❌ Analysis failed")

            except Exception as e:
                print(f"  ❌ Error: {e}")

        # Test vector database search directly
        print(f"\n🔍 Testing Vector Database Search...")
        try:
            if analyzer.vector_db_manager.quotes_collection:
                # Test semantic search
                search_results = analyzer.vector_db_manager.semantic_search_quotes(
                    "business model", n_results=3
                )
                print(f"  Semantic search: Found {len(search_results)} quotes")

                # Test speaker filtering
                expert_quotes = (
                    analyzer.vector_db_manager.search_quotes_with_speaker_filter(
                        "market", speaker_role="expert", n_results=3
                    )
                )
                print(f"  Speaker filtering: Found {len(expert_quotes)} expert quotes")

            else:
                print("  ❌ Vector database collection not available")

        except Exception as e:
            print(f"  ❌ Vector search error: {e}")

        print(f"\n✅ Main Tool RAG Integration Test Complete!")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_main_tool_rag()
