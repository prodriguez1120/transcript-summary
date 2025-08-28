#!/usr/bin/env python3
"""
Quote Analysis Tool for FlexXray Transcripts

⚠️  DEPRECATED: This tool is deprecated and will be removed in a future version.
   Use `run_streamlined_analysis.py` instead for better performance and accuracy.

This is a thin CLI wrapper that uses the WorkflowManager for orchestration.
The tool provides a simple command-line interface to execute quote analysis workflows.

MIGRATION GUIDE:
- For quick, focused analysis: Use `run_streamlined_analysis.py`
- For comprehensive, multi-perspective analysis: Use this tool (deprecated)
- For production use: Migrate to streamlined system
"""

import os
import sys
import argparse
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

# Load environment variables from centralized configuration
from settings import get_openai_api_key

# Import logging configuration
from logging_config import setup_logger

# Import the workflow manager
from workflow_manager import WorkflowManager, WorkflowConfig

# Set up logger for this module
logger = setup_logger(__name__)


def main():
    """Main entry point for the quote analysis tool CLI."""
    
    # Show deprecation warning
    print("⚠️  WARNING: This tool is deprecated and will be removed in a future version.")
    print("   Use `run_streamlined_analysis.py` instead for better performance and accuracy.")
    print("   This tool will continue to work but is not recommended for new projects.\n")
    
    try:
        # Set up argument parser
        parser = argparse.ArgumentParser(
            description="FlexXray Quote Analysis Tool - CLI Interface (DEPRECATED)",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python quote_analysis_tool.py --directory "./FlexXray Transcripts"
  python quote_analysis_tool.py --config custom_config.json
  python quote_analysis_tool.py --verbose

⚠️  DEPRECATION NOTICE:
  This tool is deprecated. Use `run_streamlined_analysis.py` instead.
            """
        )
        
        parser.add_argument(
            "--directory", "-d",
            type=str,
            help="Path to directory containing transcript documents"
        )
        
        parser.add_argument(
            "--config", "-c",
            type=str,
            help="Path to custom workflow configuration file (JSON)"
        )
        
        parser.add_argument(
            "--verbose", "-v",
            action="store_true",
            help="Enable verbose logging"
        )
        
        parser.add_argument(
            "--output", "-o",
            type=str,
            help="Output directory for results (default: ./quote_analysis_output)"
        )
        
        args = parser.parse_args()
        
        # Set up logging level
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Get OpenAI API key
        api_key = get_openai_api_key()
        if not api_key:
            print("Error: OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
            return 1
        
        # Create workflow configuration
        workflow_config = WorkflowConfig()
        
        # Initialize workflow manager
        workflow_manager = WorkflowManager(api_key, workflow_config)
        
        # Execute workflow
        print("=== FlexXray Quote Analysis Tool ===")
        print("Starting quote analysis workflow...")
        
        # Use default directory if not specified
        transcript_directory = args.directory or "FlexXray Transcripts"
        output_directory = args.output or "./Outputs"
        
        result = workflow_manager.execute_workflow(
            directory_path=transcript_directory,
            output_directory=output_directory
        )
        
        if result and not result.get("error"):
            print("\n✅ Quote analysis completed successfully!")
            print(f"Results saved to: {output_directory}")
            return 0
        else:
            error_msg = result.get("error", "Unknown error") if result else "No results returned"
            print(f"\n❌ Quote analysis failed: {error_msg}")
            return 1
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"Unexpected error: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())
