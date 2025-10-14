# クイックスタートガイド: spec-kit-docs

**Branch**: `001-draft-init-spec` | **Date**: 2025-10-14 | **Spec**: [spec.md](./spec.md)
**Audience**: spec-kitユーザー（開発者、プロジェクトマネージャー）

## 概要

spec-kit-docsは、spec-kitプロジェクトのMarkdown仕様（spec.md、plan.md、tasks.md）から、SphinxまたはMkDocsを使用して統一されたドキュメントサイトを自動生成するツールです。このガイドでは、インストールから基本的な使用方法までを学べます。

**主な機能**:
- spec-kit仕様からのドキュメント自動生成
- SphinxまたはMkDocsのサポート
- Git diffによるインクリメンタル更新
- Claude Codeスラッシュコマンド（`/speckit.doc-init`、`/speckit.doc-update`）との統合

---

## Prerequisites

spec-kit-docsを使用する前に、以下の前提条件を満たしていることを確認してください:

1. **spec-kitプロジェクトが初期化されている**:
   ```bash
   ls .specify/  # .specifyディレクトリが存在すること
   ```

2. **Gitリポジトリが初期化されている**:
   ```bash
   git status  # Gitリポジトリであること
   ```

3. **Python 3.11以上がインストールされている**:
   ```bash
   python3 --version  # Python 3.11以上
   ```

4. **Claude Codeが実行可能である**:
   - Claude Codeセッション内でこのガイドを実行していること

5. **少なくとも1つの機能仕様が存在する**:
   ```bash
   ls .specify/specs/  # 001-xxx等のディレクトリが存在すること
   ```

---

## インストール

### ステップ1: spec-kit-docs CLIツールのインストール

`uv tool install`コマンドを使用して、spec-kit-docsをグローバルCLIツールとしてインストールします：

```bash
uv tool install speckit-docs --from git+https://github.com/drillan/spec-kit-docs.git
```

これにより、`speckit-docs`コマンドがシステム全体で利用可能になります。

**注**: この方法は本家spec-kitの`uv tool install specify-cli`パターンと一貫性があり、プロジェクト環境を汚染しません（Session 2025-10-14決定、FR-021）。

### ステップ2: spec-kitプロジェクトへのコマンド追加

既存のspec-kitプロジェクトのルートディレクトリに移動し、`speckit-docs install`を実行します：

```bash
# プロジェクトルートに移動
cd your-spec-kit-project

# spec-kit-docsコマンドをプロジェクトにインストール
speckit-docs install
```

これにより、以下のファイルがプロジェクトに追加されます：
- `.claude/commands/speckit.doc-init.md` - `/speckit.doc-init`コマンド定義
- `.claude/commands/speckit.doc-update.md` - `/speckit.doc-update`コマンド定義
- `.specify/scripts/docs/doc_init.py` - ドキュメント初期化スクリプト
- `.specify/scripts/docs/doc_update.py` - ドキュメント更新スクリプト

インストール成功のメッセージが表示されます：

```
✓ Commands installed to .claude/commands/
✓ Scripts installed to .specify/scripts/docs/
✓ spec-kit-docs installation complete!

Next steps:
1. Open Claude Code in this project
2. Run /speckit.doc-init to initialize documentation
```

**注**: 既にインストールされている場合、上書き確認が表示されます。`--force`フラグを使用すると確認をスキップできます（FR-023b）。

**所要時間**: 2-3分

---

## Quick Start: Sphinxでドキュメント生成

### Step 1: ドキュメントプロジェクトの初期化

Claude Code内で以下のコマンドを実行します:

```
/speckit.doc-init --type sphinx
```

対話的プロンプトが表示されますので、必要な情報を入力します:

```
どのドキュメント生成ツールを使用しますか？
1) Sphinx (推奨 - MyST Markdown対応)
2) MkDocs (シンプル)
選択 [1]: 1

プロジェクト名を入力してください [spec-kit-docs]: my-project

著者名を入力してください [Your Name]: John Doe

初期バージョン番号を入力してください [0.1.0]: 0.1.0

ドキュメント言語を入力してください [ja]: ja
```

