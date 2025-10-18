# Tasks: spec.md最小限抽出実装（Clarificationsセクション除外）

**Input**: Design documents from `/home/driller/repo/spec-kit-docs/specs/001-draft-init-spec/`
**Prerequisites**: plan.md, spec.md (ユーザーストーリー7), data-model.md, research.md
**Branch**: `001-draft-init-spec`

**Feature Scope**: この実装は**ユーザーストーリー7（LLMによるユーザーフレンドリーなドキュメント生成）**のうち、**FR-038: spec.md最小限抽出機能**に特化しています。`/speckit.doc-update`がClarificationsセクション（600行以上の技術的Q&A）をドキュメント化している問題を解決します。

**Tests**: この機能はTDD必須（C010）。すべてのテストを実装前に作成し、Red-Green-Refactorサイクルに従います。

## Format: `[ID] [P?] [US7] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[US7]**: This feature belongs to User Story 7 (LLM-powered user-friendly documentation)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Test Infrastructure)

**Purpose**: TDD環境のセットアップとテストフィクスチャの準備

- [X] T001 [P] テストフィクスチャディレクトリを作成 `tests/fixtures/sample_specs/`
- [X] T002 [P] [US7] 有効なspec.mdサンプルを作成 `tests/fixtures/sample_specs/valid_spec.md`（ユーザーストーリー、前提条件、スコープ境界を含む）
- [X] T003 [P] [US7] セクション欠如のspec.mdサンプルを作成 `tests/fixtures/sample_specs/missing_section_spec.md`（前提条件セクションなし）
- [X] T004 [P] [US7] 不正な構造のspec.mdサンプルを作成 `tests/fixtures/sample_specs/malformed_spec.md`（ユーザーストーリーの目的が空）

---

## Phase 2: Foundational (Data Model)

**Purpose**: spec.md抽出機能の基礎となるデータモデルを実装

**⚠️ CRITICAL**: このフェーズを完了しないと、実装タスクを開始できません

- [X] T005 [US7] データモデルクラスを作成 `src/speckit_docs/utils/spec_extractor.py`（`SpecExtractionResult`と`UserStoryPurpose`の`@dataclass`定義）
- [X] T006 [US7] `SpecExtractionResult.to_markdown()`メソッドを実装（抽出結果をMarkdown形式で出力）

**Checkpoint**: データモデル準備完了 - TDDサイクル開始可能

---

## Phase 3: User Story 7 - spec.md最小限抽出機能 (Priority: P1) 🎯 MVP

**Goal**: spec.mdから必要な情報のみ（ユーザーストーリーの目的、前提条件、スコープ境界）を抽出し、Clarificationsセクション（600行以上の技術的Q&A）を除外することで、エンドユーザー向けドキュメントの品質を改善する

**Independent Test**:
1. 有効なspec.md（ユーザーストーリー、前提条件、スコープ境界を含む）から抽出し、約4,500トークン（10,000トークン以内）のコンテンツが返される
2. セクション欠如のspec.mdから抽出を試み、`SpecKitDocsError`（error_type="Missing Required Sections"）が発生する
3. 実際のプロジェクトspec.md（`specs/001-draft-init-spec/spec.md`）から抽出し、Clarificationsセクションが除外されていることを確認

### Tests for User Story 7 (TDD Required) ⚠️

**NOTE: Write these tests FIRST, ensure they FAIL before implementation**

#### 単体テスト（抽出ロジック）

- [X] T007 [P] [US7] 正常系テスト: 有効なspec.mdから正しく抽出できる `tests/unit/utils/test_spec_extractor.py::test_extract_spec_minimal_valid`
- [X] T008 [P] [US7] 必須セクション欠如テスト: 前提条件がない場合にエラーが発生 `tests/unit/utils/test_spec_extractor.py::test_extract_spec_minimal_missing_prerequisites`
- [X] T009 [P] [US7] 必須セクション欠如テスト: ユーザーストーリーがない場合にエラーが発生 `tests/unit/utils/test_spec_extractor.py::test_extract_spec_minimal_missing_user_stories`
- [X] T010 [P] [US7] 必須セクション欠如テスト: スコープ境界がない場合にエラーが発生 `tests/unit/utils/test_spec_extractor.py::test_extract_spec_minimal_missing_scope`
- [X] T011 [P] [US7] トークン数超過テスト: 抽出後のコンテンツが10,000トークンを超える場合にエラーが発生 `tests/unit/utils/test_spec_extractor.py::test_extract_spec_minimal_token_limit_exceeded`
- [X] T012 [P] [US7] 多言語対応テスト: 日本語の見出し（「## 前提条件」）を検出 `tests/unit/utils/test_spec_extractor.py::test_extract_spec_minimal_japanese_headings`
- [X] T013 [P] [US7] 多言語対応テスト: 英語の見出し（「## Prerequisites」）を検出 `tests/unit/utils/test_spec_extractor.py::test_extract_spec_minimal_english_headings`
- [X] T014 [P] [US7] 空コンテンツテスト: ユーザーストーリーの目的が空の場合にエラーが発生 `tests/unit/utils/test_spec_extractor.py::test_extract_spec_minimal_empty_purpose`
- [X] T015 [P] [US7] トークン数カウントテスト: `SpecExtractionResult.total_token_count`が正しく計算される `tests/unit/utils/test_spec_extractor.py::test_spec_extraction_result_token_count`
- [X] T016 [P] [US7] Markdown出力テスト: `SpecExtractionResult.to_markdown()`が正しいフォーマットで出力 `tests/unit/utils/test_spec_extractor.py::test_spec_extraction_result_to_markdown`

