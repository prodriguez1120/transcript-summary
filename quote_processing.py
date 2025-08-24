#!/usr/bin/env python3
"""
Quote Processing Module

Handles quote enrichment, speaker info extraction, theme categorization,
and date handling for the quote analysis system.
"""

import re
from datetime import datetime
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class QuoteProcessor:
    """Handles quote processing, enrichment, and formatting."""
    
    def __init__(self):
        """Initialize the quote processor."""
        self.theme_keywords = {
            "market_leadership": [
                "market", "leadership", "competitive", "advantage", 
                "position", "industry"
            ],
            "value_proposition": [
                "value", "proposition", "benefit", "advantage", 
                "customer", "decision"
            ],
            "local_presence": [
                "local", "presence", "footprint", "geographic", 
                "region", "area"
            ],
            "technology_advantages": [
                "technology", "proprietary", "innovation", "technical", 
                "capability"
            ],
            "rapid_turnaround": [
                "turnaround", "speed", "fast", "quick", "efficient", 
                "timing"
            ],
            "service_quality": [
                "quality", "service", "customer", "satisfaction", 
                "experience"
            ],
            "business_model": [
                "business", "model", "operation", "strategy", "approach"
            ],
            "growth_potential": [
                "growth", "expansion", "development", "potential", "future"
            ],
            "risk_management": [
                "risk", "challenge", "concern", "issue", "problem", "threat"
            ],
            "cost_efficiency": [
                "cost", "efficiency", "pricing", "budget", "financial", 
                "economic"
            ],
        }
    
    def enrich_quotes_for_export(
        self, quotes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Enrich quotes with all fields needed for proper Excel export.

        This function adds the missing fields that cause blank columns in Excel:
        - speaker_info: Speaker name, company, title
        - sentiment: Positive/negative/neutral classification
        - theme: Quote categorization based on content
        - date: Quote date from transcript metadata
        """
        enriched_quotes = []

        for quote in quotes:
            enriched_quote = quote.copy()

            # 1. Add speaker_info from transcript filename
            enriched_quote = self._add_speaker_info(enriched_quote)

            # 2. Add sentiment classification
            enriched_quote = self._add_sentiment_analysis(enriched_quote)

            # 3. Add theme categorization
            enriched_quote = self._add_theme_categorization(enriched_quote)

            # 4. Add date information
            enriched_quote = self._add_date_information(enriched_quote)

            # 5. Ensure all required fields exist
            enriched_quote = self._ensure_required_fields(enriched_quote)

            enriched_quotes.append(enriched_quote)

        return enriched_quotes

    def _add_speaker_info(self, quote: Dict[str, Any]) -> Dict[str, Any]:
        """Extract speaker information from transcript filename and quote content."""
        transcript_name = quote.get("transcript_name", "")

        # Parse speaker info from transcript filename
        # Format: "Name - Company - Title.docx"
        if " - " in transcript_name:
            parts = transcript_name.split(" - ")
            if len(parts) >= 3:
                speaker_name = parts[0].strip()
                company = parts[1].strip()
                title = parts[2].strip()

                # Clean up title if it contains date patterns
                if re.search(r"\(?\d{2}\.\d{2}\.\d{4}\)?", title):
                    title = re.sub(r"\s*\(?\d{2}\.\d{2}\.\d{4}\)?", "", title).strip()

                # Special handling for Randy_Jesberg case where name contains dash
                if speaker_name == "Randy_Jesberg" and company.lower().startswith(("former", "Former")):
                    speaker_name = f"{speaker_name} - {company}"
                    company = ""
                    if title and not title.lower().startswith(("initial", "follow")):
                        pass
                    else:
                        title = ""

                # Handle special case where company contains "Former" or similar titles
                if company.lower().startswith(("former", "Former", "current", "Current", "ex-", "ex ")):
                    title = company + (f" - {title}" if title else "")
                    company = ""

                # Additional logic: if company looks like a conversation identifier, treat it as title
                if company.lower().startswith(("initial", "Initial", "follow", "Follow", "conversation", "Conversation")):
                    title = company + (f" - {title}" if title else "")
                    company = ""

                quote["speaker_info"] = {
                    "name": speaker_name,
                    "company": company,
                    "title": title,
                }
            elif len(parts) == 2:
                speaker_name = parts[0].strip()
                company = parts[1].strip()
                quote["speaker_info"] = {
                    "name": speaker_name,
                    "company": company,
                    "title": "",
                }
            else:
                speaker_name = parts[0].strip()
                quote["speaker_info"] = {
                    "name": speaker_name,
                    "company": "",
                    "title": "",
                }
        else:
            # Fallback: use transcript name as speaker name
            quote["speaker_info"] = {
                "name": transcript_name,
                "company": "",
                "title": "",
            }

        return quote

    def _add_sentiment_analysis(self, quote: Dict[str, Any]) -> Dict[str, Any]:
        """Add sentiment classification to the quote."""
        # Skip sentiment analysis as requested by user
        quote["sentiment"] = "neutral"  # Default to neutral
        return quote

    def _add_theme_categorization(self, quote: Dict[str, Any]) -> Dict[str, Any]:
        """Add theme categorization based on quote content and focus areas."""
        text = quote.get("text", "").lower()

        # Find the best matching theme
        best_theme = "general"
        best_score = 0

        for theme, keywords in self.theme_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > best_score:
                best_score = score
                best_theme = theme

        # If no strong match, try to infer from focus areas
        if best_score == 0:
            focus_area = quote.get("focus_area_matched", "")
            if focus_area:
                # Map focus areas to themes
                focus_to_theme = {
                    "value proposition": "value_proposition",
                    "market positioning": "market_leadership",
                    "competitive advantages": "market_leadership",
                    "customer relationships": "service_quality",
                    "technology": "technology_advantages",
                    "efficiency": "cost_efficiency",
                }
                best_theme = focus_to_theme.get(focus_area, "general")

        quote["theme"] = best_theme
        return quote

    def _add_date_information(self, quote: Dict[str, Any]) -> Dict[str, Any]:
        """Add date information to the quote."""
        transcript_name = quote.get("transcript_name", "")

        # Try to extract date from transcript filename
        date_patterns = [
            r"\((\d{2}\.\d{2}\.\d{4})\)",  # (07.22.2025)
            r"(\d{2}\.\d{2}\.\d{4})",     # 07.22.2025
            r"(\d{4}-\d{2}-\d{2})",       # 2025-07-22
            r"(\d{2}/\d{2}/\d{4})",       # 07/22/2025
        ]

        date_found = None
        for pattern in date_patterns:
            match = re.search(pattern, transcript_name)
            if match:
                date_str = match.group(1)
                try:
                    # Parse the date
                    if "." in date_str:
                        date_found = datetime.strptime(date_str, "%m.%d.%Y").strftime("%Y-%m-%d")
                    elif "-" in date_str:
                        date_found = date_str
                    elif "/" in date_str:
                        date_found = datetime.strptime(date_str, "%m/%d/%Y").strftime("%Y-%m-%d")
                    break
                except ValueError:
                    continue

        # If no date found in filename, use current date or metadata timestamp
        if not date_found:
            metadata = quote.get("metadata", {})
            timestamp = metadata.get("timestamp")
            if timestamp:
                try:
                    date_found = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
                except (ValueError, TypeError):
                    date_found = datetime.now().strftime("%Y-%m-%d")
            else:
                date_found = datetime.now().strftime("%Y-%m-%d")

        quote["date"] = date_found
        return quote

    def _ensure_required_fields(self, quote: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure all required fields exist with proper fallbacks."""
        # Handle relevance_score specifically to ensure it's always numeric
        relevance_score = quote.get("relevance_score")
        if relevance_score is None or relevance_score == "" or relevance_score == "None":
            relevance_score = 0.0
        else:
            try:
                relevance_score = float(relevance_score)
            except (ValueError, TypeError):
                relevance_score = 0.0

        required_fields = {
            "id": quote.get("id", f"Q{hash(quote.get('text', '')) % 10000}"),
            "text": quote.get("text", ""),
            "speaker_info": quote.get(
                "speaker_info", {"name": "Unknown", "company": "", "title": ""}
            ),
            "transcript_name": quote.get("transcript_name", "Unknown"),
            "sentiment": quote.get("sentiment", "neutral"),
            "relevance_score": relevance_score,  # Always numeric
            "theme": quote.get("theme", "general"),
            "date": quote.get("date", ""),
            "speaker_role": quote.get("speaker_role", "unknown"),
        }

        # Update quote with required fields
        quote.update(required_fields)
        return quote

    def format_quote_for_display(self, quote: Dict[str, Any]) -> str:
        """Format a quote for display with proper speaker information."""
        if not quote:
            return ""
        
        text = quote.get("text", "")
        speaker_info = quote.get("speaker_info", {})
        transcript_name = quote.get("transcript_name", "")
        
        # Build speaker string
        speaker_parts = []
        if speaker_info.get("name"):
            speaker_parts.append(speaker_info["name"])
        if speaker_info.get("company"):
            speaker_parts.append(speaker_info["company"])
        if speaker_info.get("title"):
            speaker_parts.append(speaker_info["title"])
        
        speaker_string = ", ".join(speaker_parts) if speaker_parts else "Unknown Speaker"
        
        # Format: "quote text" - Speaker Name, Company/Title from Transcript Name
        if transcript_name and transcript_name != "Unknown":
            return f'"{text}" - {speaker_string} from {transcript_name}'
        else:
            return f'"{text}" - {speaker_string}'

    def get_quote_statistics(self, quotes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about a collection of quotes."""
        if not quotes:
            return {
                "total_quotes": 0,
                "themes": {},
                "speaker_roles": {},
                "transcripts": {},
                "average_length": 0
            }
        
        stats = {
            "total_quotes": len(quotes),
            "themes": {},
            "speaker_roles": {},
            "transcripts": {},
            "total_length": 0
        }
        
        for quote in quotes:
            # Count themes
            theme = quote.get("theme", "unknown")
            stats["themes"][theme] = stats["themes"].get(theme, 0) + 1
            
            # Count speaker roles
            role = quote.get("speaker_role", "unknown")
            stats["speaker_roles"][role] = stats["speaker_roles"].get(role, 0) + 1
            
            # Count transcripts
            transcript = quote.get("transcript_name", "unknown")
            stats["transcripts"][transcript] = stats["transcripts"].get(transcript, 0) + 1
            
            # Accumulate text length
            text = quote.get("text", "")
            stats["total_length"] += len(text)
        
        # Calculate average length
        stats["average_length"] = stats["total_length"] / len(quotes) if quotes else 0
        
        return stats
