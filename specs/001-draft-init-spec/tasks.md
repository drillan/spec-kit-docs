# Tasks: spec-kit-docs - AI駆動型ドキュメント生成システム

**Input**: Design documents from `/specs/001-draft-init-spec/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are not explicitly requested in the specification, so test tasks are minimal and focused on contract validation only.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, Setup, Foundation)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `src/speckit_docs/`, `tests/` at repository root
- Paths based on plan.md structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure per research.md Decision 10

- [X] T001 [Setup] Create project directory structure per plan.md: `src/speckit_docs/`, `src/speckit_docs/commands/`, `src/speckit_docs/generators/`, `src/speckit_docs/parsers/`, `src/speckit_docs/templates/`, `src/speckit_docs/utils/`, `tests/unit/`, `tests/integration/`, `tests/contract/`
- [X] T002 [Setup] Initialize pyproject.toml with Python 3.11+, dependencies: sphinx>=7.0, myst-parser>=2.0, mkdocs>=1.5, markdown-it-py>=3.0, GitPython>=3.1, Jinja2>=3.1 (research.md Decision 10)
- [X] T003 [P] [Setup] Configure uv for package management (research.md Decision 10)
- [X] T004 [P] [Setup] Setup .gitignore for Python project (`__pycache__/`, `*.pyc`, `.pytest_cache/`, `dist/`, `build/`, `*.egg-info/`)
- [X] T005 [P] [Setup] Create src/speckit_docs/__init__.py with version = "0.1.0"

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 [P] [Foundation] Create Jinja2 template files for Sphinx: `src/speckit_docs/templates/sphinx/conf.py.j2` (file-formats.md Section 1), `src/speckit_docs/templates/sphinx/index.md.j2` (file-formats.md Section 2), `src/speckit_docs/templates/sphinx/Makefile.j2` (file-formats.md Section 3), `src/speckit_docs/templates/sphinx/make.bat.j2` (file-formats.md Section 4)
- [X] T007 [P] [Foundation] Create Jinja2 template files for MkDocs: `src/speckit_docs/templates/mkdocs/mkdocs.yml.j2` (file-formats.md Section 5), `src/speckit_docs/templates/mkdocs/index.md.j2` (file-formats.md Section 6)
- [X] T008 [Foundation] Implement MarkdownParser class in src/speckit_docs/parsers/markdown_parser.py using markdown-it-py (data-model.md Entity 10, research.md Decision 5): parse(), extract_headings(), extract_code_blocks(), extract_metadata()
- [X] T009 [P] [Foundation] Implement FeatureScanner class in src/speckit_docs/parsers/feature_scanner.py (data-model.md Entity 1): scan .specify/specs/ directories, detect spec.md presence (FR-001), return Feature[] list
- [X] T010 [Foundation] Implement BaseGenerator abstract class in src/speckit_docs/generators/base.py (data-model.md Entity 6, research.md Decision 3): init_project(), update_docs(), build_docs(), validate_project()
- [X] T011 [P] [Foundation] Implement custom error classes in src/speckit_docs/utils/validation.py: SpecKitDocsError(message, suggestion) (data-model.md Entity 12, research.md Decision 8)
- [X] T012 [P] [Foundation] Implement Git integration utilities in src/speckit_docs/utils/git.py: GitRepository wrapper, git diff functions (data-model.md Entity 9, research.md Decision 2)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - インストールと基本使用 (Priority: P1) 🎯 MVP Part 1

**Goal**: ユーザーがspec-kit-docsをインストールし、`/speckit.doc-init`コマンドでドキュメントプロジェクトを初期化できる

**Independent Test**: `uv run python .specify/scripts/docs/doc_init.py --type sphinx --no-interaction`を実行し、docs/conf.py、docs/index.md、docs/Makefile、docs/make.batが生成されることを確認

### Contract Tests for User Story 1 (Output Validation Only)

- [ ] T013 [P] [US1] Create contract test in tests/contract/test_doc_init_output.py: Validate generated conf.py is valid Python, contains myst_parser, source_suffix, myst_enable_extensions (file-formats.md Section 1 Validation Rules)
- [ ] T014 [P] [US1] Create contract test in tests/contract/test_doc_init_output.py: Validate generated index.md contains toctree directive, :maxdepth: option (file-formats.md Section 2 Validation Rules)

### Implementation for User Story 1

- [X] T015 [P] [US1] Create GeneratorConfig dataclass in src/speckit_docs/generators/__init__.py (data-model.md Entity 5): tool, project_name, author, version, language, theme, extensions, plugins, custom_settings, to_sphinx_conf(), to_mkdocs_yaml()
- [X] T016 [P] [US1] Create DocumentStructure class in src/speckit_docs/parsers/__init__.py (data-model.md Entity 4): type (FLAT/COMPREHENSIVE), root_dir, directories, index_file, determine_structure(feature_count), get_feature_path(feature_name)
- [X] T017 [US1] Implement interactive prompts module in src/speckit_docs/utils/prompts.py (cli-interface.md Interactive Prompts): prompt_tool_selection(), prompt_project_name(), prompt_author(), prompt_version(), prompt_language() with defaults
- [X] T018 [US1] Implement SphinxGenerator class in src/speckit_docs/generators/sphinx.py (data-model.md Entity 7): init_project() renders Jinja2 templates to docs/, handles myst-parser configuration (FR-005a)
- [X] T019 [US1] Implement MkDocsGenerator class in src/speckit_docs/generators/mkdocs.py (data-model.md Entity 8): init_project() renders Jinja2 templates to docs/
- [X] T020 [US1] Implement doc_init.py CLI script in .specify/scripts/docs/doc_init.py (cli-interface.md Python API): argparse setup with --type, --no-interaction flags, call to prompts module, Generator.init_project(), error handling with SpecKitDocsError
- [X] T021 [US1] Create Claude Code command definition in .claude/commands/doc-init.md: Execute `uv run python .specify/scripts/docs/doc_init.py {{ARGS}}` (cli-interface.md Command Mapping)
- [X] T022 [US1] Add project validation logic in src/speckit_docs/utils/validation.py: validate_speckit_project() checks .specify/ directory, validate_git_repo() checks git init (cli-interface.md Execution Flow Step 1)
- [X] T023 [US1] Implement feature scanning logic: Use FeatureScanner to discover features, determine DocumentStructure based on feature_count <= 5 (FLAT) or >= 6 (COMPREHENSIVE) (cli-interface.md Execution Flow Steps 3-4, research.md Decision 4)

**Checkpoint**: At this point, User Story 1 should be fully functional - `/speckit.doc-init` can initialize Sphinx or MkDocs projects

---

## Phase 4: User Story 2 - 基本的なドキュメント生成 (Priority: P1) 🎯 MVP Part 2

**Goal**: ユーザーが`/speckit.doc-update`コマンドで、spec.mdからドキュメント（Markdown）を生成できる

**Independent Test**: `/speckit.doc-update --no-build`を実行し、docs/以下に機能ごとの.mdファイルが生成され、index.mdのtoctreeが更新されることを確認

### Implementation for User Story 2

- [X] T024 [P] [US2] Create Document dataclass in src/speckit_docs/parsers/__init__.py (data-model.md Entity 2): file_path, type (SPEC/PLAN/TASKS), content, sections, last_modified, git_status, parse(), extract_metadata(), is_changed()
- [X] T025 [P] [US2] Create Section dataclass in src/speckit_docs/parsers/__init__.py (data-model.md Entity 3): title, level, content, line_start, line_end, subsections, to_sphinx_md(), to_mkdocs_md(), extract_code_blocks()
- [X] T026 [US2] Implement Document.parse() method using MarkdownParser: Parse spec.md into Section tree, extract metadata (FR-002, FR-012)
- [X] T027 [US2] Implement Section.to_sphinx_md() method: Convert Section to MyST Markdown format with proper directive syntax (FR-008, FR-013)
- [X] T028 [US2] Implement Section.to_mkdocs_md() method: Convert Section to MkDocs Markdown, convert MyST admonitions to MkDocs format (` ```{note}` → `!!! note`) (FR-008, FR-014, file-formats.md Section 8)
- [X] T029 [US2] Implement SphinxGenerator.update_docs() method in src/speckit_docs/generators/sphinx.py: For each Feature, parse spec.md, generate {feature-name}.md using Section.to_sphinx_md(), update index.md toctree (FR-013)
- [X] T030 [US2] Implement MkDocsGenerator.update_docs() method in src/speckit_docs/generators/mkdocs.py: For each Feature, parse spec.md, generate {feature-name}.md using Section.to_mkdocs_md(), update mkdocs.yml nav (FR-014)
- [X] T031 [US2] Implement file naming logic in Generator: Strip feature number from directory name (001-user-auth → user-auth.md) (FR-013, file-formats.md Section 7)
- [X] T032 [US2] Implement doc_update.py CLI script in .specify/scripts/docs/doc_update.py (cli-interface.md Python API): argparse setup with --full, --no-build flags, detect Sphinx/MkDocs by conf.py/mkdocs.yml presence, call Generator.update_docs()
- [X] T033 [US2] Create Claude Code command definition in .claude/commands/doc-update.md: Execute `uv run python .specify/scripts/docs/doc_update.py {{ARGS}}` (cli-interface.md Command Mapping)
- [X] T034 [US2] Add BuildResult dataclass in src/speckit_docs/generators/__init__.py (data-model.md Entity 11): success, output_dir, warnings, errors, build_time, file_count, is_valid(), get_summary()

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - Full `/speckit.doc-init` → `/speckit.doc-update --no-build` workflow generates Markdown documentation

