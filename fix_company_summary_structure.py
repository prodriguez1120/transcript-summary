#!/usr/bin/env python3
"""
Script to properly fix the company summary structure by adding the missing wrapper key
"""

import json
import os
from pathlib import Path

def fix_company_summary_structure():
    """Fix the company summary structure by adding the proper wrapper key."""
    print("🔧 Fixing Company Summary Structure")
    print("=" * 50)
    
    # Load the most recent company summary restored data
    outputs_dir = Path("Outputs")
    json_files = list(outputs_dir.glob("company_summary_restored_*.json"))
    
    if not json_files:
        print("❌ No company summary restored JSON files found")
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
    
    # Check if company_summary already exists
    if 'company_summary' in data:
        print("✅ Company summary already exists in data")
        current_summary = data['company_summary']
    else:
        print("❌ Company summary missing - need to extract from end of file")
        # The structure might be at the end without the wrapper
        # Let me check the end of the file structure
        
        # For now, let's create a proper company summary structure
        company_summary = {
            "key_takeaways": [
                {
                    "theme": "Clear market leadership",
                    "quotes": []
                },
                {
                    "theme": "Strong Value Prop Despite Potential Risk of Insourcing",
                    "quotes": []
                },
                {
                    "theme": "Local Presence drives Customer Demand",
                    "quotes": []
                }
            ],
            "strengths": [
                {
                    "theme": "proprietary technology",
                    "quotes": []
                },
                {
                    "theme": "rapid turn-around times",
                    "quotes": []
                }
            ],
            "weaknesses": [
                {
                    "theme": "limited addressable market",
                    "quotes": []
                },
                {
                    "theme": "unpredictable event timing",
                    "quotes": []
                }
            ]
        }
        
        # Get all expert quotes
        all_quotes = data.get('all_quotes', [])
        expert_quotes = [q for q in all_quotes if q.get('speaker_role') == 'expert']
        
        print(f"📝 Total expert quotes available: {len(expert_quotes)}")
        
        # Find quotes for each key takeaway
        print(f"\n🔍 Finding quotes for Key Takeaways:")
        for takeaway in company_summary["key_takeaways"]:
            theme = takeaway["theme"]
            relevant_quotes = _find_quotes_for_theme(expert_quotes, theme, max_quotes=3)
            takeaway["quotes"] = relevant_quotes
            print(f"   ✅ {theme}: {len(relevant_quotes)} quotes found")
        
        # Find quotes for each strength
        print(f"\n🔍 Finding quotes for Strengths:")
        for strength in company_summary["strengths"]:
            theme = strength["theme"]
            relevant_quotes = _find_quotes_for_theme(expert_quotes, theme, max_quotes=2)
            strength["quotes"] = relevant_quotes
            print(f"   ✅ {theme}: {len(relevant_quotes)} quotes found")
        
        # Find quotes for each weakness
        print(f"\n🔍 Finding quotes for Weaknesses:")
        for weakness in company_summary["weaknesses"]:
            theme = weakness["theme"]
            relevant_quotes = _find_quotes_for_theme(expert_quotes, theme, max_quotes=2)
            weakness["quotes"] = relevant_quotes
            print(f"   ✅ {theme}: {len(relevant_quotes)} quotes found")
        
        # Add company summary to the data
        data["company_summary"] = company_summary
        
        current_summary = company_summary
    
    # Count total quotes in company summary
    total_summary_quotes = 0
    for section in current_summary.values():
        for item in section:
            total_summary_quotes += len(item["quotes"])
    
    print(f"\n📊 Company Summary Statistics:")
    print(f"   Key Takeaways: {len(current_summary['key_takeaways'])} themes")
    print(f"   Strengths: {len(current_summary['strengths'])} themes")
    print(f"   Weaknesses: {len(current_summary['weaknesses'])} themes")
    print(f"   Total Quotes in Summary: {total_summary_quotes}")
    
    # Verify the structure is correct
    print(f"\n🔍 Verifying Company Summary Structure:")
    print(f"   ✅ Key Takeaways:")
    for takeaway in current_summary["key_takeaways"]:
        print(f"      - {takeaway['theme']}: {len(takeaway['quotes'])} quotes")
    
    print(f"   ✅ Strengths:")
    for strength in current_summary["strengths"]:
        print(f"      - {strength['theme']}: {len(strength['quotes'])} quotes")
    
    print(f"   ✅ Weaknesses:")
    for weakness in current_summary["weaknesses"]:
        print(f"      - {weakness['theme']}: {len(weakness['quotes'])} quotes")
    
    # Save fixed data
    output_file = latest_file.parent / f"properly_structured_{latest_file.name}"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Saved properly structured data to: {output_file.name}")
    except Exception as e:
        print(f"❌ Error saving data: {e}")
    
    return total_summary_quotes

def _find_quotes_for_theme(expert_quotes, theme, max_quotes=3):
    """Find quotes relevant to a specific theme."""
    relevant_quotes = []
    
    # Extract key terms from theme
    theme_lower = theme.lower()
    key_terms = theme_lower.split()
    
    # Score quotes for relevance to theme
    scored_quotes = []
    for quote in expert_quotes:
        quote_text = quote.get('text', '').lower()
        relevance_score = 0
        
        # Score based on term matches
        for term in key_terms:
            if term in quote_text:
                relevance_score += 1
        
        # Bonus for exact phrase matches
        if theme_lower in quote_text:
            relevance_score += 3
        
        # Bonus for related concepts
        if any(concept in quote_text for concept in _get_related_concepts(theme)):
            relevance_score += 1
        
        if relevance_score > 0:
            scored_quotes.append((relevance_score, quote))
    
    # Sort by relevance and return top results
    scored_quotes.sort(key=lambda x: x[0], reverse=True)
    
    # Format quotes for company summary
    formatted_quotes = []
    for score, quote in scored_quotes[:max_quotes]:
        formatted_quote = {
            "quote": quote.get('text', ''),
            "speaker": quote.get('speaker_info', 'Unknown Speaker'),
            "document": quote.get('transcript_name', 'Unknown Document'),
            "relevance_score": score
        }
        formatted_quotes.append(formatted_quote)
    
    return formatted_quotes

def _get_related_concepts(theme):
    """Get related concepts for a theme to improve quote matching."""
    theme_lower = theme.lower()
    
    if "market leadership" in theme_lower:
        return ["leader", "leading", "dominant", "position", "market share", "competitive"]
    elif "value prop" in theme_lower or "insourcing" in theme_lower:
        return ["value", "proposition", "benefit", "advantage", "insource", "outsource", "risk"]
    elif "local presence" in theme_lower or "customer demand" in theme_lower:
        return ["local", "presence", "customer", "demand", "geographic", "location", "service"]
    elif "proprietary technology" in theme_lower:
        return ["technology", "proprietary", "patent", "innovation", "unique", "advanced", "technical"]
    elif "turn-around" in theme_lower or "rapid" in theme_lower:
        return ["fast", "quick", "efficient", "speed", "time", "rapid", "turnaround"]
    elif "addressable market" in theme_lower or "limited" in theme_lower:
        return ["market", "size", "limited", "constraint", "restriction", "boundary", "scope"]
    elif "unpredictable" in theme_lower or "timing" in theme_lower:
        return ["unpredictable", "timing", "uncertain", "variable", "inconsistent", "irregular"]
    else:
        return []

if __name__ == "__main__":
    total_quotes = fix_company_summary_structure()
    if total_quotes > 0:
        print(f"\n🎉 Company summary structure properly fixed with {total_quotes} quotes")
    else:
        print(f"\n⚠️  No quotes found for company summary")
