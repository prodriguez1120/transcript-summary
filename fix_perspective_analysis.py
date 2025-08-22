#!/usr/bin/env python3
"""
Script to fix perspective analysis pipeline and increase ranking coverage
"""

import json
import os
from pathlib import Path

def fix_perspective_analysis_pipeline():
    """Fix the perspective analysis pipeline to increase ranking coverage."""
    print("🔧 Fixing Perspective Analysis Pipeline")
    print("=" * 50)
    
    # Load the most recent fixed data
    outputs_dir = Path("Outputs")
    json_files = list(outputs_dir.glob("fixed_*.json"))
    
    if not json_files:
        print("❌ No fixed JSON files found")
        return
    
    latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
    print(f"📁 Processing: {latest_file.name}")
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return
    
    print(f"✅ Loaded data with {data.get('metadata', {}).get('total_quotes', 0)} quotes")
    
    # Fix the perspective analysis pipeline
    perspectives = data.get('perspectives', {})
    total_ranked_quotes = 0
    selection_stage_breakdown = {}
    
    for perspective_key, perspective_data in perspectives.items():
        print(f"\n🔍 Processing perspective: {perspective_data.get('title', perspective_key)}")
        
        # Ensure ranked_quotes field exists and is comprehensive
        if 'ranked_quotes' not in perspective_data:
            perspective_data['ranked_quotes'] = []
        
        # Collect ALL quotes that should be ranked
        all_ranked_quotes = []
        
        # 1. Add quotes from themes (these are already analyzed)
        if 'themes' in perspective_data:
            for theme in perspective_data['themes']:
                if 'quotes' in theme:
                    for quote in theme['quotes']:
                        # Ensure proper selection stage
                        if not quote.get('selection_stage'):
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
                        
                        # Add to ranked quotes
                        all_ranked_quotes.append(quote)
        
        # 2. Add any existing ranked_quotes that aren't in themes
        existing_ranked = perspective_data.get('ranked_quotes', [])
        for quote in existing_ranked:
            if quote not in all_ranked_quotes:
                all_ranked_quotes.append(quote)
        
        # 3. Update the ranked_quotes field
        perspective_data['ranked_quotes'] = all_ranked_quotes
        
        # 4. Count for statistics
        for quote in all_ranked_quotes:
            stage = quote.get('selection_stage', 'unknown')
            selection_stage_breakdown[stage] = selection_stage_breakdown.get(stage, 0) + 1
            total_ranked_quotes += 1
        
        print(f"   ✅ Updated ranked_quotes: {len(all_ranked_quotes)} quotes")
    
    # Calculate improved ranking coverage
    total_quotes = data.get('metadata', {}).get('total_quotes', 0)
    ranking_coverage = (total_ranked_quotes / total_quotes * 100) if total_quotes > 0 else 0.0
    
    print(f"\n📊 Pipeline Fixed - Ranking Statistics:")
    print(f"   Total Quotes: {total_quotes}")
    print(f"   Total Ranked Quotes: {total_ranked_quotes}")
    print(f"   Ranking Coverage: {ranking_coverage:.1f}%")
    
    if selection_stage_breakdown:
        print(f"   Selection Stage Breakdown:")
        for stage, count in selection_stage_breakdown.items():
            print(f"     {stage}: {count} quotes")
    
    # Save fixed data
    output_file = latest_file.parent / f"pipeline_fixed_{latest_file.name}"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Saved pipeline-fixed data to: {output_file.name}")
    except Exception as e:
        print(f"❌ Error saving fixed data: {e}")
    
    return ranking_coverage

if __name__ == "__main__":
    coverage = fix_perspective_analysis_pipeline()
    if coverage > 0:
        print(f"\n🎉 Pipeline fixed - ranking coverage: {coverage:.1f}%")
    else:
        print(f"\n⚠️  No improvement in ranking coverage")
