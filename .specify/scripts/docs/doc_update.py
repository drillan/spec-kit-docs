#!/usr/bin/env python3
"""
doc_update.py - Update documentation from specifications

This script wraps src/speckit_docs/doc_update.py for spec-kit integration.
Executed by /doc-update command.
"""
import sys
from pathlib import Path

# Add src directory to path to import speckit_docs module
repo_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(repo_root / "src"))

# Import and execute main function from src
from speckit_docs.doc_update import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
