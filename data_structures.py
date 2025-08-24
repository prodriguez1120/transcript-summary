#!/usr/bin/env python3
"""
Data Structures Module

Handles structured data models, quote validation, and structure enforcement
for the quote analysis system.
"""

import re
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class DataStructureManager:
    """Manages data structures, validation, and enforcement for quote analysis."""
    
    def __init__(self):
        """Initialize the data structure manager."""
        self.max_takeaways = 3
        self.max_strengths = 2
        self.max_weaknesses = 2
    
    def create_structured_data_model(self) -> Dict[str, Any]:
        """Create a structured data model with predefined template structure."""
        return {
            "key_takeaways": [],
            "strengths": [],
            "weaknesses": [],
            "generation_timestamp": None,  # Will be set by caller
            "total_quotes_analyzed": 0,
            "template_version": "2.0",
            "data_structure_validated": True,
        }
    
    def parse_all_sections(
        self, response_text: str, available_quotes: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Parse all sections from the response text with proper quote citations."""
        sections = {"key_takeaways": [], "strengths": [], "weaknesses": []}

        lines = response_text.split("\n")
        current_section = None
        current_insight = None
        current_quotes = []
        
        for line in lines:
            line = line.strip()
            
            # Determine current section
            current_section = self._determine_current_section(
                line, current_section, sections
            )
            
            # Parse items in current section
            if current_section and line:
                if re.match(r"^\d+\.", line):
                    self._save_current_insight(
                        sections, current_section, current_insight, current_quotes
                    )
                    current_insight = re.sub(r"^\d+\.\s*", "", line)
                    current_quotes = []
                
                elif line.startswith("- "):
                    quote_data = self._parse_quote_line(line)
                    if quote_data:
                        current_quotes.append(quote_data)
                
                elif re.match(r"^[•\-*]\s*", line):
                    self._save_current_insight(
                        sections, current_section, current_insight, current_quotes
                    )
                    current_insight = re.sub(r"^[•\-*]\s*", "", line)
                    current_quotes = []
        
        # Save the last insight
        self._save_current_insight(
            sections, current_section, current_insight, current_quotes
        )
        
        # Enforce the correct structure: 3 Key Takeaways, 2 Strengths, 2 Weaknesses
        self._enforce_correct_structure(sections)
        
        return sections
    
    def _determine_current_section(
        self, line: str, current_section: str, sections: Dict[str, List[Dict[str, Any]]]
    ) -> str:
        """Determine the current section based on line content."""
        if line.startswith("========================================"):
            return current_section
        
        if any(
            keyword in line.lower()
            for keyword in ["key takeaways", "takeaways", "key points", "main insights"]
        ):
            return "key_takeaways"

        if (
            any(
                keyword in line.lower()
                for keyword in ["strengths", "strength", "strong points", "advantages"]
            )
            and "key takeaways" not in line.lower()
        ):
            # Only switch to strengths if we have completed all 3 key takeaways
            if (
                current_section == "key_takeaways"
                and len(sections["key_takeaways"]) < self.max_takeaways
            ):
                return current_section
            return "strengths"

        if any(
            keyword in line.lower()
            for keyword in [
                "weaknesses",
                "weakness",
                "weak points",
                "challenges",
                "concerns",
            ]
        ):
            # Only switch to weaknesses if we have completed all 2 strengths
            if current_section == "strengths" and len(sections["strengths"]) < self.max_strengths:
                return current_section
            return "weaknesses"
        
        return current_section
    
    def _parse_quote_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a quote line and extract quote data."""
        # Parse quote with citation: "quote text" - Speaker Name, Company/Title from Transcript Name
        quote_match = re.match(r'^- "([^"]+)" - (.+?) from (.+)$', line)
        if quote_match:
            return {
                "text": quote_match.group(1),
                "speaker_info": quote_match.group(2),
                "transcript_name": quote_match.group(3),
            }
        
        # Try alternative format: "quote text" - Speaker Name, Company/Title
        alt_match = re.match(r'^- "([^"]+)" - (.+)$', line)
        if alt_match:
            return {
                "text": alt_match.group(1),
                "speaker_info": alt_match.group(2),
                "transcript_name": "Unknown",
            }
        
        # Try format without quotes: - text - Speaker Name, Company/Title from Transcript Name
        no_quote_match = re.match(r"^- (.+?) - (.+?) from (.+)$", line)
        if no_quote_match:
            return {
                "text": no_quote_match.group(1),
                "speaker_info": no_quote_match.group(2),
                "transcript_name": no_quote_match.group(3),
            }
        
        # Try format: - text - Speaker Name, Company/Title (without "from Transcript Name")
        simple_match = re.match(r"^- (.+?) - (.+)$", line)
        if simple_match:
            return {
                "text": simple_match.group(1),
                "speaker_info": simple_match.group(2),
                "transcript_name": "Unknown",
            }
        
        return None
    
    def _save_current_insight(
        self,
        sections: Dict[str, List[Dict[str, Any]]],
        current_section: str,
        current_insight: str,
        current_quotes: List[Dict[str, Any]],
    ):
        """Save current insight with quotes to the appropriate section."""
        if current_insight and current_quotes:
            item = {"insight": current_insight, "supporting_quotes": current_quotes}

            if current_section == "key_takeaways":
                sections["key_takeaways"].append(item)
            elif current_section == "strengths":
                sections["strengths"].append(item)
            elif current_section == "weaknesses":
                sections["weaknesses"].append(item)
            else:
                # If no section is set, add to key takeaways for now
                sections["key_takeaways"].append(item)
    
    def _enforce_correct_structure(self, sections: Dict[str, List[Dict[str, Any]]]):
        """Enforce the correct structure: 3 Key Takeaways, 2 Strengths, 2 Weaknesses."""
        # Move extra strengths to key takeaways
        if len(sections["strengths"]) > self.max_strengths:
            extra_strengths = sections["strengths"][self.max_strengths:]
            sections["strengths"] = sections["strengths"][:self.max_strengths]
            sections["key_takeaways"].extend(extra_strengths)
        
        # Move extra weaknesses to key takeaways
        if len(sections["weaknesses"]) > self.max_weaknesses:
            extra_weaknesses = sections["weaknesses"][self.max_weaknesses:]
            sections["weaknesses"] = sections["weaknesses"][:self.max_weaknesses]
            sections["key_takeaways"].extend(extra_weaknesses)
        
        # Ensure we have exactly 3 key takeaways
        while len(sections["key_takeaways"]) < self.max_takeaways:
            if len(sections["strengths"]) > self.max_strengths:
                sections["key_takeaways"].append(sections["strengths"].pop())
            elif len(sections["weaknesses"]) > self.max_weaknesses:
                sections["key_takeaways"].append(sections["weaknesses"].pop())
            else:
                break
        
        # Content-based redistribution
        self._redistribute_by_content(sections)
        
        # Fallback duplication if needed
        self._duplicate_insights_if_needed(sections)
        
        return sections
    
    def _redistribute_by_content(self, sections: Dict[str, List[Dict[str, Any]]]):
        """Redistribute insights based on content keywords."""
        strengths_keywords = [
            "technology",
            "proprietary",
            "turnaround",
            "rapid",
            "advantage",
            "capability",
            "efficiency",
            "benefit",
        ]
        weaknesses_keywords = [
            "limit",
            "constraint",
            "challenge",
            "risk",
            "unpredictable",
            "tam",
            "market size",
            "impact",
        ]
        
        # Move key takeaways to strengths if they fit better
        if (
            len(sections["strengths"]) < self.max_strengths
            and len(sections["key_takeaways"]) > self.max_takeaways
        ):
            for i, takeaway in enumerate(sections["key_takeaways"]):
                if (
                    len(sections["strengths"]) >= self.max_strengths
                    or len(sections["key_takeaways"]) <= self.max_takeaways
                ):
                    break
                insight_text = takeaway.get("insight", "").lower()
                if any(keyword in insight_text for keyword in strengths_keywords):
                    sections["strengths"].append(sections["key_takeaways"].pop(i))
                    break
        
        # Move key takeaways to weaknesses if they fit better
        if (
            len(sections["weaknesses"]) < self.max_weaknesses
            and len(sections["key_takeaways"]) > self.max_takeaways
        ):
            for i, takeaway in enumerate(sections["key_takeaways"]):
                if (
                    len(sections["weaknesses"]) >= self.max_weaknesses
                    or len(sections["key_takeaways"]) <= self.max_takeaways
                ):
                    break
                insight_text = takeaway.get("insight", "").lower()
                if any(keyword in insight_text for keyword in weaknesses_keywords):
                    sections["weaknesses"].append(sections["key_takeaways"].pop(i))
                    break
        
        # Move extra key takeaways to appropriate sections
        while len(sections["key_takeaways"]) > self.max_takeaways:
            if len(sections["strengths"]) < self.max_strengths:
                extra_takeaway = sections["key_takeaways"].pop()
                sections["strengths"].append(extra_takeaway)
            elif len(sections["weaknesses"]) < self.max_weaknesses:
                extra_takeaway = sections["key_takeaways"].pop()
                sections["weaknesses"].append(extra_takeaway)
            else:
                break
    
    def _duplicate_insights_if_needed(self, sections: Dict[str, List[Dict[str, Any]]]):
        """Duplicate insights if needed to reach target counts."""
        # Duplicate key takeaways if needed
        if len(sections["key_takeaways"]) < self.max_takeaways:
            self._duplicate_insights_for_section(
                sections,
                "key_takeaways",
                self.max_takeaways,
                [
                    "market",
                    "leadership",
                    "competitive",
                    "value",
                    "proposition",
                    "presence",
                    "footprint",
                    "demand",
                ],
            )
        
        # Duplicate strengths if needed
        if len(sections["strengths"]) < self.max_strengths:
            self._duplicate_insights_for_section(
                sections,
                "strengths",
                self.max_strengths,
                [
                    "technology",
                    "proprietary",
                    "turnaround",
                    "rapid",
                    "advantage",
                    "capability",
                    "efficiency",
                    "benefit",
                ],
            )
        
        # Duplicate weaknesses if needed
        if len(sections["weaknesses"]) < self.max_weaknesses:
            self._duplicate_insights_for_section(
                sections,
                "weaknesses",
                self.max_weaknesses,
                [
                    "limit",
                    "constraint",
                    "challenge",
                    "risk",
                    "unpredictable",
                    "tam",
                    "market size",
                    "impact",
                ],
            )

    def _duplicate_insights_for_section(
        self,
        sections: Dict[str, List[Dict[str, Any]]],
        section_name: str,
        target_count: int,
        keywords: List[str],
    ):
        """Duplicate insights for a specific section to reach target count."""
        all_available_insights = []
        for key in ["key_takeaways", "strengths", "weaknesses"]:
            if key != section_name:
                all_available_insights.extend(sections[key])
        
        # Score insights by relevance to section
        scored_insights = []
        for insight in all_available_insights:
            insight_text = insight.get("insight", "").lower()
            score = sum(1 for keyword in keywords if keyword in insight_text)
            scored_insights.append((score, insight))
        
        # Sort by score and duplicate the best ones
        scored_insights.sort(key=lambda x: x[0], reverse=True)
        
        section_prefix = {
            "key_takeaways": "Additional insight",
            "strengths": "Additional strength",
            "weaknesses": "Additional weakness",
        }
        
        while len(sections[section_name]) < target_count and scored_insights:
            score, insight = scored_insights.pop(0)
            duplicated_insight = {
                "insight": f"{section_prefix[section_name]}: {insight.get('insight', '')}",
                "supporting_quotes": insight.get("supporting_quotes", [])[:1],
            }
            sections[section_name].append(duplicated_insight)

    def find_supporting_quotes(
        self, insight: str, available_quotes: List[Dict[str, Any]], max_quotes: int = 3
    ) -> List[Dict[str, Any]]:
        """Find quotes that support a given insight."""
        if not insight or not available_quotes:
            return []
        
        # Extract key terms from insight
        insight_lower = insight.lower()
        key_terms = [word for word in insight_lower.split() if len(word) > 3]
        
        # Score quotes based on relevance to insight
        scored_quotes = []
        for quote in available_quotes:
            quote_text = quote.get("text", "").lower()
            score = 0
            
            # Score based on term overlap
            for term in key_terms:
                if term in quote_text:
                    score += 1
            
            # Bonus for exact phrase matches
            for phrase in insight_lower.split(","):
                phrase = phrase.strip()
                if len(phrase) > 5 and phrase in quote_text:
                    score += 2
            
            if score > 0:
                scored_quotes.append((score, quote))
        
        # Sort by score and return top quotes
        scored_quotes.sort(key=lambda x: x[0], reverse=True)
        return [quote for score, quote in scored_quotes[:max_quotes]]

    def filter_questions_from_takeaways(
        self, takeaways: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Filter out questions from takeaways."""
        return [t for t in takeaways if not self._is_question(t.get("insight", ""))]

    def filter_questions_from_strengths(
        self, strengths: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Filter out questions from strengths."""
        return [s for s in strengths if not self._is_question(s.get("insight", ""))]

    def filter_questions_from_weaknesses(
        self, weaknesses: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Filter out questions from weaknesses."""
        return [w for w in weaknesses if not self._is_question(w.get("insight", ""))]

    def _is_question(self, text: str) -> bool:
        """Determine if text is a question."""
        if not text:
            return False
        
        # More selective question detection - only filter out actual interrogative questions
        # Don't filter out insights that start with question words but are actually statements
        text_lower = text.lower()
        
        # Only filter out if it ends with a question mark or is clearly an interrogative
        if text.strip().endswith("?"):
            return True
        
        # Check for interrogative patterns that indicate actual questions, not insights
        interrogative_patterns = [
            "what do you think",
            "how do you feel",
            "why do you believe",
            "when would you",
            "where should we",
            "who should we",
            "which option",
        ]
        
        return any(pattern in text_lower for pattern in interrogative_patterns)

    def validate_quote_structure(self, quote: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and fix quote structure to ensure all required fields exist."""
        required_fields = {
            "id": quote.get("id", f"Q{hash(quote.get('text', '')) % 10000}"),
            "text": quote.get("text", ""),
            "speaker_info": quote.get(
                "speaker_info", {"name": "Unknown", "company": "", "title": ""}
            ),
            "transcript_name": quote.get("transcript_name", "Unknown"),
            "sentiment": quote.get("sentiment", "neutral"),
            "relevance_score": self._ensure_numeric_relevance_score(quote.get("relevance_score")),
            "theme": quote.get("theme", "general"),
            "date": quote.get("date", ""),
            "speaker_role": quote.get("speaker_role", "unknown"),
        }
        
        # Update quote with required fields
        quote.update(required_fields)
        return quote
    
    def _ensure_numeric_relevance_score(self, relevance_score) -> float:
        """Ensure relevance score is always numeric."""
        if (
            relevance_score is None
            or relevance_score == ""
            or relevance_score == "None"
        ):
            return 0.0
        else:
            try:
                return float(relevance_score)
            except (ValueError, TypeError):
                return 0.0

    def get_structure_statistics(self, sections: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Get statistics about the structure of analysis sections."""
        stats = {
            "key_takeaways_count": len(sections.get("key_takeaways", [])),
            "strengths_count": len(sections.get("strengths", [])),
            "weaknesses_count": len(sections.get("weaknesses", [])),
            "total_insights": 0,
            "quotes_per_section": {},
            "structure_compliant": False
        }
        
        # Count total insights
        stats["total_insights"] = (
            stats["key_takeaways_count"] + 
            stats["strengths_count"] + 
            stats["weaknesses_count"]
        )
        
        # Count quotes per section
        for section_name in ["key_takeaways", "strengths", "weaknesses"]:
            section = sections.get(section_name, [])
            total_quotes = sum(len(item.get("supporting_quotes", [])) for item in section)
            stats["quotes_per_section"][section_name] = total_quotes
        
        # Check if structure is compliant
        stats["structure_compliant"] = (
            stats["key_takeaways_count"] == self.max_takeaways and
            stats["strengths_count"] == self.max_strengths and
            stats["weaknesses_count"] == self.max_weaknesses
        )
        
        return stats
