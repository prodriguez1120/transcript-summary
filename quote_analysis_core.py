#!/usr/bin/env python3
"""
Core Quote Analysis Tool for FlexXray Transcripts

This module contains the main QuoteAnalysisTool class with basic functionality
and initialization. Other modules provide specialized functionality.
"""

import os
import json
import re
from openai import OpenAI
from typing import List, Dict, Any, Tuple
from pathlib import Path
import time
from dotenv import load_dotenv
import hashlib
from datetime import datetime
import logging

# Import configuration
try:
    from config import get_output_path, OUTPUT_FILES
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    print("Warning: config.py not found, using default output directory")

# Check if openpyxl is available for Excel export
try:
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter
    EXCEL_AVAILABLE = True
    print("openpyxl library is available for Excel export")
except ImportError as e:
    EXCEL_AVAILABLE = False
    print(f"openpyxl library not available: {e}")

# Check if ChromaDB is available
try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
    print("ChromaDB library is available")
except ImportError as e:
    CHROMA_AVAILABLE = False
    print(f"ChromaDB library not available: {e}")

# Load environment variables
load_dotenv()

class QuoteAnalysisTool:
    def __init__(self, api_key: str = None, chroma_persist_directory: str = "./chroma_db"):
        """Initialize the quote analysis tool with OpenAI API key and ChromaDB."""
        # Set up logger
        self.logger = logging.getLogger(__name__)
        
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            self.logger.error("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it to the constructor.")
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it to the constructor.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.chroma_persist_directory = chroma_persist_directory
        
        self.logger.info("Initializing QuoteAnalysisTool")
        
        # Initialize ChromaDB if available
        if CHROMA_AVAILABLE:
            try:
                self.logger.info(f"Initializing ChromaDB at {chroma_persist_directory}")
                self.chroma_client = chromadb.PersistentClient(path=chroma_persist_directory)
                
                # Create collections for different types of data
                self.collection = self.chroma_client.get_or_create_collection(
                    name="transcript_chunks",
                    metadata={"hnsw:space": "cosine"}
                )
                
                # Dedicated collection for quotes with enhanced metadata
                self.quotes_collection = self.chroma_client.get_or_create_collection(
                    name="flexray_quotes",
                    metadata={
                        "hnsw:space": "cosine",
                        "description": "FlexXray interview quotes with sentiment and perspective metadata"
                    }
                )
                
                self.logger.info(f"ChromaDB initialized successfully at {chroma_persist_directory}")
                quote_count = self.quotes_collection.count()
                self.logger.info(f"Quotes collection has {quote_count} existing quotes")
                
            except Exception as e:
                self.logger.error(f"ChromaDB initialization failed: {e}")
                self.chroma_client = None
                self.collection = None
                self.quotes_collection = None
        else:
            self.chroma_client = None
            self.collection = None
            self.quotes_collection = None
            self.logger.warning("ChromaDB not available. Quote analysis will be limited.")
        
        # Quote analysis parameters
        self.max_quotes_per_category = 5
        self.min_quote_length = 20
        self.max_quote_length = 200
        
        self.logger.info("QuoteAnalysisTool initialization completed")

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

    def get_quotes_by_speaker_role(self, quotes: List[Dict[str, Any]], speaker_role: str) -> List[Dict[str, Any]]:
        """Get quotes filtered by speaker role."""
        return [q for q in quotes if q.get('speaker_role') == speaker_role]

    def get_quotes_with_context(self, quotes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get quotes that have interviewer context."""
        return [q for q in quotes if q.get('interviewer_context')]

    def format_quote_with_context(self, quote: Dict[str, Any]) -> str:
        """Format a quote with its interviewer context."""
        if not quote.get('interviewer_context'):
            return quote.get('text', '')
        
        context_parts = []
        for context in quote['interviewer_context']:
            if context.get('is_question'):
                context_parts.append(f"Q: {context['sentence']}")
            else:
                context_parts.append(f"Context: {context['sentence']}")
        
        context_text = " | ".join(context_parts)
        return f"{context_text}\nA: {quote.get('text', '')}"

    def get_speaker_role_statistics(self, quotes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about speaker roles in quotes."""
        if not quotes:
            return {
                'total_quotes': 0,
                'expert_quotes': 0,
                'expert_percentage': 0.0,
                'interviewer_quotes': 0,
                'quotes_with_context': 0,
                'context_percentage': 0.0,
                'average_context_per_quote': 0.0
            }
        
        total_quotes = len(quotes)
        expert_quotes = len([q for q in quotes if q.get('speaker_role') == 'expert'])
        interviewer_quotes = len([q for q in quotes if q.get('speaker_role') == 'interviewer'])
        quotes_with_context = len([q for q in quotes if q.get('interviewer_context')])
        
        # Calculate context statistics
        total_context_sentences = sum(
            len(q.get('interviewer_context', [])) 
            for q in quotes if q.get('interviewer_context')
        )
        
        return {
            'total_quotes': total_quotes,
            'expert_quotes': expert_quotes,
            'expert_percentage': (expert_quotes / total_quotes * 100) if total_quotes > 0 else 0.0,
            'interviewer_quotes': interviewer_quotes,
            'quotes_with_context': quotes_with_context,
            'context_percentage': (quotes_with_context / total_quotes * 100) if total_quotes > 0 else 0.0,
            'average_context_per_quote': (total_context_sentences / quotes_with_context) if quotes_with_context > 0 else 0.0
        }

    def _clean_and_validate_quotes(self, quotes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and validate quotes for analysis."""
        cleaned_quotes = []
        
        for quote in quotes:
            if not isinstance(quote, dict):
                continue
                
            # Ensure required fields exist
            if not quote.get('text') or not quote.get('speaker_role'):
                continue
                
            # Clean text
            cleaned_text = re.sub(r'\s+', ' ', quote['text']).strip()
            if len(cleaned_text) < self.min_quote_length:
                continue
                
            # Create cleaned quote
            cleaned_quote = {
                'text': cleaned_text,
                'speaker_role': quote['speaker_role'],
                'transcript_name': quote.get('transcript_name', 'Unknown'),
                'metadata': quote.get('metadata', {}),
                'interviewer_context': quote.get('interviewer_context', [])
            }
            
            cleaned_quotes.append(cleaned_quote)
        
        return cleaned_quotes

    def _get_diverse_quotes(self, quotes: List[Dict[str, Any]], category: str, n_results: int) -> List[Dict[str, Any]]:
        """Get diverse quotes from a category, avoiding repetition."""
        if not quotes:
            return []
        
        # Sort by length to get variety
        sorted_quotes = sorted(quotes, key=lambda x: len(x.get('text', '')), reverse=True)
        
        # Take quotes from different transcripts if possible
        selected_quotes = []
        used_transcripts = set()
        
        for quote in sorted_quotes:
            if len(selected_quotes) >= n_results:
                break
                
            transcript = quote.get('transcript_name', 'Unknown')
            
            # Prefer quotes from different transcripts
            if transcript not in used_transcripts or len(selected_quotes) < n_results // 2:
                selected_quotes.append(quote)
                used_transcripts.add(transcript)
        
        # If we still need more quotes, add any remaining
        for quote in sorted_quotes:
            if len(selected_quotes) >= n_results:
                break
            if quote not in selected_quotes:
                selected_quotes.append(quote)
        
        return selected_quotes[:n_results]

    def get_quote_ranking_statistics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Get statistics about quote ranking results."""
        if not results or 'perspectives' not in results:
            return {
                'total_perspectives': 0,
                'total_ranked_quotes': 0,
                'ranking_coverage': 0.0,
                'selection_stage_breakdown': {}
            }
        
        perspectives = results['perspectives']
        total_perspectives = len(perspectives)
        total_ranked_quotes = 0
        selection_stage_breakdown = {}
        
        for perspective_key, perspective_data in perspectives.items():
            # Count quotes that have been ranked (either in themes or directly in the perspective)
            if 'themes' in perspective_data:
                for theme in perspective_data['themes']:
                    if 'quotes' in theme:
                        total_ranked_quotes += len(theme['quotes'])
                        
                        # Track selection stages
                        for quote in theme['quotes']:
                            stage = quote.get('selection_stage', 'unknown')
                            selection_stage_breakdown[stage] = selection_stage_breakdown.get(stage, 0) + 1
            
            # Also count quotes that are directly ranked in the perspective (not just in themes)
            if 'ranked_quotes' in perspective_data:
                ranked_quotes = perspective_data['ranked_quotes']
                for quote in ranked_quotes:
                    if quote.get('selection_stage') in ['openai_ranked', 'openai_failed', 'parsing_failed']:
                        total_ranked_quotes += 1
                        stage = quote.get('selection_stage', 'unknown')
                        selection_stage_breakdown[stage] = selection_stage_breakdown.get(stage, 0) + 1
        
        # Calculate ranking coverage
        all_quotes = results.get('all_quotes', [])
        ranking_coverage = (total_ranked_quotes / len(all_quotes) * 100) if all_quotes else 0.0
        
        return {
            'total_perspectives': total_perspectives,
            'total_ranked_quotes': total_ranked_quotes,
            'ranking_coverage': ranking_coverage,
            'selection_stage_breakdown': selection_stage_breakdown
        }
