# Modular Prompt System for FlexXray Transcript Summarizer

## Overview

The FlexXray Transcript Summarizer now features a **modular prompt system** that centralizes all OpenAI prompts in configurable templates. This system eliminates hardcoded prompts from the codebase, making it easy to customize, version, and maintain prompts without modifying the core application code.

## Key Benefits

✅ **Easy Customization** - Modify prompts without touching Python code  
✅ **Version Control** - Track prompt changes in your prompts.json file  
✅ **Consistent Formatting** - Standardized prompt structure across all features  
✅ **Parameter Management** - Centralized control of OpenAI parameters  
✅ **Validation** - Built-in prompt validation and error checking  
✅ **Backup & Restore** - Export/import prompt configurations  

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Core Code     │    │  PromptConfig    │    │  prompts.json   │
│                 │◄──►│     Class        │◄──►│  (User Config)  │
│ - No hardcoded  │    │                  │    │                 │
│   prompts       │    │ - Template mgmt  │    │ - Customizable  │
│                 │    │ - Parameter mgmt │    │ - Versionable   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Files Overview

| File | Purpose | Description |
|------|---------|-------------|
| `prompt_config.py` | Core Module | Centralized prompt management class |
| `prompts.json` | Configuration | User-customizable prompt templates |
| `prompt_manager.py` | CLI Tool | Interactive prompt management utility |

## Prompt Types Available

### 1. **quote_ranking**
- **Purpose**: Rank quotes by relevance to specific perspectives
- **Use Case**: Selecting the most insightful quotes for analysis
- **Parameters**: model, temperature, max_tokens

### 2. **theme_identification**
- **Purpose**: Identify key themes from quote collections
- **Use Case**: Grouping quotes into meaningful categories
- **Parameters**: model, temperature, max_tokens

### 3. **transcript_analysis**
- **Purpose**: Analyze individual transcripts for specific questions
- **Use Case**: Extracting structured information from interviews
- **Parameters**: model, temperature, top_p, max_tokens

### 4. **company_summary**
- **Purpose**: Generate comprehensive company summary pages
- **Use Case**: Creating executive summaries from interview data
- **Parameters**: model, temperature, max_tokens

### 5. **quote_scoring**
- **Purpose**: Score text chunks for relevance to questions
- **Use Case**: Finding most relevant content for analysis
- **Parameters**: model, temperature, max_tokens

### 6. **cross_transcript_analysis**
- **Purpose**: Identify themes across multiple transcripts
- **Use Case**: Finding patterns across different interviews
- **Parameters**: model, temperature, max_tokens

## Quick Start

### 1. **View Current Prompts**
```bash
python prompt_manager.py
prompt-manager> list
prompt-manager> view quote_ranking
```

### 2. **Customize a Prompt**
```bash
prompt-manager> edit company_summary
# Follow the interactive prompts to modify templates, system messages, or parameters
```

### 3. **Export/Import Configurations**
```bash
prompt-manager> export my_custom_prompts.json
prompt-manager> import backup_prompts.json
```

### 4. **Validate Configuration**
```bash
prompt-manager> validate
```

## Configuration File Structure

The `prompts.json` file contains:

```json
{
  "system_messages": {
    "quote_ranking": "You are an expert analyst...",
    "theme_identification": "You are an expert business analyst..."
  },
  "quote_ranking": {
    "template": "Analyze and rank the following quotes...",
    "parameters": {
      "model": "gpt-4",
      "temperature": 0.3,
      "max_tokens": 2000
    }
  }
}
```

## Template Variables

Each prompt template supports dynamic variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `{perspective_title}` | Title of the perspective being analyzed | "Market Position" |
| `{quotes_list}` | Formatted list of quotes to analyze | "Quote 1: [text]..." |
| `{transcript_text}` | Full transcript content | "[transcript content]" |
| `{section_questions}` | Questions for specific section | "What is the company size?" |

## Customization Examples

### Example 1: Modify Quote Ranking Criteria
```json
{
  "quote_ranking": {
    "template": "Analyze and rank the following quotes for the perspective: {perspective_title}\n\nFocus on:\n- Business impact (1-10)\n- Strategic relevance (1-10)\n- Actionability (1-10)\n\nQuotes: {quotes_list}",
    "parameters": {
      "model": "gpt-4-turbo",
      "temperature": 0.2
    }
  }
}
```

