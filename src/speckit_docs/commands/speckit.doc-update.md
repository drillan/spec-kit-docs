# /speckit.doc-update - Update Documentation from Specifications

## Overview

このコマンドは、spec-kitプロジェクトの仕様（spec.md、plan.md、tasks.md）とREADME/QUICKSTARTファイルからドキュメントを自動生成します。

**Session 2025-10-17 FR-022b**: このコマンドはLLM変換を実行し、変換済みコンテンツをバックエンドスクリプトに渡す明確な責務分担を実装しています。

## Prerequisites Check

まず、必要な環境を確認します：

```bash
# Check if docs/ directory exists
ls docs/ 2>/dev/null
```

- **docs/が存在しない場合**: `/speckit.doc-init` を先に実行する必要があることを伝える
- **docs/が存在する場合**: 次のステップへ進む

## Step 1: LLM変換実行（FR-022b ワークフロー）

### 1.1 機能検出とコンテンツソース選択

各機能に対して、以下の優先順位でコンテンツソースを選択：

```bash
# スクリプトで機能ディレクトリを検出
for feature_dir in specs/*/; do
    feature_id=$(basename "$feature_dir")

    # コンテンツソース選択（優先順: README.md → QUICKSTART.md → spec.md最小限抽出）
    if [ -f "$feature_dir/README.md" ]; then
        echo "機能 $feature_id: README.mdを使用"
    elif [ -f "$feature_dir/QUICKSTART.md" ]; then
        echo "機能 $feature_id: QUICKSTART.mdを使用"
    else
        echo "機能 $feature_id: spec.mdから最小限抽出"
    fi
done
```

### 1.2 LLM変換実行

各機能のコンテンツソースに対して、Claude APIでユーザーフレンドリーなドキュメントに変換：

**README.md単独の場合**:
- README.mdの内容をそのまま使用（LLM変換パススルー）

**QUICKSTART.md単独の場合**:
- QUICKSTART.mdの内容をそのまま使用（LLM変換パススルー）

**README.md + QUICKSTART.md両方存在の場合**:
1. 不整合検出: Claude APIで両ファイルの内容を比較
2. 整合性OK時のみ、セクション単位で優先順位判定
3. 優先順位順にセクションを統合（10,000トークン以内）

**spec.md最小限抽出の場合**:
- ユーザーストーリーの「目的」、前提条件、スコープ境界を抽出（約4,500トークン）
- Claude APIでエンドユーザー向けに変換

**エラーハンドリング**（憲章準拠）:
- 不整合検出時: 明確なエラーメッセージを表示して中断（フォールバック禁止）
- トークン数超過時: エラーメッセージを表示して中断（10,000トークン上限）
- LLM API失敗時: エラーメッセージを表示して中断（リトライなし）

### 1.3 変換済みコンテンツをJSON形式で保存

```bash
# 一時ファイルに保存（FR-022b ステップ3）
transformed_file=$(mktemp /tmp/llm-transformed-XXXXXX.json)

# JSON形式で保存
cat > "$transformed_file" <<EOF
{
  "001-feature-name": {
    "title": "機能タイトル",
    "content": "変換済みMarkdownコンテンツ..."
  },
  "002-another-feature": {
    "title": "別の機能",
    "content": "変換済みMarkdownコンテンツ..."
  }
}
EOF

echo "LLM変換完了: $transformed_file"
```

## Step 2: バックエンドスクリプト呼び出し（FR-022b ステップ4）

変換済みコンテンツをバックエンドスクリプトに渡す：

```bash
# FR-038e: --transformed-contentパラメータは必須
uv run python -m speckit_docs.scripts.doc_update --transformed-content "$transformed_file"
```

**このコマンドが実行すること**（バックエンドスクリプト）：
1. 変換済みコンテンツをJSONファイルから読み込み
2. Git diffで変更された機能を検出（インクリメンタル更新）
3. docs/以下にMarkdownページを生成（変換済みコンテンツを使用）
4. ナビゲーション（index.md / mkdocs.yml）を更新
5. 更新サマリーを表示（LLM変換統計含む）

