#!/usr/bin/env python3
"""
Auto-lint and format watcher for Python projects.

Automatically formats code, sorts imports, and checks linter errors
whenever a Python file is modified or saved.
"""

import subprocess
import sys
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent

# Replace with your project directory or pass as argument
PROJECT_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()

# Configuration
FORMATTING_TOOLS = {"black": "black", "isort": "isort", "flake8": "flake8"}


def check_tool_availability():
    """Check if required formatting tools are available."""
    missing_tools = []
    for tool_name, command in FORMATTING_TOOLS.items():
        try:
            subprocess.run([command, "--version"], capture_output=True, check=True)
            print(f"✓ {tool_name} is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing_tools.append(tool_name)
            print(f"✗ {tool_name} is not available")

    if missing_tools:
        print(f"\nMissing tools: {', '.join(missing_tools)}")
        print("Please install them with: pip install black isort flake8")
        return False
    return True


def run_command(command):
    """Run a shell command and print output."""
    try:
        # Split command into parts and use list-based execution to avoid path issues
        if isinstance(command, str):
            # For simple commands, split into parts
            if command.startswith("black "):
                parts = ["black", command[6:]]  # Remove 'black ' prefix
            elif command.startswith("isort "):
                parts = ["isort", command[7:]]  # Remove 'isort ' prefix
            elif command.startswith("flake8 "):
                parts = ["flake8", command[8:]]  # Remove 'flake8 ' prefix
            else:
                parts = command.split()
        else:
            parts = command

        result = subprocess.run(parts, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command '{command}': {e}")
        return False


def format_and_lint(file_path):
    """Run Black, isort, and flake8 on the file or directory."""
    print(f"\n🔄 Processing: {file_path}")

    success_count = 0
    total_tools = len(FORMATTING_TOOLS)

    # Run Black (formatter)
    if run_command(f"black {file_path}"):
        success_count += 1
        print("✓ Black formatting completed")

    # Run isort (import sorter)
    if run_command(f"isort {file_path}"):
        success_count += 1
        print("✓ isort import sorting completed")

    # Run flake8 (linter)
    if run_command(f"flake8 {file_path}"):
        success_count += 1
        print("✓ flake8 linting completed")

    if success_count == total_tools:
        print("🎉 All formatting tools completed successfully!")
    else:
        print(f"⚠️  {total_tools - success_count} tool(s) had issues")
    print()


class PythonFileHandler(FileSystemEventHandler):
    """Handles file change events for Python files."""

    def __init__(self):
        self.last_processed = {}  # Track last processing time to avoid duplicates
        self.event_count = 0

    def should_process(self, file_path):
        """Check if file should be processed (avoid duplicate processing)."""
        current_time = time.time()
        if file_path in self.last_processed:
            if (
                current_time - self.last_processed[file_path] < 0.5
            ):  # Reduced to 0.5 second cooldown
                return False
        self.last_processed[file_path] = current_time
        return True

    def on_any_event(self, event):
        """Log all events for debugging."""
        if hasattr(event, "src_path") and event.src_path.endswith(".py"):
            self.event_count += 1
            event_type = type(event).__name__
            print(f"🔍 Event #{self.event_count}: {event_type} - {event.src_path}")

    def on_modified(self, event):
        """Handle file modification events (triggers on save)."""
        if event.src_path.endswith(".py") and self.should_process(event.src_path):
            print(f"💾 File saved: {event.src_path}")
            format_and_lint(event.src_path)

    def on_created(self, event):
        """Handle file creation events."""
        if event.src_path.endswith(".py") and self.should_process(event.src_path):
            print(f"🆕 File created: {event.src_path}")
            format_and_lint(event.src_path)

    def on_moved(self, event):
        """Handle file move/rename events."""
        if event.dest_path.endswith(".py") and self.should_process(event.dest_path):
            print(f"🔄 File moved: {event.dest_path}")
            format_and_lint(event.dest_path)


def create_config_files():
    """Create configuration files if they don't exist."""
    configs = {
        ".flake8": """[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = 
    .git,
    __pycache__,
    .venv,
    venv,
    .env,
    chroma_db
""",
        "pyproject.toml": """[tool.black]
line-length = 88
target-version = ['py38']
include = '\\.pyi?$'
extend-exclude = '''
/(
  # directories
  \\.git
  | \\.hg
  | \\.mypy_cache
  | \\.tox
  | \\.venv
  | venv
  | _build
  | buck-out
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["flexxray"]
""",
    }

    for filename, content in configs.items():
        config_path = PROJECT_PATH / filename
        if not config_path.exists():
            with open(config_path, "w") as f:
                f.write(content)
            print(f"📝 Created {filename}")


def main():
    print(f"🔍 Auto-format watcher starting...")
    print(f"📁 Watching Python files in: {PROJECT_PATH}")
    print(f"💡 This script triggers on file SAVE events, not keystrokes")
    print(f"💡 Make sure your editor saves files (Ctrl+S) to trigger formatting")

    # Check tool availability
    if not check_tool_availability():
        print("\n❌ Cannot start watcher - missing required tools")
        sys.exit(1)

    # Create configuration files
    create_config_files()

    print("\n🚀 Starting file watcher...")
    print("📝 Save any Python file to trigger formatting")
    print("🔍 All file events will be logged for debugging")
    print("⏹️  Press Ctrl+C to stop\n")

    event_handler = PythonFileHandler()
    observer = Observer()
    observer.schedule(event_handler, str(PROJECT_PATH), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopping watcher...")
        observer.stop()
    observer.join()
    print("👋 Watcher stopped")


if __name__ == "__main__":
    main()