#### 統合テスト（実際のspec.mdを使用）

- [X] T017 [US7] エンドツーエンドテスト: 本プロジェクトの`specs/001-draft-init-spec/spec.md`から抽出し、Clarificationsが除外されることを確認 `tests/integration/test_spec_extraction.py::test_extract_from_real_spec`
- [X] T018 [US7] エラーシナリオテスト: 不正な構造のspec.mdでエラーハンドリングを検証 `tests/integration/test_spec_extraction.py::test_extract_from_malformed_spec`

### Implementation for User Story 7

**Phase 3A: 抽出ロジックの実装**

- [X] T019 [US7] `extract_spec_minimal()`関数のスケルトンを実装 `src/speckit_docs/utils/spec_extractor.py`（関数シグネチャ、docstring、Raiseクローズ）
- [X] T020 [US7] MarkdownParserを使用してspec.mdを解析 `src/speckit_docs/utils/spec_extractor.py::extract_spec_minimal()`（`parser.parse(content)`呼び出し）
- [X] T021 [US7] ユーザーストーリーの「目的」セクションを抽出 `src/speckit_docs/utils/spec_extractor.py::_extract_user_story_purposes()`（`### ユーザーストーリーN:`見出しから`**目的**:`を正規表現で抽出）
- [X] T022 [US7] 前提条件セクション全体を抽出 `src/speckit_docs/utils/spec_extractor.py::_extract_prerequisites()`（`## 前提条件`または`## Prerequisites`セクション）
- [X] T023 [US7] スコープ境界の「スコープ外」部分を抽出 `src/speckit_docs/utils/spec_extractor.py::_extract_scope_boundaries()`（`## スコープ境界` → `**スコープ外**:`部分）
- [X] T024 [US7] トークン数カウントとバリデーション `src/speckit_docs/utils/spec_extractor.py::extract_spec_minimal()`（`estimate_token_count()`を使用、10,000トークン超過時に`SpecKitDocsError`を発生）
- [X] T025 [US7] 必須セクション存在チェック `src/speckit_docs/utils/spec_extractor.py::extract_spec_minimal()`（ユーザーストーリー、前提条件、スコープ境界が存在しない場合に`SpecKitDocsError`を発生）

**Phase 3B: エラーハンドリングとエッジケース**

- [X] T026 [US7] エラーメッセージの明確化 `src/speckit_docs/utils/spec_extractor.py`（C002準拠: ファイルパス、エラー種類、推奨アクションを含む`SpecKitDocsError`）
- [X] T027 [US7] 空コンテンツのバリデーション `src/speckit_docs/utils/spec_extractor.py`（ユーザーストーリーの目的が空または空白のみの場合にエラー）
- [X] T028 [US7] 多言語見出し対応 `src/speckit_docs/utils/spec_extractor.py`（日本語と英語の両方の見出しパターンをサポート）

**Phase 3C: 統合と既存コードの修正**

- [X] T029 [US7] コマンドテンプレート修正 `.claude/commands/speckit.doc-update.md`（LLM変換ワークフローにspec抽出を統合、`extract_spec_minimal()`呼び出しを追加）
- [X] T030 [US7] 既存のLLM変換ロジック削除 `src/speckit_docs/utils/llm_transform.py:446-542`（低レベルトークン処理を削除し、新しい`extract_spec_minimal()`を使用するようリファクタリング）

**Checkpoint**: spec.md最小限抽出機能が完全に実装され、すべてのテストがパス

---

## Phase 4: Polish & Validation

**Purpose**: ドキュメント更新とコード品質の確認

- [ ] T031 [P] quickstart.mdの検証 `specs/001-draft-init-spec/quickstart.md`（記載されている使用方法と実装が一致しているか確認）
- [ ] T032 [P] 型チェック実行 `uv run mypy src/speckit_docs/utils/spec_extractor.py`（0エラー）
- [ ] T033 [P] Lintチェック実行 `uv run ruff check src/speckit_docs/utils/spec_extractor.py`（0警告）
- [ ] T034 カバレッジ確認 `uv run pytest --cov=speckit_docs.utils.spec_extractor --cov-report=term`（90%以上）
- [ ] T035 [US7] 実際のプロジェクトでの動作確認: `specs/001-draft-init-spec/spec.md`から抽出し、Clarificationsが除外されていることを手動で確認

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS User Story 7 implementation
- **User Story 7 (Phase 3)**: Depends on Foundational phase completion
  - Phase 3A (Tests): Can start after Phase 2
  - Phase 3B (Implementation): Can start after Phase 3A tests are written and FAILING
  - Phase 3C (Integration): Depends on Phase 3B completion
