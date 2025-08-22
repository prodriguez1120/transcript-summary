#!/usr/bin/env python3
"""
Configuration Manager for Transcript Summarizer

This module manages the integration between company configurations and the existing
system, providing easy switching between different companies and their settings.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from company_config import CompanyConfig, get_company_config, create_custom_company_config, list_available_companies
from logging_config import setup_logger

class ConfigManager:
    """Manages configuration for the transcript summarizer system."""
    
    def __init__(self, company_name: str = "flexxray", config_file: str = "company_settings.json"):
        """Initialize the configuration manager."""
        self.logger = setup_logger(__name__)
        self.config_file = config_file
        self.current_company = company_name
        self.company_config = get_company_config(company_name)
        self.load_custom_settings()
    
    def load_custom_settings(self):
        """Load custom settings from JSON file if it exists."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    custom_settings = json.load(f)
                
                # Apply custom settings to current company config
                if self.current_company in custom_settings:
                    company_settings = custom_settings[self.current_company]
                    for key, value in company_settings.items():
                        if hasattr(self.company_config, key):
                            setattr(self.company_config, key, value)
                            
            except (ValueError, TypeError) as e:
                self.logger.warning(f"Data validation error loading custom settings: {e}")
                print(f"Warning: Could not load custom settings: {e}")
            except (IOError, OSError) as e:
                self.logger.warning(f"File system error loading custom settings: {e}")
                print(f"Warning: Could not load custom settings: {e}")
            except Exception as e:
                self.logger.warning(f"Unexpected error loading custom settings: {e}")
                print(f"Warning: Could not load custom settings: {e}")
    
    def save_custom_settings(self):
        """Save current company configuration to JSON file."""
        try:
            # Load existing settings
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    all_settings = json.load(f)
            else:
                all_settings = {}
            
            # Update current company settings
            company_settings = {}
            for field in self.company_config.__dataclass_fields__:
                company_settings[field] = getattr(self.company_config, field)
            
            all_settings[self.current_company] = company_settings
            
            # Save to file
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(all_settings, f, indent=2, ensure_ascii=False)
                
            print(f"Settings saved for {self.company_config.display_name}")
            
        except (ValueError, TypeError) as e:
            self.logger.error(f"Data validation error saving settings: {e}")
            print(f"Error saving settings: {e}")
        except (IOError, OSError) as e:
            self.logger.error(f"File system error saving settings: {e}")
            print(f"Error saving settings: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error saving settings: {e}")
            print(f"Error saving settings: {e}")
    
    def switch_company(self, company_name: str) -> bool:
        """Switch to a different company configuration."""
        try:
            self.current_company = company_name
            self.company_config = get_company_config(company_name)
            self.load_custom_settings()
            print(f"Switched to {self.company_config.display_name}")
            return True
        except (ValueError, TypeError) as e:
            self.logger.error(f"Data validation error switching company: {e}")
            print(f"Error switching company: {e}")
            return False
        except (IOError, OSError) as e:
            self.logger.error(f"File system error switching company: {e}")
            print(f"Error switching company: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error switching company: {e}")
            print(f"Error switching company: {e}")
            return False
    
    def get_transcript_directory(self) -> str:
        """Get the current company's transcript directory."""
        return self.company_config.transcript_directory
    
    def get_output_prefix(self) -> str:
        """Get the current company's output prefix."""
        return self.company_config.output_prefix
    
    def get_key_questions(self) -> Dict[str, str]:
        """Get the current company's key questions."""
        return self.company_config.key_questions
    
    def get_question_categories(self) -> Dict[str, list]:
        """Get the current company's question categories."""
        return self.company_config.question_categories
    
    def get_speaker_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Get the current company's speaker patterns."""
        return self.company_config.speaker_patterns
    
    def get_business_insights(self) -> Dict[str, Dict[str, Any]]:
        """Get the current company's business insight patterns."""
        return self.company_config.business_insights
    
    def get_topic_synonyms(self) -> Dict[str, list]:
        """Get the current company's topic synonyms."""
        return self.company_config.topic_synonyms
    
    def get_industry_keywords(self) -> list:
        """Get the current company's industry keywords."""
        return self.company_config.industry_keywords
    
    def get_company_specific_terms(self) -> list:
        """Get the current company's specific terms."""
        return self.company_config.company_specific_terms
    
    def create_new_company(self, **kwargs) -> CompanyConfig:
        """Create a new company configuration."""
        try:
            new_config = create_custom_company_config(**kwargs)
            self.save_custom_settings()
            return new_config
        except (ValueError, TypeError) as e:
            self.logger.error(f"Data validation error creating new company: {e}")
            print(f"Error creating new company: {e}")
            return None
        except (IOError, OSError) as e:
            self.logger.error(f"File system error creating new company: {e}")
            print(f"Error creating new company: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error creating new company: {e}")
            print(f"Error creating new company: {e}")
            return None
    
    def update_current_company(self, **updates) -> bool:
        """Update the current company configuration."""
        try:
            for key, value in updates.items():
                if hasattr(self.company_config, key):
                    setattr(self.company_config, key, value)
            
            self.save_custom_settings()
            return True
        except (ValueError, TypeError) as e:
            self.logger.error(f"Data validation error updating company: {e}")
            print(f"Error updating company: {e}")
            return False
        except (IOError, OSError) as e:
            self.logger.error(f"File system error updating company: {e}")
            print(f"Error updating company: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error updating company: {e}")
            print(f"Error updating company: {e}")
            return False
    
    def list_companies(self) -> list:
        """List all available companies."""
        return list_available_companies()
    
    def get_company_info(self) -> Dict[str, Any]:
        """Get information about the current company."""
        return {
            "name": self.company_config.name,
            "display_name": self.company_config.display_name,
            "transcript_directory": self.company_config.transcript_directory,
            "output_prefix": self.company_config.output_prefix,
            "key_questions_count": len(self.company_config.key_questions),
            "question_categories": list(self.company_config.question_categories.keys()),
            "industry_keywords_count": len(self.company_config.industry_keywords)
        }
    
    def validate_transcript_directory(self) -> bool:
        """Check if the transcript directory exists."""
        return os.path.exists(self.company_config.transcript_directory)
    
    def create_transcript_directory(self) -> bool:
        """Create the transcript directory if it doesn't exist."""
        try:
            os.makedirs(self.company_config.transcript_directory, exist_ok=True)
            print(f"Transcript directory created: {self.company_config.transcript_directory}")
            return True
        except (IOError, OSError) as e:
            self.logger.error(f"File system error creating transcript directory: {e}")
            print(f"Error creating transcript directory: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error creating transcript directory: {e}")
            print(f"Error creating transcript directory: {e}")
            return False

