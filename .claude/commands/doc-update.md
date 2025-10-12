---
description: "Update documentation from spec-kit features"
---

# Update Documentation

Execute the following command to update documentation from spec-kit features:

```bash
uv run python .specify/scripts/docs/doc_update.py {{ARGS}}
```

Where {{ARGS}} are the user-provided arguments.

## Available Arguments

- `--no-incremental`: Regenerate all documentation files (default: incremental update)

## Examples

Incremental update (recommended):
```bash
uv run python .specify/scripts/docs/doc_update.py
```

Full regeneration:
```bash
uv run python .specify/scripts/docs/doc_update.py --no-incremental
```
