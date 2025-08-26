#!/usr/bin/env python3
"""
Migration Script: Old Configuration System to Unified Settings

This script helps migrate from the old scattered configuration system
(env_config.py, config_manager.py, company_config.py) to the new
unified settings.py system.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, Any, List

# Import the new unified settings system
from settings import SettingsManager, CompanyConfig, OpenAIConfig


def backup_old_config_files():
    """Create backups of old configuration files."""
    backup_dir = Path("config_backup")
    backup_dir.mkdir(exist_ok=True)
    
    old_files = [
        "env_config.py",
        "config_manager.py", 
        "company_config.py",
        "company_settings.json"
    ]
    
    print("📁 Creating backups of old configuration files...")
    
    for file_name in old_files:
        if os.path.exists(file_name):
            backup_path = backup_dir / file_name
            shutil.copy2(file_name, backup_path)
            print(f"   ✅ Backed up: {file_name} → {backup_path}")
        else:
            print(f"   ⚠️  File not found: {file_name}")
    
    return backup_dir


def migrate_company_configs():
    """Migrate company configurations from the old system."""
    print("\n🏢 Migrating company configurations...")
    
    # Import old company config to get existing companies
    try:
        from company_config import COMPANY_CONFIGS
        
        migrated_companies = {}
        
        for company_name, old_config in COMPANY_CONFIGS.items():
            print(f"   Processing company: {company_name}")
            
            # Convert old CompanyConfig to new CompanyConfig
            new_config = CompanyConfig(
                name=old_config.name,
                display_name=old_config.display_name,
                transcript_directory=old_config.transcript_directory,
                output_prefix=old_config.output_prefix,
                key_questions=old_config.key_questions,
                question_categories=old_config.question_categories,
                speaker_patterns=old_config.speaker_patterns,
                business_insights=old_config.business_insights,
                topic_synonyms=old_config.topic_synonyms,
                industry_keywords=old_config.industry_keywords,
                company_specific_terms=old_config.company_specific_terms
            )
            
            migrated_companies[company_name] = new_config
            print(f"   ✅ Migrated: {company_name}")
        
        return migrated_companies
        
    except ImportError as e:
        print(f"   ⚠️  Could not import old company config: {e}")
        return {}


def migrate_environment_settings():
    """Migrate environment-specific settings."""
    print("\n🌍 Migrating environment settings...")
    
    # Get OpenAI API key from environment
    api_key = os.getenv("OPENAI_API_KEY", "")
    
    # Create OpenAI configuration
    openai_config = OpenAIConfig(
        api_key=api_key,
        model_for_summary=os.getenv("OPENAI_MODEL_FOR_SUMMARY", "gpt-4o"),
        model_token_limit=int(os.getenv("MODEL_TOKEN_LIMIT", "128000")),
        max_quotes_for_analysis=int(os.getenv("MAX_QUOTES_FOR_ANALYSIS", "30")),
        max_tokens_per_quote=int(os.getenv("MAX_TOKENS_PER_QUOTE", "150")),
        enable_token_logging=os.getenv("ENABLE_TOKEN_LOGGING", "true").lower() in ("true", "1", "yes")
    )
    
    print(f"   ✅ OpenAI config: {openai_config.model_for_summary}")
    print(f"   ✅ Max quotes: {openai_config.max_quotes_for_analysis}")
    
    return openai_config


def create_migration_report(backup_dir: Path, migrated_companies: Dict, openai_config: OpenAIConfig):
    """Create a detailed migration report."""
    report_file = "CONFIGURATION_MIGRATION_REPORT.md"
    
    report_content = f"""# Configuration Migration Report

## Migration Summary

This report documents the migration from the old scattered configuration system to the new unified `settings.py` system.

## What Was Migrated

### 1. Company Configurations
- **Total Companies**: {len(migrated_companies)}
- **Companies**: {', '.join(migrated_companies.keys())}

### 2. OpenAI Configuration
- **Model**: {openai_config.model_for_summary}
- **Max Quotes**: {openai_config.max_quotes_for_analysis}
- **Token Limit**: {openai_config.model_token_limit:,}

### 3. Backup Files
- **Backup Directory**: {backup_dir}
- **Files Backed Up**: {len(list(backup_dir.glob('*')))}

## Migration Steps Completed

1. ✅ Created backups of old configuration files
2. ✅ Migrated company configurations
3. ✅ Migrated environment settings
4. ✅ Created new unified settings system
5. ✅ Generated migration report

## Next Steps

### For Developers
1. Update imports in your code:
   ```python
   # OLD
   from env_config import get_openai_api_key
   from config_manager import get_config_manager
   
   # NEW
   from settings import get_openai_api_key, get_config_manager
   ```

