#!/usr/bin/env python3
"""Analyze quote coverage and ranking statistics."""

import json

# Load the latest analysis results
with open('Outputs/FlexXray_quote_analysis_20250822_103440.json', 'r') as f:
    data = json.load(f)

print("=== QUOTE COVERAGE ANALYSIS ===")
print(f"Total quotes in all_quotes: {len(data.get('all_quotes', []))}")

total_quotes_in_themes = 0
ranked_quotes = 0
selection_stages = {}

for perspective_key, perspective_data in data['perspectives'].items():
    print(f"\nPerspective: {perspective_key}")
    print(f"  Themes: {len(perspective_data.get('themes', []))}")
    
    for theme in perspective_data.get('themes', []):
        theme_quotes = theme.get('quotes', [])
        total_quotes_in_themes += len(theme_quotes)
        print(f"    Theme '{theme['name']}': {len(theme_quotes)} quotes")
        
        for quote in theme_quotes:
            stage = quote.get('selection_stage', 'unknown')
            selection_stages[stage] = selection_stages.get(stage, 0) + 1
            
            if stage == 'openai_ranked':
                ranked_quotes += 1

print(f"\n=== SUMMARY ===")
print(f"Total quotes in themes: {total_quotes_in_themes}")
print(f"Total quotes ranked: {ranked_quotes}")
print(f"Coverage: {ranked_quotes/715*100:.1f}%")

print(f"\n=== SELECTION STAGE BREAKDOWN ===")
for stage, count in selection_stages.items():
    print(f"{stage}: {count} quotes")

# Check if there are ranked_quotes at the perspective level
print(f"\n=== PERSPECTIVE LEVEL RANKED QUOTES ===")
for perspective_key, perspective_data in data['perspectives'].items():
    if 'ranked_quotes' in perspective_data:
        ranked_count = len(perspective_data['ranked_quotes'])
        print(f"{perspective_key}: {ranked_count} ranked quotes")
    else:
        print(f"{perspective_key}: No ranked_quotes field")
