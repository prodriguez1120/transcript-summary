#!/usr/bin/env python3
"""
Streamlined Quote Analysis Tool for FlexXray Transcripts

This module implements a sophisticated quote analysis system that:
1. Uses vector database for semantic search
2. Implements quote ranking and reranking
3. Streamlines AI calls for better efficiency
4. Focuses on question-answer matching
"""

import os
import json
import re
from openai import OpenAI
from typing import List, Dict, Any, Tuple
from pathlib import Path
import time
from dotenv import load_dotenv
from datetime import datetime
import numpy as np

# Check if openpyxl is available for Excel export
try:
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

# Load environment variables
load_dotenv()


class StreamlinedQuoteAnalysis:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the streamlined quote analysis tool."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it to the constructor."
            )

        self.client = OpenAI(api_key=self.api_key)

        # Define the key questions for analysis
        self.key_questions = {
            "market_leadership": "What evidence shows FlexXray's market leadership and competitive advantage?",
            "value_proposition": "How does FlexXray's value proposition address the risk of insourcing?",
            "local_presence": "How does FlexXray's local presence and footprint drive customer demand?",
            "technology_advantages": "What proprietary technology advantages does FlexXray offer?",
            "rapid_turnaround": "How do FlexXray's rapid turnaround times benefit customers?",
            "limited_tam": "What limits FlexXray's Total Addressable Market (TAM)?",
            "unpredictable_timing": "How does unpredictable event timing impact FlexXray's business?",
        }

        # Question categories for organization
        self.question_categories = {
            "key_takeaways": [
                "market_leadership",
                "value_proposition",
                "local_presence",
            ],
            "strengths": ["technology_advantages", "rapid_turnaround"],
            "weaknesses": ["limited_tam", "unpredictable_timing"],
        }

    def get_expert_quotes_only(
        self, quotes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Filter quotes to include only expert quotes, excluding interviewer questions."""
        expert_quotes = []

        for quote in quotes:
            # Handle both direct format and vector database format
            speaker_role = quote.get("speaker_role")
            if not speaker_role and "metadata" in quote:
                speaker_role = quote.get("metadata", {}).get("speaker_role")
            
            if not speaker_role or speaker_role != "expert":
                continue

            text = quote.get("text", "").strip()

            # Filter out quotes that are clearly interviewer questions or addressing
            if any(
                pattern in text.lower()
                for pattern in [
                    "randy, as you think about",
                    "randy, what do you think",
                    "randy, can you explain",
                    "randy, how do you",
                    "randy, tell me about",
                    "randy, describe",
                    "randy, walk me through",
                    "randy, help me understand",
                    "randy, i want to understand",
                    "randy, i'm curious about",
                    "randy, i'd like to know",
                    "randy, can you walk me",
                    "randy, what is your",
                    "randy, what are your",
                    "randy, how would you",
                    "randy, what would you",
                    "randy, do you think",
                    "randy, do you see",
                    "randy, do you believe",
                    "randy, do you feel",
                ]
            ):
                continue

            # Filter out quotes that start with addressing someone
            if re.match(
                r"^[A-Z][a-z]+,?\s+(?:what|how|why|when|where|can you|could you|would you|do you|tell me|walk me|help me|i want|i\'m curious|i\'d like)",
                text.lower(),
            ):
                continue

            expert_quotes.append(quote)

        return expert_quotes

    def rank_quotes_for_question(
        self, quotes: List[Dict[str, Any]], question: str, top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Rank quotes for relevance to a specific question using OpenAI."""
        if not quotes:
            return []

        # Create ranking prompt
        ranking_prompt = f"""Score the relevance of the following quotes to this question: "{question}"

For each quote, provide a relevance score from 0-10 where:
- 10 = Highly relevant, directly answers the question
- 7-9 = Relevant, provides useful context or partial answer
- 4-6 = Somewhat relevant, may contain related information
- 1-3 = Minimally relevant, only tangentially related
- 0 = Not relevant, unrelated to the question

Quotes to score:
{chr(10).join([f"{i+1}. {quote.get('text', '')}" for i, quote in enumerate(quotes)])}

Please respond with a JSON array of objects:
[
  {{
    "quote_index": <0-based index>,
    "relevance_score": <0-10>,
    "relevance_explanation": "<brief explanation of score>"
  }}
]"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert analyst scoring text relevance. Provide only valid JSON.",
                    },
                    {"role": "user", "content": ranking_prompt},
                ],
                temperature=0.1,
                max_tokens=1000,
            )

            # Parse response with proper error handling
            content = response.choices[0].message.content
            if not content or not content.strip():
                print("Warning: Empty response from OpenAI API")
                return quotes[:top_k]
            
            try:
                scores = json.loads(content)
            except json.JSONDecodeError as json_error:
                print(f"JSON parsing error: {json_error}")
                print(f"Raw response content: {content[:200]}...")
                # Fallback: return quotes in original order
                return quotes[:top_k]

            # Validate scores structure
            if not isinstance(scores, list):
                print(f"Warning: Expected list, got {type(scores)}")
                return quotes[:top_k]

            # Sort quotes by score
            ranked_quotes = []
            for score_data in scores:
                if not isinstance(score_data, dict):
                    print(f"Warning: Expected dict in scores, got {type(score_data)}")
                    continue
                    
                quote_index = score_data.get("quote_index", 0)
                relevance_score = score_data.get("relevance_score", 0)

                if quote_index < len(quotes):
                    quote = quotes[quote_index].copy()
                    quote["relevance_score"] = relevance_score
                    quote["relevance_explanation"] = score_data.get(
                        "relevance_explanation", ""
                    )
                    ranked_quotes.append(quote)

            # Sort by score (highest first) and return top_k
            ranked_quotes.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
            return ranked_quotes[:top_k]

        except Exception as e:
            print(f"Error ranking quotes: {e}")
            # Fallback: return quotes in original order
            return quotes[:top_k]

    def rerank_top_quotes(
        self, quotes: List[Dict[str, Any]], question: str, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Rerank the top quotes for more precise relevance scoring."""
        if len(quotes) <= top_k:
            return quotes

        # Take top quotes and rerank them
        top_quotes = quotes[:top_k]

        # Create more detailed ranking prompt for reranking
        rerank_prompt = f"""Carefully analyze and rerank these top quotes for relevance to: "{question}"

Consider:
- Does the quote directly answer the question?
- Is the information specific and actionable?
- Does it provide concrete evidence or examples?
- Is it from a credible source/context?

Quotes to rerank:
{chr(10).join([f"{i+1}. {quote.get('text', '')}" for i, quote in enumerate(top_quotes)])}

Provide a JSON array with reranked indices (0-based) and detailed scoring:
[
  {{
    "quote_index": <0-based index>,
    "final_score": <0-10>,
    "reasoning": "<detailed explanation of why this quote is most relevant>"
  }}
]"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert analyst doing final quote selection. Provide only valid JSON.",
                    },
                    {"role": "user", "content": rerank_prompt},
                ],
                temperature=0.1,
                max_tokens=1500,
            )

            # Parse response with proper error handling
            content = response.choices[0].message.content
            if not content or not content.strip():
                print("Warning: Empty response from OpenAI API during reranking")
                return quotes[:top_k]
            
            try:
                rerank_scores = json.loads(content)
            except json.JSONDecodeError as json_error:
                print(f"JSON parsing error during reranking: {json_error}")
                print(f"Raw response content: {content[:200]}...")
                # Fallback: return quotes in original order
                return quotes[:top_k]

            # Validate rerank_scores structure
            if not isinstance(rerank_scores, list):
                print(f"Warning: Expected list in reranking, got {type(rerank_scores)}")
                return quotes[:top_k]

            # Create final reranked list
            reranked_quotes = []
            for score_data in rerank_scores:
                if not isinstance(score_data, dict):
                    print(f"Warning: Expected dict in rerank scores, got {type(score_data)}")
                    continue
                    
                quote_index = score_data.get("quote_index", 0)
                final_score = score_data.get("final_score", 0)

                if quote_index < len(top_quotes):
                    quote = top_quotes[quote_index].copy()
                    quote["final_score"] = final_score
                    quote["final_reasoning"] = score_data.get("reasoning", "")
                    reranked_quotes.append(quote)

            # Sort by final score and return
            reranked_quotes.sort(key=lambda x: x.get("final_score", 0), reverse=True)
            return reranked_quotes

        except Exception as e:
            print(f"Error reranking quotes: {e}")
            return quotes[:top_k]

    def generate_company_summary(self, quotes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate company summary using streamlined quote analysis."""
        if not quotes:
            return {}

        print("Generating company summary using streamlined analysis...")

        # Filter to expert quotes only
        expert_quotes = self.get_expert_quotes_only(quotes)
        if not expert_quotes:
            print("No expert quotes found after filtering")
            return {}

        # Analyze each question category
        summary_results = {}

        for category, question_keys in self.question_categories.items():
            print(f"\nAnalyzing {category}...")
            category_results = []

            for question_key in question_keys:
                question = self.key_questions[question_key]
                print(f"  Processing: {question[:60]}...")

                # Rank quotes for this question
                ranked_quotes = self.rank_quotes_for_question(
                    expert_quotes, question, top_k=15
                )

                # Rerank top quotes for precision
                final_quotes = self.rerank_top_quotes(ranked_quotes, question, top_k=3)

                # Select best quotes (1-2 per question)
                selected_quotes = (
                    final_quotes[:2] if len(final_quotes) >= 2 else final_quotes
                )

                category_results.append(
                    {
                        "question": question,
                        "question_key": question_key,
                        "selected_quotes": selected_quotes,
                        "total_candidates": len(ranked_quotes),
                        "final_scores": [
                            q.get("final_score", 0) for q in selected_quotes
                        ],
                    }
                )

            summary_results[category] = category_results

        return summary_results

    def format_summary_output(self, summary_results: Dict[str, Any]) -> str:
        """Format the summary results into the required output format."""
        output = "FLEXXRAY COMPANY SUMMARY PAGE\n"
        output += "========================================\n\n"

        # Format each category
        for category, results in summary_results.items():
            category_title = category.replace("_", " ").title()
            output += f"{category_title}\n"
            output += "-" * 20 + "\n"

            for i, result in enumerate(results, 1):
                question = result["question"]
                quotes = result["selected_quotes"]

                output += f"{i}. {question}\n"
                output += "   Supporting quotes:\n"

                for quote in quotes:
                    # Extract speaker and transcript info from metadata (vector DB format)
                    metadata = quote.get("metadata", {})
                    speaker_info = metadata.get("speaker_role", metadata.get("speaker", quote.get("speaker_info", "Unknown Speaker")))
                    transcript_name = metadata.get("transcript_name", quote.get("transcript_name", "Unknown Transcript"))
                    quote_text = quote.get("text", "")

                    output += f'     - "{quote_text}" - {speaker_info} from {transcript_name}\n'

                output += "\n"

            output += "\n"

        return output

    def save_summary(
        self, summary_results: Dict[str, Any], output_dir: str = "Outputs"
    ) -> str:
        """Save the summary results to files."""
        # Validate summary_results
        if not summary_results:
            print("Warning: No summary results to save")
            return ""
        
        if not isinstance(summary_results, dict):
            print(f"Warning: Expected dict for summary_results, got {type(summary_results)}")
            return ""
        
        # Check if summary_results has any content
        if not any(summary_results.values()):
            print("Warning: Summary results are empty")
            return ""
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save formatted output
        formatted_output = self.format_summary_output(summary_results)
        output_file = os.path.join(
            output_dir, f"FlexXray_Streamlined_Summary_{timestamp}.txt"
        )

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(formatted_output)

        # Save raw results as JSON
        json_file = os.path.join(
            output_dir, f"FlexXray_Streamlined_Summary_{timestamp}.json"
        )
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(summary_results, f, indent=2, ensure_ascii=False)

        # Export to Excel
        excel_file = self.export_to_excel(summary_results, output_dir)

        # Log exact paths with absolute paths for clarity
        abs_output_file = os.path.abspath(output_file)
        abs_json_file = os.path.abspath(json_file)
        
        print(f"Summary saved to: {abs_output_file}")
        print(f"Raw results saved to: {abs_json_file}")
        if excel_file:
            abs_excel_file = os.path.abspath(excel_file)
            print(f"Excel summary saved to: {abs_excel_file}")
        else:
            print("Excel export was not available or failed")

        return output_file

    def export_to_excel(
        self, summary_results: Dict[str, Any], output_dir: str = "Outputs"
    ) -> str:
        """Export streamlined summary results to Excel file."""
        if not EXCEL_AVAILABLE:
            print("openpyxl not available for Excel export")
            return ""

        # Validate summary_results
        if not summary_results:
            print("Warning: No summary results to export to Excel")
            return ""
        
        if not isinstance(summary_results, dict):
            print(f"Warning: Expected dict for summary_results in Excel export, got {type(summary_results)}")
            return ""

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_file = os.path.join(
            output_dir, f"FlexXray_Streamlined_Summary_{timestamp}.xlsx"
        )

        try:
            # Create workbook and worksheet
            wb = openpyxl.Workbook()
            ws = wb.active
            if ws is None:
                raise Exception("Failed to create worksheet")
            ws.title = "Streamlined Analysis"

            # Define styles
            header_font = Font(bold=True, size=14, color="FFFFFF")
            section_font = Font(bold=True, size=12)
            quote_font = Font(size=10)
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            section_fill = PatternFill(start_color="D9E2F3", end_color="D9E2F3", fill_type="solid")
            border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )

            # Set column widths
            ws.column_dimensions['A'].width = 15
            ws.column_dimensions['B'].width = 80
            ws.column_dimensions['C'].width = 20
            ws.column_dimensions['D'].width = 10

            row = 1

            # Add title
            ws.merge_cells(f'A{row}:D{row}')
            ws[f'A{row}'] = "FlexXray Streamlined Quote Analysis"
            ws[f'A{row}'].font = Font(bold=True, size=16)
            ws[f'A{row}'].alignment = Alignment(horizontal='center')
            ws[f'A{row}'].fill = header_fill
            row += 2

            # Add timestamp
            ws[f'A{row}'] = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            ws[f'A{row}'].font = Font(italic=True)
            row += 2

            # Process each category
            for category, results in summary_results.items():
                # Add category header
                category_title = category.replace("_", " ").title()
                ws.merge_cells(f'A{row}:D{row}')
                ws[f'A{row}'] = category_title
                ws[f'A{row}'].font = section_font
                ws[f'A{row}'].fill = section_fill
                ws[f'A{row}'].alignment = Alignment(horizontal='center')
                row += 1

                # Add column headers
                ws[f'A{row}'] = "Question"
                ws[f'B{row}'] = "Supporting Quotes"
                ws[f'C{row}'] = "Speaker/Transcript"
                ws[f'D{row}'] = "Score"
                
                for col in ['A', 'B', 'C', 'D']:
                    ws[f'{col}{row}'].font = Font(bold=True)
                    ws[f'{col}{row}'].fill = section_fill
                    ws[f'{col}{row}'].border = border
                row += 1

                # Add questions and quotes
                for i, result in enumerate(results, 1):
                    question = result["question"]
                    quotes = result["selected_quotes"]
                    final_scores = result.get("final_scores", [])

                    # Add question
                    ws[f'A{row}'] = f"{i}. {question}"
                    ws[f'A{row}'].font = Font(bold=True)
                    ws[f'A{row}'].alignment = Alignment(wrap_text=True, vertical='top')
                    ws[f'A{row}'].border = border
                    
                    # Add quotes
                    quote_texts = []
                    speaker_infos = []
                    scores = []
                    
                    for j, quote in enumerate(quotes):
                        quote_text = quote.get("text", "")
                        # Extract speaker and transcript info from metadata (vector DB format)
                        metadata = quote.get("metadata", {})
                        speaker_info = metadata.get("speaker_role", metadata.get("speaker", quote.get("speaker_info", "Unknown Speaker")))
                        transcript_name = metadata.get("transcript_name", quote.get("transcript_name", "Unknown Transcript"))
                        score = final_scores[j] if j < len(final_scores) else 0
                        
                        quote_texts.append(f'"{quote_text}"')
                        speaker_infos.append(f"{speaker_info} from {transcript_name}")
                        scores.append(score)

                    ws[f'B{row}'] = "\n\n".join(quote_texts)
                    ws[f'B{row}'].font = quote_font
                    ws[f'B{row}'].alignment = Alignment(wrap_text=True, vertical='top')
                    ws[f'B{row}'].border = border

                    ws[f'C{row}'] = "\n".join(speaker_infos)
                    ws[f'C{row}'].font = quote_font
                    ws[f'C{row}'].alignment = Alignment(wrap_text=True, vertical='top')
                    ws[f'C{row}'].border = border

                    avg_score = sum(scores) / len(scores) if scores else 0
                    ws[f'D{row}'] = f"{avg_score:.1f}"
                    ws[f'D{row}'].font = quote_font
                    ws[f'D{row}'].alignment = Alignment(horizontal='center')
                    ws[f'D{row}'].border = border

                    row += 1

                row += 1  # Add space between categories

            # Add summary statistics
            ws.merge_cells(f'A{row}:D{row}')
            ws[f'A{row}'] = "Summary Statistics"
            ws[f'A{row}'].font = section_font
            ws[f'A{row}'].fill = section_fill
            ws[f'A{row}'].alignment = Alignment(horizontal='center')
            row += 1

            # Calculate and add statistics
            total_questions = sum(len(results) for results in summary_results.values())
            total_quotes = sum(len(result["selected_quotes"]) for results in summary_results.values() for result in results)
            all_scores = [score for results in summary_results.values() for result in results for score in result.get("final_scores", [])]
            avg_score = sum(all_scores) / len(all_scores) if all_scores else 0

            stats = [
                ("Total Questions Analyzed", str(total_questions)),
                ("Total Quotes Selected", str(total_quotes)),
                ("Average Relevance Score", f"{avg_score:.1f}"),
                ("Analysis Categories", str(len(summary_results)))
            ]

            for stat_name, stat_value in stats:
                ws[f'A{row}'] = stat_name
                ws[f'B{row}'] = stat_value
                ws[f'A{row}'].font = Font(bold=True)
                ws[f'B{row}'].font = Font(bold=True)
                ws[f'A{row}'].border = border
                ws[f'B{row}'].border = border
                row += 1

            # Save the workbook
            wb.save(excel_file)
            print(f"Excel summary saved to: {excel_file}")
            return excel_file

        except Exception as e:
            print(f"Error exporting to Excel: {e}")
            return ""


def main():
    """Main function to run the streamlined analysis."""
    # Initialize the tool
    analyzer = StreamlinedQuoteAnalysis()

    # Load quotes (you'll need to implement this based on your existing quote extraction)
    # For now, this is a placeholder
    print("Streamlined Quote Analysis Tool")
    print("===============================")
    print(
        "Note: This tool requires quotes to be loaded from your existing extraction system"
    )
    print("Please integrate this with your quote extraction pipeline")


if __name__ == "__main__":
    main()
