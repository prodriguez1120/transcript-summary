#!/usr/bin/env python3
"""
Test Ranking Coverage and Selection Stages

This script tests the improved ranking formulas and coverage calculation.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from quote_analysis_tool import ModularQuoteAnalysisTool

def test_ranking_coverage():
    """Test the ranking coverage and selection stage tracking."""
    print("🧪 Testing Ranking Coverage and Selection Stages")
    print("=" * 60)
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set OPENAI_API_KEY environment variable")
        return
    
    try:
        # Initialize the tool
        print("🔧 Initializing Quote Analysis Tool...")
        analyzer = ModularQuoteAnalysisTool()
        print("✅ Tool initialized successfully")
        
        # Test perspective analysis to see ranking coverage
        print("\n🧪 Testing Perspective Analysis with Ranking...")
        
        # Test with a small set of quotes to see ranking in action
        test_quotes = [
            {
                'text': 'This is a test quote about business model',
                'speaker_role': 'expert',
                'transcript_name': 'test_transcript',
                'position': 1
            }
        ]
        
        # Test each perspective
        for perspective_key, perspective_data in analyzer.key_perspectives.items():
            print(f"\n📋 Testing: {perspective_data['title']}")
            print(f"🎯 Focus Areas: {', '.join(perspective_data['focus_areas'])}")
            
            try:
                # This should use RAG and OpenAI ranking
                result = analyzer.analyze_perspective_with_quotes(
                    perspective_key, perspective_data, test_quotes
                )
                
                if result:
                    print(f"  ✅ Analysis completed")
                    print(f"  📊 Total quotes: {result.get('total_quotes', 0)}")
                    print(f"  🎭 Themes found: {len(result.get('themes', []))}")
                    
                    # Check ranking coverage
                    if 'ranked_quotes' in result:
                        ranked_quotes = result['ranked_quotes']
                        print(f"  🔍 Ranked quotes: {len(ranked_quotes)}")
                        
                        # Check selection stages
                        selection_stages = {}
                        for quote in ranked_quotes:
                            stage = quote.get('selection_stage', 'unknown')
                            selection_stages[stage] = selection_stages.get(stage, 0) + 1
                        
                        if selection_stages:
                            print(f"  📊 Selection Stage Breakdown:")
                            for stage, count in selection_stages.items():
                                print(f"    {stage}: {count} quotes")
                        
                        # Check ranking scores
                        if ranked_quotes:
                            top_quote = ranked_quotes[0]
                            print(f"  🏆 Top quote ranking:")
                            print(f"    OpenAI Rank: {top_quote.get('openai_rank', 'N/A')}")
                            print(f"    Selection Stage: {top_quote.get('selection_stage', 'N/A')}")
                            print(f"    Relevance Explanation: {top_quote.get('relevance_explanation', 'N/A')[:50]}...")
                    
                    # Check themes for ranking info
                    themes = result.get('themes', [])
                    if themes:
                        print(f"  🎯 Theme Analysis:")
                        for i, theme in enumerate(themes[:2]):
                            print(f"    Theme {i+1}: {theme.get('name', 'Unknown')}")
                            theme_quotes = theme.get('quotes', [])
                            print(f"      Quotes: {len(theme_quotes)}")
                            
                            # Check if theme quotes have ranking info
                            ranked_in_theme = sum(1 for q in theme_quotes if q.get('openai_rank') or q.get('selection_stage'))
                            print(f"      Ranked quotes: {ranked_in_theme}")
                            
                            if theme_quotes:
                                top_theme_quote = theme_quotes[0]
                                print(f"      Top quote rank: {top_theme_quote.get('openai_rank', 'N/A')}")
                                print(f"      Selection stage: {top_theme_quote.get('selection_stage', 'N/A')}")
                else:
                    print(f"  ❌ Analysis failed")
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        # Test ranking statistics calculation with actual results
        print(f"\n📊 Testing Ranking Statistics with Actual Results...")
        try:
            # Get actual results from one perspective to test ranking statistics
            if 'business_model' in analyzer.key_perspectives:
                print(f"  📋 Testing with actual Business Model perspective results...")
                
                # Get actual results from perspective analysis
                actual_result = analyzer.analyze_perspective_with_quotes(
                    'business_model', 
                    analyzer.key_perspectives['business_model'], 
                    test_quotes
                )
                
                if actual_result:
                    # Create results structure for ranking statistics
                    actual_results = {
                        'perspectives': {
                            'business_model': actual_result
                        },
                        'all_quotes': [{'text': 'test'} for _ in range(actual_result.get('total_quotes', 0))]
                    }
                    
                    ranking_stats = analyzer.get_quote_ranking_statistics(actual_results)
                    print(f"  📈 Actual Ranking Statistics:")
                    print(f"    Total Perspectives: {ranking_stats['total_perspectives']}")
                    print(f"    Total Quotes Ranked: {ranking_stats['total_ranked_quotes']}")
                    print(f"    Ranking Coverage: {ranking_stats['ranking_coverage']:.1f}%")
                    
                    if ranking_stats['selection_stage_breakdown']:
                        print(f"    Selection Stage Breakdown:")
                        for stage, count in ranking_stats['selection_stage_breakdown'].items():
                            print(f"      {stage}: {count} quotes")
                    
                    # Show detailed breakdown
                    if 'ranked_quotes' in actual_result:
                        ranked_quotes = actual_result['ranked_quotes']
                        print(f"  🔍 Detailed Quote Analysis:")
                        print(f"    Total quotes in perspective: {len(ranked_quotes)}")
                        
                        # Count by selection stage
                        stage_counts = {}
                        for quote in ranked_quotes:
                            stage = quote.get('selection_stage', 'unknown')
                            stage_counts[stage] = stage_counts.get(stage, 0) + 1
                        
                        for stage, count in stage_counts.items():
                            print(f"      {stage}: {count} quotes")
                        
                        # Show ranking distribution
                        ranking_distribution = {}
                        for quote in ranked_quotes:
                            rank = quote.get('openai_rank', 0)
                            ranking_distribution[rank] = ranking_distribution.get(rank, 0) + 1
                        
                        print(f"    Ranking Distribution:")
                        for rank in sorted(ranking_distribution.keys()):
                            print(f"      Rank {rank}: {ranking_distribution[rank]} quotes")
                else:
                    print(f"  ❌ Could not get actual results for ranking statistics")
                    
        except Exception as e:
            print(f"  ❌ Actual ranking statistics error: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"\n✅ Ranking Coverage Test Complete!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ranking_coverage()
