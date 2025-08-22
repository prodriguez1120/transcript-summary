#!/usr/bin/env python3
"""
Example Usage of Company Configuration System

This script demonstrates how to use the new company configuration system
to easily switch between different companies and their analysis settings.
"""

from config_manager import get_config_manager, set_company
from company_config import create_custom_company_config
import os

def demonstrate_company_switching():
    """Demonstrate switching between different companies."""
    print("🏢 Company Configuration System Demo")
    print("=" * 50)
    
    # Start with FlexXray
    print("\n1. Starting with FlexXray configuration...")
    config_mgr = get_config_manager("flexxray")
    
    print(f"   Company: {config_mgr.company_config.display_name}")
    print(f"   Transcript Directory: {config_mgr.get_transcript_directory()}")
    print(f"   Output Prefix: {config_mgr.get_output_prefix()}")
    print(f"   Key Questions: {len(config_mgr.get_key_questions())}")
    
    # Show some key questions
    questions = config_mgr.get_key_questions()
    print("\n   Sample Questions:")
    for i, (key, question) in enumerate(list(questions.items())[:3], 1):
        print(f"     {i}. {key}: {question[:60]}...")
    
    # Switch to ACME Corp
    print("\n2. Switching to ACME Corporation...")
    config_mgr.switch_company("acme_corp")
    
    print(f"   Company: {config_mgr.company_config.display_name}")
    print(f"   Transcript Directory: {config_mgr.get_transcript_directory()}")
    print(f"   Output Prefix: {config_mgr.get_output_prefix()}")
    print(f"   Key Questions: {len(config_mgr.get_key_questions())}")
    
    # Show ACME questions
    questions = config_mgr.get_key_questions()
    print("\n   Sample Questions:")
    for i, (key, question) in enumerate(list(questions.items())[:3], 1):
        print(f"     {i}. {key}: {question[:60]}...")
    
    # Switch back to FlexXray
    print("\n3. Switching back to FlexXray...")
    config_mgr.switch_company("flexxray")
    print(f"   Company: {config_mgr.company_config.display_name}")

def demonstrate_new_company_creation():
    """Demonstrate creating a new company configuration."""
    print("\n\n🔧 Creating New Company Configuration")
    print("=" * 50)
    
    config_mgr = get_config_manager()
    
    # Create a new tech startup company
    print("Creating 'TechStartup Inc' configuration...")
    
    new_company = config_mgr.create_new_company(
        name="techstartup",
        display_name="TechStartup Inc",
        transcript_directory="TechStartup Transcripts",
        output_prefix="TechStartup",
        key_questions={
            "product_market_fit": "How well does TechStartup's product fit the market?",
            "competitive_advantage": "What competitive advantages does TechStartup have?",
            "growth_strategy": "What is TechStartup's growth strategy?",
            "funding_status": "What is TechStartup's current funding status?",
            "team_strength": "How strong is TechStartup's team?",
            "market_timing": "Is the market timing right for TechStartup?"
        },
        question_categories={
            "key_takeaways": ["product_market_fit", "competitive_advantage"],
            "strengths": ["team_strength", "growth_strategy"],
            "weaknesses": ["funding_status", "market_timing"]
        }
    )
    
    if new_company:
        print(f"✓ Successfully created {new_company.display_name}")
        print(f"  Transcript directory: {new_company.transcript_directory}")
        print(f"  Key questions: {len(new_company.key_questions)}")
        print(f"  Categories: {', '.join(new_company.question_categories.keys())}")
        
        # Switch to the new company
        print("\nSwitching to TechStartup...")
        config_mgr.switch_company("techstartup")
        
        print(f"Current company: {config_mgr.company_config.display_name}")
        print(f"Questions: {len(config_mgr.get_key_questions())}")
        
        # Show the new questions
        questions = config_mgr.get_key_questions()
        print("\nTechStartup Questions:")
        for key, question in questions.items():
            print(f"  {key}: {question}")
    else:
        print("✗ Failed to create new company")

