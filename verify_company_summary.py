#!/usr/bin/env python3
"""
Script to verify the company summary structure
"""

import json
from pathlib import Path

def verify_company_summary():
    """Verify the company summary structure in the data."""
    print("🔍 Verifying Company Summary Structure")
    print("=" * 50)
    
    # Load the final company summary data
    outputs_dir = Path("Outputs")
    json_files = list(outputs_dir.glob("FINAL_COMPANY_SUMMARY_*.json"))
    
    if not json_files:
        print("❌ No FINAL_COMPANY_SUMMARY JSON files found")
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
    
    # Check what keys exist in the data
    print(f"\n📋 Data Structure Keys:")
    for key in data.keys():
        print(f"   - {key}")
    
    # Check if company_summary exists
    if 'company_summary' in data:
        print(f"\n✅ Company summary found!")
        company_summary = data['company_summary']
        
        # Verify the structure
        print(f"\n🔍 Company Summary Structure:")
        for section_name, section_data in company_summary.items():
            print(f"   📁 {section_name}:")
            if isinstance(section_data, list):
                for item in section_data:
                    if isinstance(item, dict) and 'theme' in item:
                        theme = item['theme']
                        quotes_count = len(item.get('quotes', []))
                        print(f"      - {theme}: {quotes_count} quotes")
            else:
                print(f"      - {section_data}")
    else:
        print(f"\n❌ Company summary NOT found in data!")
        
        # Check if the structure is at the end without wrapper
        print(f"\n🔍 Checking for company summary structure at end of file...")
        
        # Look for the structure pattern
        file_content = latest_file.read_text(encoding='utf-8')
        
        if '"key_takeaways"' in file_content:
            print(f"   ✅ Key takeaways found in file")
        else:
            print(f"   ❌ Key takeaways NOT found")
            
        if '"strengths"' in file_content:
            print(f"   ✅ Strengths found in file")
        else:
            print(f"   ❌ Strengths NOT found")
            
        if '"weaknesses"' in file_content:
            print(f"   ✅ Weaknesses found in file")
        else:
            print(f"   ❌ Weaknesses NOT found")

if __name__ == "__main__":
    verify_company_summary()
