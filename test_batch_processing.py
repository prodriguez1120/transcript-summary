#!/usr/bin/env python3
"""
Test Script for Batch Processing Functionality

This script demonstrates the new batch processing capabilities
for quote ranking in the perspective analysis system.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from settings import get_openai_api_key
from perspective_analysis import PerspectiveAnalyzer


def test_batch_processing_configuration():
    """Test batch processing configuration and parameters."""
    print("🧪 Testing Batch Processing Configuration")
    print("=" * 50)

    try:
        # Get API key
        api_key = get_openai_api_key()
        print("✅ OpenAI API key loaded successfully")

        # Initialize perspective analyzer
        analyzer = PerspectiveAnalyzer(api_key)
        print("✅ Perspective analyzer initialized successfully")

        # Test default configuration
        print("\n📋 Default Configuration:")
        metrics = analyzer.get_batch_processing_metrics()
        config = metrics["configuration"]
        print(f"  - Batch Size: {config['batch_size']}")
        print(f"  - Batch Delay: {config['batch_delay']}s")
        print(f"  - Failure Delay: {config['failure_delay']}s")
        print(f"  - Max Quotes: {config['max_quotes_per_perspective']}")
        print(f"  - Enabled: {config['batch_processing_enabled']}")

        # Test configuration updates
        print("\n⚙️ Testing Configuration Updates:")
        analyzer.configure_batch_processing(
            batch_size=15, batch_delay=2.0, failure_delay=5.0, max_quotes=300
        )

        # Verify updates
        updated_metrics = analyzer.get_batch_processing_metrics()
        updated_config = updated_metrics["configuration"]
        print(f"  - Updated Batch Size: {updated_config['batch_size']}")
        print(f"  - Updated Batch Delay: {updated_config['batch_delay']}s")
        print(f"  - Updated Failure Delay: {updated_config['failure_delay']}s")
        print(f"  - Updated Max Quotes: {updated_config['max_quotes_per_perspective']}")

        # Test performance metrics
        print("\n📊 Performance Metrics:")
        performance = updated_metrics["performance"]
        print(
            f"  - Estimated Quotes/Minute: {performance['estimated_quotes_per_minute']}"
        )
        print(f"  - Recommended Batch Size: {performance['recommended_batch_size']}")

        # Test optimization tips
        print("\n💡 Optimization Tips:")
        for tip in updated_metrics["optimization_tips"]:
            print(f"  - {tip}")

        print("\n✅ Batch processing configuration test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Error testing batch processing configuration: {e}")
        return False


def test_batch_processing_logic():
    """Test batch processing logic without making actual API calls."""
    print("\n🧪 Testing Batch Processing Logic")
    print("=" * 50)

    try:
        # Get API key
        api_key = get_openai_api_key()

        # Initialize perspective analyzer
        analyzer = PerspectiveAnalyzer(api_key)

        # Test focus area expansion
        print("📝 Testing Focus Area Expansion:")
        test_focus_areas = [
            "market position",
            "customer satisfaction",
            "technology innovation",
        ]
        expanded_areas = analyzer._expand_focus_areas(test_focus_areas)
        print(f"  - Original: {test_focus_areas}")
        print(f"  - Expanded: {expanded_areas}")
        print(
            f"  - Expansion ratio: {len(expanded_areas) / len(test_focus_areas):.1f}x"
        )

        # Test relevance scoring
        print("\n🎯 Testing Relevance Scoring:")
        test_quotes = [
            "Our market position is strong in the healthcare sector",
            "Customer satisfaction scores have improved by 25%",
            "We're investing heavily in technology innovation",
            "The weather is nice today",
            "Our business strategy focuses on growth and expansion",
        ]

        for i, quote in enumerate(test_quotes):
            score = analyzer._calculate_focus_area_relevance(quote, "market position")
            print(f"  - Quote {i+1}: {score:.2f} - '{quote[:50]}...'")

        print("\n✅ Batch processing logic test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Error testing batch processing logic: {e}")
        return False


def main():
    """Main test function."""
    print("🚀 FlexXray Batch Processing Test Suite")
    print("=" * 60)

    # Test configuration
    config_success = test_batch_processing_configuration()

    # Test logic
    logic_success = test_batch_processing_logic()

    # Summary
    print("\n📋 Test Summary")
    print("=" * 30)
    print(f"Configuration Test: {'✅ PASSED' if config_success else '❌ FAILED'}")
    print(f"Logic Test: {'✅ PASSED' if logic_success else '❌ FAILED'}")

    if config_success and logic_success:
        print("\n🎉 All tests passed! Batch processing is ready to use.")
        print("\n💡 Next steps:")
        print("  1. Run the main quote analysis tool")
        print("  2. Monitor batch processing performance")
        print("  3. Adjust configuration parameters as needed")
    else:
        print("\n⚠️ Some tests failed. Please check the error messages above.")

    return config_success and logic_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
