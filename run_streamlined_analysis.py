#!/usr/bin/env python3
"""
Integration script to run streamlined quote analysis with existing quote extraction.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from streamlined_quote_analysis import StreamlinedQuoteAnalysis
from quote_analysis_tool import ModularQuoteAnalysisTool


def load_existing_quotes():
    """Load quotes from existing analysis tool."""
    print("Loading existing quote extraction system...")

    # Initialize the existing tool
    existing_tool = ModularQuoteAnalysisTool()

    # Get the transcript directory
    transcript_dir = "FlexXray Transcripts"
    if not os.path.exists(transcript_dir):
        print(f"Transcript directory not found: {transcript_dir}")
        return []

    # Extract quotes using existing system
    print("Extracting quotes from transcripts...")

    try:
        # Use the existing method that processes all transcripts
        results = existing_tool.process_transcripts_for_quotes(transcript_dir)
        all_quotes = results.get("all_quotes", [])

        print(f"Total quotes extracted: {len(all_quotes)}")
        return all_quotes

    except Exception as e:
        print(f"Error processing transcripts: {e}")
        return []


def run_streamlined_analysis():
    """Run the streamlined quote analysis."""
    print("FlexXray Streamlined Quote Analysis")
    print("===================================")

    # Load quotes
    quotes = load_existing_quotes()
    if not quotes:
        print("No quotes found. Exiting.")
        return

    # Initialize streamlined analyzer
    analyzer = StreamlinedQuoteAnalysis()

    # Generate company summary
    print("\nStarting streamlined analysis...")
    summary_results = analyzer.generate_company_summary(quotes)

    if not summary_results:
        print("No summary results generated. Exiting.")
        return

    # Save results
    output_file = analyzer.save_summary(summary_results)

    print(f"\nAnalysis complete!")
    print(f"Results saved to: {output_file}")

    # Display summary
    print("\n" + "=" * 50)
    print("SUMMARY OVERVIEW")
    print("=" * 50)

    for category, results in summary_results.items():
        print(f"\n{category.replace('_', ' ').title()}:")
        for result in results:
            question = result["question"]
            quote_count = len(result["selected_quotes"])
            avg_score = (
                sum(result["final_scores"]) / len(result["final_scores"])
                if result["final_scores"]
                else 0
            )

            print(
                f"  • {question[:60]}... ({quote_count} quotes, avg score: {avg_score:.1f})"
            )


if __name__ == "__main__":
    run_streamlined_analysis()
