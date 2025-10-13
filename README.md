<div align="center">
    <h1>📚 Spec Kit Docs</h1>
    <h3><em>AI-driven documentation generation for spec-kit projects.</em></h3>
</div>

<p align="center">
    <strong>Automatically generate and maintain Sphinx or MkDocs documentation from your spec-kit specifications.</strong>
</p>

<p align="center">
    <a href="https://github.com/driller/spec-kit-docs/actions/workflows/test.yml"><img src="https://github.com/driller/spec-kit-docs/actions/workflows/test.yml/badge.svg" alt="Tests"/></a>
    <a href="https://github.com/driller/spec-kit-docs/blob/main/LICENSE"><img src="https://img.shields.io/github/license/driller/spec-kit-docs" alt="License"/></a>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.11+-blue.svg" alt="Python 3.11+"/></a>
</p>

---

## Table of Contents

- [🤔 What is Spec Kit Docs?](#-what-is-spec-kit-docs)
- [⚡ Get started](#-get-started)
- [🤖 Supported Documentation Tools](#-supported-documentation-tools)
- [🔧 Command Reference](#-command-reference)
- [📚 Core philosophy](#-core-philosophy)
- [🎯 Features](#-features)
- [🔧 Prerequisites](#-prerequisites)
- [📖 Learn more](#-learn-more)
- [📋 Detailed process](#-detailed-process)
- [🔍 Troubleshooting](#-troubleshooting)
- [👥 Maintainers](#-maintainers)
- [💬 Support](#-support)
- [📄 License](#-license)

## 🤔 What is Spec Kit Docs?

**Spec Kit Docs** is an extension for [spec-kit](https://github.com/github/spec-kit) that automates documentation generation from your specifications. Instead of manually maintaining documentation alongside your code, Spec Kit Docs automatically generates and updates Sphinx or MkDocs documentation directly from your `spec.md`, `plan.md`, and `tasks.md` files.

**Note**: Spec Kit Docs requires an existing spec-kit installation and project. If you haven't used spec-kit before, please install it first by following the [spec-kit documentation](https://github.com/github/spec-kit).

## ⚡ Get started

### 0. Prerequisites: Install spec-kit

Spec Kit Docs requires an existing spec-kit project. If you haven't installed spec-kit yet:

```bash
# Install spec-kit CLI
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git

# Initialize your project
specify init your-project --ai claude
cd your-project
```

For more details, see the [spec-kit documentation](https://github.com/github/spec-kit).

### 1. Install spec-kit-docs

Once you have a spec-kit project, initialize spec-kit-docs in your project directory:

```bash
# In your existing spec-kit project
cd your-spec-kit-project

# Run initialization
uv run python /path/to/spec-kit-docs/.specify/scripts/docs/doc_init.py --tool sphinx
```

Or use MkDocs:

```bash
uv run python /path/to/spec-kit-docs/.specify/scripts/docs/doc_init.py --tool mkdocs
```

This will:
- Create `/doc-init` and `/doc-update` slash commands in `.claude/commands/`
- Set up the basic documentation structure
- Configure your chosen documentation tool (Sphinx or MkDocs)

### 2. Initialize documentation

Use the **`/doc-init`** command to set up your documentation project:

```bash
/doc-init I want to create Sphinx documentation with a clean, modern theme. Include API reference and feature documentation.
```

Or for MkDocs:

```bash
/doc-init I want to create MkDocs documentation with the Material theme. Include user guides and API documentation.
```

### 3. Update documentation

After making changes to your specifications, use the **`/doc-update`** command to regenerate documentation:

```bash
/doc-update Update the documentation to reflect the latest changes in spec.md and plan.md
```

The command will:
- Parse all features in `specs/`
- Extract information from `spec.md`, `plan.md`, and `tasks.md`
- Generate or update corresponding documentation pages
- Maintain your documentation structure and navigation

## 🤖 Supported Documentation Tools

| Tool                                    | Support | Notes                                             |
|-----------------------------------------|---------|---------------------------------------------------|
| [Sphinx](https://www.sphinx-doc.org/)   | ✅ | Supports MyST (Markdown) and reStructuredText    |
| [MkDocs](https://www.mkdocs.org/)       | ✅ | Supports Material theme and custom themes        |

## 🔧 Command Reference

### Available Slash Commands

After running initialization, your AI coding agent will have access to these slash commands:

| Command        | Description                                                           |
|----------------|-----------------------------------------------------------------------|
| `/doc-init`    | Initialize Sphinx or MkDocs documentation project for spec-kit       |
| `/doc-update`  | Update documentation from spec-kit features                           |

### Command Details

#### `/doc-init`

Initializes a new documentation project in your spec-kit repository.

**Arguments**:
- Natural language description of your documentation requirements (tool, theme, structure)

**Examples**:
```bash
/doc-init Create Sphinx documentation with RTD theme
/doc-init Set up MkDocs with Material theme for our API documentation
```

**What it does**:
1. Detects your project structure and spec-kit features
2. Creates documentation directory (`docs/` by default)
3. Generates initial configuration (e.g., `conf.py` for Sphinx, `mkdocs.yml` for MkDocs)
4. Creates index page and basic structure
5. Generates initial feature documentation from existing specs

#### `/doc-update`

Updates existing documentation based on your spec-kit specifications.

**Arguments**:
- Optional: Natural language description of what to update

**Examples**:
```bash
/doc-update
/doc-update Regenerate all feature documentation
/doc-update Update only the API reference section
```

**What it does**:
1. Scans `specs/` directory for all features
2. Parses `spec.md`, `plan.md`, and `tasks.md` for each feature
3. Generates or updates feature documentation pages
4. Updates navigation structure (TOC tree or nav menu)
5. Preserves manually edited sections (via markers)

## 📚 Core philosophy

Spec Kit Docs is built on the following principles:

### spec-kit Integration First

Spec Kit Docs is designed as a **spec-kit extension**, not a standalone tool. It follows spec-kit's patterns and conventions:

- Uses `specs/` directory structure
- Supports `specify init --here` pattern
- Follows non-interactive execution model for CI/CD compatibility
- Respects project constitution and memory system

### Documentation as Code

Documentation should be:
- **Generated from specifications**: Single source of truth in `spec.md`, `plan.md`, `tasks.md`
- **Version controlled**: Tracked alongside code
- **Automatically updated**: Regenerated when specs change
- **Consistent**: Same structure and format across all features

### Non-Interactive Execution

All backend scripts operate without user prompts:
- Use command-line arguments for configuration
- Return structured errors for AI agent interpretation
- Support automated CI/CD workflows
- Enable deterministic testing

### Extensibility & Modularity

The system is designed for easy extension:
- Abstract base classes for documentation generators
- Independent modules for Sphinx and MkDocs
- Generic command templates for multiple AI agents
- Clear separation between parsing and generation

## 🎯 Features

### Automatic Feature Documentation

- Extracts user stories, requirements, and technical details from spec.md
- Generates implementation guides from plan.md
- Creates task lists and progress tracking from tasks.md
- Maintains cross-references between features

### Flexible Configuration

- Choose between Sphinx and MkDocs
- Customize themes and styling
- Configure documentation structure
- Preserve manual edits with markers

### AI Agent Integration

- Works with Claude Code, GitHub Copilot, Gemini CLI, and other spec-kit-compatible agents
- Natural language commands for initialization and updates
- Intelligent parsing of specifications
- Context-aware documentation generation

### Incremental Updates

- Update only changed features
- Preserve manual documentation sections
- Smart merge of generated and manual content
- Track documentation versions with git

## 🔧 Prerequisites

- **Linux/macOS** (or WSL2 on Windows)
- [spec-kit](https://github.com/github/spec-kit) installed and initialized
- AI coding agent: [Claude Code](https://www.anthropic.com/claude-code), [GitHub Copilot](https://code.visualstudio.com/), [Gemini CLI](https://github.com/google-gemini/gemini-cli), etc.
- [uv](https://docs.astral.sh/uv/) for package management
- [Python 3.11+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)
- **Sphinx** (if using Sphinx): `pip install sphinx myst-parser`
- **MkDocs** (if using MkDocs): `pip install mkdocs mkdocs-material`

## 📖 Learn more

- **[Spec Kit Documentation](https://github.github.io/spec-kit/)** - Learn about spec-kit fundamentals
- **[Spec-Driven Development Methodology](https://github.com/github/spec-kit/blob/main/spec-driven.md)** - Deep dive into the process
- **[Detailed Walkthrough](#-detailed-process)** - Step-by-step implementation guide

---

## 📋 Detailed process

<details>
<summary>Click to expand the detailed step-by-step walkthrough</summary>

### Prerequisites

Before using Spec Kit Docs, ensure you have:

1. **Installed spec-kit**:
   ```bash
   # Install spec-kit CLI
   uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
   ```

2. **Initialized spec-kit project**:
   ```bash
   specify init your-project --ai claude
   cd your-project
   ```

3. **Created at least one feature**:
   ```bash
   /speckit.specify Create a user authentication feature
   /speckit.plan Use Python Flask with JWT tokens
   /speckit.tasks
   ```

### Step 1: Install Spec Kit Docs

Clone the spec-kit-docs repository:

```bash
git clone https://github.com/driller/spec-kit-docs.git /tmp/spec-kit-docs
```

Run the initialization script from your spec-kit project:

```bash
cd your-spec-kit-project
uv run python /tmp/spec-kit-docs/.specify/scripts/docs/doc_init.py --tool sphinx
```

This will:
- Create slash commands in `.claude/commands/`
- Set up basic directory structure
- Install documentation tool dependencies

### Step 2: Initialize Documentation

Launch your AI agent (e.g., Claude Code):

```bash
claude
```

Use the `/doc-init` command to set up documentation:

```bash
/doc-init Create Sphinx documentation with a modern theme. Include:
- Overview page with project description
- Feature documentation for each spec in specs/
- API reference section
- Developer guide section
Use the Furo theme for a clean, modern look.
```

The AI agent will:
1. Parse your requirements
2. Create `docs/` directory structure
3. Generate `conf.py` (Sphinx) or `mkdocs.yml` (MkDocs)
4. Create index page
5. Generate initial feature documentation from existing specs
6. Set up navigation structure

### Step 3: Review Generated Documentation

Check the generated documentation:

```bash
# For Sphinx
cd docs
uv run sphinx-build -b html . _build/html
python -m http.server 8000 -d _build/html

# For MkDocs
mkdocs serve
```

Open your browser to `http://localhost:8000` to preview.

### Step 4: Update Documentation

After making changes to your specs:

```bash
/doc-update Regenerate feature documentation to reflect the latest changes in spec.md and plan.md
```

The AI agent will:
1. Scan `specs/` directory for changes
2. Parse updated `spec.md`, `plan.md`, `tasks.md`
3. Regenerate or update affected documentation pages
4. Preserve manually edited sections (marked with special comments)

### Step 5: Customize Documentation

You can manually edit generated documentation:

- For Sphinx: Edit `.rst` or `.md` files in `docs/`
- For MkDocs: Edit `.md` files in `docs/`

To preserve manual edits during updates, use marker comments:

```markdown
<!-- MANUAL EDIT START -->
This content will be preserved during regeneration.
<!-- MANUAL EDIT END -->
```

### Step 6: Build and Deploy

Build final documentation:

```bash
# For Sphinx
cd docs
uv run sphinx-build -b html . _build/html

# For MkDocs
mkdocs build
```

Deploy to your hosting platform:

```bash
# GitHub Pages
mkdocs gh-deploy

# Or copy _build/html to your web server
rsync -avz docs/_build/html/ user@server:/var/www/docs/
```

</details>

---

## 🔍 Troubleshooting

### Common Issues

#### `/doc-init` or `/doc-update` commands not found

**Solution**: Ensure initialization script ran successfully:

```bash
ls -la .claude/commands/
# Should show doc-init.md and doc-update.md
```

If missing, re-run:

```bash
uv run python /path/to/spec-kit-docs/.specify/scripts/docs/doc_init.py --tool sphinx
```

#### Documentation not updating

**Solution**: Check that your specs are in the correct location:

```bash
ls -la specs/
# Should show directories like 001-feature-name/
```

Ensure each feature has `spec.md`:

```bash
ls -la specs/001-feature-name/
# Should show spec.md, plan.md, tasks.md
```

#### Sphinx build errors

**Solution**: Verify Sphinx installation:

```bash
uv run python -c "import sphinx; print(sphinx.__version__)"
```

Check `conf.py` for syntax errors:

```bash
uv run python docs/conf.py
```

#### MkDocs build errors

**Solution**: Verify MkDocs installation:

```bash
mkdocs --version
```

Check `mkdocs.yml` for YAML syntax:

```bash
python -c "import yaml; yaml.safe_load(open('mkdocs.yml'))"
```

### Python Execution Issues

Remember to always use `uv run python` instead of `python` or `python3`:

```bash
# Correct
uv run python .specify/scripts/docs/doc_init.py --tool sphinx

# Incorrect (will fail)
python3 .specify/scripts/docs/doc_init.py --tool sphinx
```

## 👥 Maintainers

- driller ([@eleshis](mailto:eleshis@gmail.com))

## 💬 Support

For support, please open a [GitHub issue](https://github.com/driller/spec-kit-docs/issues/new). We welcome bug reports, feature requests, and questions about using Spec Kit Docs.

## 📄 License

This project is licensed under the terms of the MIT open source license. Please refer to the [LICENSE](./LICENSE) file for the full terms.
