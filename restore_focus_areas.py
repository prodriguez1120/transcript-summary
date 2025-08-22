#!/usr/bin/env python3
"""
Script to restore missing focus areas and expand processing scope
"""

import json
import os
from pathlib import Path

def restore_focus_areas_and_expand():
    """Restore missing focus areas and expand processing scope."""
    print("🔧 Restoring Focus Areas and Expanding Processing Scope")
    print("=" * 60)
    
    # Load the most recent expanded data
    outputs_dir = Path("Outputs")
    json_files = list(outputs_dir.glob("expanded_*.json"))
    
    if not json_files:
        print("❌ No expanded JSON files found")
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
    
    # Define the correct focus areas for each perspective
    focus_areas_map = {
        "business_model": {
            "title": "Business Model & Market Position",
            "description": "How FlexXray operates, serves customers, and competes in the market",
            "focus_areas": ["value proposition", "customer relationships", "market positioning", "competitive advantages", "business strategy", "operations", "pricing", "revenue model"]
        },
        "growth_potential": {
            "title": "Growth Potential & Market Opportunity", 
            "description": "FlexXray's expansion opportunities, market trends, and future prospects",
            "focus_areas": ["market expansion", "product development", "industry trends", "growth drivers", "scaling", "innovation", "opportunities", "forecast"]
        },
        "risk_factors": {
            "title": "Risk Factors & Challenges",
            "description": "Key risks, challenges, and areas of concern for FlexXray's business",
            "focus_areas": ["service quality issues", "operational challenges", "competitive threats", "market risks", "vulnerabilities", "mitigation", "controls", "monitoring"]
        }
    }
    
    # Get all expert quotes from the data
    all_quotes = data.get('all_quotes', [])
    expert_quotes = [q for q in all_quotes if q.get('speaker_role') == 'expert']
    
    print(f"📝 Total expert quotes available: {len(expert_quotes)}")
    
    # Restore focus areas and expand processing scope
    perspectives = data.get('perspectives', {})
    total_ranked_quotes = 0
    selection_stage_breakdown = {}
    
    for perspective_key, perspective_data in perspectives.items():
        print(f"\n🔍 Processing perspective: {perspective_data.get('title', perspective_key)}")
        
        # Restore focus areas
        if perspective_key in focus_areas_map:
            perspective_data['focus_areas'] = focus_areas_map[perspective_key]['focus_areas']
            print(f"   ✅ Restored focus areas: {', '.join(perspective_data['focus_areas'])}")
        else:
            print(f"   ⚠️  No focus areas defined for {perspective_key}")
            continue
        
        # Get current ranked quotes
        current_ranked = perspective_data.get('ranked_quotes', [])
        print(f"   Current ranked quotes: {len(current_ranked)}")
        
        # Expand focus areas with related terms
        expanded_focus_areas = _expand_focus_areas(perspective_data['focus_areas'])
        print(f"   Expanded focus areas: {', '.join(expanded_focus_areas)}")
        
        # Find additional relevant quotes
        additional_quotes = _find_additional_relevant_quotes(
            expert_quotes, 
            expanded_focus_areas, 
            current_ranked,
            max_additional=150  # Increased from 100
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
    
    print(f"\n📊 Restored and Expanded - Ranking Statistics:")
    print(f"   Total Quotes: {total_quotes}")
    print(f"   Total Ranked Quotes: {total_ranked_quotes}")
    print(f"   Ranking Coverage: {ranking_coverage:.1f}%")
    
    if selection_stage_breakdown:
        print(f"   Selection Stage Breakdown:")
        for stage, count in selection_stage_breakdown.items():
            print(f"     {stage}: {count} quotes")
    
    # Save restored and expanded data
    output_file = latest_file.parent / f"restored_expanded_{latest_file.name}"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Saved restored and expanded data to: {output_file.name}")
    except Exception as e:
        print(f"❌ Error saving data: {e}")
    
    return ranking_coverage

def _expand_focus_areas(focus_areas):
    """Expand focus areas with related terms for broader coverage."""
    expanded = focus_areas.copy()
    
    # Business model related terms
    business_terms = ['strategy', 'operations', 'customer', 'service', 'product', 'market', 'competition', 'pricing', 'revenue', 'cost', 'profit', 'efficiency', 'quality', 'delivery']
    
    # Growth related terms  
    growth_terms = ['expansion', 'development', 'innovation', 'scaling', 'opportunity', 'potential', 'trend', 'forecast', 'projection', 'growth', 'increase', 'improvement', 'advancement']
    
    # Risk related terms
    risk_terms = ['challenge', 'threat', 'vulnerability', 'exposure', 'mitigation', 'control', 'monitoring', 'assessment', 'risk', 'problem', 'issue', 'concern', 'danger']
    
    # Add related terms based on existing focus areas
    for area in focus_areas:
        area_lower = area.lower()
        if any(term in area_lower for term in ['business', 'model', 'position', 'market', 'customer', 'competitive']):
            expanded.extend(business_terms)
        elif any(term in area_lower for term in ['growth', 'potential', 'opportunity', 'expansion', 'development']):
            expanded.extend(growth_terms)
        elif any(term in area_lower for term in ['risk', 'challenge', 'threat', 'issue', 'problem']):
            expanded.extend(risk_terms)
    
    # Remove duplicates and return
    return list(set(expanded))

def _find_additional_relevant_quotes(expert_quotes, focus_areas, existing_ranked, max_additional=150):
    """Find additional quotes that could be relevant to the perspective."""
    # Get quotes that aren't already ranked
    existing_texts = {q.get('text', '') for q in existing_ranked}
    available_quotes = [q for q in expert_quotes if q.get('text', '') not in existing_texts]
    
    print(f"     Available quotes for processing: {len(available_quotes)}")
    
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
    
    print(f"     Quotes with relevance scores > 0: {len(scored_quotes)}")
    
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
    coverage = restore_focus_areas_and_expand()
    if coverage > 0:
        print(f"\n🎉 Focus areas restored and processing expanded - ranking coverage: {coverage:.1f}%")
    else:
        print(f"\n⚠️  No improvement in ranking coverage")
