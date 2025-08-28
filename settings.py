#!/usr/bin/env python3
"""
Unified Configuration Management for FlexXray Transcript Summarizer

This module consolidates all configuration management into a single, layered system:
1. Defaults (hardcoded fallbacks)
2. Environment Variables (deployment-specific)
3. Company Overrides (business-specific)
4. Runtime Overrides (optional, for testing)

Uses Pydantic for validation and type safety.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

try:
    from pydantic import BaseModel, Field, field_validator, model_validator
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    # Fallback to dataclasses if Pydantic is not available
    from dataclasses import dataclass as BaseModel
    Field = lambda **kwargs: None
    field_validator = lambda *args, **kwargs: lambda f: f
    model_validator = lambda *args, **kwargs: lambda f: f


# ============================================================================
# Configuration Models
# ============================================================================

class CompanyConfig(BaseModel):
    """Configuration for a specific company."""
    
    name: str = Field(..., description="Company identifier")
    display_name: str = Field(..., description="Human-readable company name")
    transcript_directory: str = Field(..., description="Directory for transcript files")
    output_prefix: str = Field(..., description="Prefix for output files")
    key_questions: Dict[str, str] = Field(default_factory=dict, description="Key analysis questions")
    question_categories: Dict[str, List[str]] = Field(default_factory=dict, description="Question categorization")
    speaker_patterns: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Speaker identification patterns")
    business_insights: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Business insight patterns")
    topic_synonyms: Dict[str, List[str]] = Field(default_factory=dict, description="Topic synonym mappings")
    industry_keywords: List[str] = Field(default_factory=list, description="Industry-specific keywords")
    company_specific_terms: List[str] = Field(default_factory=list, description="Company-specific terminology")


class OpenAIConfig(BaseModel):
    """OpenAI API configuration."""
    
    api_key: str = Field(..., description="OpenAI API key")
    model_for_summary: str = Field(default="gpt-4o", description="Model for summary generation")
    model_token_limit: int = Field(default=128000, description="Token limit for the model")
    conservative_token_threshold: float = Field(default=0.8, description="Conservative token threshold (percentage)")
    max_quotes_for_analysis: int = Field(default=30, description="Maximum quotes for analysis")
    max_tokens_per_quote: int = Field(default=150, description="Estimated tokens per quote")
    enable_token_logging: bool = Field(default=True, description="Enable detailed token logging")
    
    @field_validator('conservative_token_threshold')
    @classmethod
    def validate_token_threshold(cls, v):
        if not 0 < v < 1:
            raise ValueError('Token threshold must be between 0 and 1')
        return v
    
    @property
    def conservative_limit(self) -> int:
        """Get the conservative token limit."""
        return int(self.model_token_limit * self.conservative_token_threshold)


class VectorDBConfig(BaseModel):
    """Vector database configuration."""
    
    chroma_persist_directory: str = Field(default="./chroma_db", description="ChromaDB persistence directory")
    embedding_model: str = Field(default="text-embedding-3-small", description="OpenAI embedding model")
    embedding_dimension: int = Field(default=1536, description="Embedding vector dimension")
    collection_name: str = Field(default="flexxray_quotes", description="ChromaDB collection name")


class PathConfig(BaseModel):
    """Path configuration."""
    
    project_root: Path = Field(default_factory=lambda: Path(__file__).parent, description="Project root directory")
    output_directory: Path = Field(default_factory=lambda: Path(__file__).parent / "Outputs", description="Output directory")
    transcript_directory: Path = Field(default_factory=lambda: Path(__file__).parent / "FlexXray Transcripts", description="Default transcript directory")
    chroma_db_directory: Path = Field(default_factory=lambda: Path(__file__).parent / "chroma_db", description="ChromaDB directory")
    
    def ensure_directories_exist(self):
        """Ensure all required directories exist."""
        directories = [self.output_directory, self.transcript_directory, self.chroma_db_directory]
        for directory in directories:
            directory.mkdir(exist_ok=True)
            print(f"✅ Directory ensured: {directory}")


class LoggingConfig(BaseModel):
    """Logging configuration."""
    
    level: str = Field(default="INFO", description="Logging level")
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", description="Log format")
    file_logging: bool = Field(default=True, description="Enable file logging")
    console_logging: bool = Field(default=True, description="Enable console logging")
    log_file: str = Field(default="flexxray.log", description="Log file name")


class BatchConfig(BaseModel):
    """Batch processing configuration."""
    
    default_batch_size: int = Field(default=100, description="Default batch size for processing")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    retry_delay: float = Field(default=1.0, description="Delay between retries (seconds)")
    exponential_backoff: bool = Field(default=True, description="Use exponential backoff for retries")
    max_delay: float = Field(default=60.0, description="Maximum delay between retries")


class Settings(BaseModel):
    """Main settings class that consolidates all configuration."""
    
    # Core configuration
    debug_mode: bool = Field(default=False, description="Enable debug mode")
    environment: str = Field(default="development", description="Environment (development, staging, production)")
    
    # Component configurations
    openai: OpenAIConfig
    vector_db: VectorDBConfig = Field(default_factory=VectorDBConfig)
    paths: PathConfig = Field(default_factory=PathConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    batch: BatchConfig = Field(default_factory=BatchConfig)
    
    # Company configuration
    current_company: str = Field(default="flexxray", description="Current company identifier")
    companies: Dict[str, CompanyConfig] = Field(default_factory=dict, description="Available company configurations")
    
    # Custom settings
    custom_settings: Dict[str, Any] = Field(default_factory=dict, description="Custom runtime settings")
    
    class Config:
        arbitrary_types_allowed = True
    
    @model_validator(mode='before')
    @classmethod
    def load_environment_variables(cls, values):
        """Load and override with environment variables."""
        if not isinstance(values, dict):
            return values
            
        env_overrides = {}
        
        # OpenAI settings
        if os.getenv("OPENAI_API_KEY"):
            env_overrides["openai"] = {"api_key": os.getenv("OPENAI_API_KEY")}
        if os.getenv("OPENAI_MODEL_FOR_SUMMARY"):
            env_overrides["openai"] = env_overrides.get("openai", {})
            env_overrides["openai"]["model_for_summary"] = os.getenv("OPENAI_MODEL_FOR_SUMMARY")
        if os.getenv("MAX_QUOTES_FOR_ANALYSIS"):
            env_overrides["openai"] = env_overrides.get("openai", {})
            env_overrides["openai"]["max_quotes_for_analysis"] = int(os.getenv("MAX_QUOTES_FOR_ANALYSIS"))
        
        # Path settings
        if os.getenv("PROJECT_ROOT"):
            env_overrides["paths"] = {"project_root": Path(os.getenv("PROJECT_ROOT"))}
        if os.getenv("OUTPUT_DIRECTORY"):
            env_overrides["paths"] = env_overrides.get("paths", {})
            env_overrides["paths"]["output_directory"] = Path(os.getenv("OUTPUT_DIRECTORY"))
        
        # Vector DB settings
        if os.getenv("CHROMA_DB_DIRECTORY"):
            env_overrides["vector_db"] = {"chroma_persist_directory": os.getenv("CHROMA_DB_DIRECTORY")}
        
        # General settings
        if os.getenv("DEBUG"):
            env_overrides["debug_mode"] = os.getenv("DEBUG").lower() in ("true", "1", "yes")
        if os.getenv("ENVIRONMENT"):
            env_overrides["environment"] = os.getenv("ENVIRONMENT")
        
        # Merge environment overrides
        for key, value in env_overrides.items():
            if key in values:
                if isinstance(value, dict) and isinstance(values[key], dict):
                    values[key].update(value)
                else:
                    values[key] = value
            else:
                values[key] = value
        
        return values
    
    def get_company_config(self, company_name: str = None) -> Optional[CompanyConfig]:
        """Get company configuration by name."""
        company_name = company_name or self.current_company
        return self.companies.get(company_name)
    
    def switch_company(self, company_name: str) -> bool:
        """Switch to a different company."""
        if company_name in self.companies:
            self.current_company = company_name
            return True
        return False
    
    def update_company_config(self, company_name: str, **updates) -> bool:
        """Update company configuration."""
        if company_name in self.companies:
            company_config = self.companies[company_name]
            for key, value in updates.items():
                if hasattr(company_config, key):
                    setattr(company_config, key, value)
            return True
        return False
    
    def add_company(self, company_config: CompanyConfig) -> bool:
        """Add a new company configuration."""
        try:
            self.companies[company_config.name] = company_config
            return True
        except Exception:
            return False
    
    def estimate_token_usage(self, quote_count: int, include_prompt: bool = True) -> Dict[str, Any]:
        """Estimate token usage for OpenAI API calls."""
        base_prompt_tokens = 800 if include_prompt else 0
        estimated_quote_tokens = quote_count * self.openai.max_tokens_per_quote
        total_tokens = base_prompt_tokens + estimated_quote_tokens
        
        # Cost estimation (approximate, based on GPT-4 pricing)
        input_cost = (total_tokens / 1000) * 0.03
        output_cost = (total_tokens / 1000) * 0.06
        total_cost = input_cost + output_cost
        
        return {
            "quote_count": quote_count,
            "base_prompt_tokens": base_prompt_tokens,
            "quote_tokens": estimated_quote_tokens,
            "total_tokens": total_tokens,
            "estimated_cost_usd": round(total_cost, 4),
            "model": self.openai.model_for_summary,
            "max_quotes_limit": self.openai.max_quotes_for_analysis
        }
    
    def validate_configuration(self) -> bool:
        """Validate the complete configuration."""
        try:
            # Validate OpenAI API key
            if not self.openai.api_key:
                print("❌ OPENAI_API_KEY not found")
                return False
            
            if not self.openai.api_key.startswith("sk-"):
                print("❌ OPENAI_API_KEY format appears invalid")
                return False
            
            # Validate company configuration
            if not self.companies:
                print("❌ No company configurations found")
                return False
            
            if self.current_company not in self.companies:
                print(f"❌ Current company '{self.current_company}' not found in available companies")
                return False
            
            print("✅ Configuration validated successfully")
            return True
            
        except Exception as e:
            print(f"❌ Configuration validation failed: {e}")
            return False


# ============================================================================
# Default Company Configurations
# ============================================================================

DEFAULT_COMPANIES = {
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
            "unpredictable_timing": "How does unpredictable event timing impact FlexXray's business?",
        },
        question_categories={
            "key_takeaways": ["market_leadership", "value_proposition", "local_presence"],
            "strengths": ["technology_advantages", "rapid_turnaround"],
            "weaknesses": ["limited_tam", "unpredictable_timing"],
        },
        speaker_patterns={
            "interviewer": {
                "patterns": [
                    r"^\s*(So|Well|Now|Let\'s|Can you|Could you|What|How|Why|When|Where|Tell me|Describe|Explain|Walk me through|Take me through|Give me|Share|What\'s|How\'s|Why\'s|When\'s|Where\'s)",
                    r"\?\s*$",
                    r"\b(interviewer|interview|question|ask|inquiry|query)\b",
                ],
                "weight": 1.0,
                "fuzzy_threshold": 75,
            },
            "expert": {
                "patterns": [
                    r"\b(I|we|our|us|FlexXray|company|firm|organization|enterprise|corporation|business|operation)\b",
                    r"\b(we have|we are|we do|we provide|we offer|we deliver|we ensure|we maintain|we focus|we specialize)\b",
                ],
                "weight": 0.8,
                "fuzzy_threshold": 70,
            },
        },
        business_insights={
            "business_insights": {
                "patterns": [
                    r"\b(advantage|strength|weakness|challenge|opportunity|risk|concern|benefit|problem|issue)\b",
                    r"\b(growth|expansion|market|customer|competition|industry|business|strategy|model|approach|method)\b",
                ],
                "weight": 1.0,
                "fuzzy_threshold": 65,
            },
        },
        topic_synonyms={},
        industry_keywords=["inspection", "equipment", "machine", "service", "capability"],
        company_specific_terms=["FlexXray", "inspection", "equipment", "machine"],
    )
}


# ============================================================================
# Configuration Manager
# ============================================================================

class SettingsManager:
    """Manages the unified configuration system."""
    
    def __init__(self, config_file: str = "settings.json"):
        """Initialize the settings manager."""
        self.config_file = config_file
        self.settings = self._load_settings()
        self._load_dotenv()
    
    def _load_dotenv(self):
        """Load environment variables from .env file."""
        env_file = ".env"
        if os.path.exists(env_file):
            load_dotenv(env_file)
        else:
            # Try to load from project root
            project_root = Path(__file__).parent
            env_path = project_root / env_file
            if env_path.exists():
                load_dotenv(env_path)
    
    def _load_settings(self) -> Settings:
        """Load settings from file or create defaults."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Load company configurations
                companies = {}
                companies_data = config_data.get("companies", {})
                
                # Handle both list and dict formats for backward compatibility
                if isinstance(companies_data, list):
                    # Old format: list of company configs
                    for company_data in companies_data:
                        if isinstance(company_data, dict):
                            try:
                                company_config = CompanyConfig(**company_data)
                                companies[company_config.name] = company_config
                            except Exception as e:
                                print(f"Warning: Could not load company config {company_data}: {e}")
                                continue
                        else:
                            print(f"Warning: Expected dict for company config, got {type(company_data)}: {company_data}")
                            continue
                elif isinstance(companies_data, dict):
                    # New format: dict of company configs
                    for company_name, company_data in companies_data.items():
                        if isinstance(company_data, dict):
                            try:
                                company_config = CompanyConfig(**company_data)
                                companies[company_name] = company_config
                            except Exception as e:
                                print(f"Warning: Could not load company config {company_name}: {e}")
                                continue
                        else:
                            print(f"Warning: Expected dict for company config {company_name}, got {type(company_data)}: {company_data}")
                            continue
                
                # Create settings with loaded companies
                config_data["companies"] = companies
                return Settings(**config_data)
            
        except Exception as e:
            print(f"Warning: Could not load settings file: {e}")
        
        # Create default settings
        return self._create_default_settings()
    
    def _create_default_settings(self) -> Settings:
        """Create default settings."""
        # Get OpenAI API key from environment
        api_key = os.getenv("OPENAI_API_KEY", "")
        
        openai_config = OpenAIConfig(
            api_key=api_key,
            model_for_summary="gpt-4o",
            model_token_limit=128000,
            max_quotes_for_analysis=30,
            max_tokens_per_quote=150,
        )
        
        return Settings(
            openai=openai_config,
            companies=DEFAULT_COMPANIES,
            current_company="flexxray"
        )
    
    def save_settings(self):
        """Save current settings to file."""
        try:
            # Convert settings to dict for JSON serialization
            settings_dict = self.settings.dict()
            
            # Convert Path objects to strings
            for key, value in settings_dict.items():
                if isinstance(value, dict) and "paths" in key:
                    for path_key, path_value in value.items():
                        if isinstance(path_value, Path):
                            value[path_key] = str(path_value)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(settings_dict, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Settings saved to {self.config_file}")
            
        except Exception as e:
            print(f"❌ Error saving settings: {e}")
    
    def reload_settings(self):
        """Reload settings from file."""
        self.settings = self._load_settings()
        print("✅ Settings reloaded")
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a specific setting value."""
        keys = key.split('.')
        value = self.settings
        
        try:
            for k in keys:
                value = getattr(value, k)
            return value
        except AttributeError:
            return default
    
    def set_setting(self, key: str, value: Any):
        """Set a specific setting value."""
        keys = key.split('.')
        obj = self.settings
        
        try:
            for k in keys[:-1]:
                obj = getattr(obj, k)
            setattr(obj, keys[-1], value)
            print(f"✅ Setting updated: {key} = {value}")
        except AttributeError:
            print(f"❌ Could not set setting: {key}")


# ============================================================================
# Global Instance and Convenience Functions
# ============================================================================

_settings_manager = None


def get_settings_manager() -> SettingsManager:
    """Get the global settings manager instance."""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    return _settings_manager


def get_settings() -> Settings:
    """Get the current settings."""
    return get_settings_manager().settings


def get_openai_config() -> OpenAIConfig:
    """Get OpenAI configuration."""
    return get_settings().openai


def get_company_config(company_name: str = None) -> Optional[CompanyConfig]:
    """Get company configuration."""
    return get_settings().get_company_config(company_name)


def get_openai_api_key() -> str:
    """Get OpenAI API key."""
    config = get_openai_config()
    if not config.api_key:
        raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
    return config.api_key


def switch_company(company_name: str) -> bool:
    """Switch to a different company."""
    return get_settings().switch_company(company_name)


# ============================================================================
# Backward Compatibility Functions
# ============================================================================

def get_env_config():
    """Backward compatibility function for env_config."""
    return get_settings()


def get_config_manager(company_name: str = "flexxray"):
    """Backward compatibility function for config_manager."""
    return get_settings_manager()


# ============================================================================
# Testing and Validation
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("UNIFIED SETTINGS TEST")
    print("=" * 60)
    
    try:
        # Initialize settings manager
        manager = get_settings_manager()
        settings = manager.settings
        
        print(f"✅ Settings loaded successfully")
        print(f"   Environment: {settings.environment}")
        print(f"   Debug Mode: {settings.debug_mode}")
        print(f"   Current Company: {settings.current_company}")
        print(f"   Available Companies: {list(settings.companies.keys())}")
        
        # Validate configuration
        if settings.validate_configuration():
            print("\n✅ Configuration validation passed")
            
            # Test company switching
            if "flexxray" in settings.companies:
                settings.switch_company("flexxray")
                print(f"✅ Switched to company: {settings.current_company}")
            
            # Test token estimation
            token_estimate = settings.estimate_token_usage(25)
            print(f"✅ Token estimation: {token_estimate['total_tokens']:,} tokens for 25 quotes")
            
            # Ensure directories exist
            print("\nEnsuring directories exist...")
            settings.paths.ensure_directories_exist()
            
        else:
            print("\n❌ Configuration validation failed")
        
        # Save settings
        print("\nSaving settings...")
        manager.save_settings()
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
