# Implementation Plan: spec-kit-docs - AI駆動型ドキュメント生成システム

**Branch**: `001-draft-init-spec` | **Date**: 2025-10-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-draft-init-spec/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

spec-kit-docsは、spec-kitプロジェクトのAI駆動型ドキュメント生成拡張機能です。

**主要機能**:
1. **`speckit-docs install`**: Pythonパッケージ内のテンプレートファイル（コマンド定義、スクリプト）をユーザープロジェクトの`.claude/commands/`と`.specify/scripts/docs/`にコピー
2. **`/doc-init`**: SphinxまたはMkDocsドキュメントプロジェクトを初期化（AIエージェント経由でインタラクティブに設定を収集）
3. **`/doc-update`**: `specs/`ディレクトリからドキュメントを自動生成・更新（Git diffベースのインクリメンタル更新）

**技術的アプローチ**（Phase 0 research.mdで決定）:
- **Markdown統一**: Sphinx + myst-parserを使用し、全ファイルをMarkdown形式で統一（spec.md/plan.md/tasks.mdからの変換不要）
- **Strategy Pattern**: BaseGeneratorを継承したSphinxGenerator/MkDocsGeneratorで拡張性を確保
- **非対話的実行**: AIエージェント（Claude Code）が対話を担当、Pythonスクリプトは引数のみで動作（CI/CD対応）
- **Git diff変更検出**: インクリメンタル更新での再処理を変更ファイルのみに限定（GitPython使用）

**重要な設計決定変更（Session 2025-10-13）**:
- **CLIフレームワーク**: argparse → **typer**に変更（Core Principle I「spec-kit Integration First」準拠）
  - 理由：本家spec-kitがtyperを使用し、specify-cli経由で既に依存ツリーに存在するため、実質的な追加依存なし
  - 利点：型ヒントのネイティブサポート（C006: 堅牢コード品質）、`typer.confirm()`統合、本家spec-kitパターンの再利用（C012: DRY原則）

## Technical Context

**Language/Version**: Python 3.11+（spec-kit前提条件との互換性）
**Primary Dependencies**:
- **CLIフレームワーク**: typer - 本家spec-kitとの一貫性を保つため採用（Session 2025-10-13 Clarificationで決定）。specify-cli経由で既に依存ツリーに存在
- **ドキュメントツール**: Sphinx 7.0+ with myst-parser 2.0+、MkDocs 1.5+
- **Markdown解析**: markdown-it-py 3.0+（MyST互換性）
- **テンプレート**: Jinja2 3.1+（設定ファイル・ドキュメント生成）
- **Git操作**: GitPython 3.1+（変更検出）
- **CLI UI（Phase 2）**: specify-cliからStepTracker/console再利用（統一UX）
**Storage**: N/A（ファイルシステム：`docs/`ディレクトリ、`.specify/scripts/docs/`、`.claude/commands/`）
**Testing**: pytest 8.0+、pytest-cov（単体テスト・統合テスト）
**Target Platform**: Linux/macOS（WSL2対応）
**Project Type**: single（Pythonパッケージとして配布、既存spec-kitプロジェクトに拡張機能を追加）
**Performance Goals**:
- `/doc-init`：30秒以内（対話的入力時間を除く）
- `/doc-update`：45秒以内（10機能フル更新）、5秒以内（1機能のみ変更時、インクリメンタル更新）
**Constraints**:
- **非対話的実行**: Pythonスクリプトは`input()`使用禁止（Core Principle II）
- **spec-kit統合**: `specify init --here`パターン、`--force`フラグ、エラーハンドリング（ベストエフォート方式）の一貫性（Core Principle I）
- **型安全性**: Python 3.11+ type hintsとmypyチェック必須（C006: 堅牢コード品質）
**Scale/Scope**:
- **対象機能数**: 1-20機能（典型的）、50機能以上（Phase 3で並列処理最適化）
- **対象ユーザー**: spec-kitプロジェクトを持つ開発者、AIエージェント（Claude Code、将来的にはGitHub Copilot/Gemini等）
- **MVP範囲（Phase 1）**: 基本的なドキュメント初期化・更新のみ（高度な統合機能、対象者別フィルタリング、バージョン履歴追跡はPhase 2-3）

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Critical Rules Compliance (C001-C014)

