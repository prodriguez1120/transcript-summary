"""
Configuration file for FlexXray Transcript Summarizer
Centralizes output directory and other settings
"""

import os
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent

# Output directory configuration
OUTPUT_DIR = PROJECT_ROOT / "Outputs"

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)

# File naming patterns
def get_output_path(filename: str) -> Path:
    """Generate output file path in the Outputs directory."""
    return OUTPUT_DIR / filename

# Common output filenames
OUTPUT_FILES = {
    "quote_analysis_json": "FlexXray_quote_analysis.json",
    "quote_analysis_txt": "FlexXray_quote_analysis.txt", 

    "transcript_analysis_json": "FlexXray_transcript_analysis_results.json",
    "transcript_analysis_txt": "FlexXray_transcript_analysis_results.txt",
    "transcript_analysis_docx": "FlexXray_transcript_analysis_results.docx",
    "transcript_analysis_with_chunks_txt": "FlexXray_transcript_analysis_with_chunks.txt",
    "transcript_analysis_with_chunks_docx": "FlexXray_transcript_analysis_with_chunks.docx",
    "transcript_analysis_summary_txt": "FlexXray_transcript_analysis_summary.txt",
    "transcript_analysis_summary_docx": "FlexXray_transcript_analysis_summary.docx",
    "concept_attribution_analysis_txt": "FlexXray_concept_attribution_analysis.txt",
    "concept_attribution_analysis_docx": "FlexXray_concept_attribution_analysis.docx",
    "company_summary_page_txt": "FlexXray_Company_Summary_Page.txt",
    "company_summary_page_xlsx": "FlexXray_Company_Summary_Page.xlsx"
}

# Get output paths
def get_output_paths():
    """Get all output file paths."""
    return {key: get_output_path(filename) for key, filename in OUTPUT_FILES.items()}

# Print configuration info
if __name__ == "__main__":
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Output Directory: {OUTPUT_DIR}")
    print(f"Output Directory exists: {OUTPUT_DIR.exists()}")
    print("\nOutput file paths:")
    for key, path in get_output_paths().items():
        print(f"  {key}: {path}")
