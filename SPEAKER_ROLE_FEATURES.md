# Speaker Role Identification & Context Preservation Features

## Overview

The FlexXray Quote Analysis Tool now includes advanced speaker role identification and filtering capabilities **with context preservation** to ensure that when you pull quotes, you're focused on what the **experts** said while maintaining the important context of what questions they were answering.

## Key Features

### 1. Automatic Speaker Role Identification

The tool automatically identifies whether each quote comes from:
- **Expert** - The person being interviewed (e.g., industry professional, company executive)
- **Interviewer** - The person conducting the interview (e.g., researcher, analyst)

### 2. Smart Pattern Recognition

The system uses sophisticated pattern matching to identify speaker roles:

#### Interviewer Patterns (automatically filtered out):
- Explicit markers: `Interviewer:`, `Q:`, `Question:`, `I:`
- Question starters: `Can you`, `Could you`, `What do you think about`
- Transitional phrases: `So`, `Well`, `Now`, `Right`, `Okay`
- Acknowledgment phrases: `I see`, `That's interesting`, `That makes sense`
- Interviewer directives: `Let me ask`, `Let me follow up`
- Question words: `When`, `Where`, `Why`, `How`, `What`, `Which`, `Who`
- Closing phrases: `Thank you`, `Thanks`, `Great conversation`

#### Expert Patterns (automatically included):
- First-person insights: `I think`, `We believe`, `Our company has`
- Company statements: `FlexXray provides`, `We offer`, `Our service`
- Service descriptions: `Our technology`, `The equipment`, `This process`
- Customer insights: `Customers say`, `Clients report`, `Users need`
- Business insights: `advantage`, `strength`, `challenge`, `opportunity`
- Technical terms: `technology`, `innovation`, `quality`, `efficiency`

### 3. Automatic Filtering with Context Preservation

- **By default**, all analysis focuses on **expert quotes only**
- Interviewer quotes are automatically filtered out during processing
- **BUT** - relevant interviewer context (questions, prompts) is preserved and linked to expert responses
- This ensures your insights come from industry experts while maintaining the context of what they were responding to

### 4. Enhanced ChromaDB Storage with Context

When quotes are stored in the vector database, they include:
- `speaker_role`: "expert" or "interviewer"
- `interviewer_context`: Array of relevant interviewer questions/statements that preceded the expert response
- `has_context`: Boolean indicating if interviewer context is available
- `context_count`: Number of context sentences preserved
- All existing metadata (transcript name, position, timestamp, etc.)
- This enables advanced filtering during semantic search while preserving conversational context

### 5. Flexible Search & Filtering

#### New Methods Available:

```python
# Get only expert quotes
expert_quotes = analyzer.get_expert_quotes_only(all_quotes)

# Get quotes by specific speaker role
expert_quotes = analyzer.get_quotes_by_speaker_role(quotes, "expert")
interviewer_quotes = analyzer.get_quotes_by_speaker_role(quotes, "interviewer")

# Search with speaker role filter
expert_results = analyzer.search_quotes_with_speaker_filter(
    query="pricing model", 
    speaker_role="expert"
)

# Get speaker role statistics
stats = analyzer.get_speaker_role_statistics(quotes)
print(f"Expert quotes: {stats['expert_quotes']} ({stats['expert_percentage']:.1f}%)")

# Get quotes with preserved context
quotes_with_context = analyzer.get_quotes_with_context(all_quotes)

# Format a quote with its context for display
formatted_quote = analyzer.format_quote_with_context(quote_with_context)
print(formatted_quote)
# Output:
# Q: What's your assessment of FlexXray's pricing model?
# 
# Expert: "We've seen significant cost savings with their approach."
```

## How It Works

### 1. During Quote Extraction with Context Capture

```python
def extract_quotes_from_text(self, text: str, transcript_name: str):
    # Track recent interviewer context
    recent_interviewer_context = []
    
    for sentence in sentences:
        speaker_role = self._identify_speaker_role(sentence)
        
        # Store interviewer sentences as potential context
        if speaker_role == "interviewer":
            recent_interviewer_context.append({
                "sentence": sentence,
                "is_question": self._is_question(sentence)
            })
            continue  # Skip interviewer quotes from analysis
        
        # For expert quotes, find relevant context
        relevant_context = self._find_relevant_context(sentence, recent_interviewer_context)
        
        quote_data = {
            "quote": clean_sentence,
            "speaker_role": speaker_role,
            "interviewer_context": relevant_context,  # Preserved context
            "has_context": len(relevant_context) > 0,
            # ... other metadata
        }
```

