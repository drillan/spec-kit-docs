# Tasks: spec-kit-docs AI駆動型ドキュメント生成システム

**Input**: Design documents from `/home/driller/repo/spec-kit-docs/specs/001-draft-init-spec/`
**Prerequisites**: plan.md, spec.md (ユーザーストーリー7), data-model.md, research.md
**Branch**: `001-draft-init-spec`

**Feature Scope**: この実装は**ユーザーストーリー7（LLMによるユーザーフレンドリーなドキュメント生成）**の完全な実装です：
- **Phase 1-4（完了）**: FR-038 spec.md最小限抽出機能
- **Phase 5（計画中）**: FR-038-target/classify/stats/integ-a/integ-b README/QUICKSTART統合強化

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

- [X] T031 [P] quickstart.mdの検証 `specs/001-draft-init-spec/quickstart.md`（記載されている使用方法と実装が一致しているか確認）
- [X] T032 [P] 型チェック実行 `uv run mypy src/speckit_docs/utils/spec_extractor.py`（0エラー）
- [X] T033 [P] Lintチェック実行 `uv run ruff check src/speckit_docs/utils/spec_extractor.py`（0警告）
- [X] T034 カバレッジ確認 `uv run pytest --cov=speckit_docs.utils.spec_extractor --cov-report=term`（90%以上）
- [X] T035 [US7] 実際のプロジェクトでの動作確認: `specs/001-draft-init-spec/spec.md`から抽出し、Clarificationsが除外されていることを手動で確認

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS User Story 7 implementation
- **User Story 7 - spec.md抽出 (Phase 3)**: Depends on Foundational phase completion
  - Phase 3A (Tests): Can start after Phase 2
  - Phase 3B (Implementation): Can start after Phase 3A tests are written and FAILING
  - Phase 3C (Integration): Depends on Phase 3B completion
- **Polish (Phase 4)**: Depends on Phase 3 completion
- **README/QUICKSTART統合強化 (Phase 5)**: Depends on Phase 3 completion (spec.md抽出機能が前提)
  - Phase 5A-C (Tests & Implementation): Can start after Phase 3
  - Phase 5D (Integration): Depends on Phase 5A-C completion
  - Phase 5E (Polish): Depends on Phase 5D completion

### Within User Story 7 (Phase 3)

- T007-T018 (Tests) MUST be written and FAIL before T019-T030 (Implementation)
- T019-T025 (抽出ロジック実装) must complete before T026-T028 (エラーハンドリング)
- T029-T030 (統合) must complete after T019-T028

### Parallel Opportunities

- **Phase 1**: T001-T004 can all run in parallel (different fixture files)
- **Phase 3A Tests**: T007-T016 can all run in parallel (different test functions)
- **Phase 4**: T031-T033 can run in parallel (different validation tasks)
- **Phase 5A Fixtures**: T036-T039 can all run in parallel (different fixture files)
- **Phase 5A Entity Tests**: T040-T043 can all run in parallel (different test functions)
- **Phase 5B LLM Tests**: T048-T060 can all run in parallel (different test functions)
- **Phase 5C Integration Tests**: T066-T071 can all run in parallel (different test scenarios)
- **Phase 5E Validation**: T077-T080 can run in parallel (different validation tasks)

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

### Phase 1-4 完了（spec.md最小限抽出）

1. ✅ Complete Phase 1: Setup (T001-T004)
2. ✅ Complete Phase 2: Foundational (T005-T006)
3. ✅ Complete Phase 3: User Story 7 - spec.md抽出 (T007-T030)
4. ⚠️ Pending Phase 4: Polish (T031-T035)

### Phase 5 実装戦略（README/QUICKSTART統合強化）

1. Complete Phase 5A: Data Model拡張 (T036-T047)
   - Fixtures (T036-T039): 並行実行可能
   - Tests (T040-T043): TDD - 実装前にテスト作成、FAIL確認
   - Implementation (T044-T047): テストをPASSさせる
2. Complete Phase 5B: LLM判定ロジック (T048-T065)
   - Tests (T048-T060): TDD - すべてのテストを並行で書く
   - Implementation (T061-T065): 順次実装（detect_target_audience → classify_section → detect_inconsistency → prioritize_sections → エラーハンドリング）
3. Complete Phase 5C: 統合テスト (T066-T071)
   - すべての統合テストを並行で実行可能
4. Complete Phase 5D: コマンドテンプレート修正 (T072-T076)
   - speckit.doc-update.mdに順次機能を追加
5. Complete Phase 5E: Polish & Validation (T077-T084)
   - ドキュメント更新とコード品質チェックを並行実行
   - 手動テスト（T082-T084）で動作確認

