#!/usr/bin/env python3
"""
Fuzzy Matching Utilities for FlexXray Transcript Analysis

This module provides fuzzy matching capabilities for:
- Topic matching with synonyms and variations
- Speaker role identification with flexible patterns
- Quote relevance scoring with semantic similarity
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from fuzzywuzzy import fuzz, process
from sentence_transformers import SentenceTransformer
import numpy as np
import logging

# Get logger without configuring at module level
logger = logging.getLogger(__name__)

class FuzzyMatcher:
    """Enhanced fuzzy matching for transcript analysis."""
    
    def __init__(self, use_semantic: bool = True, fuzzy_threshold: int = 80, semantic_threshold: float = 0.7):
        """Initialize the fuzzy matcher."""
        self.fuzzy_threshold = fuzzy_threshold
        self.semantic_threshold = semantic_threshold
        self.use_semantic = use_semantic
        
        # Initialize sentence transformer for semantic similarity
        if self.use_semantic:
            try:
                self.semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Semantic model loaded successfully")
            except (ImportError, OSError) as e:
                logger.warning(f"Failed to load semantic model: {e}. Falling back to fuzzy string matching only.")
                self.use_semantic = False
                self.semantic_model = None
            except Exception as e:
                logger.warning(f"Unexpected error loading semantic model: {e}. Falling back to fuzzy string matching only.")
                self.use_semantic = False
                self.semantic_model = None
        else:
            self.semantic_model = None
    
    def fuzzy_topic_match(self, text: str, topic_patterns: List[str], use_semantic: bool = None) -> Tuple[bool, float, str]:
        """
        Match text against topic patterns using fuzzy matching.
        
        Returns:
            Tuple of (is_match, confidence_score, best_matching_pattern)
        """
        # Early return for empty text or patterns - be more strict about empty text
        if not text or not text.strip() or not topic_patterns:
            return False, 0.0, ""
            
        if use_semantic is None:
            use_semantic = self.use_semantic
            
        text_lower = text.lower().strip()
        
        # Additional check for very short text that shouldn't match
        if len(text_lower) < 3:
            return False, 0.0, ""
        
        # First try exact pattern matching
        for pattern in topic_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.debug(f"REGEX MATCH: pattern='{pattern}' matched text='{text_lower}'")
                return True, 100.0, pattern
        
        # Try fuzzy string matching
        best_fuzzy_match = process.extractOne(
            text_lower, 
            topic_patterns, 
            scorer=fuzz.partial_ratio
        )
        
        if best_fuzzy_match and best_fuzzy_match[1] >= self.fuzzy_threshold:
            return True, best_fuzzy_match[1], best_fuzzy_match[0]
        
        # Try semantic similarity if available
        if use_semantic and self.semantic_model:
            try:
                semantic_score, best_semantic_pattern = self._semantic_topic_match(text, topic_patterns)
                if semantic_score >= self.semantic_threshold:
                    return True, semantic_score * 100, best_semantic_pattern
            except (ValueError, RuntimeError) as e:
                logger.warning(f"Semantic matching failed: {e}")
            except Exception as e:
                logger.warning(f"Unexpected error in semantic matching: {e}")
        
        return False, 0.0, ""
    
    def _semantic_topic_match(self, text: str, topic_patterns: List[str]) -> Tuple[float, str]:
        """Match text against topics using semantic similarity."""
        try:
            # Encode the input text
            text_embedding = self.semantic_model.encode([text])
            
            # Encode all topic patterns
            pattern_embeddings = self.semantic_model.encode(topic_patterns)
            
            # Calculate cosine similarities
            similarities = []
            for i, pattern_embedding in enumerate(pattern_embeddings):
                similarity = np.dot(text_embedding[0], pattern_embedding) / (
                    np.linalg.norm(text_embedding[0]) * np.linalg.norm(pattern_embedding)
                )
                similarities.append((similarity, topic_patterns[i]))
            
            # Return best match
            best_match = max(similarities, key=lambda x: x[0])
            return best_match[0], best_match[1]
            
        except (ValueError, RuntimeError) as e:
            logger.error(f"Semantic matching calculation error: {e}")
            return 0.0, ""
        except Exception as e:
            logger.error(f"Unexpected error in semantic matching: {e}")
            return 0.0, ""
    
    def fuzzy_speaker_identification(self, sentence: str, interviewer_patterns: List[str], expert_patterns: List[str]) -> Tuple[str, float]:
        """
        Identify speaker role using fuzzy matching.
        
        Returns:
            Tuple of (speaker_role, confidence_score)
        """
        sentence_lower = sentence.lower()
        
        # Calculate interviewer score with fuzzy matching
        interviewer_score = 0
        for pattern in interviewer_patterns:
            # Try exact match first
            if re.search(pattern, sentence_lower, re.IGNORECASE):
                interviewer_score += 10
            else:
                # Try fuzzy match
                fuzzy_score = fuzz.partial_ratio(sentence_lower, pattern.lower())
                if fuzzy_score >= self.fuzzy_threshold:
                    interviewer_score += fuzzy_score / 10
        
        # Calculate expert score with fuzzy matching
        expert_score = 0
        for pattern in expert_patterns:
            # Try exact match first
            if re.search(pattern, sentence_lower, re.IGNORECASE):
                expert_score += 10
            else:
                # Try fuzzy match
                fuzzy_score = fuzz.partial_ratio(sentence_lower, pattern.lower())
                if fuzzy_score >= self.fuzzy_threshold:
                    expert_score += fuzzy_score / 10
        
        # Determine role based on scores
        if interviewer_score > expert_score and interviewer_score >= 5:
            confidence = min(interviewer_score / 10, 100)
            return "interviewer", confidence
        elif expert_score >= 2:
            confidence = min(expert_score / 10, 100)
            return "expert", confidence
        else:
            # Default to expert with low confidence
            return "expert", 25.0
    
    def fuzzy_insight_detection(self, sentence: str, insight_patterns: List[str]) -> Tuple[bool, float, List[str]]:
        """
        Detect if a sentence contains insights using fuzzy matching.
        
        Returns:
            Tuple of (has_insight, confidence_score, matched_patterns)
        """
        sentence_lower = sentence.lower()
        matched_patterns = []
        total_score = 0
        
        for pattern in insight_patterns:
            # Try exact match first
            if re.search(pattern, sentence_lower, re.IGNORECASE):
                matched_patterns.append(pattern)
                total_score += 10
            else:
                # Try fuzzy match
                fuzzy_score = fuzz.partial_ratio(sentence_lower, pattern.lower())
                if fuzzy_score >= self.fuzzy_threshold:
                    matched_patterns.append(pattern)
                    total_score += fuzzy_score / 10
        
        has_insight = len(matched_patterns) > 0
        confidence = min(total_score / len(insight_patterns) * 10, 100) if insight_patterns else 0
        
        return has_insight, confidence, matched_patterns
    
    def enhanced_topic_filtering(self, quotes: List[Dict[str, Any]], topic: str, topic_patterns: List[str]) -> List[Dict[str, Any]]:
        """
        Enhanced topic filtering using fuzzy matching and semantic similarity.
        
        Returns:
            List of quotes with enhanced relevance scoring
        """
        filtered_quotes = []
        
        for quote in quotes:
            text = quote.get('text', '')
            
            # Use fuzzy matching to determine relevance
            is_match, confidence, best_pattern = self.fuzzy_topic_match(text, topic_patterns)
            
            if is_match:
                # Add fuzzy matching metadata
                enhanced_quote = quote.copy()
                enhanced_quote['fuzzy_match'] = {
                    'confidence': confidence,
                    'best_pattern': best_pattern,
                    'matching_method': 'fuzzy' if confidence < 100 else 'exact'
                }
                filtered_quotes.append(enhanced_quote)
        
        # Sort by confidence score
        filtered_quotes.sort(key=lambda x: x['fuzzy_match']['confidence'], reverse=True)
        
        return filtered_quotes
    
    def reset_semantic_model(self):
        """Reset semantic model state for testing purposes."""
        if hasattr(self, 'semantic_model') and self.semantic_model is not None:
            del self.semantic_model
        self.semantic_model = None
        self.use_semantic = False
    
    def get_synonym_patterns(self, base_patterns: List[str]) -> List[str]:
        """Generate synonym patterns for common business terms."""
        synonym_mappings = {
            'market_leadership': [
                'market leader', 'market dominance', 'industry leader', 'market share',
                'dominant position', 'market leader', 'industry dominance', 'market control'
            ],
            'value_proposition': [
                'value prop', 'value add', 'benefit', 'advantage', 'competitive edge',
                'unique value', 'customer value', 'business value', 'ROI', 'return on investment'
            ],
            'local_presence': [
                'local footprint', 'geographic presence', 'regional coverage', 'local market',
                'proximity', 'nearby', 'local service', 'regional service', 'local support'
            ],
            'technology_advantages': [
                'tech advantage', 'technical edge', 'innovation', 'proprietary tech',
                'advanced technology', 'sophisticated tech', 'unique technology', 'tech innovation'
            ],
            'turnaround_times': [
                'speed', 'fast service', 'quick turnaround', 'rapid response',
                'efficiency', 'response time', 'service speed', 'processing speed'
            ],
            'market_limitations': [
                'market size', 'market constraint', 'market limit', 'TAM', 'total addressable market',
                'market ceiling', 'market cap', 'market boundary', 'market restriction'
            ],
            'timing_challenges': [
                'timing issue', 'seasonal variation', 'cyclical pattern', 'volatility',
                'unpredictable timing', 'timing challenge', 'timing risk', 'timing uncertainty'
            ]
        }
        
        expanded_patterns = []
        for pattern in base_patterns:
            expanded_patterns.append(pattern)
            
            # Add synonyms if they exist
            for key, synonyms in synonym_mappings.items():
                if any(keyword in pattern.lower() for keyword in key.split('_')):
                    expanded_patterns.extend(synonyms)
        
        return list(set(expanded_patterns))  # Remove duplicates
