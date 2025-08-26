#!/usr/bin/env python3
"""
Environment Configuration Module for FlexXray Transcript Summarizer

This module centralizes all environment variable handling and provides
a clean interface for accessing configuration values throughout the application.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional, Dict, Any


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

    @property
    def max_quotes_for_analysis(self) -> int:
        """Get the maximum number of quotes to process in OpenAI analysis."""
        return int(os.getenv("MAX_QUOTES_FOR_ANALYSIS", "30"))

    @property
    def max_tokens_per_quote(self) -> int:
        """Get the estimated maximum tokens per quote for cost calculation."""
        return int(os.getenv("MAX_TOKENS_PER_QUOTE", "150"))

    @property
    def openai_model_for_summary(self) -> str:
        """Get the OpenAI model to use for summary generation."""
        return os.getenv("OPENAI_MODEL_FOR_SUMMARY", "gpt-4o")

    @property
    def model_token_limit(self) -> int:
        """Get the token limit for the configured OpenAI model."""
        model = self.openai_model_for_summary.lower()
        
        # Model-specific token limits (context window sizes)
        model_limits = {
            "gpt-4o": 128000,        # GPT-4o: 128k context
            "gpt-4o-mini": 128000,   # GPT-4o-mini: 128k context  
            "gpt-4": 8192,           # GPT-4: 8k context
            "gpt-4-32k": 32768,      # GPT-4-32k: 32k context
            "gpt-3.5-turbo": 16385,  # GPT-3.5-turbo: 16k context
        }
        
        # Get the limit for the configured model, default to conservative 6k if unknown
        return model_limits.get(model, 6000)

    @property
    def conservative_token_threshold(self) -> int:
        """Get the conservative token threshold for warnings (80% of model limit)."""
        return int(self.model_token_limit * 0.8)

    @property
    def enable_token_logging(self) -> bool:
        """Get whether to enable detailed token usage logging."""
        return os.getenv("ENABLE_TOKEN_LOGGING", "true").lower() in ("true", "1", "yes")

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

    def estimate_token_usage(self, quote_count: int, include_prompt: bool = True) -> Dict[str, Any]:
        """Estimate token usage for OpenAI API calls.
        
        Args:
            quote_count: Number of quotes to process
            include_prompt: Whether to include prompt tokens in estimation
            
        Returns:
            Dictionary with token estimates and cost information
        """
        # Base prompt tokens (approximate for company summary generation)
        base_prompt_tokens = 800 if include_prompt else 0
        
        # Estimate tokens per quote (including speaker, document, and quote text)
        estimated_quote_tokens = quote_count * self.max_tokens_per_quote
        
        # Total estimated tokens
        total_tokens = base_prompt_tokens + estimated_quote_tokens
        
        # Cost estimation (approximate, based on GPT-4 pricing)
        # GPT-4: $0.03 per 1K input tokens, $0.06 per 1K output tokens
        input_cost = (total_tokens / 1000) * 0.03
        output_cost = (total_tokens / 1000) * 0.06  # Assuming output is roughly same length
        total_cost = input_cost + output_cost
        
        return {
            "quote_count": quote_count,
            "base_prompt_tokens": base_prompt_tokens,
            "quote_tokens": estimated_quote_tokens,
            "total_tokens": total_tokens,
            "estimated_cost_usd": round(total_cost, 4),
            "model": self.openai_model_for_summary,
            "max_quotes_limit": self.max_quotes_for_analysis
        }

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
