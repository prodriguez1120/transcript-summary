#!/usr/bin/env python3
"""
Environment Configuration Module for FlexXray Transcript Summarizer

This module centralizes all environment variable handling and provides
a clean interface for accessing configuration values throughout the application.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional


class EnvironmentConfig:
    """Centralized environment configuration manager."""

    def __init__(self, env_file: str = ".env"):
        """Initialize the environment configuration."""
        self.env_file = env_file
        self._load_environment()

    def _load_environment(self):
        """Load environment variables from .env file."""
        # Load from .env file if it exists
        if os.path.exists(self.env_file):
            load_dotenv(self.env_file)
        else:
            # Try to load from project root
            project_root = Path(__file__).parent
            env_path = project_root / self.env_file
            if env_path.exists():
                load_dotenv(env_path)

    @property
    def openai_api_key(self) -> Optional[str]:
        """Get the OpenAI API key from environment variables."""
        return os.getenv("OPENAI_API_KEY")

    @property
    def debug_mode(self) -> bool:
        """Get debug mode setting from environment variables."""
        return os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

    @property
    def project_root(self) -> Path:
        """Get the project root directory."""
        return Path(__file__).parent

    @property
    def output_directory(self) -> Path:
        """Get the output directory path."""
        return self.project_root / "Outputs"

    @property
    def transcript_directory(self) -> Path:
        """Get the default transcript directory path."""
        return self.project_root / "FlexXray Transcripts"

    @property
    def chroma_db_directory(self) -> Path:
        """Get the ChromaDB directory path."""
        return self.project_root / "chroma_db"

    def validate_configuration(self) -> bool:
        """Validate that all required configuration is present."""
        if not self.openai_api_key:
            print("❌ OPENAI_API_KEY not found in environment variables")
            print("   Please check your .env file or set the environment variable")
            return False

        if not self.openai_api_key.startswith("sk-"):
            print("❌ OPENAI_API_KEY format appears invalid")
            print("   API key should start with 'sk-'")
            return False

        print("✅ Environment configuration validated successfully")
        print(f"   OpenAI API Key: {'*' * 10}{self.openai_api_key[-4:]}")
        print(f"   Debug Mode: {self.debug_mode}")
        print(f"   Project Root: {self.project_root}")
        print(f"   Output Directory: {self.output_directory}")
        print(f"   Transcript Directory: {self.transcript_directory}")
        print(f"   ChromaDB Directory: {self.chroma_db_directory}")

        return True

    def get_api_key_for_component(self, component_name: str) -> str:
        """Get the API key for a specific component with validation."""
        api_key = self.openai_api_key
        if not api_key:
            raise ValueError(f"OpenAI API key not found. Required for {component_name}")
        return api_key

    def ensure_directories_exist(self):
        """Ensure all required directories exist."""
        directories = [
            self.output_directory,
            self.transcript_directory,
            self.chroma_db_directory,
        ]

        for directory in directories:
            directory.mkdir(exist_ok=True)
            print(f"✅ Directory ensured: {directory}")


# Global instance
_env_config = None


def get_env_config() -> EnvironmentConfig:
    """Get the global environment configuration instance."""
    global _env_config
    if _env_config is None:
        _env_config = EnvironmentConfig()
    return _env_config


def get_openai_api_key() -> str:
    """Get the OpenAI API key from the environment configuration."""
    config = get_env_config()
    return config.get_api_key_for_component("OpenAI operations")


def is_debug_mode() -> bool:
    """Check if debug mode is enabled."""
    config = get_env_config()
    return config.debug_mode


def get_project_paths():
    """Get common project paths."""
    config = get_env_config()
    return {
        "project_root": config.project_root,
        "output_directory": config.output_directory,
        "transcript_directory": config.transcript_directory,
        "chroma_db_directory": config.chroma_db_directory,
    }


# Convenience functions for backward compatibility
def load_dotenv_if_exists():
    """Load .env file if it exists (for backward compatibility)."""
    get_env_config()


if __name__ == "__main__":
    # Test the environment configuration
    print("=" * 60)
    print("ENVIRONMENT CONFIGURATION TEST")
    print("=" * 60)

    config = get_env_config()

    # Validate configuration
    if config.validate_configuration():
        print("\n✅ Configuration is valid and ready to use!")

        # Ensure directories exist
        print("\nEnsuring directories exist...")
        config.ensure_directories_exist()

        # Test convenience functions
        print("\nTesting convenience functions...")
        try:
            api_key = get_openai_api_key()
            print(f"✅ get_openai_api_key(): {len(api_key)} characters")
        except Exception as e:
            print(f"❌ get_openai_api_key(): {e}")

        debug_mode = is_debug_mode()
        print(f"✅ is_debug_mode(): {debug_mode}")

        paths = get_project_paths()
        print(f"✅ get_project_paths(): {len(paths)} paths available")

    else:
        print("\n❌ Configuration validation failed!")
        print("Please check your .env file and environment variables.")
