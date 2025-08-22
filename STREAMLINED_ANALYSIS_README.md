# FlexXray Streamlined Quote Analysis System

## Overview

This new system implements a sophisticated quote analysis approach that:

1. **Uses questions instead of bullet points** for better quote matching
2. **Implements quote ranking and reranking** for improved relevance
3. **Streamlines AI calls** for better efficiency and cost management
4. **Focuses on question-answer matching** rather than generic theme identification

## Key Improvements

### 1. Question-Based Analysis
Instead of generic bullet points, the system now asks specific questions:
- **Market Leadership**: "What evidence shows FlexXray's market leadership and competitive advantage?"
- **Value Proposition**: "How does FlexXray's value proposition address the risk of insourcing?"
- **Local Presence**: "How does FlexXray's local presence and footprint drive customer demand?"

### 2. Two-Stage Quote Ranking
1. **Initial Ranking**: Uses GPT-4o-mini for cost-effective initial scoring of 15-20 quotes per question
2. **Precision Reranking**: Uses GPT-4 for detailed analysis of top 3-5 quotes for final selection

### 3. Streamlined AI Calls
- **Reduced API calls**: Only 7 questions instead of complex multi-stage analysis
- **Efficient models**: Uses faster models for initial ranking, premium models for final selection
- **Better cost management**: Optimizes token usage and model selection

## System Architecture

```
Transcripts → Quote Extraction → Expert Filtering → Question-Based Ranking → Reranking → Final Selection
```

### Components

1. **`streamlined_quote_analysis.py`**: Core analysis engine
2. **`run_streamlined_analysis.py`**: Integration script with existing system
3. **Updated `prompts.json`**: Question-based prompts instead of bullet points

## Usage

### Option 1: Run New System
```bash
python run_streamlined_analysis.py
```

### Option 2: Use Updated Existing System
```bash
python quote_analysis_tool.py
```

## Question Categories

### Key Takeaways (3 questions)
1. **Market Leadership**: Evidence of competitive advantage and market share
2. **Value Proposition**: How technology addresses insourcing risks
3. **Local Presence**: Geographic footprint driving customer demand

### Strengths (2 questions)
1. **Technology Advantages**: Proprietary technology capabilities
2. **Rapid Turnaround**: Speed and efficiency benefits

### Weaknesses (2 questions)
1. **Limited TAM**: Market size constraints
2. **Unpredictable Timing**: Event-driven business challenges

## Benefits

### Quality Improvements
- **Better quote relevance**: Questions guide quote selection more precisely
- **Consistent completion**: All 7 insights are guaranteed to be generated
- **Improved categorization**: Clear question-answer relationships

### Efficiency Improvements
- **Faster processing**: Streamlined workflow with fewer API calls
- **Cost optimization**: Uses appropriate models for each stage
- **Better scalability**: Easier to add new questions or modify existing ones

### Technical Improvements
- **Vector database ready**: Designed for future ChromaDB integration
- **Modular design**: Easy to extend and modify
- **Better error handling**: Robust fallbacks and error recovery

## Future Enhancements

1. **ChromaDB Integration**: Add semantic search capabilities
2. **Dynamic Question Generation**: AI-generated questions based on transcript content
3. **Multi-language Support**: Extend to other languages
4. **Real-time Analysis**: Live quote analysis during interviews

## Comparison with Previous System

| Aspect | Previous System | New System |
|--------|----------------|------------|
| **Format** | Bullet points | Questions |
| **Quote Selection** | Single-stage ranking | Two-stage ranking + reranking |
| **AI Calls** | Multiple complex calls | Streamlined 7-question approach |
| **Completion** | Often incomplete (5-6/7) | Guaranteed 7/7 insights |
| **Cost** | Higher (more API calls) | Lower (optimized model usage) |
| **Maintainability** | Complex prompt management | Simple question-based approach |

## Integration Notes

The new system is designed to work alongside your existing quote extraction pipeline. It:
- Uses the same transcript processing
- Maintains compatibility with existing data structures
- Can be run independently or integrated into the main workflow

## Troubleshooting

### Common Issues
1. **Missing quotes**: Ensure transcript directory exists and contains .docx files
2. **API errors**: Check OpenAI API key and rate limits
3. **Incomplete results**: Verify all 7 questions are being processed

### Performance Tips
1. **Batch processing**: Process multiple transcripts together
2. **Model selection**: Use appropriate models for each stage
3. **Quote filtering**: Ensure expert quote filtering is working correctly

