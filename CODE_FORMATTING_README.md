# Code Formatting & Linting Setup

This project now includes automated code formatting and linting tools to maintain consistent code quality and style.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Option A: Use the setup script (recommended)
python setup_formatting.py

# Option B: Install manually
pip install black isort flake8 watchdog
```

### 2. Run Auto-Formatter
```bash
# Start watching for file changes
python auto_format.py

# Or format all files once
black .
isort .
flake8 .
```

## 🛠️ Tools Included

- **Black**: Code formatter that enforces consistent Python style
- **isort**: Import statement organizer and sorter
- **flake8**: Linter that checks for style and potential errors
- **watchdog**: File system monitoring for automatic formatting

## 📁 Configuration Files

The setup automatically creates:

- **`.flake8`**: Linting rules and exclusions
- **`pyproject.toml`**: Black and isort configuration

### Key Settings
- Line length: 88 characters (Black default)
- Target Python version: 3.8+
- Excludes: `__pycache__`, `venv`, `.env`, `chroma_db`
- isort profile: Black-compatible

## 🔄 Auto-Formatting

### Start the Watcher
```bash
python auto_format.py
```

The watcher will:
- **Monitor file SAVE events** (not keystrokes)
- Automatically format files when saved/modified
- Avoid duplicate processing with a 0.5-second cooldown
- Show real-time progress with emojis and status indicators
- Log all file events for debugging

### ⚠️ Important: Save Detection
The formatter triggers when you **save a file** (Ctrl+S), not on every keystroke. This is the intended behavior for performance reasons.

### Stop the Watcher
Press `Ctrl+C` to stop the file watcher.

## 🧪 Testing Save Detection

Use the included test script to verify save detection is working:

```bash
# Terminal 1: Start the formatter
python auto_format.py

# Terminal 2: Create a test file
python test_save_detection.py

# Then edit and save the test file in your editor
```

## 📝 Manual Formatting

### Format a Single File
```bash
black filename.py
isort filename.py
flake8 filename.py
```

### Format All Files
```bash
# Format all Python files
black .

# Sort imports in all files
isort .

# Lint all files
flake8 .
```

## ⚙️ Customization

### Modify Black Settings
Edit `pyproject.toml`:
```toml
[tool.black]
line-length = 88  # Change line length
target-version = ['py38']  # Target Python version
```

### Modify Flake8 Rules
Edit `.flake8`:
```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503  # Add/remove error codes
```

### Modify isort Settings
Edit `pyproject.toml`:
```toml
[tool.isort]
profile = "black"
line_length = 88
known_first_party = ["flexxray"]  # Add your package names
```

## 🐛 Troubleshooting

### Common Issues

1. **Tools not found**
   ```bash
   pip install black isort flake8 watchdog
   ```

2. **Permission errors**
   - On Windows: Run as Administrator
   - On Unix: Use `sudo pip install` or virtual environment

3. **Configuration conflicts**
   - Delete existing `.flake8` or `pyproject.toml`
   - Re-run `python auto_format.py` to recreate

4. **Save events not detected**
   - Make sure you're saving files (Ctrl+S), not just typing
   - Check that the file path ends with `.py`
   - Verify the watcher is running in the correct directory
   - Use `test_save_detection.py` to test the setup

### Reset Configuration
```bash
# Remove config files
rm .flake8 pyproject.toml

# Recreate with defaults
python auto_format.py
```

## 📚 Best Practices

1. **Run before commits**: Format code before pushing changes
2. **IDE integration**: Configure your editor to use Black/isort
3. **CI/CD**: Add formatting checks to your build pipeline
4. **Team consistency**: Everyone should use the same configuration
5. **Save frequently**: The formatter only runs when you save files

## 🔗 Useful Commands

```bash
# Check what would be formatted (without changing)
black --check .

# Show diff of what would change
black --diff .

# Check import sorting
isort --check-only .

# Show flake8 errors only
flake8 --select=E,W
```

## 📖 Additional Resources

- [Black Documentation](https://black.readthedocs.io/)
- [isort Documentation](https://pycqa.github.io/isort/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [Python Style Guide (PEP 8)](https://www.python.org/dev/peps/pep-0008/)

