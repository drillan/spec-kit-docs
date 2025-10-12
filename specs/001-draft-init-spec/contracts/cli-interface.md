# CLI Interface Contract: spec-kit-docs

**Feature**: spec-kit-docs
**Date**: 2025-10-12
**Phase**: 1 - Interface Contracts
**Type**: Command Line Interface
**Source**: [spec.md](../spec.md) | [data-model.md](../data-model.md)

## Overview

このドキュメントは、spec-kit-docsのCLIインターフェース仕様を定義します。Claude Codeのスラッシュコマンド（`/speckit.doc-init`と`/speckit.doc-update`）として動作し、内部的にPythonスクリプトを実行します。

## Command: /speckit.doc-init

### Purpose
spec-kitプロジェクトに対して、ドキュメント生成環境（SphinxまたはMkDocs）を初期化します。

### Syntax
```bash
/speckit.doc-init [--type {sphinx|mkdocs}] [--no-interaction]
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `--type` | choice | No | interactive | ドキュメント生成ツール（`sphinx` or `mkdocs`） |
| `--no-interaction` | flag | No | False | 対話モードを無効化（デフォルト値を使用） |

### Interactive Prompts

`--no-interaction`フラグがない場合、以下の対話的プロンプトを表示します（FR-031）:

1. **ドキュメント生成ツール選択**（`--type`が未指定の場合）:
   ```
   どのドキュメント生成ツールを使用しますか？
   1) Sphinx (推奨 - MyST Markdown対応)
   2) MkDocs (シンプル)
   選択 [1]:
   ```
   - デフォルト: `1` (Sphinx)
   - 検証: 1または2のみ受け付け

2. **プロジェクト名**:
   ```
   プロジェクト名を入力してください [current-dir-name]:
   ```
   - デフォルト: カレントディレクトリ名
   - 検証: 空文字列不可、特殊文字（`/`, `\`, `:`）不可

3. **著者名**:
   ```
   著者名を入力してください [Git user.name]:
   ```
   - デフォルト: `git config user.name`の値
   - 検証: 空文字列の場合は"Unknown Author"を使用

4. **バージョン番号**:
   ```
   初期バージョン番号を入力してください [0.1.0]:
   ```
   - デフォルト: `0.1.0`
   - 検証: セマンティックバージョニング形式（`X.Y.Z`）を推奨、強制しない

5. **ドキュメント言語**:
   ```
   ドキュメント言語を入力してください [ja]:
   ```
   - デフォルト: `ja`（日本語）
   - 検証: ISO 639-1コード（2文字）を推奨、強制しない

### Execution Flow

```
1. spec-kitプロジェクト検証
   ├─ .specify/ ディレクトリの存在確認
   ├─ Git リポジトリの確認
   └─ エラーの場合: ValidationError + 提案

2. 既存ドキュメントプロジェクト検出
   ├─ docs/ ディレクトリの存在確認
   ├─ conf.py (Sphinx) / mkdocs.yml (MkDocs) の存在確認
   └─ 存在する場合: 警告 + 上書き確認プロンプト

3. 機能スキャン
   ├─ .specify/specs/ 配下のディレクトリ探索
   ├─ spec.md の存在確認（FR-001）
   └─ Feature[] 生成

4. DocumentStructure 決定
   ├─ feature_count <= 5: FLAT
   └─ feature_count >= 6: COMPREHENSIVE

5. GeneratorConfig 生成
   └─ ユーザー入力からconfig作成

6. Generator.init_project() 実行
   ├─ Sphinx: conf.py, index.md, Makefile, make.bat 生成
   └─ MkDocs: mkdocs.yml, index.md 生成

7. 成功メッセージ出力
```

### Output (Success)

**Exit Code**: 0

**Stdout**:
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

**Generated Files** (Sphinx):
- `docs/conf.py`: Sphinx設定ファイル（myst-parser設定を含む）
- `docs/index.md`: インデックスページ（Markdown）
- `docs/Makefile`: ビルド用Makefile（Linux/macOS）
- `docs/make.bat`: ビルド用バッチファイル（Windows）
- `docs/.gitignore`: ビルド成果物を除外（`_build/`, `_static/`, `_templates/`）

**Generated Files** (MkDocs):
- `docs/mkdocs.yml`: MkDocs設定ファイル
- `docs/index.md`: インデックスページ（Markdown）
- `docs/.gitignore`: ビルド成果物を除外（`site/`）

### Output (Error)

**Exit Code**: 1

**Stderr**:
```
✗ エラー: spec-kitプロジェクトではありません

