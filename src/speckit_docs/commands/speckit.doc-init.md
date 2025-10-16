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

Execute the following command to initialize a Sphinx or MkDocs documentation project:

```bash
uv run python .specify/scripts/docs/doc_init.py {{ARGS}}
```

Where {{ARGS}} are the user-provided arguments (e.g., `--type sphinx`).

## Workflow
1. Ask the user which documentation tool to use (Sphinx or MkDocs)
2. Collect project metadata interactively (project name, author, version, language)
3. **Ask the user about dependency installation** (FR-008c, FR-008f):
   - Explain that documentation tool dependencies need to be installed
   - Ask which dependency placement strategy to use:
     - **`optional-dependencies`** (推奨): pip/poetry/uv互換、PEP 621標準、`[project.optional-dependencies.docs]`セクションに配置
     - **`dependency-groups`**: uvネイティブ、PEP 735準拠、`[dependency-groups.docs]`セクションに配置
   - Show which packages will be installed based on doc_type:
     - Sphinx: `sphinx>=7.0`, `myst-parser>=2.0`
     - MkDocs: `mkdocs>=1.5`, `mkdocs-material>=9.0`
   - Get user confirmation for automatic installation:
     - If user agrees → add `--auto-install --dependency-target {choice}`
     - If user declines → add `--no-install`
4. Execute the script with appropriate arguments
   - **CRITICAL**: ALWAYS include either `--auto-install` or `--no-install` flag
   - DO NOT run without one of these flags (causes stdin blocking in AI environment)
5. Display the results to the user
6. If errors occur, show clear error messages and next steps

## Example Commands

**With auto-install (recommended)**:
```bash
uv run python .specify/scripts/docs/doc_init.py --type sphinx --auto-install --dependency-target optional-dependencies
```

**Skip installation**:
```bash
uv run python .specify/scripts/docs/doc_init.py --type mkdocs --no-install
```

**With dependency-groups**:
```bash
uv run python .specify/scripts/docs/doc_init.py --type sphinx --auto-install --dependency-target dependency-groups
```

## Important Notes

- The script uses `typer.confirm()` when `auto_install=False` and `no_install=False`, which requires stdin
- In AI agent environments (Claude Code), stdin is not available, so ALWAYS use `--auto-install` or `--no-install`
- Default values: `auto_install=False`, `no_install=False`, `dependency_target="optional-dependencies"`
