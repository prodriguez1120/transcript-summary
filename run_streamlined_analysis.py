#!/usr/bin/env python3
"""
Integration script to run streamlined quote analysis with existing quote extraction.
"""

import os
import sys
import logging
from pathlib import Path

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from streamlined_quote_analysis import StreamlinedQuoteAnalysis
from quote_analysis_tool import ModularQuoteAnalysisTool
from env_config import get_openai_api_key

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('flexxray.log', mode='a', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Set specific logger level for this module
logger.setLevel(logging.INFO)

# Add a separator line in the log file for new runs
logger.info("=" * 80)
logger.info("NEW ANALYSIS RUN STARTED")
logger.info("=" * 80)

# Log environment information for debugging
logger.info(f"Python version: {sys.version}")
logger.info(f"Working directory: {os.getcwd()}")
logger.info(f"Script path: {os.path.abspath(__file__)}")
logger.info(f"Transcript directory exists: {os.path.exists('FlexXray Transcripts')}")
logger.info(f"ChromaDB directory exists: {os.path.exists('chroma_db')}")
logger.info(f"Output directory exists: {os.path.exists('Outputs')}")
logger.info("=" * 80)


def load_existing_quotes(api_key: str):
    """Load quotes from existing analysis tool."""
    import time
    start_time = time.time()
    
    logger.info("Loading existing quote extraction system...")
    logger.debug(f"API key length: {len(api_key)} characters")

    # Initialize the existing tool with API key
    try:
        existing_tool = ModularQuoteAnalysisTool(api_key=api_key)
        logger.info("✅ ModularQuoteAnalysisTool initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize ModularQuoteAnalysisTool: {e}")
        return []

    # Get the transcript directory
    # Use current working directory for consistency with environment logging
    transcript_dir = "FlexXray Transcripts"
    
    if not os.path.exists(transcript_dir):
        logger.warning(f"Transcript directory not found: {transcript_dir}")
        logger.warning(f"Current working directory: {os.getcwd()}")
        logger.warning(f"Available directories: {[d for d in os.listdir('.') if os.path.isdir(d)]}")
        return []

    # Extract quotes using existing system
    logger.info("Extracting quotes from transcripts...")
    logger.debug(f"Transcript directory: {os.path.abspath(transcript_dir)}")

    try:
        # Use the existing method that processes all transcripts
        logger.debug("Calling process_transcripts_for_quotes...")
        results = existing_tool.process_transcripts_for_quotes(transcript_dir)
        
        # Validate that results is a dictionary
        if not isinstance(results, dict):
            logger.error(f"❌ Unexpected result format from quote extraction: {type(results)}")
            logger.error("   Expected dictionary, got: {results}")
            return []
        
        # Check if results is empty
        if not results:
            logger.warning("❌ Quote extraction returned empty results")
            return []
        
        # Debug: show available keys
        available_keys = list(results.keys())
        logger.debug(f"📋 Available keys in results: {available_keys}")
        
        # The process_transcripts_for_quotes method returns different structure
        # Check for expected keys and handle accordingly
        if "total_quotes" in results:
            total_quotes = results.get("total_quotes", 0)
            logger.info(f"Total quotes reported: {total_quotes}")
            
            # If we have quotes stored in vector database, retrieve them
            if total_quotes > 0:
                try:
                    # Use the existing tool's method to get quotes from vector database
                    # Search for quotes with a broad query to get all quotes
                    all_quotes = existing_tool.vector_db_manager.semantic_search_quotes(
                        query="FlexXray company business operations", 
                        n_results=total_quotes
                    )
                    logger.info(f"Retrieved {len(all_quotes)} quotes from vector database")
                except Exception as e:
                    logger.error(f"Failed to retrieve quotes from vector database: {e}")
                    all_quotes = []
            else:
                all_quotes = []
        else:
            logger.error("❌ 'total_quotes' key not found in results")
            logger.error(f"   Available keys: {available_keys}")
            return []

        # Validate that all_quotes is a list
        if not isinstance(all_quotes, list):
            logger.error(f"❌ 'all_quotes' is not a list: {type(all_quotes)}")
            logger.error("   Expected list of quotes, got: {all_quotes}")
            return []
        
        # Check if the list is empty
        if not all_quotes:
            logger.warning("❌ No quotes found in 'all_quotes' list")
            return []

        # Validate quote structure (check first few quotes)
        if all_quotes:
            sample_quote = all_quotes[0]
            if not isinstance(sample_quote, dict):
                logger.error(f"❌ Quotes are not dictionaries: {type(sample_quote)}")
                return []
            
            # Check for required fields
            required_fields = ["text", "speaker", "document"]
            missing_fields = [field for field in required_fields if field not in sample_quote]
            if missing_fields:
                logger.error(f"❌ Quotes missing required fields: {missing_fields}")
                logger.error(f"   Sample quote keys: {list(sample_quote.keys())}")
                return []
            
            logger.info(f"✅ Quote structure validated - found required fields: {required_fields}")

        elapsed_time = time.time() - start_time
        logger.info(f"Total quotes extracted: {len(all_quotes)} in {elapsed_time:.2f} seconds")
        return all_quotes

    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(f"Error processing transcripts after {elapsed_time:.2f} seconds: {e}")
        return []


def run_streamlined_analysis():
    """Run the streamlined quote analysis."""
    import time
    total_start_time = time.time()
    
    logger.info("FlexXray Streamlined Quote Analysis")
    logger.info("===================================")

    # Check if .env file exists
    env_file = ".env"
    if not os.path.exists(env_file):
        logger.warning("⚠️  .env file not found in project root")
        logger.warning("   This may cause API key loading to fail")
        logger.warning("   Consider creating a .env file with your OpenAI API key")

    # Get OpenAI API key from environment configuration
    try:
        api_key = get_openai_api_key()
        logger.info("✅ OpenAI API key loaded successfully")
        
        # Validate API key format
        if not api_key.startswith("sk-"):
            logger.warning("❌ Warning: API key format appears invalid (should start with 'sk-')")
            logger.warning("   Continuing anyway, but this may cause failures...")
            
    except ValueError as e:
        logger.error(f"❌ Failed to load OpenAI API key: {e}")
        logger.error("Please ensure OPENAI_API_KEY is set in your .env file or environment variables.")
        logger.error("\nTo set up your environment:")
        logger.error("1. Create a .env file in the project root")
        logger.error("2. Add: OPENAI_API_KEY=your_api_key_here")
        logger.error("3. Or set the environment variable: set OPENAI_API_KEY=your_api_key_here")
        return

    # Load quotes
    logger.info("\nLoading existing quotes...")
    quote_load_start = time.time()
    quotes = load_existing_quotes(api_key)
    quote_load_time = time.time() - quote_load_start
    
    if not quotes:
        logger.warning("❌ No quotes found. This could be due to:")
        logger.warning("   - No transcripts in the 'FlexXray Transcripts' directory")
        logger.warning("   - Failed quote extraction from existing system")
        logger.warning("   - Vector database initialization issues")
        logger.warning("   - API key authentication problems")
        logger.info("\nExiting analysis.")
        return
    
    logger.info(f"✅ Successfully loaded {len(quotes)} quotes for analysis in {quote_load_time:.2f} seconds")

    # Initialize streamlined analyzer
    try:
        analyzer = StreamlinedQuoteAnalysis(api_key=api_key)
        logger.info("✅ StreamlinedQuoteAnalysis initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize StreamlinedQuoteAnalysis: {e}")
        logger.error("   This may be due to API key issues or OpenAI service problems")
        return

    # Generate company summary
    logger.info("\nStarting streamlined analysis...")
    analysis_start = time.time()
    try:
        summary_results = analyzer.generate_company_summary(quotes)
        analysis_time = time.time() - analysis_start
        logger.info(f"✅ Analysis completed in {analysis_time:.2f} seconds")
    except Exception as e:
        analysis_time = time.time() - analysis_start
        logger.error(f"❌ Error during summary generation after {analysis_time:.2f} seconds: {e}")
        logger.error("   This may be due to OpenAI API issues or quote processing problems")
        return

    if not summary_results:
        logger.warning("❌ No summary results generated. This could be due to:")
        logger.warning("   - Empty quote data")
        logger.warning("   - API rate limiting")
        logger.warning("   - Quote processing failures")
        logger.info("\nExiting analysis.")
        return

    # Save results
    save_start = time.time()
    output_file = analyzer.save_summary(summary_results)
    save_time = time.time() - save_start

    total_time = time.time() - total_start_time
    logger.info(f"\nAnalysis complete in {total_time:.2f} seconds!")
    logger.info(f"Results saved to: {output_file} in {save_time:.2f} seconds")

    # Display summary
    logger.info("\n" + "=" * 50)
    logger.info("SUMMARY OVERVIEW")
    logger.info("=" * 50)

    for category, results in summary_results.items():
        logger.info(f"\n{category.replace('_', ' ').title()}:")
        for result in results:
            question = result["question"]
            quote_count = len(result["selected_quotes"])
            avg_score = (
                sum(result["final_scores"]) / len(result["final_scores"])
                if result["final_scores"]
                else 0
            )

            logger.info(
                f"  • {question[:60]}... ({quote_count} quotes, avg score: {avg_score:.1f})"
            )
    
    logger.info(f"\n🎉 Total analysis completed successfully in {total_time:.2f} seconds")
    logger.info("=" * 80)


if __name__ == "__main__":
    run_streamlined_analysis()