| Rule | Status | Compliance Note |
|------|--------|-----------------|
| C001: ルール歪曲禁止・最上位命令遵守 | ✅ PASS | このConstitution Checkの実施自体がC001への準拠を示す。すべての設計判断はconstitution.mdの原則に従う |
| C002: エラー迂回絶対禁止・主観判断排除 | ✅ PASS | SpecKitDocsError例外による明示的エラーハンドリング（FR-035）。ログファイル優先確認はGitPythonエラーログに適用 |
| C003: 冒頭表示必須 | ✅ PASS | AI Agent (Claude Code)が`/doc-init`, `/doc-update`実行時に表示する責務を持つ（コマンド定義.mdに記載） |
| C004: 理想実装ファースト原則 | ✅ PASS | **typer採用決定**（argparseからの変更）がこの原則の実践例。「とりあえずargparseで」ではなく、理想的な設計（本家spec-kitとの一貫性）を最初から実現 |
| C005: 記録管理徹底 | ✅ PASS | research.md（技術決定の根拠記録）、Session 2025-10-13 Clarification（typer採用の決定記録）が存在 |
| C006: 堅牢コード品質 | ✅ PASS | pyproject.tomlでruff/black/mypyを開発依存に含める。Type hints必須（Python 3.11+）、Constraints項で明記 |
| C007: 品質例外化禁止 | ✅ PASS | MVP範囲の明確化（Phase 1-3）により「時間がないから機能削減」ではなく、最初から必要十分な機能のみを定義 |
| C008: ドキュメント整合性絶対遵守 | ✅ PASS | spec.md → plan.md → research.mdの順で一貫性を保持。typer採用は spec.md Clarificationで記録後、plan.mdとresearch.mdに反映 |
| C009: 実装計画ブランチ作成必須 | ✅ PASS | Branch: `001-draft-init-spec`で実施中 |
| C010: テスト駆動開発必須 | ✅ PASS | pytest使用、Red-Green-Refactorサイクルを tasks.md生成時に反映（実装前テスト作成を義務付け） |
| C011: 一次データ推測禁止 | ✅ PASS | FR-003b: 引数未指定時のデフォルト値は、Git user.nameやディレクトリ名など**取得可能な値**のみ。推測は禁止 |
| C012: DRY原則 | ✅ PASS | **typer採用の理由の一つ**：本家spec-kitのtyperパターン（`typer.confirm()`等）を再利用。StepTracker/console再利用（Phase 2計画） |
| C013: 破壊的リファクタリング推奨 | ✅ PASS | **argparse → typerへの変更**がこの原則の実践例。V2クラス作成ではなく、既存設計（research.md Section 7）を直接修正 |
| C014: 妥協実装絶対禁止 | ✅ PASS | typer採用決定により「argparseで暫定実装して後でtyperにリファクタリング」という妥協を排除。最初から理想形で実装 |

**Critical Rules Summary**: 全14ルール準拠 ✅

---

### Core Principles Compliance (I-V)

#### I. spec-kit Integration First ✅ PASS

**Evidence**:
- **typer採用決定**（Session 2025-10-13）：本家spec-kitとの一貫性を最優先し、argparseから変更
- `specify init --here`パターンの採用（FR-021b）
- `--force`フラグの一貫したセマンティクス（FR-003d, FR-023b）
- エラーハンドリングのベストエフォート方式（FR-023c）
- `specs/`ディレクトリ構造の正しい認識（Session 2025-10-12 Correctionで修正済み）

**Compliance Level**: 完全準拠

---

