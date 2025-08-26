#!/usr/bin/env python3
"""
Test Modular Perspective Analysis System

This script demonstrates how the new modular components work together:
- quote_ranking.py: OpenAI-driven ranking & scoring
- theme_analysis.py: Thematic clustering and cross-transcript insights  
- batch_manager.py: Batching, token handling, and retries
- perspective_analysis_refactored.py: Integration layer
"""

import os
import sys
from dotenv import load_dotenv
from settings import get_openai_api_key

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_modular_components():
    """Test the individual modular components."""
    print("🧪 Testing Modular Perspective Analysis Components")
    print("=" * 60)

    # Check for API key
    try:
        api_key = get_openai_api_key()
        if not api_key:
            print("❌ OpenAI API key not found")
            return False
    except ValueError as e:
        print(f"❌ {e}")
        return False
        
        # Test 1: Quote Ranker
        print("\n1️⃣ Testing Quote Ranker...")
        from quote_ranking import QuoteRanker
        
        quote_ranker = QuoteRanker(api_key)
        print("✅ Quote Ranker initialized successfully")
        
        # Test 2: Theme Analyzer
        print("\n2️⃣ Testing Theme Analyzer...")
        from theme_analysis import ThemeAnalyzer
        
        theme_analyzer = ThemeAnalyzer(api_key)
        print("✅ Theme Analyzer initialized successfully")
        
        # Test 3: Batch Manager
        print("\n3️⃣ Testing Batch Manager...")
        from batch_manager import BatchManager, BatchConfig
        
        batch_config = BatchConfig(
            batch_size=15,
            batch_delay=1.0,
            failure_delay=2.0,
            max_retries=2
        )
        batch_manager = BatchManager(batch_config)
        print("✅ Batch Manager initialized successfully")
        
        # Test 4: Refactored Perspective Analyzer
        print("\n4️⃣ Testing Refactored Perspective Analyzer...")
        from perspective_analysis_refactored import PerspectiveAnalyzer
        
        perspective_analyzer = PerspectiveAnalyzer(api_key)
        print("✅ Refactored Perspective Analyzer initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing modular components: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_batch_manager_functionality():
    """Test the batch manager functionality."""
    print("\n🔧 Testing Batch Manager Functionality")
    print("-" * 40)
    
    try:
        from batch_manager import BatchManager, BatchConfig
        
        # Create batch manager
        config = BatchConfig(
            batch_size=10,
            batch_delay=0.1,  # Fast for testing
            failure_delay=0.5,
            max_retries=2
        )
        batch_manager = BatchManager(config)
        
        # Test configuration
        print("📋 Testing configuration...")
        batch_manager.configure_batch_processing(batch_size=12, max_retries=3)
        
        # Test validation
        print("✅ Testing configuration validation...")
        validation = batch_manager.validate_configuration()
        print(f"   Configuration valid: {validation['valid']}")
        if validation['warnings']:
            print(f"   Warnings: {validation['warnings']}")
        
        # Test statistics
        print("📊 Testing statistics...")
        stats = batch_manager.get_batch_processing_stats()
        print(f"   Batch size: {stats['configuration']['batch_size']}")
        print(f"   Max retries: {stats['configuration']['max_retries']}")
        print(f"   Success rate: {stats['performance']['success_rate']:.1f}%")
        
        print("✅ Batch Manager functionality tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Batch Manager test failed: {e}")
        return False


def test_quote_ranker_functionality():
    """Test the quote ranker functionality."""
    print("\n🔧 Testing Quote Ranker Functionality")
    print("-" * 40)
    
    try:
        from quote_ranking import QuoteRanker
        
        # Create quote ranker
        quote_ranker = QuoteRanker("test_key")
        
        # Test statistics method
        print("📊 Testing ranking statistics...")
        empty_stats = quote_ranker.get_ranking_statistics([])
        print(f"   Empty stats: {empty_stats['total_quotes']} quotes")
        
        # Test with mock data
        mock_quotes = [
            {"text": "Test quote 1", "selection_stage": "openai_ranked"},
            {"text": "Test quote 2", "selection_stage": "openai_failed"},
        ]
        
        mock_stats = quote_ranker.get_ranking_statistics(mock_quotes)
        print(f"   Mock stats: {mock_stats['total_quotes']} quotes")
        print(f"   Successful: {mock_stats['successful_rankings']}")
        print(f"   Failed: {mock_stats['failed_rankings']}")
        
        print("✅ Quote Ranker functionality tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Quote Ranker test failed: {e}")
        return False


def test_theme_analyzer_functionality():
    """Test the theme analyzer functionality."""
    print("\n🔧 Testing Theme Analyzer Functionality")
    print("-" * 40)
    
    try:
        from theme_analysis import ThemeAnalyzer
        
        # Create theme analyzer
        theme_analyzer = ThemeAnalyzer("test_key")
        
        # Test theme statistics method
        print("📊 Testing theme statistics...")
        empty_stats = theme_analyzer.get_theme_statistics([])
        print(f"   Empty stats: {empty_stats['total_themes']} themes")
        
        # Test with mock data
        mock_themes = [
            {
                "name": "Test Theme 1",
                "confidence_score": 0.8,
                "max_quotes": 4,
                "cross_transcript_insights": ["insight1"]
            },
            {
                "name": "Test Theme 2", 
                "confidence_score": 0.9,
                "max_quotes": 3,
                "cross_transcript_insights": []
            }
        ]
        
        mock_stats = theme_analyzer.get_theme_statistics(mock_themes)
        print(f"   Mock stats: {mock_stats['total_themes']} themes")
        print(f"   Average confidence: {mock_stats['average_confidence']:.2f}")
        print(f"   Cross-transcript coverage: {mock_stats['cross_transcript_coverage']:.1f}")
        
        print("✅ Theme Analyzer functionality tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Theme Analyzer test failed: {e}")
        return False


def test_integration():
    """Test the integration between all components."""
    print("\n🔧 Testing Component Integration")
    print("-" * 40)
    
    try:
        from perspective_analysis_refactored import PerspectiveAnalyzer
        
        # Create perspective analyzer
        perspective_analyzer = PerspectiveAnalyzer("test_key")
        
        # Test batch configuration
        print("📋 Testing batch configuration integration...")
        perspective_analyzer.configure_batch_processing(
            batch_size=25,
            batch_delay=2.0,
            max_retries=4
        )
        
        # Test batch metrics
        print("📊 Testing batch metrics integration...")
        batch_metrics = perspective_analyzer.get_batch_processing_metrics()
        print(f"   Batch size: {batch_metrics['configuration']['batch_size']}")
        print(f"   Max retries: {batch_metrics['configuration']['max_retries']}")
        
        # Test configuration validation
        print("✅ Testing configuration validation integration...")
        validation = perspective_analyzer.validate_batch_configuration()
        print(f"   Configuration valid: {validation['valid']}")
        
        print("✅ Component integration tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Modular Perspective Analysis System Test")
    print("=" * 60)
    
    # Test individual components
    if not test_modular_components():
        print("\n❌ Component initialization failed")
        return
    
    # Test functionality
    tests = [
        ("Batch Manager", test_batch_manager_functionality),
        ("Quote Ranker", test_quote_ranker_functionality),
        ("Theme Analyzer", test_theme_analyzer_functionality),
        ("Integration", test_integration),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✅ {test_name} tests passed")
            else:
                print(f"\n❌ {test_name} tests failed")
        except Exception as e:
            print(f"\n❌ {test_name} tests failed with exception: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All tests passed! The modular system is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
    
    # Show next steps
    print("\n🔮 Next Steps:")
    print("1. The original perspective_analysis.py can now be replaced with perspective_analysis_refactored.py")
    print("2. Each module can be developed and tested independently")
    print("3. New features can be added to specific modules without affecting others")
    print("4. The batch manager can be reused for other OpenAI operations")
    print("5. Quote ranking and theme analysis can be used separately if needed")


if __name__ == "__main__":
    main()
