# 🏢 Company Configuration System

The FlexXray Transcript Summarizer now features a **flexible company configuration system** that makes it easy to switch between different companies and their analysis settings without modifying code.

## 🚀 Quick Start

### 1. List Available Companies
```bash
python company_switcher.py --list
```

### 2. Switch to a Different Company
```bash
python company_switcher.py --switch acme_corp
```

### 3. Create a New Company
```bash
python company_switcher.py --create my_company
```

### 4. View Current Company Info
```bash
python company_switcher.py --info
```

## 📁 System Architecture

### Core Files
- **`company_config.py`** - Company configuration definitions and templates
- **`config_manager.py`** - Configuration management and integration
- **`company_switcher.py`** - Command-line interface for company management

### Configuration Structure
Each company configuration includes:
- **Basic Info**: Name, display name, transcript directory, output prefix
- **Analysis Questions**: Key questions for transcript analysis
- **Question Categories**: Organization of questions (key takeaways, strengths, weaknesses)
- **Speaker Patterns**: Rules for identifying interviewers vs. experts
- **Business Insights**: Patterns for detecting business-relevant content
- **Topic Synonyms**: Alternative terms for enhanced matching
- **Industry Keywords**: Company-specific terminology

## 🔧 Adding a New Company

### Method 1: Interactive Creation (Recommended)
```bash
python company_switcher.py --create startup_xyz
```
Follow the prompts to configure:
- Display name
- Transcript directory
- Output prefix
- Key questions
- Question categories

### Method 2: Programmatic Creation
```python
from config_manager import get_config_manager

config_mgr = get_config_manager()
new_company = config_mgr.create_new_company(
    name="startup_xyz",
    display_name="Startup XYZ",
    transcript_directory="Startup XYZ Transcripts",
    output_prefix="StartupXYZ",
    key_questions={
        "product_fit": "How well does Startup XYZ's product fit the market?",
        "competitive_edge": "What competitive advantages does Startup XYZ have?"
    },
    question_categories={
        "key_takeaways": ["product_fit", "competitive_edge"]
    }
)
```

### Method 3: Direct Configuration File
Edit `company_config.py` and add to `COMPANY_CONFIGS`:
```python
"startup_xyz": CompanyConfig(
    name="startup_xyz",
    display_name="Startup XYZ",
    transcript_directory="Startup XYZ Transcripts",
    output_prefix="StartupXYZ",
    # ... other configuration
)
```

## 📊 Current Company Configurations

### FlexXray (Default)
- **Industry**: Foreign material inspection services
- **Key Questions**: Market leadership, value proposition, local presence, technology advantages
- **Focus**: Quality control, food safety, inspection equipment

### ACME Corporation (Example)
- **Industry**: Manufacturing and operations
- **Key Questions**: Market position, product portfolio, operational efficiency
- **Focus**: Production, supply chain, customer service

## 🔄 Switching Between Companies

### Command Line
```bash
# Switch to ACME Corp
python company_switcher.py --switch acme_corp

# Switch back to FlexXray
python company_switcher.py --switch flexxray
```

### Python Code
```python
from config_manager import set_company, get_config_manager

# Switch company
set_company("acme_corp")

# Get configuration
config_mgr = get_config_manager()
questions = config_mgr.get_key_questions()
transcript_dir = config_mgr.get_transcript_directory()
```

## 📝 Customizing Company Settings

### Update Configuration
```bash
# Update transcript directory
python company_switcher.py --update transcript_directory:"New Transcripts"

# Update output prefix
python company_switcher.py --update output_prefix:"NewPrefix"

# Update key questions
python company_switcher.py --update key_questions:"{'new_question': 'What is the new question?'}"
```

### Modify Key Questions
```python
from config_manager import get_config_manager

config_mgr = get_config_manager()
config_mgr.update_current_company(
    key_questions={
        "market_position": "What is the company's market position?",
        "competitive_advantage": "What competitive advantages exist?",
        "growth_strategy": "What is the growth strategy?"
    }
)
```

## 🗂️ Transcript Directory Management

### Validate Directory
```bash
python company_switcher.py --validate
```

### Create Directory
```bash
python company_switcher.py --validate
# Follow prompts to create directory
```

