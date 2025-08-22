# Cursor Environment Configuration Guide

## Overview
This workspace is now fully configured to automatically load environment variables from the `.env` file in Cursor. The configuration ensures that your OpenAI API key and other environment variables are automatically available when running Python scripts, debugging, or using the integrated terminal.

## What's Been Configured

### 1. `.vscode/settings.json`
- **Python Environment**: Automatically uses the virtual environment (`./venv/Scripts/python.exe`)
- **Environment File**: Automatically loads `.env` file (`python.envFile: "${workspaceFolder}/.env"`)
- **Auto-activation**: Terminal automatically activates the virtual environment
- **Code Analysis**: Enhanced Python IntelliSense and type checking
- **Formatting**: Auto-formatting with Black on save
- **Linting**: Flake8 linting enabled

### 2. `.vscode/launch.json`
- **Debug Configurations**: Multiple pre-configured debug profiles
- **Environment Loading**: All debug sessions automatically load `.env` variables
- **Python Path**: Correctly configured Python interpreter path
- **Working Directory**: Proper workspace folder setup

### 3. `.vscode/tasks.json`
- **Build Tasks**: Pre-configured tasks for running main scripts
- **Environment Variables**: All tasks automatically load `.env` variables
- **Dependency Management**: Task for installing requirements

## How It Works

### Automatic Environment Loading
1. **Python Extension**: Automatically detects and loads `.env` file
2. **Terminal**: Integrated terminal automatically loads environment variables
3. **Debug Sessions**: All debugging automatically includes environment variables
4. **Tasks**: All build tasks automatically include environment variables

### Environment Variables Available
- `OPENAI_API_KEY`: Your OpenAI API key (automatically loaded)
- `DEBUG`: Debug mode setting
- Any additional variables you add to `.env`

## Usage

### Running Scripts
- **Terminal**: Just run `python script.py` - environment variables are automatically loaded
- **Debug**: Use F5 or the debug panel - environment variables are automatically available
- **Tasks**: Use Ctrl+Shift+P → "Tasks: Run Task" - environment variables are automatically loaded

### Adding New Environment Variables
1. Add variables to your `.env` file
2. They're automatically available in all Python scripts
3. No need to manually load them - it's handled automatically

### Virtual Environment
- **Automatic Activation**: Terminal automatically activates when opened
- **Python Path**: Correctly configured for IntelliSense and debugging
- **Dependencies**: All packages from `requirements.txt` are available

## Verification

To verify the configuration is working:

1. **Check Python Interpreter**: 
   - Ctrl+Shift+P → "Python: Select Interpreter"
   - Should show `./venv/Scripts/python.exe`

2. **Test Environment Variables**:
   ```python
   import os
   print(os.getenv('OPENAI_API_KEY'))  # Should show your API key
   ```

3. **Run a Script**:
   - Open any Python file
   - Press F5 to debug
   - Environment variables should be available

## Troubleshooting

### Environment Variables Not Loading
1. Ensure `.env` file exists in workspace root
2. Check that `.env` file has correct format (no spaces around `=`)
3. Restart Cursor after making changes to `.env`

### Python Interpreter Issues
1. Verify virtual environment exists: `./venv/Scripts/python.exe`
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Reload Cursor window: Ctrl+Shift+P → "Developer: Reload Window"

### Debug Configuration Issues
1. Check that `.vscode/launch.json` exists
2. Verify Python extension is installed
3. Restart debugging session

## Benefits

✅ **Automatic Loading**: No need to manually load `.env` files  
✅ **Integrated Experience**: Works seamlessly with Cursor's Python tools  
✅ **Debug Support**: Environment variables available in all debug sessions  
✅ **Task Integration**: All build tasks automatically include environment variables  
✅ **Terminal Integration**: Integrated terminal automatically loads environment variables  
✅ **IntelliSense**: Enhanced code completion and analysis  

## Security Note

- The `.env` file is already in `.gitignore` to prevent accidental commits
- Never commit API keys or sensitive information to version control
- The configuration automatically loads from `.env` but doesn't expose it in the UI

Your workspace is now fully configured for automatic environment variable loading! 🎉