### Example 2: Customize Company Summary Format
```json
{
  "company_summary": {
    "template": "Based on these expert quotes, create a summary with:\n\n1. EXECUTIVE SUMMARY (2-3 sentences)\n2. KEY INSIGHTS (5-7 bullet points)\n3. RISK FACTORS (3-5 items)\n4. OPPORTUNITIES (3-5 items)\n\nQuotes: {quotes_list}",
    "parameters": {
      "temperature": 0.1,
      "max_tokens": 4000
    }
  }
}
```

## Advanced Features

### 1. **Parameter Inheritance**
- Default parameters are automatically applied if not specified
- Easy to override specific parameters while keeping others

### 2. **Template Validation**
- Built-in validation ensures all required variables are present
- Error messages help identify missing template variables

### 3. **Backward Compatibility**
- System automatically falls back to defaults if config is invalid
- No breaking changes to existing functionality

### 4. **Environment-Specific Configs**
- Support for different prompt sets per environment
- Easy switching between development, staging, and production

## Migration from Hardcoded Prompts

The system automatically migrates existing hardcoded prompts:

1. **Before**: Prompts were embedded in Python code
2. **After**: Prompts are loaded from `prompts.json`
3. **Fallback**: If config file is missing, defaults are used

## Best Practices

### 1. **Template Design**
- Use clear, descriptive variable names
- Include specific instructions for output format
- Test templates with various input data

### 2. **Parameter Tuning**
- Start with conservative temperature values (0.1-0.3)
- Adjust max_tokens based on expected output length
- Use appropriate models for different tasks

### 3. **Version Control**
- Commit `prompts.json` to version control
- Use descriptive commit messages for prompt changes
- Consider branching strategies for prompt experimentation

### 4. **Testing**
- Validate prompts before deployment
- Test with edge cases and various input sizes
- Monitor OpenAI API responses for consistency

## Troubleshooting

### Common Issues

**Problem**: "Missing parameter" warnings
**Solution**: Check template variables match the expected format

**Problem**: Prompts not loading
**Solution**: Verify `prompts.json` is valid JSON and accessible

**Problem**: OpenAI errors after prompt changes
**Solution**: Validate prompt templates and check parameter values

### Debug Commands
```bash
prompt-manager> validate          # Check all prompts
prompt-manager> view <type>       # Examine specific prompt
prompt-manager> reset             # Restore defaults if needed
```

## API Reference

### PromptConfig Class Methods

| Method | Description | Parameters |
|--------|-------------|------------|
| `get_system_message(type)` | Get system message for prompt type | `type: str` |
| `get_prompt_template(type)` | Get template for prompt type | `type: str` |
| `get_prompt_parameters(type)` | Get OpenAI parameters | `type: str` |
| `format_prompt(type, **kwargs)` | Format template with variables | `type: str, **kwargs` |
| `update_prompt(type, **kwargs)` | Update prompt configuration | `type: str, **kwargs` |
| `save_config(filename)` | Save configuration to file | `filename: str` |
| `validate_prompt(type)` | Validate prompt configuration | `type: str` |

## Integration Examples

### Python Code Integration
```python
from prompt_config import get_prompt_config

# Get prompt configuration
prompt_config = get_prompt_config()

# Format a prompt
prompt = prompt_config.format_prompt("quote_ranking",
                                   perspective_title="Market Analysis",
                                   quotes_list="Quote 1: [text]...")

# Get OpenAI parameters
params = prompt_config.get_prompt_parameters("quote_ranking")

# Use in OpenAI call
response = client.chat.completions.create(
    model=params.get("model", "gpt-4"),
    messages=[
        {"role": "system", "content": prompt_config.get_system_message("quote_ranking")},
        {"role": "user", "content": prompt}
    ],
    temperature=params.get("temperature", 0.3),
    max_tokens=params.get("max_tokens", 2000)
)
```

## Future Enhancements

- **Prompt Versioning**: Track prompt changes over time
- **A/B Testing**: Compare different prompt versions
- **Performance Metrics**: Track prompt effectiveness
- **Template Library**: Pre-built prompt templates for common use cases
- **Multi-language Support**: Internationalized prompt templates

## Support

For questions or issues with the modular prompt system:

1. Check the validation output: `prompt-manager> validate`
2. Review the configuration file format
3. Test with default prompts: `prompt-manager> reset`
4. Check OpenAI API responses for specific errors

The modular prompt system transforms your FlexXray Transcript Summarizer from a static tool to a **dynamic, customizable platform** that adapts to your specific analysis needs without requiring code changes.