💡 提案: 最初に 'specify init' を実行してspec-kitプロジェクトを初期化してください。
```

### Error Cases

| Error Condition | Message | Suggestion |
|----------------|---------|------------|
| `.specify/`が存在しない | `spec-kitプロジェクトではありません` | `specify init`を実行 |
| Git未初期化 | `Gitリポジトリではありません` | `git init`を実行 |
| `docs/`が既に存在 | `ドキュメントディレクトリが既に存在します` | バックアップ後に削除、または別ディレクトリを指定 |
| 機能が0個 | `機能が見つかりませんでした` | `specify new`で機能を作成 |
| 書き込み権限なし | `ファイル書き込みに失敗しました` | ディレクトリのパーミッションを確認 |

**Source Requirements**: FR-001, FR-005, FR-006, FR-031, FR-033

---

## Command: /speckit.doc-update

### Purpose
spec-kitプロジェクトの仕様変更を検出し、ドキュメントを更新します。Git diffを使用してインクリメンタル更新を実行します。

### Syntax
```bash
/speckit.doc-update [--full] [--no-build] [--ai]
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `--full` | flag | No | False | 全機能を再生成（インクリメンタル更新を無効化） |
| `--no-build` | flag | No | False | HTMLビルドをスキップ（Markdownのみ生成） |
| `--ai` | flag | No | False | AI統合を有効化（要約生成、フローチャート生成） |

### Execution Flow

```
1. spec-kitプロジェクト検証
   └─ .specify/ と docs/ の存在確認

2. ドキュメントツール検出
   ├─ conf.py 存在 → Sphinx
   ├─ mkdocs.yml 存在 → MkDocs
   └─ どちらもない → エラー

3. 変更検出（--full フラグなしの場合）
   ├─ ChangeDetector.get_changed_features()
   ├─ Git diff で .specify/specs/ の変更を検出
   └─ 変更なし → メッセージ出力して終了

4. ドキュメント生成
   ├─ for each Feature (変更されたもの、または全機能):
   │    ├─ Document.parse() → Section[]
   │    ├─ MarkdownParser.parse()
   │    ├─ Section.to_sphinx_md() / to_mkdocs_md()
   │    └─ 機能ドキュメント書き込み (feature-name.md)
   │
   ├─ index 更新
   │    ├─ Sphinx: index.md の toctree 更新
   │    └─ MkDocs: mkdocs.yml の nav 更新
   │
   └─ AI統合（--ai フラグありの場合）
        ├─ 各セクションの要約生成（FR-024）
        ├─ フローチャート生成（FR-025）
        └─ タグ自動抽出（FR-026）

5. ビルド実行（--no-build フラグなしの場合）
   ├─ Sphinx: make html
   ├─ MkDocs: mkdocs build
   └─ BuildResult 取得

6. 成功メッセージ出力
```

### Output (Success)

**Exit Code**: 0

**Stdout** (Incremental):
```
✓ 2つの機能が変更されました:
  - 001-user-auth
  - 003-api-integration

✓ ドキュメントを生成しました:
  - docs/user-auth.md (更新)
  - docs/api-integration.md (新規)

✓ index.mdを更新しました

✓ HTMLビルドを実行しました
  - 警告: 0
  - エラー: 0
  - ビルド時間: 3.2秒
  - 生成ファイル: 15個

次のステップ:
  1. docs/_build/html/index.html をブラウザで開く
  2. 変更を確認
```

**Stdout** (No Changes):
```
✓ 変更が検出されませんでした

ドキュメントは最新です。
```

**Stdout** (Full Regeneration):
```
✓ 全機能を再生成します (5機能)

✓ ドキュメントを生成しました:
  - docs/user-auth.md
  - docs/api-integration.md
  - docs/payment-gateway.md
  - docs/notification-system.md
  - docs/analytics-dashboard.md

✓ index.mdを更新しました

✓ HTMLビルドを実行しました
  - 警告: 2
  - エラー: 0
  - ビルド時間: 8.7秒
  - 生成ファイル: 42個

次のステップ:
  1. docs/_build/html/index.html をブラウザで開く
```

### Output (Error)

**Exit Code**: 1

**Stderr**:
```
✗ エラー: ドキュメントプロジェクトが初期化されていません

💡 提案: 最初に /speckit.doc-init を実行してドキュメントプロジェクトを初期化してください。
```

### Error Cases

| Error Condition | Message | Suggestion |
|----------------|---------|------------|
| `docs/`が存在しない | `ドキュメントプロジェクトが初期化されていません` | `/speckit.doc-init`を実行 |
| `conf.py`/`mkdocs.yml`が存在しない | `ドキュメント設定ファイルが見つかりません` | `/speckit.doc-init`を再実行 |
| Git diffエラー | `Git diff の取得に失敗しました` | Gitリポジトリの状態を確認 |
| Markdown解析エラー | `spec.mdの解析に失敗しました: [file]` | Markdown構文を確認 |
| ビルドエラー | `HTMLビルドに失敗しました` | ビルドログを確認、`--no-build`で回避 |

