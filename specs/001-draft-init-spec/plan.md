# Implementation Plan: spec-kit-docs - AI駆動型ドキュメント生成システム

**Branch**: `001-draft-init-spec` | **Date**: 2025-10-18 (Updated) | **Spec**: [spec.md](spec.md)
**Input**: spec-kit-docsの完全な実装計画（spec.md最小限抽出 + README/QUICKSTART統合強化）

## Summary

spec-kit-docsは、spec-kitプロジェクトのドキュメント生成を自動化するAI駆動型ツールです。仕様ファイル（spec.md、plan.md、tasks.md）とユーザー提供のドキュメント（README.md、QUICKSTART.md）からSphinx/MkDocsドキュメントを生成します。Claude APIを使用してコンテンツをユーザーフレンドリーな形式に変換し、技術者だけでなく非技術者（プロダクトマネージャー、顧客等）にも理解しやすいドキュメントを提供します。

**実装フェーズ**:
- **Phase 1 (完了)**: spec.md最小限抽出機能（FR-038）- Clarificationsセクション除外
- **Phase 2 (計画中)**: README/QUICKSTART統合強化（FR-038-target/classify/stats/integ-a/integ-b）- ターゲット読者判定、セクション分類、不整合検出、統合

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

---

## Phase 2: README/QUICKSTART統合強化

*Session 2025-10-18追加: FR-038-target, FR-038-classify, FR-038-stats, FR-038-integ-a, FR-038-integ-b実装計画*

### 概要

Phase 1ではspec.md最小限抽出機能（FR-038）を実装しました。Phase 2では、README.md/QUICKSTART.md処理を強化し、以下の機能を追加します：

1. **ターゲット読者判定（FR-038-target）**: LLMでドキュメントのターゲット読者を判定（一般エンドユーザー、技術者/開発者、両方）
2. **セクション分類（FR-038-classify）**: 各セクションの読者を分類（エンドユーザー向け、開発者向け、両方）
3. **統計情報表示（FR-038-stats）**: 判定結果と分類結果をユーザーに表示
4. **不整合検出（FR-038-integ-a）**: README.mdとQUICKSTART.mdが両方存在する場合、LLMで矛盾を検出
5. **セクション単位統合（FR-038-integ-b）**: 不整合がない場合、LLMで優先順位付けしてセクションを統合

### Technical Context (Phase 2追加分)

**Additional Dependencies**: なし（既存のmarkdown-it-py、anthropic SDK、typer使用）
**Performance Goals**:
- ターゲット読者判定: <5秒（1ファイルあたり、LLM API依存）
- セクション分類: <10秒（10セクションあたり、LLM API依存）
- 不整合検出: <10秒（2ファイルあたり、LLM API依存）
- セクション統合: <15秒（20セクションあたり、LLM API依存）

**Constraints**:
- LLM呼び出し失敗時は明確なエラーで中断（C002: エラー迂回禁止）
- セクション分類結果は優先順位判定に影響を与えない（FR-038-integ-b、Session 2025-10-18 Q3）
- 統計情報は情報提供のみ（FR-038-stats）

### Constitution Check (Phase 2)

すべてのCore PrinciplesとCritical Rulesに準拠（Phase 1と同じ）:

✅ **C002 (エラー迂回禁止)**: LLM呼び出し失敗時は明確なエラーで中断
✅ **C010 (TDD必須)**: Red-Green-Refactorサイクルに従う
✅ **C011 (一次データ推測禁止)**: LLM判定結果が得られない場合は推測せず、エラーを発生
✅ **C012 (DRY原則)**: 既存のLLM変換ロジック（`llm_transform.py`）を再利用
✅ **C014 (妥協実装禁止)**: 最初から完全なLLM判定ロジックを実装

### Implementation Strategy

**Phase 2A: Data Model拡張**
- `llm_entities.py`に新しいエンティティ追加：
  - `TargetAudienceResult`: ターゲット読者判定結果
  - `SectionClassification`: セクション分類結果
  - `InconsistencyDetectionResult`: 不整合検出結果
  - `SectionPriority`: セクション優先順位

**Phase 2B: LLM判定ロジック実装**
- `llm_transform.py`に新しい関数追加：
  - `detect_target_audience()`: ターゲット読者判定
  - `classify_section()`: セクション分類
  - `detect_inconsistency()`: 不整合検出
  - `prioritize_sections()`: セクション優先順位付け（既存のSession 2025-10-17 Q3ロジックを拡張）

**Phase 2C: コマンドテンプレート修正**
- `.claude/commands/speckit.doc-update.md`を修正：
  - README.md/QUICKSTART.md処理時に新しいLLM判定を実行
  - 統計情報をユーザーに表示

**Phase 2D: テスト**
- 単体テスト: `tests/unit/utils/test_llm_transform_phase2.py`
  - ターゲット読者判定テスト
  - セクション分類テスト
  - 不整合検出テスト
  - セクション優先順位付けテスト
- 統合テスト: `tests/integration/test_readme_quickstart_integration.py`
  - README.md + QUICKSTART.md不整合検出（エラーケース）
  - README.md + QUICKSTART.mdセクション統合（正常ケース）

### Project Structure (Phase 2追加分)

```
src/speckit_docs/
├── llm_entities.py              # [MODIFY] 新しいエンティティ追加
├── utils/
│   └── llm_transform.py          # [MODIFY] 新しいLLM判定関数追加
└── exceptions.py                 # [MODIFY] 新しい例外クラス追加

tests/
├── unit/
│   └── utils/
│       └── test_llm_transform_phase2.py  # [NEW] Phase 2 LLM判定テスト
└── integration/
    └── test_readme_quickstart_integration.py  # [NEW] README/QUICKSTART統合テスト

.claude/commands/
└── speckit.doc-update.md         # [MODIFY] Phase 2 LLM判定を統合
```

