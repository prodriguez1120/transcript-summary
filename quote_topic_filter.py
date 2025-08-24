#!/usr/bin/env python3
"""
Quote Topic Filter for FlexXray Company Summary

This module filters quotes by specific business topics to support
the pre-filtered company summary prompt structure.
"""

import re
from typing import List, Dict, Any, Tuple
from openai import OpenAI
import json

# Import fuzzy matching utilities
try:
    from fuzzy_matching import FuzzyMatcher

    FUZZY_AVAILABLE = True
except ImportError:
    FUZZY_AVAILABLE = False
    print(
        "Warning: fuzzy_matching not available. Install with: pip install fuzzywuzzy python-Levenshtein"
    )


class QuoteTopicFilter:
    """Filters quotes by specific business topics for company summary."""

    def __init__(self, api_key: str = None, use_fuzzy: bool = True):
        """Initialize the quote topic filter."""
        self.api_key = api_key
        self.use_fuzzy = use_fuzzy and FUZZY_AVAILABLE

        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None

        # Initialize fuzzy matcher if available
        if self.use_fuzzy:
            self.fuzzy_matcher = FuzzyMatcher()
        else:
            self.fuzzy_matcher = None

        # Define topic keywords and patterns
        self.topic_patterns = {
            "market_leadership": [
                r"market\s+lead(er|ership|ing)",
                r"market\s+share",
                r"dominant",
                r"industry\s+leader",
                r"number\s+one",
                r"top\s+provider",
                r"largest",
                r"primary\s+supplier",
            ],
            "value_proposition": [
                r"value\s+proposition",
                r"insourcing",
                r"outsourcing",
                r"cost\s+benefit",
                r"ROI",
                r"return\s+on\s+investment",
                r"cost\s+effective",
                r"value\s+add",
            ],
            "local_presence": [
                r"local",
                r"footprint",
                r"presence",
                r"regional",
                r"geographic",
                r"location",
                r"proximity",
                r"nearby",
            ],
            "technology_advantages": [
                r"technology",
                r"proprietary",
                r"patent",
                r"innovation",
                r"advanced",
                r"sophisticated",
                r"unique\s+technology",
                r"technical\s+advantage",
            ],
            "turnaround_times": [
                r"turnaround",
                r"speed",
                r"fast",
                r"quick",
                r"rapid",
                r"time\s+to\s+market",
                r"efficiency",
                r"response\s+time",
            ],
            "market_limitations": [
                r"limited\s+market",
                r"TAM",
                r"total\s+addressable\s+market",
                r"market\s+size",
                r"constraint",
                r"limitation",
                r"ceiling",
                r"cap",
            ],
            "timing_challenges": [
                r"unpredictable",
                r"timing",
                r"seasonal",
                r"cyclical",
                r"volatile",
                r"fluctuation",
                r"variability",
                r"irregular",
            ],
        }

        # Expand patterns with synonyms if fuzzy matching is available
        if self.use_fuzzy and self.fuzzy_matcher:
            self.expanded_patterns = {}
            for topic, patterns in self.topic_patterns.items():
                # Convert regex patterns to plain text for synonym expansion
                plain_patterns = [
                    re.sub(r"[^\w\s]", "", pattern) for pattern in patterns
                ]
                expanded = self.fuzzy_matcher.get_synonym_patterns(plain_patterns)
                self.expanded_patterns[topic] = expanded
        else:
            self.expanded_patterns = self.topic_patterns

    def filter_quotes_by_topic(
        self, quotes: List[Dict[str, Any]], topic: str
    ) -> List[Dict[str, Any]]:
        """Filter quotes by specific topic using keyword patterns."""
        if topic not in self.topic_patterns:
            return []

        # Use fuzzy matching if available
        if self.use_fuzzy and self.fuzzy_matcher:
            return self.fuzzy_matcher.enhanced_topic_filtering(
                quotes, topic, self.expanded_patterns[topic]
            )

        # Fallback to exact pattern matching
        patterns = self.topic_patterns[topic]
        filtered_quotes = []

        for quote in quotes:
            text = quote.get("text", "").lower()

            # Check if quote matches any pattern for this topic
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    filtered_quotes.append(quote)
                    break

        return filtered_quotes

    def filter_quotes_by_ai(
        self, quotes: List[Dict[str, Any]], topic: str, max_quotes: int = 5
    ) -> List[Dict[str, Any]]:
        """Use AI to filter quotes by topic for more accurate results."""
        if not self.client:
            return self.filter_quotes_by_topic(quotes, topic)

        # Create topic-specific prompt
        topic_prompts = {
            "market_leadership": "market leadership, market share dominance, industry leadership position",
            "value_proposition": "value proposition, insourcing risks, cost-benefit analysis",
            "local_presence": "local presence, geographic footprint, regional advantages",
            "technology_advantages": "proprietary technology, technical advantages, innovation",
            "turnaround_times": "speed, turnaround times, efficiency, response time",
            "market_limitations": "market size limitations, TAM constraints, market ceiling",
            "timing_challenges": "unpredictable timing, seasonal variations, volatility",
        }

        topic_description = topic_prompts.get(topic, topic)

        prompt = f"""Given the following quotes from FlexXray interviews, identify the TOP {max_quotes} quotes that are MOST relevant to: {topic_description}

For each quote, provide a relevance score from 1-10 and brief explanation.

Quotes to analyze:
{json.dumps([{'text': q.get('text', ''), 'speaker_role': q.get('speaker_role', ''), 'transcript_name': q.get('transcript_name', '')} for q in quotes], indent=2)}

Respond with JSON format:
{{
  "selected_quotes": [
    {{
      "quote_index": <index in original list>,
      "relevance_score": <1-10>,
      "relevance_explanation": "<brief explanation>"
    }}
  ]
}}

Select only the most relevant quotes for {topic_description}. Focus on quotes with specific details, metrics, or concrete evidence."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=1000,
            )

            result = json.loads(response.choices[0].message.content)
            selected_indices = [
                item["quote_index"] for item in result.get("selected_quotes", [])
            ]

            # Return selected quotes in order of relevance
            selected_quotes = []
            for idx in selected_indices:
                if 0 <= idx < len(quotes):
                    selected_quotes.append(quotes[idx])

            return selected_quotes[:max_quotes]

        except Exception as e:
            print(f"AI filtering failed for topic {topic}: {e}")
            return self.filter_quotes_by_topic(quotes, topic)

    def get_all_topic_quotes(
        self, quotes: List[Dict[str, Any]], use_ai: bool = True
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get quotes for all topics needed for company summary."""
        topic_quotes = {}

        for topic in self.topic_patterns.keys():
            if use_ai and self.client:
                topic_quotes[topic] = self.filter_quotes_by_ai(
                    quotes, topic, max_quotes=4
                )
            else:
                topic_quotes[topic] = self.filter_quotes_by_topic(quotes, topic)[:4]

        return topic_quotes

    def format_quotes_for_prompt(
        self, topic_quotes: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, str]:
        """Format quotes for the company summary prompt variables."""
        formatted_quotes = {}

        for topic, quotes in topic_quotes.items():
            if not quotes:
                formatted_quotes[f"{topic}_quotes"] = (
                    "No relevant quotes available for this topic."
                )
                continue

            formatted_list = []
            for quote in quotes:
                text = quote.get("text", "").strip()
                speaker = quote.get("speaker_role", "Unknown Speaker")
                transcript = quote.get("transcript_name", "Unknown Transcript")

                formatted_quote = f'"{text}" - {speaker} from {transcript}'
                formatted_list.append(formatted_quote)

            formatted_quotes[f"{topic}_quotes"] = "\n".join(formatted_list)

        return formatted_quotes

    def get_company_summary_variables(
        self, quotes: List[Dict[str, Any]], use_ai: bool = True
    ) -> Dict[str, str]:
        """Get all the variables needed for the company summary prompt."""
        topic_quotes = self.get_all_topic_quotes(quotes, use_ai)
        return self.format_quotes_for_prompt(topic_quotes)