#### II. Non-Interactive Execution ✅ PASS

**Evidence**:
- FR-003c: doc_init.pyは標準入力（stdin）を使用しない
- FR-003a: すべての設定はコマンドライン引数から取得
- FR-003b: 引数未指定時のデフォルト値を明確に定義
- FR-022a/022b: AIエージェント（Claude Code）が対話を担当、スクリプトは非対話的に実行

**Constraints項で明記**: Pythonスクリプトは`input()`使用禁止

**Compliance Level**: 完全準拠

---

#### III. Extensibility & Modularity ✅ PASS

**Evidence**:
- Strategy Pattern: BaseGenerator抽象ベースクラス + SphinxGenerator/MkDocsGenerator実装（research.md Section 3）
- 独立モジュール: `generators/sphinx.py`, `generators/mkdocs.py`
- パーサーとジェネレータの分離: markdown-it-py（パーサー）とJinja2（ジェネレーター）
- 将来拡張への準備: Phase 2-3で他のドキュメントツール（Docusaurus、VitePress）やAIエージェント（GitHub Copilot、Gemini）のサポート追加が容易

**Compliance Level**: 完全準拠

---

#### IV. Incremental Delivery ✅ PASS

**Evidence**:
- MVP範囲（Phase 1）: 基本的なドキュメント初期化・更新のみ（P1ユーザーストーリー3つ）
- Phase 2-3: 高度な統合機能、対象者別フィルタリング、バージョン履歴追跡（P2-P3ユーザーストーリー）
- 優先度マーキング: spec.mdの各ユーザーストーリーにP1/P2/P3を明記
- アンインストール/アップグレード機能: MVP範囲外（Scope Boundaryで明確化）

**Relationship to C004**: typer採用決定により、**Phase 1の理想品質実装**が保証される（「まずargparseで動かして後で改善」という妥協を排除）

**Compliance Level**: 完全準拠

---

#### V. Testability (Enhanced with C010) ✅ PASS

**Evidence**:
- pytest 8.0+ + pytest-cov使用（Technical Context）
- **TDD必須（C010）**: Red-Green-Refactorサイクルを tasks.md生成時に義務付け
- 決定的な入力/出力: 非対話的実行によりテストケース作成が容易
- ファイルシステム操作の抽象化: pytestのtmpdir fixtureでモック可能
- 統合テスト計画: 実際のspec-kitプロジェクト構造を使用（Testability原則）

**Target Coverage**: 主要コードパス（初期化、更新、エラーハンドリング）の90%以上

**Compliance Level**: 完全準拠

---

### Post-Design Constitution Check Re-Evaluation

**Timing**: Phase 1設計完了後（data-model.md, contracts/, quickstart.md生成後）に再評価

**Current Status**: Phase 0完了、research.mdとplan.md Technical Contextが整合済み。**typer採用決定により、C004/C012/C013/C014への準拠が強化された**。

**Action Required**: Phase 1完了後、この Constitution Check セクションを再確認し、設計変更があればConstitution準拠を再評価する。

---

### Constitution Check Conclusion

✅ **All 14 Critical Rules (C001-C014) PASSED**
✅ **All 5 Core Principles (I-V) PASSED**

**Key Decision**: typer採用（argparseから変更）により、以下の原則への準拠が強化された：
- C004 (理想実装ファースト): 最初から理想的な設計を実現
- C012 (DRY原則): 本家spec-kitのtyperパターン再利用
- C013 (破壊的リファクタリング推奨): 既存設計を直接修正
- C014 (妥協実装絶対禁止): 「後で改善」の技術的負債を排除
- Core Principle I (spec-kit Integration First): 本家spec-kitとの完全な一貫性

**Gate Status**: ✅ CLEARED - Phase 0 researchおよびtyper採用決定により、すべての憲章要件を満たしている。Phase 1設計作業に進んで良い。

## Project Structure

### Documentation (this feature)

```
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
