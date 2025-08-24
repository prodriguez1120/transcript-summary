#!/usr/bin/env python3
"""
Summary Generation Module

Handles company summary generation, batch processing, response parsing,
and structure validation for the quote analysis system.
"""

import json
import re
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class SummaryGenerator:
    """Handles company summary generation and processing."""
    
    def __init__(self, openai_client, prompt_config):
        """Initialize the summary generator."""
        self.client = openai_client
        self.prompt_config = prompt_config
    
    def generate_company_summary_direct(
        self, quotes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate company summary directly without batch processing."""
        if not quotes:
            return {}
        
        logger.info(f"Generating company summary directly with {len(quotes)} quotes")
        
        try:
            # Create summary prompt
            summary_prompt = self._create_summary_prompt(quotes)
            
            # Get prompt configuration
            params = self.prompt_config.get_prompt_parameters("company_summary")
            
            # Call OpenAI for summary generation
            response = self.client.chat.completions.create(
                model=params.get("model", "gpt-4"),
                messages=[
                    {
                        "role": "system",
                        "content": self.prompt_config.get_system_message("company_summary"),
                    },
                    {"role": "user", "content": summary_prompt},
                ],
                temperature=params.get("temperature", 0.3),
                max_tokens=params.get("max_tokens", 3000),
            )
            
            # Parse summary response
            response_content = response.choices[0].message.content
            if response_content:
                summary_data = self._parse_summary_response(response_content, quotes)
                logger.info("Company summary page generated successfully")
                return summary_data
            else:
                logger.error("Empty response from OpenAI")
                return {}
                
        except Exception as e:
            logger.error(f"Error in company summary generation: {e}")
            return {}
    
    def generate_company_summary_with_batching(
        self, quotes: List[Dict[str, Any]], batch_size: int = 25
    ) -> Dict[str, Any]:
        """Generate company summary using batch processing to stay within token limits."""
        if not quotes:
            return {}
        
        logger.info(
            f"Using batch processing for company summary generation with batch size {batch_size}"
        )
        
        # Calculate number of batches
        total_quotes = len(quotes)
        num_batches = (total_quotes + batch_size - 1) // batch_size
        
        logger.info(f"Processing {total_quotes} quotes in {num_batches} batches")
        
        # Process each batch
        batch_results = []
        for batch_num in range(num_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, total_quotes)
            batch_quotes = quotes[start_idx:end_idx]
            
            logger.info(
                f"Processing batch {batch_num + 1}/{num_batches} with {len(batch_quotes)} quotes"
            )
            
            try:
                # Generate summary for this batch
                batch_summary = self._generate_single_batch_summary(
                    batch_quotes, batch_num + 1
                )
                if batch_summary:
                    batch_results.append(batch_summary)
                    logger.info(f"✅ Batch {batch_num + 1} completed successfully")
                else:
                    logger.warning(
                        f"⚠️ Batch {batch_num + 1} failed to generate summary"
                    )
                
                # Wait between batches to avoid rate limiting
                if batch_num < num_batches - 1:
                    time.sleep(1.5)
                    
            except Exception as e:
                logger.error(f"❌ Error processing batch {batch_num + 1}: {e}")
                continue
        
        # Combine batch results into final summary
        if not batch_results:
            logger.error("No batch results generated")
            return {}
        
        logger.info(f"Combining {len(batch_results)} batch results into final summary")
        final_summary = self._combine_batch_summaries(batch_results, quotes)
        
        return final_summary
    
    def _generate_single_batch_summary(
        self, batch_quotes: List[Dict[str, Any]], batch_num: int
    ) -> Dict[str, Any]:
        """Generate summary for a single batch of quotes."""
        try:
            # Create summary prompt for this batch
            summary_prompt = self._create_summary_prompt(batch_quotes)
            
            # Get prompt configuration
            params = self.prompt_config.get_prompt_parameters("company_summary")
            
            # Call OpenAI for this batch
            response = self.client.chat.completions.create(
                model=params.get("model", "gpt-4"),
                messages=[
                    {
                        "role": "system",
                        "content": self.prompt_config.get_system_message("company_summary"),
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

    def _create_summary_prompt(self, quotes: List[Dict[str, Any]]) -> str:
        """Create the prompt for generating company summary."""
        # The new prompt expects transcript content, so we'll format the quotes as transcript content
        transcript_content = ""
        for i, quote in enumerate(
            quotes[:30], 1
        ):  # Limit to 30 quotes for summary to stay within token limits
            quote_text = quote.get("text", "")
            
            # Use the correct fields from the main analysis quotes
            speaker_role = quote.get("speaker_role", "Unknown")
            transcript_name = quote.get("transcript_name", "Unknown Transcript")
            
            # Create a proper speaker identifier
            if speaker_role == "expert":
                # Extract speaker name from transcript name if possible
                if " - " in transcript_name:
                    speaker_name = transcript_name.split(" - ")[0]
                else:
                    speaker_name = transcript_name.replace(".docx", "")
                speaker_info = f"{speaker_name} (Expert)"
            else:
                speaker_info = f"{speaker_role}"
            
            transcript_content += (
                f'\nQuote {i}: "{quote_text}" - {speaker_info} from {transcript_name}'
            )
        
        # Get the prompt template and format it
        try:
            template = self.prompt_config.get_prompt_template("company_summary")
            # Replace the quotes_list placeholder in the template
            prompt = template.replace("{quotes_list}", transcript_content)
        except Exception as e:
            logger.warning(f"Error formatting prompt template: {e}")
            # Fallback: create a simple prompt
            prompt = f"""You are an expert business intelligence analyst. Analyze the following quotes and generate a structured summary.

Transcript Content:
{transcript_content}

Please provide a JSON response with key_takeaways, strengths, and weaknesses sections."""
        
        return prompt

    def _create_structured_data_model(self) -> Dict[str, Any]:
        """Create a structured data model with predefined template structure."""
        return {
            "key_takeaways": [],
            "strengths": [],
            "weaknesses": [],
            "generation_timestamp": datetime.now().isoformat(),
            "total_quotes_analyzed": 0,
            "template_version": "2.0",
            "data_structure_validated": True,
        }

    def _parse_summary_response(
        self, response_text: str, available_quotes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Parse OpenAI's summary response using structured data model with quote validation."""
        # Initialize structured data model
        result = self._create_structured_data_model()
        result["total_quotes_analyzed"] = len(available_quotes)
        
        try:
            # Check for empty response
            if not response_text or not response_text.strip():
                return result
            
            # Use the robust JSON extraction method
            try:
                json_content = self._extract_json_from_response(response_text)
                
                # Parse the JSON response
                parsed_data = json.loads(json_content)
                
                # Process key takeaways using structured approach with validation
                if "key_takeaways" in parsed_data and isinstance(
                    parsed_data["key_takeaways"], list
                ):
                    validated_takeaways = self._validate_and_fix_key_takeaways(
                        parsed_data["key_takeaways"], available_quotes
                    )
                    result["key_takeaways"] = validated_takeaways
                
                # Process strengths with validation
                if "strengths" in parsed_data and isinstance(
                    parsed_data["strengths"], list
                ):
                    validated_strengths = self._validate_and_fix_strengths(
                        parsed_data["strengths"], available_quotes
                    )
                    result["strengths"] = validated_strengths
                
                # Process weaknesses with validation
                if "weaknesses" in parsed_data and isinstance(
                    parsed_data["weaknesses"], list
                ):
                    validated_weaknesses = self._validate_and_fix_weaknesses(
                        parsed_data["weaknesses"], available_quotes
                    )
                    result["weaknesses"] = validated_weaknesses
                
                logger.info("Summary response parsed and validated successfully")
                return result
                
            except Exception as e:
                logger.error(f"Error parsing JSON response: {e}")
                return result
                
        except Exception as e:
            logger.error(f"Error in summary response parsing: {e}")
            return result
    
    def _extract_json_from_response(self, response_text: str) -> str:
        """Extract JSON content from OpenAI response text."""
        # Look for JSON content between triple backticks
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            return json_match.group(1).strip()
        
        # Look for JSON content between backticks
        json_match = re.search(r'```(.*?)```', response_text, re.DOTALL)
        if json_match:
            return json_match.group(1).strip()
        
        # Look for JSON content between curly braces
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        # If no JSON found, return the original text
        return response_text
    
    def _validate_and_fix_key_takeaways(
        self, takeaways: List[Dict[str, Any]], available_quotes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Validate and fix key takeaways to ensure exactly 3 quotes per theme."""
        if not isinstance(takeaways, list):
            return []

        validated_takeaways = []
        for takeaway in takeaways:
            if isinstance(takeaway, dict):
                theme = takeaway.get("theme", "")
                quotes = takeaway.get("quotes", [])

                # Ensure exactly 3 quotes - this is critical for the structure
                if len(quotes) < 3:
                    logger.warning(
                        f"Key takeaway '{theme}' has only {len(quotes)} quotes, need exactly 3. Adding placeholder quotes."
                    )
                    # Add exactly the number of quotes needed to reach 3
                    quotes_needed = 3 - len(quotes)
                    for i in range(quotes_needed):
                        quotes.append(
                            {
                                "quote": f"Additional quote needed for {theme}",
                                "speaker": "Quote Required",
                                "document": "Additional Analysis Needed",
                            }
                        )
                elif len(quotes) > 3:
                    logger.info(
                        f"Key takeaway '{theme}' has {len(quotes)} quotes, trimming to 3 best ones."
                    )
                    quotes = quotes[:3]

                # Convert to expected format
                supporting_quotes = []
                for quote_data in quotes:
                    if isinstance(quote_data, dict):
                        supporting_quotes.append(
                            {
                                "text": quote_data.get("quote", ""),
                                "speaker_info": quote_data.get(
                                    "speaker", "Unknown Speaker"
                                ),
                                "transcript_name": quote_data.get(
                                    "document", "Unknown Document"
                                ),
                            }
                        )

                if theme and supporting_quotes:
                    validated_takeaways.append(
                        {"insight": theme, "supporting_quotes": supporting_quotes}
                    )

        return validated_takeaways

    def _validate_and_fix_strengths(
        self, strengths: List[Dict[str, Any]], available_quotes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Validate and fix strengths to ensure exactly 2 quotes per theme."""
        if not isinstance(strengths, list):
            return []

        validated_strengths = []
        for strength in strengths:
            if isinstance(strength, dict):
                theme = strength.get("theme", "")
                quotes = strength.get("quotes", [])

                # Ensure exactly 2 quotes
                if len(quotes) < 2:
                    logger.warning(
                        f"Strength '{theme}' has only {len(quotes)} quotes, need 2. Adding placeholder quotes."
                    )
                    while len(quotes) < 2:
                        quotes.append(
                            {
                                "quote": f"Additional quote needed for {theme}",
                                "speaker": "Quote Required",
                                "document": "Additional Analysis Needed",
                            }
                        )
                elif len(quotes) > 2:
                    logger.info(
                        f"Strength '{theme}' has {len(quotes)} quotes, trimming to 2 best ones."
                    )
                    quotes = quotes[:2]

                # Convert to expected format
                supporting_quotes = []
                for quote_data in quotes:
                    if isinstance(quote_data, dict):
                        supporting_quotes.append(
                            {
                                "text": quote_data.get("quote", ""),
                                "speaker_info": quote_data.get(
                                    "speaker", "Unknown Speaker"
                                ),
                                "transcript_name": quote_data.get(
                                    "document", "Unknown Document"
                                ),
                            }
                        )

                if theme and supporting_quotes:
                    validated_strengths.append(
                        {"insight": theme, "supporting_quotes": supporting_quotes}
                    )

        return validated_strengths

    def _validate_and_fix_weaknesses(
        self, weaknesses: List[Dict[str, Any]], available_quotes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Validate and fix weaknesses to ensure exactly 2 quotes per theme."""
        if not isinstance(weaknesses, list):
            return []

        validated_weaknesses = []
        for weakness in weaknesses:
            if isinstance(weakness, dict):
                theme = weakness.get("theme", "")
                quotes = weakness.get("quotes", [])

                # Ensure exactly 2 quotes
                if len(quotes) < 2:
                    logger.warning(
                        f"Weakness '{theme}' has only {len(quotes)} quotes, need 2. Adding placeholder quotes."
                    )
                    while len(quotes) < 2:
                        quotes.append(
                            {
                                "quote": f"Additional quote needed for {theme}",
                                "speaker": "Quote Required",
                                "document": "Additional Analysis Needed",
                            }
                        )
                elif len(quotes) > 2:
                    logger.info(
                        f"Weakness '{theme}' has {len(quotes)} quotes, trimming to 2 best ones."
                    )
                    quotes = quotes[:2]

                # Convert to expected format
                supporting_quotes = []
                for quote_data in quotes:
                    if isinstance(quote_data, dict):
                        supporting_quotes.append(
                            {
                                "text": quote_data.get("quote", ""),
                                "speaker_info": quote_data.get(
                                    "speaker", "Unknown Speaker"
                                ),
                                "transcript_name": quote_data.get(
                                    "document", "Unknown Document"
                                ),
                            }
                        )

                if theme and supporting_quotes:
                    validated_weaknesses.append(
                        {"insight": theme, "supporting_quotes": supporting_quotes}
                    )

        return validated_weaknesses