**Source Requirements**: FR-010, FR-012, FR-013, FR-014, FR-018, FR-019, FR-033

---

## Python Script Interface

Claude Codeコマンドは内部的にPythonスクリプトを呼び出します。

### Script Location
```
.specify/scripts/docs/doc_init.py
.specify/scripts/docs/doc_update.py
```

### Python API

**doc_init.py**:
```python
def main(
    tool: str = "sphinx",
    project_name: str | None = None,
    author: str | None = None,
    version: str = "0.1.0",
    language: str = "ja",
    no_interaction: bool = False
) -> int:
    """
    ドキュメントプロジェクトを初期化

    Returns:
        0: 成功
        1: エラー
    """
```

**doc_update.py**:
```python
def main(
    full: bool = False,
    no_build: bool = False,
    ai: bool = False
) -> int:
    """
    ドキュメントを更新

    Returns:
        0: 成功
        1: エラー
    """
```

### Command Mapping

**`.claude/commands/doc-init.md`**:
```markdown
Execute the following command to initialize documentation project:

`uv run python .specify/scripts/docs/doc_init.py {{ARGS}}`

Where {{ARGS}} are the user-provided arguments.
```

**`.claude/commands/doc-update.md`**:
```markdown
Execute the following command to update documentation:

`uv run python .specify/scripts/docs/doc_update.py {{ARGS}}`

Where {{ARGS}} are the user-provided arguments.
```

**Source Requirements**: research.md Decision 7 (argparse)

---

## Performance Requirements

| Operation | Target | Measurement |
|-----------|--------|-------------|
| `/speckit.doc-init` | ≤ 30秒 | 対話入力時間を除く（SC-001） |
| `/speckit.doc-update` (10機能) | ≤ 45秒 | AI統合を除く（SC-006） |
| `/speckit.doc-update` (incremental, 1機能) | ≤ 5秒 | ビルドを除く（SC-008） |

**Source Requirements**: SC-001, SC-006, SC-008

---

## Validation and Testing

### Contract Tests

**Input Validation**:
- [ ] `--type`は`sphinx`または`mkdocs`のみ受け付ける
- [ ] プロジェクト名に特殊文字（`/`, `\`, `:`）が含まれる場合はエラー
- [ ] バージョン番号が不正な場合は警告（処理は続行）

**Output Validation**:
- [ ] 生成された`conf.py`がPython構文として正しい
- [ ] 生成された`mkdocs.yml`がYAML構文として正しい
- [ ] 生成された`index.md`が有効なMarkdown
- [ ] Exit codeが0（成功）または1（エラー）

**Error Handling**:
- [ ] `.specify/`が存在しない場合、適切なエラーメッセージを出力
- [ ] Git未初期化の場合、適切なエラーメッセージを出力
- [ ] 書き込み権限がない場合、適切なエラーメッセージを出力

### Integration Tests

**End-to-End (Sphinx)**:
```bash
# Setup
mkdir test-project && cd test-project
git init
specify init

# Create sample feature
specify new 001-sample-feature

# Test doc-init
/speckit.doc-init --type sphinx --no-interaction

# Verify
test -f docs/conf.py
test -f docs/index.md
test -f docs/Makefile

# Test doc-update
/speckit.doc-update --no-build

# Verify
test -f docs/sample-feature.md
grep "sample-feature" docs/index.md
```

**End-to-End (MkDocs)**:
```bash
# Test doc-init
/speckit.doc-init --type mkdocs --no-interaction

# Verify
test -f docs/mkdocs.yml
test -f docs/index.md

# Test doc-update
/speckit.doc-update --no-build

# Verify
test -f docs/sample-feature.md
grep "sample-feature" docs/mkdocs.yml
```

---

## Backward Compatibility

**Version 1.0**:
- 初期リリース、互換性保証の基準バージョン

**Future Versions**:
- コマンドインターフェースは後方互換性を維持
- 新しいオプションは`--`プレフィックスで追加
- 既存オプションの削除は非推奨（deprecated）警告を経てメジャーバージョンアップで実施

---

## Summary

このCLIインターフェース仕様は、spec-kit-docsの2つの主要コマンド（`/speckit.doc-init`と`/speckit.doc-update`）を定義しています。主要な設計決定：

1. **対話的プロンプト**: ユーザーフレンドリーな初期化（FR-031）
2. **明確なエラーメッセージ**: エラー + 提案のパターン（research.md Decision 8）
3. **インクリメンタル更新**: Git diffで変更検出（FR-010）
4. **標準argparse**: シンプルなCLI実装（research.md Decision 7）
5. **性能目標**: 30秒/45秒の明確なターゲット（SC-001, SC-006）

次のドキュメント（quickstart.md）では、これらのコマンドを使用した基本的な使用方法を説明します。