def demonstrate_configuration_updates():
    """Demonstrate updating company configurations."""
    print("\n\n📝 Updating Company Configuration")
    print("=" * 50)
    
    config_mgr = get_config_manager("techstartup")
    
    print(f"Current company: {config_mgr.company_config.display_name}")
    print(f"Current transcript directory: {config_mgr.get_transcript_directory()}")
    
    # Update the transcript directory
    print("\nUpdating transcript directory...")
    config_mgr.update_current_company(
        transcript_directory="TechStartup Interview Transcripts"
    )
    
    print(f"New transcript directory: {config_mgr.get_transcript_directory()}")
    
    # Update key questions
    print("\nAdding a new key question...")
    current_questions = config_mgr.get_key_questions()
    current_questions["customer_feedback"] = "What customer feedback has TechStartup received?"
    
    config_mgr.update_current_company(key_questions=current_questions)
    
    print(f"Updated questions count: {len(config_mgr.get_key_questions())}")
    print("New question added: customer_feedback")

def demonstrate_directory_management():
    """Demonstrate transcript directory management."""
    print("\n\n🗂️ Transcript Directory Management")
    print("=" * 50)
    
    config_mgr = get_config_manager("techstartup")
    
    transcript_dir = config_mgr.get_transcript_directory()
    print(f"Current transcript directory: {transcript_dir}")
    
    # Check if directory exists
    if config_mgr.validate_transcript_directory():
        print("✓ Transcript directory exists")
    else:
        print("✗ Transcript directory does not exist")
        
        # Create the directory
        print("Creating transcript directory...")
        if config_mgr.create_transcript_directory():
            print("✓ Directory created successfully")
        else:
            print("✗ Failed to create directory")
    
    # List all available companies and their directories
    print("\nAll company transcript directories:")
    for company in config_mgr.list_companies():
        temp_config = get_config_manager(company)
        dir_path = temp_config.get_transcript_directory()
        exists = "✓" if temp_config.validate_transcript_directory() else "✗"
        print(f"  {exists} {company}: {dir_path}")

def demonstrate_integration_with_analysis():
    """Demonstrate how the configuration integrates with analysis."""
    print("\n\n🔍 Integration with Analysis System")
    print("=" * 50)
    
    # Show how configuration affects analysis
    config_mgr = get_config_manager("techstartup")
    
    print("TechStartup Analysis Configuration:")
    print(f"  Company: {config_mgr.company_config.display_name}")
    print(f"  Transcript Directory: {config_mgr.get_transcript_directory()}")
    print(f"  Output Prefix: {config_mgr.get_output_prefix()}")
    
    # Show how output files would be named
    print(f"\nOutput files would be named:")
    print(f"  - {config_mgr.get_output_prefix()}_quote_analysis.json")
    print(f"  - {config_mgr.get_output_prefix()}_transcript_analysis.txt")
    print(f"  - {config_mgr.get_output_prefix()}_company_summary.xlsx")
    
    # Show key questions for analysis
    print(f"\nAnalysis will focus on these questions:")
    questions = config_mgr.get_key_questions()
    for i, (key, question) in enumerate(questions.items(), 1):
        print(f"  {i}. {question}")
    
    # Show question categories
    print(f"\nQuestions organized into categories:")
    categories = config_mgr.get_question_categories()
    for category, question_keys in categories.items():
        print(f"  {category}: {', '.join(question_keys)}")

def main():
    """Run all demonstrations."""
    try:
        # Run all demonstrations
        demonstrate_company_switching()
        demonstrate_new_company_creation()
        demonstrate_configuration_updates()
        demonstrate_directory_management()
        demonstrate_integration_with_analysis()
        
        print("\n\n🎉 Demo completed successfully!")
        print("\nTo use the system:")
        print("1. python company_switcher.py --list")
        print("2. python company_switcher.py --switch <company_name>")
        print("3. python company_switcher.py --create <new_company>")
        print("4. python company_switcher.py --info")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
