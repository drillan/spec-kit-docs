---
name: git-commit
description: >
  Analyze staged git changes and generate Conventional Commits format messages.
  Use when the user wants to commit changes, asks for commit message help,
  or mentions "commit", "git commit", "conventional commits", or "stage and commit".
---

# Git Commit Message Generator

このスキルは、ステージされたgit変更を分析し、Conventional Commitsフォーマットに準拠したコミットメッセージを生成します。

## 発動タイミング

以下のようなユーザーの発言で自動発動します：
- "Help me commit these changes"
- "Generate a commit message"
- "I want to commit"
- "Create a conventional commit"
- "git commit with proper message"

## Conventional Commitsフォーマット

コミットメッセージは以下の構造に従います：

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type（必須）
- **feat**: 新機能追加
- **fix**: バグ修正
- **docs**: ドキュメントのみの変更
- **style**: コードの動作に影響しない変更（フォーマット、セミコロン等）
- **refactor**: リファクタリング（機能追加でもバグ修正でもない）
- **perf**: パフォーマンス改善
- **test**: テストの追加・修正
- **build**: ビルドシステムや外部依存関係の変更
- **ci**: CI設定ファイルの変更
- **chore**: その他の変更（ビルドプロセス、補助ツール等）

### Scope（オプショナル）
変更の影響範囲を示す（例: auth, api, ui, db）

### Subject（必須）
変更の簡潔な説明（72文字以内、命令形、小文字開始、末尾ピリオドなし）

### Body（オプショナル）
変更の詳細な説明や理由

### Footer（オプショナル）
Breaking changesやissue番号の参照

## 実行ワークフロー

1. **ステージされた変更の確認**
   ```bash
   git diff --staged --stat
   git diff --staged
   ```

2. **変更の分析**
   - 変更ファイル数とパス
   - 追加/削除行数
   - ファイルタイプ（コード/ドキュメント/設定等）
   - 変更パターン（新規/修正/削除）

3. **Type/Scope候補の提示**
   以下のスクリプトを実行して候補を生成：
   ```bash
   uv run python .claude/skills/git-commit/scripts/analyze_diff.py
   uv run python .claude/skills/git-commit/scripts/classify_type.py
   ```

4. **ユーザーへの確認**
   - Type候補を3つまで提示
   - Scope候補を提示（該当する場合）
   - Subject案を提示
   - ユーザーの承認を得る

5. **コミットの実行**
   ```bash
   git commit -m "$(cat <<'EOF'
   <type>(<scope>): <subject>

   <body>

   <footer>
   EOF
   )"
   ```

## 自動判定ルール

### Type判定
- 新規ファイル追加 → **feat**
- テストファイルのみ変更 → **test**
- ドキュメントファイル(.md, .rst)のみ → **docs**
- パッケージ管理ファイル(package.json, requirements.txt) → **build**
- CI設定ファイル(.github/workflows/, .gitlab-ci.yml) → **ci**
- ファイル名に"fix"や"bug"を含む → **fix**
- 上記に該当しない → **chore**（デフォルト）

### Scope判定
ディレクトリ構造から自動推定：
- `src/auth/*` → scope: **auth**
- `src/api/*` → scope: **api**
- `src/ui/*` → scope: **ui**
- `docs/*` → scope: **docs**（通常はスコープ不要）
- `tests/*` → スコープなし

### Breaking Changes検出
以下のパターンを検出した場合、Breaking Changeの可能性を警告：
- 関数シグネチャの変更
- public APIの削除
- 設定ファイルのスキーマ変更
- `@deprecated`アノテーションの追加

## プロジェクト固有カスタマイズ

`.claude/skills/git-commit/templates/project_config.json`を編集することで、プロジェクト固有のルールを設定できます：

```json
{
  "scopes": {
    "allowed": ["api", "ui", "db", "auth"],
    "required_for_paths": {
      "src/api/*": "api",
      "src/auth/*": "auth"
    }
  },
  "rules": {
    "subject_max_length": 72,
    "require_scope": false,
    "emoji_prefix": false
  }
}
```

## 良いコミットメッセージの例

### 例1: 新機能追加
```
feat(auth): add OAuth2 login support

Implement OAuth2 authentication flow with Google and GitHub providers.
Includes token refresh mechanism and session management.

Closes #123
```

### 例2: バグ修正
```
fix(api): handle null response in user endpoint

Previously, the endpoint would crash when receiving a null user object.
Now returns a 404 status with appropriate error message.
```

### 例3: Breaking Change
```
feat(api)!: change user endpoint response format

BREAKING CHANGE: User API now returns ISO 8601 timestamps instead of Unix timestamps.
Migration guide: https://docs.example.com/migration/v2

Refs #456
```

### 例4: ドキュメント更新
```
docs: update installation guide for Python 3.11

Add instructions for installing with uv and pip.
Remove outdated Python 3.8 references.
```

### 例5: テスト追加
```
test(auth): add integration tests for OAuth flow

Cover success and error cases for Google and GitHub providers.
Increase test coverage from 60% to 85%.
```

## 注意事項

1. **必ずステージングを確認**: 意図しないファイルが含まれていないか確認してください
2. **Breaking Changesは明示**: APIや動作の変更がある場合は必ずフッターに記載
3. **Subjectは簡潔に**: 72文字以内、詳細はBodyに記述
4. **命令形を使用**: "add feature" (○) / "added feature" (×) / "adds feature" (×)
5. **小文字で開始**: "Add feature" (×) / "add feature" (○)

## トラブルシューティング

### スキルが発動しない場合
- "commit"または"git commit"というキーワードを明示的に使用してください
- ステージされた変更があることを確認してください（`git status`）

### Type判定が不正確な場合
- 手動でTypeを選択し直してください
- `project_config.json`のルールを調整してください

### 複数の関心事が混在している場合
- コミットを分割することを推奨します
- 各関心事ごとに別々のコミットを作成してください

## 参考資料

- [Conventional Commits仕様](https://www.conventionalcommits.org/)
- [How to Write Better Git Commit Messages](https://www.freecodecamp.org/news/how-to-write-better-git-commit-messages/)
- [Semantic Versioning](https://semver.org/)
