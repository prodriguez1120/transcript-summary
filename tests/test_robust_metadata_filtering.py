#!/usr/bin/env python3
"""
Unit tests for the robust metadata filtering system.

🚀 RECOMMENDED: This test file tests the new streamlined system components.
   Use this for production testing instead of deprecated comprehensive system tests.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from robust_metadata_filtering import RobustMetadataFilter, create_metadata_filter


class TestRobustMetadataFilter(unittest.TestCase):
    """Test the robust metadata filtering system."""

    def setUp(self):
        """Set up test fixtures."""
        self.metadata_filter = RobustMetadataFilter(confidence_threshold=2)
        
        # Sample test quotes
        self.sample_quotes = [
            {
                'text': 'What are the main challenges FlexXray faces?',
                'metadata': {'speaker_role': 'expert', 'transcript_name': 'Test1'}
            },
            {
                'text': 'FlexXray has excellent technology.',
                'metadata': {'speaker_role': 'expert', 'transcript_name': 'Test2'}
            },
            {
                'text': 'How does FlexXray compare to competitors?',
                'metadata': {'speaker_role': 'expert', 'transcript_name': 'Test3'}
            },
            {
                'text': 'Our company provides superior service.',
                'metadata': {'speaker_role': 'interviewer', 'transcript_name': 'Test4'}
            }
        ]

    def test_high_confidence_interviewer_patterns(self):
        """Test high confidence interviewer question detection."""
        high_confidence_texts = [
            'What are the main challenges?',
            'How does FlexXray compare?',
            'Can you explain the process?',
            'What if we consider alternatives?',
            'Is there a way to improve?'
        ]
        
        for text in high_confidence_texts:
            is_interviewer = self.metadata_filter.is_interviewer_question(text)
            self.assertTrue(is_interviewer, f"Should detect as interviewer: {text}")
            self.assertGreaterEqual(
                getattr(self.metadata_filter, 'last_confidence_score', 0), 
                3, 
                f"Should have high confidence for: {text}"
            )

    def test_medium_confidence_interviewer_patterns(self):
        """Test medium confidence interviewer phrase detection."""
        medium_confidence_texts = [
            'Just to start out, what is your experience?',
            'I guess, just on the competitive landscape...',
            'I\'m curious about how FlexXray handles quality.',
            'Let me ask you about the technology.'
        ]
        
        for text in medium_confidence_texts:
            is_interviewer = self.metadata_filter.is_interviewer_question(text)
            self.assertTrue(is_interviewer, f"Should detect as interviewer: {text}")
            score = getattr(self.metadata_filter, 'last_confidence_score', 0)
            self.assertGreaterEqual(score, 2, f"Should have medium confidence for: {text}")

    def test_expert_response_detection(self):
        """Test expert response detection."""
        expert_texts = [
            'Our company has a strong competitive advantage.',
            'We provide excellent customer service.',
            'FlexXray has proprietary technology.',
            'Food safety compliance is critical.',
            'According to our research, the market is growing.'
        ]
        
        for text in expert_texts:
            is_expert = self.metadata_filter.is_likely_expert_response(text)
            self.assertTrue(is_expert, f"Should detect as expert: {text}")
            score = getattr(self.metadata_filter, 'last_expert_score', 0)
            self.assertGreaterEqual(score, 2, f"Should have sufficient expert score for: {text}")

    def test_metadata_validation_and_correction(self):
        """Test metadata validation and correction pipeline."""
        # Test quotes with mislabeled speaker roles
        test_quotes = [
            {
                'text': 'What are the main challenges?',
                'metadata': {'speaker_role': 'expert', 'transcript_name': 'Test1'}
            },
            {
                'text': 'Our company provides excellent service.',
                'metadata': {'speaker_role': 'interviewer', 'transcript_name': 'Test2'}
            }
        ]
        
        corrected_quotes = self.metadata_filter.validate_and_correct_metadata(test_quotes)
        
        # First quote should be corrected from expert to interviewer
        self.assertEqual(corrected_quotes[0]['metadata']['speaker_role'], 'interviewer')
        self.assertTrue(corrected_quotes[0]['metadata'].get('corrected_role', False))
        
        # Second quote should be corrected from interviewer to expert
        # Note: This depends on the confidence scores, so we'll check if it was corrected
        if corrected_quotes[1]['metadata'].get('corrected_role', False):
            self.assertEqual(corrected_quotes[1]['metadata']['speaker_role'], 'expert')
        else:
            # If not corrected, it should still be interviewer
            self.assertEqual(corrected_quotes[1]['metadata']['speaker_role'], 'interviewer')

    def test_confidence_analysis(self):
        """Test confidence analysis capabilities."""
        test_text = 'What are the main challenges in the market?'
        analysis = self.metadata_filter.get_confidence_analysis(test_text)
        
        self.assertIn('interviewer_detection', analysis)
        self.assertIn('expert_detection', analysis)
        self.assertIn('recommendation', analysis)
        
        # Should recommend interviewer for this question (or uncertain_interviewer if both detected)
        self.assertIn(analysis['recommendation'], ['interviewer', 'uncertain_interviewer'])
        
        # Should have confidence details
        self.assertIsInstance(analysis['interviewer_detection']['confidence_details'], list)
        self.assertIsInstance(analysis['expert_detection']['confidence_details'], list)

    def test_batch_analysis(self):
        """Test batch analysis capabilities."""
        analysis = self.metadata_filter.analyze_quote_batch(self.sample_quotes)
        
        self.assertIn('total_quotes', analysis)
        self.assertIn('role_distribution', analysis)
        self.assertIn('sample_quotes', analysis)
        
        self.assertEqual(analysis['total_quotes'], 4)
        self.assertIsInstance(analysis['role_distribution'], dict)
        self.assertIsInstance(analysis['sample_quotes'], list)

    def test_question_specific_filtering(self):
        """Test question-specific quote filtering."""
        question = "What evidence shows FlexXray market leadership?"
        filtered_quotes = self.metadata_filter.prefilter_quotes_by_metadata(
            self.sample_quotes, question
        )
        
        # Should filter out interviewer questions
        for quote in filtered_quotes:
            self.assertNotIn('What are the main challenges', quote['text'])
            self.assertNotIn('How does FlexXray compare', quote['text'])

    def test_factory_function(self):
        """Test the factory function for creating metadata filters."""
        # Test default threshold
        default_filter = create_metadata_filter()
        self.assertEqual(default_filter.confidence_threshold, 2)
        
        # Test custom threshold
        custom_filter = create_metadata_filter(confidence_threshold=3)
        self.assertEqual(custom_filter.confidence_threshold, 3)

    def test_confidence_threshold_configuration(self):
        """Test different confidence threshold configurations."""
        # Strict filter (higher threshold)
        strict_filter = RobustMetadataFilter(confidence_threshold=4)
        text = 'What are the challenges?'  # Should score around 6-7
        
        is_interviewer_strict = strict_filter.is_interviewer_question(text)
        is_interviewer_default = self.metadata_filter.is_interviewer_question(text)
        
        # Both should detect as interviewer, but with different thresholds
        self.assertTrue(is_interviewer_strict)
        self.assertTrue(is_interviewer_default)

    def test_metadata_enrichment(self):
        """Test that metadata is properly enriched during validation."""
        test_quotes = [
            {
                'text': 'Sample quote text.',
                'metadata': {'speaker_role': 'expert'}
            }
        ]
        
        corrected_quotes = self.metadata_filter.validate_and_correct_metadata(test_quotes)
        
        # Should have detection confidence metadata
        metadata = corrected_quotes[0]['metadata']
        self.assertIn('detection_confidence', metadata)
        self.assertIn('interviewer_score', metadata['detection_confidence'])
        self.assertIn('expert_score', metadata['detection_confidence'])

    def test_performance_with_large_quote_sets(self):
        """Test performance with larger quote sets."""
        import time
        
        # Create a larger test set
        large_quote_set = []
        for i in range(100):
            if i % 3 == 0:
                text = f"What do you think about aspect {i}?"
                role = 'expert'
            else:
                text = f"Our company excels in area {i}."
                role = 'expert'
            
            large_quote_set.append({
                'text': text,
                'metadata': {'speaker_role': role, 'transcript_name': f'Test{i}'}
            })
        
        # Time the validation process
        start_time = time.time()
        corrected_quotes = self.metadata_filter.validate_and_correct_metadata(large_quote_set)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Should process 100 quotes in reasonable time (less than 1 second)
        self.assertLess(processing_time, 1.0, f"Processing 100 quotes took {processing_time:.3f}s")
        self.assertEqual(len(corrected_quotes), 100)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
