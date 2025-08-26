# Unified Configuration System

## Overview

The FlexXray Transcript Summarizer now uses a unified configuration system that consolidates all settings into a single, layered configuration model. This replaces the previous scattered approach with `env_config.py`, `config_manager.py`, and `company_config.py`.

## 🎯 Key Benefits

### 1. **Single Source of Truth**
- All configuration in one place (`settings.py`)
- No more scattered config files
- Centralized validation and management

### 2. **Layered Configuration Model**
```
1. Defaults (hardcoded fallbacks)
2. Environment Variables (deployment-specific)
3. Company Overrides (business-specific)
4. Runtime Overrides (optional, for testing)
```

### 3. **Type Safety & Validation**
- Pydantic models for configuration validation
- Automatic type checking and error detection
- Fallback to dataclasses if Pydantic unavailable

### 4. **Better Testing & Deployment**
- Easier to mock configurations
- Environment-specific settings
- Cloud-ready architecture

## 🏗️ Architecture

### Core Components

#### `Settings` Class
The main configuration container that holds all settings:

```python
class Settings(BaseModel):
    # Core configuration
    debug_mode: bool
    environment: str
    
    # Component configurations
    openai: OpenAIConfig
    vector_db: VectorDBConfig
    paths: PathConfig
    logging: LoggingConfig
    batch: BatchConfig
    
    # Company configuration
    current_company: str
    companies: Dict[str, CompanyConfig]
    
    # Custom settings
    custom_settings: Dict[str, Any]
```

#### `SettingsManager` Class
Manages the configuration lifecycle:

```python
class SettingsManager:
    def __init__(self, config_file: str = "settings.json")
    def save_settings(self)
    def reload_settings(self)
    def get_setting(self, key: str, default: Any = None)
    def set_setting(self, key: str, value: Any)
```

### Configuration Models

#### `OpenAIConfig`
```python
class OpenAIConfig(BaseModel):
    api_key: str
    model_for_summary: str = "gpt-4o"
    model_token_limit: int = 128000
    max_quotes_for_analysis: int = 30
    max_tokens_per_quote: int = 150
    enable_token_logging: bool = True
```

#### `CompanyConfig`
```python
class CompanyConfig(BaseModel):
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
```

#### `VectorDBConfig`
```python
class VectorDBConfig(BaseModel):
    chroma_persist_directory: str = "./chroma_db"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536
    collection_name: str = "flexxray_quotes"
```

## 🚀 Usage

### Basic Configuration Access

```python
from settings import get_settings, get_openai_api_key, get_company_config

# Get all settings
settings = get_settings()

# Get OpenAI API key
api_key = get_openai_api_key()

# Get company configuration
company = get_company_config("flexxray")
```

### Advanced Configuration Management

```python
from settings import get_settings_manager

# Get settings manager
manager = get_settings_manager()

# Get specific setting
max_quotes = manager.get_setting("openai.max_quotes_for_analysis", 30)

# Set specific setting
manager.set_setting("openai.max_quotes_for_analysis", 50)

# Save settings
manager.save_settings()
```

### Company Management

```python
from settings import switch_company, get_company_config

# Switch to different company
switch_company("startup_xyz")

# Get current company config
current_company = get_company_config()

# Access company-specific settings
transcript_dir = current_company.transcript_directory
key_questions = current_company.key_questions
```

### Environment Variable Overrides

The system automatically loads from environment variables:

```bash
# OpenAI settings
export OPENAI_API_KEY="sk-your-api-key"
export OPENAI_MODEL_FOR_SUMMARY="gpt-4o-mini"
export MAX_QUOTES_FOR_ANALYSIS="25"

# Path settings
export PROJECT_ROOT="/custom/project/path"
export OUTPUT_DIRECTORY="/custom/output/path"

# General settings
export DEBUG="true"
export ENVIRONMENT="production"
```

## 📁 File Structure

```
project_root/
├── settings.py                    # Main configuration module
├── settings.json                  # Saved configuration (auto-generated)
├── .env                          # Environment variables (optional)
├── config_backup/                # Backup of old config files
│   ├── env_config.py
│   ├── config_manager.py
│   └── company_config.py
└── CONFIGURATION_MIGRATION_REPORT.md
```

## 🔄 Migration from Old System

### Automatic Migration

Run the migration script to automatically transition:

```bash
python migrate_to_unified_config.py
```

This script will:
1. ✅ Create backups of old configuration files
2. ✅ Migrate company configurations
3. ✅ Migrate environment settings
4. ✅ Update import statements in Python files
5. ✅ Generate migration report
6. ✅ Test the new system

### Manual Migration

If you prefer manual migration:

1. **Update imports**:
   ```python
   # OLD
   from env_config import get_openai_api_key
   from config_manager import get_config_manager
   
   # NEW
   from settings import get_openai_api_key, get_config_manager
   ```

2. **Update configuration access**:
   ```python
   # OLD
   config = get_env_config()
   max_quotes = config.max_quotes_for_analysis
   
   # NEW
   from settings import get_settings
   settings = get_settings()
   max_quotes = settings.openai.max_quotes_for_analysis
   ```

