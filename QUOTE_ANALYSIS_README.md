# FlexXray Quote Analysis Tool

A standalone tool that extracts quotes from transcript documents and creates three key summary perspectives with supporting quotes, plus strengths and weaknesses buckets.

## Overview

This tool is designed to work alongside your existing FlexXray Transcript Summarizer platform. It focuses specifically on:

1. **Quote Extraction**: Intelligently extracts meaningful quotes from transcript documents
2. **Sentiment Analysis**: Categorizes quotes into strengths, weaknesses, and neutral categories
3. **Perspective Analysis**: Creates 3 key business perspectives with supporting evidence
4. **Output Generation**: Produces structured reports in multiple formats

## Key Features

### Three Key Perspectives
- **Business Model & Market Position**: How FlexXray operates, serves customers, and competes
- **Growth Potential & Market Opportunity**: Expansion opportunities, market trends, and future prospects  
- **Risk Factors & Challenges**: Key risks, challenges, and areas of concern

### Quote Categorization
- **Strengths Bucket**: Positive aspects, advantages, and strengths of FlexXray
- **Weaknesses Bucket**: Negative aspects, concerns, and areas for improvement
- **Neutral Bucket**: Factual information without clear positive/negative sentiment

### Output Formats
- JSON data file for programmatic access
- Formatted text file for easy reading
- Word document with professional formatting

## Installation & Setup

### Prerequisites
- Python 3.8+
- OpenAI API key
- Existing FlexXray Transcript Summarizer setup (optional, for vector database access)

### Dependencies
All required packages are already installed in your environment:
- `openai` - For AI-powered analysis
- `python-docx` - For Word document processing
- `chromadb` - For vector database access (optional)
- `python-dotenv` - For environment variable management

### Environment Setup
1. Ensure your OpenAI API key is set:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
   
   Or create a `.env` file in your project directory:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

## Usage

### Quick Start

Run the main tool directly:
```bash
python quote_analysis_tool.py
```

The tool will automatically:
1. Look for the "FlexXray Transcripts" directory
2. Process all .docx files in that directory
3. Extract and analyze quotes
4. Generate output files

### Programmatic Usage

```python
from quote_analysis_tool import QuoteAnalysisTool

# Initialize the tool
analyzer = QuoteAnalysisTool()

# Process transcripts
results = analyzer.process_transcripts_for_quotes("FlexXray Transcripts")

# Save results
analyzer.save_quote_analysis(results)
analyzer.export_quote_analysis_to_text(results)
analyzer.export_quote_analysis_to_word(results)
```

### Demo Scripts

Run the demo suite to see examples:
```bash
python quote_analysis_demo.py
```

This will run:
- Basic usage demonstration
- Custom perspectives configuration
- Single transcript analysis

## Customization

### Modifying Key Perspectives

You can customize the three key perspectives by modifying the `key_perspectives` attribute:

```python
analyzer = QuoteAnalysisTool()

# Customize perspectives
analyzer.key_perspectives = {
    "market_analysis": {
        "title": "Market Analysis & Competitive Landscape",
        "description": "Understanding FlexXray's market position",
        "focus_areas": ["market share", "competition", "competitive advantage"]
    },
    "operational_excellence": {
        "title": "Operational Excellence & Efficiency", 
        "description": "FlexXray's operational capabilities",
        "focus_areas": ["operations", "efficiency", "quality"]
    },
    "customer_satisfaction": {
        "title": "Customer Satisfaction & Relationships",
        "description": "Customer experience and relationships",
        "focus_areas": ["customer satisfaction", "relationships", "service quality"]
    }
}
```

### Adjusting Quote Parameters

Modify quote extraction parameters:

```python
analyzer = QuoteAnalysisTool()

# Adjust quote length limits
analyzer.min_quote_length = 25      # Minimum quote length
analyzer.max_quote_length = 250     # Maximum quote length
analyzer.max_quotes_per_category = 8  # Max quotes per category
```

## Output Files

**All output files are now automatically saved to the `Outputs/` folder** for better organization.

The tool generates three main output files:

### 1. JSON Data File (`Outputs/FlexXray_quote_analysis.json`)
- Complete structured data
- All quotes with metadata
- Categorization results
- Perspective analyses
- Programmatic access to all data

### 2. Text Report (`Outputs/FlexXray_quote_analysis.txt`)
- Human-readable format
- Key insights and summaries
- Supporting quotes for each perspective
- Strengths and weaknesses buckets

### 3. Word Document (`Outputs/FlexXray_quote_analysis.docx`)
- Professional formatting
- Structured sections
- Easy to share and present
- Formatted quotes and insights

### Output Directory Configuration

The project now uses a centralized configuration system (`config.py`) that automatically directs all outputs to the `Outputs/` folder. This includes:

- Quote analysis files
- Transcript analysis files
- Company summary pages
- All other generated reports

To change the output directory, simply modify the `OUTPUT_DIR` variable in `config.py`.

## Architecture

### Quote Extraction Process
1. **Text Extraction**: Parse Word documents to extract text content
2. **Sentence Segmentation**: Split text into meaningful sentences
3. **Insight Detection**: Identify sentences containing business insights
4. **Quote Formation**: Create structured quote objects with metadata

### Sentiment Analysis
1. **Batch Processing**: Process quotes in batches to avoid rate limiting
2. **AI Classification**: Use OpenAI GPT-4 to categorize quotes
3. **Category Assignment**: Assign quotes to strengths, weaknesses, or neutral
4. **Quality Control**: Handle API errors gracefully

### Perspective Analysis
1. **Relevance Scoring**: Score quotes based on perspective focus areas
2. **Quote Selection**: Select most relevant quotes for each perspective
3. **AI Synthesis**: Generate insights and summaries using OpenAI
4. **Structured Output**: Format results for easy consumption

## Integration with Existing Platform

This tool is designed to work alongside your existing FlexXray Transcript Summarizer:

- **Shared Infrastructure**: Uses the same ChromaDB vector database
- **Complementary Analysis**: Focuses on quotes while the main tool handles comprehensive analysis
- **No Code Changes**: Doesn't modify any existing functionality
- **Enhanced Insights**: Provides quote-focused perspective that complements the main analysis

## Performance Considerations

- **Rate Limiting**: Built-in delays to respect OpenAI API limits
- **Batch Processing**: Processes quotes in batches for efficiency
- **Error Handling**: Graceful fallbacks when API calls fail
- **Memory Management**: Processes transcripts sequentially to manage memory usage

## Troubleshooting

### Common Issues

1. **API Key Not Set**
   - Ensure `OPENAI_API_KEY` environment variable is set
   - Check that the API key is valid and has sufficient credits

2. **No Transcripts Found**
   - Verify the "FlexXray Transcripts" directory exists
   - Ensure it contains .docx files

3. **ChromaDB Errors**
   - The tool will work without ChromaDB (with limited functionality)
   - Check that the `./chroma_db` directory is accessible

4. **Memory Issues with Large Transcripts**
   - The tool processes transcripts sequentially to manage memory
   - Consider processing smaller batches if memory becomes an issue

### Debug Mode

Enable verbose logging by modifying the tool:

```python
# Add debug prints
print(f"Processing quote: {quote_data}")
print(f"API response: {response_text}")
```

## Future Enhancements

Potential improvements for future versions:

- **Advanced Sentiment Analysis**: More nuanced sentiment scoring
- **Quote Clustering**: Group similar quotes by theme
- **Interactive Dashboard**: Web-based interface for exploring results
- **Export Formats**: Additional output formats (Excel, PowerPoint)
- **Real-time Processing**: Stream processing for large transcript volumes
- **Custom Models**: Support for custom OpenAI fine-tuned models

## Support

This tool is part of the broader FlexXray Transcript Summarizer platform. For questions or issues:

1. Check the existing documentation for the main platform
2. Review the demo scripts for usage examples
3. Examine the source code for implementation details
4. Test with a small subset of transcripts first

## License

This tool follows the same license terms as your existing FlexXray Transcript Summarizer platform.