# Global configuration manager instance
_global_config_manager = None

def get_config_manager(company_name: str = "flexxray") -> ConfigManager:
    """Get the global configuration manager instance."""
    global _global_config_manager
    if _global_config_manager is None or _global_config_manager.current_company != company_name:
        _global_config_manager = ConfigManager(company_name)
    return _global_config_manager

def set_company(company_name: str) -> bool:
    """Set the current company for the global configuration manager."""
    global _global_config_manager
    if _global_config_manager is None:
        _global_config_manager = ConfigManager(company_name)
    else:
        return _global_config_manager.switch_company(company_name)
    return True

# Example usage and testing
if __name__ == "__main__":
    # Initialize with FlexXray
    config_mgr = ConfigManager("flexxray")
    
    print("=== Current Company Info ===")
    print(json.dumps(config_mgr.get_company_info(), indent=2))
    
    print("\n=== Available Companies ===")
    print(config_mgr.list_companies())
    
    print("\n=== Key Questions ===")
    for key, question in config_mgr.get_key_questions().items():
        print(f"{key}: {question}")
    
    print("\n=== Transcript Directory ===")
    print(f"Directory: {config_mgr.get_transcript_directory()}")
    print(f"Exists: {config_mgr.validate_transcript_directory()}")
    
    # Example of creating a new company
    print("\n=== Creating New Company ===")
    new_company = config_mgr.create_new_company(
        name="startup_xyz",
        display_name="Startup XYZ",
        transcript_directory="Startup XYZ Transcripts",
        output_prefix="StartupXYZ",
        key_questions={
            "product_fit": "How well does Startup XYZ's product fit the market?",
            "competitive_edge": "What competitive advantages does Startup XYZ have?"
        },
        question_categories={
            "key_takeaways": ["product_fit", "competitive_edge"]
        }
    )
    
    if new_company:
        print(f"Created new company: {new_company.display_name}")
        print(f"Available companies: {config_mgr.list_companies()}")