3. **Update company access**:
   ```python
   # OLD
   config_mgr = get_config_manager()
   company = config_mgr.company_config
   
   # NEW
   from settings import get_company_config
   company = get_company_config()
   ```

## 🧪 Testing

### Test the Configuration System

```bash
python settings.py
```

This will:
- Load the configuration
- Validate all settings
- Test company switching
- Test token estimation
- Ensure directories exist
- Save initial settings

### Test in Your Application

```python
from settings import get_settings

def test_configuration():
    settings = get_settings()
    
    # Validate configuration
    assert settings.validate_configuration()
    
    # Test OpenAI config
    assert settings.openai.api_key.startswith("sk-")
    assert settings.openai.model_for_summary in ["gpt-4o", "gpt-4o-mini", "gpt-4"]
    
    # Test company config
    assert "flexxray" in settings.companies
    assert settings.current_company == "flexxray"
    
    print("✅ Configuration test passed!")
```

## 🔧 Configuration File Format

The `settings.json` file is automatically generated and contains:

```json
{
  "debug_mode": false,
  "environment": "development",
  "openai": {
    "api_key": "sk-your-api-key",
    "model_for_summary": "gpt-4o",
    "model_token_limit": 128000,
    "max_quotes_for_analysis": 30,
    "max_tokens_per_quote": 150,
    "enable_token_logging": true
  },
  "vector_db": {
    "chroma_persist_directory": "./chroma_db",
    "embedding_model": "text-embedding-3-small",
    "embedding_dimension": 1536,
    "collection_name": "flexxray_quotes"
  },
  "paths": {
    "project_root": "/path/to/project",
    "output_directory": "/path/to/project/Outputs",
    "transcript_directory": "/path/to/project/FlexXray Transcripts",
    "chroma_db_directory": "/path/to/project/chroma_db"
  },
  "current_company": "flexxray",
  "companies": {
    "flexxray": {
      "name": "flexxray",
      "display_name": "FlexXray",
      "transcript_directory": "FlexXray Transcripts",
      "output_prefix": "FlexXray",
      "key_questions": {...},
      "question_categories": {...}
    }
  }
}
```

## 🚨 Troubleshooting

### Common Issues

#### 1. **Import Errors**
```
ModuleNotFoundError: No module named 'env_config'
```
**Solution**: Update imports to use `settings` module

#### 2. **Configuration Validation Failed**
```
❌ OPENAI_API_KEY not found
```
**Solution**: Set `OPENAI_API_KEY` environment variable

#### 3. **Company Not Found**
```
❌ Current company 'startup_xyz' not found in available companies
```
**Solution**: Add company configuration or switch to existing company

#### 4. **Settings File Corrupted**
```
❌ Error loading settings file: ...
```
**Solution**: Delete `settings.json` and restart (will regenerate from defaults)

### Debug Mode

Enable debug mode to see detailed configuration information:

```bash
export DEBUG="true"
python settings.py
```

### Rollback

If you need to rollback to the old system:

```bash
# Restore from backup
cp config_backup/env_config.py .
cp config_backup/config_manager.py .
cp config_backup/company_config.py .

# Update imports back to old modules
```

## 🔮 Future Enhancements

### Planned Features

1. **Configuration Templates**
   - Pre-configured templates for common use cases
   - Industry-specific configurations

2. **Dynamic Configuration**
   - Runtime configuration updates
   - Hot-reloading of settings

3. **Configuration Validation Rules**
   - Custom validation rules
   - Cross-field validation

4. **Configuration Migration Tools**
   - Import from other configuration formats
   - Export to various formats

5. **Multi-Environment Support**
   - Development/Staging/Production profiles
   - Environment-specific overrides

## 📚 API Reference

### Main Functions

- `get_settings()` → `Settings`
- `get_settings_manager()` → `SettingsManager`
- `get_openai_config()` → `OpenAIConfig`
- `get_company_config(name: str = None)` → `CompanyConfig`
- `get_openai_api_key()` → `str`
- `switch_company(name: str)` → `bool`

### SettingsManager Methods

- `save_settings()` → `None`
- `reload_settings()` → `None`
- `get_setting(key: str, default: Any = None)` → `Any`
- `set_setting(key: str, value: Any)` → `None`

### Settings Methods

- `get_company_config(name: str = None)` → `CompanyConfig`
- `switch_company(name: str)` → `bool`
- `update_company_config(name: str, **updates)` → `bool`
- `add_company(config: CompanyConfig)` → `bool`
- `estimate_token_usage(quote_count: int, include_prompt: bool = True)` → `Dict[str, Any]`
- `validate_configuration()` → `bool`

## 🤝 Contributing

When adding new configuration options:

1. **Add to appropriate model class** (e.g., `OpenAIConfig`, `CompanyConfig`)
2. **Update environment variable loading** in `Settings.root_validator`
3. **Add validation rules** if needed
4. **Update documentation** and examples
5. **Add tests** for new configuration options

## 📞 Support

For configuration-related issues:

1. Check this documentation
2. Review the migration report
3. Test with `python settings.py`
4. Check environment variables
5. Review `settings.json` file

---

*This unified configuration system provides a robust, maintainable foundation for the FlexXray Transcript Summarizer, making it easier to deploy, test, and extend.*