---

## Phase 5: User Story 3 - HTMLビルド実行 (Priority: P1) 🎯 MVP Part 3

**Goal**: ユーザーが`/speckit.doc-update`でHTMLビルドまで実行し、ブラウザで閲覧可能なドキュメントを生成できる

**Independent Test**: `/speckit.doc-update`を実行し、docs/_build/html/index.html (Sphinx) または docs/site/index.html (MkDocs) が生成され、ブラウザで開けることを確認

### Implementation for User Story 3

- [X] T035 [US3] Implement SphinxGenerator.build_docs() method in src/speckit_docs/generators/sphinx.py: Execute `subprocess.run(["make", "html"])` in docs/ directory, capture output, parse warnings/errors, return BuildResult (FR-018)
- [X] T036 [US3] Implement MkDocsGenerator.build_docs() method in src/speckit_docs/generators/mkdocs.py: Execute `subprocess.run(["mkdocs", "build"])` in docs/ directory, capture output, return BuildResult (FR-019)
- [X] T037 [US3] Add build execution logic to doc_update.py: If --no-build flag absent, call Generator.build_docs() after update_docs(), display BuildResult.get_summary() (cli-interface.md Execution Flow Step 5)
- [X] T038 [US3] Implement performance tracking in BuildResult: Record build_time using time.time(), track file_count by counting generated HTML files (SC-001, SC-006)
- [X] T039 [US3] Add success message output in doc_update.py: Display checkmarks, file counts, build time, next steps (cli-interface.md Output Success)

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work - Complete `/speckit.doc-init` → `/speckit.doc-update` workflow produces browsable HTML documentation (MVP COMPLETE!)