**出力**:
```
✓ spec-kitプロジェクトを検出しました
✓ 3つの機能を発見しました
✓ ドキュメント構造: フラット (5機能以下)
✓ Sphinxプロジェクトを初期化しました

生成されたファイル:
  - docs/conf.py
  - docs/index.md
  - docs/Makefile
  - docs/make.bat

次のステップ:
  1. /speckit.doc-update を実行してドキュメントを生成
  2. cd docs && make html でHTMLをビルド
  3. docs/_build/html/index.html をブラウザで開く
```

**所要時間**: 1分（対話的入力時間を除く）

---

### Step 2: ドキュメントの生成

初期化後、実際のドキュメントを生成します:

```
/speckit.doc-update
```

**出力**:
```
✓ 3つの機能が変更されました:
  - 001-user-auth
  - 002-api-integration
  - 003-payment-gateway

✓ ドキュメントを生成しました:
  - docs/user-auth.md (新規)
  - docs/api-integration.md (新規)
  - docs/payment-gateway.md (新規)

✓ index.mdを更新しました

✓ HTMLビルドを実行しました
  - 警告: 0
  - エラー: 0
  - ビルド時間: 3.2秒
  - 生成ファイル: 15個

次のステップ:
  1. docs/_build/html/index.html をブラウザで開く
```

**所要時間**: 10-45秒（機能数による、5機能の場合は約45秒、SC-006）

---

### Step 3: ドキュメントの確認

生成されたHTMLをブラウザで確認します:

**Linux/macOS**:
```bash
cd docs
make html
open _build/html/index.html  # macOS
xdg-open _build/html/index.html  # Linux
```

**Windows**:
```bash
cd docs
make.bat html
start _build/html/index.html
```

**所要時間**: 1分（対話的入力時間を除く）

---

## Quick Start: MkDocsでドキュメント生成

MkDocsを使用する場合は、以下の手順で実行します:

### Step 1: ドキュメントプロジェクトの初期化

```
/speckit.doc-init --type mkdocs
```

対話的プロンプトが表示されますので、必要な情報を入力します（Sphinxと同様）。

**出力**:
```
✓ spec-kitプロジェクトを検出しました
✓ 3つの機能を発見しました
✓ ドキュメント構造: フラット (5機能以下)
✓ MkDocsプロジェクトを初期化しました

生成されたファイル:
  - docs/mkdocs.yml
  - docs/index.md

次のステップ:
  1. /speckit.doc-update を実行してドキュメントを生成
  2. cd docs && mkdocs serve でプレビュー
  3. ブラウザで http://127.0.0.1:8000 を開く
```

### Step 2: ドキュメントの生成

```
/speckit.doc-update
```

### Step 3: ライブプレビュー

MkDocsの場合、ライブプレビュー機能が利用できます:

```bash
cd docs
mkdocs serve
```

ブラウザで `http://127.0.0.1:8000` を開くと、ドキュメントが表示されます。

**所要時間**: 3-5分

---

## Common Use Cases

### Use Case 1: 仕様変更後のドキュメント更新

spec.mdを編集した後、ドキュメントを更新します:

```bash
# 1. spec.mdを編集
vim .specify/specs/001-user-auth/spec.md

# 2. Gitコミット
git add .
git commit -m "Update user-auth spec"

# 3. ドキュメント更新（インクリメンタル）
/speckit.doc-update
```

**出力**:
```
✓ 1つの機能が変更されました:
  - 001-user-auth

✓ ドキュメントを生成しました:
  - docs/user-auth.md (更新)

✓ index.mdを更新しました

✓ HTMLビルドを実行しました
  - 警告: 0
  - エラー: 0
  - ビルド時間: 1.8秒
  - 生成ファイル: 15個
```

