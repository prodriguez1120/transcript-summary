#!/usr/bin/env python3
"""
Company Configuration Module for Transcript Summarizer

This module centralizes all company-specific configurations, making it easy to
switch between different companies and their analysis settings.
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from pathlib import Path

@dataclass
class CompanyConfig:
    """Configuration for a specific company."""
    name: str
    display_name: str
    transcript_directory: str
    output_prefix: str
    key_questions: Dict[str, str]
    question_categories: Dict[str, List[str]]
    speaker_patterns: Dict[str, Dict[str, Any]]
    business_insights: Dict[str, Dict[str, Any]]
    topic_synonyms: Dict[str, List[str]]
    industry_keywords: List[str]
    company_specific_terms: List[str]

# Default company configurations
COMPANY_CONFIGS = {
    "flexxray": CompanyConfig(
        name="flexxray",
        display_name="FlexXray",
        transcript_directory="FlexXray Transcripts",
        output_prefix="FlexXray",
        key_questions={
            "market_leadership": "What evidence shows FlexXray's market leadership and competitive advantage?",
            "value_proposition": "How does FlexXray's value proposition address the risk of insourcing?",
            "local_presence": "How does FlexXray's local presence and footprint drive customer demand?",
            "technology_advantages": "What proprietary technology advantages does FlexXray offer?",
            "rapid_turnaround": "How do FlexXray's rapid turnaround times benefit customers?",
            "limited_tam": "What limits FlexXray's Total Addressable Market (TAM)?",
            "unpredictable_timing": "How does unpredictable event timing impact FlexXray's business?"
        },
        question_categories={
            "key_takeaways": ["market_leadership", "value_proposition", "local_presence"],
            "strengths": ["technology_advantages", "rapid_turnaround"],
            "weaknesses": ["limited_tam", "unpredictable_timing"]
        },
        speaker_patterns={
            "interviewer": {
                "patterns": [
                    r'^\s*(So|Well|Now|Let\'s|Can you|Could you|What|How|Why|When|Where|Tell me|Describe|Explain|Walk me through|Take me through|Give me|Share|What\'s|How\'s|Why\'s|When\'s|Where\'s)',
                    r'\?\s*$',  # Ends with question mark
                    r'\b(interviewer|interview|question|ask|inquiry|query)\b',
                    r'^\s*[A-Z][a-z]+:\s*',  # Starts with "Name:" format
                    r'\b(what do you think|how do you feel|what\'s your opinion|what\'s your take|what\'s your view)\b',
                    r'\b(can you elaborate|can you expand|can you clarify|can you provide more detail)\b',
                    r'\b(that\'s interesting|that\'s fascinating|that\'s helpful|that\'s useful|that\'s good)\b',
                    r'\b(thank you|thanks|appreciate it|appreciate that|good to know)\b'
                ],
                "weight": 1.0,
                "fuzzy_threshold": 75
            },
            "expert": {
                "patterns": [
                    r'\b(I|we|our|us|FlexXray|company|firm|organization|enterprise|corporation|business|operation)\b',
                    r'\b(we have|we are|we do|we provide|we offer|we deliver|we ensure|we maintain|we focus|we specialize)\b',
                    r'\b(our customers|our clients|our users|our team|our staff|our equipment|our technology|our service|our process)\b',
                    r'\b(experience|expertise|knowledge|understanding|insight|perspective|viewpoint|assessment|evaluation|analysis)\b',
                    r'\b(industry|market|sector|field|domain|area|space|landscape|environment|ecosystem)\b',
                    r'\b(advantage|strength|weakness|challenge|opportunity|risk|concern|benefit|problem|issue)\b',
                    r'\b(growth|expansion|development|improvement|enhancement|optimization|streamlining|efficiency|effectiveness)\b'
                ],
                "weight": 0.8,
                "fuzzy_threshold": 70
            }
        },
        business_insights={
            "business_insights": {
                "patterns": [
                    r'\b(advantage|strength|weakness|challenge|opportunity|risk|concern|benefit|problem|issue|advantageous|disadvantageous)\b',
                    r'\b(growth|expansion|market|customer|competition|industry|business|strategy|model|approach|method)\b',
                    r'\b(revenue|profit|cost|pricing|investment|strategy|financial|economic|monetary|budget)\b',
                    r'\b(technology|innovation|product|service|quality|efficiency|performance|capability|feature)\b',
                    r'\b(FlexXray|company|firm|organization|enterprise|corporation|business|operation)\b',
                    r'\b(inspection|equipment|machine|service|capability|capacity|staffing|cost|pricing|effectiveness)\b',
                    r'\b(portal|interface|user|customer|experience|satisfaction|loyalty|retention)\b'
                ],
                "weight": 1.0,
                "fuzzy_threshold": 65
            },
            "technical_insights": {
                "patterns": [
                    r'\b(technology|innovation|proprietary|patent|advanced|sophisticated|unique|technical)\b',
                    r'\b(equipment|machine|system|process|methodology|approach|solution|capability)\b',
                    r'\b(quality|efficiency|performance|accuracy|reliability|precision|effectiveness)\b'
                ],
                "weight": 0.9,
                "fuzzy_threshold": 70
            }
        },
        topic_synonyms={
            "market_leadership": [
                "market leader", "market dominance", "industry leader", "market share",
                "dominant position", "market leader", "industry dominance", "market control",
                "number one", "top provider", "largest", "primary supplier"
            ],
            "value_proposition": [
                "value prop", "value add", "benefit", "advantage", "competitive edge",
                "unique value", "customer value", "business value", "ROI", "return on investment",
                "cost benefit", "cost effective", "insourcing", "outsourcing"
            ],
            "local_presence": [
                "local footprint", "geographic presence", "regional coverage", "local market",
                "proximity", "nearby", "local service", "regional service", "local support",
                "regional footprint", "geographic coverage"
            ],
            "technology_advantages": [
                "tech advantage", "technical edge", "innovation", "proprietary tech",
                "advanced technology", "sophisticated tech", "unique technology", "tech innovation",
                "patent", "proprietary", "advanced", "sophisticated"
            ],
            "turnaround_times": [
                "speed", "fast service", "quick turnaround", "rapid response",
                "efficiency", "response time", "service speed", "processing speed",
                "fast", "quick", "rapid", "time to market"
            ],
            "market_limitations": [
                "market size", "market constraint", "market limit", "TAM", "total addressable market",
                "market ceiling", "market cap", "market boundary", "market restriction",
                "limited market", "constraint", "limitation", "ceiling", "cap"
            ],
            "timing_challenges": [
                "timing issue", "seasonal variation", "cyclical pattern", "volatility",
                "unpredictable timing", "timing challenge", "timing risk", "timing uncertainty",
                "unpredictable", "seasonal", "cyclical", "fluctuation", "variability", "irregular"
            ]
        },
        industry_keywords=[
            "inspection", "quality control", "food safety", "foreign material",
            "x-ray", "detection", "manufacturing", "production", "batch processing",
            "compliance", "regulatory", "safety standards", "equipment", "machinery"
        ],
        company_specific_terms=[
            "FlexXray", "inspection services", "foreign material detection",
            "batch inspection", "quality assurance", "safety compliance"
        ]
    ),
    
    "acme_corp": CompanyConfig(
        name="acme_corp",
        display_name="ACME Corporation",
        transcript_directory="ACME Transcripts",
        output_prefix="ACME",
        key_questions={
            "market_position": "What is ACME's current market position and competitive landscape?",
            "product_portfolio": "How does ACME's product portfolio address customer needs?",
            "operational_efficiency": "What operational efficiencies does ACME demonstrate?",
            "customer_satisfaction": "How do customers perceive ACME's service quality?",
            "growth_potential": "What growth opportunities exist for ACME?",
            "risk_factors": "What are the main risk factors affecting ACME's business?"
        },
        question_categories={
            "key_takeaways": ["market_position", "product_portfolio", "operational_efficiency"],
            "strengths": ["customer_satisfaction", "growth_potential"],
            "weaknesses": ["risk_factors"]
        },
        speaker_patterns={
            "interviewer": {
                "patterns": [
                    r'^\s*(So|Well|Now|Let\'s|Can you|Could you|What|How|Why|When|Where|Tell me|Describe|Explain|Walk me through|Take me through|Give me|Share|What\'s|How\'s|Why\'s|When\'s|Where\'s)',
                    r'\?\s*$',
                    r'\b(interviewer|interview|question|ask|inquiry|query)\b',
                    r'^\s*[A-Z][a-z]+:\s*',
                    r'\b(what do you think|how do you feel|what\'s your opinion|what\'s your take|what\'s your view)\b'
                ],
                "weight": 1.0,
                "fuzzy_threshold": 75
            },
            "expert": {
                "patterns": [
                    r'\b(I|we|our|us|ACME|company|firm|organization|enterprise|corporation|business|operation)\b',
                    r'\b(we have|we are|we do|we provide|we offer|we deliver|we ensure|we maintain|we focus|we specialize)\b',
                    r'\b(our customers|our clients|our users|our team|our staff|our products|our technology|our service|our process)\b'
                ],
                "weight": 0.8,
                "fuzzy_threshold": 70
            }
        },
        business_insights={
            "business_insights": {
                "patterns": [
                    r'\b(advantage|strength|weakness|challenge|opportunity|risk|concern|benefit|problem|issue)\b',
                    r'\b(growth|expansion|market|customer|competition|industry|business|strategy|model|approach|method)\b',
                    r'\b(ACME|company|firm|organization|enterprise|corporation|business|operation)\b'
                ],
                "weight": 1.0,
                "fuzzy_threshold": 65
            }
        },
        topic_synonyms={
            "market_position": ["market share", "competitive position", "industry standing", "market presence"],
            "product_portfolio": ["product line", "service offerings", "product range", "service portfolio"],
            "operational_efficiency": ["efficiency", "productivity", "performance", "operational excellence"]
        },
        industry_keywords=[
            "manufacturing", "production", "quality", "efficiency", "operations",
            "supply chain", "logistics", "customer service", "product development"
        ],
        company_specific_terms=[
            "ACME", "product portfolio", "operational efficiency", "customer satisfaction"
        ]
    ),

    "practifi": CompanyConfig(
        name="practifi",
        display_name="Practifi",
        transcript_directory="Practifi Transcripts",
        output_prefix="Practifi",
        key_questions={
            "platform_adoption": "How is Practifi's platform being adopted by financial advisors?",
            "user_experience": "What is the user experience like for financial advisors using Practifi?",
            "feature_effectiveness": "Which Practifi features are most effective for advisor workflows?",
            "integration_capabilities": "How well does Practifi integrate with existing advisor systems?",
            "customer_satisfaction": "What is the overall satisfaction level of Practifi users?",
            "competitive_position": "How does Practifi compare to other advisor technology platforms?",
            "growth_opportunities": "What growth opportunities exist for Practifi in the advisor market?"
        },
        question_categories={
            "key_takeaways": ["platform_adoption", "user_experience", "feature_effectiveness"],
            "strengths": ["integration_capabilities", "customer_satisfaction"],
            "weaknesses": ["competitive_position", "growth_opportunities"]
        },
        speaker_patterns={
            "interviewer": {
                "patterns": [
                    r'^\s*(So|Well|Now|Let\'s|Can you|Could you|What|How|Why|When|Where|Tell me|Describe|Explain|Walk me through|Take me through|Give me|Share|What\'s|How\'s|Why\'s|When\'s|Where\'s)',
                    r'\?\s*$',
                    r'\b(interviewer|interview|question|ask|inquiry|query)\b',
                    r'^\s*[A-Z][a-z]+:\s*',
                    r'\b(what do you think|how do you feel|what\'s your opinion|what\'s your take|what\'s your view)\b',
                    r'\b(can you elaborate|can you expand|can you clarify|can you provide more detail)\b'
                ],
                "weight": 1.0,
                "fuzzy_threshold": 75
            },
            "expert": {
                "patterns": [
                    r'\b(I|we|our|us|Practifi|company|firm|organization|enterprise|corporation|business|operation)\b',
                    r'\b(we have|we are|we do|we provide|we offer|we deliver|we ensure|we maintain|we focus|we specialize)\b',
                    r'\b(our customers|our clients|our users|our team|our staff|our platform|our technology|our service|our product)\b',
                    r'\b(financial advisor|advisor|wealth management|practice management|client management)\b',
                    r'\b(platform|software|system|tool|solution|application|interface|dashboard)\b'
                ],
                "weight": 0.8,
                "fuzzy_threshold": 70
            }
        },
        business_insights={
            "business_insights": {
                "patterns": [
                    r'\b(advantage|strength|weakness|challenge|opportunity|risk|concern|benefit|problem|issue)\b',
                    r'\b(growth|expansion|market|customer|competition|industry|business|strategy|model|approach|method)\b',
                    r'\b(Practifi|company|firm|organization|enterprise|corporation|business|operation)\b',
                    r'\b(platform|software|system|tool|solution|application|interface|dashboard)\b'
                ],
                "weight": 1.0,
                "fuzzy_threshold": 65
            },
            "technical_insights": {
                "patterns": [
                    r'\b(technology|innovation|proprietary|advanced|sophisticated|unique|technical)\b',
                    r'\b(platform|software|system|process|methodology|approach|solution|capability)\b',
                    r'\b(integration|API|workflow|automation|efficiency|performance|accuracy|reliability)\b'
                ],
                "weight": 0.9,
                "fuzzy_threshold": 70
            }
        },
        topic_synonyms={
            "platform_adoption": [
                "adoption rate", "user adoption", "platform usage", "market penetration",
                "customer adoption", "user uptake", "platform utilization", "market adoption"
            ],
            "user_experience": [
                "UX", "user interface", "ease of use", "usability", "user satisfaction",
                "interface design", "user workflow", "user journey", "user interaction"
            ],
            "feature_effectiveness": [
                "feature performance", "tool effectiveness", "functionality", "feature value",
                "tool performance", "feature utility", "tool usefulness", "feature impact"
            ],
            "integration_capabilities": [
                "system integration", "API integration", "workflow integration", "data integration",
                "third-party integration", "platform connectivity", "system connectivity"
            ]
        },
        industry_keywords=[
            "financial advisor", "wealth management", "practice management", "client management",
            "financial planning", "investment management", "portfolio management", "client relationship",
            "practice technology", "advisor technology", "wealth tech", "fintech"
        ],
        company_specific_terms=[
            "Practifi", "financial advisor platform", "practice management software",
            "wealth management technology", "advisor workflow", "client management system"
        ]
    )
}

def get_company_config(company_name: str = "flexxray") -> CompanyConfig:
    """Get configuration for a specific company."""
    return COMPANY_CONFIGS.get(company_name.lower(), COMPANY_CONFIGS["flexxray"])

def list_available_companies() -> List[str]:
    """List all available company configurations."""
    return list(COMPANY_CONFIGS.keys())

def create_custom_company_config(
    name: str,
    display_name: str,
    transcript_directory: str,
    output_prefix: str,
    key_questions: Dict[str, str],
    question_categories: Dict[str, List[str]],
    **kwargs
) -> CompanyConfig:
    """Create a custom company configuration."""
    
    # Start with default patterns and customize
    base_config = COMPANY_CONFIGS["flexxray"]
    
    custom_config = CompanyConfig(
        name=name,
        display_name=display_name,
        transcript_directory=transcript_directory,
        output_prefix=output_prefix,
        key_questions=key_questions,
        question_categories=question_categories,
        speaker_patterns=kwargs.get("speaker_patterns", base_config.speaker_patterns),
        business_insights=kwargs.get("business_insights", base_config.business_insights),
        topic_synonyms=kwargs.get("topic_synonyms", base_config.topic_synonyms),
        industry_keywords=kwargs.get("industry_keywords", base_config.industry_keywords),
        company_specific_terms=kwargs.get("company_specific_terms", [display_name])
    )
    
    # Add to available configs
    COMPANY_CONFIGS[name.lower()] = custom_config
    return custom_config

def update_company_config(company_name: str, **updates) -> CompanyConfig:
    """Update an existing company configuration."""
    config = get_company_config(company_name)
    
    for key, value in updates.items():
        if hasattr(config, key):
            setattr(config, key, value)
    
    return config

# Example usage for creating a new company
if __name__ == "__main__":
    # Create a new company configuration
    new_company = create_custom_company_config(
        name="techstartup",
        display_name="TechStartup Inc",
        transcript_directory="TechStartup Transcripts",
        output_prefix="TechStartup",
        key_questions={
            "product_market_fit": "How well does TechStartup's product fit the market?",
            "competitive_advantage": "What competitive advantages does TechStartup have?",
            "growth_strategy": "What is TechStartup's growth strategy?"
        },
        question_categories={
            "key_takeaways": ["product_market_fit", "competitive_advantage"],
            "strengths": ["growth_strategy"]
        }
    )
    
    print(f"Available companies: {list_available_companies()}")
    print(f"New company config: {new_company.display_name}")
