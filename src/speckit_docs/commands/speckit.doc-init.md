# /speckit.doc-init - Initialize Documentation Project

[Active Rules: C001-C014]
**CRITICAL原則**: ルール歪曲禁止・エラー迂回禁止・理想実装ファースト・記録管理・品質基準遵守・ドキュメント整合性・TDD必須・DRY原則・破壊的リファクタリング推奨・妥協実装絶対禁止

## Prerequisites

Before running this command, ensure spec-kit-docs is installed:

```bash
# Install spec-kit-docs CLI tool (recommended method)
uv tool install speckit-docs --from git+https://github.com/drillan/spec-kit-docs.git

# Then install commands to your project
cd your-spec-kit-project
speckit-docs install
```

This follows the same pattern as spec-kit's `uv tool install specify-cli` (Session 2025-10-14, FR-021).

## Command

Execute the following command to initialize a Sphinx documentation project with default settings:

```bash
uv run python .specify/scripts/docs/doc_init.py --type sphinx --auto-install --dependency-target optional-dependencies
```

**Default values**:
- Documentation tool: `sphinx` (Sphinx with MyST Markdown support)
- Auto-install: `--auto-install` (automatically install dependencies without confirmation)
- Dependency target: `optional-dependencies` (PEP 621 standard, pip/poetry/uv compatible)
- Project metadata: Auto-detected from directory name and git config

**Customization options**:
- Change documentation tool: Replace `--type sphinx` with `--type mkdocs`
- Change dependency target: Replace `--dependency-target optional-dependencies` with `--dependency-target dependency-groups`
- Skip installation: Replace `--auto-install` with `--no-install`
- Override metadata: Add `--project-name "MyProject" --author "Your Name" --version "1.0.0"`

## Workflow
1. Execute the script with default values (Sphinx, auto-install, optional-dependencies)
2. The script will:
   - Auto-detect project name from directory name
   - Auto-detect author from `git config user.name`
   - Discover features from `.specify/specs/` directory
   - Create `docs/` directory structure
   - Generate configuration files (conf.py or mkdocs.yml)
   - Install required dependencies via `uv add --optional docs <packages>`
3. Display the results to the user
4. If errors occur, show clear error messages and next steps

**CRITICAL**: ALWAYS include either `--auto-install` or `--no-install` flag. DO NOT run without one of these flags (causes stdin blocking in AI environment).

## Example Commands

**Default (Sphinx with auto-install - RECOMMENDED)**:
```bash
uv run python .specify/scripts/docs/doc_init.py --type sphinx --auto-install --dependency-target optional-dependencies
```

**MkDocs with auto-install**:
```bash
uv run python .specify/scripts/docs/doc_init.py --type mkdocs --auto-install --dependency-target optional-dependencies
```

**Skip dependency installation**:
```bash
uv run python .specify/scripts/docs/doc_init.py --type sphinx --no-install
```

**Use dependency-groups (uv native, PEP 735)**:
```bash
uv run python .specify/scripts/docs/doc_init.py --type sphinx --auto-install --dependency-target dependency-groups
```

## Important Notes

- **CRITICAL**: In AI agent environments (Claude Code), stdin is not available
- **MUST ALWAYS** include either `--auto-install` or `--no-install` flag
- **DO NOT** run without these flags → causes `typer.confirm()` to block waiting for stdin
- Default execution: `--type sphinx --auto-install --dependency-target optional-dependencies`