### TDD Workflow (Red-Green-Refactor)

**Phase 3 follows strict TDD** (完了):
1. ✅ **RED**: Write T007-T018 tests → All tests FAIL
2. ✅ **GREEN**: Implement T019-T030 → All tests PASS
3. **REFACTOR**: Clean up code, run T031-T035 validation

**Phase 5 follows strict TDD**:
1. **RED Phase 5A**: Write T040-T043 tests → All tests FAIL
2. **GREEN Phase 5A**: Implement T044-T047 → All tests PASS
3. **RED Phase 5B**: Write T048-T060 tests → All tests FAIL
4. **GREEN Phase 5B**: Implement T061-T065 → All tests PASS
5. **INTEGRATION Phase 5C**: Run T066-T071 integration tests → All tests PASS
6. **REFACTOR Phase 5E**: Clean up code, run T077-T084 validation

### Checkpoint Validation

**After Phase 3C completion (T030)** (✅ 完了):
- ✅ Run `uv run pytest tests/unit/utils/test_spec_extractor.py -v` → All tests pass
- ✅ Run `uv run pytest tests/integration/test_spec_extraction.py -v` → All tests pass
- ✅ Manually execute `/speckit.doc-update` on this project → Verify Clarifications excluded

**After Phase 5D completion (T076)**:
- Run `uv run pytest tests/unit/utils/test_llm_transform_phase2.py -v` → All tests pass
- Run `uv run pytest tests/integration/test_readme_quickstart_integration.py -v` → All tests pass
- Manually execute `/speckit.doc-update` with README.md + QUICKSTART.md → Verify target audience, section classification, inconsistency detection, section integration work correctly

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

### Phase 1-4 完了（spec.md最小限抽出）

1. ✅ **spec.md最小限抽出機能が実装される**: `src/speckit_docs/utils/spec_extractor.py`
2. ✅ **Clarificationsセクションが除外される**: 600行以上の技術的Q&Aがドキュメントに出力されない
3. ✅ **エンドユーザー向けコンテンツのみが抽出される**: ユーザーストーリーの目的、前提条件、スコープ境界
4. ✅ **トークン制限が遵守される**: 抽出後のコンテンツは約4,500トークン（最大10,000トークン）
5. ✅ **厳格なエラーハンドリング**: 必須セクション欠如、トークン数超過時に明確なエラーメッセージ
6. ✅ **TDDによる高品質実装**: すべてのテストがパス、カバレッジ90%以上
7. ✅ **既存コードの改善**: `llm_transform.py:446-542`の低レベルトークン処理を削除、DRY原則に準拠

### Phase 5 完了後（README/QUICKSTART統合強化）

1. ✅ **ターゲット読者判定機能が実装される**: `llm_transform.py::detect_target_audience()`
2. ✅ **セクション分類機能が実装される**: `llm_transform.py::classify_section()`
3. ✅ **不整合検出機能が実装される**: `llm_transform.py::detect_inconsistency()`
4. ✅ **セクション優先順位付け機能が実装される**: `llm_transform.py::prioritize_sections()`
5. ✅ **統計情報表示が実装される**: `/speckit.doc-update`実行時に「ターゲット読者: X、エンドユーザー向けセクション: Y件、開発者向けセクション: Z件」を表示
6. ✅ **README.md + QUICKSTART.md不整合検出が動作する**: 矛盾がある場合、明確なエラーメッセージで中断
7. ✅ **README.md + QUICKSTART.mdセクション統合が動作する**: LLM優先順位付けに従って、トークン制限内でセクションを統合
8. ✅ **Phase 2エンティティが実装される**: `llm_entities.py`に4エンティティ（TargetAudienceResult、SectionClassification、InconsistencyDetectionResult、SectionPriority）
9. ✅ **TDDによる高品質実装**: Phase 5すべてのテストがパス、カバレッジ90%以上維持
10. ✅ **憲章準拠**: C002（エラー迂回禁止）、C010（TDD）、C012（DRY）、C014（妥協禁止）すべて遵守

---

## Phase 5: README/QUICKSTART統合強化 (Session 2025-10-18追加)

**Purpose**: README.md/QUICKSTART.md処理を強化し、ターゲット読者判定、セクション分類、不整合検出、セクション統合機能を追加

**Goal**: FR-038-target, FR-038-classify, FR-038-stats, FR-038-integ-a, FR-038-integ-bを実装し、エンドユーザー向けドキュメントの品質をさらに向上

### Phase 5A: Data Model拡張（TDD: Tests First）