**実行後の出力例**：
```
ドキュメントツール: sphinx
構造タイプ: flat

LLM変換済みコンテンツを読み込み中... (/tmp/llm-transformed-xxxxx.json)
✓ 2 件の変換済みコンテンツを読み込みました

機能を検出中...
✓ 2 個の変更された機能を検出しました（インクリメンタル更新）

ドキュメントページを生成中...
✓ 2 ページを生成しました

ナビゲーションを更新中...
✓ ナビゲーションを更新しました

✓ ドキュメント更新が完了しました！

サマリー:
  • 更新された機能: 2
  • 生成されたページ: 2

LLM変換統計:
  • 合計機能数: 2
  • LLM変換済み: 2
  • 元のコンテンツ: 0
  • 変換率: 100.0%
```

## Step 3: 一時ファイルのクリーンアップ

```bash
# 一時ファイルを削除
rm -f "$transformed_file"
echo "一時ファイルを削除しました"
```

## Error Handling（憲章準拠）

### Error 1: docs/が存在しない

```
✗ ドキュメントプロジェクトが見つかりません。
  最初に /speckit.doc-init を実行してください。
```

→ `/speckit.doc-init` を実行

### Error 2: specs/に機能がない

```
✗ specs/ ディレクトリに機能が見つかりません。
  /speckit.specify を実行して機能仕様を作成してください。
```

→ `/speckit.specify` を実行

### Error 3: LLM変換失敗（不整合検出）

```
✗ LLM変換エラー: README.md と QUICKSTART.md に重大な不整合が検出されました。

不整合の詳細:
  • 技術スタック: README.md では "Python 3.11" と記載、QUICKSTART.md では "Python 3.9" と記載
  • 機能: README.md では "認証機能" が含まれるが、QUICKSTART.md では言及なし

推奨アクション: README.md と QUICKSTART.md の内容を整合させてから再実行してください。
```

→ README.md/QUICKSTART.mdを修正してから再実行

### Error 4: LLM API失敗

```
✗ LLM API エラー: Claude API呼び出しに失敗しました。

エラー詳細: API rate limit exceeded (429)

推奨アクション: 数分待ってから再実行してください。
```

→ 待機してから再実行

### Error 5: transformed_contentパラメータ未提供（FR-038e）

```
✗ --transformed-contentパラメータは必須です。LLM変換を実行してから.specify/scripts/docs/doc_update.pyを呼び出してください。

推奨アクション: このコマンドテンプレートのワークフロー（Step 1 → Step 2）に従って実行してください。
```

→ コマンドテンプレートのワークフローに従う

### Note: Git履歴がない

```
Note: Git履歴が見つかりません。フル更新にフォールバックします。
```

→ 自動的にフル更新が実行される（問題なし）

## Generated Files

実行後、以下のファイルが更新/生成されます：

**Sphinx の場合**：
- `docs/[feature-name].md` - 各機能のドキュメントページ（LLM変換済みコンテンツ使用）
- `docs/index.md` - インデックスページ（toctree更新）

**MkDocs の場合**：
- `docs/[feature-name].md` - 各機能のドキュメントページ（LLM変換済みコンテンツ使用）
- `mkdocs.yml` - ナビゲーション設定（nav更新）

**一時ファイル**（実行中のみ）：
- `/tmp/llm-transformed-XXXXXX.json` - LLM変換済みコンテンツ（Step 3で削除）

## Next Steps

ドキュメント生成後：

### Sphinx の場合

```bash
cd docs
make html
open _build/html/index.html  # macOS
xdg-open _build/html/index.html  # Linux
```

### MkDocs の場合

```bash
cd docs
mkdocs serve
# ブラウザで http://127.0.0.1:8000 を開く
```

## Implementation Note（Session 2025-10-17）

このコマンドテンプレートは以下の実装に基づいています：

- ✅ **T018 (FR-022b)**: LLM変換ワークフロー実装（このテンプレート）
- ✅ **T070 (FR-038e)**: transformed_content必須パラメータ実装（doc_update.py）
- ⏳ **T062-T068**: LLM変換機能実装（コンテンツソース選択、不整合検出、セクション優先順位判定）
- ⏳ **T069**: LLM変換品質チェック実装
- ⏳ **T074-T075**: --quickフラグ実装

**注意**: LLM変換は常に有効です（Session 2025-10-17 決定39）。フォールバック動作は憲章により禁止されています。
