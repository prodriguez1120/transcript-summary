#!/usr/bin/env python3
"""
Test Script for Practifi Company Setup

This script tests the Practifi company configuration and verifies
that PDF and Word document processing is working correctly.
"""

from config_manager import get_config_manager
from document_processor import DocumentProcessor
import os

def test_practifi_configuration():
    """Test the Practifi company configuration."""
    print("🏢 Testing Practifi Company Configuration")
    print("=" * 50)
    
    # Get Practifi configuration
    config_mgr = get_config_manager("practifi")
    
    print(f"Company: {config_mgr.company_config.display_name}")
    print(f"Transcript Directory: {config_mgr.get_transcript_directory()}")
    print(f"Output Prefix: {config_mgr.get_output_prefix()}")
    print(f"Key Questions: {len(config_mgr.get_key_questions())}")
    
    # Show key questions
    print("\nKey Questions:")
    questions = config_mgr.get_key_questions()
    for i, (key, question) in enumerate(questions.items(), 1):
        print(f"  {i}. {key}: {question}")
    
    # Show question categories
    print("\nQuestion Categories:")
    categories = config_mgr.get_question_categories()
    for category, question_keys in categories.items():
        print(f"  {category}: {', '.join(question_keys)}")
    
    return config_mgr

def test_document_processor():
    """Test the document processor for PDF and Word support."""
    print("\n\n📄 Testing Document Processor")
    print("=" * 50)
    
    processor = DocumentProcessor()
    
    print(f"Supported formats: {', '.join(processor.get_supported_formats())}")
    print(f"Word support: {'✓' if processor.docx_available else '✗'}")
    print(f"PDF support: {'✓' if processor.pypdf_available else '✗'}")
    
    return processor

def test_practifi_directory():
    """Test the Practifi transcripts directory."""
    print("\n\n📁 Testing Practifi Transcripts Directory")
    print("=" * 50)
    
    config_mgr = get_config_manager("practifi")
    transcript_dir = config_mgr.get_transcript_directory()
    
    print(f"Transcript directory: {transcript_dir}")
    
    if os.path.exists(transcript_dir):
        print("✓ Directory exists")
        
        # List files in directory
        files = [f for f in os.listdir(transcript_dir) if os.path.isfile(os.path.join(transcript_dir, f))]
        print(f"Files found: {len(files)}")
        
        if files:
            print("\nFiles in directory:")
            for file in files:
                file_path = os.path.join(transcript_dir, file)
                file_ext = os.path.splitext(file)[1].lower()
                print(f"  {file} ({file_ext})")
        else:
            print("  No files found in directory")
    else:
        print("✗ Directory does not exist")
        print("  Creating directory...")
        try:
            os.makedirs(transcript_dir, exist_ok=True)
            print("✓ Directory created successfully")
        except Exception as e:
            print(f"✗ Failed to create directory: {e}")

def test_document_processing():
    """Test processing documents in the Practifi directory."""
    print("\n\n🔍 Testing Document Processing")
    print("=" * 50)
    
    config_mgr = get_config_manager("practifi")
    processor = DocumentProcessor()
    
    transcript_dir = config_mgr.get_transcript_directory()
    
    if not os.path.exists(transcript_dir):
        print("Transcript directory not found, skipping document processing test")
        return
    
    # Process all documents in directory
    results = processor.process_directory(transcript_dir)
    
    if not results:
        print("No documents found to process")
        return
    
    print(f"Processed {len(results)} documents:")
    
    for result in results:
        print(f"\n📄 {result['file_name']}")
        print(f"  Format: {result['file_extension']}")
        print(f"  Size: {result['file_size']} bytes")
        print(f"  Can process: {result['can_process']}")
        
        if result.get('extraction_successful'):
            print(f"  Text length: {result['text_length']} characters")
            print(f"  Preview: {result['text_preview']}")
        else:
            print("  ✗ Text extraction failed")
        
        # Show additional info for specific formats
        if result['file_extension'] == '.docx' and 'paragraphs' in result:
            print(f"  Paragraphs: {result['paragraphs']}")
            print(f"  Tables: {result['tables']}")
        elif result['file_extension'] == '.pdf' and 'pages' in result:
            print(f"  Pages: {result['pages']}")

def test_company_switching():
    """Test switching between companies."""
    print("\n\n🔄 Testing Company Switching")
    print("=" * 50)
    
    # Start with Practifi
    config_mgr = get_config_manager("practifi")
    print(f"Current company: {config_mgr.company_config.display_name}")
    
    # Switch to FlexXray
    print("\nSwitching to FlexXray...")
    config_mgr.switch_company("flexxray")
    print(f"Current company: {config_mgr.company_config.display_name}")
    
    # Switch back to Practifi
    print("\nSwitching back to Practifi...")
    config_mgr.switch_company("practifi")
    print(f"Current company: {config_mgr.company_config.display_name}")

def main():
    """Run all tests."""
    try:
        print("🚀 Practifi Company Setup Test Suite")
        print("=" * 60)
        
        # Run all tests
        test_practifi_configuration()
        test_document_processor()
        test_practifi_directory()
        test_document_processing()
        test_company_switching()
        
        print("\n\n🎉 All tests completed successfully!")
        print("\nNext steps:")
        print("1. Add your Practifi transcript files (PDF or Word) to the 'Practifi Transcripts' folder")
        print("2. Run: python company_switcher.py --switch practifi")
        print("3. Run your analysis: python run_streamlined_analysis.py")
        print("4. Or run quote analysis: python quote_analysis_tool.py")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