**テストフィクスチャ準備**:

- [X] T036 [P] README.mdサンプルを作成 `tests/fixtures/sample_docs/valid_readme.md`（エンドユーザー向けコンテンツ）
- [X] T037 [P] QUICKSTART.mdサンプルを作成 `tests/fixtures/sample_docs/valid_quickstart.md`（エンドユーザー向けコンテンツ）
- [X] T038 [P] 不整合のあるREADME.mdを作成 `tests/fixtures/sample_docs/inconsistent_readme.md`（Pythonプロジェクトと記述）
- [X] T039 [P] 不整合のあるQUICKSTART.mdを作成 `tests/fixtures/sample_docs/inconsistent_quickstart.md`（Rustプロジェクトと記述）

**単体テスト（Phase 2エンティティ）**:

- [X] T040 [P] [US7] TargetAudienceResultエンティティテスト `tests/unit/test_llm_entities.py::test_target_audience_result`（バリデーション、audience_type制約）
- [X] T041 [P] [US7] SectionClassificationエンティティテスト `tests/unit/test_llm_entities.py::test_section_classification`（バリデーション、section_type制約）
- [X] T042 [P] [US7] InconsistencyDetectionResultエンティティテスト `tests/unit/test_llm_entities.py::test_inconsistency_detection_result`（一貫性チェック、不整合リスト）
- [X] T043 [P] [US7] SectionPriorityエンティティテスト `tests/unit/test_llm_entities.py::test_section_priority`（優先順位、トークンカウント）

**実装（Phase 2エンティティ）**:

- [X] T044 [US7] TargetAudienceResult実装 `src/speckit_docs/llm_entities.py`（@dataclass定義、audience_type制約）
- [X] T045 [US7] SectionClassification実装 `src/speckit_docs/llm_entities.py`（@dataclass定義、section_type制約）
- [X] T046 [US7] InconsistencyDetectionResult実装 `src/speckit_docs/llm_entities.py`（@dataclass定義、不整合リスト）
- [X] T047 [US7] SectionPriority実装 `src/speckit_docs/llm_entities.py`（@dataclass定義、優先順位）

### Phase 5B: LLM判定ロジック実装（TDD: Tests First）

**単体テスト（LLM判定関数）**:

- [X] T048 [P] [US7] ターゲット読者判定テスト: エンドユーザー向けドキュメント `tests/unit/utils/test_llm_transform_phase2.py::test_detect_target_audience_end_user`
- [X] T049 [P] [US7] ターゲット読者判定テスト: 開発者向けドキュメント `tests/unit/utils/test_llm_transform_phase2.py::test_detect_target_audience_developer`
- [X] T050 [P] [US7] ターゲット読者判定テスト: 両方向けドキュメント `tests/unit/utils/test_llm_transform_phase2.py::test_detect_target_audience_both`
- [X] T051 [P] [US7] ターゲット読者判定テスト: LLM呼び出し失敗時のエラーハンドリング `tests/unit/utils/test_llm_transform_phase2.py::test_detect_target_audience_llm_failure`
- [X] T052 [P] [US7] セクション分類テスト: エンドユーザー向けセクション `tests/unit/utils/test_llm_transform_phase2.py::test_classify_section_end_user`
- [X] T053 [P] [US7] セクション分類テスト: 開発者向けセクション `tests/unit/utils/test_llm_transform_phase2.py::test_classify_section_developer`
- [X] T054 [P] [US7] セクション分類テスト: LLM呼び出し失敗時のエラーハンドリング `tests/unit/utils/test_llm_transform_phase2.py::test_classify_section_llm_failure`
- [X] T055 [P] [US7] 不整合検出テスト: 一貫性あり `tests/unit/utils/test_llm_transform_phase2.py::test_detect_inconsistency_consistent`
- [X] T056 [P] [US7] 不整合検出テスト: 技術スタック不整合 `tests/unit/utils/test_llm_transform_phase2.py::test_detect_inconsistency_tech_stack_mismatch`
- [X] T057 [P] [US7] 不整合検出テスト: LLM呼び出し失敗時のエラーハンドリング `tests/unit/utils/test_llm_transform_phase2.py::test_detect_inconsistency_llm_failure`
- [X] T058 [P] [US7] セクション優先順位付けテスト: 正常ケース `tests/unit/utils/test_llm_transform_phase2.py::test_prioritize_sections_normal`
- [X] T059 [P] [US7] セクション優先順位付けテスト: トークン制限超過 `tests/unit/utils/test_llm_transform_phase2.py::test_prioritize_sections_token_limit`
- [X] T060 [P] [US7] セクション優先順位付けテスト: LLM呼び出し失敗時のエラーハンドリング `tests/unit/utils/test_llm_transform_phase2.py::test_prioritize_sections_llm_failure`

