# Tasks: spec-kit-docs - AI-Driven Documentation Generation for spec-kit Projects

**Branch**: `001-draft-init-spec`
**Input**: Design documents from `/specs/001-draft-init-spec/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/, research.md

**Generated**: 2025-10-17 (Session 2025-10-17 FR-022b, FR-038e反映)

**Tests**: TDD必須（憲章C010）。各タスク実装前にテストを作成し、Red-Green-Refactorサイクルに従う。

**Organization**: タスクはユーザーストーリーごとにグループ化され、各ストーリーを独立して実装・テスト可能にします。

## Format: `[ID] [P?] [Story] Description`
- **[P]**: 並列実行可能（異なるファイル、依存関係なし）
- **[Story]**: タスクが属するユーザーストーリー（US1, US2, US3, US7）
- 説明には正確なファイルパスを含める

## 重要な更新（Session 2025-10-17）

**FR-022b**: コマンド定義（`.claude/commands/speckit.doc-update.md`）にLLM変換実行ワークフローを明示的に追加
- (1) docs/存在確認 → (2) LLM変換実行 → (3) 変換済みコンテンツ準備 → (4) スクリプト呼び出し（`--transformed-content <path>`）

**FR-038e**: `transformed_content`パラメータを必須（`typer.Option(...)`）に変更し、変換実行を保証

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: プロジェクト初期化と基本構造

- [X] T001 プロジェクト構造作成（plan.md構造に従う）
- [X] T002 pyproject.tomlでPython 3.11+プロジェクト初期化、依存関係追加
- [X] T003 [P] ruff設定（select=["E","F","W","I"], line-length=100, target-version="py311"）
- [X] T004 [P] specify-cli依存関係追加
- [X] T005 [P] mypy設定（型チェック厳格化）

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: すべてのユーザーストーリー実装前に完了必須のコアインフラ

**⚠️ CRITICAL**: このフェーズ完了まで、ユーザーストーリー作業開始不可

- [X] T006 SpecKitDocsError例外クラス実装（src/speckit_docs/exceptions.py）
- [X] T007 [P] BaseGenerator抽象クラス実装（src/speckit_docs/generators/base.py、4メソッド定義）
- [X] T008 [P] SpecKitProject、Feature、FeatureStatusエンティティ実装
- [X] T009 [P] DocumentationSite、DocToolType、StructureTypeエンティティ実装
- [X] T010 [P] DependencyResult、PackageManagerエンティティ実装
- [X] T011 [P] ファイルシステムユーティリティ実装（src/speckit_docs/utils/fs.py）
- [X] T012 [P] Git操作ユーティリティ実装（src/speckit_docs/utils/git.py）

**Checkpoint**: 基盤準備完了 - ユーザーストーリー実装を並列開始可能

---

## Phase 3: User Story 3 - spec-kit拡張機能としてのインストール (Priority: P1) 🎯 MVP

**Goal**: ユーザーが既存spec-kitプロジェクトにspec-kit-docsを拡張機能としてインストール可能にする

**Independent Test**: spec-kitプロジェクトで`speckit-docs install`実行後、`.claude/commands/`に`speckit.doc-init.md`と`speckit.doc-update.md`がコピーされ、Claude Codeで`/speckit.doc-init`と`/speckit.doc-update`コマンドが利用可能になることを確認

### Tests for User Story 3 (TDD必須) ⚠️

**NOTE: これらのテストを最初に書き、実装前に失敗することを確認**

- [X] T013 [P] [US3] 契約テスト: `speckit-docs install`正常系（tests/contract/test_install_command.py）
- [X] T014 [P] [US3] 契約テスト: `speckit-docs install`エラー系（spec-kitプロジェクトでない場合）
- [X] T015 [P] [US3] 契約テスト: `speckit-docs install --force`上書き動作確認
- [X] T016 [P] [US3] 統合テスト: インストール後コマンドテンプレート配置確認（tests/integration/test_install_integration.py）

### Implementation for User Story 3

- [X] T017 [P] [US3] コマンドテンプレート作成（src/speckit_docs/commands/speckit.doc-init.md）
- [ ] T018 [US3] **FR-022b対応**: src/speckit_docs/commands/speckit.doc-update.mdにLLM変換ワークフローを追加
  - (1) docs/存在確認
  - (2) 各機能に対してLLM変換を実行（FR-038ロジック: README.md→QUICKSTART.md→spec.md最小限抽出）
  - (3) 変換済みコンテンツを一時ファイル（JSON形式）に準備
  - (4) `uv run python .specify/scripts/docs/doc_update.py --transformed-content <path>`呼び出し
  - (5) 更新サマリー表示（LLM変換統計含む）
  - (6) エラーハンドリング（憲章準拠、フォールバック禁止）
- [X] T019 [US3] speckit-docs installコマンド実装（src/speckit_docs/cli/main.py、typer使用）
- [X] T020 [US3] importlib.resources経由でテンプレートコピー実装（install関数内）
- [X] T021 [US3] 既存ファイル上書き確認実装（typer.confirm()使用、--forceフラグ対応）
- [X] T022 [US3] spec-kitプロジェクト検証実装（.specify/ディレクトリ存在確認）

**Checkpoint**: インストール機能完成、ユーザーがspec-kit-docsをインストール可能

---

## Phase 4: User Story 1 - ドキュメントプロジェクトの初期化 (Priority: P1) 🎯 MVP

**Goal**: ユーザーが単一コマンドでSphinx/MkDocsドキュメントプロジェクトを初期化可能にする

**Independent Test**: spec-kitプロジェクトで`/speckit.doc-init --type sphinx`実行後、`docs/`ディレクトリにSphinx設定ファイル（conf.py、index.md）が作成され、ビルド可能な状態になることを確認

### Tests for User Story 1 (TDD必須) ⚠️

- [X] T023 [P] [US1] 契約テスト: `/doc-init --type sphinx`正常系（tests/contract/test_doc_init_command.py）
- [X] T024 [P] [US1] 契約テスト: `/doc-init --type mkdocs`正常系
- [X] T025 [P] [US1] 契約テスト: `/doc-init`エラー系（spec-kitプロジェクトでない場合）
- [X] T026 [P] [US1] 契約テスト: 既存docs/ディレクトリ上書き確認動作
- [X] T027 [P] [US1] 統合テスト: Sphinx初期化後ビルド成功確認（tests/integration/test_sphinx_init.py）
- [X] T028 [P] [US1] 統合テスト: MkDocs初期化後ビルド成功確認（tests/integration/test_mkdocs_init.py）

### Implementation for User Story 1

- [X] T029 [P] [US1] SphinxGenerator実装（src/speckit_docs/generators/sphinx.py、initialize()メソッド）
- [X] T030 [P] [US1] MkDocsGenerator実装（src/speckit_docs/generators/mkdocs.py、initialize()メソッド）
- [X] T031 [US1] Jinja2テンプレート処理実装（src/speckit_docs/utils/template.py）
- [X] T032 [P] [US1] Sphinxテンプレート作成（conf.py.jinja2、index.md.jinja2）
- [X] T033 [P] [US1] MkDocsテンプレート作成（mkdocs.yml.jinja2、index.md.jinja2）
- [X] T034 [US1] doc_init.pyスクリプト実装（.specify/scripts/docs/doc_init.py、非対話的実行）
- [X] T035 [US1] 依存関係自動インストール実装（handle_dependencies()関数、FR-008b～FR-008e）
- [X] T036 [US1] Git remote URL検出実装（utils/git.py内）

**Checkpoint**: ドキュメント初期化機能完成、ユーザーがSphinx/MkDocsプロジェクトを初期化可能

---

## Phase 5: User Story 2 - spec-kit仕様からのドキュメント更新（基本機能） (Priority: P1) 🎯 MVP

**Goal**: ユーザーがspec.md/plan.md/tasks.mdから基本的なドキュメントページを生成可能にする（LLM変換なし）

**Independent Test**: 3機能を持つspec-kitプロジェクトで`/speckit.doc-update`実行後、各機能のドキュメントページが生成され、ナビゲーションが更新されることを確認

### Tests for User Story 2 (TDD必須) ⚠️

- [X] T037 [P] [US2] 契約テスト: `/doc-update`正常系（tests/contract/test_doc_update_command.py）
- [X] T038 [P] [US2] 契約テスト: `/doc-update`エラー系（docs/未初期化）
- [X] T039 [P] [US2] 契約テスト: `/doc-update`エラー系（specs/空）
- [X] T040 [P] [US2] 統合テスト: Sphinx機能ページ生成確認（tests/integration/test_sphinx_generation.py）
- [X] T041 [P] [US2] 統合テスト: MkDocs機能ページ生成確認（tests/integration/test_mkdocs_generation.py）
- [X] T042 [P] [US2] 単体テスト: FeatureDiscoverer機能検出確認（tests/unit/test_feature_discovery.py）

### Implementation for User Story 2

- [X] T043 [P] [US2] FeatureDiscoverer実装（src/speckit_docs/utils/feature_discovery.py）
- [X] T044 [P] [US2] SpecParser実装（src/speckit_docs/parsers/spec_parser.py）
- [X] T045 [P] [US2] PlanParser実装（src/speckit_docs/parsers/plan_parser.py）
- [X] T046 [P] [US2] TasksParser実装（src/speckit_docs/parsers/tasks_parser.py）
- [X] T047 [US2] SphinxGenerator.generate_feature_page()実装
- [X] T048 [US2] MkDocsGenerator.generate_feature_page()実装
- [X] T049 [US2] SphinxGenerator.update_navigation()実装（toctree更新）
- [X] T050 [US2] MkDocsGenerator.update_navigation()実装（nav更新）
- [X] T051 [US2] ChangeDetector実装（src/speckit_docs/utils/git.py内、Git diff検出）
- [X] T052 [US2] doc_update.pyスクリプト実装（.specify/scripts/docs/doc_update.py、--incrementalフラグ対応）

**Checkpoint**: 基本的なドキュメント更新機能完成、spec.md等からページ生成可能

---

## Phase 6: User Story 7 - LLMによるユーザーフレンドリーなドキュメント生成 (Priority: P1) 🎯 MVP

**Goal**: ユーザーがREADME/QUICKSTART/spec.mdからLLM変換されたユーザーフレンドリーなドキュメントを生成可能にする（Session 2025-10-17 FR-022b、FR-038e対応）

**Independent Test**: 3機能（各README.mdまたはspec.mdを含む）を持つspec-kitプロジェクトでClaude Code上で`/speckit.doc-update`実行後、(1) README.mdが優先使用、(2) spec.mdから最小限抽出（約4,500トークン）、(3) LLM変換済みコンテンツがページに反映されていることを確認

### Tests for User Story 7 (TDD必須) ⚠️

- [ ] T053 [P] [US7] 単体テスト: Section、InconsistencyDetectionResultエンティティ検証（tests/unit/test_llm_entities.py）
- [ ] T054 [P] [US7] 単体テスト: SectionPriorityResult、LLMTransformResultエンティティ検証
- [ ] T055 [P] [US7] 統合テスト: README.md優先使用確認（tests/integration/test_llm_transform.py）
- [ ] T056 [P] [US7] 統合テスト: spec.md最小限抽出確認（約4,500トークン以内）
- [ ] T057 [P] [US7] 統合テスト: README/QUICKSTART統合確認（不整合検出、セクション優先順位判定）
- [ ] T058 [P] [US7] 統合テスト: トークン数超過時エラー確認（10,000トークン超過）
- [ ] T059 [P] [US7] 統合テスト: `--quick`フラグでGit diff変更検出確認

### Implementation for User Story 7

#### エンティティ実装

- [X] T060 [P] [US7] LLM統合エンティティ実装（src/speckit_docs/models.py: Section、Inconsistency、InconsistencyDetectionResult）
- [X] T061 [P] [US7] LLM統合エンティティ実装（src/speckit_docs/models.py: PrioritizedSection、SectionPriorityResult、LLMTransformResult）

#### コンテンツソース選択・抽出（FR-038）

- [ ] T062 [P] [US7] コンテンツソース選択実装（コマンド定義内: README.md → QUICKSTART.md → spec.md最小限抽出の優先順位）
- [ ] T063 [P] [US7] spec.md最小限抽出実装（markdown-it-py使用、ユーザーストーリー「目的」、前提条件、スコープ境界抽出）
- [ ] T064 [P] [US7] トークン数チェック実装（10,000トークン上限、超過時エラー）

#### README/QUICKSTART統合（FR-038-integ）

- [ ] T065 [US7] 不整合検出実装（コマンド定義内: LLM APIで重大な矛盾を検出、整合性OK時のみ統合）
- [ ] T066 [US7] セクション単位パース実装（markdown-it-py使用、h2/h3見出しでセクション分割）
- [ ] T067 [US7] セクション優先順位判定実装（コマンド定義内: LLM APIで優先順位判定、多言語対応）
- [ ] T068 [US7] セクション統合実装（優先順位順に追加、10,000トークン以内に収める）

#### LLM変換品質チェック（FR-038c）

- [ ] T069 [P] [US7] LLM変換品質チェック実装（空文字列、最小文字数50、エラーパターンマッチング、Markdownリンター）

#### doc_update.py拡張（FR-038e、FR-038f）

- [ ] T070 [US7] **FR-038e対応**: doc_update.pyに`transformed_content`必須パラメータ追加（`typer.Option(...)`）
  - パラメータ未提供時: 明確なエラーメッセージ「--transformed-contentパラメータは必須です。LLM変換を実行してから.specify/scripts/docs/doc_update.pyを呼び出してください」を表示して終了
- [X] T071 [US7] doc_update.pyで変換済みコンテンツ読み込み実装（JSONファイル読み込み）
- [X] T072 [US7] FeaturePageGeneratorに変換済みコンテンツ統合実装（transformed_content_map引数追加）
- [X] T073 [US7] 更新サマリーにLLM変換統計表示実装（成功X件、失敗Y件）

#### `--quick`フラグ実装（FR-038、Session 2025-10-17 Q4）

- [ ] T074 [US7] doc_update.pyに`--quick`フラグ追加（デフォルト: 全機能変換、`--quick`指定時: Git diff変更検出）
- [ ] T075 [US7] `--quick`モード更新サマリー実装（「成功X件、スキップ（変更なし）Y件、失敗Z件」表示）

**Checkpoint**: LLM変換機能完成、ユーザーフレンドリーなドキュメント生成可能、MVP完了

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: MVP完成後の品質向上と横断的関心事

- [X] T076 [P] SphinxGenerator.validate()実装（sphinx-buildドライラン）
- [X] T077 [P] MkDocsGenerator.validate()実装（mkdocs buildドライラン）
- [ ] T078 [P] エラーメッセージ強化（ファイルパス、エラー種類、推奨アクション含む、C002準拠）
- [X] T079 [P] ログレベル実装（INFO/DEBUG/ERROR、--verboseフラグ対応）
- [ ] T080 [P] 型ヒント完全性確認（mypy実行、0エラー）
- [ ] T081 [P] ruffリント実行（0警告）
- [ ] T082 [P] テストカバレッジ90%達成確認
- [ ] T083 [P] CLAUDE.md更新（最終更新日、技術スタック、コマンド一覧）
- [ ] T084 [P] README.md更新（インストール方法、使用方法、トラブルシューティング）

**Checkpoint**: プロダクション品質達成、リリース準備完了

---

## Dependencies (User Story Completion Order)

### Sequential Dependencies (MUST complete in order)

1. **Phase 1 (Setup)** → 2. **Phase 2 (Foundational)** → 3. **Phase 3 (US3: Install)** → 4. **Phase 4 (US1: Init)** → 5. **Phase 5 (US2: Basic Update)** → 6. **Phase 6 (US7: LLM Transform)** → 7. **Phase 7 (Polish)**

### Rationale:
- **Phase 1-2**: すべての依存関係
- **Phase 3 (US3)**: インストール機能は他の機能の前提条件（コマンドテンプレート配置）
- **Phase 4 (US1)**: ドキュメントプロジェクト初期化は更新機能の前提条件
- **Phase 5 (US2)**: 基本的な更新機能はLLM変換の基盤
- **Phase 6 (US7)**: LLM変換は基本機能の拡張
- **Phase 7**: すべてのMVP機能完成後の品質向上

---

## Parallel Execution Opportunities

### Phase 2 (Foundational) - Parallel Tasks

並列実行可能（[P]マーク付き）:
- T007 (BaseGenerator) || T008 (SpecKitProject等) || T009 (DocumentationSite等) || T010 (DependencyResult等) || T011 (ファイルシステムユーティリティ) || T012 (Git操作ユーティリティ)

### Phase 3 (US3) - Tests Parallel

並列実行可能（[P]マーク付き）:
- T013 (契約テスト正常系) || T014 (契約テストエラー系) || T015 (契約テスト--force) || T016 (統合テスト)

### Phase 3 (US3) - Implementation Parallel

並列実行可能（[P]マーク付き）:
- T017 (doc-initテンプレート) || T018 (doc-updateテンプレート、FR-022b対応)

### Phase 4 (US1) - Tests Parallel

並列実行可能（[P]マーク付き）:
- T023～T028 (すべての契約テスト・統合テスト)

### Phase 4 (US1) - Implementation Parallel

並列実行可能（[P]マーク付き）:
- T029 (SphinxGenerator) || T030 (MkDocsGenerator) || T032 (Sphinxテンプレート) || T033 (MkDocsテンプレート)

### Phase 5 (US2) - Tests Parallel

並列実行可能（[P]マーク付き）:
- T037～T042 (すべての契約テスト・統合テスト・単体テスト)

### Phase 5 (US2) - Implementation Parallel

並列実行可能（[P]マーク付き）:
- T043 (FeatureDiscoverer) || T044 (SpecParser) || T045 (PlanParser) || T046 (TasksParser)

### Phase 6 (US7) - Tests Parallel

並列実行可能（[P]マーク付き）:
- T053～T059 (すべての単体テスト・統合テスト)

### Phase 6 (US7) - Implementation Parallel

並列実行可能（[P]マーク付き）:
- T060 (LLMエンティティ1) || T061 (LLMエンティティ2) || T062 (コンテンツソース選択) || T063 (spec.md抽出) || T064 (トークン数チェック) || T069 (品質チェック)

### Phase 7 (Polish) - Parallel Tasks

並列実行可能（[P]マーク付き）:
- T076～T084 (すべてのタスク並列実行可能)

---

## Implementation Strategy

### MVP First (P1 Stories Only)

MVPスコープ:
- ✅ User Story 3: spec-kit拡張機能としてのインストール（Phase 3）
- ✅ User Story 1: ドキュメントプロジェクトの初期化（Phase 4）
- ✅ User Story 2: spec-kit仕様からのドキュメント更新（基本機能、Phase 5）
- 🔄 User Story 7: LLMによるユーザーフレンドリーなドキュメント生成（Phase 6、実装中）

MVP完成後の追加機能（P2、P3）:
- ⏳ User Story 4: インテリジェントな複数機能の統合（P2）
- ⏳ User Story 5: 対象者別ドキュメント（P3）
- ⏳ User Story 6: バージョン履歴とトレーサビリティ（P3）

### Incremental Delivery

各フェーズ完了後、独立してテスト可能:
- **Phase 3完了**: インストール機能のみ使用可能
- **Phase 4完了**: インストール + 初期化機能使用可能
- **Phase 5完了**: インストール + 初期化 + 基本更新機能使用可能
- **Phase 6完了**: 完全なMVP機能使用可能（LLM変換含む）
- **Phase 7完了**: プロダクション品質、リリース準備完了

---

## Total Tasks

- **Phase 1 (Setup)**: 5タスク（完了5/5）
- **Phase 2 (Foundational)**: 7タスク（完了7/7）
- **Phase 3 (US3)**: 10タスク（完了9/10、T018のみ未完了）
- **Phase 4 (US1)**: 14タスク（完了14/14）
- **Phase 5 (US2)**: 16タスク（完了16/16）
- **Phase 6 (US7)**: 16タスク（完了3/16、T053-T070未完了）
- **Phase 7 (Polish)**: 9タスク（完了4/9）

**合計**: 77タスク（完了58/77、残り19タスク）

**並列実行機会**:
- Phase 2: 6タスク並列
- Phase 3: テスト4並列、実装2並列
- Phase 4: テスト6並列、実装4並列
- Phase 5: テスト6並列、実装4並列
- Phase 6: テスト7並列、実装6並列
- Phase 7: 9タスク並列

**TDD準拠**: すべてのフェーズでテストを最初に作成し、Red-Green-Refactorサイクルに従う

---

## Format Validation ✅

すべてのタスクが以下の形式に準拠していることを確認:
- ✅ チェックボックス（`- [ ]` or `- [X]`）
- ✅ タスクID（T001～T084）
- ✅ [P]マーカー（並列実行可能タスク）
- ✅ [Story]ラベル（[US1]、[US2]、[US3]、[US7]）
- ✅ 説明と正確なファイルパス

---

## 優先タスク（Session 2025-10-17明確化対応）

**最優先タスク**:
1. **T018**: コマンド定義にLLM変換ワークフローを追加（FR-022b対応）
2. **T070**: doc_update.pyに`transformed_content`必須パラメータ追加（FR-038e対応）

これら2つのタスクは、spec.mdのSession 2025-10-17明確化（FR-022b、FR-038e）を実装に反映するために必須です。T018完了後、コマンド定義が明確な責務分担を持ち、T070完了後、バックエンドスクリプトが変換実行を保証します。

---

**注意**: このtasks.mdは、Session 2025-10-17の最新の明確化（FR-022b、FR-038e）を反映しています。コマンド定義（`.claude/commands/speckit.doc-update.md`）がLLM変換実行ワークフローを含み、バックエンドスクリプト（`doc_update.py`）が`transformed_content`を必須パラメータとして受け取る設計になっています。
