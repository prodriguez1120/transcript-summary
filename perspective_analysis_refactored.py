#!/usr/bin/env python3
"""
Refactored Perspective Analysis Module for FlexXray Transcripts

This module now integrates with the new modular components:
- quote_ranking.py: OpenAI-driven ranking & scoring
- theme_analysis.py: Thematic clustering and cross-transcript insights  
- batch_manager.py: Batching, token handling, and retries

The original functionality is preserved while leveraging the new modular architecture.
"""

import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI

# Import the new modular components
from quote_ranking import QuoteRanker
from theme_analysis import ThemeAnalyzer
from batch_manager import BatchManager, BatchConfig


class PerspectiveAnalyzer:
    """Refactored perspective analyzer using modular components."""
    
    def __init__(self, api_key: str):
        """Initialize the perspective analyzer with OpenAI API key."""
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)
        self.vector_db_manager = None  # Will be set by the main tool
        self.logger = logging.getLogger(__name__)

        # Initialize modular components
        self.quote_ranker = QuoteRanker(api_key)
        self.theme_analyzer = ThemeAnalyzer(api_key)
        
        # Initialize batch manager with default configuration
        batch_config = BatchConfig(
            batch_size=20,
            batch_delay=1.5,
            failure_delay=3.0,
            max_retries=3,
            enable_batch_processing=True,
            max_quotes_per_perspective=200
        )
        self.batch_manager = BatchManager(batch_config)

    def set_vector_db_manager(self, vector_db_manager):
        """Set the vector database manager for RAG functionality."""
        self.vector_db_manager = vector_db_manager
        if vector_db_manager:
            self.logger.info("Vector database manager connected for RAG functionality")
        else:
            self.logger.info("Vector database manager disconnected")

    def configure_batch_processing(
        self,
        batch_size: Optional[int] = None,
        batch_delay: Optional[float] = None,
        failure_delay: Optional[float] = None,
        max_retries: Optional[int] = None,
        max_quotes: Optional[int] = None,
        enable: Optional[bool] = None,
    ):
        """Configure batch processing parameters using the batch manager."""
        self.batch_manager.configure_batch_processing(
            batch_size=batch_size,
            batch_delay=batch_delay,
            failure_delay=failure_delay,
            max_retries=max_retries,
            max_quotes=max_quotes,
            enable=enable,
        )

    def analyze_perspective_with_quotes(
        self,
        perspective_key: str,
        perspective_data: dict,
        all_quotes: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Analyze a perspective using available quotes with OpenAI ranking."""
        self.logger.info(f"Analyzing perspective: {perspective_data['title']}")

        # Find relevant quotes for this perspective
        relevant_quotes = self._find_relevant_quotes_for_perspective(
            perspective_key, perspective_data, all_quotes
        )

        if not relevant_quotes:
            self.logger.warning(f"No relevant quotes found for {perspective_key}")
            return self._create_empty_perspective_result(perspective_data)

        # Limit quotes based on configuration
        max_quotes = self.batch_manager.config.max_quotes_per_perspective
        if len(relevant_quotes) > max_quotes:
            self.logger.info(f"Limiting quotes from {len(relevant_quotes)} to {max_quotes}")
            relevant_quotes = relevant_quotes[:max_quotes]

        # Rank quotes using the quote ranker
        self.logger.info(f"Ranking {len(relevant_quotes)} quotes for {perspective_key}")
        ranked_quotes = self.quote_ranker.rank_quotes_with_openai(
            perspective_key, perspective_data, relevant_quotes
        )

        if not ranked_quotes:
            self.logger.warning(f"No quotes ranked for {perspective_key}")
            return self._create_empty_perspective_result(perspective_data)

        # Identify themes using the theme analyzer
        self.logger.info(f"Identifying themes for {perspective_key}")
        themes = self.theme_analyzer.identify_themes_with_openai(
            perspective_key, perspective_data, ranked_quotes
        )

        # Select quotes for each theme
        themes_with_quotes = []
        for theme in themes:
            theme_quotes = self.theme_analyzer.select_quotes_for_theme(
                theme["name"], ranked_quotes, theme.get("max_quotes", 4)
            )
            
            theme_copy = theme.copy()
            theme_copy["quotes"] = theme_quotes
            themes_with_quotes.append(theme_copy)

        # Analyze cross-transcript insights
        cross_transcript_themes = self.theme_analyzer.analyze_cross_transcript_insights(
            themes_with_quotes, all_quotes
        )

        # Create the final result
        result = {
            "perspective_key": perspective_key,
            "title": perspective_data["title"],
            "description": perspective_data.get("description", ""),
            "focus_areas": perspective_data.get("focus_areas", []),
            "ranked_quotes": ranked_quotes,
            "themes": themes_with_quotes,
            "cross_transcript_insights": cross_transcript_themes,
            "analysis_metadata": {
                "total_quotes_analyzed": len(relevant_quotes),
                "quotes_ranked": len(ranked_quotes),
                "themes_identified": len(themes),
                "cross_transcript_themes": len(cross_transcript_themes),
            }
        }

        self.logger.info(f"Perspective analysis completed for {perspective_key}")
        return result

    def _find_relevant_quotes_for_perspective(
        self,
        perspective_key: str,
        perspective_data: dict,
        all_quotes: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Find quotes relevant to a specific perspective using vector database semantic search (RAG)."""
        if not all_quotes:
            return []

        # Get focus areas for this perspective
        focus_areas = perspective_data.get("focus_areas", [])

        if not focus_areas:
            self.logger.warning(f"No focus areas defined for perspective: {perspective_key}")
            return []

        # Expand focus areas for better coverage
        expanded_focus_areas = self._expand_focus_areas(focus_areas)

        # Use vector database semantic search for better quote retrieval
        relevant_quotes = []

        try:
            # Try to use vector database for semantic search if available
            if (
                hasattr(self, "vector_db_manager")
                and self.vector_db_manager
                and self.vector_db_manager.quotes_collection
            ):
                self.logger.info(f"Using vector database semantic search for {perspective_key}...")

                # Search for each focus area and combine results
                for focus_area in expanded_focus_areas:
                    # Use semantic search to find relevant quotes
                    search_results = self.vector_db_manager.semantic_search_quotes(
                        query=focus_area,
                        n_results=20,  # Increased from 15 to 20 for better coverage
                        filter_metadata={
                            "speaker_role": "expert"
                        },  # Only expert quotes
                    )

                    # Process and deduplicate results
                    for result in search_results:
                        # Check if we already have this quote (by ID or text)
                        quote_id = result.get("id")
                        quote_text = result.get("text", "")

                        # Skip if we already have this quote
                        if any(
                            q.get("id") == quote_id or q.get("text") == quote_text
                            for q in relevant_quotes
                        ):
                            continue

                        # Calculate relevance score based on focus area match
                        relevance_score = self._calculate_focus_area_relevance(
                            quote_text, focus_area
                        )

                        # Create quote object with metadata
                        quote = {
                            "text": quote_text,
                            "speaker_role": "expert",
                            "transcript_name": result.get("metadata", {}).get(
                                "transcript_name", "Unknown"
                            ),
                            "position": result.get("metadata", {}).get("position", 0),
                            "has_insight": True,
                            "relevance_score": relevance_score,
                            "focus_area_matched": focus_area,
                            "vector_distance": result.get("distance", 0),
                            "id": quote_id,
                            "metadata": result.get("metadata", {}),
                        }

                        relevant_quotes.append(quote)

                self.logger.info(
                    f"Vector database search found {len(relevant_quotes)} relevant quotes"
                )

            else:
                # Fallback to local filtering if vector database not available
                self.logger.info(
                    f"Vector database not available, using local filtering for {perspective_key}..."
                )
                relevant_quotes = self._fallback_local_filtering(
                    all_quotes, focus_areas
                )

        except Exception as e:
            self.logger.error(f"Error using vector database search: {e}")
            self.logger.info("Falling back to local filtering...")
            relevant_quotes = self._fallback_local_filtering(all_quotes, focus_areas)

        # Sort by relevance score and limit results
        relevant_quotes.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

        return relevant_quotes

    def _expand_focus_areas(self, focus_areas: List[str]) -> List[str]:
        """Expand focus areas with related terms for better quote coverage."""
        expanded_areas = focus_areas.copy()

        # Define related terms for common business concepts
        focus_expansions = {
            "market": [
                "market",
                "marketplace",
                "market demand",
                "market size",
                "market share",
                "market position",
            ],
            "customer": [
                "customer",
                "client",
                "user",
                "buyer",
                "consumer",
                "customer satisfaction",
                "customer needs",
            ],
            "technology": [
                "technology",
                "tech",
                "innovation",
                "digital",
                "software",
                "platform",
                "solution",
            ],
            "business": [
                "business",
                "company",
                "enterprise",
                "operation",
                "strategy",
                "model",
                "approach",
            ],
            "growth": [
                "growth",
                "expansion",
                "development",
                "increase",
                "scaling",
                "progress",
                "advancement",
            ],
            "risk": [
                "risk",
                "challenge",
                "concern",
                "issue",
                "problem",
                "threat",
                "vulnerability",
            ],
            "quality": [
                "quality",
                "excellence",
                "standard",
                "performance",
                "reliability",
                "consistency",
                "accuracy",
            ],
        }

        # Expand each focus area
        for area in focus_areas:
            area_lower = area.lower()
            for key, expansions in focus_expansions.items():
                if key in area_lower:
                    for expansion in expansions:
                        if expansion not in expanded_areas:
                            expanded_areas.append(expansion)

        self.logger.info(
            f"Expanded focus areas from {len(focus_areas)} to {len(expanded_areas)} for better coverage"
        )
        return expanded_areas

    def _calculate_focus_area_relevance(self, quote_text: str, focus_area: str) -> float:
        """Calculate relevance score between quote text and focus area."""
        quote_lower = quote_text.lower()
        focus_lower = focus_area.lower()

        # Simple keyword matching with scoring
        relevance_score = 0.0
        focus_words = focus_lower.split()

        for word in focus_words:
            if len(word) > 2:  # Only consider words longer than 2 characters
                if word in quote_lower:
                    relevance_score += 1.0
                
                # Also check for partial matches
                if self._check_partial_match(word, quote_lower):
                    relevance_score += 0.5

        # Normalize score
        if focus_words:
            relevance_score = relevance_score / len(focus_words)
        
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
            "risk": ["challenge", "concern", "issue", "problem", "threat"],
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

    def _fallback_local_filtering(
        self, all_quotes: List[Dict[str, Any]], focus_areas: List[str]
    ) -> List[Dict[str, Any]]:
        """Fallback to local filtering when vector database is not available."""
        self.logger.info("Using local filtering fallback")
        
        relevant_quotes = []
        
        for quote in all_quotes:
            if quote.get("speaker_role") != "expert":
                continue

            quote_text = quote.get("text", "")
            best_match_score = 0.0
            best_focus_area = ""

            # Check relevance to each focus area
            for focus_area in focus_areas:
                relevance_score = self._calculate_focus_area_relevance(quote_text, focus_area)
                if relevance_score > best_match_score:
                    best_match_score = relevance_score
                    best_focus_area = focus_area

            # If quote is relevant enough, include it - lowered threshold for better coverage
            if best_match_score >= 0.5:  # Reduced from 1.0 to 0.5 for better coverage
                quote_copy = quote.copy()
                quote_copy["relevance_score"] = best_match_score
                quote_copy["focus_area_matched"] = best_focus_area
                relevant_quotes.append(quote_copy)

        self.logger.info(f"Local filtering found {len(relevant_quotes)} relevant quotes")
        return relevant_quotes

    def _create_empty_perspective_result(self, perspective_data: dict) -> Dict[str, Any]:
        """Create an empty result when no quotes are found."""
        return {
            "perspective_key": "unknown",
            "title": perspective_data.get("title", "Unknown Perspective"),
            "description": perspective_data.get("description", ""),
            "focus_areas": perspective_data.get("focus_areas", []),
            "ranked_quotes": [],
            "themes": [],
            "cross_transcript_insights": [],
            "analysis_metadata": {
                "total_quotes_analyzed": 0,
                "quotes_ranked": 0,
                "themes_identified": 0,
                "cross_transcript_themes": 0,
            }
        }

    def get_batch_processing_metrics(self) -> Dict[str, Any]:
        """Get comprehensive batch processing performance metrics."""
        return self.batch_manager.get_batch_processing_stats()

    def get_ranking_statistics(self, ranked_quotes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about quote ranking results."""
        return self.quote_ranker.get_ranking_statistics(ranked_quotes)

    def get_theme_statistics(self, themes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about theme analysis results."""
        return self.theme_analyzer.get_theme_statistics(themes)

    def reset_batch_statistics(self):
        """Reset batch processing statistics."""
        self.batch_manager.reset_statistics()

    def validate_batch_configuration(self) -> Dict[str, Any]:
        """Validate the current batch processing configuration."""
        return self.batch_manager.validate_configuration()