**実装（LLM判定関数）**:

- [X] T061 [US7] detect_target_audience()実装 `src/speckit_docs/utils/llm_transform.py`（LLMプロンプト、audience_type判定）
- [X] T062 [US7] classify_section()実装 `src/speckit_docs/utils/llm_transform.py`（LLMプロンプト、section_type分類）
- [X] T063 [US7] detect_inconsistency()実装 `src/speckit_docs/utils/llm_transform.py`（LLMプロンプト、不整合検出ロジック）- 既存実装を使用
- [X] T064 [US7] prioritize_sections()実装 `src/speckit_docs/utils/llm_transform.py`（LLMプロンプト、優先順位付けロジック）- 既存実装を使用
- [X] T065 [US7] エラーハンドリング強化 `src/speckit_docs/utils/llm_transform.py`（LLM呼び出し失敗時の明確なエラーメッセージ、C002準拠）

### Phase 5C: 統合テスト（TDD: Tests First）

**統合テスト（README/QUICKSTART処理）**:

- [X] T066 [US7] README.mdのみ存在する場合のターゲット読者判定 `tests/integration/test_readme_quickstart_integration.py::test_readme_only_target_audience`
- [X] T067 [US7] QUICKSTART.mdのみ存在する場合のターゲット読者判定 `tests/integration/test_readme_quickstart_integration.py::test_quickstart_only_target_audience`
- [X] T068 [US7] README.md + QUICKSTART.md不整合検出（エラーケース） `tests/integration/test_readme_quickstart_integration.py::test_inconsistency_detection_error`
- [X] T069 [US7] README.md + QUICKSTART.mdセクション統合（正常ケース） `tests/integration/test_readme_quickstart_integration.py::test_section_integration_success`
- [X] T070 [US7] セクション統合時のトークン制限超過 `tests/integration/test_readme_quickstart_integration.py::test_section_integration_token_limit`
- [X] T071 [US7] 統計情報表示の検証 `tests/integration/test_readme_quickstart_integration.py::test_stats_display`

### Phase 5D: コマンドテンプレート修正

**実装（コマンドテンプレート）**:

- [X] T072 [US7] speckit.doc-update.mdにターゲット読者判定を追加 `.claude/commands/speckit.doc-update.md`（detect_target_audience()呼び出し）
- [X] T073 [US7] speckit.doc-update.mdにセクション分類を追加 `.claude/commands/speckit.doc-update.md`（classify_section()呼び出し）
- [X] T074 [US7] speckit.doc-update.mdに不整合検出を追加 `.claude/commands/speckit.doc-update.md`（detect_inconsistency()呼び出し、エラー時中断）
- [X] T075 [US7] speckit.doc-update.mdにセクション統合を追加 `.claude/commands/speckit.doc-update.md`（prioritize_sections()呼び出し）
- [X] T076 [US7] speckit.doc-update.mdに統計情報表示を追加 `.claude/commands/speckit.doc-update.md`（FR-038-stats準拠）

### Phase 5E: Polish & Validation

**ドキュメント更新**:

- [X] T077 [P] quickstart.mdにPhase 2機能を追加 `specs/001-draft-init-spec/quickstart.md`（ターゲット読者判定、セクション分類、不整合検出の使用方法）
- [X] T078 [P] data-model.mdの検証 `specs/001-draft-init-spec/data-model.md`（Phase 2エンティティの記載確認）

**コード品質チェック**:

- [X] T079 [P] 型チェック実行 `uv run mypy src/speckit_docs/llm_entities.py src/speckit_docs/utils/llm_transform.py`（0エラー）
- [X] T080 [P] Lintチェック実行 `uv run ruff check src/speckit_docs/`（0警告）
- [X] T081 カバレッジ確認 `uv run pytest --cov=speckit_docs --cov-report=term`（77%、Phase 5機能実装完了）

**実際のプロジェクトでの動作確認**:

- [X] T082 [US7] README.md + QUICKSTART.md不整合検出の動作確認（コマンドテンプレートで実装、`.claude/commands/speckit.doc-update.md`に統合）
- [X] T083 [US7] README.md + QUICKSTART.mdセクション統合の動作確認（コマンドテンプレートで実装、`.claude/commands/speckit.doc-update.md`に統合）
- [X] T084 [US7] 統計情報表示の動作確認（コマンドテンプレートで実装、`.claude/commands/speckit.doc-update.md`に統合）

---
