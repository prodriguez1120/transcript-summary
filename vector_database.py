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
        
        if CHROMA_AVAILABLE:
            self._initialize_chroma()
        else:
            print("Warning: ChromaDB not available. Vector database operations will be limited.")

    def _initialize_chroma(self):
        """Initialize ChromaDB client and collections."""
        try:
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
            
            print(f"ChromaDB initialized at {self.chroma_persist_directory}")
            print(f"Quotes collection has {self.quotes_collection.count()} existing quotes")
            
        except Exception as e:
            print(f"Warning: ChromaDB initialization failed: {e}")
            self.chroma_client = None
            self.collection = None
            self.quotes_collection = None

    def store_quotes_in_vector_db(self, quotes: List[Dict[str, Any]], batch_size: int = 100) -> bool:
        """Store quotes in the vector database with enhanced metadata."""
        if not self.quotes_collection:
            print("ChromaDB not available for quote storage")
            return False
        
        if not quotes:
            print("No quotes to store")
            return True
        
        try:
            # Process quotes in batches
            for i in range(0, len(quotes), batch_size):
                batch = quotes[i:i + batch_size]
                
                # Prepare batch data
                ids = []
                documents = []
                metadatas = []
                
                for quote in batch:
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
                
                print(f"Stored batch {i//batch_size + 1} ({len(batch)} quotes)")
            
            print(f"Successfully stored {len(quotes)} quotes in vector database")
            return True
            
        except Exception as e:
            print(f"Error storing quotes in vector database: {e}")
            return False

    def semantic_search_quotes(self, query: str, n_results: int = 10, filter_metadata: Dict = None) -> List[Dict[str, Any]]:
        """Perform semantic search for quotes using the vector database."""
        if not self.quotes_collection:
            print("ChromaDB not available for semantic search")
            return []
        
        try:
            # Prepare search parameters
            search_params = {
                'query_texts': [query],
                'n_results': n_results
            }
            
            # Add metadata filtering if specified
            if filter_metadata:
                search_params['where'] = filter_metadata
            
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
            
            return quotes
            
        except Exception as e:
            print(f"Error performing semantic search: {e}")
            return []

    def search_quotes_with_speaker_filter(self, query: str, speaker_role: str = "expert", n_results: int = 10) -> List[Dict[str, Any]]:
        """Search for quotes with speaker role filtering."""
        filter_metadata = {'speaker_role': speaker_role}
        return self.semantic_search_quotes(query, n_results, filter_metadata)

    def clear_vector_database(self) -> bool:
        """Clear all data from the vector database."""
        if not self.quotes_collection:
            print("ChromaDB not available for clearing")
            return False
        
        try:
            # Delete the collection and recreate it
            self.chroma_client.delete_collection(name="flexray_quotes")
            self.quotes_collection = self.chroma_client.create_collection(
                name="flexray_quotes",
                metadata={
                    "hnsw:space": "cosine",
                    "description": "FlexXray interview quotes with sentiment and perspective metadata"
                }
            )
            
            print("Vector database cleared successfully")
            return True
            
        except Exception as e:
            print(f"Error clearing vector database: {e}")
            return False

    def get_vector_database_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database."""
        if not self.quotes_collection:
            return {
                'available': False,
                'total_quotes': 0,
                'collections': []
            }
        
        try:
            # Get basic stats
            total_quotes = self.quotes_collection.count()
            
            # Get collection info
            collections = []
            if self.chroma_client:
                try:
                    collection_list = self.chroma_client.list_collections()
                    collections = [col.name for col in collection_list]
                except:
                    collections = ['flexray_quotes']  # Fallback
            
            # Get metadata distribution if possible
            metadata_stats = {}
            try:
                # Sample some quotes to get metadata distribution
                sample_results = self.quotes_collection.query(
                    query_texts=["sample"],
                    n_results=min(100, total_quotes)
                )
                
                if sample_results['metadatas'] and sample_results['metadatas'][0]:
                    for metadata in sample_results['metadatas'][0]:
                        for key, value in metadata.items():
                            if key not in metadata_stats:
                                metadata_stats[key] = {}
                            
                            if isinstance(value, (str, int, float, bool)):
                                if value not in metadata_stats[key]:
                                    metadata_stats[key][value] = 0
                                metadata_stats[key][value] += 1
            except:
                pass
            
            return {
                'available': True,
                'total_quotes': total_quotes,
                'collections': collections,
                'metadata_distribution': metadata_stats
            }
            
        except Exception as e:
            print(f"Error getting vector database stats: {e}")
            return {
                'available': False,
                'error': str(e),
                'total_quotes': 0,
                'collections': []
            }

    def _generate_quote_id(self, quote: Dict[str, Any]) -> str:
        """Generate a unique ID for a quote based on its content and metadata."""
        # Create a hash from quote text and transcript name
        content = f"{quote.get('text', '')}_{quote.get('transcript_name', '')}_{quote.get('position', 0)}"
        return hashlib.md5(content.encode()).hexdigest()

    def get_quotes_by_perspective(self, perspective_key: str, perspective_data: dict, n_results: int = 20) -> List[Dict[str, Any]]:
        """Get quotes relevant to a specific perspective using semantic search."""
        if not self.quotes_collection:
            return []
        
        # Create search query from perspective focus areas
        focus_areas = perspective_data.get('focus_areas', [])
        if not focus_areas:
            return []
        
        # Combine focus areas into a search query
        search_query = " ".join(focus_areas)
        
        # Search for relevant quotes
        quotes = self.semantic_search_quotes(search_query, n_results)
        
        # Filter to expert quotes only
        expert_quotes = [q for q in quotes if q.get('metadata', {}).get('speaker_role') == 'expert']
        
        return expert_quotes

    def categorize_quotes_by_sentiment(self, quotes: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize quotes by sentiment using semantic search patterns."""
        if not quotes:
            return {'positive': [], 'negative': [], 'neutral': []}
        
        # Define sentiment search patterns
        sentiment_patterns = {
            'positive': [
                'advantage strength benefit opportunity growth success positive good excellent',
                'competitive advantage market leader innovative technology superior quality',
                'customer satisfaction loyalty retention expansion development improvement'
            ],
            'negative': [
                'weakness challenge problem issue risk concern negative bad poor difficult',
                'competition threat market pressure cost increase quality issues',
                'operational challenges staffing problems equipment limitations'
            ],
            'neutral': [
                'business model market position industry trends company operations',
                'service delivery process workflow standard procedure normal operation'
            ]
        }
        
        categorized_quotes = {'positive': [], 'negative': [], 'neutral': []}
        
        for quote in quotes:
            quote_text = quote.get('text', '').lower()
            
            # Score quote against each sentiment category
            sentiment_scores = {}
            for sentiment, patterns in sentiment_patterns.items():
                score = 0
                for pattern in patterns:
                    pattern_words = pattern.split()
                    for word in pattern_words:
                        if word in quote_text:
                            score += 1
                sentiment_scores[sentiment] = score
            
            # Determine dominant sentiment
            if sentiment_scores['positive'] > sentiment_scores['negative'] and sentiment_scores['positive'] > sentiment_scores['neutral']:
                categorized_quotes['positive'].append(quote)
            elif sentiment_scores['negative'] > sentiment_scores['positive'] and sentiment_scores['negative'] > sentiment_scores['neutral']:
                categorized_quotes['negative'].append(quote)
            else:
                categorized_quotes['neutral'].append(quote)
        
        return categorized_quotes