---

## Phase 6: User Story 4 - 仕様変更の統合 (Priority: P2)

**Goal**: spec.mdを編集後、Git diffでインクリメンタル更新を実行し、変更された機能のみを再生成できる

**Independent Test**: spec.mdを編集してgit commitし、`/speckit.doc-update`を実行すると変更された機能のみが再生成されることを確認

### Implementation for User Story 4

- [X] T040 [US4] Implement ChangeDetector class in src/speckit_docs/utils/git.py (data-model.md Entity 9): get_changed_features() using `git diff --name-only HEAD~1 HEAD`, filter .specify/specs/ changes, return changed Feature[] (FR-010, research.md Decision 2)
- [X] T041 [US4] Integrate ChangeDetector into doc_update.py: If --full flag absent, use ChangeDetector.get_changed_features() instead of all features, display "X features changed" message (cli-interface.md Execution Flow Step 3)
- [X] T042 [US4] Add "no changes" handling in doc_update.py: If ChangeDetector returns empty list, display "変更が検出されませんでした" and exit (cli-interface.md Output "No Changes")
- [X] T043 [US4] Implement --full flag handling in doc_update.py: When --full is set, bypass ChangeDetector and regenerate all features (cli-interface.md Output "Full Regeneration")
- [X] T044 [US4] Add performance optimization: Document.is_changed(since) method to check file modification time, skip unchanged files within incremental update (data-model.md Entity 2)

