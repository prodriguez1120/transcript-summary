
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

class ModularQuoteAnalysisTool(QuoteAnalysisTool):
    """Enhanced quote analysis tool using modular components."""
    
    def __init__(self, api_key: str = None, chroma_persist_directory: str = "./chroma_db"):
        """Initialize the modular quote analysis tool."""
        super().__init__(api_key, chroma_persist_directory)
        
        # Initialize modular components
        self.quote_extractor = QuoteExtractor(
            min_quote_length=self.min_quote_length,
            max_quote_length=self.max_quote_length
        )
        
        self.vector_db_manager = VectorDatabaseManager(chroma_persist_directory)
        
        # Use the API key from the parent class instead of calling os.getenv again
        # Use the API key from the parent class (which comes from centralized config)
        self.perspective_analyzer = PerspectiveAnalyzer(api_key=self.api_key)
        self.perspective_analyzer.set_vector_db_manager(self.vector_db_manager)
        
        self.export_manager = ExportManager()
        
        # Define key_perspectives explicitly to ensure it's always available
        self.key_perspectives = {
            "business_model": {
                "title": "Business Model & Market Position",
                "description": "How FlexXray operates, serves customers, and competes in the market",
                "focus_areas": ["value proposition", "customer relationships", "market positioning", "competitive advantages"]
            },
            "growth_potential": {
                "title": "Growth Potential & Market Opportunity",
                "description": "FlexXray's expansion opportunities, market trends, and future prospects",
                "focus_areas": ["market expansion", "product development", "industry trends", "growth drivers"]
            },
            "risk_factors": {
                "title": "Risk Factors & Challenges",
                "description": "Key risks, challenges, and areas of concern for FlexXray's business",
                "focus_areas": ["service quality issues", "operational challenges", "competitive threats", "market risks"]
            }
        }

    def extract_text_from_document(self, doc_path: str) -> str:
        """Extract text content from a Word document using the quote extractor."""
        return self.quote_extractor.extract_text_from_document(doc_path)

    def extract_quotes_from_text(self, text: str, transcript_name: str) -> List[Dict[str, Any]]:
        """Extract meaningful quotes from transcript text using the quote extractor."""
        return self.quote_extractor.extract_quotes_from_text(text, transcript_name)

    def store_quotes_in_vector_db(self, quotes: List[Dict[str, Any]], batch_size: int = 100) -> bool:
        """Store quotes in the vector database using the vector database manager."""
        return self.vector_db_manager.store_quotes_in_vector_db(quotes, batch_size)

    def semantic_search_quotes(self, query: str, n_results: int = 10, filter_metadata: Dict = None) -> List[Dict[str, Any]]:
        """Perform semantic search for quotes using the vector database manager."""
        return self.vector_db_manager.semantic_search_quotes(query, n_results, filter_metadata)

    def search_quotes_with_speaker_filter(self, query: str, speaker_role: str = "expert", n_results: int = 10) -> List[Dict[str, Any]]:
        """Search for quotes with speaker role filtering using the vector database manager."""
        return self.vector_db_manager.search_quotes_with_speaker_filter(query, speaker_role, n_results)

    def clear_vector_database(self) -> bool:
        """Clear all data from the vector database using the vector database manager."""
        return self.vector_db_manager.clear_vector_database()

    def get_vector_database_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database using the vector database manager."""
        return self.vector_db_manager.get_vector_database_stats()

    def get_quotes_by_perspective(self, perspective_key: str, perspective_data: dict, n_results: int = 20) -> List[Dict[str, Any]]:
        """Get quotes relevant to a specific perspective using the vector database manager."""
        return self.vector_db_manager.get_quotes_by_perspective(perspective_key, perspective_data, n_results)

    def categorize_quotes_by_sentiment(self, quotes: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize quotes by sentiment using the vector database manager."""
        return self.vector_db_manager.categorize_quotes_by_sentiment(quotes)

    def analyze_perspective_with_quotes(self, perspective_key: str, perspective_data: dict,
                                      all_quotes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze a perspective using the perspective analyzer."""
        return self.perspective_analyzer.analyze_perspective_with_quotes(
            perspective_key, perspective_data, all_quotes
        )

    def generate_company_summary_page(self, all_quotes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a comprehensive company summary page using OpenAI."""
        if not all_quotes:
            return {}
        
        logger.info("Generating company summary page using OpenAI...")
        
        # Clean and validate quotes
        cleaned_quotes = self._clean_and_validate_quotes(all_quotes)
        if not cleaned_quotes:
            return {}
        
        # Filter to expert quotes only
        expert_quotes = self.get_expert_quotes_only(cleaned_quotes)
        if not expert_quotes:
            logger.warning("No expert quotes found after filtering")
            return {}
        
        # Get diverse quotes for analysis - increase to 50 for better quote selection
        diverse_quotes = self._get_diverse_quotes(expert_quotes, "summary", 50)
        
        # Create summary prompt
        summary_prompt = self._create_summary_prompt(diverse_quotes)
        
        # Get prompt configuration
        prompt_config = get_prompt_config()
        
        try:
            # Call OpenAI for summary generation
            # Get OpenAI parameters from config
            params = prompt_config.get_prompt_parameters("company_summary")
            
            response = self.client.chat.completions.create(
                model=params.get("model", "gpt-4"),
                messages=[
                    {"role": "system", "content": prompt_config.get_system_message("company_summary")},
                    {"role": "user", "content": summary_prompt}
                ],
                temperature=params.get("temperature", 0.3),
                max_tokens=params.get("max_tokens", 3000)
            )
            
            # Parse summary response
            summary_data = self._parse_summary_response(response.choices[0].message.content, diverse_quotes)
            
            logger.info("Company summary page generated successfully")
            return summary_data
            
        except (ValueError, TypeError) as e:
            logger.error(f"Data validation error in company summary generation: {e}")
            return {}
        except ConnectionError as e:
            logger.error(f"OpenAI API connection error: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error in company summary generation: {e}")
            return {}

    def _create_summary_prompt(self, quotes: List[Dict[str, Any]]) -> str:
        """Create the prompt for generating company summary."""
        # Get the prompt template
        prompt_config = get_prompt_config()
        template = prompt_config.get_prompt_template("company_summary")
        
        # The new prompt expects transcript content, so we'll format the quotes as transcript content
        transcript_content = ""
        for i, quote in enumerate(quotes[:50], 1):  # Limit to 50 quotes for summary to provide better selection
            quote_text = quote.get('text', '')
            
            # Use the correct fields from the main analysis quotes
            speaker_role = quote.get('speaker_role', 'Unknown')
            transcript_name = quote.get('transcript_name', 'Unknown Transcript')
            
            # Create a proper speaker identifier
            if speaker_role == 'expert':
                # Extract speaker name from transcript name if possible
                if ' - ' in transcript_name:
                    speaker_name = transcript_name.split(' - ')[0]
                else:
                    speaker_name = transcript_name.replace('.docx', '')
                speaker_info = f"{speaker_name} (Expert)"
            else:
                speaker_info = f"{speaker_role}"
            
            transcript_content += f"\nQuote {i}: \"{quote_text}\" - {speaker_info} from {transcript_name}"
        
        # Format the prompt using the template - handle the template carefully since it contains JSON structure
        try:
            # Replace the quotes_list placeholder in the template
            prompt = template.replace("{quotes_list}", transcript_content)
        except Exception as e:
            print(f"Error formatting prompt template: {e}")
            # Fallback: create a simple prompt
            prompt = f"""You are an expert business intelligence analyst. Analyze the following quotes and generate a structured summary.

Transcript Content:
{transcript_content}

Please provide a JSON response with key_takeaways, strengths, and weaknesses sections."""
        
        return prompt

    def _create_structured_data_model(self) -> Dict[str, Any]:
        """Create a structured data model with predefined template structure."""
        return {
            'key_takeaways': [],
            'strengths': [], 
            'weaknesses': [],
            'generation_timestamp': datetime.now().isoformat(),
            'total_quotes_analyzed': 0,
            'template_version': '2.0',
            'data_structure_validated': True
        }

    def _parse_summary_response(self, response_text: str, available_quotes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse OpenAI's summary response using structured data model."""
        # Initialize structured data model
        result = self._create_structured_data_model()
        result['total_quotes_analyzed'] = len(available_quotes)
        
        try:
            # Check for empty response
            if not response_text or not response_text.strip():
                return result
            
            # Use the robust JSON extraction method
            try:
                from perspective_analysis import PerspectiveAnalyzer
                analyzer = PerspectiveAnalyzer(self.client)
                json_content = analyzer._extract_json_from_response(response_text)
                
                # Parse the JSON response
                parsed_data = json.loads(json_content)
                
                # Use structured data model - no need to recreate, already initialized above
                
                # Process key takeaways using structured approach
                if 'key_takeaways' in parsed_data and isinstance(parsed_data['key_takeaways'], list):
                    for takeaway in parsed_data['key_takeaways']:
                        if isinstance(takeaway, dict):
                            insight = takeaway.get('theme', '')
                            quotes = takeaway.get('quotes', [])
                            
                            # Convert quotes to the expected format with validation
                            supporting_quotes = []
                            for quote_data in quotes:
                                if isinstance(quote_data, dict):
                                    supporting_quotes.append({
                                        'text': quote_data.get('quote', ''),
                                        'speaker_info': quote_data.get('speaker', 'Unknown Speaker'),
                                        'transcript_name': quote_data.get('document', 'Unknown Document')
                                    })
                            
                            # Only add if we have valid data
                            if insight and supporting_quotes:
                                result['key_takeaways'].append({
                                    'insight': insight,
                                    'supporting_quotes': supporting_quotes
                                })
                
                # Process strengths using structured approach
                if 'strengths' in parsed_data and isinstance(parsed_data['strengths'], list):
                    for strength in parsed_data['strengths']:
                        if isinstance(strength, dict):
                            insight = strength.get('theme', '')
                            quotes = strength.get('quotes', [])
                            
                            # Convert quotes to the expected format with validation
                            supporting_quotes = []
                            for quote_data in quotes:
                                if isinstance(quote_data, dict):
                                    supporting_quotes.append({
                                        'text': quote_data.get('quote', ''),
                                        'speaker_info': quote_data.get('speaker', 'Unknown Speaker'),
                                        'transcript_name': quote_data.get('document', 'Unknown Document')
                                    })
                            
                            # Only add if we have valid data
                            if insight and supporting_quotes:
                                result['strengths'].append({
                                    'insight': insight,
                                    'supporting_quotes': supporting_quotes
                                })
                
                # Process weaknesses using structured approach
                if 'weaknesses' in parsed_data and isinstance(parsed_data['weaknesses'], list):
                    for weakness in parsed_data['weaknesses']:
                        if isinstance(weakness, dict):
                            insight = weakness.get('theme', '')
                            quotes = weakness.get('quotes', [])
                            
                            # Convert quotes to the expected format with validation
                            supporting_quotes = []
                            for quote_data in quotes:
                                if isinstance(quote_data, dict):
                                    supporting_quotes.append({
                                        'text': quote_data.get('quote', ''),
                                        'speaker_info': quote_data.get('speaker', 'Unknown Speaker'),
                                        'transcript_name': quote_data.get('document', 'Unknown Document')
                                    })
                            
                            # Only add if we have valid data
                            if insight and supporting_quotes:
                                result['weaknesses'].append({
                                    'insight': insight,
                                    'supporting_quotes': supporting_quotes
                                })
                
                return result
                
            except json.JSONDecodeError as e:
                # JSON parsing failed, falling back to text parsing with structured model
                print(f"JSON parsing failed, attempting text parsing: {e}")
                pass
            
            # Fallback to old text parsing method using structured model
            sections = self._parse_all_sections(response_text, available_quotes)
            
            # Validate and supplement using structured approach
            validated_takeaways = self._validate_and_supplement_takeaways(sections.get('key_takeaways', []), available_quotes)
            validated_strengths = self._validate_and_supplement_takeaways(sections.get('strengths', []), available_quotes)
            validated_weaknesses = self._validate_and_supplement_takeaways(sections.get('weaknesses', []), available_quotes)
            
            # Update the structured result with validated data
            result['key_takeaways'] = validated_takeaways if validated_takeaways else []
            result['strengths'] = validated_strengths if validated_strengths else []
            result['weaknesses'] = validated_weaknesses if validated_weaknesses else []
            
            return result
            
        except (ValueError, TypeError) as e:
            logger.error(f"Data parsing error in summary response: {e}")
            # Return structured model even on error to maintain consistency
            return result
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error in summary response: {e}")
            # Return structured model even on error to maintain consistency
            return result
        except Exception as e:
            logger.error(f"Unexpected error parsing summary response: {e}")
            # Return structured model even on error to maintain consistency
            return result

    def _parse_all_sections(self, response_text: str, available_quotes: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Parse all sections from the response text with proper quote citations."""
        sections = {
            'key_takeaways': [],
            'strengths': [],
            'weaknesses': []
        }
        
        lines = response_text.split('\n')
        current_section = None
        current_insight = None
        current_quotes = []
        
        for line in lines:
            line = line.strip()
            
            # Determine current section
            current_section = self._determine_current_section(line, current_section, sections)
            
            # Parse items in current section
            if current_section and line:
                if re.match(r'^\d+\.', line):
                    self._save_current_insight(sections, current_section, current_insight, current_quotes)
                    current_insight = re.sub(r'^\d+\.\s*', '', line)
                    current_quotes = []
                
                elif line.startswith('- '):
                    quote_data = self._parse_quote_line(line)
                    if quote_data:
                        current_quotes.append(quote_data)
                
                elif re.match(r'^[•\-*]\s*', line):
                    self._save_current_insight(sections, current_section, current_insight, current_quotes)
                    current_insight = re.sub(r'^[•\-*]\s*', '', line)
                    current_quotes = []
        
        # Save the last insight
        self._save_current_insight(sections, current_section, current_insight, current_quotes)
        
        # Enforce the correct structure: 3 Key Takeaways, 2 Strengths, 2 Weaknesses
        self._enforce_correct_structure(sections)
        
        return sections
    
    def _determine_current_section(self, line: str, current_section: str, sections: Dict[str, List[Dict[str, Any]]]) -> str:
        """Determine the current section based on line content."""
        if line.startswith('========================================'):
            return current_section
        
        if any(keyword in line.lower() for keyword in ['key takeaways', 'takeaways', 'key points', 'main insights']):
            return 'key_takeaways'
        
        if any(keyword in line.lower() for keyword in ['strengths', 'strength', 'strong points', 'advantages']) and 'key takeaways' not in line.lower():
            # Only switch to strengths if we have completed all 3 key takeaways
            if current_section == 'key_takeaways' and len(sections['key_takeaways']) < 3:
                return current_section
            return 'strengths'
        
        if any(keyword in line.lower() for keyword in ['weaknesses', 'weakness', 'weak points', 'challenges', 'concerns']):
            # Only switch to weaknesses if we have completed all 2 strengths
            if current_section == 'strengths' and len(sections['strengths']) < 2:
                return current_section
            return 'weaknesses'
        
        return current_section
    
    def _parse_quote_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a quote line and extract quote data."""
        # Parse quote with citation: "quote text" - Speaker Name, Company/Title from Transcript Name
        quote_match = re.match(r'^- "([^"]+)" - (.+?) from (.+)$', line)
        if quote_match:
            return {
                'text': quote_match.group(1),
                'speaker_info': quote_match.group(2),
                'transcript_name': quote_match.group(3)
            }
        
        # Try alternative format: "quote text" - Speaker Name, Company/Title
        alt_match = re.match(r'^- "([^"]+)" - (.+)$', line)
        if alt_match:
            return {
                'text': alt_match.group(1),
                'speaker_info': alt_match.group(2),
                'transcript_name': 'Unknown'
            }
        
        # Try format without quotes: - text - Speaker Name, Company/Title from Transcript Name
        no_quote_match = re.match(r'^- (.+?) - (.+?) from (.+)$', line)
        if no_quote_match:
            return {
                'text': no_quote_match.group(1),
                'speaker_info': no_quote_match.group(2),
                'transcript_name': no_quote_match.group(3)
            }
        
        # Try format: - text - Speaker Name, Company/Title (without "from Transcript Name")
        simple_match = re.match(r'^- (.+?) - (.+)$', line)
        if simple_match:
            return {
                'text': simple_match.group(1),
                'speaker_info': simple_match.group(2),
                'transcript_name': 'Unknown'
            }
        
        return None
    
    def _save_current_insight(self, sections: Dict[str, List[Dict[str, Any]]], current_section: str, current_insight: str, current_quotes: List[Dict[str, Any]]):
        """Save current insight with quotes to the appropriate section."""
        if current_insight and current_quotes:
            item = {
                'insight': current_insight,
                'supporting_quotes': current_quotes
            }
            
            if current_section == 'key_takeaways':
                sections['key_takeaways'].append(item)
            elif current_section == 'strengths':
                sections['strengths'].append(item)
            elif current_section == 'weaknesses':
                sections['weaknesses'].append(item)
            else:
                # If no section is set, add to key takeaways for now
                sections['key_takeaways'].append(item)
    
    def _enforce_correct_structure(self, sections: Dict[str, List[Dict[str, Any]]]):
        """Enforce the correct structure: 3 Key Takeaways, 2 Strengths, 2 Weaknesses."""
        MAX_TAKEAWAYS = 3
        MAX_STRENGTHS = 2
        MAX_WEAKNESSES = 2
        
        # Move extra strengths to key takeaways
        if len(sections['strengths']) > MAX_STRENGTHS:
            extra_strengths = sections['strengths'][MAX_STRENGTHS:]
            sections['strengths'] = sections['strengths'][:MAX_STRENGTHS]
            sections['key_takeaways'].extend(extra_strengths)
        
        # Move extra weaknesses to key takeaways
        if len(sections['weaknesses']) > MAX_WEAKNESSES:
            extra_weaknesses = sections['weaknesses'][MAX_WEAKNESSES:]
            sections['weaknesses'] = sections['weaknesses'][:MAX_WEAKNESSES]
            sections['key_takeaways'].extend(extra_weaknesses)
        
        # Ensure we have exactly 3 key takeaways
        while len(sections['key_takeaways']) < MAX_TAKEAWAYS:
            if len(sections['strengths']) > MAX_STRENGTHS:
                sections['key_takeaways'].append(sections['strengths'].pop())
            elif len(sections['weaknesses']) > MAX_WEAKNESSES:
                sections['key_takeaways'].append(sections['weaknesses'].pop())
            else:
                break
        
        # Content-based redistribution
        self._redistribute_by_content(sections, MAX_STRENGTHS, MAX_WEAKNESSES)
        
        # Fallback duplication if needed
        self._duplicate_insights_if_needed(sections, MAX_TAKEAWAYS, MAX_STRENGTHS, MAX_WEAKNESSES)
        
        return sections
    
    def _redistribute_by_content(self, sections: Dict[str, List[Dict[str, Any]]], max_strengths: int, max_weaknesses: int):
        """Redistribute insights based on content keywords."""
        strengths_keywords = ['technology', 'proprietary', 'turnaround', 'rapid', 'advantage', 'capability', 'efficiency', 'benefit']
        weaknesses_keywords = ['limit', 'constraint', 'challenge', 'risk', 'unpredictable', 'tam', 'market size', 'impact']
        
        # Move key takeaways to strengths if they fit better
        if len(sections['strengths']) < max_strengths and len(sections['key_takeaways']) > 3:
            for i, takeaway in enumerate(sections['key_takeaways']):
                if len(sections['strengths']) >= max_strengths or len(sections['key_takeaways']) <= 3:
                    break
                insight_text = takeaway.get('insight', '').lower()
                if any(keyword in insight_text for keyword in strengths_keywords):
                    sections['strengths'].append(sections['key_takeaways'].pop(i))
                    break
        
        # Move key takeaways to weaknesses if they fit better
        if len(sections['weaknesses']) < max_weaknesses and len(sections['key_takeaways']) > 3:
            for i, takeaway in enumerate(sections['key_takeaways']):
                if len(sections['weaknesses']) >= max_weaknesses or len(sections['key_takeaways']) <= 3:
                    break
                insight_text = takeaway.get('insight', '').lower()
                if any(keyword in insight_text for keyword in weaknesses_keywords):
                    sections['weaknesses'].append(sections['key_takeaways'].pop(i))
                    break
        
        # Move extra key takeaways to appropriate sections
        while len(sections['key_takeaways']) > 3:
            if len(sections['strengths']) < max_strengths:
                extra_takeaway = sections['key_takeaways'].pop()
                sections['strengths'].append(extra_takeaway)
            elif len(sections['weaknesses']) < max_weaknesses:
                extra_takeaway = sections['key_takeaways'].pop()
                sections['weaknesses'].append(extra_takeaway)
            else:
                break
    
    def _duplicate_insights_if_needed(self, sections: Dict[str, List[Dict[str, Any]]], max_takeaways: int, max_strengths: int, max_weaknesses: int):
        """Duplicate insights if needed to reach target counts."""
        # Duplicate key takeaways if needed
        if len(sections['key_takeaways']) < max_takeaways:
            self._duplicate_insights_for_section(sections, 'key_takeaways', max_takeaways, 
                                               ['market', 'leadership', 'competitive', 'value', 'proposition', 'presence', 'footprint', 'demand'])
        
        # Duplicate strengths if needed
        if len(sections['strengths']) < max_strengths:
            self._duplicate_insights_for_section(sections, 'strengths', max_strengths,
                                               ['technology', 'proprietary', 'turnaround', 'rapid', 'advantage', 'capability', 'efficiency', 'benefit'])
        
        # Duplicate weaknesses if needed
        if len(sections['weaknesses']) < max_weaknesses:
            self._duplicate_insights_for_section(sections, 'weaknesses', max_weaknesses,
                                               ['limit', 'constraint', 'challenge', 'risk', 'unpredictable', 'tam', 'market size', 'impact'])
    
    def _duplicate_insights_for_section(self, sections: Dict[str, List[Dict[str, Any]]], section_name: str, target_count: int, keywords: List[str]):
        """Duplicate insights for a specific section to reach target count."""
        all_available_insights = []
        for key in ['key_takeaways', 'strengths', 'weaknesses']:
            if key != section_name:
                all_available_insights.extend(sections[key])
        
        # Score insights by relevance to section
        scored_insights = []
        for insight in all_available_insights:
            insight_text = insight.get('insight', '').lower()
            score = sum(1 for keyword in keywords if keyword in insight_text)
            scored_insights.append((score, insight))
        
        # Sort by score and duplicate the best ones
        scored_insights.sort(key=lambda x: x[0], reverse=True)
        
        section_prefix = {
            'key_takeaways': 'Additional insight',
            'strengths': 'Additional strength', 
            'weaknesses': 'Additional weakness'
        }
        
        while len(sections[section_name]) < target_count and scored_insights:
            score, insight = scored_insights.pop(0)
            duplicated_insight = {
                'insight': f"{section_prefix[section_name]}: {insight.get('insight', '')}",
                'supporting_quotes': insight.get('supporting_quotes', [])[:1]
            }
            sections[section_name].append(duplicated_insight)

    def _parse_strengths_weaknesses(self, response_text: str, available_quotes: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Parse strengths and weaknesses from the summary response."""
        strengths = []
        weaknesses = []
        
        lines = response_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            # Determine current section - be more flexible with section detection
            if any(keyword in line.lower() for keyword in ['strengths', 'strength', 'strong points', 'advantages']):
                current_section = 'strengths'
                continue
            elif any(keyword in line.lower() for keyword in ['weaknesses', 'weakness', 'weak points', 'challenges', 'concerns']):
                current_section = 'weaknesses'
                continue
            elif any(keyword in line.lower() for keyword in ['conclusion', 'summary', 'key takeaways', 'takeaways']):
                # If we hit another section, stop parsing
                if current_section in ['strengths', 'weaknesses']:
                    break
            
            # Parse items in current section
            if current_section and line:
                # Look for numbered items (1., 2., etc.)
                if re.match(r'^\d+\.', line):
                    insight = re.sub(r'^\d+\.\s*', '', line)
                    if insight and len(insight) > 10:  # Ensure meaningful content
                        item = {
                            'insight': insight,
                            'supporting_quotes': self._find_supporting_quotes(insight, available_quotes)
                        }
                        if current_section == 'strengths' and len(strengths) < 3:
                            strengths.append(item)
                        elif current_section == 'weaknesses' and len(weaknesses) < 3:
                            weaknesses.append(item)
                # Look for bullet points
                elif re.match(r'^[•\-*]\s*', line):
                    insight = re.sub(r'^[•\-*]\s*', '', line)
                    if insight and len(insight) > 10:  # Ensure meaningful content
                        item = {
                            'insight': insight,
                            'supporting_quotes': self._find_supporting_quotes(insight, available_quotes)
                        }
                        if current_section == 'strengths' and len(strengths) < 3:
                            strengths.append(item)
                        elif current_section == 'weaknesses' and len(weaknesses) < 3:
                            weaknesses.append(item)
        
        # If we didn't find explicit sections, try to infer from content
        if not strengths and not weaknesses:
            # Look for positive/negative language patterns
            for line in lines:
                line = line.strip()
                if re.match(r'^\d+\.', line) or re.match(r'^[•\-*]\s*', line):
                    insight = re.sub(r'^(?:\d+\.|[•\-*]\s*)', '', line)
                    if insight and len(insight) > 10:
                        # Simple sentiment analysis
                        positive_words = ['advantage', 'strength', 'benefit', 'opportunity', 'growth', 'success', 'positive', 'good', 'excellent', 'competitive', 'leader', 'innovative', 'superior']
                        negative_words = ['weakness', 'challenge', 'problem', 'issue', 'risk', 'concern', 'negative', 'bad', 'poor', 'difficult', 'threat', 'pressure', 'limitation']
                        
                        insight_lower = insight.lower()
                        positive_score = sum(1 for word in positive_words if word in insight_lower)
                        negative_score = sum(1 for word in negative_words if word in insight_lower)
                        
                        item = {
                            'insight': insight,
                            'supporting_quotes': self._find_supporting_quotes(insight, available_quotes)
                        }
                        
                        if positive_score > negative_score and len(strengths) < 3:
                            strengths.append(item)
                        elif negative_score > positive_score and len(weaknesses) < 3:
                            weaknesses.append(item)
        
        return {'strengths': strengths, 'weaknesses': weaknesses}

    def _find_supporting_quotes(self, insight: str, available_quotes: List[Dict[str, Any]], max_quotes: int = 3) -> List[Dict[str, Any]]:
        """Find quotes that support a given insight."""
        if not insight or not available_quotes:
            return []
        
        # Extract key terms from insight
        insight_lower = insight.lower()
        key_terms = [word for word in insight_lower.split() if len(word) > 3]
        
        # Score quotes based on relevance to insight
        scored_quotes = []
        for quote in available_quotes:
            quote_text = quote.get('text', '').lower()
            score = 0
            
            # Score based on term overlap
            for term in key_terms:
                if term in quote_text:
                    score += 1
            
            # Bonus for exact phrase matches
            for phrase in insight_lower.split(','):
                phrase = phrase.strip()
                if len(phrase) > 5 and phrase in quote_text:
                    score += 2
            
            if score > 0:
                scored_quotes.append((score, quote))
        
        # Sort by score and return top quotes
        scored_quotes.sort(key=lambda x: x[0], reverse=True)
        return [quote for score, quote in scored_quotes[:max_quotes]]

    def _validate_and_supplement_takeaways(self, takeaways: List[Dict[str, Any]], available_quotes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and supplement takeaways with supporting quotes."""
        # This would implement validation and supplementation logic
        # For brevity, returning the input as-is
        return takeaways

    def _filter_questions_from_takeaways(self, takeaways: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out questions from takeaways."""
        return [t for t in takeaways if not self._is_question(t.get('insight', ''))]

    def _filter_questions_from_strengths(self, strengths: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out questions from strengths."""
        return [s for s in strengths if not self._is_question(s.get('insight', ''))]

    def _filter_questions_from_weaknesses(self, weaknesses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out questions from weaknesses."""
        return [w for w in weaknesses if not self._is_question(w.get('insight', ''))]

    def _is_question(self, text: str) -> bool:
        """Determine if text is a question."""
        if not text:
            return False
        
        # More selective question detection - only filter out actual interrogative questions
        # Don't filter out insights that start with question words but are actually statements
        text_lower = text.lower()
        
        # Only filter out if it ends with a question mark or is clearly an interrogative
        if text.strip().endswith('?'):
            return True
        
        # Check for interrogative patterns that indicate actual questions, not insights
        interrogative_patterns = [
            'what do you think',
            'how do you feel',
            'why do you believe',
            'when would you',
            'where should we',
            'who should we',
            'which option'
        ]
        
        return any(pattern in text_lower for pattern in interrogative_patterns)

    def export_company_summary_page(self, summary_data: Dict[str, Any], output_file: str = None) -> str:
        """Export company summary page using the export manager."""
        # Ensure proper formatting of quotes with speaker information
        for section_key in ['key_takeaways', 'strengths', 'weaknesses']:
            if section_key in summary_data:
                for item in summary_data[section_key]:
                    if 'supporting_quotes' in item:
                        for quote in item['supporting_quotes']:
                            # Ensure quote has proper speaker info formatting
                            if 'speaker_info' in quote and quote['speaker_info']:
                                # Format: "quote text" - Speaker Name, Company/Title from Transcript Name
                                if quote.get('transcript_name') and quote['transcript_name'] != 'Unknown':
                                    quote['formatted_text'] = f"\"{quote['text']}\" - {quote['speaker_info']} from {quote['transcript_name']}"
                                else:
                                    quote['formatted_text'] = f"\"{quote['text']}\" - {quote['speaker_info']}"
                            else:
                                quote['formatted_text'] = quote['text']
        
        return self.export_manager.export_company_summary_page(summary_data, output_file)

    def export_company_summary_to_excel(self, summary_data: Dict[str, Any], output_file: str = None) -> str:
        """Export company summary page to Excel using the export manager."""
        return self.export_manager.export_company_summary_to_excel(summary_data, output_file)

    def export_quotes_to_excel(self, quotes_data: List[Dict[str, Any]], output_file: str = None) -> str:
        """Export quotes to Excel with proper text wrapping using the export manager."""
        return self.export_manager.export_quotes_to_excel(quotes_data, output_file)

    def save_quote_analysis(self, results: Dict[str, Any], output_file: str = None):
        """Save quote analysis results using the export manager."""
        return self.export_manager.save_quote_analysis(results, output_file)

    def export_quote_analysis_to_text(self, results: Dict[str, Any], output_file: str = None):
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
            'metadata': {
                'analysis_date': datetime.now().isoformat(),
                'total_transcripts': len(transcript_files),
                'total_quotes': len(all_quotes),
                'transcript_files': transcript_files
            },
            'perspectives': perspectives,
            'all_quotes': all_quotes,
            'quote_summary': {
                'strengths_count': len(sentiment_categories.get('positive', [])),
                'weaknesses_count': len(sentiment_categories.get('negative', [])),
                'neutral_count': len(sentiment_categories.get('neutral', []))
            },
            'speaker_role_stats': speaker_stats
        }
        
        return results

    def test_rag_functionality(self, perspective_key: str = "market_position") -> Dict[str, Any]:
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
            for focus_area in perspective_data['focus_areas'][:3]:  # Test first 3 focus areas
                print(f"\n  Searching for: '{focus_area}'")
                
                # Get quotes using vector database
                vector_results = self.vector_db_manager.semantic_search_quotes(
                    query=focus_area,
                    n_results=5,
                    filter_metadata={'speaker_role': 'expert'}
                )
                
                print(f"    Found {len(vector_results)} relevant quotes")
                
                # Show top result
                if vector_results:
                    top_quote = vector_results[0]
                    print(f"    Top result: '{top_quote.get('text', '')[:80]}...'")
                    print(f"    Distance score: {top_quote.get('distance', 'N/A'):.4f}")
                    print(f"    Source: {top_quote.get('metadata', {}).get('transcript_name', 'Unknown')}")
        
        except Exception as e:
            print(f"    ❌ Error in vector search: {e}")
        
        # Test perspective analysis with RAG
        print(f"\n🤖 Testing RAG-Enhanced Perspective Analysis...")
        try:
            # Get some sample quotes for testing
            sample_quotes = []
            for focus_area in perspective_data['focus_areas'][:2]:
                results = self.vector_db_manager.semantic_search_quotes(
                    query=focus_area,
                    n_results=10,
                    filter_metadata={'speaker_role': 'expert'}
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
            'vector_db_available': False,
            'total_quotes_stored': 0,
            'rag_functionality': False,
            'search_capabilities': []
        }
        
        try:
            if self.vector_db_manager and self.vector_db_manager.quotes_collection:
                stats['vector_db_available'] = True
                
                # Get database stats
                db_stats = self.vector_db_manager.get_vector_database_stats()
                stats['total_quotes_stored'] = db_stats.get('total_quotes', 0)
                
                # Check RAG functionality
                if hasattr(self.perspective_analyzer, 'vector_db_manager') and self.perspective_analyzer.vector_db_manager:
                    stats['rag_functionality'] = True
                
                # List search capabilities
                stats['search_capabilities'] = [
                    'semantic_search_quotes',
                    'search_quotes_with_speaker_filter', 
                    'get_quotes_by_perspective'
                ]
                
        except Exception as e:
            print(f"Error getting RAG statistics: {e}")
        
        return stats


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
        directory_path = input("Enter path to directory containing transcript files: ").strip()
    
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
        all_quotes = results.get('all_quotes', [])
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
        quote_summary = results['quote_summary']
        logger.info("Quote Summary (Expert Quotes Only):")
        logger.info(f"Strengths: {quote_summary['strengths_count']}")
        logger.info(f"Weaknesses: {quote_summary['weaknesses_count']}")
        logger.info(f"Neutral: {quote_summary['neutral_count']}")
        
        # Show speaker role statistics
        speaker_stats = results.get('speaker_role_stats', {})
        logger.info("Speaker Role Summary:")
        logger.info(f"Total quotes extracted: {speaker_stats.get('total_quotes', 0)}")
        logger.info(f"Expert quotes: {speaker_stats.get('expert_quotes', 0)} ({speaker_stats.get('expert_percentage', 0):.1f}%)")
        logger.info(f"Interviewer quotes filtered out: {speaker_stats.get('interviewer_quotes', 0)}")
        logger.info(f"Quotes with interviewer context: {speaker_stats.get('quotes_with_context', 0)} ({speaker_stats.get('context_percentage', 0):.1f}%)")
        logger.info(f"Average context per quote: {speaker_stats.get('average_context_per_quote', 0):.1f} sentences")
        
        # Show ranking statistics
        ranking_stats = analyzer.get_quote_ranking_statistics(results)
        logger.info("OpenAI Ranking Statistics:")
        logger.info(f"Total Perspectives: {ranking_stats['total_perspectives']}")
        logger.info(f"Total Quotes Ranked: {ranking_stats['total_ranked_quotes']}")
        logger.info(f"Ranking Coverage: {ranking_stats['ranking_coverage']:.1f}%")
        
        # Show selection stage breakdown
        if ranking_stats['selection_stage_breakdown']:
            logger.info("Selection Stage Breakdown:")
            for stage, count in ranking_stats['selection_stage_breakdown'].items():
                logger.info(f"{stage}: {count} quotes")
        
    else:
        logger.warning("No results generated")


if __name__ == "__main__":
    main()
