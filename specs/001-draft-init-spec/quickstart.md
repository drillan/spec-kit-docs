# Quickstart: spec.md最小限抽出機能の使用方法

**作成日**: 2025-10-17
**対象**: spec.mdから必要な情報のみを抽出してエンドユーザー向けドキュメントを生成する機能

## 概要

この機能は、spec.mdの技術的な詳細（Clarificationsセクション等）を除外し、エンドユーザー向けに必要な情報のみを抽出します。

**抽出対象**（FR-038準拠）:
1. ユーザーストーリーの「**目的**」部分
2. 前提条件セクション全体
3. スコープ境界の「**スコープ外**」部分

**目的**: 600行以上のClarifications（技術的Q&A）がドキュメントに出力される問題を解決

---

## 使用方法

### 基本的な使い方

```bash
# 1. spec-kitプロジェクトのドキュメントを初期化
/speckit.doc-init

# 2. ドキュメントを更新（spec.md最小限抽出が自動的に実行される）
/speckit.doc-update
```

**内部処理**:
1. `/.claude/commands/speckit.doc-update.md`がLLM変換ワークフローを実行
2. spec.md最小限抽出が実行される（`utils/spec_extractor.py`）
3. 抽出されたコンテンツがLLM変換される（Claude API）
4. 変換済みコンテンツがドキュメントページに出力される

---

## spec.mdの推奨構造

抽出機能が正しく動作するために、spec.mdは以下の構造に従うことを推奨します：

```markdown
# 機能仕様書: [Feature Name]

## Clarifications
（このセクションは抽出されません）

## ユーザーストーリー

### ユーザーストーリー1: [Title]

**目的**: [Purpose description]  ← 抽出対象

**この優先度の理由**: ...

**独立テスト**: ...

### ユーザーストーリー2: [Title]

**目的**: [Purpose description]  ← 抽出対象

...

## 要件

（このセクションは抽出されません）

## 前提条件  ← 抽出対象（セクション全体）

- **spec-kit プロジェクト**: ...
- **仕様フォーマット**: ...

## スコープ境界

**スコープ外（フェーズ1 - MVP）**:  ← 抽出対象

- アンインストールコマンド
- 専用アップグレードコマンド
...

## 成功基準

（このセクションは抽出されません）
```

---

## エラーハンドリング

### エラー1: 必須セクション欠如

**エラーメッセージ**:
```
✗ specs/001-draft-init-spec/spec.md does not contain expected sections: Missing '## 前提条件'.

💡 Check that spec.md follows the recommended structure (User Stories, Prerequisites, Scope).
```

**解決方法**:
- spec.mdに`## 前提条件`または`## Prerequisites`セクションを追加
- `### ユーザーストーリーN:`見出しと`**目的**:`部分を追加
- `## スコープ境界`セクションと`**スコープ外**:`部分を追加

### エラー2: トークン数超過

**エラーメッセージ**:
```
✗ Extracted content exceeds 10,000 token limit: 12500 tokens.

💡 Please reduce spec.md content in User Story Purpose, Prerequisites, or Scope sections.
```

**解決方法**:
- ユーザーストーリーの「目的」部分を簡潔化
- 前提条件セクションの項目を削減
- スコープ境界の「スコープ外」リストを削減

---

## 開発者向け: プログラム的な使用

### Pythonコードからの使用

```python
from pathlib import Path
from speckit_docs.utils.spec_extractor import extract_spec_minimal
from speckit_docs.exceptions import SpecKitDocsError

try:
    spec_file = Path("specs/001-draft-init-spec/spec.md")
    result = extract_spec_minimal(spec_file)
    
    print(f"抽出成功: {result.total_token_count} トークン")
    print(f"ユーザーストーリー: {len(result.user_story_purposes)} 件")
    print(f"\n--- 抽出されたコンテンツ ---\n{result.to_markdown()}")
    
except SpecKitDocsError as e:
    print(f"エラー: {e.message}")
    print(f"推奨アクション: {e.suggestion}")
```

### 出力例

```
抽出成功: 4500 トークン
ユーザーストーリー: 7 件

--- 抽出されたコンテンツ ---
### ユーザーストーリー1: ドキュメント初期化

**目的**: spec-kitユーザーが、プロジェクト固有のニーズに合わせてカスタマイズ可能な、すぐに使える初期ドキュメント構造を生成できるようにします。

### ユーザーストーリー2: ドキュメント更新

**目的**: spec-kitユーザーが、機能仕様が進化するにつれてドキュメントを自動的に再生成できるようにします。

...

## 前提条件

- **spec-kit プロジェクト**: ユーザーは有効な spec-kit プロジェクトを持っている
- **仕様フォーマット**: ユーザーは標準 spec-kit テンプレートに従う

...

## スコープ境界

**スコープ外（フェーズ1 - MVP）**:

- アンインストールコマンド
- 専用アップグレードコマンド
- 他のドキュメントジェネレータのサポート
...
```

---

## テスト

### 単体テスト

```bash
# spec抽出ロジックのテスト
uv run pytest tests/unit/utils/test_spec_extractor.py -v
```

### 統合テスト

```bash
# 実際のspec.mdを使用したエンドツーエンドテスト
uv run pytest tests/integration/test_spec_extraction.py -v
```

---

## トラブルシューティング

### Q1: ClarificationsセクションがまだドキュメントI出力される

**確認事項**:
1. `.claude/commands/speckit.doc-update.md`がLLM変換ワークフローを実行しているか
2. `extract_spec_minimal()`が正しく呼び出されているか
3. `transformed_content_map`が正しく渡されているか

**デバッグ**:
```bash
# doc_update.pyの実行ログを確認
uv run python -m speckit_docs.scripts.doc_update --verbose --transformed-content /tmp/test.json
```

### Q2: 多言語のspec.mdに対応していない

**解決策**:
- 日本語と英語の見出しパターンに対応済み
- 他の言語が必要な場合は`spec_extractor.py`の見出しパターンを追加

---

## 関連ドキュメント

- **機能仕様**: [spec.md](spec.md) - FR-038
- **実装計画**: [plan.md](plan.md)
- **データモデル**: [data-model.md](data-model.md)
- **研究レポート**: [research.md](research.md)