**Checkpoint**: At this point, incremental updates work efficiently - Only changed features are regenerated, saving time on large projects

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T045 [P] [Polish] Create integration test in tests/integration/test_sphinx_workflow.py: End-to-end test for Sphinx (cli-interface.md Integration Tests): setup test project, run doc-init, run doc-update, verify files exist
- [ ] T046 [P] [Polish] Create integration test in tests/integration/test_mkdocs_workflow.py: End-to-end test for MkDocs (cli-interface.md Integration Tests): setup test project, run doc-init, run doc-update, verify files exist
- [ ] T047 [P] [Polish] Add comprehensive error handling: Validate all error cases in cli-interface.md Error Cases table (.specify/ missing, Git missing, docs/ exists, etc.)
- [ ] T048 [P] [Polish] Create .gitignore template files: For Sphinx (file-formats.md Section 9 Sphinx), for MkDocs (file-formats.md Section 9 MkDocs), include in init_project()
- [ ] T049 [Polish] Add logging infrastructure: Use Python logging module for debug output, info messages, warnings (research.md Decision 8)
- [ ] T050 [Polish] Performance validation: Run doc-update on 10-feature test project, verify completes in ≤ 45 seconds (SC-006), verify incremental update (1 feature) completes in ≤ 5 seconds (SC-008)
- [ ] T051 [P] [Polish] Code cleanup and type hints: Ensure all functions have type hints per Python 3.11+ features (data-model.md Implementation Notes)
- [ ] T052 [P] [Polish] Add docstrings: Document all public classes and methods with Google-style docstrings
- [ ] T053 [Polish] Run quickstart.md validation: Follow quickstart.md step-by-step to verify all instructions work

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2) - doc-init command
- **User Story 2 (Phase 4)**: Depends on User Story 1 (Phase 3) - doc-update command needs doc-init output
- **User Story 3 (Phase 5)**: Depends on User Story 2 (Phase 4) - HTML build needs Markdown output
- **User Story 4 (Phase 6)**: Depends on User Story 3 (Phase 5) - Incremental update enhancement
- **Polish (Phase 7)**: Depends on all MVP stories (Phase 3-5) being complete

### User Story Dependencies

- **User Story 1 (P1)**: Independent - Can start after Foundational (Phase 2)
- **User Story 2 (P1)**: Depends on User Story 1 - Needs doc-init output to test doc-update
- **User Story 3 (P1)**: Depends on User Story 2 - Needs Markdown to build HTML
- **User Story 4 (P2)**: Depends on User Story 3 - Enhancement to existing doc-update command

### Within Each User Story

- Contract tests can run in parallel [P]
- Templates and data classes can be created in parallel [P]
- Implementation follows: Data classes → Parser/Generator logic → CLI integration
- User Story phases must complete sequentially (US1 → US2 → US3 → US4) due to dependencies

### Parallel Opportunities

- **Phase 1 (Setup)**: T003, T004, T005 can run in parallel
- **Phase 2 (Foundational)**: T006, T007, T009, T011, T012 can run in parallel
- **Phase 3 (US1)**: T013, T014 (tests), T015, T016 (data classes) can run in parallel
- **Phase 4 (US2)**: T024, T025, T034 (data classes) can run in parallel
- **Phase 7 (Polish)**: T045, T046, T047, T048, T051, T052 can run in parallel

