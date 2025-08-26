#!/usr/bin/env python3
"""
Core Quote Analysis Tool for FlexXray Transcripts

This module contains the main QuoteAnalysisTool class with basic functionality
and initialization. Other modules provide specialized functionality.

IMPORTANT: ChromaDB collection creation is centralized in VectorDatabaseManager
to prevent metadata mismatches and ensure consistent collection configuration.
"""

import os
import json
import re
from openai import OpenAI
from settings import get_openai_api_key
from typing import List, Dict, Any, Tuple, Optional, Union
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

# Import VectorDatabaseManager for centralized ChromaDB operations
try:
    from vector_database import VectorDatabaseManager
    VECTOR_DB_AVAILABLE = True
    print("VectorDatabaseManager is available")
except ImportError as e:
    VECTOR_DB_AVAILABLE = False
    print(f"VectorDatabaseManager not available: {e}")

# Load environment variables
load_dotenv()

class QuoteAnalysisTool:
    def __init__(self, api_key: Union[str, None] = None, chroma_persist_directory: str = "./chroma_db", min_quote_length: int = 10):
        """Initialize the quote analysis tool with OpenAI API key and ChromaDB."""
        # Set up logger
        self.logger = logging.getLogger(__name__)
        
        self.api_key = api_key or get_openai_api_key()
        if not self.api_key:
            self.logger.error("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it to the constructor.")
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it to the constructor.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.chroma_persist_directory = chroma_persist_directory
        
        self.logger.info("Initializing QuoteAnalysisTool")
        
        # Initialize Vector Database Manager if available
        if VECTOR_DB_AVAILABLE:
            try:
                self.logger.info(f"Initializing Vector Database Manager at {chroma_persist_directory}")
                # At this point, self.api_key is guaranteed to be a string due to validation above
                assert self.api_key is not None, "API key should be set by this point"
                self.vector_db_manager = VectorDatabaseManager(
                    chroma_persist_directory=chroma_persist_directory,
                    openai_api_key=self.api_key  # Pass the API key explicitly
                )
                
                # Get references to collections from the centralized manager
                self.chroma_client = self.vector_db_manager.chroma_client
                self.collection = self.vector_db_manager.collection
                self.quotes_collection = self.vector_db_manager.quotes_collection
                
                self.logger.info(f"Vector Database Manager initialized successfully at {chroma_persist_directory}")
                if self.quotes_collection:
                    quote_count = self.quotes_collection.count()
                    self.logger.info(f"Quotes collection has {quote_count} existing quotes")
                
            except Exception as e:
                self.logger.error(f"Vector Database Manager initialization failed: {e}")
                self.vector_db_manager = None
                self.chroma_client = None
                self.collection = None
                self.quotes_collection = None
        else:
            self.vector_db_manager = None
            self.chroma_client = None
            self.collection = None
            self.quotes_collection = None
            self.logger.warning("Vector Database Manager not available. Quote analysis will be limited.")
        
        # Quote analysis parameters
        self.max_quotes_per_category = 5
        self.min_quote_length = min_quote_length  # Now configurable via constructor
        self.max_quote_length = 200
        
        self.logger.info("QuoteAnalysisTool initialization completed")

    def set_min_quote_length(self, min_length: int) -> None:
        """Set the minimum quote length threshold."""
        if min_length < 1:
            raise ValueError("Minimum quote length must be at least 1 character")
        self.min_quote_length = min_length
        self.logger.info(f"Minimum quote length set to {min_length}")

    def get_min_quote_length(self) -> int:
        """Get the current minimum quote length threshold."""
        return self.min_quote_length

    def get_vector_db_manager(self) -> Optional[VectorDatabaseManager]:
        """Get the vector database manager for advanced operations."""
        return self.vector_db_manager

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
        
        # Use a set to track unique quotes and avoid double counting
        unique_ranked_quotes = set()
        selection_stage_breakdown = {}
        
        for perspective_key, perspective_data in perspectives.items():
            # Count quotes that are directly ranked in the perspective
            if 'ranked_quotes' in perspective_data:
                ranked_quotes = perspective_data['ranked_quotes']
                for quote in ranked_quotes:
                    # Create unique identifier for the quote (using text hash)
                    quote_text = quote.get('text', '')
                    quote_id = hash(quote_text) if quote_text else id(quote)
                    
                    # Only count if we haven't seen this quote before
                    if quote_id not in unique_ranked_quotes:
                        # Count all quotes that went through the ranking pipeline
                        if quote.get('selection_stage') in ['openai_ranked', 'openai_processed', 'openai_failed', 'parsing_failed']:
                            unique_ranked_quotes.add(quote_id)
                            stage = quote.get('selection_stage', 'unknown')
                            selection_stage_breakdown[stage] = selection_stage_breakdown.get(stage, 0) + 1
            
            # Count quotes from themes (only if not already counted in ranked_quotes)
            if 'themes' in perspective_data:
                for theme in perspective_data['themes']:
                    if 'quotes' in theme:
                        for quote in theme['quotes']:
                            # Create unique identifier for the quote
                            quote_text = quote.get('text', '')
                            quote_id = hash(quote_text) if quote_text else id(quote)
                            
                            # Only count if we haven't seen this quote before
                            if quote_id not in unique_ranked_quotes:
                                # Check if quote has selection stage, openai_rank, or relevance_score
                                if (quote.get('selection_stage') or 
                                    quote.get('openai_rank') or 
                                    quote.get('relevance_score')):
                                    unique_ranked_quotes.add(quote_id)
                                    stage = quote.get('selection_stage', 'theme_selected')
                                    selection_stage_breakdown[stage] = selection_stage_breakdown.get(stage, 0) + 1
        
        total_ranked_quotes = len(unique_ranked_quotes)
        
        # Calculate ranking coverage
        all_quotes = results.get('all_quotes', [])
        ranking_coverage = (total_ranked_quotes / len(all_quotes) * 100) if all_quotes else 0.0
        
        return {
            'total_perspectives': total_perspectives,
            'total_ranked_quotes': total_ranked_quotes,
            'ranking_coverage': ranking_coverage,
            'selection_stage_breakdown': selection_stage_breakdown
        }

    def store_quotes_in_vector_db(self, quotes: List[Dict[str, Any]], batch_size: int = 100) -> bool:
        """Store quotes in the vector database using the centralized manager."""
        if not self.vector_db_manager:
            self.logger.warning("Vector Database Manager not available for quote storage")
            return False
        
        try:
            return self.vector_db_manager.store_quotes_in_vector_db(quotes, batch_size)
        except Exception as e:
            self.logger.error(f"Error storing quotes in vector database: {e}")
            return False

    def search_quotes_semantically(self, query: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """Search quotes semantically using the centralized vector database manager."""
        if not self.vector_db_manager:
            self.logger.warning("Vector Database Manager not available for semantic search")
            return []
        
        try:
            return self.vector_db_manager.semantic_search_quotes(query, n_results)
        except Exception as e:
            self.logger.error(f"Error searching quotes semantically: {e}")
            return []
