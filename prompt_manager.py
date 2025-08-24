#!/usr/bin/env python3
"""
Prompt Manager Utility for FlexXray Transcript Summarizer

This script provides a command-line interface for managing prompt configurations.
Users can view, edit, and customize prompts without modifying the core code.
"""

import json
import os
import sys
from typing import Dict, Any, List
from prompt_config import PromptConfig


def print_banner():
    """Print the application banner."""
    print("=" * 60)
    print("  FlexXray Transcript Summarizer - Prompt Manager")
    print("=" * 60)
    print()


def print_help():
    """Print help information."""
    print("Available commands:")
    print("  list                    - List all available prompt types")
    print("  view <prompt_type>      - View a specific prompt configuration")
    print("  edit <prompt_type>      - Edit a specific prompt")
    print("  export <filename>       - Export current config to file")
    print("  import <filename>       - Import config from file")
    print("  validate                - Validate all prompt configurations")
    print("  reset                   - Reset to default prompts")
    print("  help                    - Show this help message")
    print("  quit                    - Exit the prompt manager")
    print()


def list_prompts(prompt_config: PromptConfig):
    """List all available prompt types."""
    print("Available prompt types:")
    print("-" * 30)

    prompt_types = prompt_config.get_all_prompt_types()
    for i, prompt_type in enumerate(prompt_types, 1):
        print(f"{i}. {prompt_type}")

    print(f"\nTotal: {len(prompt_types)} prompt types")
    print()


def view_prompt(prompt_config: PromptConfig, prompt_type: str):
    """View a specific prompt configuration."""
    if prompt_type not in prompt_config.prompts:
        print(f"Error: Prompt type '{prompt_type}' not found.")
        return

    print(f"Prompt Configuration for: {prompt_type}")
    print("=" * 50)

    prompt_data = prompt_config.prompts[prompt_type]

    # Show system message
    system_msg = prompt_config.get_system_message(prompt_type)
    if system_msg:
        print(f"System Message: {system_msg}")
        print()

    # Show template
    if "template" in prompt_data:
        print("Template:")
        print("-" * 20)
        print(prompt_data["template"])
        print()

    # Show parameters
    if "parameters" in prompt_data:
        print("OpenAI Parameters:")
        print("-" * 20)
        for key, value in prompt_data["parameters"].items():
            print(f"  {key}: {value}")
        print()


def edit_prompt(prompt_config: PromptConfig, prompt_type: str):
    """Edit a specific prompt."""
    if prompt_type not in prompt_config.prompts:
        print(f"Error: Prompt type '{prompt_type}' not found.")
        return

    print(f"Editing prompt: {prompt_type}")
    print("=" * 30)

    current_template = prompt_config.get_prompt_template(prompt_type)
    current_system = prompt_config.get_system_message(prompt_type)
    current_params = prompt_config.get_prompt_parameters(prompt_type)

    print("Current configuration:")
    print(f"System Message: {current_system}")
    print(f"Model: {current_params.get('model', 'Not set')}")
    print(f"Temperature: {current_params.get('temperature', 'Not set')}")
    print(f"Max Tokens: {current_params.get('max_tokens', 'Not set')}")
    print()

    print("What would you like to edit?")
    print("1. Template")
    print("2. System Message")
    print("3. OpenAI Parameters")
    print("4. Cancel")

    choice = input("Enter your choice (1-4): ").strip()

    if choice == "1":
        print("\nCurrent template:")
        print("-" * 20)
        print(current_template)
        print("\nEnter new template (press Enter twice to finish):")

        lines = []
        while True:
            line = input()
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)

        new_template = "\n".join(lines[:-1])  # Remove the last empty line

        if new_template.strip():
            prompt_config.update_prompt(prompt_type, template=new_template)
            print("Template updated successfully!")
        else:
            print("Template not changed.")

    elif choice == "2":
        print(f"\nCurrent system message: {current_system}")
        new_system = input("Enter new system message: ").strip()

        if new_system:
            prompt_config.update_prompt(prompt_type, system_message=new_system)
            print("System message updated successfully!")
        else:
            print("System message not changed.")

    elif choice == "3":
        print("\nCurrent OpenAI parameters:")
        for key, value in current_params.items():
            print(f"  {key}: {value}")

        print("\nEnter new parameters (press Enter to keep current value):")

        new_params = {}
        for key in current_params:
            new_value = input(f"{key} ({current_params[key]}): ").strip()
            if new_value:
                try:
                    # Try to convert to appropriate type
                    if isinstance(current_params[key], bool):
                        new_params[key] = new_value.lower() in ["true", "1", "yes"]
                    elif isinstance(current_params[key], int):
                        new_params[key] = int(new_value)
                    elif isinstance(current_params[key], float):
                        new_params[key] = float(new_value)
                    else:
                        new_params[key] = new_value
                except ValueError:
                    print(f"Invalid value for {key}, keeping current value.")
                    new_params[key] = current_params[key]
            else:
                new_params[key] = current_params[key]

        prompt_config.update_prompt(prompt_type, parameters=new_params)
        print("OpenAI parameters updated successfully!")

    elif choice == "4":
        print("Edit cancelled.")
        return

    else:
        print("Invalid choice.")
        return

    # Save changes
    if prompt_config.save_config():
        print("Changes saved to configuration file.")


