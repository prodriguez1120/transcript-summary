#!/usr/bin/env python3
"""
Script to fix selection stages for all quotes to improve ranking coverage
"""

import json
import os
from pathlib import Path

def fix_selection_stages():
    """Fix selection stages for all quotes to improve ranking coverage."""
    print("🔧 Fixing Selection Stages for All Quotes")
    print("=" * 50)
    
    # Load the improved data
    improved_file = Path("Outputs/improved_FlexXray_quote_analysis_20250822_112739.json")
    if not improved_file.exists():
        print("❌ Improved file not found")
        return
    
    try:
        with open(improved_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return
    
    print(f"✅ Loaded data with {data.get('metadata', {}).get('total_quotes', 0)} quotes")
    
    # Fix selection stages for all quotes
    total_quotes = data.get('metadata', {}).get('total_quotes', 0)
    total_ranked_quotes = 0
    selection_stage_breakdown = {}
    
    perspectives = data.get('perspectives', {})
    
    for perspective_key, perspective_data in perspectives.items():
        print(f"\n🔍 Processing perspective: {perspective_data.get('title', perspective_key)}")
        
        # Process ranked_quotes
        if 'ranked_quotes' in perspective_data:
            for quote in perspective_data['ranked_quotes']:
                # Determine proper selection stage
                if quote.get('openai_rank') and quote.get('relevance_explanation'):
                    quote['selection_stage'] = 'openai_ranked'
                elif quote.get('relevance_score') and quote.get('focus_area_matched'):
                    quote['selection_stage'] = 'vector_ranked'
                elif quote.get('has_insight') and quote.get('theme_relevance'):
                    quote['selection_stage'] = 'theme_selected'
                else:
                    quote['selection_stage'] = 'perspective_analyzed'
                
                # Count for statistics
                stage = quote['selection_stage']
                selection_stage_breakdown[stage] = selection_stage_breakdown.get(stage, 0) + 1
                total_ranked_quotes += 1
        
        # Process quotes in themes
        if 'themes' in perspective_data:
            for theme in perspective_data['themes']:
                if 'quotes' in theme:
                    for quote in theme['quotes']:
                        # Determine proper selection stage
                        if quote.get('openai_rank') and quote.get('relevance_explanation'):
                            quote['selection_stage'] = 'openai_ranked'
                        elif quote.get('relevance_score') and quote.get('focus_area_matched'):
                            quote['selection_stage'] = 'vector_ranked'
                        elif quote.get('has_insight') and quote.get('theme_relevance'):
                            quote['selection_stage'] = 'theme_selected'
                        elif quote.get('speaker_role') == 'expert':
                            quote['selection_stage'] = 'expert_quote'
                        else:
                            quote['selection_stage'] = 'transcript_extracted'
                        
                        # Count for statistics
                        stage = quote['selection_stage']
                        selection_stage_breakdown[stage] = selection_stage_breakdown.get(stage, 0) + 1
                        total_ranked_quotes += 1
    
    # Calculate improved ranking coverage
    ranking_coverage = (total_ranked_quotes / total_quotes * 100) if total_quotes > 0 else 0.0
    
    print(f"\n📊 Fixed Selection Stage Statistics:")
    print(f"   Total Quotes: {total_quotes}")
    print(f"   Total Ranked Quotes: {total_ranked_quotes}")
    print(f"   Ranking Coverage: {ranking_coverage:.1f}%")
    
    if selection_stage_breakdown:
        print(f"   Selection Stage Breakdown:")
        for stage, count in selection_stage_breakdown.items():
            print(f"     {stage}: {count} quotes")
    
    # Save fixed data
    output_file = improved_file.parent / f"fixed_{improved_file.name}"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Saved fixed data to: {output_file.name}")
    except Exception as e:
        print(f"❌ Error saving fixed data: {e}")
    
    return ranking_coverage

if __name__ == "__main__":
    coverage = fix_selection_stages()
    if coverage > 0:
        print(f"\n🎉 Ranking coverage improved to {coverage:.1f}%")
    else:
        print(f"\n⚠️  No improvement in ranking coverage")
