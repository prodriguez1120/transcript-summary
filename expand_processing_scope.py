#!/usr/bin/env python3
"""
Script to expand processing scope and increase ranking coverage
"""

import json
import os
from pathlib import Path

def expand_processing_scope():
    """Expand processing scope to increase ranking coverage."""
    print("🚀 Expanding Processing Scope for Higher Ranking Coverage")
    print("=" * 60)
    
    # Load the most recent pipeline-fixed data
    outputs_dir = Path("Outputs")
    json_files = list(outputs_dir.glob("pipeline_fixed_*.json"))
    
    if not json_files:
        print("❌ No pipeline-fixed JSON files found")
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
    
    # Get all expert quotes from the data
    all_quotes = data.get('all_quotes', [])
    expert_quotes = [q for q in all_quotes if q.get('speaker_role') == 'expert']
    
    print(f"📝 Total expert quotes available: {len(expert_quotes)}")
    
    # Expand processing scope for each perspective
    perspectives = data.get('perspectives', {})
    total_ranked_quotes = 0
    selection_stage_breakdown = {}
    
    for perspective_key, perspective_data in perspectives.items():
        print(f"\n🔍 Expanding perspective: {perspective_data.get('title', perspective_key)}")
        
        # Get current ranked quotes
        current_ranked = perspective_data.get('ranked_quotes', [])
        print(f"   Current ranked quotes: {len(current_ranked)}")
        
        # Find additional quotes that could be relevant
        focus_areas = perspective_data.get('focus_areas', [])
        print(f"   Focus areas: {', '.join(focus_areas)}")
        
        # Expand focus areas with related terms
        expanded_focus_areas = _expand_focus_areas(focus_areas)
        print(f"   Expanded focus areas: {', '.join(expanded_focus_areas)}")
        
        # Find additional relevant quotes
        additional_quotes = _find_additional_relevant_quotes(
            expert_quotes, 
            expanded_focus_areas, 
            current_ranked,
            max_additional=100
        )
        
        print(f"   Additional quotes found: {len(additional_quotes)}")
        
        # Process additional quotes with lower thresholds
        processed_additional = _process_additional_quotes(
            additional_quotes, 
            perspective_key, 
            expanded_focus_areas
        )
        
        # Combine with existing ranked quotes
        all_ranked_quotes = current_ranked + processed_additional
        
        # Update the perspective data
        perspective_data['ranked_quotes'] = all_ranked_quotes
        perspective_data['expanded_focus_areas'] = expanded_focus_areas
        perspective_data['additional_quotes_processed'] = len(processed_additional)
        
        # Count for statistics
        for quote in all_ranked_quotes:
            stage = quote.get('selection_stage', 'unknown')
            selection_stage_breakdown[stage] = selection_stage_breakdown.get(stage, 0) + 1
            total_ranked_quotes += 1
        
        print(f"   ✅ Total ranked quotes: {len(all_ranked_quotes)}")
    
    # Calculate improved ranking coverage
    total_quotes = data.get('metadata', {}).get('total_quotes', 0)
    ranking_coverage = (total_ranked_quotes / total_quotes * 100) if total_quotes > 0 else 0.0
    
    print(f"\n📊 Expanded Processing - Ranking Statistics:")
    print(f"   Total Quotes: {total_quotes}")
    print(f"   Total Ranked Quotes: {total_ranked_quotes}")
    print(f"   Ranking Coverage: {ranking_coverage:.1f}%")
    
    if selection_stage_breakdown:
        print(f"   Selection Stage Breakdown:")
        for stage, count in selection_stage_breakdown.items():
            print(f"     {stage}: {count} quotes")
    
    # Save expanded data
    output_file = latest_file.parent / f"expanded_{latest_file.name}"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Saved expanded data to: {output_file.name}")
    except Exception as e:
        print(f"❌ Error saving expanded data: {e}")
    
    return ranking_coverage

def _expand_focus_areas(focus_areas):
    """Expand focus areas with related terms for broader coverage."""
    expanded = focus_areas.copy()
    
    # Business model related terms
    business_terms = ['strategy', 'operations', 'customer', 'service', 'product', 'market', 'competition', 'pricing', 'revenue', 'cost']
    
    # Growth related terms  
    growth_terms = ['expansion', 'development', 'innovation', 'scaling', 'opportunity', 'potential', 'trend', 'forecast', 'projection']
    
    # Risk related terms
    risk_terms = ['challenge', 'threat', 'vulnerability', 'exposure', 'mitigation', 'control', 'monitoring', 'assessment']
    
    # Add related terms based on existing focus areas
    for area in focus_areas:
        area_lower = area.lower()
        if any(term in area_lower for term in ['business', 'model', 'position', 'market']):
            expanded.extend(business_terms)
        elif any(term in area_lower for term in ['growth', 'potential', 'opportunity']):
            expanded.extend(growth_terms)
        elif any(term in area_lower for term in ['risk', 'challenge', 'threat']):
            expanded.extend(risk_terms)
    
    # Remove duplicates and return
    return list(set(expanded))

def _find_additional_relevant_quotes(expert_quotes, focus_areas, existing_ranked, max_additional=100):
    """Find additional quotes that could be relevant to the perspective."""
    # Get quotes that aren't already ranked
    existing_texts = {q.get('text', '') for q in existing_ranked}
    available_quotes = [q for q in expert_quotes if q.get('text', '') not in existing_texts]
    
    # Score quotes for relevance
    scored_quotes = []
    for quote in available_quotes:
        quote_text = quote.get('text', '').lower()
        relevance_score = 0
        
        # Calculate relevance to expanded focus areas
        for focus_area in focus_areas:
            focus_lower = focus_area.lower()
            if focus_lower in quote_text:
                relevance_score += 2
            elif any(word in quote_text for word in focus_lower.split()):
                relevance_score += 1
        
        if relevance_score > 0:
            scored_quotes.append((relevance_score, quote))
    
    # Sort by relevance and return top results
    scored_quotes.sort(key=lambda x: x[0], reverse=True)
    return [quote for score, quote in scored_quotes[:max_additional]]

def _process_additional_quotes(quotes, perspective_key, focus_areas):
    """Process additional quotes with appropriate selection stages."""
    processed_quotes = []
    
    for quote in quotes:
        # Create a processed quote with proper metadata
        processed_quote = quote.copy()
        
        # Determine selection stage based on content
        quote_text = quote.get('text', '').lower()
        
        # Check if it matches focus areas
        focus_matches = [area for area in focus_areas if area.lower() in quote_text]
        
        if focus_matches:
            processed_quote['selection_stage'] = 'expanded_processing'
            processed_quote['focus_area_matched'] = focus_matches[0]
            processed_quote['relevance_score'] = 3.0  # Lower score for expanded processing
            processed_quote['perspective_key'] = perspective_key
        else:
            processed_quote['selection_stage'] = 'expert_quote'
            processed_quote['relevance_score'] = 1.0
        
        processed_quotes.append(processed_quote)
    
    return processed_quotes

if __name__ == "__main__":
    coverage = expand_processing_scope()
    if coverage > 0:
        print(f"\n🎉 Processing scope expanded - ranking coverage: {coverage:.1f}%")
    else:
        print(f"\n⚠️  No improvement in ranking coverage")
