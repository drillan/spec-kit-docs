# Contributing to Spec Kit Docs

Thank you for your interest in contributing to spec-kit-docs! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment Setup](#development-environment-setup)
- [Running Tests](#running-tests)
- [Code Quality Standards](#code-quality-standards)
- [Pull Request Process](#pull-request-process)
- [Project Structure](#project-structure)
- [Coding Guidelines](#coding-guidelines)

## Code of Conduct

This project adheres to a code of conduct that all contributors are expected to follow. Please be respectful and constructive in all interactions.

## Getting Started

Before contributing, please:

1. Check the [issue tracker](https://github.com/driller/spec-kit-docs/issues) for existing issues
2. Read the [README.md](./README.md) to understand the project's goals and scope
3. Review this contributing guide completely

## Development Environment Setup

### Prerequisites

- **Python 3.11+** (3.13 recommended for development)
- **uv** package manager ([installation guide](https://docs.astral.sh/uv/))
- **Git** for version control
- **spec-kit** for testing integration ([installation guide](https://github.com/github/spec-kit))

### Setup Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/driller/spec-kit-docs.git
   cd spec-kit-docs
   ```

2. **Install dependencies and package in editable mode**:
   ```bash
   # Install all dependencies including dev dependencies
   uv sync --all-extras --dev

   # Or install in editable mode for active development
   uv pip install -e .
   ```

3. **Verify installation**:
   ```bash
   # Run tests to verify setup
   uv run pytest tests/
   ```

4. **Install pre-commit hooks** (optional but recommended):
   ```bash
   uv run pre-commit install
   ```

### Project Dependencies

The project uses:
- **uv**: For package management and virtual environments
- **pytest**: For testing
- **mypy**: For static type checking
- **ruff**: For linting
- **black**: For code formatting
- **pytest-cov**: For code coverage measurement

## Running Tests

### Run All Tests

```bash
uv run pytest tests/
```

### Run Specific Test Categories

```bash
# Unit tests only
uv run pytest tests/unit/

# Integration tests only
uv run pytest tests/integration/

# Performance tests
uv run pytest tests/performance/

# Contract tests
uv run pytest tests/contract/
```

### Run Tests with Coverage

```bash
# Generate coverage report
uv run pytest tests/ --cov=src/speckit_docs --cov-report=term-missing --cov-report=html

# View HTML coverage report
open htmlcov/index.html
```

### Run Specific Tests

```bash
# Run a specific test file
uv run pytest tests/unit/test_models.py

# Run a specific test function
uv run pytest tests/unit/test_models.py::test_feature_creation

# Run tests matching a pattern
uv run pytest -k "test_sphinx"
```

## Code Quality Standards

All code must meet the following quality standards before being merged:

### 1. Type Safety (mypy)

All code must pass mypy strict mode:

```bash
uv run mypy src/ --strict
```

Requirements:
- All functions must have type annotations
- No `Any` types without justification
- No `type: ignore` comments without explanation

### 2. Linting (ruff)

Code must pass ruff linting:

```bash
uv run ruff check .
```

Ruff checks for:
- Code style violations
- Common errors and anti-patterns
- Import organization
- Unused variables and imports

### 3. Formatting (black)

Code must be formatted with Black:

```bash
# Check formatting
uv run black --check src/ tests/

# Apply formatting
uv run black src/ tests/
```

### 4. Testing

- New features must include tests
- Bug fixes should include regression tests
- Aim for >80% code coverage for new code
- All tests must pass before merging

### 5. Documentation

- All public functions and classes must have docstrings
- Docstrings should follow Google style
- Update README.md for user-facing changes
- Add inline comments for complex logic

### Running All Quality Checks

Run all quality checks at once:

```bash
# Lint
uv run ruff check .

# Format check
uv run black --check src/ tests/

# Type check
uv run mypy src/ --strict

# Tests with coverage
uv run pytest tests/ --cov=src/speckit_docs --cov-report=term-missing
```

## Pull Request Process

### Before Submitting

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding guidelines

3. **Run all quality checks**:
   ```bash
   uv run ruff check .
   uv run black src/ tests/
   uv run mypy src/ --strict
   uv run pytest tests/
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: Add your feature description"
   ```

   Use conventional commit messages:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation changes
   - `test:` for test additions/changes
   - `refactor:` for code refactoring
   - `style:` for formatting changes
   - `chore:` for maintenance tasks

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

### Submitting the PR

1. Go to the [GitHub repository](https://github.com/driller/spec-kit-docs)
2. Click "New Pull Request"
3. Select your feature branch
4. Fill out the PR template:
   - **Title**: Brief description of changes
   - **Description**:
     - What changes were made
     - Why they were made
     - How to test them
   - **Issue Reference**: Link related issues (e.g., "Fixes #123")
   - **Checklist**: Complete the PR checklist

### PR Review Process

1. **Automated Checks**: CI will run all tests and quality checks
2. **Code Review**: A maintainer will review your code
3. **Feedback**: Address any requested changes
4. **Approval**: Once approved, a maintainer will merge your PR

### PR Checklist

Before submitting, ensure:

- [ ] Code follows project style guidelines
- [ ] All tests pass (`uv run pytest tests/`)
- [ ] Type checking passes (`uv run mypy src/ --strict`)
- [ ] Linting passes (`uv run ruff check .`)
- [ ] Formatting is correct (`uv run black --check src/ tests/`)
- [ ] Documentation is updated (if needed)
- [ ] New tests are added for new features
- [ ] Commit messages follow conventional commit format
- [ ] PR description clearly explains the changes

## Project Structure

```
spec-kit-docs/
├── src/speckit_docs/          # Main package source code
│   ├── cli/                   # CLI handlers and commands
│   ├── generators/            # Documentation generators (Sphinx, MkDocs)
│   ├── parsers/               # Markdown and feature parsers
│   ├── scripts/               # Backend scripts (doc_init, doc_update)
│   ├── templates/             # Jinja2 templates
│   ├── utils/                 # Utility functions
│   ├── models.py              # Data models
│   └── exceptions.py          # Custom exceptions
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   ├── performance/           # Performance tests
│   └── contract/              # Contract tests
├── specs/                     # Spec-kit feature specifications
├── .github/workflows/         # GitHub Actions CI configuration
├── pyproject.toml             # Project configuration and dependencies
├── README.md                  # User documentation
└── CONTRIBUTING.md            # This file
```

### Key Modules

- **`cli/`**: Command-line interface and installation handlers
- **`generators/`**: Core documentation generation logic
  - `base.py`: Abstract base generator
  - `sphinx.py`: Sphinx-specific implementation
  - `mkdocs.py`: MkDocs-specific implementation
- **`parsers/`**: Parsing spec.md, plan.md, and markdown files
- **`models.py`**: Data models (Feature, Section, etc.)
- **`utils/`**: Helper functions for git, validation, etc.

## Coding Guidelines

### Python Style

Follow PEP 8 with these specifics:

- Line length: 100 characters (enforced by Black)
- Use type hints for all function signatures
- Prefer dataclasses for data structures
- Use f-strings for string formatting
- Avoid `Any` type unless absolutely necessary

### Type Annotations

```python
# Good
def process_feature(feature: Feature) -> Document:
    """Process a feature and return a document."""
    ...

# Bad
def process_feature(feature):
    """Process a feature and return a document."""
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def generate_docs(features: list[Feature], output_dir: Path) -> None:
    """Generate documentation from features.

    Args:
        features: List of Feature objects to process
        output_dir: Directory to write generated docs

    Raises:
        DocumentationError: If generation fails
    """
    ...
```

### Error Handling

- Use custom exceptions from `exceptions.py`
- Provide clear error messages
- Include actionable suggestions in exceptions

```python
# Good
raise DocumentationError(
    "Failed to generate documentation",
    "Check that the docs/ directory is writable"
)

# Bad
raise Exception("Error")
```

### Testing

- Write unit tests for all new functions
- Use descriptive test names
- Follow AAA pattern: Arrange, Act, Assert
- Use fixtures for common test data

```python
def test_feature_parsing_with_valid_spec(tmp_path):
    """Test that feature parsing works with a valid spec.md."""
    # Arrange
    spec_file = tmp_path / "spec.md"
    spec_file.write_text("# Feature Title\n\nContent")

    # Act
    feature = Feature.parse(spec_file)

    # Assert
    assert feature.title == "Feature Title"
```

## Development Workflow

### Working with spec-kit

To test integration with spec-kit:

1. Create a test spec-kit project:
   ```bash
   mkdir /tmp/test-project
   cd /tmp/test-project
   specify init . --ai claude
   ```

2. Install spec-kit-docs:
   ```bash
   uv run python -c "from speckit_docs.cli.install_handler import install_handler; install_handler()"
   ```

3. Test documentation generation:
   ```bash
   /speckit.doc-init Create Sphinx documentation
   /speckit.doc-update
   ```

### Debugging

- Use `pytest -vv` for verbose test output
- Use `pytest -s` to see print statements
- Use `pytest --pdb` to drop into debugger on failure
- Use `uv run python -m pdb script.py` for script debugging

## Questions or Need Help?

- Open an issue for bugs or feature requests
- Start a discussion for questions
- Check existing issues and PRs first

Thank you for contributing to spec-kit-docs!
