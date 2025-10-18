# Git Commit Skill

Claude Codeでステージされたgit変更を分析し、Conventional Commitsフォーマットに準拠したコミットメッセージを生成するスキルです。

## 特徴

- **自動Type判定**: 変更内容から適切なcommit type (feat/fix/docs等) を自動提案
- **スコープ抽出**: ディレクトリ構造からscopeを自動推定
- **Breaking Changes検出**: APIや設定の大幅変更を自動検出
- **カスタマイズ可能**: プロジェクト固有のルールを`project_config.json`で設定
- **複数候補提示**: type判定で迷う場合は最大3候補を提示

## インストール

このスキルは`.claude/skills/git-commit/`ディレクトリに配置することで自動的に読み込まれます。

### チームで共有する場合

```bash
# リポジトリに追加
git add .claude/skills/git-commit/
git commit -m "feat(tools): add git-commit skill for team"
git push origin main

# チームメンバーは git pull で自動取得
git pull
```

## 使い方

### 基本的な使い方

1. 変更をステージング:
```bash
git add <files>
```

2. Claude Codeでスキルを発動:
```
"Help me commit these changes"
```
または
```
"Generate a commit message"
```

3. 提案されたコミットメッセージを確認・承認

4. コミットが自動実行されます

### 発動キーワード

以下のフレーズでスキルが自動的に発動します：
- "Help me commit"
- "I want to commit"
- "Generate a commit message"
- "Create a conventional commit"
- "git commit with proper message"

## Conventional Commits フォーマット

