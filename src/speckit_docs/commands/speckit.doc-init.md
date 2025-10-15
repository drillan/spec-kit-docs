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
3. Execute the script with appropriate arguments
4. Display the results to the user
5. If errors occur, show clear error messages and next steps
