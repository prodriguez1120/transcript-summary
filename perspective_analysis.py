#!/usr/bin/env python3
"""
Perspective Analysis Module for FlexXray Transcripts

This module handles perspective analysis, OpenAI ranking, and thematic analysis
for the quote analysis tool.
"""

import json
import time
from typing import List, Dict, Any
from openai import OpenAI
from prompt_config import get_prompt_config

class PerspectiveAnalyzer:
    def __init__(self, openai_client: OpenAI):
        """Initialize the perspective analyzer with OpenAI client."""
        self.client = openai_client

    def analyze_perspective_with_quotes(self, perspective_key: str, perspective_data: dict,
                                      all_quotes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze a perspective using available quotes with OpenAI ranking."""
        print(f"Analyzing perspective: {perspective_data['title']}")
        
        # Find relevant quotes for this perspective
        relevant_quotes = self._find_relevant_quotes_for_perspective(
            perspective_key, perspective_data, all_quotes
        )
        
        if not relevant_quotes:
            print(f"No relevant quotes found for {perspective_key}")
            return {
                'perspective_key': perspective_key,
                'title': perspective_data['title'],
                'description': perspective_data['description'],
                'themes': [],
                'total_quotes': 0
            }
        
        # Rank quotes using OpenAI
        ranked_quotes = self._rank_quotes_with_openai(
            perspective_key, perspective_data, relevant_quotes
        )
        
        # Analyze themes
        themes = self._analyze_perspective_thematically(
            perspective_key, perspective_data, ranked_quotes
        )
        
        # Identify cross-transcript themes
        cross_transcript_themes = self._identify_cross_transcript_themes(all_quotes)
        
        return {
            'perspective_key': perspective_key,
            'title': perspective_data['title'],
            'description': perspective_data['description'],
            'themes': themes,
            'cross_transcript_themes': cross_transcript_themes,
            'total_quotes': len(relevant_quotes),
            'ranked_quotes': ranked_quotes
        }

    def _find_relevant_quotes_for_perspective(self, perspective_key: str, perspective_data: dict,
                                            all_quotes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find quotes relevant to a specific perspective."""
        if not all_quotes:
            return []
        
        # Filter to expert quotes only
        expert_quotes = [q for q in all_quotes if q.get('speaker_role') == 'expert']
        
        if not expert_quotes:
            return []
        
        # Get focus areas for this perspective
        focus_areas = perspective_data.get('focus_areas', [])
        
        relevant_quotes = []
        for quote in expert_quotes:
            quote_text = quote.get('text', '').lower()
            
            # Check if quote contains any focus area keywords
            relevance_score = 0
            for focus_area in focus_areas:
                focus_words = focus_area.lower().split()
                for word in focus_words:
                    if word in quote_text:
                        relevance_score += 1
            
            # If quote is relevant enough, include it
            if relevance_score >= 1:
                quote['relevance_score'] = relevance_score
                relevant_quotes.append(quote)
        
        # Sort by relevance score
        relevant_quotes.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        # Limit to top quotes
        max_quotes = 50
        return relevant_quotes[:max_quotes]

    def _rank_quotes_with_openai(self, perspective_key: str, perspective_data: dict,
                                quotes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank quotes using OpenAI for relevance and insight quality."""
        if not quotes:
            return []
        
        print(f"Ranking {len(quotes)} quotes for {perspective_key} using OpenAI...")
        
        # Get prompt configuration
        prompt_config = get_prompt_config()
        
        # Prepare ranking prompt
        ranking_prompt = self._create_ranking_prompt(perspective_key, perspective_data, quotes)
        
        try:
            # Get OpenAI parameters from config
            params = prompt_config.get_prompt_parameters("quote_ranking")
            
            # Call OpenAI for ranking
            response = self.client.chat.completions.create(
                model=params.get("model", "gpt-4"),
                messages=[
                    {"role": "system", "content": prompt_config.get_system_message("quote_ranking")},
                    {"role": "user", "content": ranking_prompt}
                ],
                temperature=params.get("temperature", 0.3),
                max_tokens=params.get("max_tokens", 2000)
            )
            
            # Parse ranking response
            ranked_quotes = self._parse_ranking_response(response.choices[0].message.content, quotes)
            
            print(f"Successfully ranked {len(ranked_quotes)} quotes")
            return ranked_quotes
            
        except Exception as e:
            print(f"Error ranking quotes with OpenAI: {e}")
            # Return quotes with default ranking
            for i, quote in enumerate(quotes):
                quote['openai_rank'] = i + 1
                quote['selection_stage'] = 'openai_failed'
            return quotes

    def _create_ranking_prompt(self, perspective_key: str, perspective_data: dict,
                             quotes: List[Dict[str, Any]]) -> str:
        """Create the prompt for OpenAI quote ranking."""
        prompt_config = get_prompt_config()
        
        # Prepare quotes list for template
        quotes_list = ""
        for i, quote in enumerate(quotes):
            quotes_list += f"\nQuote {i+1}: {quote.get('text', '')[:200]}..."
            if quote.get('transcript_name'):
                quotes_list += f" [From: {quote['transcript_name']}]"
        
        # Format prompt using template
        return prompt_config.format_prompt("quote_ranking",
                                         perspective_title=perspective_data['title'],
                                         perspective_description=perspective_data['description'],
                                         focus_areas=', '.join(perspective_data['focus_areas']),
                                         quotes_list=quotes_list)

    def _parse_ranking_response(self, response_text: str, quotes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse OpenAI's ranking response and apply it to quotes."""
        try:
            # Extract JSON from response
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON array found in response")
            
            json_text = response_text[json_start:json_end]
            rankings = json.loads(json_text)
            
            # Apply rankings to quotes
            for ranking in rankings:
                quote_index = ranking.get('quote_index', 0) - 1  # Convert to 0-based
                if 0 <= quote_index < len(quotes):
                    quote = quotes[quote_index]
                    quote['openai_rank'] = ranking.get('relevance_score', 0)
                    quote['relevance_explanation'] = ranking.get('relevance_explanation', '')
                    quote['key_insight'] = ranking.get('key_insight', '')
                    quote['selection_stage'] = 'openai_ranked'
            
            # Sort by OpenAI rank
            quotes.sort(key=lambda x: x.get('openai_rank', 0), reverse=True)
            
            return quotes
            
        except Exception as e:
            print(f"Error parsing ranking response: {e}")
            # Return quotes with default ranking
            for i, quote in enumerate(quotes):
                quote['openai_rank'] = 0
                quote['selection_stage'] = 'parsing_failed'
            return quotes

    def _analyze_perspective_thematically(self, perspective_key: str, perspective_data: dict,
                                        quotes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze quotes thematically within a perspective."""
        if not quotes:
            return []
        
        print(f"Analyzing themes for {perspective_key}...")
        
        # Group quotes by themes using OpenAI
        themes = self._identify_themes_with_openai(perspective_key, perspective_data, quotes)
        
        # Select quotes for each theme
        for theme in themes:
            theme_quotes = self._select_quotes_for_theme(theme['name'], quotes, theme.get('max_quotes', 3))
            theme['quotes'] = theme_quotes
        
        return themes

    def _identify_themes_with_openai(self, perspective_key: str, perspective_data: dict,
                                   quotes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify themes using OpenAI analysis."""
        if not quotes:
            return []
        
        # Get prompt configuration
        prompt_config = get_prompt_config()
        
        # Create theme identification prompt
        quotes_list = ""
        for i, quote in enumerate(quotes[:20]):  # Limit to first 20 quotes for theme analysis
            quotes_list += f"\nQuote {i+1}: {quote.get('text', '')[:150]}..."
        
        prompt = prompt_config.format_prompt("theme_identification",
                                           perspective_title=perspective_data['title'],
                                           quotes_list=quotes_list)
        
        try:
            # Get OpenAI parameters from config
            params = prompt_config.get_prompt_parameters("theme_identification")
            
            response = self.client.chat.completions.create(
                model=params.get("model", "gpt-4"),
                messages=[
                    {"role": "system", "content": prompt_config.get_system_message("theme_identification")},
                    {"role": "user", "content": prompt}
                ],
                temperature=params.get("temperature", 0.3),
                max_tokens=params.get("max_tokens", 1500)
            )
            
            # Parse themes
            themes = self._parse_themes_response(response.choices[0].message.content)
            return themes
            
        except Exception as e:
            print(f"Error identifying themes with OpenAI: {e}")
            # Return default themes
            return [
                {
                    'name': 'Key Insights',
                    'description': 'Primary insights from the perspective',
                    'key_insights': ['Analysis completed'],
                    'max_quotes': 3
                }
            ]

    def _parse_themes_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse OpenAI's themes response."""
        try:
            # Extract JSON from response
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON array found in response")
            
            json_text = response_text[json_start:json_end]
            themes = json.loads(json_text)
            
            # Validate themes
            valid_themes = []
            for theme in themes:
                if isinstance(theme, dict) and 'name' in theme:
                    valid_themes.append({
                        'name': theme.get('name', 'Unknown Theme'),
                        'description': theme.get('description', ''),
                        'key_insights': theme.get('key_insights', []),
                        'max_quotes': theme.get('max_quotes', 3)
                    })
            
            return valid_themes
            
        except Exception as e:
            print(f"Error parsing themes response: {e}")
            return []

    def _select_quotes_for_theme(self, theme: str, quotes: List[Dict[str, Any]],
                                max_quotes: int) -> List[Dict[str, Any]]:
        """Select the best quotes for a specific theme."""
        if not quotes:
            return []
        
        # Filter quotes that might be relevant to the theme
        theme_keywords = theme.lower().split()
        relevant_quotes = []
        
        for quote in quotes:
            quote_text = quote.get('text', '').lower()
            relevance_score = 0
            
            for keyword in theme_keywords:
                if keyword in quote_text:
                    relevance_score += 1
            
            if relevance_score > 0:
                quote['theme_relevance'] = relevance_score
                relevant_quotes.append(quote)
        
        # Sort by theme relevance and OpenAI rank
        relevant_quotes.sort(key=lambda x: (x.get('theme_relevance', 0), x.get('openai_rank', 0)), reverse=True)
        
        # Return top quotes
        return relevant_quotes[:max_quotes]

    def _identify_cross_transcript_themes(self, all_quotes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify themes that appear across multiple transcripts."""
        if not all_quotes:
            return []
        
        print("Identifying cross-transcript themes...")
        
        # Group quotes by transcript
        transcript_quotes = {}
        for quote in all_quotes:
            transcript = quote.get('transcript_name', 'Unknown')
            if transcript not in transcript_quotes:
                transcript_quotes[transcript] = []
            transcript_quotes[transcript].append(quote)
        
        # Find common themes across transcripts
        cross_transcript_themes = self._find_common_themes_across_transcripts(transcript_quotes)
        
        return cross_transcript_themes

    def _find_common_themes_across_transcripts(self, transcript_quotes: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Find themes that appear in multiple transcripts."""
        if len(transcript_quotes) < 2:
            return []
        
        # Get prompt configuration
        prompt_config = get_prompt_config()
        
        # Create prompt for cross-transcript analysis
        transcripts_data = ""
        for transcript_name, quotes in transcript_quotes.items():
            transcripts_data += f"Transcript: {transcript_name}\n"
            for i, quote in enumerate(quotes[:5]):  # Limit to 5 quotes per transcript
                transcripts_data += f"  Quote {i+1}: {quote.get('text', '')[:100]}...\n"
            transcripts_data += "\n"
        
        prompt = prompt_config.format_prompt("cross_transcript_analysis",
                                           transcripts_data=transcripts_data)
        
        try:
            # Get OpenAI parameters from config
            params = prompt_config.get_prompt_parameters("cross_transcript_analysis")
            
            response = self.client.chat.completions.create(
                model=params.get("model", "gpt-4"),
                messages=[
                    {"role": "system", "content": prompt_config.get_system_message("cross_transcript_analysis")},
                    {"role": "user", "content": prompt}
                ],
                temperature=params.get("temperature", 0.3),
                max_tokens=params.get("max_tokens", 1500)
            )
            
            # Parse cross-transcript themes
            themes = self._parse_cross_transcript_themes(response.choices[0].message.content)
            return themes
            
        except Exception as e:
            print(f"Error identifying cross-transcript themes: {e}")
            return []

    def _parse_cross_transcript_themes(self, theme_text: str) -> List[Dict[str, Any]]:
        """Parse cross-transcript themes response."""
        try:
            # Extract JSON from response
            json_start = theme_text.find('[')
            json_end = theme_text.rfind(']') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON array found in response")
            
            json_text = theme_text[json_start:json_end]
            themes = json.loads(json_text)
            
            # Validate and clean themes
            valid_themes = []
            for theme in themes:
                if isinstance(theme, dict) and 'theme_name' in theme:
                    valid_themes.append({
                        'theme_name': theme.get('theme_name', 'Unknown Theme'),
                        'description': theme.get('description', ''),
                        'transcripts_covered': theme.get('transcripts_covered', []),
                        'key_insights': theme.get('key_insights', []),
                        'consistency_level': theme.get('consistency_level', 'medium')
                    })
            
            return valid_themes
            
        except Exception as e:
            print(f"Error parsing cross-transcript themes: {e}")
            return []