このスキルは[Conventional Commits](https://www.conventionalcommits.org/)仕様に準拠したメッセージを生成します。

### フォーマット

```
<type>(<scope>): <subject>

<body>

<footer>
```

### サポートされるType

| Type | 説明 | 例 |
|------|------|-----|
| `feat` | 新機能追加 | `feat(auth): add OAuth2 support` |
| `fix` | バグ修正 | `fix(api): handle null response` |
| `docs` | ドキュメント変更 | `docs: update installation guide` |
| `style` | フォーマット変更 | `style: fix indentation` |
| `refactor` | リファクタリング | `refactor(core): simplify logic` |
| `perf` | パフォーマンス改善 | `perf(db): add index` |
| `test` | テスト追加・修正 | `test(auth): add unit tests` |
| `build` | ビルドシステム変更 | `build: upgrade dependencies` |
| `ci` | CI設定変更 | `ci: add GitHub Actions` |
| `chore` | その他の変更 | `chore: update .gitignore` |

## 自動判定ロジック

### Type判定

スキルは以下のルールでtypeを自動判定します：

1. **テストファイルのみ** → `test`
2. **ドキュメントファイルのみ** → `docs`
3. **CI設定ファイル** → `ci`
4. **パッケージ管理ファイル** → `build`
5. **新規ファイル追加** → `feat`
6. **ファイル名に"fix"/"bug"** → `fix`
7. **上記以外** → `chore`

### Scope判定

ディレクトリ構造から自動推定：

```
src/auth/* → scope: "auth"
src/api/* → scope: "api"
src/ui/* → scope: "ui"
docs/* → スコープなし
tests/* → スコープなし
```

### Breaking Changes検出

以下のパターンで検出：
- 100行以上の削除
- APIファイルの大幅変更
- 設定ファイルのスキーマ変更

## プロジェクト固有カスタマイズ

`.claude/skills/git-commit/templates/project_config.json`を編集することで、プロジェクト固有のルールを設定できます。

### 設定例

```json
{
  "scopes": {
    "allowed": ["api", "ui", "db", "auth", "core"],
    "required_for_paths": {
      "src/api/*": "api",
      "src/auth/*": "auth"
    }
  },
  "rules": {
    "subject_max_length": 72,
    "require_scope": false,
    "emoji_prefix": false
  },
  "integrations": {
    "jira_pattern": "[A-Z]+-\\d+",
    "github_issue_pattern": "#\\d+"
  }
}
```

### カスタマイズ可能な項目

- **`scopes.allowed`**: 許可するスコープのリスト
- **`scopes.required_for_paths`**: 特定のパスで必須のスコープ
- **`rules.subject_max_length`**: subjectの最大文字数（デフォルト: 72）
- **`rules.require_scope`**: スコープを必須にするか（デフォルト: false）
- **`rules.emoji_prefix`**: 絵文字プレフィックスを有効にするか（デフォルト: false）

## スクリプト

### analyze_diff.py

ステージされた変更を分析するスクリプト。

**実行例:**
```bash
uv run python .claude/skills/git-commit/scripts/analyze_diff.py
```

**出力（JSON）:**
```json
{
  "files": [
    {
      "path": "src/auth/login.py",
      "status": "M",
      "additions": 15,
      "deletions": 3,
      "file_type": "python"
    }
  ],
  "summary": {
    "total_files": 1,
    "total_additions": 15,
    "total_deletions": 3,
    "new_files": 0,
    "modified_files": 1,
    "deleted_files": 0
  }
}
```

### classify_type.py

変更内容からtype/scopeを判定するスクリプト。

**実行例:**
```bash
uv run python .claude/skills/git-commit/scripts/analyze_diff.py | \
uv run python .claude/skills/git-commit/scripts/classify_type.py
```

**出力（JSON）:**
```json
{
  "type_candidates": ["feat", "refactor"],
  "scope": "auth",
  "has_breaking_changes": false,
  "subject_suggestion": "add OAuth2 login",
  "recommended_format": "feat(auth): add OAuth2 login"
}
```

## トラブルシューティング

### スキルが発動しない

**原因**: キーワードが認識されていない

**解決策**:
- "commit"または"git commit"を明示的に使用
- ステージされた変更があることを確認（`git status`）

### Type判定が不正確

**原因**: 自動判定ルールが適合しない

**解決策**:
- 手動でtypeを選択し直す
- `project_config.json`のルールを調整
- `classify_type.py`のロジックをカスタマイズ

### 複数の関心事が混在

**原因**: 1つのコミットに複数の変更が含まれている

**解決策**:
- コミットを分割することを推奨
- 各関心事ごとに別々のコミットを作成

## 例

### 例1: 新機能追加

**ステージされた変更:**
```bash
git add src/auth/oauth.py
```

**Claude Code:**
```
User: "Help me commit this"
Claude: [分析実行] → Type: feat, Scope: auth
Claude: "I suggest: feat(auth): add OAuth2 authentication"
User: "Yes, commit it"
Claude: [コミット実行完了]
```

### 例2: バグ修正

**ステージされた変更:**
```bash
git add src/api/users.py
```

**Claude Code:**
```
User: "Generate a commit message"
Claude: → Type: fix, Scope: api
Claude: "Suggested: fix(api): handle null response in user endpoint"
```

### 例3: ドキュメント更新

**ステージされた変更:**
```bash
git add README.md docs/installation.md
```

**Claude Code:**
```
User: "I want to commit"
Claude: → Type: docs, Scope: なし
Claude: "Suggested: docs: update installation guide"
```

## ファイル構造

```
.claude/skills/git-commit/
├── SKILL.md                      # メインスキル定義
├── README.md                     # このファイル
├── scripts/
│   ├── analyze_diff.py           # 変更分析スクリプト
│   └── classify_type.py          # Type/Scope判定スクリプト
├── templates/
│   └── project_config.json       # プロジェクト固有設定
└── examples/
    └── good_commits.md           # 良いコミット例集
```

## 参考資料

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [How to Write a Git Commit Message](https://chris.beams.io/posts/git-commit/)
- [Claude Code Skills Documentation](https://docs.claude.com/en/docs/claude-code/skills)

## ライセンス

このスキルはMITライセンスの下で提供されています。自由にカスタマイズしてご利用ください。

## 貢献

バグ報告や機能提案は、プロジェクトのIssueトラッカーまでお願いします。

---

**バージョン**: 1.0.0
**最終更新**: 2025-10-18