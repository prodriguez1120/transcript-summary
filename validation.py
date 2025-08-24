#!/usr/bin/env python3
"""
Input Validation Module for FlexXray Transcript Summarizer

This module provides comprehensive input validation for all major functions
and data structures used throughout the application.
"""

import os
import re
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
from exceptions import (
    InputValidationError,
    QuoteValidationError,
    ConfigurationError,
    DocumentValidationError,
)


class InputValidator:
    """Centralized input validation for the FlexXray application."""

    @staticmethod
    def validate_file_path(
        file_path: str,
        must_exist: bool = True,
        allowed_extensions: Optional[List[str]] = None,
    ) -> str:
        """Validate a file path."""
        if not file_path or not isinstance(file_path, str):
            raise InputValidationError("File path must be a non-empty string")

        if must_exist and not os.path.exists(file_path):
            raise InputValidationError(f"File does not exist: {file_path}")

        if allowed_extensions:
            file_ext = Path(file_path).suffix.lower()
            if file_ext not in [ext.lower() for ext in allowed_extensions]:
                raise InputValidationError(
                    f"File extension {file_ext} not allowed. Allowed: {allowed_extensions}"
                )

        return file_path

    @staticmethod
    def validate_directory_path(
        dir_path: str, must_exist: bool = True, create_if_missing: bool = False
    ) -> str:
        """Validate a directory path."""
        if not dir_path or not isinstance(dir_path, str):
            raise InputValidationError("Directory path must be a non-empty string")

        if must_exist and not os.path.isdir(dir_path):
            if create_if_missing:
                try:
                    os.makedirs(dir_path, exist_ok=True)
                except Exception as e:
                    raise InputValidationError(
                        f"Cannot create directory {dir_path}: {e}"
                    )
            else:
                raise InputValidationError(f"Directory does not exist: {dir_path}")

        return dir_path

    @staticmethod
    def validate_api_key(api_key: str) -> str:
        """Validate OpenAI API key format."""
        if not api_key or not isinstance(api_key, str):
            raise InputValidationError("API key must be a non-empty string")

        if not api_key.startswith("sk-"):
            raise InputValidationError("API key must start with 'sk-'")

        if len(api_key) < 10:
            raise InputValidationError("API key appears to be too short")

        return api_key

    @staticmethod
    def validate_text_content(
        text: str, min_length: int = 1, max_length: Optional[int] = None
    ) -> str:
        """Validate text content."""
        if not text or not isinstance(text, str):
            raise InputValidationError("Text must be a non-empty string")

        if len(text.strip()) < min_length:
            raise InputValidationError(
                f"Text must be at least {min_length} characters long"
            )

        if max_length and len(text) > max_length:
            raise InputValidationError(
                f"Text must be no more than {max_length} characters long"
            )

        return text.strip()

    @staticmethod
    def validate_quote_data(quote: Dict[str, Any]) -> Dict[str, Any]:
        """Validate quote data structure."""
        if not isinstance(quote, dict):
            raise QuoteValidationError("Quote must be a dictionary")

        required_fields = ["text", "speaker_role"]
        for field in required_fields:
            if field not in quote:
                raise QuoteValidationError(f"Quote missing required field: {field}")

        # Validate text content
        if not quote["text"] or not isinstance(quote["text"], str):
            raise QuoteValidationError("Quote text must be a non-empty string")

        # Validate speaker role
        valid_roles = ["expert", "interviewer", "unknown"]
        if quote["speaker_role"] not in valid_roles:
            raise QuoteValidationError(
                f"Invalid speaker role: {quote['speaker_role']}. Valid: {valid_roles}"
            )

        # Validate optional fields if present
        if "transcript_name" in quote and not isinstance(quote["transcript_name"], str):
            raise QuoteValidationError("transcript_name must be a string")

        if "position" in quote and not isinstance(quote["position"], (int, float)):
            raise QuoteValidationError("position must be a number")

        return quote

    @staticmethod
    def validate_quotes_list(quotes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate a list of quotes."""
        if not isinstance(quotes, list):
            raise QuoteValidationError("Quotes must be a list")

        if not quotes:
            return quotes  # Empty list is valid

        validated_quotes = []
        for i, quote in enumerate(quotes):
            try:
                validated_quote = InputValidator.validate_quote_data(quote)
                validated_quotes.append(validated_quote)
            except QuoteValidationError as e:
                raise QuoteValidationError(f"Quote at index {i} is invalid: {e}")

        return validated_quotes

    @staticmethod
    def validate_perspective_data(perspective: Dict[str, Any]) -> Dict[str, Any]:
        """Validate perspective data structure."""
        if not isinstance(perspective, dict):
            raise InputValidationError("Perspective must be a dictionary")

        required_fields = ["title", "description", "focus_areas"]
        for field in required_fields:
            if field not in perspective:
                raise InputValidationError(
                    f"Perspective missing required field: {field}"
                )

        # Validate title
        if (
            not isinstance(perspective["title"], str)
            or not perspective["title"].strip()
        ):
            raise InputValidationError("Perspective title must be a non-empty string")

        # Validate description
        if (
            not isinstance(perspective["description"], str)
            or not perspective["description"].strip()
        ):
            raise InputValidationError(
                "Perspective description must be a non-empty string"
            )

        # Validate focus areas
        if not isinstance(perspective["focus_areas"], list):
            raise InputValidationError("Focus areas must be a list")

        if not perspective["focus_areas"]:
            raise InputValidationError("Focus areas cannot be empty")

        for i, focus_area in enumerate(perspective["focus_areas"]):
            if not isinstance(focus_area, str) or not focus_area.strip():
                raise InputValidationError(
                    f"Focus area at index {i} must be a non-empty string"
                )

        return perspective

    @staticmethod
    def validate_search_parameters(
        query: str,
        n_results: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> tuple:
        """Validate search parameters."""
        if not query or not isinstance(query, str):
            raise InputValidationError("Search query must be a non-empty string")

        if not isinstance(n_results, int) or n_results < 1:
            raise InputValidationError("n_results must be a positive integer")

        if n_results > 100:
            raise InputValidationError("n_results cannot exceed 100")

        if filter_metadata is not None and not isinstance(filter_metadata, dict):
            raise InputValidationError("filter_metadata must be a dictionary or None")

        return query, n_results, filter_metadata

    @staticmethod
    def validate_batch_size(batch_size: int) -> int:
        """Validate batch size for operations."""
        if not isinstance(batch_size, int) or batch_size < 1:
            raise InputValidationError("Batch size must be a positive integer")

        if batch_size > 1000:
            raise InputValidationError("Batch size cannot exceed 1000")

        return batch_size

    @staticmethod
    def validate_model_parameters(
        model: str, temperature: float, max_tokens: int
    ) -> tuple:
        """Validate OpenAI model parameters."""
        valid_models = ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"]
        if model not in valid_models:
            raise InputValidationError(f"Invalid model: {model}. Valid: {valid_models}")

        if (
            not isinstance(temperature, (int, float))
            or temperature < 0
            or temperature > 2
        ):
            raise InputValidationError("Temperature must be a number between 0 and 2")

        if not isinstance(max_tokens, int) or max_tokens < 1:
            raise InputValidationError("max_tokens must be a positive integer")

        if max_tokens > 8000:
            raise InputValidationError("max_tokens cannot exceed 8000")

        return model, temperature, max_tokens


class DocumentValidator:
    """Specialized validation for document-related operations."""

    @staticmethod
    def validate_document_format(file_path: str) -> str:
        """Validate document format and extension."""
        allowed_extensions = [".docx", ".doc", ".txt", ".pdf"]
        return InputValidator.validate_file_path(
            file_path, must_exist=True, allowed_extensions=allowed_extensions
        )

    @staticmethod
    def validate_transcript_name(name: str) -> str:
        """Validate transcript name format."""
        if not name or not isinstance(name, str):
            raise DocumentValidationError("Transcript name must be a non-empty string")

        # Remove any file extensions
        name = Path(name).stem

        if len(name.strip()) < 3:
            raise DocumentValidationError(
                "Transcript name must be at least 3 characters long"
            )

        return name.strip()


class ConfigurationValidator:
    """Specialized validation for configuration data."""

    @staticmethod
    def validate_prompt_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate prompt configuration structure."""
        if not isinstance(config, dict):
            raise ConfigurationError("Prompt configuration must be a dictionary")

        required_sections = ["system_messages", "quote_ranking", "theme_identification"]
        for section in required_sections:
            if section not in config:
                raise ConfigurationError(
                    f"Prompt configuration missing required section: {section}"
                )

        return config

    @staticmethod
    def validate_environment_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate environment configuration."""
        if not isinstance(config, dict):
            raise ConfigurationError("Environment configuration must be a dictionary")

        required_keys = ["OPENAI_API_KEY"]
        for key in required_keys:
            if key not in config or not config[key]:
                raise ConfigurationError(
                    f"Environment configuration missing required key: {key}"
                )

        return config


# Convenience functions for common validations
def validate_input(func):
    """Decorator to automatically validate function inputs based on type hints."""

    def wrapper(*args, **kwargs):
        # This is a simplified version - in practice, you'd want more sophisticated
        # type checking based on the function's signature
        return func(*args, **kwargs)

    return wrapper


def safe_validate(validator_func, *args, **kwargs):
    """Safely run validation and return None if validation fails."""
    try:
        return validator_func(*args, **kwargs)
    except Exception:
        return None