### 2. During ChromaDB Storage with Context

```python
def store_quotes_in_vector_db(self, quotes: List[Dict]):
    metadata = {
        'transcript_name': quote['transcript_name'],
        'speaker_role': quote.get('speaker_role', 'expert'),
        'has_context': quote.get('has_context', False),
        'context_count': len(quote.get('interviewer_context', [])),
        # ... other metadata
        # Note: Full context is preserved in the quote object, not just metadata
    }
```

### 3. During Analysis

```python
def get_quotes_by_perspective(self, perspective_key: str, perspective_data: dict):
    # Get relevant quotes
    relevant_quotes = self.semantic_search_quotes(query=search_query)
    
    # Filter to expert quotes only
    expert_quotes = self.get_expert_quotes_only(relevant_quotes)
    
    return expert_quotes  # Only expert insights
```

## Benefits

### 1. **Focused Insights**
- All analysis automatically focuses on expert opinions
- No more interviewer questions cluttering your insights
- Cleaner, more actionable business intelligence

### 2. **Better Quote Quality**
- Quotes come from industry professionals with direct experience
- Higher credibility and relevance
- More specific, actionable insights

### 3. **Flexible Analysis**
- Can still access interviewer quotes if needed for context
- Speaker role statistics provide transparency
- Easy to filter and search by role

### 4. **Improved Search Results**
- Semantic search automatically prioritizes expert content
- Better relevance when searching for insights
- Reduced noise from questions and transitions

## Usage Examples

### Basic Usage (Default Behavior)

```python
# Initialize the tool
analyzer = QuoteAnalysisTool()

# Process transcripts - automatically filters for expert quotes
results = analyzer.process_transcripts_for_quotes("FlexXray Transcripts")

# All analysis now focuses on expert quotes only
print(f"Expert quotes analyzed: {len(results['expert_quotes'])}")
```

### Advanced Filtering

```python
# Get speaker role breakdown
stats = analyzer.get_speaker_role_statistics(results['all_quotes'])
print(f"Expert quotes: {stats['expert_quotes']} ({stats['expert_percentage']:.1f}%)")
print(f"Interviewer quotes filtered: {stats['interviewer_quotes']}")

# Search with specific speaker role filter
expert_quotes = analyzer.search_quotes_with_speaker_filter(
    query="customer satisfaction",
    speaker_role="expert",
    n_results=20
)

# Get quotes by role
all_expert_quotes = analyzer.get_expert_quotes_only(results['all_quotes'])
all_interviewer_quotes = analyzer.get_quotes_by_speaker_role(results['all_quotes'], "interviewer")
```

### Output Reports

The tool now includes speaker role information in all output formats:

- **Text files**: Speaker role breakdown and filtering notes
- **Word documents**: Speaker role statistics and expert-only focus
- **Excel files**: Speaker role metadata preserved
- **Console output**: Real-time speaker role statistics during processing

## Testing

Run the test script to see the speaker role identification in action:

```bash
python test_speaker_roles.py
```

This will demonstrate:
- Speaker role identification accuracy
- Filtering functionality
- Statistics generation
- Sample quote categorization

## Configuration

The speaker role identification uses conservative defaults:
- **Default behavior**: Treats unclear sentences as "expert" quotes
- **Filtering**: Automatically excludes clear interviewer patterns
- **Customization**: Can be extended with additional patterns if needed

## Summary

With these new features, your FlexXray transcript analysis will now:

✅ **Automatically identify** expert vs. interviewer quotes  
✅ **Filter out** interviewer questions and transitions  
✅ **Focus analysis** on industry expert insights only  
✅ **Store metadata** for advanced filtering and search  
✅ **Provide statistics** on speaker role distribution  
✅ **Enable flexible** quote retrieval by speaker role  

This ensures that when you pull quotes for analysis, you're getting the most valuable insights from the people who actually know the business - the experts being interviewed, not the questions being asked.