---

## Parallel Example: Foundational Phase

```bash
# Launch all parallel Foundational tasks together:
Task: "Create Jinja2 template files for Sphinx in src/speckit_docs/templates/sphinx/"
Task: "Create Jinja2 template files for MkDocs in src/speckit_docs/templates/mkdocs/"
Task: "Implement FeatureScanner class in src/speckit_docs/parsers/feature_scanner.py"
Task: "Implement custom error classes in src/speckit_docs/utils/validation.py"
Task: "Implement Git integration utilities in src/speckit_docs/utils/git.py"

# Then sequentially:
Task: "Implement MarkdownParser class" (depends on none)
Task: "Implement BaseGenerator abstract class" (depends on none)
```

## Parallel Example: User Story 1

```bash
# Launch all parallel User Story 1 tasks together:
Task: "Contract test for conf.py validation"
Task: "Contract test for index.md validation"
Task: "Create GeneratorConfig dataclass"
Task: "Create DocumentStructure class"

# Then sequentially:
Task: "Implement interactive prompts module"
Task: "Implement SphinxGenerator class"
Task: "Implement MkDocsGenerator class"
Task: "Implement doc_init.py CLI script"
```

---

## Implementation Strategy

### MVP First (User Stories 1-3 Only)

1. Complete Phase 1: Setup → Project structure ready
2. Complete Phase 2: Foundational (CRITICAL) → Templates, parsers, base classes ready
3. Complete Phase 3: User Story 1 → `/speckit.doc-init` works
4. Complete Phase 4: User Story 2 → `/speckit.doc-update --no-build` generates Markdown
5. Complete Phase 5: User Story 3 → `/speckit.doc-update` builds HTML
6. **STOP and VALIDATE**: Test full workflow end-to-end
7. Demo/Deploy MVP!

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (T001-T012)
2. Add User Story 1 → Test independently → `/speckit.doc-init` command works! (T013-T023)
3. Add User Story 2 → Test independently → Markdown generation works! (T024-T034)
4. Add User Story 3 → Test independently → HTML build works! (T035-T039) **MVP COMPLETE!**
5. Add User Story 4 → Test independently → Incremental updates work! (T040-T044)
6. Add Polish → Final testing and cleanup (T045-T053)

### Success Criteria Per Phase

- **After Phase 2**: All templates exist, MarkdownParser can parse spec.md, Generators inherit from BaseGenerator
- **After Phase 3**: `/speckit.doc-init --type sphinx --no-interaction` creates docs/ with conf.py, index.md, Makefile, make.bat
- **After Phase 4**: `/speckit.doc-update --no-build` creates docs/*.md files from spec.md
- **After Phase 5**: `/speckit.doc-update` creates docs/_build/html/index.html (Sphinx) or docs/site/index.html (MkDocs)
- **After Phase 6**: Editing spec.md and git commit → `/speckit.doc-update` only regenerates changed features

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story or phase (Setup, Foundation, US1-US4, Polish)
- MVP = User Stories 1, 2, 3 (doc-init + doc-update with HTML build)
- User Story 4 is P2 enhancement (incremental updates)
- User Stories 4 and 5 from spec.md (filtering, version history) are out of scope for this initial implementation phase - can be added in future iterations
- Contract tests focus on output validation only (no TDD approach requested)
- Performance targets: doc-init ≤ 30s, doc-update (10 features) ≤ 45s, incremental (1 feature) ≤ 5s
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Use uv for all Python commands: `uv run python ...`

**Total Tasks**: 53
**Tasks per Story**: Setup (5), Foundation (7), US1 (11), US2 (11), US3 (5), US4 (5), Polish (9)
**Parallel Opportunities**: 19 tasks marked [P]
**MVP Scope**: Phases 1-5 (Tasks T001-T039) = 39 tasks
