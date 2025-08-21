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
from typing import List, Dict, Any, Tuple
from pathlib import Path
import time
from datetime import datetime

# Import our modular components
from quote_analysis_core import QuoteAnalysisTool
from quote_extraction import QuoteExtractor
from vector_database import VectorDatabaseManager
from perspective_analysis import PerspectiveAnalyzer
from export_utils import ExportManager

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
        
        self.perspective_analyzer = PerspectiveAnalyzer(self.client)
        
        self.export_manager = ExportManager()

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
        
        print("Generating company summary page using OpenAI...")
        
        # Clean and validate quotes
        cleaned_quotes = self._clean_and_validate_quotes(all_quotes)
        if not cleaned_quotes:
            return {}
        
        # Get diverse quotes for analysis
        diverse_quotes = self._get_diverse_quotes(cleaned_quotes, "summary", 50)
        
        # Create summary prompt
        summary_prompt = self._create_summary_prompt(diverse_quotes)
        
        try:
            # Call OpenAI for summary generation
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert business analyst creating a comprehensive company summary."},
                    {"role": "user", "content": summary_prompt}
                ],
                temperature=0.3,
                max_tokens=3000
            )
            
            # Parse summary response
            summary_data = self._parse_summary_response(response.choices[0].message.content, diverse_quotes)
            
            print("Company summary page generated successfully")
            return summary_data
            
        except Exception as e:
            print(f"Error generating company summary page: {e}")
            return {}

    def _create_summary_prompt(self, quotes: List[Dict[str, Any]]) -> str:
        """Create the prompt for OpenAI company summary generation."""
        prompt = """Based on the following expert quotes from FlexXray interviews, create a comprehensive company summary page.

The summary should include:

1. KEY TAKEAWAYS (3-5 bullet points with supporting quotes)
2. STRENGTHS (3-5 bullet points with supporting quotes)
3. WEAKNESSES (3-5 bullet points with supporting quotes)

Guidelines:
- Focus on actionable business insights
- Use specific quotes to support each point
- Keep insights concise and punchy
- Avoid questions in the output
- Select 1-2 most relevant quotes per insight

Expert Quotes:
"""
        
        for i, quote in enumerate(quotes[:30], 1):  # Limit to 30 quotes for summary
            prompt += f"\nQuote {i}: {quote.get('text', '')}"
            if quote.get('transcript_name'):
                prompt += f" [From: {quote['transcript_name']}]"
        
        prompt += """

Please respond with a structured format that can be easily parsed into sections.
Focus on the most important insights that emerge from these quotes.
"""
        
        return prompt

    def _parse_summary_response(self, response_text: str, available_quotes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse OpenAI's summary response and structure it."""
        try:
            # Extract sections
            key_takeaways = self._parse_summary_takeaways(response_text, available_quotes)
            strengths_weaknesses = self._parse_strengths_weaknesses(response_text, available_quotes)
            
            # Validate and supplement takeaways
            validated_takeaways = self._validate_and_supplement_takeaways(key_takeaways, available_quotes)
            validated_strengths = self._validate_and_supplement_takeaways(strengths_weaknesses.get('strengths', []), available_quotes)
            validated_weaknesses = self._validate_and_supplement_takeaways(strengths_weaknesses.get('weaknesses', []), available_quotes)
            
            # Filter out questions
            filtered_takeaways = self._filter_questions_from_takeaways(validated_takeaways)
            filtered_strengths = self._filter_questions_from_strengths(validated_strengths)
            filtered_weaknesses = self._filter_questions_from_weaknesses(validated_weaknesses)
            
            return {
                'key_takeaways': filtered_takeaways,
                'strengths': filtered_strengths,
                'weaknesses': filtered_weaknesses,
                'generation_timestamp': datetime.now().isoformat(),
                'total_quotes_analyzed': len(available_quotes)
            }
            
        except Exception as e:
            print(f"Error parsing summary response: {e}")
            return {}

    def _parse_summary_takeaways(self, response_text: str, available_quotes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse key takeaways from the summary response."""
        takeaways = []
        
        # Look for key takeaways section
        lines = response_text.split('\n')
        in_takeaways = False
        
        for line in lines:
            line = line.strip()
            
            # Check if we're entering key takeaways section
            if any(keyword in line.lower() for keyword in ['key takeaways', 'takeaways', 'key points', 'main insights']):
                in_takeaways = True
                continue
            
            # Check if we're leaving key takeaways section
            if in_takeaways and any(keyword in line.lower() for keyword in ['strengths', 'weaknesses', 'conclusion']):
                break
            
            # If we're in takeaways section, look for numbered or bulleted items
            if in_takeaways and line:
                # Look for numbered items (1., 2., etc.)
                if re.match(r'^\d+\.', line):
                    insight = re.sub(r'^\d+\.\s*', '', line)
                    if insight:
                        takeaways.append({
                            'insight': insight,
                            'supporting_quotes': self._find_supporting_quotes(insight, available_quotes)
                        })
                # Look for bullet points
                elif re.match(r'^[•\-*]\s*', line):
                    insight = re.sub(r'^[•\-*]\s*', '', line)
                    if insight:
                        takeaways.append({
                            'insight': insight,
                            'supporting_quotes': self._find_supporting_quotes(insight, available_quotes)
                        })
        
        return takeaways

    def _parse_strengths_weaknesses(self, response_text: str, available_quotes: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Parse strengths and weaknesses from the summary response."""
        strengths = []
        weaknesses = []
        
        lines = response_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            # Determine current section
            if any(keyword in line.lower() for keyword in ['strengths', 'strength']):
                current_section = 'strengths'
                continue
            elif any(keyword in line.lower() for keyword in ['weaknesses', 'weakness']):
                current_section = 'weaknesses'
                continue
            elif any(keyword in line.lower() for keyword in ['conclusion', 'summary', 'key takeaways']):
                break
            
            # Parse items in current section
            if current_section and line:
                # Look for numbered items (1., 2., etc.)
                if re.match(r'^\d+\.', line):
                    insight = re.sub(r'^\d+\.\s*', '', line)
                    if insight:
                        item = {
                            'insight': insight,
                            'supporting_quotes': self._find_supporting_quotes(insight, available_quotes)
                        }
                        if current_section == 'strengths':
                            strengths.append(item)
                        else:
                            weaknesses.append(item)
                # Look for bullet points
                elif re.match(r'^[•\-*]\s*', line):
                    insight = re.sub(r'^[•\-*]\s*', '', line)
                    if insight:
                        item = {
                            'insight': insight,
                            'supporting_quotes': self._find_supporting_quotes(insight, available_quotes)
                        }
                        if current_section == 'strengths':
                            strengths.append(item)
                        else:
                            weaknesses.append(item)
        
        return {'strengths': strengths, 'weaknesses': weaknesses}

    def _find_supporting_quotes(self, insight: str, available_quotes: List[Dict[str, Any]], max_quotes: int = 2) -> List[Dict[str, Any]]:
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
        
        # Simple question detection
        question_indicators = ['?', 'what', 'how', 'why', 'when', 'where', 'who', 'which']
        text_lower = text.lower()
        
        return any(indicator in text_lower for indicator in question_indicators)

    def export_company_summary_page(self, summary_data: Dict[str, Any], output_file: str = None) -> str:
        """Export company summary page using the export manager."""
        return self.export_manager.export_company_summary_page(summary_data, output_file)

    def export_company_summary_to_excel(self, summary_data: Dict[str, Any], output_file: str = None) -> str:
        """Export company summary page to Excel using the export manager."""
        return self.export_manager.export_company_summary_to_excel(summary_data, output_file)

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


def main():
    """Main function to run the quote analysis tool."""
    print("FlexXray Quote Analysis Tool (Modular Version)")
    print("=" * 50)
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("Please set OPENAI_API_KEY environment variable")
        return
    
    # Initialize the tool
    try:
        analyzer = ModularQuoteAnalysisTool()
        print("Quote analysis tool initialized successfully")
    except Exception as e:
        print(f"Error initializing tool: {e}")
        return
    
    # Set default directory
    default_directory = "FlexXray Transcripts"
    
    if os.path.exists(default_directory):
        directory_path = default_directory
        print(f"Using default directory: {directory_path}")
    else:
        directory_path = input("Enter path to directory containing transcript files: ").strip()
    
    if not os.path.exists(directory_path):
        print(f"Directory {directory_path} does not exist")
        return
    
    # Process transcripts
    print(f"\nProcessing transcripts from: {directory_path}")
    results = analyzer.process_transcripts_for_quotes(directory_path)
    
    if results:
        # Save results
        analyzer.save_quote_analysis(results)
        analyzer.export_quote_analysis_to_text(results)
        
        print(f"\nAnalysis complete!")
        print(f"Processed {results['metadata']['total_transcripts']} transcripts")
        print(f"Extracted {results['metadata']['total_quotes']} quotes")
        print(f"Generated 3 key perspective analyses")
        print(f"Created strengths and weaknesses buckets")
        
        # Generate and export the company summary page
        print(f"\nGenerating company summary page...")
        all_quotes = results.get('all_quotes', [])
        if all_quotes:
            summary_page = analyzer.generate_company_summary_page(all_quotes)
            if summary_page:
                # Export to both text and Excel formats
                text_file = analyzer.export_company_summary_page(summary_page)
                excel_file = analyzer.export_company_summary_to_excel(summary_page)
                print(f"Company summary page generated successfully!")
                print(f"  Text file: {text_file}")
                print(f"  Excel file: {excel_file}")
            else:
                print(f"Failed to generate company summary page")
        else:
            print(f"No quotes available for company summary page")
        
        # Show summary
        quote_summary = results['quote_summary']
        print(f"\nQuote Summary (Expert Quotes Only):")
        print(f"  Strengths: {quote_summary['strengths_count']}")
        print(f"  Weaknesses: {quote_summary['weaknesses_count']}")
        print(f"  Neutral: {quote_summary['neutral_count']}")
        
        # Show speaker role statistics
        speaker_stats = results.get('speaker_role_stats', {})
        print(f"\nSpeaker Role Summary:")
        print(f"  Total quotes extracted: {speaker_stats.get('total_quotes', 0)}")
        print(f"  Expert quotes: {speaker_stats.get('expert_quotes', 0)} ({speaker_stats.get('expert_percentage', 0):.1f}%)")
        print(f"  Interviewer quotes filtered out: {speaker_stats.get('interviewer_quotes', 0)}")
        print(f"  Quotes with interviewer context: {speaker_stats.get('quotes_with_context', 0)} ({speaker_stats.get('context_percentage', 0):.1f}%)")
        print(f"  Average context per quote: {speaker_stats.get('average_context_per_quote', 0):.1f} sentences")
        
        # Show ranking statistics
        ranking_stats = analyzer.get_quote_ranking_statistics(results['perspectives'])
        print(f"\nOpenAI Ranking Statistics:")
        print(f"  Total Perspectives: {ranking_stats['total_perspectives']}")
        print(f"  Total Quotes Ranked: {ranking_stats['total_ranked_quotes']}")
        print(f"  Ranking Coverage: {ranking_stats['ranking_coverage']:.1f}%")
        
        # Show selection stage breakdown
        if ranking_stats['selection_stage_breakdown']:
            print(f"  Selection Stage Breakdown:")
            for stage, count in ranking_stats['selection_stage_breakdown'].items():
                print(f"    {stage}: {count} quotes")
        
    else:
        print("No results generated")


if __name__ == "__main__":
    main()
