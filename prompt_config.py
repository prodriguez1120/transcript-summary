#!/usr/bin/env python3
"""
Prompt Configuration Module for FlexXray Transcript Summarizer

This module centralizes all OpenAI prompts in a modular, configurable system.
Prompts can be easily modified, versioned, and customized without changing the core code.
"""

from typing import Dict, Any, List
import json
import os


class PromptConfig:
    """Centralized prompt configuration for all OpenAI interactions."""

    def __init__(self, config_file: str = None):
        """Initialize prompt configuration."""
        self.config_file = config_file or "prompts.json"
        self.prompts = self._load_prompts()

    def _load_prompts(self) -> Dict[str, Any]:
        """Load prompts from configuration file or use defaults."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(
                    f"Warning: Could not load prompt config from {self.config_file}: {e}"
                )
                print("Using default prompts.")

        return self._get_default_prompts()

    def _get_default_prompts(self) -> Dict[str, Any]:
        """Get default prompt configurations."""
        return {
            "system_messages": {
                "quote_ranking": "You are an expert analyst evaluating quotes for business insights.",
                "theme_identification": "You are an expert business analyst identifying key themes from interview quotes.",
                "transcript_analysis": "You are a professional analyst extracting structured information from call transcripts. Provide clear, concise answers based only on the transcript content. Include 1-2 relevant quotes per answer where helpful to support your analysis.",
                "company_summary": "You are an expert business intelligence analyst. Your task is to process a transcript and generate a structured summary supported by direct quotes.",
                "quote_scoring": "You are an expert analyst scoring text chunks for relevance to specific questions.",
            },
            "quote_ranking": {
                "template": """Analyze and rank the following quotes for the perspective: {perspective_title}

Perspective Description: {perspective_description}
Focus Areas: {focus_areas}

For each quote, provide:
1. A relevance score (1-10, where 10 is most relevant)
2. A brief explanation of why it's relevant
3. The quote's key insight

Quotes to analyze:
{quotes_list}

Please respond with a JSON array of objects, each containing:
{{
  "quote_index": <1-based index>,
  "relevance_score": <1-10>,
  "relevance_explanation": "<brief explanation>",
  "key_insight": "<main insight from quote>"
}}

Rank the quotes from most relevant (highest score) to least relevant (lowest score).""",
                "parameters": {
                    "model": "gpt-4",
                    "temperature": 0.3,
                    "max_tokens": 2000,
                },
            },
            "theme_identification": {
                "template": """Analyze the following quotes for the perspective: {perspective_title}

Identify 3-5 key themes that emerge from these quotes. Each theme should represent a distinct aspect or insight.

Quotes:
{quotes_list}

Please respond with a JSON array of theme objects:
[
  {{
    "name": "<theme name>",
    "description": "<brief description of the theme>",
    "key_insights": ["<insight 1>", "<insight 2>"],
    "max_quotes": <number of quotes to select for this theme>
  }}
]

Focus on themes that provide actionable business insights.""",
                "parameters": {
                    "model": "gpt-4",
                    "temperature": 0.3,
                    "max_tokens": 1500,
                },
            },
            "transcript_analysis": {
                "template": """You are analyzing a transcript from a call conversation. Please extract information from the following transcript and answer the questions below.

{context_section}TRANSCRIPT:
{transcript_text}

Please provide detailed answers to the following questions based ONLY on the information in this transcript. If information is not available in the transcript, clearly state "Information not available in transcript."

IMPORTANT: Only use information from this specific transcript. Do not make assumptions or use external knowledge.

QUOTE REQUIREMENTS:
- For each answer, include 1-2 relevant quotes from the transcript where helpful
- Quotes should be direct statements from the interviewee that support your answer
- Keep quotes concise (1-2 sentences max)
- Format quotes as: "Quote: [exact quote from transcript]"
- Only include quotes that add value to understanding the answer
- If no relevant quotes are available, omit the quote section

{section_title}:
{section_questions}""",
                "parameters": {
                    "model": "gpt-4o",
                    "temperature": 0.3,
                    "top_p": 1.0,
                    "max_tokens": 4000,
                },
            },
            "company_summary": {
                "template": """You are an expert business intelligence analyst. Your task is to process a transcript and generate a structured summary supported by direct quotes.

**Input:** A single FlexXray interview transcript, which is a conversation between an interviewer and one or more industry experts.

**Instructions:**
1. **Analyze the transcript** to identify key themes related to business performance.
2. **Extract quotes** that directly support the following pre-defined themes:
   * **Key Takeaways:**
       * "Clear market leadership"
       * "Strong Value Prop Despite Potential Risk of Insourcing"
       * "Local Presence drives Customer Demand"
   * **Strengths:**
       * "proprietary technology"
       * "rapid turn-around times"
   * **Weaknesses:**
       * "limited addressable market"
       * "unpredictable event timing"
3. **Quote Requirements:**
   * For each **Key Takeaway**, find **3-4 distinct quotes**.
   * For each **Strength** and **Weakness**, find **2-3 distinct quotes**.
   * The quotes must be from the **expert(s)**, not the interviewer. Use your speaker role filtering to ensure this.
   * The quotes should be concise and directly relevant to the theme. Prioritize clear, direct statements over conversational filler.
