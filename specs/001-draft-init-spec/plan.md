# Implementation Plan: spec.md最小限抽出実装（Clarificationsセクション除外）

**Branch**: `001-draft-init-spec` | **Date**: 2025-10-17 | **Spec**: [spec.md](spec.md)
**Input**: `/speckit.doc-update`がClarificationsセクション（600行以上の技術的Q&A）をドキュメント化している問題を修正

## Summary

現在、`/speckit.doc-update`コマンドはspec.md全体をテンプレートに渡しているため、Clarificationsセクション（600行以上の技術的Q&A）がそのままエンドユーザー向けドキュメントに出力されています。FR-038で既に定義されている**spec.md最小限抽出**ロジックを実装し、エンドユーザー向けに必要な情報のみ（ユーザーストーリーの目的、前提条件、スコープ境界）を抽出します。

**技術的アプローチ**: markdown-it-pyを使用したMarkdown ASTパース + セクション抽出ロジックの実装

## Technical Context

**Language/Version**: Python 3.11+（既存プロジェクトと同じ）
**Primary Dependencies**:
- markdown-it-py 3.0+（既存依存関係、Markdownパース）
- anthropic 0.28+（LLM変換用、既存依存関係）
- typer 0.9+（CLI、既存依存関係）

**Storage**: N/A（ファイルシステムのみ）
**Testing**: pytest 8.0+、pytest-cov 4.0+（既存テストフレームワーク）
**Target Platform**: Linux/macOS/WSL2（spec-kitと同じ）
**Project Type**: Single project（既存構造）
**Performance Goals**:
- spec.md抽出処理: <1秒（100KB以下のファイル）
- LLM変換: <10秒（1機能あたり、API依存）

**Constraints**:
- FR-038: 抽出後のコンテンツは約4,500トークン、最大10,000トークン以内
- FR-038c: LLM生成コンテンツの品質チェック（空文字列、最小50文字、エラーパターン、Markdown構文）
- C002: エラー発生時は迂回禁止（フォールバック動作なし）
- C010: TDD必須（Red-Green-Refactorサイクル）

**Scale/Scope**:
- 対象: 1-20機能のspec-kitプロジェクト（既存想定と同じ）
- spec.mdサイズ: 通常100-500行、最大2000行程度

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Core Principles Compliance

✅ **I. spec-kit Integration First**:
- FR-038はspec.mdの推奨構造を前提としており、spec-kit標準テンプレートと整合
- コマンドテンプレート（`.claude/commands/speckit.doc-update.md`）を修正し、既存ワークフローに統合

✅ **II. Non-Interactive Execution**:
- Markdown抽出ロジックは決定的（同じspec.mdから同じ結果）
- エラー時は構造化されたエラーメッセージを返す（FR-038: 抽出失敗時のエラーハンドリング）

✅ **III. Extensibility & Modularity**:
- 新しい`utils/spec_extractor.py`モジュールとして実装（既存の`utils/`構造と一貫）
- markdown-it-pyを使用し、将来的な抽出ルール拡張が容易

✅ **IV. Incremental Delivery**:
- この修正はP1（MVP）機能の一部（FR-038: Phase 1 - MVP）
- 既存の機能を破壊せず、spec.md抽出機能のみを追加

✅ **V. Testability**:
- TDD必須（C010）: 実装前にテストを作成
- 単体テスト: `tests/unit/utils/test_spec_extractor.py`（抽出ロジック）
- 統合テスト: `tests/integration/test_spec_extraction.py`（実際のspec.mdファイル使用）

### Critical Rules Compliance

✅ **C001 (ルール歪曲禁止)**: FR-038の定義に厳密に従う
✅ **C002 (エラー迂回禁止)**: 抽出失敗時は明確なエラーで中断（フォールバックなし）
✅ **C004 (理想実装ファースト)**: 段階的改善ではなく、最初から完全な抽出ロジックを実装
✅ **C008 (ドキュメント整合性)**: FR-038仕様に完全準拠
✅ **C010 (TDD必須)**: Red-Green-Refactorサイクルに従う
✅ **C011 (一次データ推測禁止)**: セクション見出しが見つからない場合は推測せず、エラーを発生
✅ **C012 (DRY原則)**: markdown-it-pyの既存パーサーを再利用
✅ **C014 (妥協実装禁止)**: 簡易版ではなく、完全な抽出ロジックを実装

### Gate Result

**PASS** - すべての原則とクリティカルルールに準拠。Phase 0に進む。

## Project Structure

### Documentation (this feature)

```
specs/001-draft-init-spec/
├── spec.md              # 機能仕様（既存、変更なし）
├── plan.md              # このファイル
├── research.md          # Phase 0で生成（markdown-it-pyのベストプラクティス等）
├── data-model.md        # Phase 1で生成（SpecExtractionResultエンティティ等）
├── quickstart.md        # Phase 1で生成（spec.md抽出機能の使用方法）
└── contracts/           # N/A（APIエンドポイントなし）
```

### Source Code (repository root)

```
src/speckit_docs/
├── utils/
│   ├── spec_extractor.py         # [NEW] spec.md最小限抽出ロジック
│   ├── markdown_parser.py         # [EXISTING] 既存のMarkdownパーサー（参照用）
│   └── llm_transform.py           # [EXISTING] LLM変換ロジック（変更あり）
├── generators/
│   └── feature_page.py            # [MODIFY] spec抽出ロジックを使用
├── scripts/
│   └── doc_update.py              # [NO CHANGE] バックエンドスクリプト（変更なし）
└── exceptions.py                  # [MODIFY] 新しい例外クラス追加（SpecExtractionError）

tests/
├── unit/
│   └── utils/
│       └── test_spec_extractor.py # [NEW] spec抽出ロジックの単体テスト
├── integration/
│   └── test_spec_extraction.py    # [NEW] 実際のspec.mdを使用した統合テスト
└── fixtures/
    └── sample_specs/
        ├── valid_spec.md          # [NEW] テスト用の有効なspec.md
        ├── missing_section_spec.md # [NEW] セクション欠如のspec.md
        └── malformed_spec.md      # [NEW] 不正な構造のspec.md

.claude/commands/
└── speckit.doc-update.md          # [MODIFY] LLM変換ワークフローにspec抽出を統合
```

**Structure Decision**: 既存の単一プロジェクト構造を維持。新しい`utils/spec_extractor.py`モジュールを追加し、既存の`feature_page.py`と`.claude/commands/speckit.doc-update.md`を修正してspec抽出ロジックを統合します。

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

該当なし - すべての憲章原則に準拠しています。
