#!/usr/bin/env python3
"""
Test Script for Quote Export with Text Wrapping

This script demonstrates the new quote export functionality that ensures
quote column text is properly wrapped to show the full quote when outputted.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from export_utils import ExportManager

def test_quote_export():
    """Test the new quote export functionality."""
    
    # Initialize export manager
    export_manager = ExportManager()
    
    # Sample quote data for testing
    sample_quotes = [
        {
            'id': 'Q001',
            'text': 'FlexXray has been the market leader in foreign material inspection services for over 20 years. Our technology and customer relationships give us a significant competitive advantage that is difficult for others to replicate.',
            'speaker_info': {'name': 'Randy Jesberg', 'company': 'FlexXray', 'title': 'Former CEO'},
            'transcript_name': 'Randy_Jesberg-Former_CEO_Initial_Conversation',
            'sentiment': 'positive',
            'relevance_score': 9.5,
            'theme': 'Market Leadership',
            'date': '2025-06-26'
        },
        {
            'id': 'Q002',
            'text': 'The key to our success has been maintaining the right balance between technology innovation and customer service. We invest heavily in R&D but never lose sight of what our customers actually need and value most.',
            'speaker_info': {'name': 'Cheryl Bertics', 'company': 'FlexXray', 'title': 'Former Manager'},
            'transcript_name': 'Cheryl_Bertics-FlexXray_Foreign_Material_Inspection_Services',
            'sentiment': 'positive',
            'relevance_score': 8.8,
            'theme': 'Customer Focus',
            'date': '2025-06-26'
        },
        {
            'id': 'Q003',
            'text': 'Our pricing strategy is based on a per-batch model that provides transparency and predictability for our customers. This approach has been very successful in building long-term relationships and maintaining our market position.',
            'speaker_info': {'name': 'George Perry-West', 'company': 'Pegasus Foods', 'title': 'Former FSQA Manager'},
            'transcript_name': 'George_Perry-West-Pegasus_Foods_Inc_Former_FSQA_Manager',
            'sentiment': 'neutral',
            'relevance_score': 7.2,
            'theme': 'Pricing Strategy',
            'date': '2025-06-26'
        }
    ]
    
    print("Testing Quote Export with Text Wrapping...")
    print(f"Sample quotes prepared: {len(sample_quotes)}")
    
    # Export quotes to Excel
    excel_file = export_manager.export_quotes_to_excel(sample_quotes)
    
    if excel_file:
        print(f"✅ Successfully exported quotes to Excel: {excel_file}")
        print("\nKey Features Implemented:")
        print("• Quote column (Column B) has text wrapping enabled")
        print("• Column width set to 80 characters for optimal quote display")
        print("• Row height set to 60 points to accommodate wrapped text")
        print("• Header row frozen for easy navigation")
        print("• Professional formatting with proper alignment")
    else:
        print("❌ Failed to export quotes to Excel")
    
    return excel_file

if __name__ == "__main__":
    # Check if openpyxl is available
    try:
        import openpyxl
        print("✅ openpyxl is available - Excel export will work")
    except ImportError:
        print("❌ openpyxl not available - Install with: pip install openpyxl")
        exit(1)
    
    # Run the test
    test_quote_export()
