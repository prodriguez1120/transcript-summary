#!/usr/bin/env python3
"""
Robust Metadata Filtering System for FlexXray Transcript Analysis

This module provides enhanced metadata validation and correction capabilities
to improve the accuracy of speaker role classification and quote filtering.
"""

import re
from typing import List, Dict, Any, Optional
import logging

class RobustMetadataFilter:
    """Enhanced metadata filtering and validation for quote analysis."""
    
    def __init__(self, confidence_threshold: int = 2):
        """Initialize the metadata filter with configurable confidence threshold."""
        self.confidence_threshold = confidence_threshold
        self.logger = logging.getLogger(__name__)
        
        # Enhanced interviewer question patterns with advanced detection
        self.high_confidence_patterns = [
            r'^what\s+', r'^how\s+', r'^why\s+', r'^when\s+', r'^where\s+', r'^who\s+',
            r'^can you\s+', r'^could you\s+', r'^would you\s+', r'^is that\s+',
            r'^has\s+', r'^do you\s+', r'^are you\s+', r'^tell me\s+', r'^describe\s+',
            r'^explain\s+', r'^walk me through\s+', r'^take me through\s+',
            r'^what if\s+', r'^how about\s+', r'^why do you\s+', r'^when do you\s+',
            r'^where do you\s+', r'^who do you\s+', r'^can we\s+', r'^could we\s+',
            r'^would we\s+', r'^is there\s+', r'^are there\s+', r'^does it\s+',
            r'^do they\s+', r'^have you\s+', r'^has it\s+', r'^will you\s+',
            r'^should we\s+', r'^might you\s+', r'^could it\s+', r'^would it\s+'
        ]
        
        self.medium_confidence_patterns = [
            r'^just to start out', r'^i guess, just on', r'^out of those, how many',
            r'^you would really go to', r'^i\'m curious about', r'^i\'d like to understand',
            r'^help me understand', r'^can you help me', r'^i want to know',
            r'^i\'m wondering', r'^i\'d love to hear', r'^it would be great to know',
            r'^i\'m trying to understand', r'^i\'m looking to understand', r'^i need to know',
            r'^i\'d appreciate if you could', r'^would it be possible to', r'^i was thinking',
            r'^let me ask you', r'^let me get this straight', r'^so what you\'re saying is',
            r'^to clarify', r'^to make sure i understand', r'^just to confirm',
            r'^one more thing', r'^before we move on', r'^while we\'re on the topic'
        ]
        
        # Low confidence patterns (subtle interviewer indicators)
        self.low_confidence_patterns = [
            r'\b(think|thought|thinking)\s+about\b', r'\b(see|saw|seeing)\s+in\b',
            r'\b(find|found|finding)\s+out\b', r'\b(learn|learned|learning)\s+about\b',
            r'\b(hear|heard|hearing)\s+about\b', r'\b(read|reading)\s+about\b',
            r'\b(experience|experienced)\s+with\b', r'\b(work|worked|working)\s+with\b',
            r'\b(deal|dealt|dealing)\s+with\b', r'\b(handle|handled|handling)\b'
        ]
        
        self.expert_indicators = [
            'our company', 'our team', 'our customers', 'our service', 'our technology',
            'we have', 'we provide', 'we offer', 'we deliver', 'we specialize',
            'flexxray has', 'flexxray provides', 'flexxray offers', 'flexxray delivers',
            'i believe', 'i think', 'in my experience', 'from my perspective',
            'the advantage', 'the benefit', 'the challenge', 'the opportunity',
            'our approach', 'our strategy', 'our process', 'our methodology',
            'we focus on', 'we concentrate on', 'we emphasize', 'we prioritize',
            'our capabilities', 'our expertise', 'our knowledge', 'our understanding',
            'we\'ve developed', 'we\'ve created', 'we\'ve built', 'we\'ve established',
            'our competitive position', 'our market position', 'our industry position',
            'we\'re able to', 'we can', 'we will', 'we do', 'we are', 'we have been'
        ]
        
        self.business_terms = [
            'revenue', 'profit', 'market', 'customer', 'competition', 'technology', 
            'innovation', 'strategy', 'advantage', 'benefit', 'challenge', 'opportunity',
            'efficiency', 'effectiveness', 'quality', 'performance', 'capability',
            'capacity', 'scalability', 'sustainability', 'reliability', 'flexibility',
            'integration', 'optimization', 'standardization', 'automation', 'digitization',
            'compliance', 'regulatory', 'certification', 'accreditation', 'validation',
            'verification', 'testing', 'inspection', 'analysis', 'assessment', 'evaluation'
        ]
        
        # Industry-specific terms for FlexXray
        self.industry_terms = [
            'food safety', 'quality assurance', 'foreign material', 'contamination',
            'inspection', 'detection', 'x-ray', 'imaging', 'processing', 'packaging',
            'manufacturing', 'production', 'supply chain', 'logistics', 'distribution',
            'retail', 'wholesale', 'restaurant', 'catering', 'food service', 'hospitality'
        ]
    
    def is_interviewer_question(self, text: str) -> bool:
        """Enhanced interviewer question detection with advanced confidence scoring."""
        text_lower = text.lower().strip()
        interviewer_confidence = 0
        confidence_details = []
        
        # High confidence patterns (definitive interviewer questions)
        for pattern in self.high_confidence_patterns:
            if re.search(pattern, text_lower):
                interviewer_confidence += 3
                confidence_details.append(f"high_pattern:+3")
                break
        
        # Medium confidence patterns (interviewer phrases)
        for pattern in self.medium_confidence_patterns:
            if re.search(pattern, text_lower):
                interviewer_confidence += 2
                confidence_details.append(f"medium_pattern:+2")
                break
        
        # Low confidence patterns (subtle interviewer indicators)
        for pattern in self.low_confidence_patterns:
            if re.search(pattern, text_lower):
                interviewer_confidence += 1
                confidence_details.append(f"low_pattern:+1")
                break
        
        # Question mark analysis
        if '?' in text:
            interviewer_confidence += 1
            confidence_details.append("question_mark:+1")
            
            # Short questions are more likely to be interviewer questions
            if len(text) < 150:
                interviewer_confidence += 1
                confidence_details.append("short_length:+1")
            
            # Questions about FlexXray specifically
            if 'flexxray' in text_lower:
                interviewer_confidence += 1
                confidence_details.append("flexxray_mention:+1")
        
        # Question words analysis (more sophisticated)
        question_words = ['what', 'how', 'why', 'when', 'where', 'who', 'can', 'could', 'would', 'is', 'are', 'do', 'does', 'has', 'have']
        question_word_count = sum(1 for word in question_words if word in text_lower)
        if question_word_count > 0:
            interviewer_confidence += min(question_word_count, 2)  # Cap at +2
            confidence_details.append(f"question_words:+{min(question_word_count, 2)}")
        
        # Expert response indicators (reduce confidence)
        expert_indicator_count = sum(1 for indicator in self.expert_indicators if indicator in text_lower)
        if expert_indicator_count > 0:
            interviewer_confidence -= min(expert_indicator_count * 2, 4)  # Cap at -4
            confidence_details.append(f"expert_indicators:-{min(expert_indicator_count * 2, 4)}")
        
        # Business/industry terms (reduce confidence)
        business_term_count = sum(1 for term in self.business_terms if term in text_lower)
        industry_term_count = sum(1 for term in self.industry_terms if term in text_lower)
        if business_term_count > 0 or industry_term_count > 0:
            total_terms = business_term_count + industry_term_count
            interviewer_confidence -= min(total_terms, 3)  # Cap at -3
            confidence_details.append(f"business_terms:-{min(total_terms, 3)}")
        
        # Length-based analysis (more nuanced)
        if len(text) > 300:  # Very long responses are more likely to be expert insights
            interviewer_confidence -= 2
            confidence_details.append("very_long_length:-2")
        elif len(text) > 200:  # Long responses
            interviewer_confidence -= 1
            confidence_details.append("long_length:-1")
        elif len(text) < 50:  # Very short responses might be questions
            interviewer_confidence += 1
            confidence_details.append("very_short_length:+1")
        
        # Context analysis (interviewer vs expert context)
        if any(phrase in text_lower for phrase in ['you think', 'you believe', 'you see', 'you find']):
            interviewer_confidence += 1
            confidence_details.append("you_context:+1")
        
        # Store confidence details for debugging
        self.last_confidence_details = confidence_details
        self.last_confidence_score = interviewer_confidence
        
        return interviewer_confidence >= self.confidence_threshold
    
    def is_likely_expert_response(self, text: str) -> bool:
        """Detect if a quote is likely an expert response that was mislabeled."""
        text_lower = text.lower().strip()
        expert_score = 0
        score_details = []
        
        # Check for expert indicators
        expert_indicator_count = sum(1 for indicator in self.expert_indicators if indicator in text_lower)
        expert_score += expert_indicator_count
        if expert_indicator_count > 0:
            score_details.append(f"expert_indicators:+{expert_indicator_count}")
        
        # Length-based analysis (expert responses tend to be longer)
        if len(text) > 200:
            expert_score += 2
            score_details.append("long_length:+2")
        elif len(text) > 100:
            expert_score += 1
            score_details.append("medium_length:+1")
        
        # Check for business/technical terminology
        business_term_count = sum(1 for term in self.business_terms if term in text_lower)
        if business_term_count > 0:
            expert_score += min(business_term_count, 3)  # Cap at +3
            score_details.append(f"business_terms:+{min(business_term_count, 3)}")
        
        # Check for industry-specific terminology
        industry_term_count = sum(1 for term in self.industry_terms if term in text_lower)
        if industry_term_count > 0:
            expert_score += min(industry_term_count, 2)  # Cap at +2
            score_details.append(f"industry_terms:+{min(industry_term_count, 2)}")
        
        # Check for professional language patterns
        professional_patterns = [
            r'\b(according to|based on|research shows|studies indicate|data suggests)\b',
            r'\b(typically|generally|usually|commonly|frequently)\b',
            r'\b(however|nevertheless|furthermore|additionally|moreover)\b',
            r'\b(consequently|therefore|thus|hence|as a result)\b'
        ]
        
        professional_score = sum(1 for pattern in professional_patterns if re.search(pattern, text_lower))
        if professional_score > 0:
            expert_score += professional_score
            score_details.append(f"professional_language:+{professional_score}")
        
        # Check for specific vs general statements
        specific_indicators = ['specific', 'particular', 'exact', 'precise', 'detailed', 'comprehensive']
        if any(indicator in text_lower for indicator in specific_indicators):
            expert_score += 1
            score_details.append("specific_language:+1")
        
        # Store score details for debugging
        self.last_expert_score_details = score_details
        self.last_expert_score = expert_score
        
        return expert_score >= 2
    
    def validate_and_correct_metadata(self, quotes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and correct metadata for quotes with enhanced confidence reporting."""
        corrected_quotes = []
        corrections_made = 0
        confidence_summary = {
            'high_confidence_corrections': 0,
            'medium_confidence_corrections': 0,
            'low_confidence_corrections': 0,
            'correction_reasons': {}
        }
        
        for i, quote in enumerate(quotes):
            corrected_quote = quote.copy()
            metadata = corrected_quote.get("metadata", {})
            text = corrected_quote.get("text", "")
            
            # Check if speaker_role needs correction
            current_role = metadata.get("speaker_role", "unknown")
            
            # Use our enhanced interviewer detection
            is_interviewer = self.is_interviewer_question(text)
            interviewer_confidence = getattr(self, 'last_confidence_score', 0)
            
            # Use our enhanced expert response detection
            is_expert = self.is_likely_expert_response(text)
            expert_confidence = getattr(self, 'last_expert_score', 0)
            
            correction_made = False
            correction_reason = ""
            confidence_level = "low"
            
            if is_interviewer and current_role == "expert":
                # Correct mislabeled interviewer questions
                metadata["speaker_role"] = "interviewer"
                metadata["corrected_role"] = True
                metadata["correction_reason"] = "interviewer_question_detected"
                metadata["correction_confidence"] = interviewer_confidence
                metadata["correction_details"] = getattr(self, 'last_confidence_details', [])
                
                # Determine confidence level
                if interviewer_confidence >= 4:
                    confidence_level = "high"
                    confidence_summary['high_confidence_corrections'] += 1
                elif interviewer_confidence >= 2:
                    confidence_level = "medium"
                    confidence_summary['medium_confidence_corrections'] += 1
                else:
                    confidence_summary['low_confidence_corrections'] += 1
                
                correction_made = True
                correction_reason = "interviewer_question_detected"
                corrections_made += 1
                
            elif not is_interviewer and current_role == "interviewer":
                # Check if this might be a mislabeled expert response
                if is_expert:
                    metadata["speaker_role"] = "expert"
                    metadata["corrected_role"] = True
                    metadata["correction_reason"] = "expert_response_detected"
                    metadata["correction_confidence"] = expert_confidence
                    metadata["correction_details"] = getattr(self, 'last_expert_score_details', [])
                    
                    # Determine confidence level
                    if expert_confidence >= 5:
                        confidence_level = "high"
                        confidence_summary['high_confidence_corrections'] += 1
                    elif expert_confidence >= 3:
                        confidence_level = "medium"
                        confidence_summary['medium_confidence_corrections'] += 1
                    else:
                        confidence_summary['low_confidence_corrections'] += 1
                    
                    correction_made = True
                    correction_reason = "expert_response_detected"
                    corrections_made += 1
            
            # Track correction reasons
            if correction_made:
                if correction_reason not in confidence_summary['correction_reasons']:
                    confidence_summary['correction_reasons'][correction_reason] = 0
                confidence_summary['correction_reasons'][correction_reason] += 1
                
                self.logger.debug(f"Corrected speaker role for quote {i+1}: {text[:50]}... (confidence: {confidence_level})")
            
            # Ensure required metadata fields exist
            if "quote_type" not in metadata:
                metadata["quote_type"] = "expert_insight" if metadata.get("speaker_role") == "expert" else "other"
            
            if "transcript_name" not in metadata:
                metadata["transcript_name"] = "Unknown Transcript"
            
            # Add confidence metadata
            metadata["detection_confidence"] = {
                "interviewer_score": interviewer_confidence,
                "expert_score": expert_confidence,
                "interviewer_details": getattr(self, 'last_confidence_details', []),
                "expert_details": getattr(self, 'last_expert_score_details', [])
            }
            
            corrected_quote["metadata"] = metadata
            corrected_quotes.append(corrected_quote)
        
        # Print detailed correction summary
        if corrections_made > 0:
            print(f"Metadata validation: Corrected {corrections_made} speaker role misclassifications")
            print(f"  High confidence: {confidence_summary['high_confidence_corrections']}")
            print(f"  Medium confidence: {confidence_summary['medium_confidence_corrections']}")
            print(f"  Low confidence: {confidence_summary['low_confidence_corrections']}")
            
            if confidence_summary['correction_reasons']:
                print("  Correction reasons:")
                for reason, count in confidence_summary['correction_reasons'].items():
                    print(f"    {reason}: {count}")
        
        return corrected_quotes
    
    def prefilter_quotes_by_metadata(self, quotes: List[Dict[str, Any]], question: str) -> List[Dict[str, Any]]:
        """Enhanced pre-filtering with robust metadata validation."""
        if not quotes:
            return []
        
        filtered_quotes = []
        interviewer_questions_removed = 0
        
        for quote in quotes:
            metadata = quote.get("metadata", {})
            quote_type = metadata.get("quote_type", "")
            speaker_role = metadata.get("speaker_role", "")
            text = quote.get("text", "")
            text_lower = text.lower()
            
            # Skip if not expert
            if speaker_role != "expert":
                continue
            
            # CRITICAL: Remove interviewer questions that are mislabeled as expert
            if self.is_interviewer_question(text):
                interviewer_questions_removed += 1
                continue
            
            # Question-specific filtering with expanded keywords
            question_lower = question.lower()
            
            # Market leadership
            if "market leadership" in question_lower or "competitive advantage" in question_lower:
                if any(word in text_lower for word in ["advantage", "strength", "leadership", "competitive", "superior", "better", "excellent", "strong", "market", "position", "edge", "benefit"]):
                    filtered_quotes.append(quote)
            
            # Value proposition
            elif "value proposition" in question_lower or "insourcing risk" in question_lower:
                if any(word in text_lower for word in ["value", "proposition", "benefit", "advantage", "cost", "pricing", "quality", "service", "turnaround", "efficiency", "effectiveness", "superior", "better", "advantageous"]):
                    filtered_quotes.append(quote)
            
            # Customer satisfaction
            elif "customer satisfaction" in question_lower or "loyalty" in question_lower:
                if any(word in text_lower for word in ["customer", "satisfaction", "loyalty", "retention", "experience", "service", "quality", "turnaround", "portal", "interface", "user", "friendly", "easy", "convenient", "helpful"]):
                    filtered_quotes.append(quote)
            
            # Technology advantage
            elif "technology" in question_lower or "innovation" in question_lower:
                if any(word in text_lower for word in ["technology", "innovation", "proprietary", "advanced", "sophisticated", "cutting-edge", "modern", "efficient", "automated", "digital", "software", "system", "platform", "solution"]):
                    filtered_quotes.append(quote)
            
            # Growth potential
            elif "growth" in question_lower or "expansion" in question_lower:
                if any(word in text_lower for word in ["growth", "expansion", "increase", "grow", "expand", "scalable", "scalability", "capacity", "volume", "demand", "opportunity", "potential", "future", "market", "customer"]):
                    filtered_quotes.append(quote)
            
            # Operational efficiency
            elif "operational efficiency" in question_lower or "cost structure" in question_lower:
                if any(word in text_lower for word in ["efficiency", "efficient", "cost", "pricing", "turnaround", "speed", "fast", "quick", "rapid", "streamlined", "optimized", "process", "workflow", "automation", "productivity"]):
                    filtered_quotes.append(quote)
            
            # Industry expertise
            elif "industry expertise" in question_lower or "knowledge" in question_lower:
                if any(word in text_lower for word in ["expertise", "knowledge", "experience", "understanding", "insight", "perspective", "viewpoint", "assessment", "evaluation", "analysis", "industry", "market", "sector", "field", "domain"]):
                    filtered_quotes.append(quote)
            
            # Default: include if no specific category matches
            else:
                filtered_quotes.append(quote)
        
        print(f"Pre-filtered {len(quotes)} quotes to {len(filtered_quotes)} based on question context")
        if interviewer_questions_removed > 0:
            print(f"Removed {interviewer_questions_removed} interviewer questions that were mislabeled as expert")
        
        return filtered_quotes

    def get_confidence_analysis(self, text: str) -> Dict[str, Any]:
        """Get detailed confidence analysis for a given text."""
        # Run both detection methods to get scores
        is_interviewer = self.is_interviewer_question(text)
        is_expert = self.is_likely_expert_response(text)
        
        return {
            'text_preview': text[:100] + '...' if len(text) > 100 else text,
            'interviewer_detection': {
                'is_interviewer': is_interviewer,
                'confidence_score': getattr(self, 'last_confidence_score', 0),
                'confidence_details': getattr(self, 'last_confidence_details', []),
                'threshold': self.confidence_threshold
            },
            'expert_detection': {
                'is_expert': is_expert,
                'confidence_score': getattr(self, 'last_expert_score', 0),
                'confidence_details': getattr(self, 'last_expert_score_details', []),
                'threshold': 2
            },
            'recommendation': self._get_role_recommendation(text, is_interviewer, is_expert)
        }
    
    def _get_role_recommendation(self, text: str, is_interviewer: bool, is_expert: bool) -> str:
        """Get role recommendation based on detection results."""
        if is_interviewer and not is_expert:
            return "interviewer"
        elif is_expert and not is_interviewer:
            return "expert"
        elif is_interviewer and is_expert:
            return "uncertain_interviewer"  # Both detected, prioritize interviewer
        else:
            return "uncertain_expert"  # Neither detected, default to expert
    
    def analyze_quote_batch(self, quotes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze a batch of quotes and provide comprehensive statistics."""
        if not quotes:
            return {'error': 'No quotes provided'}
        
        analysis = {
            'total_quotes': len(quotes),
            'role_distribution': {'expert': 0, 'interviewer': 0, 'unknown': 0},
            'correction_summary': {'total': 0, 'high_confidence': 0, 'medium_confidence': 0, 'low_confidence': 0},
            'confidence_ranges': {'interviewer': [], 'expert': []},
            'sample_quotes': []
        }
        
        # Process each quote
        for i, quote in enumerate(quotes[:5]):  # Sample first 5 for detailed analysis
            text = quote.get('text', '')
            metadata = quote.get('metadata', {})
            current_role = metadata.get('speaker_role', 'unknown')
            
            # Count roles
            analysis['role_distribution'][current_role] = analysis['role_distribution'].get(current_role, 0) + 1
            
            # Get confidence analysis
            confidence_analysis = self.get_confidence_analysis(text)
            
            # Store confidence scores
            interviewer_score = confidence_analysis['interviewer_detection']['confidence_score']
            expert_score = confidence_analysis['expert_detection']['confidence_score']
            
            if interviewer_score > 0:
                analysis['confidence_ranges']['interviewer'].append(interviewer_score)
            if expert_score > 0:
                analysis['confidence_ranges']['expert'].append(expert_score)
            
            # Store sample analysis
            analysis['sample_quotes'].append({
                'index': i,
                'current_role': current_role,
                'recommended_role': confidence_analysis['recommendation'],
                'interviewer_score': interviewer_score,
                'expert_score': expert_score,
                'text_preview': text[:80] + '...' if len(text) > 80 else text
            })
        
        # Calculate confidence statistics
        for role_type, scores in analysis['confidence_ranges'].items():
            if scores:
                analysis['confidence_ranges'][role_type] = {
                    'min': min(scores),
                    'max': max(scores),
                    'avg': sum(scores) / len(scores),
                    'count': len(scores)
                }
        
        return analysis

def create_metadata_filter(confidence_threshold: int = 2) -> RobustMetadataFilter:
    """Factory function to create a metadata filter instance."""
    return RobustMetadataFilter(confidence_threshold)
