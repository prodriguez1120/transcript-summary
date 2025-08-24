#!/usr/bin/env python3
"""
Perspective Analysis Module for FlexXray Transcripts

This module handles the analysis of different business perspectives
using OpenAI for quote ranking and theme identification.
"""

import json
import re
import time
import logging
from typing import List, Dict, Any, Tuple, Optional
from openai import OpenAI
from prompt_config import get_prompt_config


class PerspectiveAnalyzer:
    def __init__(self, api_key: str):
        """Initialize the perspective analyzer with OpenAI API key."""
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)
        self.vector_db_manager = None  # Will be set by the main tool
        self.logger = logging.getLogger(__name__)

        # Batch processing configuration
        self.batch_size = 20  # Default batch size for OpenAI processing
        self.batch_delay = 1.5  # Delay between batches in seconds
        self.failure_delay = 3.0  # Delay after batch failure in seconds
        self.max_quotes_per_perspective = (
            200  # Maximum quotes to process per perspective
        )
        self.enable_batch_processing = True  # Enable/disable batch processing

    def set_vector_db_manager(self, vector_db_manager):
        """Set the vector database manager for RAG functionality."""
        self.vector_db_manager = vector_db_manager
        if vector_db_manager:
            print("Vector database manager connected for RAG functionality")
        else:
            print("Vector database manager disconnected")

    def configure_batch_processing(
        self,
        batch_size: Optional[int] = None,
        batch_delay: Optional[float] = None,
        failure_delay: Optional[float] = None,
        max_quotes: Optional[int] = None,
        enable: Optional[bool] = None,
    ):
        """Configure batch processing parameters."""
        if batch_size is not None:
            self.batch_size = max(5, min(50, batch_size))  # Ensure reasonable range
            print(f"Batch size set to {self.batch_size}")

        if batch_delay is not None:
            self.batch_delay = max(
                0.5, min(5.0, batch_delay)
            )  # Ensure reasonable range
            print(f"Batch delay set to {self.batch_delay}s")

        if failure_delay is not None:
            self.failure_delay = max(
                1.0, min(10.0, failure_delay)
            )  # Ensure reasonable range
            print(f"Failure delay set to {self.failure_delay}s")

        if max_quotes is not None:
            self.max_quotes_per_perspective = max(
                50, min(500, max_quotes)
            )  # Ensure reasonable range
            print(
                f"Max quotes per perspective set to {self.max_quotes_per_perspective}"
            )

        if enable is not None:
            self.enable_batch_processing = enable
            status = "enabled" if enable else "disabled"
            print(f"Batch processing {status}")

        print(
            f"Batch processing configuration: size={self.batch_size}, delay={self.batch_delay}s, failure_delay={self.failure_delay}s, max_quotes={self.max_quotes_per_perspective}"
        )

    def analyze_perspective_with_quotes(
        self,
        perspective_key: str,
        perspective_data: dict,
        all_quotes: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Analyze a perspective using available quotes with OpenAI ranking."""
        print(f"Analyzing perspective: {perspective_data['title']}")

        # Find relevant quotes for this perspective
        relevant_quotes = self._find_relevant_quotes_for_perspective(
            perspective_key, perspective_data, all_quotes
        )

        if not relevant_quotes:
            print(f"No relevant quotes found for {perspective_key}")
            return {
                "perspective_key": perspective_key,
                "title": perspective_data["title"],
                "description": perspective_data["description"],
                "themes": [],
                "total_quotes": 0,
            }

        # Rank quotes using OpenAI
        ranked_quotes = self._rank_quotes_with_openai(
            perspective_key, perspective_data, relevant_quotes
        )

        # Analyze themes
        themes = self._analyze_perspective_thematically(
            perspective_key, perspective_data, ranked_quotes
        )

        return {
            "perspective_key": perspective_key,
            "title": perspective_data["title"],
            "description": perspective_data["description"],
            "themes": themes,
            "total_quotes": len(relevant_quotes),
            "ranked_quotes": ranked_quotes,
            "total_ranked_quotes": len(
                [
                    q
                    for q in ranked_quotes
                    if q.get("selection_stage")
                    in [
                        "openai_ranked",
                        "openai_failed",
                        "parsing_failed",
                        "batch_failed",
                    ]
                ]
            ),
            "batch_processing_stats": self._get_batch_processing_stats(ranked_quotes),
        }

    def _get_batch_processing_stats(
        self, ranked_quotes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Get statistics about batch processing performance."""
        if not ranked_quotes:
            return {}

        stats = {
            "total_quotes": len(ranked_quotes),
            "selection_stages": {},
            "batch_failures": 0,
            "successful_rankings": 0,
            "coverage_percentage": 0.0,
        }

        # Count quotes by selection stage
        for quote in ranked_quotes:
            stage = quote.get("selection_stage", "unknown")
            stats["selection_stages"][stage] = (
                stats["selection_stages"].get(stage, 0) + 1
            )

            if stage == "batch_failed":
                stats["batch_failures"] += 1
            elif stage == "openai_ranked":
                stats["successful_rankings"] += 1

        # Calculate coverage percentage
        if stats["total_quotes"] > 0:
            stats["coverage_percentage"] = (
                stats["successful_rankings"] / stats["total_quotes"]
            ) * 100

        return stats

    def get_batch_processing_metrics(self) -> Dict[str, Any]:
        """Get comprehensive batch processing performance metrics."""
        metrics = {
            "configuration": {
                "batch_size": self.batch_size,
                "batch_delay": self.batch_delay,
                "failure_delay": self.failure_delay,
                "max_quotes_per_perspective": self.max_quotes_per_perspective,
                "batch_processing_enabled": self.enable_batch_processing,
            },
            "performance": {
                "estimated_quotes_per_minute": int(
                    60 / (self.batch_delay + 0.5)
                ),  # Rough estimate
                "estimated_batch_processing_time": lambda quote_count: (
                    quote_count / self.batch_size
                )
                * (self.batch_delay + 0.5),
                "recommended_batch_size": self._get_recommended_batch_size(),
            },
            "optimization_tips": [
                "Increase batch_size for faster processing (if API allows)",
                "Decrease batch_delay for faster processing (if rate limits allow)",
                "Increase max_quotes_per_perspective for better coverage",
                "Monitor API rate limits and adjust delays accordingly",
            ],
        }

        return metrics

    def _get_recommended_batch_size(self) -> int:
        """Get recommended batch size based on current configuration."""
        # Conservative recommendation based on typical API limits
        if self.batch_delay <= 1.0:
            return min(15, self.batch_size)  # Smaller batches for faster processing
        elif self.batch_delay <= 2.0:
            return min(20, self.batch_size)  # Medium batches for balanced processing
        else:
            return min(25, self.batch_size)  # Larger batches for slower processing

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
                "organization",
                "enterprise",
                "operation",
                "strategy",
            ],
            "growth": [
                "growth",
                "expansion",
                "scaling",
                "development",
                "increase",
                "improvement",
            ],
            "competition": [
                "competition",
                "competitive",
                "competitor",
                "rival",
                "market leader",
                "competitive advantage",
            ],
            "revenue": [
                "revenue",
                "sales",
                "income",
                "profit",
                "earnings",
                "financial performance",
            ],
            "quality": [
                "quality",
                "excellence",
                "standards",
                "performance",
                "efficiency",
                "effectiveness",
            ],
        }

        # Expand each focus area with related terms
        for focus_area in focus_areas:
            focus_lower = focus_area.lower()
            for key, related_terms in focus_expansions.items():
                if key in focus_lower or any(
                    term in focus_lower for term in key.split()
                ):
                    # Add related terms that aren't already in the focus areas
                    for term in related_terms:
                        if term not in expanded_areas and not any(
                            term in existing.lower() for existing in expanded_areas
                        ):
                            expanded_areas.append(term)

        print(
            f"Expanded focus areas from {len(focus_areas)} to {len(expanded_areas)} for better coverage"
        )
        return expanded_areas

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
            print(f"No focus areas defined for perspective: {perspective_key}")
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
                print(f"Using vector database semantic search for {perspective_key}...")

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

                print(
                    f"Vector database search found {len(relevant_quotes)} relevant quotes"
                )

            else:
                # Fallback to local filtering if vector database not available
                print(
                    f"Vector database not available, using local filtering for {perspective_key}..."
                )
                relevant_quotes = self._fallback_local_filtering(
                    all_quotes, focus_areas
                )

        except Exception as e:
            print(f"Error using vector database search: {e}")
            print("Falling back to local filtering...")
            relevant_quotes = self._fallback_local_filtering(all_quotes, focus_areas)

        # Sort by relevance score and limit results
        relevant_quotes.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

        # Use configurable quote limit for better coverage with batch processing
        max_quotes = self.max_quotes_per_perspective
        print(
            f"Processing top {min(len(relevant_quotes), max_quotes)} quotes out of {len(relevant_quotes)} relevant quotes"
        )
        return relevant_quotes[:max_quotes]

    def _calculate_focus_area_relevance(
        self, quote_text: str, focus_area: str
    ) -> float:
        """Calculate relevance score between quote text and focus area."""
        if not quote_text or not focus_area:
            return 0.0

        quote_lower = quote_text.lower()
        focus_lower = focus_area.lower()

        # Split focus area into words
        focus_words = [
            word.strip() for word in focus_lower.split() if len(word.strip()) > 2
        ]

        # Count exact matches
        exact_matches = sum(1 for word in focus_words if word in quote_lower)

        # Count partial matches (for compound terms)
        partial_matches = sum(
            1
            for word in focus_words
            if any(word in quote_word for quote_word in quote_lower.split())
        )

        # Calculate base score - made less restrictive for better coverage
        base_score = (exact_matches * 1.5) + (
            partial_matches * 0.8
        )  # Reduced from 2.0/1.0

        # Bonus for longer focus areas (more specific)
        length_bonus = min(len(focus_words) * 0.3, 1.5)  # Reduced from 0.5/2.0

        # Bonus for exact phrase matches
        phrase_bonus = 2.0 if focus_lower in quote_lower else 0.0  # Reduced from 3.0

        # New: Context relevance bonus for business-related terms
        business_terms = [
            "business",
            "market",
            "customer",
            "strategy",
            "growth",
            "revenue",
            "profit",
            "competition",
            "industry",
        ]
        context_bonus = sum(0.5 for term in business_terms if term in quote_lower)

        total_score = base_score + length_bonus + phrase_bonus + context_bonus

        # Lower threshold for inclusion - more quotes will pass
        return min(total_score, 8.0)  # Reduced cap from 10.0 to 8.0

    def _fallback_local_filtering(
        self, all_quotes: List[Dict[str, Any]], focus_areas: List[str]
    ) -> List[Dict[str, Any]]:
        """Fallback method for local quote filtering when vector database is unavailable."""
        relevant_quotes = []

        # Filter to expert quotes only
        expert_quotes = [q for q in all_quotes if q.get("speaker_role") == "expert"]

        if not expert_quotes:
            return []

        for quote in expert_quotes:
            quote_text = quote.get("text", "").lower()

            # Check if quote contains any focus area keywords
            relevance_score = 0
            matched_focus_area = None

            for focus_area in focus_areas:
                focus_words = focus_area.lower().split()
                for word in focus_words:
                    if word in quote_text:
                        relevance_score += 1
                        matched_focus_area = focus_area

            # If quote is relevant enough, include it - lowered threshold for better coverage
            if relevance_score >= 0.5:  # Reduced from 1.0 to 0.5 for better coverage
                quote_copy = quote.copy()
                quote_copy["relevance_score"] = relevance_score
                quote_copy["focus_area_matched"] = matched_focus_area
                relevant_quotes.append(quote_copy)

        return relevant_quotes

    def _rank_quotes_with_openai(
        self, perspective_key: str, perspective_data: dict, quotes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Rank quotes using OpenAI for relevance and insight quality."""
        if not quotes:
            return []

        print(f"Ranking {len(quotes)} quotes for {perspective_key} using OpenAI...")

        # Use batch processing for better coverage and reliability
        if len(quotes) > 20:  # Use batch processing for larger quote sets
            print(f"Using batch processing for {len(quotes)} quotes...")
            return self._rank_quotes_with_openai_batch(
                perspective_key, perspective_data, quotes
            )
        else:
            print(f"Processing {len(quotes)} quotes in single batch...")
            return self._rank_quotes_with_openai_single(
                perspective_key, perspective_data, quotes
            )

    def _rank_quotes_with_openai_batch(
        self,
        perspective_key: str,
        perspective_data: dict,
        quotes: List[Dict[str, Any]],
        batch_size: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Rank quotes in batches for better coverage and reliability."""
        if not quotes:
            return []

        # Use configured batch size if not specified
        if batch_size is None:
            batch_size = self.batch_size

        # Ensure batch_size is a valid integer
        batch_size = max(5, min(50, batch_size))  # Ensure reasonable range

        print(
            f"Starting batch processing for {len(quotes)} quotes with batch size {batch_size}"
        )

        all_ranked_quotes = []
        total_batches = (len(quotes) + batch_size - 1) // batch_size

        # Process quotes in batches
        for i in range(0, len(quotes), batch_size):
            batch_num = i // batch_size + 1
            batch = quotes[i : i + batch_size]

            print(f"Processing batch {batch_num}/{total_batches} ({len(batch)} quotes)")

            try:
                # Process this batch
                ranked_batch = self._rank_quotes_with_openai_single(
                    perspective_key, perspective_data, batch
                )

                if ranked_batch:
                    all_ranked_quotes.extend(ranked_batch)
                    print(
                        f"✅ Batch {batch_num} completed successfully - {len(ranked_batch)} quotes ranked"
                    )
                else:
                    print(f"⚠️ Batch {batch_num} returned no results")

                # Add delay between batches to avoid rate limiting (except for last batch)
                if i + batch_size < len(quotes):
                    delay = self.batch_delay
                    print(f"Waiting {delay}s before next batch...")
                    time.sleep(delay)

            except Exception as e:
                print(f"❌ Batch {batch_num} failed: {e}")
                print("Continuing with next batch...")

                # Add failed quotes with default ranking to maintain data integrity
                for quote in batch:
                    quote_copy = quote.copy()
                    quote_copy["openai_rank"] = max(1, len(quotes) - i)
                    quote_copy["selection_stage"] = "batch_failed"
                    quote_copy["error_message"] = str(e)
                    all_ranked_quotes.append(quote_copy)

                # Add longer delay after failure to avoid cascading issues
                if i + batch_size < len(quotes):
                    delay = self.failure_delay
                    print(f"Waiting {delay}s after batch failure...")
                    time.sleep(delay)

        print(
            f"Batch processing completed: {len(all_ranked_quotes)} total quotes processed"
        )

        # Sort all quotes by rank for consistent ordering
        all_ranked_quotes.sort(key=lambda x: x.get("openai_rank", 0), reverse=True)

        return all_ranked_quotes

    def _rank_quotes_with_openai_single(
        self, perspective_key: str, perspective_data: dict, quotes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Rank a single batch of quotes using OpenAI (original implementation)."""
        if not quotes:
            return []

        print(f"Ranking {len(quotes)} quotes in single batch for {perspective_key}...")

        # Get prompt configuration
        prompt_config = get_prompt_config()

        # Prepare ranking prompt
        ranking_prompt = self._create_ranking_prompt(
            perspective_key, perspective_data, quotes
        )

        try:
            # Get OpenAI parameters from config
            params = prompt_config.get_prompt_parameters("quote_ranking")

            # Validate system message
            system_message = prompt_config.get_system_message("quote_ranking")
            if not system_message:
                print("WARNING: Empty system message for quote_ranking")
                system_message = (
                    "You are an expert analyst. Respond with ONLY valid JSON."
                )

            # Validate prompt content
            if not ranking_prompt or len(ranking_prompt.strip()) < 100:
                print("ERROR: Ranking prompt is too short or empty")
                print(f"Prompt length: {len(ranking_prompt)}")
                print(f"Prompt preview: {ranking_prompt[:200]}...")
                raise ValueError("Invalid ranking prompt")

            # Debug: Print API call details
            print(f"API Call - Model: {params.get('model', 'gpt-4')}")
            print(f"API Call - System message length: {len(system_message)}")
            print(f"API Call - User prompt length: {len(ranking_prompt)}")
            print(f"API Call - Temperature: {params.get('temperature', 0.3)}")
            print(f"API Call - Max tokens: {params.get('max_tokens', 2000)}")

            # Validate API client
            if not self.client:
                raise ValueError("OpenAI client is not initialized")

            # Call OpenAI for ranking
            response = self.client.chat.completions.create(
                model=params.get("model", "gpt-4"),
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": ranking_prompt},
                ],
                temperature=params.get("temperature", 0.3),
                max_tokens=params.get("max_tokens", 2000),
            )

            # Validate response
            if not response or not response.choices or len(response.choices) == 0:
                raise ValueError("Empty response from OpenAI API")

            # Debug: Print response details
            response_content = response.choices[0].message.content
            print(f"API Response length: {len(response_content)}")
            print(f"API Response preview: {response_content[:100]}...")

            # Validate response content
            if not response_content or len(response_content.strip()) < 10:
                raise ValueError("Response content is too short or empty")

            # Parse ranking response
            ranked_quotes = self._parse_ranking_response(response_content, quotes)

            print(f"Successfully ranked {len(ranked_quotes)} quotes")
            return ranked_quotes

        except Exception as e:
            print(f"Error ranking quotes with OpenAI: {e}")

            # Try fallback with more explicit prompt
            try:
                print("Attempting fallback with explicit JSON-only prompt...")

                # Create a simplified, more direct prompt
                quotes_list = ""
                for i, quote in enumerate(quotes):
                    quotes_list += f"\nQuote {i+1}: {quote.get('text', '')[:200]}..."
                    if quote.get("transcript_name"):
                        quotes_list += f" [From: {quote['transcript_name']}]"

                fallback_prompt = f"""CRITICAL: You must respond with ONLY valid JSON. No conversational text, no explanations.

Analyze and rank the following quotes for the perspective: {perspective_data['title']}

Perspective Description: {perspective_data['description']}
Focus Areas: {', '.join(perspective_data['focus_areas'])}

For each quote, provide a JSON array of objects:
[
  {{
    "quote_index": <1-based index>,
    "relevance_score": <1-10>,
    "relevance_explanation": "<brief explanation>",
    "key_insight": "<main insight from quote>"
  }}
]

Quotes to analyze:
{quotes_list}

RESPOND WITH ONLY THE JSON ARRAY. NO OTHER TEXT. NO GREETINGS. NO EXPLANATIONS."""

                fallback_response = self.client.chat.completions.create(
                    model=params.get("model", "gpt-4"),
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an AI assistant that ONLY responds with valid JSON. Never include conversational text.",
                        },
                        {"role": "user", "content": fallback_prompt},
                    ],
                    temperature=0.1,  # Lower temperature for more consistent output
                    max_tokens=2000,
                )

                fallback_content = fallback_response.choices[0].message.content
                print(f"Fallback response preview: {fallback_content[:100]}...")

                ranked_quotes = self._parse_ranking_response(fallback_content, quotes)
                print(f"Fallback successful - ranked {len(ranked_quotes)} quotes")
                return ranked_quotes

            except Exception as fallback_error:
                print(f"First fallback failed: {fallback_error}")

                # Try second fallback with even more explicit instructions
                try:
                    print("Attempting second fallback with minimal prompt...")
                    # Create quotes list for minimal prompt
                    minimal_quotes_list = ""
                    for i, quote in enumerate(quotes):
                        minimal_quotes_list += (
                            f"\nQuote {i+1}: {quote.get('text', '')[:100]}..."
                        )

                    minimal_prompt = f"""JSON ONLY. No text outside brackets.

Rank these quotes for {perspective_data['title']}:

{minimal_quotes_list}

Return: [{{"quote_index": 1, "relevance_score": 8, "relevance_explanation": "relevant", "key_insight": "insight"}}]"""

                    minimal_response = self.client.chat.completions.create(
                        model=params.get("model", "gpt-4"),
                        messages=[
                            {
                                "role": "system",
                                "content": "JSON only. No conversation.",
                            },
                            {"role": "user", "content": minimal_prompt},
                        ],
                        temperature=0.0,  # Zero temperature for most consistent output
                        max_tokens=1000,
                    )

                    minimal_content = minimal_response.choices[0].message.content
                    print(
                        f"Second fallback response preview: {minimal_content[:100]}..."
                    )

                    ranked_quotes = self._parse_ranking_response(
                        minimal_content, quotes
                    )
                    print(
                        f"Second fallback successful - ranked {len(ranked_quotes)} quotes"
                    )
                    return ranked_quotes

                except Exception as second_fallback_error:
                    print(f"Second fallback also failed: {second_fallback_error}")
                    # Continue to final fallback

            except Exception as fallback_error:
                print(f"Fallback also failed: {fallback_error}")
                # Return quotes with default ranking
                for i, quote in enumerate(quotes):
                    quote["openai_rank"] = i + 1
                    quote["selection_stage"] = "openai_failed"
                return quotes

        # Final fallback - if all else fails, return quotes with default ranking
        print("All ranking methods failed, using default ranking...")
        for i, quote in enumerate(quotes):
            quote["openai_rank"] = i + 1
            quote["selection_stage"] = "openai_failed"
        return quotes

    def _create_ranking_prompt(
        self, perspective_key: str, perspective_data: dict, quotes: List[Dict[str, Any]]
    ) -> str:
        """Create the prompt for OpenAI quote ranking."""
        prompt_config = get_prompt_config()

        # Prepare quotes list for template
        quotes_list = ""
        for i, quote in enumerate(quotes):
            quotes_list += f"\nQuote {i+1}: {quote.get('text', '')[:200]}..."
            if quote.get("transcript_name"):
                quotes_list += f" [From: {quote['transcript_name']}]"

        # Format prompt using template
        return prompt_config.format_prompt(
            "quote_ranking",
            perspective_title=perspective_data["title"],
            perspective_description=perspective_data["description"],
            focus_areas=", ".join(perspective_data["focus_areas"]),
            quotes_list=quotes_list,
        )

    def _extract_json_from_response(self, response_text: str) -> str:
        """Extract JSON from OpenAI response text using robust multi-step approach."""
        import re
        import json

        if not response_text or not response_text.strip():
            raise ValueError("Empty response text")

        # Clean up common formatting issues first
        cleaned_text = response_text.strip()

        # Remove markdown code blocks
        cleaned_text = re.sub(r"```json\s*", "", cleaned_text)
        cleaned_text = re.sub(r"\s*```", "", cleaned_text)

        # Remove common conversational prefixes and greetings
        conversational_patterns = [
            r"^Hello! How can I assist you today\?",
            r"^Hello! How can I help you today\?",
            r"^Hello! How can I help you\?",
            r"^Hello! How can I assist you\?",
            r"^Hello! How can I assist you\?",
            r"^Hello! How can I help you\?",
            r"^Hello! How can I assist you\?",
            r"^Hello! How can I help you\?",
            r"^Hello! How can I assist you\?",
            r"^Hello! How can I help you\?",
            r"^Here is the analysis:",
            r"^Here is the response:",
            r"^Analysis:",
            r"^Response:",
            r"^JSON:",
            r"^Here is the JSON:",
        ]

        for pattern in conversational_patterns:
            cleaned_text = re.sub(pattern, "", cleaned_text, flags=re.IGNORECASE)

        # Remove any leading/trailing whitespace and newlines
        cleaned_text = cleaned_text.strip()

        # Strategy 1: Try to find JSON object with balanced braces (most reliable)
        brace_start = cleaned_text.find("{")
        if brace_start != -1:
            brace_count = 0
            brace_end = brace_start

            for i in range(brace_start, len(cleaned_text)):
                char = cleaned_text[i]
                if char == "{":
                    brace_count += 1
                elif char == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        brace_end = i + 1
                        break

            if brace_count == 0:  # Found balanced braces
                json_text = cleaned_text[brace_start:brace_end]
                try:
                    json.loads(json_text)
                    return json_text
                except json.JSONDecodeError:
                    pass

        # Strategy 2: Try to find JSON array with balanced brackets
        bracket_start = cleaned_text.find("[")
        if bracket_start != -1:
            bracket_count = 0
            bracket_end = bracket_start

            for i in range(bracket_start, len(cleaned_text)):
                char = cleaned_text[i]
                if char == "[":
                    bracket_count += 1
                elif char == "]":
                    bracket_count -= 1
                    if bracket_count == 0:
                        bracket_end = i + 1
                        break

            if bracket_count == 0:  # Found balanced brackets
                json_text = cleaned_text[bracket_start:bracket_end]
                try:
                    json.loads(json_text)
                    return json_text
                except json.JSONDecodeError:
                    pass

        # Strategy 3: Try to find the largest valid JSON object/array
        # Look for patterns like { ... } or [ ... ] and try to extract them
        json_patterns = [
            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",  # Nested objects
            r"\[[^\[\]]*(?:\{[^{}]*\}[^\[\]]*)*\]",  # Arrays with objects
            r"\{[^{}]*\}",  # Simple objects
            r"\[[^\[\]]*\]",  # Simple arrays
        ]

        for pattern in json_patterns:
            matches = re.findall(pattern, cleaned_text, re.DOTALL)
            for match in matches:
                try:
                    json.loads(match)
                    return match
                except json.JSONDecodeError:
                    continue

        # Strategy 4: Try to fix common JSON formatting issues
        # Remove trailing commas, fix unquoted keys, etc.
        potential_json = cleaned_text

        # Find the first { or [ and try to extract from there
        start_chars = ["{", "["]
        for start_char in start_chars:
            start_pos = potential_json.find(start_char)
            if start_pos != -1:
                # Try to extract from start_char to end, then work backwards
                for end_pos in range(len(potential_json), start_pos, -1):
                    try:
                        test_json = potential_json[start_pos:end_pos]
                        json.loads(test_json)
                        return test_json
                    except json.JSONDecodeError:
                        continue

        # Strategy 5: Last resort - try to construct valid JSON from fragments
        # Look for key-value patterns and try to build a valid object
        if "{" in cleaned_text or "[" in cleaned_text:
            # Try to extract just the JSON-like part
            lines = cleaned_text.split("\n")
            json_lines = []
            in_json = False

            for line in lines:
                line = line.strip()
                if "{" in line or "[" in line:
                    in_json = True
                if in_json:
                    json_lines.append(line)
                if in_json and ("}" in line or "]" in line):
                    break

            if json_lines:
                potential_json = "\n".join(json_lines)
                # Try to fix common issues
                potential_json = re.sub(
                    r",\s*([}\]])", r"\1", potential_json
                )  # Remove trailing commas
                potential_json = re.sub(
                    r'([{[])\s*([^"\'\w])', r'\1"\2"', potential_json
                )  # Quote unquoted keys

                try:
                    json.loads(potential_json)
                    return potential_json
                except json.JSONDecodeError:
                    pass

        # Strategy 6: Try to extract JSON from conversational responses
        # Look for patterns that might indicate where JSON starts
        json_start_patterns = [
            r"Here is the JSON:?\s*(\{.*\}|\[.*\])",
            r"Here is the response:?\s*(\{.*\}|\[.*\])",
            r"Here is the analysis:?\s*(\{.*\}|\[.*\])",
            r"JSON:?\s*(\{.*\}|\[.*\])",
            r"Response:?\s*(\{.*\}|\[.*\])",
            r"Analysis:?\s*(\{.*\}|\[.*\])",
        ]

        for pattern in json_start_patterns:
            matches = re.findall(pattern, cleaned_text, re.DOTALL | re.IGNORECASE)
            for match in matches:
                try:
                    json.loads(match)
                    return match
                except json.JSONDecodeError:
                    continue

        # Strategy 7: Last resort - try to find any JSON-like structure
        # Look for the longest substring that might be JSON
        if "{" in cleaned_text or "[" in cleaned_text:
            # Find all potential JSON start positions
            start_positions = []
            for char in ["{", "["]:
                pos = cleaned_text.find(char)
                if pos != -1:
                    start_positions.append((pos, char))

            # Try each start position
            for start_pos, start_char in start_positions:
                # Find the matching closing character
                if start_char == "{":
                    end_char = "}"
                else:
                    end_char = "]"

                # Count brackets/braces to find the end
                count = 0
                for i in range(start_pos, len(cleaned_text)):
                    if cleaned_text[i] == start_char:
                        count += 1
                    elif cleaned_text[i] == end_char:
                        count -= 1
                        if count == 0:
                            try:
                                potential_json = cleaned_text[start_pos : i + 1]
                                json.loads(potential_json)
                                return potential_json
                            except json.JSONDecodeError:
                                break

        # Strategy 8: Try to fix common JSON formatting issues and retry
        if "{" in cleaned_text or "[" in cleaned_text:
            # Try to fix trailing commas, missing quotes, etc.
            fixed_text = cleaned_text

            # Remove trailing commas before closing brackets/braces
            fixed_text = re.sub(r",\s*([}\]])", r"\1", fixed_text)

            # Try to quote unquoted keys
            fixed_text = re.sub(
                r"([{[])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:", r'\1"\2":', fixed_text
            )

            # Try to parse the fixed text
            try:
                json.loads(fixed_text)
                return fixed_text
            except json.JSONDecodeError:
                pass

            # Try to extract just the JSON part from the fixed text
            for start_char in ["{", "["]:
                start_pos = fixed_text.find(start_char)
                if start_pos != -1:
                    # Find the matching closing character
                    end_char = "}" if start_char == "{" else "]"
                    count = 0
                    for i in range(start_pos, len(fixed_text)):
                        if fixed_text[i] == start_char:
                            count += 1
                        elif fixed_text[i] == end_char:
                            count -= 1
                            if count == 0:
                                try:
                                    potential_json = fixed_text[start_pos : i + 1]
                                    json.loads(potential_json)
                                    return potential_json
                                except json.JSONDecodeError:
                                    break

        # If all else fails, provide detailed error information
        print(f"Response text preview: {cleaned_text[:200]}...")
        print("Contains {: " + str(cleaned_text.count("{")))
        print("Contains }: " + str(cleaned_text.count("}")))
        print(f"Contains [: {cleaned_text.count('[')}")
        print(f"Contains ]: {cleaned_text.count(']')}")

        raise ValueError(
            "No valid JSON found in response after all extraction strategies"
        )

    def _parse_ranking_response(
        self, response_text: str, quotes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Parse OpenAI's ranking response and apply it to quotes."""
        try:
            # Extract JSON from response using robust extraction
            json_text = self._extract_json_from_response(response_text)

            # Parse the JSON
            rankings = json.loads(json_text)

            # Handle both array and single object responses
            if not isinstance(rankings, list):
                rankings = [rankings]

            # Track which quotes were explicitly ranked by OpenAI
            explicitly_ranked_indices = set()

            # Apply rankings to quotes
            for ranking in rankings:
                quote_index = ranking.get("quote_index", 0) - 1  # Convert to 0-based
                if 0 <= quote_index < len(quotes):
                    quote = quotes[quote_index]
                    quote["openai_rank"] = ranking.get("relevance_score", 0)
                    quote["relevance_explanation"] = ranking.get(
                        "relevance_explanation", ""
                    )
                    quote["key_insight"] = ranking.get("key_insight", "")
                    quote["selection_stage"] = "openai_ranked"
                    explicitly_ranked_indices.add(quote_index)

            # Assign selection stages to all quotes that weren't explicitly ranked
            for i, quote in enumerate(quotes):
                if i not in explicitly_ranked_indices:
                    # These quotes went through the ranking process but weren't in OpenAI's top results
                    if not quote.get("selection_stage"):
                        quote["selection_stage"] = "openai_processed"
                    if not quote.get("openai_rank"):
                        # Assign a default rank based on position (lower = better)
                        quote["openai_rank"] = max(1, len(quotes) - i)

            # Sort by OpenAI rank
            quotes.sort(key=lambda x: x.get("openai_rank", 0), reverse=True)

            print(f"Successfully processed {len(quotes)} quotes:")
            print(f"  - Explicitly ranked by OpenAI: {len(explicitly_ranked_indices)}")
            print(
                f"  - Processed through ranking pipeline: {len(quotes) - len(explicitly_ranked_indices)}"
            )

            return quotes

        except Exception as e:
            print(f"Error parsing ranking response: {e}")
            # Return quotes with default ranking and selection stages
            for i, quote in enumerate(quotes):
                quote["openai_rank"] = max(1, len(quotes) - i)
                quote["selection_stage"] = "parsing_failed"
            return quotes

    def _analyze_perspective_thematically(
        self, perspective_key: str, perspective_data: dict, quotes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Analyze quotes thematically within a perspective."""
        if not quotes:
            return []

        print(f"Analyzing themes for {perspective_key}...")

        # Group quotes by themes using OpenAI
        themes = self._identify_themes_with_openai(
            perspective_key, perspective_data, quotes
        )

        # Select quotes for each theme
        for theme in themes:
            theme_quotes = self._select_quotes_for_theme(
                theme["name"], quotes, theme.get("max_quotes", 3)
            )
            theme["quotes"] = theme_quotes

        return themes

    def _identify_themes_with_openai(
        self, perspective_key: str, perspective_data: dict, quotes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify themes using OpenAI analysis."""
        if not quotes:
            return []

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
            themes = self._parse_themes_response(response.choices[0].message.content)
            return themes

        except Exception as e:
            print(f"Error identifying themes with OpenAI: {e}")
            # Return default themes
            return [
                {
                    "name": "Key Insights",
                    "description": "Primary insights from the perspective",
                    "key_insights": ["Analysis completed"],
                    "max_quotes": 4,
                }
            ]

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
                    valid_themes.append(
                        {
                            "name": theme.get("name", "Unknown Theme"),
                            "description": theme.get("description", ""),
                            "key_insights": theme.get("key_insights", []),
                            "max_quotes": theme.get("max_quotes", 4),
                        }
                    )

            return valid_themes

        except Exception as e:
            print(f"Error parsing themes response: {e}")
            return []

    def _select_quotes_for_theme(
        self, theme_name: str, quotes: List[Dict[str, Any]], max_quotes: int
    ) -> List[Dict[str, Any]]:
        """Select quotes for a specific theme."""
        if not quotes:
            return []

        # Filter quotes that might be relevant to this theme
        relevant_quotes = []
        for quote in quotes:
            quote_text = quote.get("text", "").lower()
            theme_lower = theme_name.lower()

            # Simple relevance scoring
            relevance_score = 0
            theme_words = theme_lower.split()

            for word in theme_words:
                if word in quote_text:
                    relevance_score += 1

            if relevance_score > 0:
                quote_copy = quote.copy()
                quote_copy["theme_relevance"] = relevance_score
                # Ensure selection stage is set if not already present
                if not quote_copy.get("selection_stage"):
                    quote_copy["selection_stage"] = "theme_selected"
                relevant_quotes.append(quote_copy)

        # Sort by theme relevance and take top quotes
        relevant_quotes.sort(key=lambda x: x.get("theme_relevance", 0), reverse=True)
        return relevant_quotes[:max_quotes]
