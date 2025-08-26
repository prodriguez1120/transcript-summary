#!/usr/bin/env python3
"""
Quote Ranking Module for FlexXray Transcripts

This module handles OpenAI-driven quote ranking and scoring for business perspectives.
Extracted from perspective_analysis.py to provide focused quote ranking functionality.
"""

import json
import re
import time
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
from prompt_config import get_prompt_config


class QuoteRanker:
    """Handles OpenAI-driven quote ranking and scoring."""
    
    def __init__(self, api_key: str):
        """Initialize the quote ranker with OpenAI API key."""
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)
        self.logger = logging.getLogger(__name__)

    def rank_quotes_with_openai(
        self, perspective_key: str, perspective_data: dict, quotes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Rank quotes using OpenAI for relevance and insight quality."""
        if not quotes:
            return []

        self.logger.info(f"Ranking {len(quotes)} quotes for {perspective_key} using OpenAI...")

        # Use batch processing for better coverage and reliability
        if len(quotes) > 20:  # Use batch processing for larger quote sets
            self.logger.info(f"Using batch processing for {len(quotes)} quotes...")
            return self._rank_quotes_with_openai_batch(
                perspective_key, perspective_data, quotes
            )
        else:
            self.logger.info(f"Processing {len(quotes)} quotes in single batch...")
            return self._rank_quotes_with_openai_single(
                perspective_key, perspective_data, quotes
            )

    def _rank_quotes_with_openai_batch(
        self,
        perspective_key: str,
        perspective_data: dict,
        quotes: List[Dict[str, Any]],
        batch_size: int = 20,
        batch_delay: float = 1.5,
        failure_delay: float = 3.0,
    ) -> List[Dict[str, Any]]:
        """Rank quotes in batches for better coverage and reliability."""
        if not quotes:
            return []

        # Ensure batch_size is a valid integer
        batch_size = max(5, min(50, batch_size))  # Ensure reasonable range

        self.logger.info(
            f"Starting batch processing for {len(quotes)} quotes with batch size {batch_size}"
        )

        all_ranked_quotes = []
        total_batches = (len(quotes) + batch_size - 1) // batch_size

        # Process quotes in batches
        for i in range(0, len(quotes), batch_size):
            batch_num = i // batch_size + 1
            batch = quotes[i : i + batch_size]

            self.logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} quotes)")

            try:
                # Process this batch
                ranked_batch = self._rank_quotes_with_openai_single(
                    perspective_key, perspective_data, batch
                )

                if ranked_batch:
                    all_ranked_quotes.extend(ranked_batch)
                    self.logger.info(
                        f"✅ Batch {batch_num} completed successfully - {len(ranked_batch)} quotes ranked"
                    )
                else:
                    self.logger.warning(f"⚠️ Batch {batch_num} returned no results")

                # Add delay between batches to avoid rate limiting (except for last batch)
                if i + batch_size < len(quotes):
                    self.logger.info(f"Waiting {batch_delay}s before next batch...")
                    time.sleep(batch_delay)

            except Exception as e:
                self.logger.error(f"❌ Batch {batch_num} failed: {e}")
                self.logger.info("Continuing with next batch...")

                # Add failed quotes with default ranking to maintain data integrity
                for quote in batch:
                    quote_copy = quote.copy()
                    quote_copy["openai_rank"] = max(1, len(quotes) - i)
                    quote_copy["selection_stage"] = "batch_failed"
                    quote_copy["error_message"] = str(e)
                    all_ranked_quotes.append(quote_copy)

                # Add longer delay after failure to avoid cascading issues
                if i + batch_size < len(quotes):
                    self.logger.info(f"Waiting {failure_delay}s after batch failure...")
                    time.sleep(failure_delay)

        self.logger.info(
            f"Batch processing completed: {len(all_ranked_quotes)} total quotes processed"
        )
        return all_ranked_quotes

    def _rank_quotes_with_openai_single(
        self, perspective_key: str, perspective_data: dict, quotes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Rank a single batch of quotes using OpenAI."""
        if not quotes:
            return []

        try:
            # Create ranking prompt
            prompt = self._create_ranking_prompt(perspective_key, perspective_data, quotes)

            # Get prompt configuration
            prompt_config = get_prompt_config()
            params = prompt_config.get_prompt_parameters("quote_ranking")

            # Call OpenAI
            response = self.client.chat.completions.create(
                model=params.get("model", "gpt-4"),
                messages=[
                    {
                        "role": "system",
                        "content": prompt_config.get_system_message("quote_ranking"),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=params.get("temperature", 0.3),
                max_tokens=params.get("max_tokens", 2000),
            )

            # Parse response
            ranked_quotes = self._parse_ranking_response(
                response.choices[0].message.content, quotes
            )

            if ranked_quotes:
                self.logger.info(f"Successfully ranked {len(ranked_quotes)} quotes")
                return ranked_quotes
            else:
                self.logger.warning("No quotes ranked from OpenAI response")
                return self._fallback_ranking(quotes)

        except Exception as e:
            self.logger.error(f"Error ranking quotes with OpenAI: {e}")
            return self._fallback_ranking(quotes)

    def _create_ranking_prompt(
        self, perspective_key: str, perspective_data: dict, quotes: List[Dict[str, Any]]
    ) -> str:
        """Create the ranking prompt for OpenAI."""
        prompt_config = get_prompt_config()

        # Create quotes list for prompt
        quotes_list = ""
        for i, quote in enumerate(quotes):
            quote_text = quote.get("text", "")[:200]  # Limit quote length
            speaker_role = quote.get("speaker_role", "unknown")
            transcript_name = quote.get("transcript_name", "Unknown")
            
            quotes_list += f"\nQuote {i+1}:\n"
            quotes_list += f"Text: {quote_text}\n"
            quotes_list += f"Speaker: {speaker_role}\n"
            quotes_list += f"Source: {transcript_name}\n"

        # Format the prompt
        prompt = prompt_config.format_prompt(
            "quote_ranking",
            perspective_title=perspective_data["title"],
            perspective_description=perspective_data.get("description", ""),
            focus_areas=", ".join(perspective_data.get("focus_areas", [])),
            quotes_list=quotes_list,
            ranking_instructions="Rank quotes by relevance and insight quality (1=best, higher=worse)",
        )

        return prompt

    def _parse_ranking_response(
        self, response_text: str, original_quotes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Parse OpenAI's ranking response."""
        try:
            # Extract JSON from response using robust extraction
            json_text = self._extract_json_from_response(response_text)

            # Parse the JSON
            ranking_data = json.loads(json_text)

            # Handle different response formats
            if isinstance(ranking_data, list):
                ranked_quotes = ranking_data
            elif isinstance(ranking_data, dict) and "quotes" in ranking_data:
                ranked_quotes = ranking_data["quotes"]
            else:
                self.logger.warning(f"Unexpected ranking response format: {type(ranking_data)}")
                return []

            # Process ranked quotes
            processed_quotes = []
            for ranked_quote in ranked_quotes:
                if not isinstance(ranked_quote, dict):
                    continue

                # Find corresponding original quote
                quote_id = ranked_quote.get("id")
                quote_text = ranked_quote.get("text", "")
                
                original_quote = None
                for quote in original_quotes:
                    if (quote.get("id") == quote_id or 
                        quote.get("text", "") == quote_text):
                        original_quote = quote
                        break

                if original_quote:
                    # Merge ranking data with original quote
                    processed_quote = original_quote.copy()
                    processed_quote["openai_rank"] = ranked_quote.get("rank", 999)
                    processed_quote["ranking_reason"] = ranked_quote.get("reason", "")
                    processed_quote["selection_stage"] = "openai_ranked"
                    processed_quotes.append(processed_quote)

            # Sort by rank
            processed_quotes.sort(key=lambda x: x.get("openai_rank", 999))
            
            self.logger.info(f"Successfully parsed {len(processed_quotes)} ranked quotes")
            return processed_quotes

        except Exception as e:
            self.logger.error(f"Error parsing ranking response: {e}")
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

    def _fallback_ranking(self, quotes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Provide fallback ranking when OpenAI fails."""
        self.logger.warning("Using fallback ranking due to OpenAI failure")
        
        fallback_quotes = []
        for i, quote in enumerate(quotes):
            quote_copy = quote.copy()
            quote_copy["openai_rank"] = i + 1
            quote_copy["ranking_reason"] = "Fallback ranking - OpenAI unavailable"
            quote_copy["selection_stage"] = "openai_failed"
            fallback_quotes.append(quote_copy)

        return fallback_quotes

    def get_ranking_statistics(self, ranked_quotes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about quote ranking results."""
        if not ranked_quotes:
            return {
                "total_quotes": 0,
                "successful_rankings": 0,
                "failed_rankings": 0,
                "selection_stages": {},
                "ranking_coverage": 0.0,
            }

        stats = {
            "total_quotes": len(ranked_quotes),
            "successful_rankings": 0,
            "failed_rankings": 0,
            "selection_stages": {},
            "ranking_coverage": 0.0,
        }

        # Count quotes by selection stage
        for quote in ranked_quotes:
            stage = quote.get("selection_stage", "unknown")
            stats["selection_stages"][stage] = (
                stats["selection_stages"].get(stage, 0) + 1
            )

            if stage == "openai_ranked":
                stats["successful_rankings"] += 1
            elif stage in ["openai_failed", "batch_failed", "parsing_failed"]:
                stats["failed_rankings"] += 1

        # Calculate coverage percentage
        if stats["total_quotes"] > 0:
            stats["ranking_coverage"] = (
                stats["successful_rankings"] / stats["total_quotes"]
            ) * 100

        return stats
