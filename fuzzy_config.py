_#!/usr/bin/env python3
"""
Configuration file for fuzzy matching settings in FlexXray transcript analysis.

This module provides configurable thresholds and settings for:
- Fuzzy string matching thresholds
- Semantic similarity thresholds
- Topic matching confidence levels
- Speaker identification sensitivity
"""

from typing import Dict, Any

# Fuzzy matching thresholds
FUZZY_THRESHOLDS = {
    "default": 80,  # Default fuzzy matching threshold
    "strict": 90,  # Strict matching for critical patterns
    "lenient": 70,  # Lenient matching for broader coverage
    "speaker_identification": 75,  # Threshold for speaker role identification
    "insight_detection": 65,  # Threshold for insight detection
    "topic_matching": 75,  # Threshold for topic matching
}

# Semantic similarity thresholds
SEMANTIC_THRESHOLDS = {
    "default": 0.7,  # Default semantic similarity threshold
    "high": 0.8,  # High confidence semantic matching
    "medium": 0.6,  # Medium confidence semantic matching
    "low": 0.5,  # Low confidence semantic matching
}

# Topic matching confidence levels
TOPIC_CONFIDENCE_LEVELS = {
    "exact_match": 100,  # Exact pattern match
    "high_confidence": 90,  # High confidence fuzzy match
    "medium_confidence": 75,  # Medium confidence fuzzy match
    "low_confidence": 60,  # Low confidence fuzzy match
    "semantic_match": 85,  # Semantic similarity match
}

# Speaker identification patterns and weights
SPEAKER_PATTERNS = {
    "interviewer": {
        "patterns": [
            r"^\s*(So|Well|Now|Let\'s|Can you|Could you|What|How|Why|When|Where|Tell me|Describe|Explain|Walk me through|Take me through|Give me|Share|What\'s|How\'s|Why\'s|When\'s|Where\'s)",
            r"\?\s*$",  # Ends with question mark
            r"\b(interviewer|interview|question|ask|inquiry|query)\b",
            r"^\s*[A-Z][a-z]+:\s*",  # Starts with "Name:" format
            r"\b(what do you think|how do you feel|what\'s your opinion|what\'s your take|what\'s your view)\b",
            r"\b(can you elaborate|can you expand|can you clarify|can you provide more detail)\b",
            r"\b(that\'s interesting|that\'s fascinating|that\'s helpful|that\'s useful|that\'s good)\b",
            r"\b(thank you|thanks|appreciate it|appreciate that|good to know)\b",
        ],
        "weight": 1.0,
        "fuzzy_threshold": 75,
    },
    "expert": {
        "patterns": [
            r"\b(I|we|our|us|FlexXray|company|firm|organization|enterprise|corporation|business|operation)\b",
            r"\b(we have|we are|we do|we provide|we offer|we deliver|we ensure|we maintain|we focus|we specialize)\b",
            r"\b(our customers|our clients|our users|our team|our staff|our equipment|our technology|our service|our process)\b",
            r"\b(experience|expertise|knowledge|understanding|insight|perspective|viewpoint|assessment|evaluation|analysis)\b",
            r"\b(industry|market|sector|field|domain|area|space|landscape|environment|ecosystem)\b",
            r"\b(advantage|strength|weakness|challenge|opportunity|risk|concern|benefit|problem|issue)\b",
            r"\b(growth|expansion|development|improvement|enhancement|optimization|streamlining|efficiency|effectiveness)\b",
        ],
        "weight": 0.8,
        "fuzzy_threshold": 70,
    },
}

# Insight detection patterns and weights
INSIGHT_PATTERNS = {
    "business_insights": {
        "patterns": [
            r"\b(advantage|strength|weakness|challenge|opportunity|risk|concern|benefit|problem|issue|advantageous|disadvantageous)\b",
            r"\b(growth|expansion|market|customer|competition|industry|business|strategy|model|approach|method)\b",
            r"\b(revenue|profit|cost|pricing|investment|strategy|financial|economic|monetary|budget)\b",
            r"\b(technology|innovation|product|service|quality|efficiency|performance|capability|feature)\b",
            r"\b(FlexXray|company|firm|organization|enterprise|corporation|business|operation)\b",
            r"\b(inspection|equipment|machine|service|capability|capacity|staffing|cost|pricing|effectiveness)\b",
            r"\b(portal|interface|user|customer|experience|satisfaction|loyalty|retention)\b",
        ],
        "weight": 1.0,
        "fuzzy_threshold": 65,
    },
    "technical_insights": {
        "patterns": [
            r"\b(technology|innovation|proprietary|patent|advanced|sophisticated|unique|technical)\b",
            r"\b(equipment|machine|system|process|methodology|approach|solution|capability)\b",
            r"\b(quality|efficiency|performance|accuracy|reliability|precision|effectiveness)\b",
        ],
        "weight": 0.9,
        "fuzzy_threshold": 70,
    },
}