2. Update configuration access:
   ```python
   # OLD
   config = get_env_config()
   max_quotes = config.max_quotes_for_analysis
   
   # NEW
   from settings import get_settings
   settings = get_settings()
   max_quotes = settings.openai.max_quotes_for_analysis
   ```

### For Users
1. The new system automatically loads from:
   - Environment variables
   - `settings.json` file (if exists)
   - Default values

2. Company switching works the same way:
   ```python
   from settings import switch_company
   switch_company("flexxray")
   ```

## Rollback Instructions

If you need to rollback to the old system:

1. Restore files from backup:
   ```bash
   cp config_backup/env_config.py .
   cp config_backup/config_manager.py .
   cp config_backup/company_config.py .
   ```

2. Update imports back to old modules

## Benefits of New System

- **Single Source of Truth**: All configuration in one place
- **Type Safety**: Pydantic validation and type checking
- **Layered Configuration**: Defaults → Environment → Company → Runtime
- **Better Testing**: Easier to mock and test configurations
- **Cloud Ready**: Better support for multi-tenant and cloud deployments

## Support

If you encounter issues during migration:
1. Check this migration report
2. Review the backup files in `{backup_dir}`
3. Consult the new `settings.py` documentation
4. Test with the new system using `python settings.py`

---
*Migration completed on: {os.popen('date').read().strip()}*
"""
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n📋 Migration report created: {report_file}")
    return report_file


def update_imports_in_files():
    """Update import statements in Python files to use the new settings system."""
    print("\n🔄 Updating import statements in Python files...")
    
    # Files that need import updates
    files_to_update = [
        "quote_analysis_tool.py",
        "workflow_manager.py",
        "quote_analysis_core.py",
        "perspective_analysis_refactored.py",
        "quote_ranking.py",
        "theme_analysis.py",
        "batch_manager.py",
        "summary_generation.py",
        "vector_database.py"
    ]
    
    import_mappings = {
        "from env_config import": "from settings import",
        "from config_manager import": "from settings import",
        "from company_config import": "from settings import"
    }
    
    updated_files = []
    
    for file_name in files_to_update:
        if not os.path.exists(file_name):
            print(f"   ⚠️  File not found: {file_name}")
            continue
        
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Update imports
            for old_import, new_import in import_mappings.items():
                if old_import in content:
                    content = content.replace(old_import, new_import)
            
            # Update specific function calls
            content = content.replace("get_env_config()", "get_settings()")
            content = content.replace("get_config_manager()", "get_settings_manager()")
            
            # Only write if content changed
            if content != original_content:
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(content)
                updated_files.append(file_name)
                print(f"   ✅ Updated: {file_name}")
            else:
                print(f"   ℹ️  No changes needed: {file_name}")
                
        except Exception as e:
            print(f"   ❌ Error updating {file_name}: {e}")
    
    return updated_files


def main():
    """Main migration function."""
    print("=" * 60)
    print("CONFIGURATION SYSTEM MIGRATION")
    print("=" * 60)
    
    try:
        # Step 1: Backup old files
        backup_dir = backup_old_config_files()
        
        # Step 2: Migrate company configurations
        migrated_companies = migrate_company_configs()
        
        # Step 3: Migrate environment settings
        openai_config = migrate_environment_settings()
        
        # Step 4: Create migration report
        report_file = create_migration_report(backup_dir, migrated_companies, openai_config)
        
        # Step 5: Update imports in Python files
        updated_files = update_imports_in_files()
        
        # Step 6: Test new system
        print("\n🧪 Testing new unified settings system...")
        try:
            from settings import get_settings_manager
            manager = get_settings_manager()
            settings = manager.settings
            
            if settings.validate_configuration():
                print("   ✅ New settings system working correctly")
                
                # Save initial settings
                manager.save_settings()
                print("   ✅ Initial settings saved to settings.json")
                
            else:
                print("   ❌ New settings system validation failed")
                
        except Exception as e:
            print(f"   ❌ Error testing new system: {e}")
        
        # Summary
        print("\n" + "=" * 60)
        print("MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"📁 Backups created in: {backup_dir}")
        print(f"📋 Migration report: {report_file}")
        print(f"🏢 Companies migrated: {len(migrated_companies)}")
        print(f"🔄 Files updated: {len(updated_files)}")
        print(f"⚙️  New settings file: settings.json")
        
        print("\n🎯 Next Steps:")
        print("1. Review the migration report")
        print("2. Test your application with the new system")
        print("3. Remove old config files when ready")
        print("4. Update any remaining import statements")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
