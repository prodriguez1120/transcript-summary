#!/usr/bin/env python3
"""
Theme Analysis Module for FlexXray Transcripts

This module handles thematic clustering and cross-transcript insights.
Extracted from perspective_analysis.py to provide focused theme analysis functionality.
"""

import json
import re
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
from prompt_config import get_prompt_config


class ThemeAnalyzer:
    """Handles thematic clustering and cross-transcript insights."""
    
    def __init__(self, api_key: str):
        """Initialize the theme analyzer with OpenAI API key."""
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)
        self.logger = logging.getLogger(__name__)

    def identify_themes_with_openai(
        self, perspective_key: str, perspective_data: dict, quotes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify themes using OpenAI analysis."""
        if not quotes:
            return []

        self.logger.info(f"Identifying themes for {perspective_key} using OpenAI...")

        # Get prompt configuration
        prompt_config = get_prompt_config()

        # Create theme identification prompt
        quotes_list = ""
        for i, quote in enumerate(
            quotes[:20]
        ):  # Limit to first 20 quotes for theme analysis
            quotes_list += f"\nQuote {i+1}: {quote.get('text', '')[:150]}..."

        prompt = prompt_config.format_prompt(
            "theme_identification",
            perspective_title=perspective_data["title"],
            quotes_list=quotes_list,
        )

        try:
            # Get OpenAI parameters from config
            params = prompt_config.get_prompt_parameters("theme_identification")

            response = self.client.chat.completions.create(
                model=params.get("model", "gpt-4"),
                messages=[
                    {
                        "role": "system",
                        "content": prompt_config.get_system_message(
                            "theme_identification"
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=params.get("temperature", 0.3),
                max_tokens=params.get("max_tokens", 1500),
            )

            # Parse themes
            response_content = response.choices[0].message.content
            if response_content:
                themes = self._parse_themes_response(response_content)
            else:
                self.logger.warning("Empty response from OpenAI")
                themes = self._get_default_themes(perspective_data)
            
            if themes:
                self.logger.info(f"Successfully identified {len(themes)} themes")
                return themes
            else:
                self.logger.warning("No themes identified from OpenAI response")
                return self._get_default_themes(perspective_data)

        except Exception as e:
            self.logger.error(f"Error identifying themes with OpenAI: {e}")
            # Return default themes
            return self._get_default_themes(perspective_data)

    def _parse_themes_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse OpenAI's themes response."""
        try:
            # Extract JSON from response using robust extraction
            json_text = self._extract_json_from_response(response_text)

            # Parse the JSON
            themes = json.loads(json_text)

            # Handle both array and single object responses
            if not isinstance(themes, list):
                themes = [themes]

            # Validate themes
            valid_themes = []
            for theme in themes:
                if isinstance(theme, dict) and "name" in theme:
                    valid_theme = {
                        "name": theme.get("name", "Unknown Theme"),
                        "description": theme.get("description", ""),
                        "key_insights": theme.get("key_insights", []),
                        "max_quotes": theme.get("max_quotes", 4),
                        "theme_id": theme.get("theme_id", f"theme_{len(valid_themes) + 1}"),
                        "confidence_score": theme.get("confidence_score", 0.8),
                        "cross_transcript_insights": theme.get("cross_transcript_insights", []),
                    }
                    valid_themes.append(valid_theme)

            self.logger.info(f"Successfully parsed {len(valid_themes)} valid themes")
            return valid_themes

        except Exception as e:
            self.logger.error(f"Error parsing themes response: {e}")
            return []

    def _extract_json_from_response(self, response_text: str) -> str:
        """Extract JSON from OpenAI response text."""
        # Try to find JSON content
        json_patterns = [
            r"```json\s*([\s\S]*?)\s*```",  # JSON code blocks
            r"```\s*([\s\S]*?)\s*```",      # Generic code blocks
            r"\{[\s\S]*\}",                  # JSON object
            r"\[[\s\S]*\]",                  # JSON array
        ]

        for pattern in json_patterns:
            matches = re.findall(pattern, response_text)
            if matches:
                return matches[0]

        # If no patterns match, try to find JSON-like content
        lines = response_text.split("\n")
        json_lines = []
        in_json = False

        for line in lines:
            if "{" in line or "[" in line:
                in_json = True
            if in_json:
                json_lines.append(line)
            if "}" in line or "]" in line:
                break

        if json_lines:
            return "\n".join(json_lines)

        # Last resort - return the entire response
        return response_text

    def _get_default_themes(self, perspective_data: dict) -> List[Dict[str, Any]]:
        """Get default themes when OpenAI analysis fails."""
        self.logger.info("Using default themes due to OpenAI failure")
        
        default_themes = [
            {
                "name": "Key Insights",
                "description": "Primary insights from the perspective",
                "key_insights": ["Analysis completed"],
                "max_quotes": 4,
                "theme_id": "default_key_insights",
                "confidence_score": 0.5,
                "cross_transcript_insights": [],
            }
        ]
        
        return default_themes

    def select_quotes_for_theme(
        self, theme_name: str, quotes: List[Dict[str, Any]], max_quotes: int
    ) -> List[Dict[str, Any]]:
        """Select quotes for a specific theme."""
        if not quotes:
            return []

        self.logger.info(f"Selecting quotes for theme: {theme_name}")

        # Filter quotes that might be relevant to this theme
        relevant_quotes = []
        for quote in quotes:
            quote_text = quote.get("text", "").lower()
            theme_lower = theme_name.lower()

            # Simple relevance scoring
            relevance_score = self._calculate_theme_relevance(quote_text, theme_lower)

            if relevance_score > 0:
                quote_copy = quote.copy()
                quote_copy["theme_relevance"] = relevance_score
                quote_copy["theme_name"] = theme_name
                # Ensure selection stage is set if not already present
                if not quote_copy.get("selection_stage"):
                    quote_copy["selection_stage"] = "theme_selected"
                relevant_quotes.append(quote_copy)

        # Sort by theme relevance and take top quotes
        relevant_quotes.sort(key=lambda x: x.get("theme_relevance", 0), reverse=True)
        selected_quotes = relevant_quotes[:max_quotes]
        
        self.logger.info(f"Selected {len(selected_quotes)} quotes for theme '{theme_name}'")
        return selected_quotes

    def _calculate_theme_relevance(self, quote_text: str, theme_name: str) -> float:
        """Calculate relevance score between quote text and theme name."""
        theme_words = theme_name.lower().split()
        relevance_score = 0.0
        
        # Count exact word matches
        for word in theme_words:
            if len(word) > 2:  # Only consider words longer than 2 characters
                if word in quote_text:
                    relevance_score += 1.0
                
                # Also check for partial matches and synonyms
                if self._check_partial_match(word, quote_text):
                    relevance_score += 0.5

        # Normalize score
        if theme_words:
            relevance_score = relevance_score / len(theme_words)
        
        return relevance_score

    def _check_partial_match(self, word: str, text: str) -> bool:
        """Check for partial word matches and synonyms."""
        # Common business synonyms and related terms
        synonyms = {
            "market": ["marketplace", "demand", "position", "share"],
            "customer": ["client", "user", "buyer", "consumer"],
            "technology": ["tech", "innovation", "digital", "solution"],
            "business": ["company", "enterprise", "operation", "strategy"],
            "growth": ["expansion", "development", "increase", "scaling"],
            "risk": ["challenge", "concern", "issue", "threat"],
            "quality": ["excellence", "standard", "performance", "reliability"],
        }
        
        if word in synonyms:
            for synonym in synonyms[word]:
                if synonym in text:
                    return True
        
        # Check for partial matches (e.g., "tech" in "technology")
        for text_word in text.split():
            if word in text_word or text_word in word:
                return True
        
        return False

    def analyze_cross_transcript_insights(
        self, themes: List[Dict[str, Any]], all_quotes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Analyze insights that appear across multiple transcripts."""
        self.logger.info("Analyzing cross-transcript insights...")
        
        cross_transcript_themes = []
        
        for theme in themes:
            theme_quotes = [q for q in all_quotes if q.get("theme_name") == theme["name"]]
            
            if not theme_quotes:
                continue
            
            # Group quotes by transcript
            transcript_groups = {}
            for quote in theme_quotes:
                transcript_name = quote.get("transcript_name", "Unknown")
                if transcript_name not in transcript_groups:
                    transcript_groups[transcript_name] = []
                transcript_groups[transcript_name].append(quote)
            
            # Analyze cross-transcript patterns
            if len(transcript_groups) > 1:
                cross_insights = self._identify_cross_transcript_patterns(
                    theme, transcript_groups
                )
                
                theme_copy = theme.copy()
                theme_copy["cross_transcript_insights"] = cross_insights
                theme_copy["transcript_coverage"] = len(transcript_groups)
                cross_transcript_themes.append(theme_copy)
        
        self.logger.info(f"Identified {len(cross_transcript_themes)} themes with cross-transcript insights")
        return cross_transcript_themes

    def _identify_cross_transcript_patterns(
        self, theme: Dict[str, Any], transcript_groups: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Identify patterns that appear across multiple transcripts."""
        cross_insights = []
        
        # Look for common keywords and concepts across transcripts
        all_theme_quotes = []
        for quotes in transcript_groups.values():
            all_theme_quotes.extend(quotes)
        
        # Extract common terms
        common_terms = self._extract_common_terms(all_theme_quotes)
        
        # Analyze sentiment patterns
        sentiment_patterns = self._analyze_sentiment_patterns(all_theme_quotes)
        
        # Look for consensus vs. disagreement
        consensus_analysis = self._analyze_consensus_patterns(transcript_groups)
        
        cross_insights = [
            {
                "type": "common_terms",
                "description": "Terms frequently mentioned across transcripts",
                "data": common_terms,
            },
            {
                "type": "sentiment_patterns",
                "description": "Sentiment patterns across transcripts",
                "data": sentiment_patterns,
            },
            {
                "type": "consensus_analysis",
                "description": "Areas of agreement and disagreement",
                "data": consensus_analysis,
            },
        ]
        
        return cross_insights

    def _extract_common_terms(self, quotes: List[Dict[str, Any]]) -> List[str]:
        """Extract common terms from theme quotes."""
        term_frequency = {}
        
        for quote in quotes:
            text = quote.get("text", "").lower()
            words = re.findall(r'\b\w+\b', text)
            
            for word in words:
                if len(word) > 3:  # Only consider words longer than 3 characters
                    term_frequency[word] = term_frequency.get(word, 0) + 1
        
        # Get most frequent terms
        sorted_terms = sorted(term_frequency.items(), key=lambda x: x[1], reverse=True)
        common_terms = [term for term, count in sorted_terms[:10] if count > 1]
        
        return common_terms

    def _analyze_sentiment_patterns(self, quotes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment patterns in theme quotes."""
        positive_indicators = ["positive", "good", "great", "excellent", "strong", "benefit", "advantage"]
        negative_indicators = ["negative", "bad", "poor", "weak", "risk", "challenge", "problem"]
        
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for quote in quotes:
            text = quote.get("text", "").lower()
            
            positive_matches = sum(1 for indicator in positive_indicators if indicator in text)
            negative_matches = sum(1 for indicator in negative_indicators if indicator in text)
            
            if positive_matches > negative_matches:
                positive_count += 1
            elif negative_matches > positive_matches:
                negative_count += 1
            else:
                neutral_count += 1
        
        total = len(quotes)
        if total == 0:
            return {"positive": 0, "negative": 0, "neutral": 0}
        
        return {
            "positive": positive_count / total,
            "negative": negative_count / total,
            "neutral": neutral_count / total,
            "total_quotes": total,
        }

    def _analyze_consensus_patterns(
        self, transcript_groups: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Analyze consensus patterns across transcripts."""
        if len(transcript_groups) < 2:
            return {"consensus_level": "insufficient_data"}
        
        # Look for common themes and divergent opinions
        all_quotes = []
        for quotes in transcript_groups.values():
            all_quotes.extend(quotes)
        
        # Simple consensus analysis based on common terms
        common_terms = self._extract_common_terms(all_quotes)
        
        consensus_score = len(common_terms) / 10.0  # Normalize to 0-1 scale
        
        if consensus_score > 0.7:
            consensus_level = "high"
        elif consensus_score > 0.4:
            consensus_level = "medium"
        else:
            consensus_level = "low"
        
        return {
            "consensus_level": consensus_level,
            "consensus_score": consensus_score,
            "common_terms": common_terms,
            "transcript_count": len(transcript_groups),
        }

    def get_theme_statistics(self, themes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about theme analysis results."""
        if not themes:
            return {
                "total_themes": 0,
                "average_confidence": 0.0,
                "cross_transcript_coverage": 0.0,
                "total_quotes_analyzed": 0,
            }

        stats = {
            "total_themes": len(themes),
            "average_confidence": 0.0,
            "cross_transcript_coverage": 0.0,
            "total_quotes_analyzed": 0,
            "theme_details": [],
        }

        total_confidence = 0.0
        cross_transcript_count = 0

        for theme in themes:
            confidence = theme.get("confidence_score", 0.0)
            total_confidence += confidence
            
            if theme.get("cross_transcript_insights"):
                cross_transcript_count += 1
            
            theme_detail = {
                "name": theme.get("name", "Unknown"),
                "confidence": confidence,
                "max_quotes": theme.get("max_quotes", 0),
                "has_cross_transcript_insights": bool(theme.get("cross_transcript_insights")),
            }
            stats["theme_details"].append(theme_detail)

        if stats["total_themes"] > 0:
            stats["average_confidence"] = total_confidence / stats["total_themes"]
            stats["cross_transcript_coverage"] = cross_transcript_count / stats["total_themes"]

        return stats