# Topic synonym mappings for enhanced matching
TOPIC_SYNONYMS = {
    "market_leadership": [
        "market leader",
        "market dominance",
        "industry leader",
        "market share",
        "dominant position",
        "market leader",
        "industry dominance",
        "market control",
        "number one",
        "top provider",
        "largest",
        "primary supplier",
    ],
    "value_proposition": [
        "value prop",
        "value add",
        "benefit",
        "advantage",
        "competitive edge",
        "unique value",
        "customer value",
        "business value",
        "ROI",
        "return on investment",
        "cost benefit",
        "cost effective",
        "insourcing",
        "outsourcing",
    ],
    "local_presence": [
        "local footprint",
        "geographic presence",
        "regional coverage",
        "local market",
        "proximity",
        "nearby",
        "local service",
        "regional service",
        "local support",
        "regional footprint",
        "geographic coverage",
    ],
    "technology_advantages": [
        "tech advantage",
        "technical edge",
        "innovation",
        "proprietary tech",
        "advanced technology",
        "sophisticated tech",
        "unique technology",
        "tech innovation",
        "patent",
        "proprietary",
        "advanced",
        "sophisticated",
    ],
    "turnaround_times": [
        "speed",
        "fast service",
        "quick turnaround",
        "rapid response",
        "efficiency",
        "response time",
        "service speed",
        "processing speed",
        "fast",
        "quick",
        "rapid",
        "time to market",
    ],
    "market_limitations": [
        "market size",
        "market constraint",
        "market limit",
        "TAM",
        "total addressable market",
        "market ceiling",
        "market cap",
        "market boundary",
        "market restriction",
        "limited market",
        "constraint",
        "limitation",
        "ceiling",
        "cap",
    ],
    "timing_challenges": [
        "timing issue",
        "seasonal variation",
        "cyclical pattern",
        "volatility",
        "unpredictable timing",
        "timing challenge",
        "timing risk",
        "timing uncertainty",
        "unpredictable",
        "seasonal",
        "cyclical",
        "fluctuation",
        "variability",
        "irregular",
    ],
}

# Performance optimization settings
PERFORMANCE_SETTINGS = {
    "use_semantic_matching": True,  # Enable semantic similarity matching
    "use_fuzzy_matching": True,  # Enable fuzzy string matching
    "cache_embeddings": True,  # Cache semantic embeddings for reuse
    "batch_size": 100,  # Batch size for semantic processing
    "max_patterns_per_topic": 50,  # Maximum patterns to consider per topic
    "confidence_caching": True,  # Cache confidence scores for repeated patterns
}


def get_fuzzy_config(config_type: str = "default") -> Dict[str, Any]:
    """Get configuration for a specific type of fuzzy matching."""
    configs = {
        "default": {
            "fuzzy_threshold": FUZZY_THRESHOLDS["default"],
            "semantic_threshold": SEMANTIC_THRESHOLDS["default"],
            "use_semantic": PERFORMANCE_SETTINGS["use_semantic_matching"],
            "use_fuzzy": PERFORMANCE_SETTINGS["use_fuzzy_matching"],
        },
        "strict": {
            "fuzzy_threshold": FUZZY_THRESHOLDS["strict"],
            "semantic_threshold": SEMANTIC_THRESHOLDS["high"],
            "use_semantic": PERFORMANCE_SETTINGS["use_semantic_matching"],
            "use_fuzzy": PERFORMANCE_SETTINGS["use_fuzzy_matching"],
        },
        "lenient": {
            "fuzzy_threshold": FUZZY_THRESHOLDS["lenient"],
            "semantic_threshold": SEMANTIC_THRESHOLDS["low"],
            "use_semantic": PERFORMANCE_SETTINGS["use_semantic_matching"],
            "use_fuzzy": PERFORMANCE_SETTINGS["use_fuzzy_matching"],
        },
    }

    return configs.get(config_type, configs["default"])


def get_topic_patterns(topic: str) -> list:
    """Get expanded patterns for a specific topic including synonyms."""
    base_patterns = TOPIC_SYNONYMS.get(topic, [])
    if base_patterns:
        # Add the base topic name to patterns
        base_patterns.insert(0, topic.replace("_", " "))
    return base_patterns


def get_speaker_config(speaker_type: str) -> Dict[str, Any]:
    """Get configuration for a specific speaker type."""
    return SPEAKER_PATTERNS.get(speaker_type, {})


def get_insight_config(insight_type: str) -> Dict[str, Any]:
    """Get configuration for a specific insight type."""
    return INSIGHT_PATTERNS.get(insight_type, {})
