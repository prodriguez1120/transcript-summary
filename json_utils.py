#!/usr/bin/env python3
"""
JSON Utilities Module for FlexXray Transcript Summarizer

This module provides robust JSON extraction and parsing utilities to replace
the complex JSON extraction logic in perspective_analysis.py.
"""

import json
import re
from typing import Any, Dict, List, Optional, Union
from exceptions import JSONParsingError


class JSONExtractor:
    """Robust JSON extraction from OpenAI API responses."""
    
    @staticmethod
    def extract_json_from_response(response_text: str) -> str:
        """Extract valid JSON from OpenAI response text using multiple strategies."""
        if not response_text or not response_text.strip():
            raise JSONParsingError("Empty response text")
        
        cleaned_text = JSONExtractor._clean_response_text(response_text)
        
        # Try extraction strategies in order of reliability
        strategies = [
            JSONExtractor._extract_balanced_json,
            JSONExtractor._extract_json_with_patterns,
            JSONExtractor._extract_json_with_fixes,
            JSONExtractor._extract_json_from_conversation
        ]
        
        for strategy in strategies:
            try:
                result = strategy(cleaned_text)
                if result:
                    return result
            except Exception:
                continue
        
        raise JSONParsingError("No valid JSON found in response after all extraction strategies")
    
    @staticmethod
    def _clean_response_text(text: str) -> str:
        """Clean up common formatting issues in response text."""
        cleaned = text.strip()
        
        # Remove markdown code blocks
        cleaned = re.sub(r'```json\s*', '', cleaned)
        cleaned = re.sub(r'\s*```', '', cleaned)
        
        # Remove common conversational prefixes
        conversational_patterns = [
            r'^Hello! How can I assist you today\?',
            r'^Hello! How can I help you today\?',
            r'^Hello! How can I help you\?',
            r'^Hello! How can I assist you\?',
            r'^Here is the analysis:',
            r'^Here is the response:',
            r'^Analysis:',
            r'^Response:',
            r'^JSON:',
            r'^Here is the JSON:'
        ]
        
        for pattern in conversational_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        return cleaned.strip()
    
    @staticmethod
    def _extract_balanced_json(text: str) -> Optional[str]:
        """Extract JSON by finding balanced braces/brackets."""
        # Find first opening character
        start_chars = ['{', '[']
        for start_char in start_chars:
            start_pos = text.find(start_char)
            if start_pos != -1:
                end_char = '}' if start_char == '{' else ']'
                json_text = JSONExtractor._extract_balanced_content(text, start_pos, start_char, end_char)
                if json_text and JSONExtractor._is_valid_json(json_text):
                    return json_text
        return None
    
    @staticmethod
    def _extract_balanced_content(text: str, start_pos: int, start_char: str, end_char: str) -> Optional[str]:
        """Extract content between balanced start and end characters."""
        count = 0
        for i in range(start_pos, len(text)):
            if text[i] == start_char:
                count += 1
            elif text[i] == end_char:
                count -= 1
                if count == 0:
                    return text[start_pos:i+1]
        return None
    
    @staticmethod
    def _extract_json_with_patterns(text: str) -> Optional[str]:
        """Extract JSON using regex patterns."""
        json_patterns = [
            r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # Nested objects
            r'\[[^\[\]]*(?:\{[^{}]*\}[^\[\]]*)*\]',  # Arrays with objects
            r'\{[^{}]*\}',  # Simple objects
            r'\[[^\[\]]*\]'   # Simple arrays
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                if JSONExtractor._is_valid_json(match):
                    return match
        return None
    
    @staticmethod
    def _extract_json_with_fixes(text: str) -> Optional[str]:
        """Extract JSON and apply common fixes."""
        if '{' in text or '[' in text:
            # Find potential JSON start
            for start_char in ['{', '[']:
                start_pos = text.find(start_char)
                if start_pos != -1:
                    # Try to extract and fix JSON
                    fixed_json = JSONExtractor._apply_common_fixes(text[start_pos:])
                    if fixed_json and JSONExtractor._is_valid_json(fixed_json):
                        return fixed_json
        return None
    
    @staticmethod
    def _apply_common_fixes(text: str) -> str:
        """Apply common JSON formatting fixes."""
        fixed = text
        
        # Remove trailing commas before closing brackets/braces
        fixed = re.sub(r',\s*([}\]])', r'\1', fixed)
        
        # Try to quote unquoted keys
        fixed = re.sub(r'([{[])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', fixed)
        
        # Try to find balanced content
        for start_char in ['{', '[']:
            if start_char in fixed:
                end_char = '}' if start_char == '{' else ']'
                balanced = JSONExtractor._extract_balanced_content(fixed, 0, start_char, end_char)
                if balanced:
                    return balanced
        
        return fixed
    
    @staticmethod
    def _extract_json_from_conversation(text: str) -> Optional[str]:
        """Extract JSON from conversational responses."""
        json_start_patterns = [
            r'Here is the JSON:?\s*(\{.*\}|\[.*\])',
            r'Here is the response:?\s*(\{.*\}|\[.*\])',
            r'Here is the analysis:?\s*(\{.*\}|\[.*\])',
            r'JSON:?\s*(\{.*\}|\[.*\])',
            r'Response:?\s*(\{.*\}|\[.*\])',
            r'Analysis:?\s*(\{.*\}|\[.*\])'
        ]
        
        for pattern in json_start_patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            for match in matches:
                if JSONExtractor._is_valid_json(match):
                    return match
        return None
    
    @staticmethod
    def _is_valid_json(text: str) -> bool:
        """Check if text is valid JSON."""
        try:
            json.loads(text)
            return True
        except (json.JSONDecodeError, ValueError):
            return False


class JSONParser:
    """Enhanced JSON parsing with validation and error handling."""
    
    @staticmethod
    def parse_json_safe(json_text: str, context: str = "JSON parsing") -> Any:
        """Safely parse JSON with detailed error reporting."""
        try:
            return json.loads(json_text)
        except json.JSONDecodeError as e:
            raise JSONParsingError(
                f"Failed to parse JSON in {context}",
                f"JSONDecodeError: {e.msg} at line {e.lineno}, column {e.colno}",
                e
            )
        except Exception as e:
            raise JSONParsingError(f"Unexpected error parsing JSON in {context}", str(e), e)
    
    @staticmethod
    def validate_json_structure(data: Any, expected_type: type, context: str = "JSON validation") -> Any:
        """Validate that JSON data has the expected type."""
        if not isinstance(data, expected_type):
            raise JSONParsingError(
                f"Invalid JSON structure in {context}",
                f"Expected {expected_type.__name__}, got {type(data).__name__}",
                None
            )
        return data
    
    @staticmethod
    def extract_and_validate_quotes_ranking(response_text: str, quotes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract and validate quote ranking JSON from OpenAI response."""
        try:
            # Extract JSON from response
            json_text = JSONExtractor.extract_json_from_response(response_text)
            
            # Parse JSON
            rankings = JSONParser.parse_json_safe(json_text, "quote ranking response")
            
            # Validate structure
            if not isinstance(rankings, list):
                rankings = [rankings]
            
            # Validate each ranking entry
            validated_rankings = []
            for i, ranking in enumerate(rankings):
                if not isinstance(ranking, dict):
                    continue
                
                # Check required fields
                if 'quote_index' not in ranking:
                    continue
                
                quote_index = ranking.get('quote_index', 0) - 1  # Convert to 0-based
                if 0 <= quote_index < len(quotes):
                    validated_ranking = {
                        'quote_index': quote_index,
                        'relevance_score': ranking.get('relevance_score', 0),
                        'relevance_explanation': ranking.get('relevance_explanation', ''),
                        'key_insight': ranking.get('key_insight', '')
                    }
                    validated_rankings.append(validated_ranking)
            
            return validated_rankings
            
        except Exception as e:
            raise JSONParsingError(
                "Failed to extract and validate quote rankings",
                str(e),
                e
            )
    
    @staticmethod
    def extract_and_validate_themes(response_text: str) -> List[Dict[str, Any]]:
        """Extract and validate themes JSON from OpenAI response."""
        try:
            # Extract JSON from response
            json_text = JSONExtractor.extract_json_from_response(response_text)
            
            # Parse JSON
            themes = JSONParser.parse_json_safe(json_text, "themes response")
            
            # Validate structure
            if not isinstance(themes, list):
                themes = [themes]
            
            # Validate each theme
            validated_themes = []
            for theme in themes:
                if isinstance(theme, dict) and 'name' in theme:
                    validated_theme = {
                        'name': theme.get('name', 'Unknown Theme'),
                        'description': theme.get('description', ''),
                        'key_insights': theme.get('key_insights', []),
                        'max_quotes': theme.get('max_quotes', 4)
                    }
                    validated_themes.append(validated_theme)
            
            return validated_themes
            
        except Exception as e:
            raise JSONParsingError(
                "Failed to extract and validate themes",
                str(e),
                e
            )


# Convenience functions for backward compatibility
def extract_json_from_response(response_text: str) -> str:
    """Extract JSON from OpenAI response text."""
    return JSONExtractor.extract_json_from_response(response_text)


def parse_json_safe(json_text: str, context: str = "JSON parsing") -> Any:
    """Safely parse JSON with error handling."""
    return JSONParser.parse_json_safe(json_text, context)