**所要時間**: 5秒以内（インクリメンタル更新）

---

### Use Case 2: 全ドキュメントの再生成

すべての機能を再生成する場合は、`--full`フラグを使用します:

```
/speckit.doc-update --full
```

**出力**:
```
✓ 全機能を再生成します (3機能)

✓ ドキュメントを生成しました:
  - docs/user-auth.md
  - docs/api-integration.md
  - docs/payment-gateway.md

✓ index.mdを更新しました

✓ HTMLビルドを実行しました
  - 警告: 0
  - エラー: 0
  - ビルド時間: 3.5秒
  - 生成ファイル: 15個
```

**所要時間**: 10-45秒（機能数による）

---

### Use Case 3: Markdownのみ生成（ビルドスキップ）

HTMLビルドをスキップして、Markdownファイルのみを生成する場合:

```
/speckit.doc-update --no-build
```

**出力**:
```
✓ 3つの機能が変更されました:
  - 001-user-auth
  - 002-api-integration
  - 003-payment-gateway

✓ ドキュメントを生成しました:
  - docs/user-auth.md (更新)
  - docs/api-integration.md (更新)
  - docs/payment-gateway.md (更新)

✓ index.mdを更新しました

HTMLビルドはスキップされました。
```

**所要時間**: 3-5秒

---

### Use Case 4: 非対話モードでの初期化

CI/CD環境やスクリプトで使用する場合、対話モードを無効化できます:

```
/speckit.doc-init --type sphinx --no-interaction
```

デフォルト値が自動的に使用されます（プロジェクト名、著者名、バージョン等）。

**所要時間**: 10-30秒

---

## Generated File Structure

### Flat Structure (5機能以下)

```
docs/
├── conf.py                 # Sphinx設定ファイル（myst-parser設定を含む）
├── index.md                # インデックスページ
├── Makefile                # ビルド用Makefile（Linux/macOS）
├── make.bat                # ビルド用バッチファイル（Windows）
├── .gitignore              # Git除外設定
├── user-auth.md            # 機能ドキュメント（spec.mdから生成）
├── api-integration.md      # 機能ドキュメント
└── payment-gateway.md      # 機能ドキュメント
```

### Comprehensive Structure (6機能以上)

```
docs/
├── conf.py
├── index.md
├── Makefile
├── make.bat
├── .gitignore
├── features/               # 機能ドキュメント
│   ├── user-auth.md
│   ├── api-integration.md
│   ├── payment-gateway.md
│   ├── notification-system.md
│   ├── analytics-dashboard.md
│   └── admin-panel.md
├── guides/                 # ガイド（将来拡張）
│   └── getting-started.md
├── api/                    # API リファレンス（将来拡張）
│   └── reference.md
└── architecture/           # アーキテクチャ（将来拡張）
    └── overview.md
```

**自動決定ロジック**:
- 5機能以下: フラット構造
- 6機能以上: 包括的構造

---

## Troubleshooting

### Problem 1: "spec-kitプロジェクトではありません"エラー

**Symptom**:
```
✗ エラー: spec-kitプロジェクトではありません

💡 提案: 最初に 'specify init' を実行してspec-kitプロジェクトを初期化してください。
```

**Solution**:
```bash
specify init  # spec-kitプロジェクトを初期化
```

---

### Problem 2: "Gitリポジトリではありません"エラー

**Symptom**:
```
✗ エラー: Gitリポジトリではありません

💡 提案: 'git init' を実行してGitリポジトリを初期化してください。
```

**Solution**:
```bash
git init
git add .
git commit -m "Initial commit"
```

---

### Problem 3: "機能が見つかりませんでした"エラー

**Symptom**:
```
✗ エラー: 機能が見つかりませんでした

💡 提案: 'specify new' で機能を作成してください。
```

**Solution**:
```bash
specify new 001-my-first-feature
```

---

### Problem 4: "HTMLビルドに失敗しました"エラー

