#!/usr/bin/env python3
"""
Quote Analysis Tool for FlexXray Transcripts

This is the main entry point that orchestrates the modular quote analysis system.
The tool extracts quotes from transcript documents and creates:
1. Three key summary perspectives with supporting quotes
2. Strengths bucket with supporting evidence
3. Weaknesses bucket with supporting evidence

Uses the existing vector database infrastructure without modifying existing code.
"""

import os
import json
import re
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
import time
from datetime import datetime
import logging

# Load environment variables from centralized configuration
from env_config import get_env_config, get_openai_api_key

# Import logging configuration
from logging_config import setup_logger

# Set up logger for this module
logger = setup_logger(__name__)

# Import our modular components
from quote_analysis_core import QuoteAnalysisTool
from quote_extraction import QuoteExtractor
from vector_database import VectorDatabaseManager
from perspective_analysis import PerspectiveAnalyzer
from export_utils import ExportManager
from prompt_config import get_prompt_config

# Import our new refactored modules
from quote_processing import QuoteProcessor
from summary_generation import SummaryGenerator
from data_structures import DataStructureManager


class ModularQuoteAnalysisTool(QuoteAnalysisTool):
    """Enhanced quote analysis tool using modular components."""
    
    def __init__(
        self, api_key: str = None, chroma_persist_directory: str = "./chroma_db"
    ):
        """Initialize the modular quote analysis tool."""
        super().__init__(api_key, chroma_persist_directory)
        
        # Initialize modular components
        self.quote_extractor = QuoteExtractor(
            min_quote_length=self.min_quote_length,
            max_quote_length=self.max_quote_length,
        )
        
        self.vector_db_manager = VectorDatabaseManager(chroma_persist_directory)
        
        # Test vector database initialization and log stats
        try:
            db_stats = self.vector_db_manager.get_vector_database_stats()
            self.logger.info(f"Vector database initialization test: {db_stats}")
            if db_stats.get("available"):
                self.logger.info(
                    f"✅ ChromaDB path valid, {db_stats.get('total_quotes', 0)} quotes available"
                )
                if (
                    hasattr(self.vector_db_manager, "embedding_function")
                    and self.vector_db_manager.embedding_function
                ):
                    self.logger.info(
                        f"✅ Using OpenAI embeddings: {self.vector_db_manager.embedding_function.model_name}"
                    )
                else:
                    self.logger.warning(
                        "⚠️ Using ChromaDB default embeddings (OpenAI not configured)"
                    )
            else:
                self.logger.warning("❌ Vector database not available")
        except Exception as e:
            self.logger.error(f"Vector database test failed: {e}")

        # Use the API key from the parent class instead of calling os.getenv again
        # Use the API key from the parent class (which comes from centralized config)
        self.perspective_analyzer = PerspectiveAnalyzer(api_key=self.api_key)
        self.perspective_analyzer.set_vector_db_manager(self.vector_db_manager)
        
        self.export_manager = ExportManager()
        
        # Initialize our new refactored components
        self.quote_processor = QuoteProcessor()
        self.data_structure_manager = DataStructureManager()
        
        # Initialize summary generator with OpenAI client and prompt config
        prompt_config = get_prompt_config()
        # Use the OpenAI client from the parent class
        self.summary_generator = SummaryGenerator(self.client, prompt_config)
        
        # Define key_perspectives explicitly to ensure it's always available
        self.key_perspectives = {
            "business_model": {
                "title": "Business Model & Market Position",
                "description": "How FlexXray operates, serves customers, and competes in the market",
                "focus_areas": [
                    "value proposition",
                    "customer relationships",
                    "market positioning",
                    "competitive advantages",
                ],
            },
            "growth_potential": {
                "title": "Growth Potential & Market Opportunity",
                "description": "FlexXray's expansion opportunities, market trends, and future prospects",
                "focus_areas": [
                    "market expansion",
                    "product development",
                    "industry trends",
                    "growth drivers",
                ],
            },
            "risk_factors": {
                "title": "Risk Factors & Challenges",
                "description": "Key risks, challenges, and areas of concern for FlexXray's business",
                "focus_areas": [
                    "service quality issues",
                    "operational challenges",
                    "competitive threats",
                    "market risks",
                ],
            },
        }

    def extract_text_from_document(self, doc_path: str) -> str:
        """Extract text content from a Word document using the quote extractor."""
        return self.quote_extractor.extract_text_from_document(doc_path)

    def extract_quotes_from_text(
        self, text: str, transcript_name: str
    ) -> List[Dict[str, Any]]:
        """Extract meaningful quotes from transcript text using the quote extractor."""
        return self.quote_extractor.extract_quotes_from_text(text, transcript_name)

    def store_quotes_in_vector_db(
        self, quotes: List[Dict[str, Any]], batch_size: int = 100
    ) -> bool:
        """Store quotes in the vector database using the vector database manager."""
        return self.vector_db_manager.store_quotes_in_vector_db(quotes, batch_size)

    def semantic_search_quotes(
        self, query: str, n_results: int = 10, filter_metadata: Dict = None
    ) -> List[Dict[str, Any]]:
        """Perform semantic search for quotes using the vector database manager."""
        return self.vector_db_manager.semantic_search_quotes(
            query, n_results, filter_metadata
        )

    def search_quotes_with_speaker_filter(
        self, query: str, speaker_role: str = "expert", n_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for quotes with speaker role filtering using the vector database manager."""
        return self.vector_db_manager.search_quotes_with_speaker_filter(
            query, speaker_role, n_results
        )

    def clear_vector_database(self) -> bool:
        """Clear all data from the vector database using the vector database manager."""
        return self.vector_db_manager.clear_vector_database()

    def get_vector_database_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database using the vector database manager."""
        return self.vector_db_manager.get_vector_database_stats()

    def verify_embeddings(self, sample_size: int = 3) -> Dict[str, Any]:
        """Verify that stored documents actually have embeddings."""
        return self.vector_db_manager.verify_stored_embeddings(sample_size)

    def force_embedding_function_reattachment(self) -> bool:
        """Force reattachment of embedding functions to collections."""
        return self.vector_db_manager.force_embedding_function_reattachment()

    def get_quotes_by_perspective(
        self, perspective_key: str, perspective_data: dict, n_results: int = 20
    ) -> List[Dict[str, Any]]:
        """Get quotes relevant to a specific perspective using the vector database manager."""
        return self.vector_db_manager.get_quotes_by_perspective(
            perspective_key, perspective_data, n_results
        )

    def categorize_quotes_by_sentiment(
        self, quotes: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize quotes by sentiment using the vector database manager."""
        return self.vector_db_manager.categorize_quotes_by_sentiment(quotes)

    def _verify_quotes_storage(self, quotes: List[Dict[str, Any]]) -> None:
        """Verify that quotes are stored properly by querying back known quotes."""
        if not quotes or not self.vector_db_manager.quotes_collection:
            return

        try:
            self.logger.info("🔍 Verifying quotes storage in vector database...")

            # Test with a few sample quotes to verify storage
            test_quotes = quotes[:3]  # Test first 3 quotes

            for i, quote in enumerate(test_quotes):
                quote_text = quote.get("text", "").strip()
                if not quote_text:
                    continue

                # Use first 50 characters as search query
                search_query = quote_text[:50]
                transcript_name = quote.get("transcript_name", "Unknown")

                self.logger.info(f"  Testing quote {i+1} from {transcript_name}...")

                # Search for this specific quote
                search_results = self.vector_db_manager.semantic_search_quotes(
                    query=search_query, n_results=5
                )

                # Check if we found the original quote
                found_original = False
                for result in search_results:
                    if (
                        result.get("text", "").strip() == quote_text
                        or result.get("metadata", {}).get("transcript_name")
                        == transcript_name
                    ):
                        found_original = True
                        distance = result.get("distance", "N/A")
                        self.logger.info(f"    ✅ Quote found! Distance: {distance}")
                        break

                if not found_original:
                    self.logger.warning(f"    ⚠️ Quote not found in search results")

                # Also test exact text search
                exact_results = self.vector_db_manager.semantic_search_quotes(
                    query=f'"{quote_text}"', n_results=3  # Exact phrase search
                )

                if exact_results:
                    self.logger.info(f"    ✅ Exact text search successful")
                else:
                    self.logger.warning(f"    ⚠️ Exact text search failed")

            # Get final database stats
            final_stats = self.vector_db_manager.get_vector_database_stats()
            self.logger.info(
                f"✅ Storage verification complete. Database now contains {final_stats.get('total_quotes', 0)} quotes"
            )

        except Exception as e:
            self.logger.error(f"❌ Quote storage verification failed: {e}")

    def analyze_perspective_with_quotes(
        self,
        perspective_key: str,
        perspective_data: dict,
        all_quotes: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Analyze a perspective using the perspective analyzer."""
        return self.perspective_analyzer.analyze_perspective_with_quotes(
            perspective_key, perspective_data, all_quotes
        )

    def generate_company_summary_page(
        self, all_quotes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate a comprehensive company summary page using OpenAI with batch processing."""
        if not all_quotes:
            return {}
        
        logger.info(
            "Generating company summary page using OpenAI with batch processing..."
        )
        
        # Clean and validate quotes
        cleaned_quotes = self._clean_and_validate_quotes(all_quotes)
        if not cleaned_quotes:
            return {}
        
        # Filter to expert quotes only
        expert_quotes = self.get_expert_quotes_only(cleaned_quotes)
        if not expert_quotes:
            logger.warning("No expert quotes found after filtering")
            return {}
        
        # Get diverse quotes for analysis - use batch processing to handle more quotes
        diverse_quotes = self._get_diverse_quotes(
            expert_quotes, "summary", 60
        )  # Increased to 60 for better selection
        
        # Use the summary generator for better results
        return self.summary_generator.generate_company_summary_direct(diverse_quotes)
    
    # Company summary generation moved to SummaryGenerator module
    # Use self.summary_generator.generate_company_summary_direct() instead
    
    # Batch processing methods moved to SummaryGenerator module
    # Use self.summary_generator.generate_company_summary_with_batching() instead
    
    def _generate_single_batch_summary(
        self, batch_quotes: List[Dict[str, Any]], batch_num: int
    ) -> Dict[str, Any]:
        """Generate summary for a single batch of quotes."""
        try:
            # Create summary prompt for this batch
            summary_prompt = self._create_summary_prompt(batch_quotes)
            
            # Get prompt configuration
            prompt_config = get_prompt_config()
            params = prompt_config.get_prompt_parameters("company_summary")
            
            # Call OpenAI for this batch
            response = self.client.chat.completions.create(
                model=params.get("model", "gpt-4"),
                messages=[
                    {
                        "role": "system",
                        "content": prompt_config.get_system_message("company_summary"),
                    },
                    {"role": "user", "content": summary_prompt},
                ],
                temperature=params.get("temperature", 0.3),
                max_tokens=params.get("max_tokens", 3000),
            )
            
            # Parse batch response
            batch_data = self._parse_summary_response(
                response.choices[0].message.content, batch_quotes
            )
            batch_data["batch_number"] = batch_num
            batch_data["quotes_processed"] = len(batch_quotes)
            
            return batch_data
            
        except Exception as e:
            logger.error(f"Error generating batch {batch_num} summary: {e}")
            return {}
    
    def _combine_batch_summaries(
        self, batch_results: List[Dict[str, Any]], all_quotes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Combine multiple batch summaries into a final comprehensive summary."""
        logger.info("Combining batch summaries...")
        
        # Initialize final summary structure
        final_summary = self._create_structured_data_model()
        final_summary["total_quotes_analyzed"] = len(all_quotes)
        final_summary["batch_processing_used"] = True
        final_summary["total_batches"] = len(batch_results)
        
        # Combine key takeaways from all batches
        all_key_takeaways = []
        for batch in batch_results:
            if "key_takeaways" in batch and isinstance(batch["key_takeaways"], list):
                all_key_takeaways.extend(batch["key_takeaways"])
        
        # Deduplicate and select best key takeaways (ensure exactly 3 per theme)
        final_summary["key_takeaways"] = self._consolidate_key_takeaways(
            all_key_takeaways
        )
        
        # Combine strengths from all batches
        all_strengths = []
        for batch in batch_results:
            if "strengths" in batch and isinstance(batch["strengths"], list):
                all_strengths.extend(batch["strengths"])
        
        # Deduplicate and select best strengths (ensure exactly 2 per theme)
        final_summary["strengths"] = self._consolidate_strengths(all_strengths)
        
        # Combine weaknesses from all batches
        all_weaknesses = []
        for batch in batch_results:
            if "weaknesses" in batch and isinstance(batch["weaknesses"], list):
                all_weaknesses.extend(batch["weaknesses"])
        
        # Deduplicate and select best weaknesses (ensure exactly 2 per theme)
        final_summary["weaknesses"] = self._consolidate_weaknesses(all_weaknesses)
        
        logger.info("Batch summaries combined successfully")
        return final_summary
    
    def _consolidate_key_takeaways(
        self, all_takeaways: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Consolidate key takeaways ensuring exactly 3 quotes per theme."""
        # Group by theme
        theme_groups = {}
        for takeaway in all_takeaways:
            theme = takeaway.get("theme", "")
            if theme:
                if theme not in theme_groups:
                    theme_groups[theme] = []
                theme_groups[theme].append(takeaway)
        
        # Select best 3 quotes per theme
        consolidated = []
        for theme, takeaways in theme_groups.items():
            # Sort by relevance/quality if available
            sorted_takeaways = sorted(
                takeaways, key=lambda x: len(x.get("quotes", [])), reverse=True
            )
            best_takeaway = sorted_takeaways[0] if sorted_takeaways else {}
            
            # Ensure exactly 3 quotes
            quotes = best_takeaway.get("quotes", [])
            if len(quotes) >= 3:
                best_takeaway["quotes"] = quotes[:3]
            elif len(quotes) < 3:
                # Pad with placeholder if needed
                while len(quotes) < 3:
                    quotes.append(
                        {
                            "quote": "Additional quote needed",
                            "speaker": "Unknown",
                            "document": "Unknown",
                        }
                    )
                best_takeaway["quotes"] = quotes
            
            consolidated.append(best_takeaway)
        
        return consolidated
    
    def _consolidate_strengths(
        self, all_strengths: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Consolidate strengths ensuring exactly 2 quotes per theme."""
        # Similar logic to key takeaways but for 2 quotes
        theme_groups = {}
        for strength in all_strengths:
            theme = strength.get("theme", "")
            if theme:
                if theme not in theme_groups:
                    theme_groups[theme] = []
                theme_groups[theme].append(strength)
        
        consolidated = []
        for theme, strengths in theme_groups.items():
            sorted_strengths = sorted(
                strengths, key=lambda x: len(x.get("quotes", [])), reverse=True
            )
            best_strength = sorted_strengths[0] if sorted_strengths else {}
            
            quotes = best_strength.get("quotes", [])
            if len(quotes) >= 2:
                best_strength["quotes"] = quotes[:2]
            elif len(quotes) < 2:
                while len(quotes) < 2:
                    quotes.append(
                        {
                            "quote": "Additional quote needed",
                            "speaker": "Quote Required",
                            "document": "Additional Analysis Needed",
                        }
                    )
                best_strength["quotes"] = quotes
            
            consolidated.append(best_strength)
        
        return consolidated
    
    def _consolidate_weaknesses(
        self, all_weaknesses: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Consolidate weaknesses ensuring exactly 2 quotes per theme."""
        # Similar logic to strengths
        theme_groups = {}
        for weakness in all_weaknesses:
            theme = weakness.get("theme", "")
            if theme:
                if theme not in theme_groups:
                    theme_groups[theme] = []
                theme_groups[theme].append(weakness)
        
        consolidated = []
        for theme, weaknesses in theme_groups.items():
            sorted_weaknesses = sorted(
                weaknesses, key=lambda x: len(x.get("quotes", [])), reverse=True
            )
            best_weakness = sorted_weaknesses[0] if sorted_weaknesses else {}
            
            quotes = best_weakness.get("quotes", [])
            if len(quotes) >= 2:
                best_weakness["quotes"] = quotes[:2]
            elif len(quotes) < 2:
                while len(quotes) < 2:
                    quotes.append(
                        {
                            "quote": "Additional quote needed",
                            "speaker": "Quote Required",
                            "document": "Additional Analysis Needed",
                        }
                    )
                best_weakness["quotes"] = quotes
            
            consolidated.append(best_weakness)
        
        return consolidated

    # Summary generation methods moved to SummaryGenerator module
    # Use self.summary_generator methods instead
    
    # Validation methods moved to SummaryGenerator module

    # Validation methods moved to SummaryGenerator module

    # Validation methods moved to SummaryGenerator module

    def _parse_all_sections(
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
                and len(sections["key_takeaways"]) < 3
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
            if current_section == "strengths" and len(sections["strengths"]) < 2:
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
        MAX_TAKEAWAYS = 3
        MAX_STRENGTHS = 2
        MAX_WEAKNESSES = 2
        
        # Move extra strengths to key takeaways
        if len(sections["strengths"]) > MAX_STRENGTHS:
            extra_strengths = sections["strengths"][MAX_STRENGTHS:]
            sections["strengths"] = sections["strengths"][:MAX_STRENGTHS]
            sections["key_takeaways"].extend(extra_strengths)
        
        # Move extra weaknesses to key takeaways
        if len(sections["weaknesses"]) > MAX_WEAKNESSES:
            extra_weaknesses = sections["weaknesses"][MAX_WEAKNESSES:]
            sections["weaknesses"] = sections["weaknesses"][:MAX_WEAKNESSES]
            sections["key_takeaways"].extend(extra_weaknesses)
        
        # Ensure we have exactly 3 key takeaways
        while len(sections["key_takeaways"]) < MAX_TAKEAWAYS:
            if len(sections["strengths"]) > MAX_STRENGTHS:
                sections["key_takeaways"].append(sections["strengths"].pop())
            elif len(sections["weaknesses"]) > MAX_WEAKNESSES:
                sections["key_takeaways"].append(sections["weaknesses"].pop())
            else:
                break
        
        # Content-based redistribution
        self._redistribute_by_content(sections, MAX_STRENGTHS, MAX_WEAKNESSES)
        
        # Fallback duplication if needed
        self._duplicate_insights_if_needed(
            sections, MAX_TAKEAWAYS, MAX_STRENGTHS, MAX_WEAKNESSES
        )
        
        return sections
    
    def _redistribute_by_content(
        self,
        sections: Dict[str, List[Dict[str, Any]]],
        max_strengths: int,
        max_weaknesses: int,
    ):
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
            len(sections["strengths"]) < max_strengths
            and len(sections["key_takeaways"]) > 3
        ):
            for i, takeaway in enumerate(sections["key_takeaways"]):
                if (
                    len(sections["strengths"]) >= max_strengths
                    or len(sections["key_takeaways"]) <= 3
                ):
                    break
                insight_text = takeaway.get("insight", "").lower()
                if any(keyword in insight_text for keyword in strengths_keywords):
                    sections["strengths"].append(sections["key_takeaways"].pop(i))
                    break
        
        # Move key takeaways to weaknesses if they fit better
        if (
            len(sections["weaknesses"]) < max_weaknesses
            and len(sections["key_takeaways"]) > 3
        ):
            for i, takeaway in enumerate(sections["key_takeaways"]):
                if (
                    len(sections["weaknesses"]) >= max_weaknesses
                    or len(sections["key_takeaways"]) <= 3
                ):
                    break
                insight_text = takeaway.get("insight", "").lower()
                if any(keyword in insight_text for keyword in weaknesses_keywords):
                    sections["weaknesses"].append(sections["key_takeaways"].pop(i))
                    break
        
        # Move extra key takeaways to appropriate sections
        while len(sections["key_takeaways"]) > 3:
            if len(sections["strengths"]) < max_strengths:
                extra_takeaway = sections["key_takeaways"].pop()
                sections["strengths"].append(extra_takeaway)
            elif len(sections["weaknesses"]) < max_weaknesses:
                extra_takeaway = sections["key_takeaways"].pop()
                sections["weaknesses"].append(extra_takeaway)
            else:
                break
    
    def _duplicate_insights_if_needed(
        self,
        sections: Dict[str, List[Dict[str, Any]]],
        max_takeaways: int,
        max_strengths: int,
        max_weaknesses: int,
    ):
        """Duplicate insights if needed to reach target counts."""
        # Duplicate key takeaways if needed
        if len(sections["key_takeaways"]) < max_takeaways:
            self._duplicate_insights_for_section(
                sections,
                "key_takeaways",
                max_takeaways,
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
        if len(sections["strengths"]) < max_strengths:
            self._duplicate_insights_for_section(
                sections,
                "strengths",
                max_strengths,
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
        if len(sections["weaknesses"]) < max_weaknesses:
            self._duplicate_insights_for_section(
                sections,
                "weaknesses",
                max_weaknesses,
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

    def _find_supporting_quotes(
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

    def _validate_and_supplement_takeaways(
        self, takeaways: List[Dict[str, Any]], available_quotes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Validate and supplement takeaways with supporting quotes."""
        # This would implement validation and supplementation logic
        # For brevity, returning the input as-is
        return takeaways

    def _filter_questions_from_takeaways(
        self, takeaways: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Filter out questions from takeaways."""
        return [t for t in takeaways if not self._is_question(t.get("insight", ""))]

    def _filter_questions_from_strengths(
        self, strengths: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Filter out questions from strengths."""
        return [s for s in strengths if not self._is_question(s.get("insight", ""))]

    def _filter_questions_from_weaknesses(
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

    def export_company_summary_page(
        self, summary_data: Dict[str, Any], output_file: str = None
    ) -> str:
        """Export company summary page using the export manager."""
        # Ensure proper formatting of quotes with speaker information
        for section_key in ["key_takeaways", "strengths", "weaknesses"]:
            if section_key in summary_data:
                for item in summary_data[section_key]:
                    if "supporting_quotes" in item:
                        for quote in item["supporting_quotes"]:
                            # Ensure quote has proper speaker info formatting
                            if "speaker_info" in quote and quote["speaker_info"]:
                                # Format: "quote text" - Speaker Name, Company/Title from Transcript Name
                                if (
                                    quote.get("transcript_name")
                                    and quote["transcript_name"] != "Unknown"
                                ):
                                    quote["formatted_text"] = (
                                        f"\"{quote['text']}\" - {quote['speaker_info']} from {quote['transcript_name']}"
                                    )
                                else:
                                    quote["formatted_text"] = (
                                        f"\"{quote['text']}\" - {quote['speaker_info']}"
                                    )
                            else:
                                quote["formatted_text"] = quote["text"]
        
        return self.export_manager.export_company_summary_page(
            summary_data, output_file
        )

    def export_company_summary_to_excel(
        self, summary_data: Dict[str, Any], output_file: str = None
    ) -> str:
        """Export company summary page to Excel using the export manager."""
        return self.export_manager.export_company_summary_to_excel(
            summary_data, output_file
        )

    def export_quotes_to_excel(
        self, quotes_data: List[Dict[str, Any]], output_file: str = None
    ) -> str:
        """Export quotes to Excel with proper text wrapping using the export manager."""
        # Enrich quotes with all required fields before export
        enriched_quotes = self.enrich_quotes_for_export(quotes_data)
        return self.export_manager.export_quotes_to_excel(enriched_quotes, output_file)

    def save_quote_analysis(self, results: Dict[str, Any], output_file: str = None):
        """Save quote analysis results using the export manager."""
        return self.export_manager.save_quote_analysis(results, output_file)

    def export_quote_analysis_to_text(
        self, results: Dict[str, Any], output_file: str = None
    ):
        """Export quote analysis results to text using the export manager."""
        return self.export_manager.export_quote_analysis_to_text(results, output_file)

    def process_transcripts_for_quotes(self, directory_path: str) -> Dict[str, Any]:
        """Process transcripts and generate comprehensive quote analysis."""
        print(f"Processing transcripts from: {directory_path}")
        
        # Get transcript files
        transcript_files = []
        for file_path in Path(directory_path).glob("*.docx"):
            transcript_files.append(str(file_path))
        
        if not transcript_files:
            print("No transcript files found")
            return {}
        
        print(f"Found {len(transcript_files)} transcript files")
        
        # Process each transcript
        all_quotes = []
        for file_path in transcript_files:
            transcript_name = Path(file_path).stem
            print(f"Processing: {transcript_name}")
            
            # Extract text (this would need document processing implementation)
            text = self.extract_text_from_document(file_path)
            if not text:
                print(f"No text extracted from {transcript_name}")
                continue
            
            # Extract quotes
            quotes = self.extract_quotes_from_text(text, transcript_name)
            if quotes:
                all_quotes.extend(quotes)
                print(f"Extracted {len(quotes)} quotes from {transcript_name}")
            else:
                print(f"No quotes extracted from {transcript_name}")
        
        if not all_quotes:
            print("No quotes extracted from any transcripts")
            return {}
        
        print(f"Total quotes extracted: {len(all_quotes)}")
        
        # Store quotes in vector database
        if self.vector_db_manager.quotes_collection:
            self.store_quotes_in_vector_db(all_quotes)
        
            # Verify quotes are stored properly by querying back a known quote
            if all_quotes:
                self._verify_quotes_storage(all_quotes)

        # Analyze perspectives
        perspectives = {}
        for perspective_key, perspective_data in self.key_perspectives.items():
            perspective_result = self.analyze_perspective_with_quotes(
                perspective_key, perspective_data, all_quotes
            )
            perspectives[perspective_key] = perspective_result
        
        # Categorize quotes by sentiment
        sentiment_categories = self.categorize_quotes_by_sentiment(all_quotes)
        
        # Get speaker role statistics
        speaker_stats = self.get_speaker_role_statistics(all_quotes)
        
        # Prepare results
        results = {
            "metadata": {
                "analysis_date": datetime.now().isoformat(),
                "total_transcripts": len(transcript_files),
                "total_quotes": len(all_quotes),
                "transcript_files": transcript_files,
            },
            "perspectives": perspectives,
            "all_quotes": all_quotes,
            "quote_summary": {
                "strengths_count": len(sentiment_categories.get("positive", [])),
                "weaknesses_count": len(sentiment_categories.get("negative", [])),
                "neutral_count": len(sentiment_categories.get("neutral", [])),
            },
            "speaker_role_stats": speaker_stats,
        }
        
        return results

    def test_rag_functionality(
        self, perspective_key: str = "market_position"
    ) -> Dict[str, Any]:
        """Test the RAG functionality to demonstrate improved quote retrieval."""
        print(f"\n🧪 Testing RAG Functionality for perspective: {perspective_key}")
        print("=" * 60)
        
        if not self.vector_db_manager.quotes_collection:
            print("❌ Vector database not available for RAG testing")
            return {}
        
        # Get perspective data
        if perspective_key not in self.key_perspectives:
            print(f"❌ Perspective '{perspective_key}' not found")
            return {}
        
        perspective_data = self.key_perspectives[perspective_key]
        print(f"📋 Perspective: {perspective_data['title']}")
        print(f"🎯 Focus Areas: {', '.join(perspective_data['focus_areas'])}")
        
        # Test vector database search
        print(f"\n🔍 Testing Vector Database Search...")
        try:
            # Test semantic search for each focus area
            for focus_area in perspective_data["focus_areas"][
                :3
            ]:  # Test first 3 focus areas
                print(f"\n  Searching for: '{focus_area}'")
                
                # Get quotes using vector database
                vector_results = self.vector_db_manager.semantic_search_quotes(
                    query=focus_area,
                    n_results=5,
                    filter_metadata={"speaker_role": "expert"},
                )
                
                print(f"    Found {len(vector_results)} relevant quotes")
                
                # Show top result
                if vector_results:
                    top_quote = vector_results[0]
                    print(f"    Top result: '{top_quote.get('text', '')[:80]}...'")
                    print(f"    Distance score: {top_quote.get('distance', 'N/A'):.4f}")
                    print(
                        f"    Source: {top_quote.get('metadata', {}).get('transcript_name', 'Unknown')}"
                    )
        
        except Exception as e:
            print(f"    ❌ Error in vector search: {e}")
        
        # Test perspective analysis with RAG
        print(f"\n🤖 Testing RAG-Enhanced Perspective Analysis...")
        try:
            # Get some sample quotes for testing
            sample_quotes = []
            for focus_area in perspective_data["focus_areas"][:2]:
                results = self.vector_db_manager.semantic_search_quotes(
                    query=focus_area,
                    n_results=10,
                    filter_metadata={"speaker_role": "expert"},
                )
                sample_quotes.extend(results[:5])  # Take top 5 from each
            
            if sample_quotes:
                print(f"  Retrieved {len(sample_quotes)} sample quotes for analysis")
                
                # Test the perspective analyzer
                result = self.analyze_perspective_with_quotes(
                    perspective_key, perspective_data, sample_quotes
                )
                
                print(f"  ✅ Analysis completed successfully")
                print(f"  📊 Total quotes analyzed: {result.get('total_quotes', 0)}")
                print(f"  🎭 Themes identified: {len(result.get('themes', []))}")
                
                return result
            else:
                print("  ❌ No sample quotes found for analysis")
                return {}
                
        except Exception as e:
            print(f"  ❌ Error in RAG analysis: {e}")
            return {}
    
    def get_rag_statistics(self) -> Dict[str, Any]:
        """Get statistics about the RAG system performance."""
        stats = {
            "vector_db_available": False,
            "total_quotes_stored": 0,
            "rag_functionality": False,
            "search_capabilities": [],
        }
        
        try:
            if self.vector_db_manager and self.vector_db_manager.quotes_collection:
                stats["vector_db_available"] = True
                
                # Get database stats
                db_stats = self.vector_db_manager.get_vector_database_stats()
                stats["total_quotes_stored"] = db_stats.get("total_quotes", 0)
                
                # Check RAG functionality
                if (
                    hasattr(self.perspective_analyzer, "vector_db_manager")
                    and self.perspective_analyzer.vector_db_manager
                ):
                    stats["rag_functionality"] = True
                
                # List search capabilities
                stats["search_capabilities"] = [
                    "semantic_search_quotes",
                    "search_quotes_with_speaker_filter",
                    "get_quotes_by_perspective",
                ]
                
        except Exception as e:
            print(f"Error getting RAG statistics: {e}")
        
        return stats

    def enrich_quotes_for_export(
        self, quotes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Enrich quotes with all fields needed for proper Excel export.
        Delegates to the QuoteProcessor module for consistent processing.
        """
        return self.quote_processor.enrich_quotes_for_export(quotes)

        # Quote enrichment methods moved to QuoteProcessor module
    # Use self.quote_processor.enrich_quotes_for_export() instead


def main():
    """Main function to run the quote analysis tool."""
    print("FlexXray Quote Analysis Tool (Modular Version)")
    print("=" * 50)
    
    # Check for API key using centralized configuration
    try:
        api_key = get_openai_api_key()
        logger.info("OpenAI API key loaded successfully")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return
    
    # Initialize the tool
    try:
        analyzer = ModularQuoteAnalysisTool()
        logger.info("Quote analysis tool initialized successfully")
    except (ValueError, TypeError) as e:
        logger.error(f"Configuration error initializing tool: {e}")
        return
    except ConnectionError as e:
        logger.error(f"OpenAI API connection error: {e}")
        return
    except Exception as e:
        logger.error(f"Unexpected error initializing tool: {e}")
        return
    
    # Set default directory
    default_directory = "FlexXray Transcripts"
    
    if os.path.exists(default_directory):
        directory_path = default_directory
        logger.info(f"Using default directory: {directory_path}")
    else:
        directory_path = input(
            "Enter path to directory containing transcript files: "
        ).strip()
    
    if not os.path.exists(directory_path):
        logger.error(f"Directory {directory_path} does not exist")
        return
    
    # Process transcripts
    logger.info(f"Processing transcripts from: {directory_path}")
    results = analyzer.process_transcripts_for_quotes(directory_path)
    
    if results:
        # Save results
        analyzer.save_quote_analysis(results)
        analyzer.export_quote_analysis_to_text(results)
        
        logger.info("Analysis complete!")
        logger.info(f"Processed {results['metadata']['total_transcripts']} transcripts")
        logger.info(f"Extracted {results['metadata']['total_quotes']} quotes")
        logger.info("Generated 3 key perspective analyses")
        logger.info("Created strengths and weaknesses buckets")
        
        # Generate and export the company summary page
        logger.info("Generating company summary page...")
        all_quotes = results.get("all_quotes", [])
        if all_quotes:
            summary_page = analyzer.generate_company_summary_page(all_quotes)
            if summary_page:
                # Export to both text and Excel formats
                text_file = analyzer.export_company_summary_page(summary_page)
                excel_file = analyzer.export_company_summary_to_excel(summary_page)
                logger.info("Company summary page generated successfully!")
                logger.info(f"Text file: {text_file}")
                logger.info(f"Excel file: {excel_file}")
            else:
                logger.error("Failed to generate company summary page")
        else:
            logger.warning("No quotes available for company summary page")
        
        # Show summary
        quote_summary = results["quote_summary"]
        logger.info("Quote Summary (Expert Quotes Only):")
        logger.info(f"Strengths: {quote_summary['strengths_count']}")
        logger.info(f"Weaknesses: {quote_summary['weaknesses_count']}")
        logger.info(f"Neutral: {quote_summary['neutral_count']}")
        
        # Show speaker role statistics
        speaker_stats = results.get("speaker_role_stats", {})
        logger.info("Speaker Role Summary:")
        logger.info(f"Total quotes extracted: {speaker_stats.get('total_quotes', 0)}")
        logger.info(
            f"Expert quotes: {speaker_stats.get('expert_quotes', 0)} ({speaker_stats.get('expert_percentage', 0):.1f}%)"
        )
        logger.info(
            f"Interviewer quotes filtered out: {speaker_stats.get('interviewer_quotes', 0)}"
        )
        logger.info(
            f"Quotes with interviewer context: {speaker_stats.get('quotes_with_context', 0)} ({speaker_stats.get('context_percentage', 0):.1f}%)"
        )
        logger.info(
            f"Average context per quote: {speaker_stats.get('average_context_per_quote', 0):.1f} sentences"
        )
        
        # Show ranking statistics
        ranking_stats = analyzer.get_quote_ranking_statistics(results)
        logger.info("OpenAI Ranking Statistics:")
        logger.info(f"Total Perspectives: {ranking_stats['total_perspectives']}")
        logger.info(f"Total Quotes Ranked: {ranking_stats['total_ranked_quotes']}")
        logger.info(f"Ranking Coverage: {ranking_stats['ranking_coverage']:.1f}%")
        
        # Show selection stage breakdown
        if ranking_stats["selection_stage_breakdown"]:
            logger.info("Selection Stage Breakdown:")
            for stage, count in ranking_stats["selection_stage_breakdown"].items():
                logger.info(f"{stage}: {count} quotes")
        
    else:
        logger.warning("No results generated")


if __name__ == "__main__":
    main()
