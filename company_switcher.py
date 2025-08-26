#!/usr/bin/env python3
"""
Company Switcher - Command Line Interface

Simple command-line tool for switching between different company configurations
and managing transcript analysis settings.
"""

import argparse
import sys
import os
import logging
from settings import get_config_manager, switch_company, SettingsManager
from logging_config import setup_logger

# Set up logging
logger = setup_logger(__name__)


def main():
    """Main command-line interface."""
    parser = argparse.ArgumentParser(
        description="Company Configuration Switcher for Transcript Summarizer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python company_switcher.py --list                    # List all companies
  python company_switcher.py --switch flexxray         # Switch to FlexXray
  python company_switcher.py --switch techpro          # Switch to TechPro
  python company_switcher.py --info                    # Show current company info
  python company_switcher.py --create startup_xyz      # Create new company
  python company_switcher.py --validate                # Validate transcript directory
        """,
    )

    parser.add_argument(
        "--list", "-l", action="store_true", help="List all available companies"
    )

    parser.add_argument(
        "--switch", "-s", metavar="COMPANY", help="Switch to specified company"
    )

    parser.add_argument(
        "--info", "-i", action="store_true", help="Show current company information"
    )

    parser.add_argument(
        "--create",
        "-c",
        metavar="COMPANY_NAME",
        help="Create a new company configuration (interactive)",
    )

    parser.add_argument(
        "--validate",
        "-v",
        action="store_true",
        help="Validate current company transcript directory",
    )

    parser.add_argument(
        "--questions",
        "-q",
        action="store_true",
        help="Show current company key questions",
    )

    parser.add_argument(
        "--update",
        "-u",
        metavar="FIELD:VALUE",
        nargs="+",
        help="Update company configuration fields (format: field:value)",
    )

    args = parser.parse_args()

    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        return

    try:
        # Get current config manager
        config_mgr = get_config_manager()

        # Handle different commands
        if args.list:
            list_companies(config_mgr)

        elif args.switch:
            switch_company(config_mgr, args.switch)

        elif args.info:
            show_company_info(config_mgr)

        elif args.create:
            create_company_interactive(config_mgr, args.create)

        elif args.validate:
            validate_transcript_directory(config_mgr)

        elif args.questions:
            show_key_questions(config_mgr)

        elif args.update:
            update_company_config(config_mgr, args.update)

        else:
            parser.print_help()

    except (ValueError, TypeError) as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except ConnectionError as e:
        logger.error(f"Connection error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


def list_companies(config_mgr: SettingsManager):
    """List all available companies."""
    companies = config_mgr.list_companies()
    current = config_mgr.current_company

    print("Available Companies:")
    print("=" * 50)

    for company in companies:
        if company == current:
            print(f"  * {company} (current)")
        else:
            print(f"    {company}")

    print(f"\nCurrent company: {current}")


def switch_company(config_mgr: SettingsManager, company_name: str):
    """Switch to a different company."""
    if config_mgr.switch_company(company_name):
        print(f"Successfully switched to {company_name}")
        show_company_info(config_mgr)
    else:
        print(f"Failed to switch to {company_name}")


def show_company_info(config_mgr: SettingsManager):
    """Show current company information."""
    info = config_mgr.get_company_info()

    print(f"Current Company: {info['display_name']}")
    print("=" * 50)
    print(f"Name: {info['name']}")
    print(f"Transcript Directory: {info['transcript_directory']}")
    print(f"Output Prefix: {info['output_prefix']}")
    print(f"Key Questions: {info['key_questions_count']}")
    print(f"Question Categories: {', '.join(info['question_categories'])}")
    print(f"Industry Keywords: {info['industry_keywords_count']}")

    # Check if transcript directory exists
    if config_mgr.validate_transcript_directory():
        print(f"✓ Transcript directory exists")
    else:
        print(f"✗ Transcript directory does not exist")
        print(f"  Use --validate to create it")


def create_company_interactive(config_mgr: SettingsManager, company_name: str):
    """Create a new company configuration interactively."""
    print(f"Creating new company: {company_name}")
    print("=" * 50)

    # Get basic information
    display_name = (
        input(f"Display name [{company_name.title()}]: ").strip()
        or company_name.title()
    )
    transcript_dir = (
        input(f"Transcript directory [{display_name} Transcripts]: ").strip()
        or f"{display_name} Transcripts"
    )
    output_prefix = input(
        f"Output prefix [{display_name.replace(' ', '')}]: "
    ).strip() or display_name.replace(" ", "")

    # Get key questions
    print("\nEnter key questions (press Enter twice to finish):")
    key_questions = {}
    question_num = 1

    while True:
        question_key = input(
            f"Question {question_num} key (e.g., market_position): "
        ).strip()
        if not question_key:
            break

        question_text = input(f"Question {question_num} text: ").strip()
        if question_text:
            key_questions[question_key] = question_text
            question_num += 1
        else:
            print("Question text cannot be empty")

    if not key_questions:
        print("No questions provided, using default questions")
        key_questions = {
            "market_position": f"What is {display_name}'s market position?",
            "competitive_advantage": f"What competitive advantages does {display_name} have?",
        }

    # Get question categories
    print("\nEnter question categories (press Enter twice to finish):")
    question_categories = {}

    while True:
        category = input("Category name (e.g., key_takeaways): ").strip()
        if not category:
            break

        questions = input(f"Questions for {category} (comma-separated): ").strip()
        if questions:
            question_list = [q.strip() for q in questions.split(",")]
            question_categories[category] = question_list

    if not question_categories:
        print("No categories provided, using default categories")
        question_categories = {
            "key_takeaways": list(key_questions.keys())[:2],
            "strengths": (
                list(key_questions.keys())[2:] if len(key_questions) > 2 else []
            ),
        }

    # Create the company
    try:
        new_company = config_mgr.create_new_company(
            name=company_name,
            display_name=display_name,
            transcript_directory=transcript_dir,
            output_prefix=output_prefix,
            key_questions=key_questions,
            question_categories=question_categories,
        )

        if new_company:
            print(f"\n✓ Successfully created {display_name}")
            print(f"  Transcript directory: {transcript_dir}")
            print(f"  Key questions: {len(key_questions)}")
            print(f"  Categories: {', '.join(question_categories.keys())}")

            # Ask if user wants to switch to new company
            switch_now = (
                input(f"\nSwitch to {display_name} now? (y/n): ").strip().lower()
            )
            if switch_now in ["y", "yes"]:
                config_mgr.switch_company(company_name)
                print(f"Switched to {display_name}")
        else:
            print("Failed to create company")

    except (ValueError, TypeError) as e:
        logger.error(f"Data validation error creating company: {e}")
        print(f"Error creating company: {e}")
    except (IOError, OSError) as e:
        logger.error(f"File system error creating company: {e}")
        print(f"Error creating company: {e}")
    except Exception as e:
        logger.error(f"Unexpected error creating company: {e}")
        print(f"Error creating company: {e}")


def validate_transcript_directory(config_mgr: SettingsManager):
    """Validate and optionally create transcript directory."""
    if config_mgr.validate_transcript_directory():
        print(f"✓ Transcript directory exists: {config_mgr.get_transcript_directory()}")
    else:
        print(
            f"✗ Transcript directory does not exist: {config_mgr.get_transcript_directory()}"
        )

        create_dir = input("Create directory now? (y/n): ").strip().lower()
        if create_dir in ["y", "yes"]:
            if config_mgr.create_transcript_directory():
                print("✓ Directory created successfully")
            else:
                print("✗ Failed to create directory")


def show_key_questions(config_mgr: SettingsManager):
    """Show current company key questions."""
    questions = config_mgr.get_key_questions()
    categories = config_mgr.get_question_categories()

    print(f"Key Questions for {config_mgr.company_config.display_name}")
    print("=" * 60)

    for category, question_keys in categories.items():
        print(f"\n{category.upper().replace('_', ' ')}:")
        print("-" * 30)
        for key in question_keys:
            if key in questions:
                print(f"  {key}: {questions[key]}")

    print(f"\nTotal questions: {len(questions)}")


def update_company_config(config_mgr: SettingsManager, updates: list):
    """Update company configuration fields."""
    update_dict = {}

    for update in updates:
        if ":" in update:
            field, value = update.split(":", 1)
            field = field.strip()
            value = value.strip()

            # Try to convert value to appropriate type
            if value.lower() in ["true", "false"]:
                value = value.lower() == "true"
            elif value.isdigit():
                value = int(value)
            elif value.startswith("[") and value.endswith("]"):
                # Handle list values
                value = [item.strip() for item in value[1:-1].split(",")]
            elif value.startswith("{") and value.endswith("}"):
                # Handle dict values (simplified)
                try:
                    value = eval(value)  # Note: eval should be used carefully
                except:
                    print(f"Warning: Could not parse dict value: {value}")
                    continue

            update_dict[field] = value
        else:
            print(f"Warning: Invalid update format: {update} (use field:value)")

    if update_dict:
        if config_mgr.update_current_company(**update_dict):
            print("✓ Configuration updated successfully")
            show_company_info(config_mgr)
        else:
            print("✗ Failed to update configuration")


if __name__ == "__main__":
    main()
