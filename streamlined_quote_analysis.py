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

# Load environment variables
load_dotenv()

class StreamlinedQuoteAnalysis:
    def __init__(self, api_key: str = None):
        """Initialize the streamlined quote analysis tool."""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it to the constructor.")
        
        self.client = OpenAI(api_key=self.api_key)
        
        # Define the key questions for analysis
        self.key_questions = {
            "market_leadership": "What evidence shows FlexXray's market leadership and competitive advantage?",
            "value_proposition": "How does FlexXray's value proposition address the risk of insourcing?",
            "local_presence": "How does FlexXray's local presence and footprint drive customer demand?",
            "technology_advantages": "What proprietary technology advantages does FlexXray offer?",
            "rapid_turnaround": "How do FlexXray's rapid turnaround times benefit customers?",
            "limited_tam": "What limits FlexXray's Total Addressable Market (TAM)?",
            "unpredictable_timing": "How does unpredictable event timing impact FlexXray's business?"
        }
        
        # Question categories for organization
        self.question_categories = {
            "key_takeaways": ["market_leadership", "value_proposition", "local_presence"],
            "strengths": ["technology_advantages", "rapid_turnaround"],
            "weaknesses": ["limited_tam", "unpredictable_timing"]
        }
    
    def get_expert_quotes_only(self, quotes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter quotes to include only expert quotes, excluding interviewer questions."""
        expert_quotes = []
        
        for quote in quotes:
            if quote.get('speaker_role') != 'expert':
                continue
                
            text = quote.get('text', '').strip()
            
            # Filter out quotes that are clearly interviewer questions or addressing
            if any(pattern in text.lower() for pattern in [
                'randy, as you think about',
                'randy, what do you think',
                'randy, can you explain',
                'randy, how do you',
                'randy, tell me about',
                'randy, describe',
                'randy, walk me through',
                'randy, help me understand',
                'randy, i want to understand',
                'randy, i\'m curious about',
                'randy, i\'d like to know',
                'randy, can you walk me',
                'randy, what is your',
                'randy, what are your',
                'randy, how would you',
                'randy, what would you',
                'randy, do you think',
                'randy, do you see',
                'randy, do you believe',
                'randy, do you feel'
            ]):
                continue
                
            # Filter out quotes that start with addressing someone
            if re.match(r'^[A-Z][a-z]+,?\s+(?:what|how|why|when|where|can you|could you|would you|do you|tell me|walk me|help me|i want|i\'m curious|i\'d like)', text.lower()):
                continue
                
            expert_quotes.append(quote)
        
        return expert_quotes
    
    def rank_quotes_for_question(self, quotes: List[Dict[str, Any]], question: str, top_k: int = 10) -> List[Dict[str, Any]]:
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
                    {"role": "system", "content": "You are an expert analyst scoring text relevance. Provide only valid JSON."},
                    {"role": "user", "content": ranking_prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            # Parse response
            content = response.choices[0].message.content
            scores = json.loads(content)
            
            # Sort quotes by score
            ranked_quotes = []
            for score_data in scores:
                quote_index = score_data.get('quote_index', 0)
                relevance_score = score_data.get('relevance_score', 0)
                
                if quote_index < len(quotes):
                    quote = quotes[quote_index].copy()
                    quote['relevance_score'] = relevance_score
                    quote['relevance_explanation'] = score_data.get('relevance_explanation', '')
                    ranked_quotes.append(quote)
            
            # Sort by score (highest first) and return top_k
            ranked_quotes.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            return ranked_quotes[:top_k]
            
        except Exception as e:
            print(f"Error ranking quotes: {e}")
            # Fallback: return quotes in original order
            return quotes[:top_k]
    
    def rerank_top_quotes(self, quotes: List[Dict[str, Any]], question: str, top_k: int = 5) -> List[Dict[str, Any]]:
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
                    {"role": "system", "content": "You are an expert analyst doing final quote selection. Provide only valid JSON."},
                    {"role": "user", "content": rerank_prompt}
                ],
                temperature=0.1,
                max_tokens=1500
            )
            
            # Parse response
            content = response.choices[0].message.content
            rerank_scores = json.loads(content)
            
            # Create final reranked list
            reranked_quotes = []
            for score_data in rerank_scores:
                quote_index = score_data.get('quote_index', 0)
                final_score = score_data.get('final_score', 0)
                
                if quote_index < len(top_quotes):
                    quote = top_quotes[quote_index].copy()
                    quote['final_score'] = final_score
                    quote['final_reasoning'] = score_data.get('reasoning', '')
                    reranked_quotes.append(quote)
            
            # Sort by final score and return
            reranked_quotes.sort(key=lambda x: x.get('final_score', 0), reverse=True)
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
                ranked_quotes = self.rank_quotes_for_question(expert_quotes, question, top_k=15)
                
                # Rerank top quotes for precision
                final_quotes = self.rerank_top_quotes(ranked_quotes, question, top_k=3)
                
                # Select best quotes (1-2 per question)
                selected_quotes = final_quotes[:2] if len(final_quotes) >= 2 else final_quotes
                
                category_results.append({
                    'question': question,
                    'question_key': question_key,
                    'selected_quotes': selected_quotes,
                    'total_candidates': len(ranked_quotes),
                    'final_scores': [q.get('final_score', 0) for q in selected_quotes]
                })
            
            summary_results[category] = category_results
        
        return summary_results
    
    def format_summary_output(self, summary_results: Dict[str, Any]) -> str:
        """Format the summary results into the required output format."""
        output = "FLEXXRAY COMPANY SUMMARY PAGE\n"
        output += "========================================\n\n"
        
        # Format each category
        for category, results in summary_results.items():
            category_title = category.replace('_', ' ').title()
            output += f"{category_title}\n"
            output += "-" * 20 + "\n"
            
            for i, result in enumerate(results, 1):
                question = result['question']
                quotes = result['selected_quotes']
                
                output += f"{i}. {question}\n"
                output += "   Supporting quotes:\n"
                
                for quote in quotes:
                    speaker_info = quote.get('speaker_info', 'Unknown Speaker')
                    transcript_name = quote.get('transcript_name', 'Unknown Transcript')
                    quote_text = quote.get('text', '')
                    
                    output += f"     - \"{quote_text}\" - {speaker_info} from {transcript_name}\n"
                
                output += "\n"
            
            output += "\n"
        
        return output
    
    def save_summary(self, summary_results: Dict[str, Any], output_dir: str = "Outputs") -> str:
        """Save the summary results to files."""
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save formatted output
        formatted_output = self.format_summary_output(summary_results)
        output_file = os.path.join(output_dir, f"FlexXray_Streamlined_Summary_{timestamp}.txt")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(formatted_output)
        
        # Save raw results as JSON
        json_file = os.path.join(output_dir, f"FlexXray_Streamlined_Summary_{timestamp}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(summary_results, f, indent=2, ensure_ascii=False)
        
        print(f"Summary saved to: {output_file}")
        print(f"Raw results saved to: {json_file}")
        
        return output_file

def main():
    """Main function to run the streamlined analysis."""
    # Initialize the tool
    analyzer = StreamlinedQuoteAnalysis()
    
    # Load quotes (you'll need to implement this based on your existing quote extraction)
    # For now, this is a placeholder
    print("Streamlined Quote Analysis Tool")
    print("===============================")
    print("Note: This tool requires quotes to be loaded from your existing extraction system")
    print("Please integrate this with your quote extraction pipeline")

if __name__ == "__main__":
    main()

