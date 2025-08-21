#!/usr/bin/env python3
"""
Quote Extraction Module for FlexXray Transcripts

This module handles the extraction of quotes from transcript documents
and processes them for analysis.
"""

import re
from typing import List, Dict, Any
from pathlib import Path

# Try to import python-docx for Word document processing
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("Warning: python-docx not available. Install with: pip install python-docx")

class QuoteExtractor:
    def __init__(self, min_quote_length: int = 20, max_quote_length: int = 200):
        """Initialize the quote extractor with configuration parameters."""
        self.min_quote_length = min_quote_length
        self.max_quote_length = max_quote_length

    def extract_text_from_document(self, doc_path: str) -> str:
        """Extract text content from a Word document."""
        try:
            file_extension = Path(doc_path).suffix.lower()
            
            if file_extension == '.docx':
                if not DOCX_AVAILABLE:
                    print(f"python-docx not available for {doc_path}")
                    return ""
                
                try:
                    doc = Document(doc_path)
                    text_parts = []
                    
                    for paragraph in doc.paragraphs:
                        if paragraph.text.strip():
                            text_parts.append(paragraph.text.strip())
                    
                    extracted_text = "\n\n".join(text_parts)
                    print(f"Successfully extracted {len(extracted_text)} characters from {Path(doc_path).name}")
                    return extracted_text
                    
                except Exception as e:
                    print(f"Error processing {doc_path}: {e}")
                    return ""
            else:
                print(f"Unsupported file format: {file_extension}. Only .docx files are supported.")
                return ""
                
        except Exception as e:
            print(f"Error extracting text from {doc_path}: {e}")
            return ""

    def extract_quotes_from_text(self, text: str, transcript_name: str) -> List[Dict[str, Any]]:
        """Extract meaningful quotes from transcript text with speaker role identification and context preservation."""
        if not text:
            return []
            
        quotes = []
        
        # Split text into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Track recent interviewer context for pairing with expert responses
        recent_interviewer_context = []
        max_context_sentences = 3  # Keep last 3 interviewer sentences as potential context
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            
            # Skip very short or very long sentences
            if len(sentence) < self.min_quote_length or len(sentence) > self.max_quote_length:
                continue
            
            # Identify speaker role
            speaker_role = self._identify_speaker_role(sentence)
            
            # If this is an interviewer sentence, store it as potential context
            if speaker_role == "interviewer":
                # Clean and store interviewer context
                clean_interviewer_sentence = re.sub(r'\s+', ' ', sentence).strip()
                interviewer_context = {
                    "sentence": clean_interviewer_sentence,
                    "position": i,
                    "is_question": self._is_question(clean_interviewer_sentence)
                }
                recent_interviewer_context.append(interviewer_context)
                
                # Keep only the most recent context sentences
                if len(recent_interviewer_context) > max_context_sentences:
                    recent_interviewer_context = recent_interviewer_context[-max_context_sentences:]
                
                continue  # Don't process interviewer sentences as quotes
            
            # Skip sentences that are just filler words or incomplete thoughts
            if re.match(r'^(So|Well|Um|Uh|Yeah|No|Yes|Right|Okay|I mean|You know|That\'s|It\'s)', sentence, re.IGNORECASE):
                continue
            
            # Look for sentences that contain actual insights (not just filler)
            insight_indicators = [
                r'\b(advantage|strength|weakness|challenge|opportunity|risk|concern|benefit|problem|issue|advantageous|disadvantageous)\b',
                r'\b(growth|expansion|market|customer|competition|industry|business|strategy|model|approach|method)\b',
                r'\b(revenue|profit|cost|pricing|investment|strategy|financial|economic|monetary|budget)\b',
                r'\b(technology|innovation|product|service|quality|efficiency|performance|capability|feature)\b',
                r'\b(FlexXray|company|firm|organization|enterprise|corporation|business|operation)\b',
                r'\b(inspection|equipment|machine|service|capability|capacity|staffing|cost|pricing|effectiveness)\b',
                r'\b(portal|interface|user|customer|experience|satisfaction|loyalty|retention)\b'
            ]
            
            # Check if sentence contains insight indicators
            has_insight = any(re.search(pattern, sentence, re.IGNORECASE) for pattern in insight_indicators)
            
            if has_insight:
                # Find relevant interviewer context for this quote
                relevant_context = self._find_relevant_context(sentence, recent_interviewer_context)
                
                quote = {
                    'text': sentence,
                    'speaker_role': speaker_role,
                    'transcript_name': transcript_name,
                    'position': i,
                    'has_insight': True,
                    'interviewer_context': relevant_context,
                    'metadata': {
                        'length': len(sentence),
                        'word_count': len(sentence.split()),
                        'insight_indicators': [pattern for pattern in insight_indicators if re.search(pattern, sentence, re.IGNORECASE)]
                    }
                }
                
                quotes.append(quote)
        
        return quotes

    def _identify_speaker_role(self, sentence: str) -> str:
        """Identify whether a sentence is from an interviewer or expert based on content patterns."""
        # Interviewer patterns
        interviewer_patterns = [
            r'^\s*(So|Well|Now|Let\'s|Can you|Could you|What|How|Why|When|Where|Tell me|Describe|Explain|Walk me through|Take me through|Give me|Share|What\'s|How\'s|Why\'s|When\'s|Where\'s)',
            r'\?\s*$',  # Ends with question mark
            r'\b(interviewer|interview|question|ask|inquiry|query)\b',
            r'^\s*[A-Z][a-z]+:\s*',  # Starts with "Name:" format
            r'\b(what do you think|how do you feel|what\'s your opinion|what\'s your take|what\'s your view)\b',
            r'\b(can you elaborate|can you expand|can you clarify|can you provide more detail)\b',
            r'\b(that\'s interesting|that\'s fascinating|that\'s helpful|that\'s useful|that\'s good)\b',
            r'\b(thank you|thanks|appreciate it|appreciate that|good to know)\b'
        ]
        
        # Expert patterns
        expert_patterns = [
            r'\b(I|we|our|us|FlexXray|company|firm|organization|enterprise|corporation|business|operation)\b',
            r'\b(we have|we are|we do|we provide|we offer|we deliver|we ensure|we maintain|we focus|we specialize)\b',
            r'\b(our customers|our clients|our users|our team|our staff|our equipment|our technology|our service|our process)\b',
            r'\b(experience|expertise|knowledge|understanding|insight|perspective|viewpoint|assessment|evaluation|analysis)\b',
            r'\b(industry|market|sector|field|domain|area|space|landscape|environment|ecosystem)\b',
            r'\b(advantage|strength|weakness|challenge|opportunity|risk|concern|benefit|problem|issue)\b',
            r'\b(growth|expansion|development|improvement|enhancement|optimization|streamlining|efficiency|effectiveness)\b'
        ]
        
        # Check interviewer patterns first (more specific)
        for pattern in interviewer_patterns:
            if re.search(pattern, sentence, re.IGNORECASE):
                return "interviewer"
        
        # Check expert patterns
        expert_score = 0
        for pattern in expert_patterns:
            if re.search(pattern, sentence, re.IGNORECASE):
                expert_score += 1
        
        # If sentence has multiple expert indicators, classify as expert
        if expert_score >= 2:
            return "expert"
        
        # Default to expert for sentences that don't match interviewer patterns
        return "expert"

    def _is_question(self, sentence: str) -> bool:
        """Determine if a sentence is a question."""
        # Direct question patterns
        question_patterns = [
            r'\?\s*$',  # Ends with question mark
            r'^\s*(What|How|Why|When|Where|Who|Which|Can|Could|Would|Will|Do|Does|Is|Are|Was|Were|Have|Has)\b',
            r'\b(can you|could you|would you|will you|do you|does it|is it|are they|was it|were they)\b',
            r'\b(what do you|how do you|why do you|when do you|where do you|who do you)\b',
            r'\b(tell me|describe|explain|walk me through|take me through|give me|share)\b',
            r'\b(what\'s|how\'s|why\'s|when\'s|where\'s|who\'s|which\'s)\b'
        ]
        
        return any(re.search(pattern, sentence, re.IGNORECASE) for pattern in question_patterns)

    def _find_relevant_context(self, expert_quote: str, recent_context: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find relevant interviewer context for an expert quote."""
        if not recent_context:
            return []
        
        relevant_context = []
        
        # Look for context that might be related to the expert quote
        for context in recent_context:
            context_sentence = context.get('sentence', '').lower()
            quote_lower = expert_quote.lower()
            
            # Check for semantic relevance
            relevance_score = 0
            
            # Topic relevance
            topic_keywords = [
                'flexxray', 'company', 'business', 'service', 'customer', 'market',
                'inspection', 'equipment', 'quality', 'technology', 'portal',
                'growth', 'expansion', 'challenge', 'opportunity', 'risk'
            ]
            
            for keyword in topic_keywords:
                if keyword in context_sentence and keyword in quote_lower:
                    relevance_score += 2
                elif keyword in context_sentence or keyword in quote_lower:
                    relevance_score += 1
            
            # Question-answer relevance
            if context.get('is_question'):
                relevance_score += 1
            
            # Position relevance (closer context is more relevant)
            position_weight = 1.0 / (abs(context.get('position', 0)) + 1)
            relevance_score += position_weight
            
            # If context is relevant enough, include it
            if relevance_score >= 1.5:
                relevant_context.append(context)
        
        return relevant_context
