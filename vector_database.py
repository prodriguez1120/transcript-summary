#!/usr/bin/env python3
"""
Vector Database Module for FlexXray Transcripts

This module handles ChromaDB operations and semantic search functionality
for the quote analysis tool.
"""

import os
import hashlib
from typing import List, Dict, Any, Optional
import time
import logging

# Custom exception classes for better error handling
class VectorDatabaseError(Exception):
    """Base exception for vector database operations."""
    pass

class ChromaDBConnectionError(VectorDatabaseError):
    """Raised when ChromaDB connection fails."""
    pass

class ChromaDBInitializationError(VectorDatabaseError):
    """Raised when ChromaDB initialization fails."""
    pass

class QuoteStorageError(VectorDatabaseError):
    """Raised when quote storage operations fail."""
    pass

class SearchError(VectorDatabaseError):
    """Raised when search operations fail."""
    pass

class DataValidationError(VectorDatabaseError):
    """Raised when data validation fails."""
    pass

# Check if ChromaDB is available
try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

class VectorDatabaseManager:
    def __init__(self, chroma_persist_directory: str = "./chroma_db"):
        """Initialize the vector database manager."""
        self.chroma_persist_directory = chroma_persist_directory
        self.chroma_client = None
        self.collection = None
        self.quotes_collection = None
        
        # Set up logger
        self.logger = logging.getLogger(__name__)
        
        if CHROMA_AVAILABLE:
            self._initialize_chroma()
        else:
            self.logger.warning("ChromaDB not available. Vector database operations will be limited.")

    def _initialize_chroma(self):
        """Initialize ChromaDB client and collections."""
        try:
            self.logger.info(f"Initializing ChromaDB at {self.chroma_persist_directory}")
            self.chroma_client = chromadb.PersistentClient(path=self.chroma_persist_directory)
            
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
            
            self.logger.info(f"ChromaDB initialized successfully at {self.chroma_persist_directory}")
            quote_count = self.quotes_collection.count()
            self.logger.info(f"Quotes collection has {quote_count} existing quotes")
            
        except ConnectionError as e:
            error_msg = f"ChromaDB connection failed: {e}"
            self.logger.error(error_msg)
            self.chroma_client = None
            self.collection = None
            self.quotes_collection = None
            raise ChromaDBConnectionError(error_msg) from e
        except (ValueError, TypeError) as e:
            error_msg = f"ChromaDB configuration error: {e}"
            self.logger.error(error_msg)
            self.chroma_client = None
            self.collection = None
            self.quotes_collection = None
            raise ChromaDBInitializationError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected ChromaDB initialization error: {e}"
            self.logger.error(error_msg)
            self.chroma_client = None
            self.collection = None
            self.quotes_collection = None
            raise ChromaDBInitializationError(error_msg) from e

    def store_quotes_in_vector_db(self, quotes: List[Dict[str, Any]], batch_size: int = 100) -> bool:
        """Store quotes in the vector database with enhanced metadata."""
        if not self.quotes_collection:
            error_msg = "ChromaDB not available for quote storage"
            self.logger.warning(error_msg)
            raise QuoteStorageError(error_msg)
        
        if not quotes:
            self.logger.info("No quotes to store")
            return True
        
        # Validate input data
        if not isinstance(quotes, list):
            error_msg = f"Expected list of quotes, got {type(quotes)}"
            self.logger.error(error_msg)
            raise DataValidationError(error_msg)
        
        if batch_size <= 0:
            error_msg = f"Batch size must be positive, got {batch_size}"
            self.logger.error(error_msg)
            raise DataValidationError(error_msg)
        
        try:
            self.logger.info(f"Starting to store {len(quotes)} quotes with batch size {batch_size}")
            start_time = time.time()
            
            # Process quotes in batches
            for i in range(0, len(quotes), batch_size):
                batch = quotes[i:i + batch_size]
                batch_start_time = time.time()
                
                # Prepare batch data
                ids = []
                documents = []
                metadatas = []
                
                for quote in batch:
                    # Validate quote structure
                    if not isinstance(quote, dict):
                        error_msg = f"Expected quote to be dict, got {type(quote)}"
                        self.logger.error(error_msg)
                        raise DataValidationError(error_msg)
                    
                    if 'text' not in quote:
                        error_msg = "Quote missing required 'text' field"
                        self.logger.error(error_msg)
                        raise DataValidationError(error_msg)
                    
                    # Generate unique ID for the quote
                    quote_id = self._generate_quote_id(quote)
                    ids.append(quote_id)
                    
                    # Store the quote text as the document
                    documents.append(quote.get('text', ''))
                    
                    # Enhanced metadata
                    metadata = {
                        'speaker_role': quote.get('speaker_role', 'unknown'),
                        'transcript_name': quote.get('transcript_name', 'Unknown'),
                        'position': quote.get('position', 0),
                        'has_insight': quote.get('has_insight', False),
                        'length': quote.get('metadata', {}).get('length', 0),
                        'word_count': quote.get('metadata', {}).get('word_count', 0),
                        'timestamp': time.time(),
                        'quote_type': 'expert_insight' if quote.get('speaker_role') == 'expert' else 'other'
                    }
                    
                    # Add interviewer context if available
                    if quote.get('interviewer_context'):
                        metadata['has_context'] = True
                        metadata['context_count'] = len(quote['interviewer_context'])
                        metadata['context_questions'] = sum(1 for ctx in quote['interviewer_context'] if ctx.get('is_question'))
                    else:
                        metadata['has_context'] = False
                        metadata['context_count'] = 0
                        metadata['context_questions'] = 0
                    
                    metadatas.append(metadata)
                
                # Add batch to collection
                self.quotes_collection.add(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas
                )
                
                batch_duration = time.time() - batch_start_time
                self.logger.debug(f"Stored batch {i//batch_size + 1} ({len(batch)} quotes) in {batch_duration:.3f}s")
            
            total_duration = time.time() - start_time
            self.logger.info(f"Successfully stored {len(quotes)} quotes in vector database in {total_duration:.3f}s")
            return True
            
        except (ValueError, TypeError) as e:
            error_msg = f"Data validation error storing quotes: {e}"
            self.logger.error(error_msg)
            raise DataValidationError(error_msg) from e
        except ConnectionError as e:
            error_msg = f"ChromaDB connection error: {e}"
            self.logger.error(error_msg)
            raise ChromaDBConnectionError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error storing quotes: {e}"
            self.logger.error(error_msg)
            raise QuoteStorageError(error_msg) from e

    def semantic_search_quotes(self, query: str, n_results: int = 10, filter_metadata: Dict = None) -> List[Dict[str, Any]]:
        """Perform semantic search for quotes using the vector database."""
        if not self.quotes_collection:
            error_msg = "ChromaDB not available for semantic search"
            self.logger.warning(error_msg)
            raise SearchError(error_msg)
        
        # Validate input parameters
        if not isinstance(query, str) or not query.strip():
            error_msg = "Search query must be a non-empty string"
            self.logger.error(error_msg)
            raise DataValidationError(error_msg)
        
        if not isinstance(n_results, int) or n_results <= 0:
            error_msg = f"n_results must be a positive integer, got {n_results}"
            self.logger.error(error_msg)
            raise DataValidationError(error_msg)
        
        if filter_metadata is not None and not isinstance(filter_metadata, dict):
            error_msg = f"filter_metadata must be a dict or None, got {type(filter_metadata)}"
            self.logger.error(error_msg)
            raise DataValidationError(error_msg)
        
        try:
            self.logger.debug(f"Performing semantic search for query: '{query}' with {n_results} results")
            start_time = time.time()
            
            # Prepare search parameters
            search_params = {
                'query_texts': [query],
                'n_results': n_results
            }
            
            # Add metadata filtering if specified
            if filter_metadata:
                search_params['where'] = filter_metadata
                self.logger.debug(f"Applied metadata filter: {filter_metadata}")
            
            # Perform search
            results = self.quotes_collection.query(**search_params)
            
            # Process results
            quotes = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    quote = {
                        'text': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {},
                        'id': results['ids'][0][i] if results['ids'] and results['ids'][0] else None,
                        'distance': results['distances'][0][i] if results['distances'] and results['distances'][0] else None
                    }
                    quotes.append(quote)
            
            search_duration = time.time() - start_time
            self.logger.debug(f"Semantic search completed in {search_duration:.3f}s, found {len(quotes)} results")
            return quotes
            
        except (ValueError, TypeError) as e:
            error_msg = f"Data validation error in semantic search: {e}"
            self.logger.error(error_msg)
            raise DataValidationError(error_msg) from e
        except ConnectionError as e:
            error_msg = f"ChromaDB connection error in semantic search: {e}"
            self.logger.error(error_msg)
            raise ChromaDBConnectionError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error in semantic search: {e}"
            self.logger.error(error_msg)
            raise SearchError(error_msg) from e

    def search_quotes_with_speaker_filter(self, query: str, speaker_role: str = "expert", n_results: int = 10) -> List[Dict[str, Any]]:
        """Search for quotes with speaker role filtering."""
        self.logger.debug(f"Searching for quotes with speaker role filter: {speaker_role}")
        filter_metadata = {'speaker_role': speaker_role}
        return self.semantic_search_quotes(query, n_results, filter_metadata)

    def clear_vector_database(self) -> bool:
        """Clear all data from the vector database."""
        if not self.quotes_collection:
            error_msg = "ChromaDB not available for clearing"
            self.logger.warning(error_msg)
            raise QuoteStorageError(error_msg)
        
        try:
            self.logger.info("Clearing vector database")
            # Delete the quotes collection
            self.chroma_client.delete_collection(name="flexray_quotes")
            
            # Recreate the collection
            self.quotes_collection = self.chroma_client.get_or_create_collection(
                name="flexray_quotes",
                metadata={
                    "hnsw:space": "cosine",
                    "description": "FlexXray interview quotes with sentiment and perspective metadata"
                }
            )
            
            self.logger.info("Vector database cleared successfully")
            return True
            
        except Exception as e:
            error_msg = f"Error clearing vector database: {e}"
            self.logger.error(error_msg)
            raise QuoteStorageError(error_msg) from e

    def get_vector_database_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database."""
        if not self.quotes_collection:
            return {
                'available': False,
                'total_quotes': 0,
                'collections': []
            }
        
        try:
            total_quotes = self.quotes_collection.count()
            collections = [col.name for col in self.chroma_client.list_collections()]
            
            stats = {
                'available': True,
                'total_quotes': total_quotes,
                'collections': collections
            }
            
            self.logger.debug(f"Database stats: {stats}")
            return stats
            
        except Exception as e:
            error_msg = f"Error getting database stats: {e}"
            self.logger.error(error_msg)
            return {
                'available': False,
                'total_quotes': 0,
                'collections': []
            }

    def _generate_quote_id(self, quote: Dict[str, Any]) -> str:
        """Generate a unique ID for a quote."""
        # Create a hash from transcript name, position, and first 50 characters of text
        text_preview = quote.get('text', '')[:50]
        hash_input = f"{quote.get('transcript_name', '')}_{quote.get('position', 0)}_{text_preview}"
        return hashlib.md5(hash_input.encode()).hexdigest()

    def get_quotes_by_perspective(self, perspective_key: str, perspective_data: dict, n_results: int = 20) -> List[Dict[str, Any]]:
        """Get quotes relevant to a specific perspective."""
        if not perspective_data or 'keywords' not in perspective_data:
            self.logger.warning(f"No keywords found for perspective: {perspective_key}")
            return []
        
        # Use the first keyword for search
        search_term = perspective_data['keywords'][0] if perspective_data['keywords'] else perspective_key
        return self.semantic_search_quotes(search_term, n_results)

    def categorize_quotes_by_sentiment(self, quotes: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize quotes by sentiment."""
        if not quotes:
            return {}
        
        categorized = {
            'positive': [],
            'negative': [],
            'neutral': []
        }
        
        for quote in quotes:
            # Simple sentiment categorization based on keywords
            text_lower = quote.get('text', '').lower()
            if any(word in text_lower for word in ['excellent', 'great', 'good', 'amazing', 'outstanding']):
                categorized['positive'].append(quote)
            elif any(word in text_lower for word in ['poor', 'bad', 'terrible', 'awful', 'horrible']):
                categorized['negative'].append(quote)
            else:
                categorized['neutral'].append(quote)
        
        self.logger.debug(f"Categorized {len(quotes)} quotes: {len(categorized['positive'])} positive, {len(categorized['negative'])} negative, {len(categorized['neutral'])} neutral")
        return categorized
