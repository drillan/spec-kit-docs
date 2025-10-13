# Tasks: spec-kit-docs - AI駆動型ドキュメント生成システム

**Input**: 設計ドキュメント from `/specs/001-draft-init-spec/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/

**MVP範囲**: Phase 1-5（US1: /speckit.doc-init、US2: /speckit.doc-update、US3: speckit-docs install）
**優先度**: すべてP1（MVP必須）

## Format: `[ID] [P?] [Story] Description`
- **[P]**: 並列実行可能（異なるファイル、依存関係なし）
- **[Story]**: タスクが属するユーザーストーリー（US1, US2, US3）
- ファイルパスは絶対パス（`/home/driller/repo/spec-kit-docs/...`）

---

## Phase 1: Setup（プロジェクト初期化）

**目的**: プロジェクト構造とビルド環境の構築

- [X] T001 [P] pyproject.tomlの依存関係確認と追加パッケージのインストール（typer、jinja2、GitPython、ruamel.yaml、markdown-it-py、sphinx、myst-parser、mkdocs、mkdocs-material）
- [X] T002 [P] src/speckit_docs/__init__.pyにバージョン情報を追加（`__version__ = "0.1.0"`）
- [X] T003 [P] .ruff.tomlとmypy設定の確認（C006: 90%カバレッジ、mypy --strict）
- [X] T004 tests/conftest.pyにpytest共通フィクスチャを追加（pyfakefsセットアップ、spec-kitプロジェクトモック）
- [X] T005 src/speckit_docs/exceptions.pyの検証（SpecKitDocsError、ValidationError、BuildErrorが定義済みであることを確認）

**Checkpoint**: ビルド環境準備完了 - 全依存関係がインストールされ、テスト実行可能

---

## Phase 2: Foundational（全ユーザーストーリーのブロッキング前提条件）

**目的**: すべてのユーザーストーリーが依存する共通インフラの構築

**⚠️ CRITICAL**: このフェーズが完了するまで、どのユーザーストーリーも開始できません

- [X] T006 [P] src/speckit_docs/models.pyのFeatureモデル検証（id、name、directory_path、spec_file、plan_file、tasks_file、status、priorityフィールドが定義済みか確認）
- [X] T007 [P] src/speckit_docs/models.pyのDocumentモデル検証（file_path、type、content、sections、last_modified、git_statusフィールドが定義済みか確認）
- [X] T008 [P] src/speckit_docs/models.pyのSectionモデル検証（title、level、content、line_start、line_end、subsectionsフィールドが定義済みか確認）
- [X] T009 [P] src/speckit_docs/parsers/markdown_parser.pyの検証（MarkdownParserクラスが存在し、parse()、extract_headings()、extract_metadata()メソッドが定義済みか確認）
- [X] T010 [P] src/speckit_docs/parsers/feature_scanner.pyの検証（FeatureScannerクラスが存在し、scan_features()メソッドが定義済みか確認）
- [X] T011 [P] src/speckit_docs/utils/validation.pyの検証（validate_speckit_project()、validate_git_repo()が定義済みか確認）
- [X] T012 [P] src/speckit_docs/utils/git.pyの検証（ChangeDetectorクラスが存在し、get_changed_features()メソッドが定義済みか確認）
- [X] T013 tests/unit/test_models.pyの拡張（Feature、Document、Sectionモデルの基本的なインスタンス化テストが存在するか確認）
- [X] T014 tests/unit/parsers/test_markdown_parser.pyの拡張（基本的なMarkdown解析テストが存在するか確認）
- [X] T015 tests/unit/utils/test_git.pyの拡張（Git diff検出テストが存在するか確認）

**Checkpoint**: 基盤準備完了 - ユーザーストーリー実装を並列開始可能

---

## Phase 3: User Story 1 - /speckit.doc-init コマンド（優先度: P1）🎯 MVP

**目標**: spec-kitプロジェクトにSphinxまたはMkDocsドキュメント環境を初期化

**独立テスト**: ユーザーが`/speckit.doc-init --type sphinx`を実行し、`docs/conf.py`、`docs/index.md`、`docs/Makefile`が生成され、`make html`でビルド成功することを確認

### Tests for User Story 1（TDD: Red-Green-Refactor）

**NOTE: これらのテストを最初に実装し、FAILすることを確認してから実装開始**

- [X] T016 [P] [US1] tests/unit/test_models.pyにGeneratorConfigモデルのテスト追加（tool、project_name、author、version、language、theme、extensions、plugins、custom_settingsフィールドのインスタンス化テスト）
- [X] T017 [P] [US1] tests/unit/parsers/test_document_structure.pyの作成（DocumentStructureクラスのdetermine_structure()テスト: 5機能以下→FLAT、6機能以上→COMPREHENSIVE）
- [X] T018 [P] [US1] tests/unit/generators/test_base.pyの拡張（BaseGeneratorの抽象メソッド定義テスト）
- [X] T019 [P] [US1] tests/unit/generators/test_sphinx.pyの拡張（SphinxGenerator.init_project()テスト: conf.pyにmyst-parser設定が含まれるか確認）
- [X] T020 [P] [US1] tests/unit/generators/test_mkdocs.pyの拡張（MkDocsGenerator.init_project()テスト: mkdocs.ymlにMaterial theme設定が含まれるか確認）
- [X] T021 [P] [US1] tests/contract/test_doc_init_output.pyの拡張（生成されたconf.pyがPython構文として正しいか、必須フィールドが含まれるか確認）
- [X] T022 [US1] tests/integration/test_sphinx_workflow.pyの拡張（エンドツーエンド: doc-init → ファイル生成確認 → make htmlの成功確認）
- [X] T023 [US1] tests/integration/test_mkdocs_workflow.pyの拡張（エンドツーエンド: doc-init → ファイル生成確認 → mkdocs buildの成功確認）

### Implementation for User Story 1

- [X] T024 [P] [US1] src/speckit_docs/models.pyにGeneratorConfigデータクラスを追加（toolはGeneratorTool enum、to_sphinx_conf()とto_mkdocs_yaml()メソッド実装）
- [X] T025 [P] [US1] src/speckit_docs/parsers/document_structure.pyの検証と拡張（DocumentStructureクラスのdetermine_structure()メソッドが機能数に基づいてFLAT/COMPREHENSIVEを返すか確認）
- [X] T026 [US1] src/speckit_docs/generators/base.pyの検証と拡張（BaseGeneratorに抽象メソッドinit_project()、update_docs()、build_docs()、validate_project()が定義済みか確認）
- [X] T027 [US1] src/speckit_docs/generators/sphinx.pyの拡張（SphinxGenerator.init_project()の実装: Jinja2テンプレートを使用してconf.py、index.md、Makefile、make.batを生成、FR-005a準拠でmyst-parser設定を含める）
- [X] T028 [US1] src/speckit_docs/generators/mkdocs.pyの拡張（MkDocsGenerator.init_project()の実装: Jinja2テンプレートを使用してmkdocs.yml、index.mdを生成、Material theme設定を含める）
- [X] T029 [US1] src/speckit_docs/templates/sphinx/内のJinja2テンプレート検証（conf.py.j2、index.md.j2、Makefile.j2、make.bat.j2が存在し、contracts/file-formats.md仕様に準拠しているか確認）
- [X] T030 [US1] src/speckit_docs/templates/mkdocs/内のJinja2テンプレート検証（mkdocs.yml.j2、index.md.j2が存在し、contracts/file-formats.md仕様に準拠しているか確認）
- [X] T031 [US1] src/speckit_docs/doc_init.pyの拡張（対話的プロンプト収集、GeneratorConfig生成、Generator.init_project()呼び出しロジックの実装確認）
- [X] T032 [US1] .specify/scripts/docs/doc_init.pyの検証（typerベースのCLI: --type、--project-name、--author、--version、--language、--forceオプションが定義され、main()が非対話的に動作するか確認）
- [X] T033 [US1] src/speckit_docs/commands/doc-init.mdの検証（Claude Code用コマンド定義: 対話的質問→引数構築→doc_init.py呼び出し→結果フィードバックのプロンプトが記述されているか確認）
- [X] T034 [US1] src/speckit_docs/generators/sphinx.pyのエラーハンドリング追加（docs/既存時に--forceフラグなしの場合、明確なエラーメッセージを返す）
- [X] T035 [US1] src/speckit_docs/generators/mkdocs.pyのエラーハンドリング追加（同上）

**Checkpoint**: `/speckit.doc-init`コマンドが完全に機能し、SphinxまたはMkDocsプロジェクトを初期化できる。生成されたプロジェクトは`make html`または`mkdocs build`でビルド可能。

---

## Phase 4: User Story 2 - /speckit.doc-update コマンド（優先度: P1）🎯 MVP

**目標**: specs/ディレクトリからspec.md、plan.md、tasks.mdを解析してドキュメント生成

**独立テスト**: 3つの機能（001-user-auth、002-api-integration、003-notifications）を持つspec-kitプロジェクトで`/speckit.doc-update`を実行し、各機能のドキュメントが生成され、index.mdが更新されることを確認

### Tests for User Story 2（TDD: Red-Green-Refactor）

- [X] T036 [P] [US2] tests/unit/parsers/test_markdown_parser.pyの拡張（Document.parse()が見出し、リスト、テーブル、コードブロックを正しく抽出するテスト）
- [X] T037 [P] [US2] tests/unit/generators/test_feature_page.pyの拡張（FeaturePageGeneratorがspec.md、plan.md、tasks.mdから統合されたMarkdownページを生成するテスト）
- [X] T038 [P] [US2] tests/unit/generators/test_document.pyの拡張（DocumentGeneratorが機能ドキュメントを正しいパスに書き込むテスト: FR-013の命名規則に準拠）
- [X] T039 [P] [US2] tests/unit/generators/test_navigation.pyの拡張（NavigationUpdaterがindex.mdのtoctree（Sphinx）またはmkdocs.ymlのnav（MkDocs）を更新するテスト）
- [X] T040 [P] [US2] tests/unit/utils/test_git.pyの拡張（ChangeDetector.get_changed_features()がGit diffで変更されたFeatureのみを返すテスト）
- [X] T041 [US2] tests/integration/test_sphinx_workflow.pyの拡張（エンドツーエンド: doc-init → doc-update → 機能ページ生成確認 → index.md更新確認 → make htmlの成功確認）
- [X] T042 [US2] tests/integration/test_mkdocs_workflow.pyの拡張（エンドツーエンド: doc-init → doc-update → 機能ページ生成確認 → mkdocs.yml更新確認 → mkdocs buildの成功確認）
- [X] T043 [US2] tests/unit/scripts/test_incremental_update.pyの拡張（インクリメンタル更新テスト: 1機能のみ変更時、その機能のみ再生成されるか確認）

### Implementation for User Story 2

- [X] T044 [P] [US2] src/speckit_docs/parsers/document.pyの拡張（Document.parse()メソッドの実装: MarkdownParserを使用してセクションツリーを生成）
- [X] T045 [P] [US2] src/speckit_docs/parsers/markdown_parser.pyの拡張（extract_headings()、extract_code_blocks()、extract_metadata()の実装: markdown-it-pyを使用）
- [X] T046 [US2] src/speckit_docs/models.pyにSectionの変換メソッド追加（Section.to_sphinx_md()とSection.to_mkdocs_md(): MyST構文 ↔ MkDocs構文の変換）
- [X] T047 [US2] src/speckit_docs/generators/feature_page.pyの拡張（FeaturePageGeneratorクラスの実装: spec.md、plan.md、tasks.mdを統合してMarkdownページを生成、欠落ファイルには視覚的アドモニション追加）
- [X] T048 [US2] src/speckit_docs/generators/document.pyの拡張（DocumentGeneratorクラスの実装: feature-page.md.jinja2テンプレートを使用してMarkdownファイルを書き込む、FR-013の命名規則に準拠）
- [X] T049 [US2] src/speckit_docs/generators/navigation.pyの拡張（NavigationUpdaterクラスの実装: Sphinxのindex.mdにtoctree追加、MkDocsのmkdocs.ymlにnav追加、ruamel.yamlでコメント保持）
- [X] T050 [US2] src/speckit_docs/utils/git.pyの拡張（ChangeDetector.get_changed_features()の実装: GitPythonでgit diff --name-only HEAD~1 HEADを実行し、specs/配下の変更をフィルタリング）
- [X] T051 [US2] src/speckit_docs/generators/sphinx.pyのupdate_docs()メソッド実装（変更されたFeatureのみまたは全Featureを処理し、FeaturePageGenerator → DocumentGenerator → NavigationUpdaterを順次呼び出し）
- [X] T052 [US2] src/speckit_docs/generators/mkdocs.pyのupdate_docs()メソッド実装（同上）
- [X] T053 [US2] src/speckit_docs/doc_update.pyの拡張（ChangeDetector呼び出し、Generator.update_docs()呼び出し、更新サマリー表示ロジックの実装確認）
- [X] T054 [US2] .specify/scripts/docs/doc_update.pyの検証（typerベースのCLI: --full、--no-build、--aiオプションが定義され、main()が非対話的に動作するか確認）
- [X] T055 [US2] src/speckit_docs/commands/doc-update.mdの検証（Claude Code用コマンド定義: docs/存在確認→doc_update.py呼び出し→更新サマリー表示→エラーハンドリングのプロンプトが記述されているか確認）
- [X] T056 [US2] src/speckit_docs/generators/sphinx.pyのbuild_docs()メソッド実装（subprocess.run()で`make html`を実行し、BuildResultを返す）
- [X] T057 [US2] src/speckit_docs/generators/mkdocs.pyのbuild_docs()メソッド実装（subprocess.run()で`mkdocs build`を実行し、BuildResultを返す）
- [X] T058 [US2] src/speckit_docs/models.pyにBuildResultとValidationResultデータクラス追加（success、output_dir、warnings、errors、build_time、file_count等のフィールド）
- [X] T059 [US2] FR-019aとFR-019bの実装（DocumentStructureの自動移行: 機能数が6以上になった場合、フラット構造から包括的構造に自動移行、逆方向の移行は禁止）

**Checkpoint**: `/speckit.doc-update`コマンドが完全に機能し、specs/から機能ドキュメントを生成・更新できる。Git diffによるインクリメンタル更新が動作し、ビルドが成功する。

---

## Phase 5: User Story 3 - speckit-docs install コマンド（優先度: P1）🎯 MVP

**目標**: spec-kit拡張機能として.claude/commands/と.specify/scripts/にファイルをコピー

**独立テスト**: 既存のspec-kitプロジェクトで`speckit-docs install`を実行し、`.claude/commands/speckit.doc-init.md`、`.claude/commands/speckit.doc-update.md`、`.specify/scripts/docs/doc_init.py`、`.specify/scripts/docs/doc_update.py`が作成され、Claude Codeで`/speckit.doc-init`と`/speckit.doc-update`が認識されることを確認

### Tests for User Story 3（TDD: Red-Green-Refactor）

- [X] T060 [P] [US3] tests/unit/cli/test_install_handler.pyの拡張（install_handler.install()がカレントディレクトリに.claude/commands/と.specify/scripts/を作成するテスト）
- [X] T061 [P] [US3] tests/unit/cli/test_install_handler.pyに上書き確認テスト追加（既存ファイルがある場合、--forceフラグなしで確認プロンプトを表示するテスト）
- [X] T062 [P] [US3] tests/unit/cli/test_install_handler.pyにspec-kitプロジェクト検証テスト追加（.specify/と.claude/が存在しない場合、エラーを返すテスト）
- [X] T063 [P] [US3] tests/integration/test_install.pyの拡張（エンドツーエンド: speckit-docs install → ファイル作成確認 → /speckit.doc-initの実行確認）

### Implementation for User Story 3

- [X] T064 [P] [US3] src/speckit_docs/cli/install_handler.pyの拡張（install()関数の実装: importlib.resourcesでsrc/speckit_docs/commands/とsrc/speckit_docs/scripts/にアクセスし、.claude/commands/と.specify/scripts/docs/にコピー）
- [X] T065 [P] [US3] src/speckit_docs/cli/__init__.pyの拡張（typerアプリ定義: @app.command("install")でinstall_handler.install()を呼び出す）
- [X] T066 [US3] pyproject.tomlに[project.scripts]エントリ追加（`speckit-docs = "speckit_docs.cli:app"`）
- [X] T067 [US3] src/speckit_docs/cli/install_handler.pyに既存ファイル確認ロジック追加（.claude/commands/speckit.doc-*.mdまたは.specify/scripts/docs/が存在する場合、typer.confirm()で上書き確認、--forceフラグで確認スキップ）
- [X] T068 [US3] src/speckit_docs/cli/install_handler.pyにspec-kitプロジェクト検証追加（validate_speckit_project()を呼び出し、.specify/と.claude/の存在確認、エラー時は明確なメッセージを表示）
- [X] T069 [US3] src/speckit_docs/cli/install_handler.pyにベストエフォートエラーハンドリング追加（ファイルコピー中にエラーが発生してもそれまでのファイルは残す、FR-023c準拠）
- [X] T070 [US3] .claude/commands/speckit.doc-init.mdと.claude/commands/speckit.doc-update.mdの最終確認（Claude Codeが認識できる形式でコマンド定義が記述されているか確認）

**Checkpoint**: `speckit-docs install`コマンドが完全に機能し、既存のspec-kitプロジェクトに拡張機能をインストールできる。Claude Codeで`/speckit.doc-init`と`/speckit.doc-update`が認識され、実行可能。

---

## Phase 6: Polish & Integration（統合と品質向上）

**目的**: MVP機能の品質向上とドキュメント整備

- [ ] T071 [P] src/speckit_docs/exceptions.pyのエラーメッセージ改善（すべてのSpecKitDocsError例外にsuggestionフィールドを追加、research.md Decision 8準拠）
- [ ] T072 [P] src/speckit_docs/utils/validation.pyにValidationResultのformat_errors()メソッド追加（エラー + 提案のフォーマット）
- [ ] T073 [P] README.mdの更新（インストール手順、基本的な使用方法、トラブルシューティングを含める）
- [ ] T074 [P] CONTRIBUTING.mdの更新（開発環境セットアップ、TDDワークフロー、コーディング規約を含める）
- [ ] T075 [P] .github/workflows/ci.ymlの作成（pytest、mypy --strict、ruff、カバレッジ90%確認を含むCI/CDパイプライン）
- [ ] T076 パフォーマンステストの実施（tests/performance/test_update_performance.py: 10機能プロジェクトで45秒以内、1機能インクリメンタル更新で5秒以内を確認、SC-006とSC-008準拠）
- [ ] T077 全統合テストの実施（tests/integration/配下のすべてのテストを実行し、エンドツーエンドフローが動作することを確認）
- [ ] T078 quickstart.mdの検証実行（quickstart.mdの手順に従ってspec-kit-docsをインストール・実行し、10-15分以内に完了することを確認）
- [ ] T079 カバレッジレポート生成と確認（pytest-covで90%以上のカバレッジを達成していることを確認、C006準拠）
- [ ] T080 最終的なmypy --strict実行（型エラーがないことを確認、C006準拠）

**Checkpoint**: MVP完成 - すべてのユーザーストーリーが実装され、テストが通過し、ドキュメントが整備されている。

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 依存関係なし - すぐに開始可能
- **Foundational (Phase 2)**: SetupフェーズのT001-T005完了後に開始可能 - **すべてのユーザーストーリーをブロック**
- **User Stories (Phase 3-5)**: Foundationalフェーズ完了後に開始可能
  - US1（Phase 3）: T015完了後に開始可能
  - US2（Phase 4）: T015とT035完了後に開始可能（US1の一部機能に依存）
  - US3（Phase 5）: T015完了後に開始可能（US1とUS2に独立）
- **Polish (Phase 6)**: US1、US2、US3すべて完了後に開始可能

### User Story Dependencies

- **User Story 1 (P1 - US1)**: Foundationalフェーズ完了後すぐに開始可能 - 他のストーリーへの依存なし
- **User Story 2 (P1 - US2)**: FoundationalフェーズとUS1のT027-T028（Generator実装）完了後に開始可能 - US1のGeneratorインターフェースに依存
- **User Story 3 (P1 - US3)**: Foundationalフェーズ完了後すぐに開始可能 - 他のストーリーへの依存なし

### Within Each User Story

- **Tests FIRST**: TDDサイクルに従い、テストを最初に実装してFAILを確認してから実装開始
- **Models → Services → CLI**: データモデル → ビジネスロジック → CLIインターフェースの順
- **Template → Generator**: Jinja2テンプレート準備後、Generator実装
- **Story完了確認**: 次の優先度に移る前に、各ストーリーのCheckpointで独立テストを実施

### Parallel Opportunities

- **Phase 1（Setup）**: T001-T005はすべて[P]で並列実行可能
- **Phase 2（Foundational）**: T006-T015はすべて[P]で並列実行可能
- **US1 Tests**: T016-T023はすべて[P]で並列実行可能
- **US1 Implementation**: T024-T025、T029-T030は[P]で並列実行可能
- **US2 Tests**: T036-T043はほぼすべて[P]で並列実行可能（T041-T043は統合テストのため若干依存あり）
- **US2 Implementation**: T044-T045、T047-T048は[P]で並列実行可能
- **US3 Tests**: T060-T063はすべて[P]で並列実行可能
- **US3 Implementation**: T064-T065は[P]で並列実行可能
- **Phase 6（Polish）**: T071-T075は[P]で並列実行可能

---

## Implementation Strategy

### MVP First（User Story 1のみ）

1. Phase 1完了（Setup）
2. Phase 2完了（Foundational） - **CRITICAL GATE**
3. Phase 3完了（US1: /speckit.doc-init）
4. **STOP and VALIDATE**: US1のCheckpointで独立テスト - `/speckit.doc-init`でSphinxプロジェクトを初期化し、`make html`が成功することを確認
5. デモ/デプロイ可能

### Incremental Delivery（すべてのMVPストーリー）

1. Phase 1-2完了 → 基盤準備完了
2. Phase 3完了（US1） → 独立テスト → デモ（ドキュメントプロジェクト初期化が可能）
3. Phase 4完了（US2） → 独立テスト → デモ（仕様からドキュメント生成が可能）
4. Phase 5完了（US3） → 独立テスト → デモ（spec-kit拡張機能としてインストール可能）
5. Phase 6完了 → MVP完成 → プロダクションデプロイ

### Parallel Team Strategy

複数の開発者がいる場合:

1. チーム全員でPhase 1-2を完了
2. Foundational完了後:
   - Developer A: Phase 3（US1: /speckit.doc-init）
   - Developer B: Phase 5（US3: speckit-docs install） - US1と独立して実装可能
   - Developer C: Phase 2のテスト拡充、Phase 6の準備
3. US1完了後:
   - Developer A: Phase 4（US2: /speckit.doc-update） - US1のGeneratorインターフェースを使用
4. すべて完了後、Phase 6をチームで実施

---

## Notes

- **[P]タスク** = 異なるファイル、依存関係なし、並列実行可能
- **[Story]ラベル** = タスクが属するユーザーストーリーをトレーサビリティのため明示
- **各ユーザーストーリー** = 独立して完了・テスト可能
- **TDD必須**: テストを実装してFAILを確認してから実装開始（C010準拠）
- **各タスクまたは論理グループ後にコミット**
- **Checkpointで検証**: 各ストーリーのCheckpointで独立テストを実施し、次のフェーズに進む前に機能を確認
- **避けるべきこと**: 曖昧なタスク、同じファイルへの競合、ストーリー間の独立性を壊す依存関係

---

## Performance Targets（from plan.md）

- `/speckit.doc-init`: 30秒以内（対話的入力時間を除く、SC-001）
- `/speckit.doc-update`: 45秒以内（10機能プロジェクト、SC-006）
- インクリメンタル更新: 5秒以内（1機能のみ変更時、SC-008）

---

## Critical Requirements（from spec.md）

- **FR-005a**: conf.pyにmyst-parser設定を含める（T027で実装確認）
- **FR-013/FR-014**: 機能ファイル命名規則（001-user-auth → user-auth.md、T048で実装確認）
- **FR-019**: Git diffでインクリメンタル更新（T050で実装確認）
- **FR-019a/FR-019b**: DocumentStructureの自動移行（T059で実装）
- **FR-022**: コマンドファイル名`speckit.doc-init.md`と`speckit.doc-update.md`（T033、T055で確認）
- **FR-023a**: importlib.resourcesでテンプレートアクセス（T029、T030、T064で確認）
- **FR-023b**: 既存ファイル上書き確認（T067で実装）
- **FR-023c**: ベストエフォートエラーハンドリング（T069で実装）

---

## Summary to Return

- **総タスク数**: 80タスク
- **ユーザーストーリー別タスク数**:
  - Setup（Phase 1）: 5タスク
  - Foundational（Phase 2）: 10タスク
  - US1（/speckit.doc-init）: 20タスク（テスト: 8、実装: 12）
  - US2（/speckit.doc-update）: 24タスク（テスト: 8、実装: 16）
  - US3（speckit-docs install）: 11タスク（テスト: 4、実装: 7）
  - Polish & Integration（Phase 6）: 10タスク
- **並列実行可能タスク数**: 45タスク（全体の56%）
- **MVP範囲**: Phase 1-5（すべてのフェーズ、US1-US3すべて含む、P1優先度）
  - Phase 1-2: 基盤構築（15タスク）
  - Phase 3: US1完成で初期化コマンド使用可能（20タスク）
  - Phase 4: US2完成でドキュメント生成可能（24タスク）
  - Phase 5: US3完成でspec-kit拡張として配布可能（11タスク）
  - Phase 6: 品質向上とドキュメント整備（10タスク）

**推定実装時間**:
- Foundationalフェーズ完了まで: 2-3日
- US1完了（初期化機能）: 3-4日
- US2完了（更新機能）: 4-5日
- US3完了（インストール機能）: 2-3日
- Phase 6（品質向上）: 2-3日
- **合計**: 13-18日（単一開発者、TDD準拠）

**並列開発時の推定時間**:
- Foundationalフェーズ: 1-2日（並列不可）
- US1、US3並列実装: 3-4日
- US2実装: 4-5日
- Phase 6: 1-2日（並列可）
- **合計**: 9-13日（3人チーム）