- **Polish (Phase 4)**: Depends on Phase 3 completion

### Within User Story 7 (Phase 3)

- T007-T018 (Tests) MUST be written and FAIL before T019-T030 (Implementation)
- T019-T025 (抽出ロジック実装) must complete before T026-T028 (エラーハンドリング)
- T029-T030 (統合) must complete after T019-T028

### Parallel Opportunities

- **Phase 1**: T001-T004 can all run in parallel (different fixture files)
- **Phase 3A Tests**: T007-T016 can all run in parallel (different test functions)
- **Phase 4**: T031-T033 can run in parallel (different validation tasks)

---

## Parallel Example: User Story 7

```bash
# Phase 1: Create all test fixtures together
Task: "テストフィクスチャディレクトリを作成 tests/fixtures/sample_specs/"
Task: "有効なspec.mdサンプルを作成 tests/fixtures/sample_specs/valid_spec.md"
Task: "セクション欠如のspec.mdサンプルを作成 tests/fixtures/sample_specs/missing_section_spec.md"
Task: "不正な構造のspec.mdサンプルを作成 tests/fixtures/sample_specs/malformed_spec.md"

# Phase 3A: Write all unit tests together (BEFORE implementation)
Task: "正常系テスト tests/unit/utils/test_spec_extractor.py::test_extract_spec_minimal_valid"
Task: "必須セクション欠如テスト tests/unit/utils/test_spec_extractor.py::test_extract_spec_minimal_missing_prerequisites"
Task: "トークン数超過テスト tests/unit/utils/test_spec_extractor.py::test_extract_spec_minimal_token_limit_exceeded"
# ... (all T007-T016 tests)

# Phase 4: Run all validation checks together
Task: "型チェック実行 uv run mypy src/speckit_docs/utils/spec_extractor.py"
Task: "Lintチェック実行 uv run ruff check src/speckit_docs/utils/spec_extractor.py"
```

---

## Implementation Strategy

### MVP First (User Story 7 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T006) - CRITICAL
3. Complete Phase 3: User Story 7
   - Write ALL tests first (T007-T018)
   - Verify tests FAIL
   - Implement extraction logic (T019-T025)
   - Add error handling (T026-T028)
   - Integrate with existing code (T029-T030)
4. **STOP and VALIDATE**: Run all tests, verify spec.md extraction works
5. Complete Phase 4: Polish (T031-T035)

### TDD Workflow (Red-Green-Refactor)

**Phase 3 follows strict TDD**:
1. **RED**: Write T007-T018 tests → All tests FAIL
2. **GREEN**: Implement T019-T030 → All tests PASS
3. **REFACTOR**: Clean up code, run T031-T035 validation

### Checkpoint Validation

After Phase 3C completion (T030):
- Run `uv run pytest tests/unit/utils/test_spec_extractor.py -v` → All tests pass
- Run `uv run pytest tests/integration/test_spec_extraction.py -v` → All tests pass
- Manually execute `/speckit.doc-update` on this project → Verify Clarifications excluded

---

## Notes

- **[P] tasks**: Different files, no dependencies - can run in parallel
- **[US7] label**: Maps task to User Story 7 (LLM-powered documentation)
- **TDD Required (C010)**: All tests (T007-T018) MUST be written before implementation (T019-T030)
- **Constitution Compliance**:
  - **C002**: No fallback behavior - strict error handling
  - **C010**: TDD mandatory - Red-Green-Refactor cycle
  - **C011**: No primary data assumption - raise error if sections missing
  - **C012**: DRY - reuse existing MarkdownParser
  - **C014**: No compromise implementation - complete extraction logic from start
- **Error Messages**: Must include file path, error type, and actionable suggestion (C002)
- **Token Limit**: 10,000 tokens maximum per feature (FR-038a)
- **Extraction Target**: User story purposes + Prerequisites + Scope boundaries only (FR-038)
- **Excluded Content**: Clarifications, Success Criteria, Implementation details, plan.md, tasks.md

---

## Expected Outcomes

After completing all tasks:

1. ✅ **spec.md最小限抽出機能が実装される**: `src/speckit_docs/utils/spec_extractor.py`
2. ✅ **Clarificationsセクションが除外される**: 600行以上の技術的Q&Aがドキュメントに出力されない
3. ✅ **エンドユーザー向けコンテンツのみが抽出される**: ユーザーストーリーの目的、前提条件、スコープ境界
4. ✅ **トークン制限が遵守される**: 抽出後のコンテンツは約4,500トークン（最大10,000トークン）
5. ✅ **厳格なエラーハンドリング**: 必須セクション欠如、トークン数超過時に明確なエラーメッセージ
6. ✅ **TDDによる高品質実装**: すべてのテストがパス、カバレッジ90%以上
7. ✅ **既存コードの改善**: `llm_transform.py:446-542`の低レベルトークン処理を削除、DRY原則に準拠