**Symptom**:
```
✗ エラー: HTMLビルドに失敗しました
  - ビルドエラー: WARNING: document isn't included in any toctree
```

**Solution 1**: `--no-build`フラグでMarkdownのみ生成し、手動でビルドして詳細を確認
```
/speckit.doc-update --no-build
cd docs
make html  # エラーログを確認
```

**Solution 2**: `--full`フラグで全ドキュメントを再生成
```
/speckit.doc-update --full
```

---

### Problem 5: "変更が検出されませんでした"メッセージ

**Symptom**:
```
✓ 変更が検出されませんでした

ドキュメントは最新です。
```

**Explanation**:
- Git diffで変更がないため、ドキュメント更新をスキップしています
- これは正常な動作です

**Solution** (全ドキュメントを強制的に再生成したい場合):
```
/speckit.doc-update --full
```

---

## Best Practices

### 1. 定期的なドキュメント更新

spec.mdを編集するたびに、ドキュメントを更新することを推奨します:

```bash
# 編集後
git add .
git commit -m "Update spec"

# ドキュメント更新
/speckit.doc-update
```

### 2. CI/CDでの自動ドキュメント生成

GitHub ActionsやGitLab CIで自動的にドキュメントを生成・デプロイできます:

```yaml
# .github/workflows/docs.yml
name: Generate Docs

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install speckit-docs sphinx

      - name: Generate docs
        run: |
          python .specify/scripts/docs/doc_update.py --full

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs/_build/html
```

### 3. ドキュメントレビュー

生成されたドキュメントを手動で確認し、必要に応じてspec.mdを修正します:

1. `/speckit.doc-update`を実行
2. ブラウザでドキュメントを確認
3. 不備があればspec.mdを編集
4. 再度`/speckit.doc-update`を実行

### 4. 小規模プロジェクト向けのシンプルな構造

5機能以下の小規模プロジェクトでは、フラット構造が自動的に選択されます。これにより、過剰な階層を避け、ナビゲーションをシンプルに保ちます。

### 5. バージョン管理

ドキュメント生成ファイル（`docs/`配下のMarkdown）をGitで管理することで、ドキュメントの変更履歴を追跡できます:

```bash
git add docs/
git commit -m "Update documentation"
```

ビルド成果物（`_build/`, `site/`）は`.gitignore`で除外されます。

---

## Next Steps

このクイックスタートガイドを完了したら、以下のリソースを参照してください:

1. **[spec.md](spec.md)**: 機能仕様の詳細
2. **[data-model.md](data-model.md)**: データモデルとエンティティ定義
3. **[contracts/cli-interface.md](contracts/cli-interface.md)**: CLIインターフェース仕様
4. **[contracts/file-formats.md](contracts/file-formats.md)**: 生成ファイルの形式仕様
5. **[research.md](research.md)**: 技術的決定の背景

**Advanced Features** (Phase 2以降):
- AI統合（`--ai`フラグ）: 要約生成、フローチャート生成
- 複数バージョン管理
- 国際化対応（i18n）

---

## まとめ

このクイックスタートガイドでは、以下の内容をカバーしました:

- **前提条件の確認**: spec-kit、Git、Python 3.11+、uv
- **インストール**: `uv tool install speckit-docs --from git+https://github.com/drillan/spec-kit-docs.git`、`speckit-docs install`
- **Sphinx初期化**: `/speckit.doc-init --type sphinx`
- **ドキュメント生成**: `/speckit.doc-update`
- **一般的なユースケース**: インクリメンタル更新、全再生成、ビルドスキップ、非対話モード
- **トラブルシューティング**: 5つの一般的な問題と解決方法
- **ベストプラクティス**: 定期的な更新、CI/CD統合、ドキュメントレビュー

**所要時間合計**: 10-15分

spec-kit-docsを使用することで、spec-kit仕様から統一されたドキュメントサイトを簡単に生成できます。さらに詳しい情報は、[spec.md](./spec.md)と[plan.md](./plan.md)を参照してください。