### Directory Structure
```
Project Root/
├── FlexXray Transcripts/          # FlexXray transcripts
├── ACME Transcripts/              # ACME transcripts
├── Startup XYZ Transcripts/       # New company transcripts
└── Outputs/                       # Analysis outputs
    ├── FlexXray_analysis.json
    ├── ACME_analysis.json
    └── StartupXYZ_analysis.json
```

## 🔍 Integration with Existing System

### Automatic Configuration Loading
The system automatically loads company-specific settings:
- **Output file naming** (e.g., `FlexXray_analysis.json` vs `ACME_analysis.json`)
- **Key questions** for analysis
- **Speaker identification patterns**
- **Business insight detection**
- **Topic synonym mappings**

### Seamless Switching
When you switch companies:
1. All configuration is updated automatically
2. Output files use new company prefix
3. Analysis questions change to company-specific ones
4. Speaker patterns adapt to company terminology

## 📋 Example Workflow

### 1. Start with FlexXray
```bash
python company_switcher.py --info
# Shows FlexXray configuration
```

### 2. Create New Company
```bash
python company_switcher.py --create techstartup
# Interactive configuration
```

### 3. Switch to New Company
```bash
python company_switcher.py --switch techstartup
# All settings updated
```

### 4. Run Analysis
```bash
python run_streamlined_analysis.py
# Uses TechStartup configuration automatically
```

### 5. Switch Back
```bash
python company_switcher.py --switch flexxray
# Back to FlexXray settings
```

## 🛠️ Advanced Configuration

### Custom Speaker Patterns
```python
custom_speaker_patterns = {
    "interviewer": {
        "patterns": [
            r'\b(what|how|why|when|where)\b',
            r'\?\s*$'
        ],
        "weight": 1.0,
        "fuzzy_threshold": 80
    }
}

config_mgr.update_current_company(
    speaker_patterns=custom_speaker_patterns
)
```

### Custom Business Insights
```python
custom_insights = {
    "financial_insights": {
        "patterns": [
            r'\b(revenue|profit|cost|pricing|investment)\b',
            r'\b(financial|economic|monetary|budget)\b'
        ],
        "weight": 0.9,
        "fuzzy_threshold": 70
    }
}

config_mgr.update_current_company(
    business_insights=custom_insights
)
```

## 🔧 Troubleshooting

### Common Issues

**Company not found**
```bash
python company_switcher.py --list
# Check available companies
```

**Transcript directory missing**
```bash
python company_switcher.py --validate
# Create directory if needed
```

**Configuration not saving**
- Check file permissions for `company_settings.json`
- Ensure valid JSON format in custom settings

### Reset to Default
```python
from company_config import COMPANY_CONFIGS
from config_manager import get_config_manager

config_mgr = get_config_manager()
config_mgr.company_config = COMPANY_CONFIGS["flexxray"]
config_mgr.save_custom_settings()
```

## 📚 API Reference

### ConfigManager Methods
- `switch_company(company_name)` - Switch to different company
- `get_key_questions()` - Get current company questions
- `get_transcript_directory()` - Get transcript directory
- `get_output_prefix()` - Get output file prefix
- `update_current_company(**updates)` - Update configuration
- `create_new_company(**kwargs)` - Create new company
- `list_companies()` - List all available companies

### CompanyConfig Fields
- `name` - Internal identifier
- `display_name` - Human-readable name
- `transcript_directory` - Directory for transcripts
- `output_prefix` - Prefix for output files
- `key_questions` - Analysis questions
- `question_categories` - Question organization
- `speaker_patterns` - Speaker identification rules
- `business_insights` - Business content detection
- `topic_synonyms` - Topic matching synonyms
- `industry_keywords` - Industry-specific terms

## 🎯 Benefits

### For Analysts
- **Quick company switching** without code changes
- **Customized analysis questions** per company
- **Company-specific terminology** recognition
- **Organized output files** by company

### For Developers
- **Centralized configuration** management
- **Extensible architecture** for new companies
- **Consistent API** across different configurations
- **Easy testing** with different company settings

### For Organizations
- **Multi-company support** in single system
- **Standardized analysis** across different businesses
- **Easy onboarding** of new companies
- **Maintainable configuration** structure

## 🚀 Future Enhancements

- **Web-based configuration interface**
- **Configuration templates** by industry
- **Import/export** of company configurations
- **Version control** for configuration changes
- **Multi-user** configuration management
- **Configuration validation** and testing tools
