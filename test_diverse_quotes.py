#!/usr/bin/env python3
"""
Test script to verify that diverse_quotes is actually populated
"""

import logging
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from quote_analysis_tool import ModularQuoteAnalysisTool
from env_config import get_env_config, get_openai_api_key

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_diverse_quotes_population():
    """Test if diverse_quotes is actually populated."""
    logger.info("Testing diverse_quotes population...")
    
    try:
        # Get environment configuration and API key
        env_config = get_env_config()
        api_key = get_openai_api_key()
        
        if not api_key:
            logger.error("❌ OpenAI API key not found. Please check your environment configuration.")
            return False
        
        logger.info("✅ OpenAI API key loaded successfully")
        
        # Initialize the tool
        tool = ModularQuoteAnalysisTool(api_key=api_key)
        logger.info("✅ Quote analysis tool initialized successfully")
        
        # Test the diverse quotes generation directly
        logger.info("🔍 Testing diverse quotes generation...")
        
        # Get some sample quotes first
        if hasattr(tool, 'vector_db_manager') and tool.vector_db_manager:
            # Try to get some quotes from the database
            try:
                sample_quotes = tool.vector_db_manager.get_all_quotes(limit=100)
                logger.info(f"Found {len(sample_quotes)} sample quotes in database")
                
                if sample_quotes:
                    # Test the diverse quotes method directly
                    diverse_quotes = tool._get_diverse_quotes(sample_quotes, "summary", 30)
                    logger.info(f"✅ diverse_quotes populated: {len(diverse_quotes)} quotes")
                    
                    if diverse_quotes:
                        logger.info(f"First quote: {diverse_quotes[0]}")
                        logger.info(f"Last quote: {diverse_quotes[-1]}")
                        
                        # Check quote sources
                        transcript_sources = set(quote.get('transcript_name', 'Unknown') for quote in diverse_quotes)
                        logger.info(f"Quotes from transcripts: {transcript_sources}")
                        
                        return True
                    else:
                        logger.error("❌ diverse_quotes is empty!")
                        return False
                else:
                    logger.warning("⚠️ No sample quotes found in database")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ Error accessing vector database: {e}")
                return False
        else:
            logger.warning("⚠️ Vector database manager not available")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error in test: {e}")
        logger.exception("Full exception details:")
        return False

def main():
    """Main test function."""
    logger.info("🧪 Starting diverse_quotes population test...")
    
    success = test_diverse_quotes_population()
    
    if success:
        logger.info("✅ Test completed successfully - diverse_quotes is populated")
    else:
        logger.error("❌ Test failed - diverse_quotes is not populated")
        sys.exit(1)

if __name__ == "__main__":
    main()
