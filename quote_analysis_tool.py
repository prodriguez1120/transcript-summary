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
        self, api_key: str, chroma_persist_directory: str = "./chroma_db"
    ):
        """Initialize the modular quote analysis tool."""
        if not api_key:
            raise ValueError("API key is required and must be passed explicitly")
        
        super().__init__(api_key, chroma_persist_directory)
        
        # Initialize modular components
        self.quote_extractor = QuoteExtractor(
            min_quote_length=self.min_quote_length,
            max_quote_length=self.max_quote_length,
        )
        
        # Ensure API key is available from parent class
        assert self.api_key is not None, "API key should be set by parent class"
        
        self.vector_db_manager = VectorDatabaseManager(
            chroma_persist_directory=chroma_persist_directory,
            openai_api_key=self.api_key  # Pass the API key from parent class
        )
        
        # Test vector database initialization and validate OpenAI embeddings
        try:
            # First, test basic vector database connectivity
            db_stats = self.vector_db_manager.get_vector_database_stats()
            self.logger.info(f"Vector database initialization test: {db_stats}")
            
            if not db_stats.get("available"):
                raise RuntimeError("Vector database not available - ChromaDB initialization failed")
            
            self.logger.info(f"✅ ChromaDB path valid, {db_stats.get('total_quotes', 0)} quotes available")
            
            # Test OpenAI embeddings - fail fast if they're not working
            self.logger.info("🔍 Testing OpenAI embeddings...")
            try:
                # Test embedding generation with a simple text
                test_embedding = self.vector_db_manager._embedding_function(["test"])
                if test_embedding and len(test_embedding[0]) == 1536:  # text-embedding-3-small dimension
                    self.logger.info("✅ OpenAI embeddings working correctly (text-embedding-3-small)")
                else:
                    raise RuntimeError("OpenAI embeddings returned unexpected format")
                    
            except Exception as embedding_error:
                self.logger.error(f"❌ OpenAI embeddings test failed: {embedding_error}")
                raise RuntimeError(f"OpenAI embeddings are required but not working: {embedding_error}")
                
        except Exception as e:
            self.logger.error(f"❌ Critical initialization failure: {e}")
            raise RuntimeError(f"Quote analysis tool cannot initialize: {e}")

        # Use the API key from the parent class instead of calling os.getenv again
        # Use the API key from the parent class (which comes from centralized config)
        self.perspective_analyzer = PerspectiveAnalyzer(api_key=self.api_key)
        self.perspective_analyzer.set_vector_db_manager(self.vector_db_manager)
        
        self.export_manager = ExportManager()
        
        # Initialize environment configuration
        self.env_config = get_env_config()
        
        # Initialize our new refactored components
        self.quote_processor = QuoteProcessor()
        self.data_structure_manager = DataStructureManager()
        
        # Initialize summary generator with OpenAI client and prompt config
        prompt_config = get_prompt_config()
        # Use the OpenAI client from the parent class
        self.summary_generator = SummaryGenerator(self.client, prompt_config)
        
        # Define key_perspectives explicitly to ensure it's always available
        self.key_perspectives = [
            "business_model",
            "growth_potential", 
            "risk_factors"
        ]
        
        # Set default directory for transcript processing
        self.default_directory = "FlexXray Transcripts"
        
        logger.info("Quote analysis tool initialized successfully")

    def _verify_quotes_storage(self, quotes: List[Dict[str, Any]]) -> None:
        """Verify that quotes were properly stored in the vector database."""
        if not quotes:
            logger.warning("No quotes to verify")
            return
        
        # Test querying back a known quote
        test_quote = quotes[0]
        test_text = test_quote.get("text", "")[:100]  # First 100 chars
        
        try:
            # Search for the test quote
            search_results = self.vector_db_manager.semantic_search_quotes(
                test_text, n_results=5
            )
            
            if search_results:
                logger.info(f"✅ Quote storage verification successful: Found {len(search_results)} results")
                # Log the first result to show what was found
                first_result = search_results[0]
                logger.info(f"First result: {first_result.get('text', '')[:100]}...")
            else:
                logger.warning("⚠️ Quote storage verification: No search results found")
                
        except Exception as e:
            logger.error(f"❌ Quote storage verification failed: {e}")

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
        
        # Get diverse quotes for analysis - use configurable limit from environment
        max_quotes = self.env_config.max_quotes_for_analysis
        logger.info(f"Getting diverse quotes with max_quotes={max_quotes}")
        logger.info(f"Input expert_quotes count: {len(expert_quotes)}")
        
        diverse_quotes = self._get_diverse_quotes(
            expert_quotes, "summary", max_quotes
        )
        
        # Log detailed information about diverse_quotes
        logger.info(f"diverse_quotes populated: {len(diverse_quotes)} quotes")
        if diverse_quotes:
            logger.info(f"First quote sample: {diverse_quotes[0]}")
            logger.info(f"Last quote sample: {diverse_quotes[-1]}")
            # Log quote sources for diversity check
            transcript_sources = set(quote.get('transcript_name', 'Unknown') for quote in diverse_quotes)
            logger.info(f"Quotes from transcripts: {transcript_sources}")
        else:
            logger.error("diverse_quotes is empty! This will cause issues.")
            logger.error(f"expert_quotes count: {len(expert_quotes)}")
            logger.error(f"max_quotes setting: {max_quotes}")
            return {}
        
        # Log token usage estimation
        logger.info(f"🔍 Token logging enabled: {self.env_config.enable_token_logging}")
        if self.env_config.enable_token_logging:
            try:
                token_estimate = self.env_config.estimate_token_usage(len(diverse_quotes))
                logger.info(f"📊 Token Usage Estimate:")
                logger.info(f"   Quotes to process: {token_estimate['quote_count']}")
                logger.info(f"   Estimated total tokens: {token_estimate['total_tokens']:,}")
                logger.info(f"   Estimated cost: ${token_estimate['estimated_cost_usd']}")
                logger.info(f"   Model: {token_estimate['model']}")
                logger.info(f"   Model token limit: {self.env_config.model_token_limit:,}")
                logger.info(f"   Conservative threshold: {self.env_config.conservative_token_threshold:,}")
                
                # Show cost comparison with previous 60-quote approach
                if len(diverse_quotes) < 60:
                    old_estimate = self.env_config.estimate_token_usage(60)
                    cost_savings = old_estimate['estimated_cost_usd'] - token_estimate['estimated_cost_usd']
                    token_savings = old_estimate['total_tokens'] - token_estimate['total_tokens']
                    logger.info(f"💰 Cost Optimization:")
                    logger.info(f"   Previous approach (60 quotes): ${old_estimate['estimated_cost_usd']}")
                    logger.info(f"   Current approach ({len(diverse_quotes)} quotes): ${token_estimate['estimated_cost_usd']}")
                    logger.info(f"   Savings: ${cost_savings} (${token_savings:,} tokens)")
                
                # Warn if approaching limits - use configurable threshold based on model
                threshold = self.env_config.conservative_token_threshold
                if token_estimate['total_tokens'] > threshold:
                    logger.warning(f"⚠️ High token usage detected: {token_estimate['total_tokens']:,} tokens")
                    logger.warning(f"   Threshold: {threshold:,} tokens (80% of {self.env_config.model_token_limit:,} model limit)")
                    logger.warning(f"   Model: {self.env_config.openai_model_for_summary}")
                    logger.warning(f"   Consider reducing quote count or using shorter quotes")
            except Exception as e:
                logger.error(f"❌ Error calculating token usage: {e}")
        else:
            logger.info("📊 Token logging disabled - no usage estimates provided")
        
        # Use the summary generator for better results
        logger.info(f"Calling SummaryGenerator with {len(diverse_quotes)} diverse quotes")
        result = self.summary_generator.generate_company_summary_direct(diverse_quotes)
        logger.info(f"SummaryGenerator returned: {type(result)} with keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        if isinstance(result, dict) and "key_takeaways" in result:
            logger.info(f"Key takeaways count: {len(result['key_takeaways'])}")
            for i, takeaway in enumerate(result["key_takeaways"]):
                if isinstance(takeaway, dict):
                    quotes_count = len(takeaway.get("supporting_quotes", []))
                    logger.info(f"Takeaway {i+1}: {quotes_count} quotes")
        return result

    def enrich_quotes_for_export(self, quotes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enrich quotes with additional information for export using QuoteProcessor."""
        return self.quote_processor.enrich_quotes_for_export(quotes)

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
        logger.info(f"Processing transcripts from: {directory_path}")
        
        # Get transcript files
        transcript_files = []
        for file_path in Path(directory_path).glob("*.docx"):
            transcript_files.append(str(file_path))
        
        if not transcript_files:
            logger.warning("No transcript files found")
            return {}
        
        logger.info(f"Found {len(transcript_files)} transcript files")
        
        # Process each transcript
        all_quotes = []
        for file_path in transcript_files:
            transcript_name = Path(file_path).stem
            logger.info(f"Processing: {transcript_name}")
            
            # Extract text using QuoteExtractor
            text = self.quote_extractor.extract_text_from_document(file_path)
            if not text:
                logger.warning(f"No text extracted from {transcript_name}")
                continue
            
            # Extract quotes using QuoteExtractor
            quotes = self.quote_extractor.extract_quotes_from_text(text, transcript_name)
            if quotes:
                all_quotes.extend(quotes)
                logger.info(f"Extracted {len(quotes)} quotes from {transcript_name}")
            else:
                logger.warning(f"No quotes extracted from {transcript_name}")
        
        if not all_quotes:
            logger.warning("No quotes extracted from any transcripts")
            return {}
        
        logger.info(f"Total quotes extracted: {len(all_quotes)}")
        
        # Store quotes in vector database
        try:
            self.vector_db_manager.store_quotes_in_vector_db(all_quotes)
            logger.info("✅ Quotes stored in vector database")
            
            # Verify storage
            self._verify_quotes_storage(all_quotes)
            
        except Exception as e:
            logger.error(f"❌ Error storing quotes in vector database: {e}")
            return {}
        
        # Analyze perspectives
        perspective_results = self.analyze_perspectives(all_quotes)
        
        # Generate company summary
        company_summary = self.generate_company_summary_page(all_quotes)
        
        # Combine results
        results = {
            "transcripts_processed": len(transcript_files),
            "total_quotes": len(all_quotes),
            "perspective_analysis": perspective_results,
            "company_summary": company_summary,
            "generation_timestamp": datetime.now().isoformat(),
        }
        
        return results

    def analyze_perspectives(self, quotes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze quotes from different business perspectives."""
        if not quotes:
            return {}
        
        results = {}
        
        for perspective in self.key_perspectives:
            try:
                logger.info(f"Analyzing perspective: {perspective}")
                
                # Use the available method from PerspectiveAnalyzer
                perspective_data = {
                    "title": perspective.replace("_", " ").title(),
                    "description": f"Analysis of {perspective.replace('_', ' ')} perspective"
                }
                analysis_result = self.perspective_analyzer.analyze_perspective_with_quotes(
                    perspective_key=perspective,
                    perspective_data=perspective_data,
                    all_quotes=quotes
                )
                
                if not analysis_result or not analysis_result.get("quotes"):
                    logger.warning(f"No relevant quotes found for {perspective}")
                    continue
                
                # Extract quotes and themes from the analysis result
                ranked_quotes = analysis_result.get("quotes", [])
                themes = analysis_result.get("themes", [])
                
                results[perspective] = {
                    "quotes_analyzed": len(relevant_quotes),
                    "ranked_quotes": ranked_quotes,
                    "themes": themes,
                }
                
                logger.info(f"✅ {perspective} analysis completed")
                
            except Exception as e:
                logger.error(f"❌ Error analyzing {perspective}: {e}")
                results[perspective] = {"error": str(e)}
        
        return results

    def run_analysis(self, directory_path: str = None) -> Dict[str, Any]:
        """Run the complete quote analysis pipeline."""
        if not directory_path:
            directory_path = self.default_directory
        
        logger.info(f"Using default directory: {directory_path}")
        
        try:
            # Process transcripts and generate quotes
            results = self.process_transcripts_for_quotes(directory_path)
            
            if not results:
                logger.error("No results generated from transcript processing")
                return {}
            
            # Save results
            self.save_quote_analysis(results)
            self.export_quote_analysis_to_text(results)
            
            # Export company summary
            if "company_summary" in results:
                self.export_company_summary_page(results["company_summary"])
                self.export_company_summary_to_excel(results["company_summary"])
            
            # Export quotes to Excel
            if "perspective_analysis" in results:
                all_quotes = []
                for perspective_data in results["perspective_analysis"].values():
                    if "ranked_quotes" in perspective_data:
                        all_quotes.extend(perspective_data["ranked_quotes"])
                
                if all_quotes:
                    self.export_quotes_to_excel(all_quotes)
            
            logger.info("Analysis complete!")
            logger.info(f"Processed {results.get('transcripts_processed', 0)} transcripts")
            logger.info(f"Extracted {results.get('total_quotes', 0)} quotes")
            logger.info(f"Generated {len(results.get('perspective_analysis', {}))} key perspective analyses")
            logger.info(f"Created strengths and weaknesses buckets")
            
            # Use the company summary already generated in process_transcripts_for_quotes()
            if "company_summary" in results:
                logger.info("Company summary already generated, reusing existing result...")
                company_summary = results["company_summary"]
                
                if company_summary:
                    logger.info("Company summary page generated successfully!")
                    logger.info("✅ Company summary exported to text and Excel files")
                
                # Log basic statistics
                logger.info(f"✅ Analysis completed successfully with {len(company_summary.get('key_takeaways', []))} key takeaways")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in analysis pipeline: {e}")
            return {}

    def _get_all_quotes_from_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract all quotes from analysis results."""
        all_quotes = []
        
        if "perspective_analysis" in results:
            for perspective_data in results["perspective_analysis"].values():
                if "ranked_quotes" in perspective_data:
                    all_quotes.extend(perspective_data["ranked_quotes"])
        
        return all_quotes

    def _log_quote_summary_stats(self, results: Dict[str, Any]) -> None:
        """Log summary statistics about quotes."""
        all_quotes = self._get_all_quotes_from_results(results)
        
        if not all_quotes:
            return
        
        # Count by sentiment
        sentiment_counts = {}
        for quote in all_quotes:
            sentiment = quote.get("sentiment", "neutral")
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
        
        logger.info("Quote Summary (Expert Quotes Only):")
        for sentiment, count in sentiment_counts.items():
            logger.info(f"{sentiment.capitalize()}: {count}")

    def _log_speaker_role_stats(self, results: Dict[str, Any]) -> None:
        """Log statistics about speaker roles."""
        all_quotes = self._get_all_quotes_from_results(results)
        
        if not all_quotes:
            return
        
        total_quotes = len(all_quotes)
        expert_quotes = [q for q in all_quotes if q.get("speaker_role") == "expert"]
        interviewer_quotes = [q for q in all_quotes if q.get("speaker_role") == "interviewer"]
        
        quotes_with_context = [q for q in all_quotes if q.get("interviewer_context")]
        total_context_sentences = sum(
            len(q.get("interviewer_context", [])) for q in quotes_with_context
        )
        
        logger.info("Speaker Role Summary:")
        logger.info(f"Total quotes extracted: {total_quotes}")
        logger.info(f"Expert quotes: {len(expert_quotes)} ({len(expert_quotes)/total_quotes*100:.1f}%)")
        logger.info(f"Interviewer quotes filtered out: {len(interviewer_quotes)}")
        logger.info(f"Quotes with interviewer context: {len(quotes_with_context)} ({len(quotes_with_context)/total_quotes*100:.1f}%)")
        logger.info(f"Average context per quote: {total_context_sentences/len(quotes_with_context):.1f} sentences" if quotes_with_context else "Average context per quote: 0 sentences")

    def _log_openai_ranking_stats(self, results: Dict[str, Any]) -> None:
        """Log statistics about OpenAI ranking."""
        if "perspective_analysis" not in results:
            return
        
        total_perspectives = len(results["perspective_analysis"])
        total_quotes_ranked = 0
        selection_stages = {}
        
        for perspective_data in results["perspective_analysis"].values():
            if "ranked_quotes" in perspective_data:
                ranked_quotes = perspective_data["ranked_quotes"]
                total_quotes_ranked += len(ranked_quotes)
                
                for quote in ranked_quotes:
                    stage = quote.get("selection_stage", "unknown")
                    selection_stages[stage] = selection_stages.get(stage, 0) + 1
        
        if total_quotes_ranked > 0:
            ranking_coverage = total_quotes_ranked / total_quotes_ranked * 100
        else:
            ranking_coverage = 0
        
        logger.info("OpenAI Ranking Statistics:")
        logger.info(f"Total Perspectives: {total_perspectives}")
        logger.info(f"Total Quotes Ranked: {total_quotes_ranked}")
        logger.info(f"Ranking Coverage: {ranking_coverage:.1f}%")
        
        if selection_stages:
            logger.info("Selection Stage Breakdown:")
            for stage, count in selection_stages.items():
                logger.info(f"{stage}: {count} quotes")


def main():
    """Main entry point for the quote analysis tool."""
    logger.info("FlexXray Quote Analysis Tool (Modular Version)")
    logger.info("=" * 50)
    
    # Get environment configuration and API key
    try:
        env_config = get_env_config()
        api_key = get_openai_api_key()
        
        
        if not api_key:
            logger.error("❌ OpenAI API key not found. Please check your environment configuration.")
            return
        
        logger.info("✅ OpenAI API key loaded successfully")
        
        # Log configuration settings
        logger.info(f"📋 Configuration:")
        logger.info(f"   Max quotes for analysis: {env_config.max_quotes_for_analysis}")
        logger.info(f"   Max tokens per quote: {env_config.max_tokens_per_quote}")
        logger.info(f"   OpenAI model: {env_config.openai_model_for_summary}")
        logger.info(f"   Model token limit: {env_config.model_token_limit:,}")
        logger.info(f"   Conservative threshold: {env_config.conservative_token_threshold:,}")
        logger.info(f"   Token logging: {'enabled' if env_config.enable_token_logging else 'disabled'}")
        
    except Exception as e:
        logger.error(f"❌ Failed to load environment configuration: {e}")
        return
    
    # Initialize the tool with explicit API key
    try:
        tool = ModularQuoteAnalysisTool(api_key=api_key)
        logger.info("✅ Quote analysis tool initialized successfully")
        
        # Additional validation: ensure the tool is ready for analysis
        logger.info("🔍 Validating system readiness...")
        if not tool.vector_db_manager or not tool.vector_db_manager.chroma_client:
            raise RuntimeError("Vector database not properly initialized")
        
        logger.info("✅ System validation complete - ready for analysis")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize quote analysis tool: {e}")
        logger.error("💡 Please check:")
        logger.error("   - OpenAI API key is valid and has sufficient credits")
        logger.error("   - ChromaDB can be initialized")
        logger.error("   - Network connectivity to OpenAI API")
        return
    
    # Run analysis
    results = tool.run_analysis()
    
    if results:
        logger.info("✅ Analysis completed successfully!")
    else:
        logger.warning("❌ Analysis failed or no results generated.")


if __name__ == "__main__":
    main()
