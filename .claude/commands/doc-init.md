---
description: "Initialize Sphinx or MkDocs documentation project for spec-kit"
---

# Initialize Documentation Project

Execute the following command to initialize a documentation project:

```bash
uv run python .specify/scripts/docs/doc_init.py {{ARGS}}
```

Where {{ARGS}} are the user-provided arguments.

## Available Arguments

- `--type {sphinx|mkdocs}`: Choose documentation tool (default: interactive prompt)
- `--no-interaction`: Use default values without prompts

## Examples

Interactive mode (recommended):
```bash
uv run python .specify/scripts/docs/doc_init.py
```

Non-interactive with Sphinx:
```bash
uv run python .specify/scripts/docs/doc_init.py --type sphinx --no-interaction
```

Non-interactive with MkDocs:
```bash
uv run python .specify/scripts/docs/doc_init.py --type mkdocs --no-interaction
```
