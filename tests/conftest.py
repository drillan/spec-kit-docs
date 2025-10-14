"""Pytest configuration and shared fixtures for speckit-docs tests."""

from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem


@pytest.fixture
def fs(fs: FakeFilesystem) -> Generator[FakeFilesystem, None, None]:
    """Provide pyfakefs filesystem fixture.

    This fixture enables filesystem mocking for all file operations in tests.
    All file I/O operations will use the fake filesystem instead of the real one.

    Args:
        fs: The pyfakefs filesystem fixture (automatically provided by pyfakefs)

    Yields:
        FakeFilesystem: The mocked filesystem instance
    """
    yield fs


@pytest.fixture
def mock_speckit_project(fs: FakeFilesystem) -> Path:
    """Create a mock spec-kit project structure for testing.

    Creates a minimal but valid spec-kit project directory structure with:
    - .specify/ directory
    - specs/ directory with one sample feature
    - .gitignore file
    - pyproject.toml file

    Args:
        fs: The pyfakefs filesystem fixture

    Returns:
        Path: Path to the root of the mock spec-kit project
    """
    # Create project root
    project_root = Path("/tmp/test-speckit-project")
    fs.create_dir(project_root)

    # Create .specify directory structure
    specify_dir = project_root / ".specify"
    fs.create_dir(specify_dir / "scripts" / "docs")
    fs.create_dir(specify_dir / "memory")

    # Create specs directory with sample feature
    specs_dir = project_root / "specs"
    feature_dir = specs_dir / "001-sample-feature"
    fs.create_dir(feature_dir)

    # Create sample spec.md
    spec_content = """# Sample Feature

## Overview
This is a sample feature for testing.

## User Stories
- US1: As a user, I want to do something
- US2: As a developer, I want to implement something

## Requirements
- REQ-001: The system shall support something
- REQ-002: The system shall validate something
"""
    fs.create_file(feature_dir / "spec.md", contents=spec_content)

    # Create sample plan.md
    plan_content = """# Implementation Plan: Sample Feature

## Phase 0: Research
- Research complete

## Phase 1: Design
- Design complete

## Next Steps
- Implement tasks
"""
    fs.create_file(feature_dir / "plan.md", contents=plan_content)

    # Create sample tasks.md
    tasks_content = """# Tasks: Sample Feature

## Phase 1: Setup
- [ ] T001 Setup task 1
- [ ] T002 Setup task 2
"""
    fs.create_file(feature_dir / "tasks.md", contents=tasks_content)

    # Create .gitignore
    gitignore_content = """__pycache__/
*.pyc
.venv/
dist/
build/
"""
    fs.create_file(project_root / ".gitignore", contents=gitignore_content)

    # Create pyproject.toml
    pyproject_content = """[project]
name = "test-project"
version = "0.1.0"
"""
    fs.create_file(project_root / "pyproject.toml", contents=pyproject_content)

    return project_root


@pytest.fixture
def mock_sphinx_project(fs: FakeFilesystem, mock_speckit_project: Path) -> Path:
    """Create a mock Sphinx documentation project for testing.

    Creates a Sphinx documentation directory with configuration and sample pages.

    Args:
        fs: The pyfakefs filesystem fixture
        mock_speckit_project: Path to the mock spec-kit project

    Returns:
        Path: Path to the Sphinx docs directory
    """
    docs_dir = mock_speckit_project / "docs"
    fs.create_dir(docs_dir)

    # Create conf.py
    conf_content = """# Sphinx configuration
project = 'Test Project'
extensions = ['myst_parser']
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}
"""
    fs.create_file(docs_dir / "conf.py", contents=conf_content)

    # Create index.md
    index_content = """# Test Project Documentation

Welcome to the test project documentation.
"""
    fs.create_file(docs_dir / "index.md", contents=index_content)

    # Create features directory
    fs.create_dir(docs_dir / "features")

    return docs_dir


@pytest.fixture
def mock_mkdocs_project(fs: FakeFilesystem, mock_speckit_project: Path) -> Path:
    """Create a mock MkDocs documentation project for testing.

    Creates an MkDocs documentation directory with configuration and sample pages.

    Args:
        fs: The pyfakefs filesystem fixture
        mock_speckit_project: Path to the mock spec-kit project

    Returns:
        Path: Path to the MkDocs docs directory
    """
    docs_dir = mock_speckit_project / "docs"
    fs.create_dir(docs_dir)

    # Create mkdocs.yml
    mkdocs_content = """site_name: Test Project
theme:
  name: material
nav:
  - Home: index.md
  - Features: features/
"""
    fs.create_file(
        mock_speckit_project / "mkdocs.yml",
        contents=mkdocs_content,
    )

    # Create index.md
    index_content = """# Test Project Documentation

Welcome to the test project documentation.
"""
    fs.create_file(docs_dir / "index.md", contents=index_content)

    # Create features directory
    fs.create_dir(docs_dir / "features")

    return docs_dir


@pytest.fixture
def sample_feature_data() -> dict[str, Any]:
    """Provide sample feature data for testing.

    Returns:
        dict: Sample feature data with title, overview, user stories, etc.
    """
    return {
        "title": "Sample Feature",
        "overview": "This is a sample feature for testing.",
        "user_stories": [
            "US1: As a user, I want to do something",
            "US2: As a developer, I want to implement something",
        ],
        "requirements": [
            "REQ-001: The system shall support something",
            "REQ-002: The system shall validate something",
        ],
        "feature_dir": Path("/tmp/test-speckit-project/specs/001-sample-feature"),
    }