### Phase 2 Deliverables

1. ✅ **Data Model拡張完了**: 新しいエンティティ定義
2. ✅ **LLM判定ロジック実装完了**: 4つの新しい関数
3. ✅ **コマンドテンプレート修正完了**: README/QUICKSTART処理強化
4. ✅ **テスト完了**: 単体テスト + 統合テスト（TDD）
5. ✅ **ドキュメント更新完了**: quickstart.md、data-model.mdにPhase 2内容を追加

### Risks and Mitigation

1. **LLM判定の精度**: ターゲット読者判定やセクション分類が不正確な場合
   - **対策**: プロンプトに明確な判定基準を含める（例：「技術用語が多い場合は開発者向け」）
   - **フォールバック**: なし（C002: エラー迂回禁止）- 判定失敗時は明確なエラー

2. **LLM API呼び出しコスト**: セクション数が多い場合
   - **対策**: セクション分類は必要に応じてバッチ処理（複数セクションを1回のLLM呼び出しで分類）
   - **制約**: 10,000トークン制限内で処理

3. **不整合検出の厳格さ**: 軽微な差異を不整合と誤判定
   - **対策**: プロンプトに「許容される差異」の例を含める（表記揺れ、詳細度の違い）
   - **ユーザー制御**: 不整合検出をスキップするフラグ提供（`--skip-inconsistency-check`）

### Phase 2 Readiness

✅ **Phase 2実装に進む準備が整いました**

- Phase 1（spec.md最小限抽出）が完了
- 新しいFR（FR-038-target/classify/stats/integ-a/integ-b）の要件が明確
- 憲章準拠を確認
- 実装戦略とリスク対策が定義済み

---

## Phase 2 Post-Design Constitution Re-check

*Phase 2（design）完了後の再評価*

### Core Principles Re-check

**I. spec-kit Integration First**: ✅ PASS（変更なし）
- Phase 2機能は既存のspec-kit統合を維持
- LLM判定ロジックは既存のワークフロー（`.claude/commands/speckit.doc-update.md`）に統合

**II. Non-Interactive Execution**: ✅ PASS（変更なし）
- LLM判定は決定的な入力（README.md/QUICKSTART.mdの内容）から結果を生成
- エラー時は構造化されたエラーメッセージを返す

**III. Extensibility & Modularity**: ✅ PASS（強化）
- 新しいLLM判定関数（`llm_transform.py`）は既存のLLM変換ロジックを拡張
- エンティティ（`llm_entities.py`）は独立して定義され、再利用可能

**IV. Incremental Delivery**: ✅ PASS（変更なし）
- Phase 2はMVP範囲（FR-038拡張）
- 既存機能を破壊せず、README/QUICKSTART処理のみを強化

**V. Testability**: ✅ PASS（強化）
- TDD必須（C010）: Phase 2テスト戦略をplan.mdに定義
- 単体テスト + 統合テストを追加

### Critical Rules Re-check

すべてのクリティカルルール（C001-C014）に変更なし、引き続き準拠：

✅ **C002 (エラー迂回禁止)**: LLM判定失敗時は明確なエラーで中断
✅ **C010 (TDD必須)**: Red-Green-Refactorサイクルに従う
✅ **C011 (一次データ推測禁止)**: LLM判定結果が得られない場合は推測せず、エラーを発生
✅ **C012 (DRY原則)**: 既存のLLM変換ロジック（`llm_transform.py`）を再利用
✅ **C014 (妥協実装禁止)**: 最初から完全なLLM判定ロジックを実装

### Design Quality Assessment (Phase 2)

1. **データモデルの完全性**: ✅
   - Phase 2エンティティ（TargetAudienceResult、SectionClassification、InconsistencyDetectionResult、SectionPriority）をdata-model.mdに定義
   - エンティティ関係図でデータフローを可視化
   - データ整合性ルール（5-8）を追加

2. **実装可能性**: ✅
   - 既存コード（llm_transform.py、llm_entities.py）の拡張方針を明確化
   - 新規作成ファイルと既存ファイルの修正を区別
   - 実装戦略（Phase 2A-D）を詳細化

3. **テスト容易性**: ✅
   - 単体テスト戦略を定義（`test_llm_transform_phase2.py`）
   - 統合テスト戦略を定義（`test_readme_quickstart_integration.py`）
   - モック戦略を明確化（LLM API呼び出しをモック）

### Potential Risks Update (Phase 2)

Phase 2で特定されたリスクと対策：

1. **LLM判定の精度** → **リスク軽減済み**
   - プロンプトに明確な判定基準を含める
   - フォールバック禁止（C002）により、判定失敗時は明確なエラー

2. **LLM API呼び出しコスト** → **リスク軽減済み**
   - セクション分類はバッチ処理可能
   - 10,000トークン制限内で処理

3. **不整合検出の厳格さ** → **リスク軽減済み**
   - プロンプトに「許容される差異」の例を含める
   - ユーザー制御可能（`--skip-inconsistency-check`フラグ）

### Phase 3 Readiness

✅ **Phase 3（/speckit.tasks）に進む準備が整いました**

- Phase 2設計ドキュメント（plan.md、data-model.md）が完成
- Phase 2エンティティが明確化
- エージェントコンテキスト（CLAUDE.md）が更新済み
- 憲章準拠を再確認

---