def export_config(prompt_config: PromptConfig, filename: str):
    """Export current configuration to file."""
    try:
        if prompt_config.save_config(filename):
            print(f"Configuration exported to: {filename}")
        else:
            print("Failed to export configuration.")
    except Exception as e:
        print(f"Error exporting configuration: {e}")


def import_config(prompt_config: PromptConfig, filename: str):
    """Import configuration from file."""
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        return

    try:
        with open(filename, "r", encoding="utf-8") as f:
            imported_config = json.load(f)

        # Validate imported config
        if not isinstance(imported_config, dict):
            print("Error: Invalid configuration file format.")
            return

        # Update current config
        prompt_config.prompts.update(imported_config)

        # Save to current config file
        if prompt_config.save_config():
            print(f"Configuration imported from: {filename}")
        else:
            print("Failed to save imported configuration.")

    except Exception as e:
        print(f"Error importing configuration: {e}")


def validate_config(prompt_config: PromptConfig):
    """Validate all prompt configurations."""
    print("Validating prompt configurations...")
    print("-" * 40)

    prompt_types = prompt_config.get_all_prompt_types()
    valid_count = 0
    invalid_count = 0

    for prompt_type in prompt_types:
        if prompt_config.validate_prompt(prompt_type):
            print(f"✓ {prompt_type}")
            valid_count += 1
        else:
            print(f"✗ {prompt_type} - Missing required fields")
            invalid_count += 1

    print()
    print(f"Validation complete: {valid_count} valid, {invalid_count} invalid")

    if invalid_count > 0:
        print("Invalid prompts may cause errors during execution.")
        print("Use 'edit <prompt_type>' to fix invalid prompts.")


def reset_config(prompt_config: PromptConfig):
    """Reset to default prompts."""
    print("This will reset all prompts to their default values.")
    confirm = input("Are you sure? (yes/no): ").strip().lower()

    if confirm in ["yes", "y"]:
        prompt_config.prompts = prompt_config._get_default_prompts()
        if prompt_config.save_config():
            print("Configuration reset to defaults.")
        else:
            print("Failed to save reset configuration.")
    else:
        print("Reset cancelled.")


def main():
    """Main function for the prompt manager."""
    print_banner()

    # Initialize prompt configuration
    config_file = "prompts.json"
    prompt_config = PromptConfig(config_file)

    print(f"Using configuration file: {config_file}")
    print()

    print_help()

    while True:
        try:
            command = input("prompt-manager> ").strip().lower()

            if command == "quit" or command == "exit":
                print("Goodbye!")
                break

            elif command == "help":
                print_help()

            elif command == "list":
                list_prompts(prompt_config)

            elif command.startswith("view "):
                prompt_type = command[5:].strip()
                view_prompt(prompt_config, prompt_type)

            elif command.startswith("edit "):
                prompt_type = command[5:].strip()
                edit_prompt(prompt_config, prompt_type)

            elif command.startswith("export "):
                filename = command[7:].strip()
                export_config(prompt_config, filename)

            elif command.startswith("import "):
                filename = command[7:].strip()
                import_config(prompt_config, filename)

            elif command == "validate":
                validate_config(prompt_config)

            elif command == "reset":
                reset_config(prompt_config)

            elif command == "":
                continue

            else:
                print(f"Unknown command: {command}")
                print("Type 'help' for available commands.")

            print()

        except KeyboardInterrupt:
            print("\nUse 'quit' to exit.")
        except EOFError:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