4. **Structured Output:** Format the output as a JSON object with the following structure:
   ```json
   {{
     "key_takeaways": [
       {{
         "theme": "Clear market leadership",
         "quotes": [
           {{ "quote": "...", "speaker": "...", "document": "..." }},
           {{ "quote": "...", "speaker": "...", "document": "..." }}
         ]
       }},
       {{
         "theme": "Strong Value Prop Despite Potential Risk of Insourcing",
         "quotes": [
           {{ "quote": "...", "speaker": "...", "document": "..." }},
           {{ "quote": "...", "speaker": "...", "document": "..." }}
         ]
       }},
       {{
         "theme": "Local Presence drives Customer Demand",
         "quotes": [
           {{ "quote": "...", "speaker": "...", "document": "..." }},
           {{ "quote": "...", "speaker": "...", "document": "..." }}
         ]
       }}
     ],
     "strengths": [
       {{
         "theme": "proprietary technology",
         "quotes": [
           {{ "quote": "...", "speaker": "...", "document": "..." }}
         ]
       }},
       {{
         "theme": "rapid turn-around times",
         "quotes": [
           {{ "quote": "...", "speaker": "...", "document": "..." }}
         ]
       }}
     ],
     "weaknesses": [
       {{
         "theme": "limited addressable market",
         "quotes": [
           {{ "quote": "...", "speaker": "...", "document": "..." }}
         ]
       }},
       {{
         "theme": "unpredictable event timing",
         "quotes": [
           {{ "quote": "...", "speaker": "...", "document": "..." }}
         ]
       }}
     ]
   }}
   ```
5. **Attribution:** For each quote, you must provide the following:
   * `"quote"`: The exact text of the quote.
   * `"speaker"`: The name of the person who said the quote.
   * `"document"`: The name of the transcript file you are processing. (Your program will handle this part, but the prompt ensures the AI understands the need for this data point.)

**Note:** If a theme is not supported by the transcript, return an empty list of quotes for that theme. Do not invent quotes or themes.

**Transcript Content:**
{quotes_list}

Please respond with ONLY the JSON object as specified above. Do not include any additional text, explanations, or formatting outside the JSON structure.""",
                "parameters": {
                    "model": "gpt-4",
                    "temperature": 0.3,
                    "max_tokens": 3000,
                },
            },
            "quote_scoring": {
                "template": """Score the relevance of the following text chunks to the question: "{question}"

Question Context: {question_context}

For each chunk, provide a relevance score from 0-10 where:
- 10 = Highly relevant, directly answers or strongly supports the question
- 7-9 = Relevant, provides useful context or partial answer
- 4-6 = Somewhat relevant, may contain related information
- 1-3 = Minimally relevant, only tangentially related
- 0 = Not relevant, unrelated to the question

Text Chunks to Score:
{chunks_list}

Please respond with a JSON array of objects:
[
  {{
    "chunk_index": <0-based index>,
    "relevance_score": <0-10>,
    "relevance_explanation": "<brief explanation of score>"
  }}
]""",
                "parameters": {
                    "model": "gpt-4o",
                    "temperature": 0.2,
                    "max_tokens": 1500,
                },
            },
        }

    def get_system_message(self, prompt_type: str) -> str:
        """Get system message for a specific prompt type."""
        return self.prompts.get("system_messages", {}).get(prompt_type, "")

    def get_prompt_template(self, prompt_type: str) -> str:
        """Get prompt template for a specific type."""
        return self.prompts.get(prompt_type, {}).get("template", "")

    def get_prompt_parameters(self, prompt_type: str) -> Dict[str, Any]:
        """Get OpenAI parameters for a specific prompt type."""
        return self.prompts.get(prompt_type, {}).get("parameters", {})

    def format_prompt(self, prompt_type: str, **kwargs) -> str:
        """Format a prompt template with the given parameters."""
        template = self.get_prompt_template(prompt_type)
        try:
            return template.format(**kwargs)
        except KeyError as e:
            print(f"Warning: Missing parameter {e} for prompt type {prompt_type}")
            return template

    def save_config(self, output_file: str = None) -> bool:
        """Save current prompt configuration to file."""
        output_file = output_file or self.config_file
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(self.prompts, f, indent=2, ensure_ascii=False)
            print(f"Prompt configuration saved to: {output_file}")
            return True
        except Exception as e:
            print(f"Error saving prompt configuration: {e}")
            return False

    def update_prompt(
        self,
        prompt_type: str,
        template: str = None,
        system_message: str = None,
        parameters: Dict[str, Any] = None,
    ) -> bool:
        """Update a specific prompt configuration."""
        if prompt_type not in self.prompts:
            self.prompts[prompt_type] = {}

        if template is not None:
            self.prompts[prompt_type]["template"] = template

        if system_message is not None:
            if "system_messages" not in self.prompts:
                self.prompts["system_messages"] = {}
            self.prompts["system_messages"][prompt_type] = system_message

        if parameters is not None:
            self.prompts[prompt_type]["parameters"] = parameters

        return True

    def get_all_prompt_types(self) -> List[str]:
        """Get list of all available prompt types."""
        return [key for key in self.prompts.keys() if key != "system_messages"]

    def validate_prompt(self, prompt_type: str) -> bool:
        """Validate that a prompt type has all required components."""
        if prompt_type not in self.prompts:
            return False

        prompt_config = self.prompts[prompt_type]
        required_fields = ["template"]

        return all(field in prompt_config for field in required_fields)


# Global prompt configuration instance
prompt_config = PromptConfig()


def get_prompt_config() -> PromptConfig:
    """Get the global prompt configuration instance."""
    return prompt_config
