# Quote Limit Configuration and Token Usage

## Overview
The quote analysis tool now includes configurable limits for the number of quotes processed in OpenAI analysis, along with token usage estimation and logging to help manage API costs.

## Environment Variables

### Quote Processing Limits
- `MAX_QUOTES_FOR_ANALYSIS`: Maximum number of quotes to send to OpenAI (default: 30)
- `MAX_TOKENS_PER_QUOTE`: Estimated tokens per quote for cost calculation (default: 150)

### OpenAI Configuration
- `OPENAI_MODEL_FOR_SUMMARY`: Model to use for summary generation (default: gpt-4)
- `ENABLE_TOKEN_LOGGING`: Enable detailed token usage logging (default: true)

## Example .env Configuration
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Quote Analysis Configuration
MAX_QUOTES_FOR_ANALYSIS=30
MAX_TOKENS_PER_QUOTE=150
OPENAI_MODEL_FOR_SUMMARY=gpt-4
ENABLE_TOKEN_LOGGING=true

# Debug Mode
DEBUG=false
```

## Token Usage Estimation

The system automatically estimates token usage before processing:

- **Base Prompt Tokens**: ~800 tokens for the company summary prompt
- **Quote Tokens**: Number of quotes × MAX_TOKENS_PER_QUOTE
- **Total Tokens**: Base + Quote tokens
- **Cost Estimation**: Based on GPT-4 pricing ($0.03/1K input, $0.06/1K output)

## Benefits

1. **Cost Control**: Limit the number of quotes to prevent excessive API costs
2. **Token Management**: Avoid hitting OpenAI token limits
3. **Configurable**: Adjust limits based on your needs and budget
4. **Transparency**: See estimated costs before processing
5. **Fail Fast**: System validates configuration before starting expensive operations

## Recommendations

- **Small Transcripts** (< 10 quotes): Use 20-30 quotes
- **Medium Transcripts** (10-30 quotes): Use 30-40 quotes  
- **Large Transcripts** (> 30 quotes): Use 40-50 quotes (monitor costs)
- **Budget Conscious**: Start with 20-25 quotes and adjust based on results

## Monitoring

The system logs:
- Configuration settings at startup
- Token usage estimates before processing
- Warnings when approaching token limits
- Actual quote counts processed
