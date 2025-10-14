# /doc-update - Update Documentation from Specifications

[Active Rules: C001-C014]
**CRITICAL原則**: ルール歪曲禁止・エラー迂回禁止・理想実装ファースト・記録管理・品質基準遵守・ドキュメント整合性・TDD必須・DRY原則・破壊的リファクタリング推奨・妥協実装絶対禁止

Execute the following command to update documentation:

```bash
uv run python .specify/scripts/docs/doc_update.py
```

## Workflow
1. Check that docs/ directory exists
2. Execute the script to update documentation
3. Display summary of updated features
4. If errors occur, show clear error messages and next steps
