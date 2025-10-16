---
description: "Implementation task list for spec-kit-docs feature"
---

# Tasks: spec-kit-docs - AI駆動型ドキュメント生成システム

**Branch**: `001-draft-init-spec` | **Date**: 2025-10-16
**Input**: Design documents from `/specs/001-draft-init-spec/` (spec.md, plan.md, data-model.md, contracts/)
**Prerequisites**: plan.md (completed), spec.md (completed), research.md (completed), data-model.md (completed), contracts/ (completed)

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US7)
- Include exact file paths in descriptions

## MVP Scope Definition

MVP consists of Phase 3-6 (User Stories 1, 2, 3, 7):
- **User Story 1**: `/doc-init` command - Initialize Sphinx/MkDocs project
- **User Story 2**: `/doc-update` command - Generate docs from specs/
- **User Story 3**: `speckit-docs install` command - Install as spec-kit extension
- **User Story 7**: LLM transformation - Default-enabled AI-driven user-friendly content generation

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure: `src/speckit_docs/`, `tests/contract/`, `tests/integration/`, `tests/unit/`
- [ ] T002 Initialize pyproject.toml with dependencies: typer>=0.9, sphinx>=7.0, myst-parser>=2.0, mkdocs>=1.5, mkdocs-material>=9.0, gitpython>=3.1, jinja2>=3.1, markdown-it-py>=3.0, pytest>=8.0, pytest-cov>=4.0
- [ ] T003 [P] Configure ruff in pyproject.toml: select=["E", "F", "W", "I"], line-length=100, target-version="py311"
- [ ] T004 [P] Add specify-cli dependency: `specify-cli @ git+https://github.com/github/spec-kit.git`
- [ ] T005 [P] Configure mypy for type checking in pyproject.toml

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Implement SpecKitDocsError exception class in src/speckit_docs/exceptions.py with structured error messages (file_path, error_type, recommended_action)
- [ ] T007 [P] Implement BaseGenerator abstract class in src/speckit_docs/generators/base.py with 4 methods: initialize(), generate_feature_page(), update_navigation(), validate()
- [ ] T008 [P] Create SpecKitProject dataclass in src/speckit_docs/parsers/spec_parser.py (root_dir, specify_dir, specs_dir, git_repo)
- [ ] T009 [P] Create Feature dataclass in src/speckit_docs/parsers/spec_parser.py (id, number, name, directory, spec_file, plan_file, tasks_file, status)
- [ ] T010 [P] Create DocumentationSite dataclass in src/speckit_docs/generators/base.py (root_dir, tool_type, structure_type, project_name, feature_pages)
- [ ] T011 [P] Create DependencyResult dataclass in src/speckit_docs/utils/dependencies.py (status, message, installed_packages)
- [ ] T012 [P] Create PackageManager dataclass in src/speckit_docs/utils/dependencies.py (name, command, available)
- [ ] T013 [P] Implement Git utility functions in src/speckit_docs/utils/git.py: get_changed_files(), get_remote_url(), get_user_name()
- [ ] T014 [P] Implement filesystem utility functions in src/speckit_docs/utils/fs.py: ensure_dir_exists(), copy_file(), detect_feature_directories()
- [ ] T015 [P] Implement Jinja2 template loader in src/speckit_docs/utils/template.py: load_template(), render_template()
- [ ] T016 Implement logging configuration in src/speckit_docs/utils/logging.py: setup_logging() with INFO/DEBUG/ERROR levels

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - ドキュメントプロジェクトの初期化 (Priority: P1) 🎯 MVP

**Goal**: Users can initialize documentation projects (Sphinx/MkDocs) with a single command

**Independent Test**: Run `/doc-init --type sphinx` in a spec-kit project, verify docs/ directory is created with conf.py, index.md, Makefile

### Tests for User Story 1 (TDD Required - Write FIRST) ⚠️

- [ ] T017 [P] [US1] Contract test for doc_init.py CLI arguments in tests/contract/test_doc_init_command.py
- [ ] T018 [P] [US1] Integration test for Sphinx initialization in tests/integration/test_sphinx_generation.py
- [ ] T019 [P] [US1] Integration test for MkDocs initialization in tests/integration/test_mkdocs_generation.py

### Implementation for User Story 1

- [ ] T020 [P] [US1] Implement SphinxGenerator class in src/speckit_docs/generators/sphinx.py (initialize(), generate_feature_page(), update_navigation(), validate())
- [ ] T021 [P] [US1] Implement MkDocsGenerator class in src/speckit_docs/generators/mkdocs.py (initialize(), generate_feature_page(), update_navigation(), validate())
- [ ] T022 [US1] Implement doc_init.py script in src/speckit_docs/scripts/doc_init.py with argparse: --type, --project-name, --author, --version, --language, --force, --dependency-target, --auto-install, --no-install
- [ ] T023 [US1] Implement feature count detection in doc_init.py: detect_structure_type() function (flat if <=5 features, comprehensive if >=6 features)
- [ ] T024 [US1] Implement dependency detection in src/speckit_docs/utils/dependencies.py: detect_installed_packages() using importlib.util.find_spec()
- [ ] T025 [US1] Implement dependency installation in src/speckit_docs/utils/dependencies.py: handle_dependencies() function with user confirmation (typer.confirm())
- [ ] T026 [US1] Implement package manager detection in src/speckit_docs/utils/dependencies.py: detect_package_managers() using shutil.which()
- [ ] T027 [US1] Implement alternative installation methods display in src/speckit_docs/utils/dependencies.py: show_alternative_methods() function
- [ ] T028 [US1] Add Sphinx templates to src/speckit_docs/templates/sphinx/: conf.py.j2, index.md.j2, Makefile.j2
- [ ] T029 [US1] Add MkDocs templates to src/speckit_docs/templates/mkdocs/: mkdocs.yml.j2, index.md.j2
- [ ] T030 [US1] Add error handling in doc_init.py: validate .specify/ directory exists (FR-001), handle existing docs/ directory (FR-003d)
- [ ] T031 [US1] Add logging to doc_init.py: progress messages (INFO level), dependency installation status

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - spec-kit仕様からのドキュメント更新 (Priority: P1) 🎯 MVP

**Goal**: Users can update documentation from specs/ directory with a single command

**Independent Test**: Run `/doc-update` after `/doc-init`, verify docs/features/ contains pages for all features in specs/

### Tests for User Story 2 (TDD Required - Write FIRST) ⚠️

- [ ] T032 [P] [US2] Contract test for doc_update.py CLI arguments in tests/contract/test_doc_update_command.py
- [ ] T033 [P] [US2] Integration test for Sphinx documentation update in tests/integration/test_sphinx_generation.py
- [ ] T034 [P] [US2] Integration test for MkDocs documentation update in tests/integration/test_mkdocs_generation.py
- [ ] T035 [P] [US2] Unit test for SpecParser in tests/unit/test_parsers/test_spec_parser.py
- [ ] T036 [P] [US2] Unit test for PlanParser in tests/unit/test_parsers/test_plan_parser.py
- [ ] T037 [P] [US2] Unit test for TasksParser in tests/unit/test_parsers/test_tasks_parser.py

### Implementation for User Story 2

- [ ] T038 [P] [US2] Implement SpecParser class in src/speckit_docs/parsers/spec_parser.py: parse_spec_md() function (extract user stories, requirements, success criteria)
- [ ] T039 [P] [US2] Implement PlanParser class in src/speckit_docs/parsers/plan_parser.py: parse_plan_md() function (extract architecture, technical decisions)
- [ ] T040 [P] [US2] Implement TasksParser class in src/speckit_docs/parsers/tasks_parser.py: parse_tasks_md() function (extract task list, dependencies)
- [ ] T041 [US2] Implement doc_update.py script in src/speckit_docs/scripts/doc_update.py with argparse: --verbose, --quiet, --no-llm-transform (for US7 integration)
- [ ] T042 [US2] Implement feature discovery in doc_update.py: discover_features() function (scan specs/ directory, validate spec.md exists)
- [ ] T043 [US2] Implement Git diff-based change detection in doc_update.py: detect_changed_features() using GitPython (FR-019)
- [ ] T044 [US2] Implement structure migration logic in doc_update.py: migrate_to_comprehensive() function (move files from docs/ to docs/features/, update navigation)
- [ ] T045 [US2] Complete SphinxGenerator.generate_feature_page() in src/speckit_docs/generators/sphinx.py: render feature page with spec.md/plan.md/tasks.md content
- [ ] T046 [US2] Complete SphinxGenerator.update_navigation() in src/speckit_docs/generators/sphinx.py: update index.md toctree with feature pages
- [ ] T047 [US2] Complete MkDocsGenerator.generate_feature_page() in src/speckit_docs/generators/mkdocs.py: render feature page with spec.md/plan.md/tasks.md content
- [ ] T048 [US2] Complete MkDocsGenerator.update_navigation() in src/speckit_docs/generators/mkdocs.py: update mkdocs.yml nav section with feature pages
- [ ] T049 [US2] Add missing file handling in generators: render admonitions (.. note:: for Sphinx, !!! note for MkDocs) for missing plan.md/tasks.md (FR-018)
- [ ] T050 [US2] Add update summary logging in doc_update.py: display count of updated/unchanged features, structure migration status (FR-020)
- [ ] T051 [US2] Add error handling in doc_update.py: validate docs/ directory exists (FR-010), handle invalid markdown (FR-035)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - spec-kitインストール (Priority: P1) 🎯 MVP

**Goal**: Users can install spec-kit-docs as an extension to existing spec-kit projects

**Independent Test**: Run `uv tool install speckit-docs --from git+...` then `speckit-docs install` in a spec-kit project, verify `/doc-init` and `/doc-update` commands are available in Claude Code

### Tests for User Story 3 (TDD Required - Write FIRST) ⚠️

- [ ] T052 [P] [US3] Contract test for `speckit-docs install` CLI command in tests/contract/test_install_command.py
- [ ] T053 [P] [US3] Integration test for command template installation in tests/integration/test_command_installation.py

### Implementation for User Story 3

- [ ] T054 [US3] Implement CLI main entry point in src/speckit_docs/cli/main.py using typer: app = typer.Typer(), install command
- [ ] T055 [US3] Implement install command in src/speckit_docs/cli/main.py: validate spec-kit project (.specify/ and .claude/ exist), handle --force flag (FR-023b)
- [ ] T056 [US3] Create command template files in src/speckit_docs/commands/: doc-init.md, doc-update.md (to be copied to .claude/commands/)
- [ ] T057 [US3] Implement template file copying in install command: use importlib.resources to access src/speckit_docs/commands/, copy to .claude/commands/speckit.doc-init.md and .claude/commands/speckit.doc-update.md (FR-022, FR-023a)
- [ ] T058 [US3] Implement script file copying in install command: copy doc_init.py and doc_update.py from src/speckit_docs/scripts/ to .specify/scripts/docs/ (FR-023)
- [ ] T059 [US3] Implement existing file handling in install command: check if files exist, prompt user for confirmation (typer.confirm()), skip if declined (FR-023b)
- [ ] T060 [US3] Add best-effort error handling in install command: continue on partial failure, log errors, exit with code 1 (FR-023c)
- [ ] T061 [US3] Configure pyproject.toml [project.scripts]: add speckit-docs = "speckit_docs.cli.main:app" entry point

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 7 - LLM変換(デフォルト有効) (Priority: P1) 🎯 MVP

**Goal**: AI agent (Claude Code) transforms technical specifications into user-friendly documentation by default

**Independent Test**: Run `/doc-update` in Claude Code (without --no-llm-transform flag), verify generated docs contain natural language (not "FR-001: System MUST..."), verify cache is stored in .claude/.cache/llm-transforms.json

### Tests for User Story 7 (TDD Required - Write FIRST) ⚠️

- [ ] T062 [P] [US7] Unit test for LLM transform cache in tests/unit/test_utils/test_cache.py: test cache hit/miss, MD5 hash validation
- [ ] T063 [P] [US7] Integration test for LLM transform workflow in tests/integration/test_llm_transform.py: test successful transform, cache reuse, error handling

### Implementation for User Story 7

- [ ] T064 [P] [US7] Implement LLMTransformCache class in src/speckit_docs/utils/cache.py: load_cache(), save_cache(), get_cached_transform(), set_cached_transform()
- [ ] T065 [P] [US7] Implement MD5 hash generation in src/speckit_docs/utils/cache.py: compute_content_hash() using hashlib.md5()
- [ ] T066 [US7] Update doc-update.md command template in src/speckit_docs/commands/doc-update.md: add LLM transform workflow (read spec.md, transform Functional Requirements, pass to doc_update.py)
- [ ] T067 [US7] Update doc-update.md command template: add cache integration (check cache before transform, store after transform)
- [ ] T068 [US7] Update doc-update.md command template: add content size validation (max 10,000 tokens per feature, FR-038a)
- [ ] T069 [US7] Update doc-update.md command template: add error handling (transform failure, quality check failure, FR-038b, FR-038c)
- [ ] T070 [US7] Update doc-update.md command template: add Git diff integration (only transform changed features, use cache for unchanged, FR-038e)
- [ ] T071 [US7] Update doc_update.py script: accept --transformed-content argument (path to JSON file with transformed content per feature)
- [ ] T072 [US7] Update doc_update.py script: add --no-llm-transform flag support (skip LLM transform, use original content, FR-038g)
- [ ] T073 [US7] Update SphinxGenerator/MkDocsGenerator: render transformed content if provided, add link to original spec.md (FR-038d)
- [ ] T074 [US7] Update doc_update.py: add LLM transform statistics to update summary (success count, cache reuse count, FR-038f, FR-020)
- [ ] T075 [US7] Add error messages to doc-update.md: content size exceeded, transform error, quality check failure (with file path, error type, recommended action)

**Checkpoint**: At this point, MVP (User Stories 1, 2, 3, 7) is complete and fully functional

---

## Phase 7: User Story 4 - 複数機能統合 (Priority: P2)

**Goal**: System intelligently integrates entities and APIs across multiple features

**Independent Test**: Create project with 001-core defining User{id, name, email} and 003-profiles adding User.profile_picture, verify generated docs show single unified User entity

### Tests for User Story 4 (TDD Required - Write FIRST) ⚠️

- [ ] T076 [P] [US4] Unit test for EntityParser in tests/unit/test_parsers/test_entity_parser.py
- [ ] T077 [P] [US4] Unit test for APIEndpointParser in tests/unit/test_parsers/test_api_parser.py
- [ ] T078 [P] [US4] Unit test for SynthesisEngine in tests/unit/test_synthesis/test_synthesis_engine.py
- [ ] T079 [P] [US4] Integration test for entity integration in tests/integration/test_entity_integration.py

### Implementation for User Story 4

- [ ] T080 [P] [US4] Create Entity dataclass in src/speckit_docs/parsers/entity_parser.py (name, fields, introduced_in, is_enum, enum_values)
- [ ] T081 [P] [US4] Create EntityField dataclass in src/speckit_docs/parsers/entity_parser.py (name, type_hint, description, introduced_in, modified_in)
- [ ] T082 [P] [US4] Create APIEndpoint dataclass in src/speckit_docs/parsers/api_parser.py (method, path, summary, parameters, introduced_in, modified_in)
- [ ] T083 [P] [US4] Create SynthesisResult dataclass in src/speckit_docs/synthesis/synthesis_engine.py (entities, api_endpoints, conflicts, breaking_changes)
- [ ] T084 [US4] Implement EntityParser in src/speckit_docs/parsers/entity_parser.py: parse_data_model_md() function (FR-025)
- [ ] T085 [US4] Implement APIEndpointParser in src/speckit_docs/parsers/api_parser.py: parse_contracts_dir() function (FR-026)
- [ ] T086 [US4] Implement SynthesisEngine in src/speckit_docs/synthesis/synthesis_engine.py: merge_entities() function with conflict detection (FR-027)
- [ ] T087 [US4] Implement breaking change detection in SynthesisEngine: detect_breaking_changes() function (type changes, field deletions)
- [ ] T088 [US4] Update SphinxGenerator/MkDocsGenerator: render integrated data model section with feature annotations (FR-028)
- [ ] T089 [US4] Update SphinxGenerator/MkDocsGenerator: render integrated API reference section with feature annotations
- [ ] T090 [US4] Add conflict resolution logging: log warnings for conflicts, apply latest-wins strategy

**Checkpoint**: User Story 4 complete, data model and API integration working

---

## Phase 8: User Story 5 - 対象者別ドキュメント (Priority: P3)

**Goal**: Users can generate audience-specific documentation (enduser/developer/contributor)

**Independent Test**: Generate docs with --audience=enduser, verify plan.md and tasks.md are excluded, then generate with --audience=developer, verify API contracts are included

### Tests for User Story 5 (TDD Required - Write FIRST) ⚠️

- [ ] T091 [P] [US5] Unit test for AudienceFilter in tests/unit/test_filters/test_audience_filter.py
- [ ] T092 [P] [US5] Integration test for audience filtering in tests/integration/test_audience_filtering.py

### Implementation for User Story 5

- [ ] T093 [P] [US5] Create Audience dataclass in src/speckit_docs/filters/audience_filter.py (type: AudienceType enum)
- [ ] T094 [US5] Implement AudienceFilter in src/speckit_docs/filters/audience_filter.py: filter_content() function (FR-029)
- [ ] T095 [US5] Update doc_update.py: add --audience argument (enduser/developer/contributor)
- [ ] T096 [US5] Update generators: apply audience filter before rendering pages (exclude plan.md/tasks.md for enduser, etc.)
- [ ] T097 [US5] Update generators: filter in-progress features for enduser audience (FR-029)

**Checkpoint**: User Story 5 complete, audience-specific documentation working

---

## Phase 9: User Story 6 - バージョン履歴 (Priority: P3)

**Goal**: Users can see how entities and APIs evolved across features with version history

**Independent Test**: Generate docs for project with User entity modified across 3 features, verify User page has "Version History" section with 3 entries

### Tests for User Story 6 (TDD Required - Write FIRST) ⚠️

- [ ] T098 [P] [US6] Unit test for VersionHistory in tests/unit/test_history/test_version_history.py
- [ ] T099 [P] [US6] Integration test for version history rendering in tests/integration/test_version_history.py

### Implementation for User Story 6

- [ ] T100 [US6] Implement VersionHistory class in src/speckit_docs/history/version_history.py: track_entity_evolution() function (FR-031)
- [ ] T101 [US6] Implement breaking change detection in VersionHistory: detect_breaking_changes() function (FR-032)
- [ ] T102 [US6] Update generators: render version history section for entities and APIs
- [ ] T103 [US6] Update generators: add breaking change badges (⚠️ Breaking Change (v003)) to documentation (FR-032)

**Checkpoint**: User Story 6 complete, version history and traceability working

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T104 [P] Add comprehensive docstrings to all public functions and classes in src/speckit_docs/
- [ ] T105 [P] Update CLAUDE.md with all conventions from plan.md (architecture patterns, code style, testing requirements)
- [ ] T106 [P] Create README.md with installation instructions: uv tool install speckit-docs --from git+https://github.com/drillan/spec-kit-docs.git
- [ ] T107 [P] Create quickstart.md guide with step-by-step tutorial (install → doc-init → doc-update)
- [ ] T108 Run full test suite: uv run pytest --cov=speckit_docs --cov-report=html (verify 80%+ coverage)
- [ ] T109 Run ruff linter: uv run ruff check . (fix all errors and warnings)
- [ ] T110 Run mypy type checker: uv run mypy src/speckit_docs (fix all type errors)
- [ ] T111 Validate all user story acceptance scenarios manually (US1-US7)
- [ ] T112 Validate quickstart.md tutorial works end-to-end in a test project

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion
- **User Story 2 (Phase 4)**: Depends on Foundational completion AND User Story 1 (needs generators from US1)
- **User Story 3 (Phase 5)**: Depends on Foundational completion AND User Story 1 AND User Story 2 (installs commands that use US1/US2)
- **User Story 7 (Phase 6)**: Depends on User Story 2 (extends doc-update workflow)
- **User Story 4 (Phase 7)**: Depends on User Story 2 (extends parsing and generation)
- **User Story 5 (Phase 8)**: Depends on User Story 2 AND User Story 4 (filters integrated content)
- **User Story 6 (Phase 9)**: Depends on User Story 4 (tracks entity/API evolution)
- **Polish (Phase 10)**: Depends on all MVP user stories (Phase 3-6) completion

### User Story Dependencies

- **User Story 1 (P1)**: Foundation → US1 (can start immediately after Phase 2)
- **User Story 2 (P1)**: Foundation → US1 → US2 (needs generators from US1)
- **User Story 3 (P1)**: Foundation → US1 → US2 → US3 (installs commands that use US1/US2)
- **User Story 7 (P1)**: Foundation → US1 → US2 → US7 (extends US2 workflow)
- **User Story 4 (P2)**: Foundation → US1 → US2 → US4 (extends US2 parsing)
- **User Story 5 (P3)**: Foundation → US1 → US2 → US4 → US5 (filters US4 integrated content)
- **User Story 6 (P3)**: Foundation → US1 → US2 → US4 → US6 (tracks US4 entity evolution)

### Dependency Graph

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) ← BLOCKS all user stories
    ↓
    ├─→ Phase 3 (US1: doc-init) ← MVP
    │       ↓
    ├─→ Phase 4 (US2: doc-update) ← MVP (depends on US1 generators)
    │       ↓
    ├─→ Phase 5 (US3: install) ← MVP (depends on US1 + US2)
    │       ↓
    ├─→ Phase 6 (US7: LLM transform) ← MVP (depends on US2)
    │       ↓
    ├─→ Phase 7 (US4: integration) (depends on US2)
    │       ↓
    │       ├─→ Phase 8 (US5: audience) (depends on US4)
    │       └─→ Phase 9 (US6: version history) (depends on US4)
    ↓
Phase 10 (Polish) ← Depends on MVP complete (Phase 3-6)
```

### Within Each User Story

- Tests (contract/integration/unit) MUST be written and FAIL before implementation (TDD required)
- Dataclasses before parsers
- Parsers before generators
- Generators before CLI commands
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**: All tasks T001-T005 can run in parallel (different files, configuration only)

**Phase 2 (Foundational)**: Tasks T007-T015 can run in parallel (independent modules):
- T007 (BaseGenerator) || T008 (SpecKitProject) || T009 (Feature) || T010 (DocumentationSite) || T011 (DependencyResult) || T012 (PackageManager) || T013 (Git utils) || T014 (FS utils) || T015 (Template utils)

**Phase 3 (US1)**:
- Tests T017-T019 can run in parallel (different test files)
- Generators T020-T021 can run in parallel (SphinxGenerator || MkDocsGenerator)
- Templates T028-T029 can run in parallel (Sphinx templates || MkDocs templates)

**Phase 4 (US2)**:
- Tests T032-T037 can run in parallel (different test files)
- Parsers T038-T040 can run in parallel (SpecParser || PlanParser || TasksParser)

**Phase 5 (US3)**:
- Tests T052-T053 can run in parallel

**Phase 6 (US7)**:
- Tests T062-T063 can run in parallel
- Cache implementation T064-T065 can run in parallel

**Phase 7 (US4)**:
- Tests T076-T079 can run in parallel
- Dataclasses T080-T083 can run in parallel

**Phase 8 (US5)**:
- Tests T091-T092 can run in parallel

**Phase 9 (US6)**:
- Tests T098-T099 can run in parallel

**Phase 10 (Polish)**:
- Tasks T104-T107 can run in parallel (documentation and docstrings)

---

## Parallel Example: Phase 2 (Foundational)

```bash
# Launch all independent foundational tasks together:
Task: "Implement BaseGenerator abstract class in src/speckit_docs/generators/base.py"
Task: "Create SpecKitProject dataclass in src/speckit_docs/parsers/spec_parser.py"
Task: "Create Feature dataclass in src/speckit_docs/parsers/spec_parser.py"
Task: "Create DocumentationSite dataclass in src/speckit_docs/generators/base.py"
Task: "Create DependencyResult dataclass in src/speckit_docs/utils/dependencies.py"
Task: "Create PackageManager dataclass in src/speckit_docs/utils/dependencies.py"
Task: "Implement Git utility functions in src/speckit_docs/utils/git.py"
Task: "Implement filesystem utility functions in src/speckit_docs/utils/fs.py"
Task: "Implement Jinja2 template loader in src/speckit_docs/utils/template.py"
```

---

## Parallel Example: Phase 3 (User Story 1)

```bash
# Launch all tests for User Story 1 together:
Task: "Contract test for doc_init.py CLI arguments in tests/contract/test_doc_init_command.py"
Task: "Integration test for Sphinx initialization in tests/integration/test_sphinx_generation.py"
Task: "Integration test for MkDocs initialization in tests/integration/test_mkdocs_generation.py"

# Launch both generators together:
Task: "Implement SphinxGenerator class in src/speckit_docs/generators/sphinx.py"
Task: "Implement MkDocsGenerator class in src/speckit_docs/generators/mkdocs.py"

# Launch all templates together:
Task: "Add Sphinx templates to src/speckit_docs/templates/sphinx/: conf.py.j2, index.md.j2, Makefile.j2"
Task: "Add MkDocs templates to src/speckit_docs/templates/mkdocs/: mkdocs.yml.j2, index.md.j2"
```

---

## Implementation Strategy

### MVP First (Phase 3-6 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (doc-init)
4. Complete Phase 4: User Story 2 (doc-update)
5. Complete Phase 5: User Story 3 (install)
6. Complete Phase 6: User Story 7 (LLM transform with default-enabled behavior)
7. **STOP and VALIDATE**: Test all MVP stories independently
8. Deploy/demo MVP

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Demo (doc-init works!)
3. Add User Story 2 → Test independently → Demo (doc-update works!)
4. Add User Story 3 → Test independently → Demo (install works!)
5. Add User Story 7 → Test independently → Demo (LLM transform works!) → **MVP COMPLETE**
6. Add User Story 4 → Test independently → Demo (integration works!)
7. Add User Story 5 → Test independently → Demo (audience filtering works!)
8. Add User Story 6 → Test independently → Demo (version history works!)
9. Polish → Final release

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (doc-init)
   - Developer B: User Story 2 (doc-update) - starts after US1 generators are ready
   - Developer C: User Story 3 (install) - starts after US1 + US2 are ready
3. After MVP (US1-3) complete:
   - Developer A: User Story 7 (LLM transform)
   - Developer B: User Story 4 (integration)
   - Developer C: User Story 5 (audience) - starts after US4
4. Stories complete and integrate independently

---

## Task Count Summary

**Total Tasks**: 112

**By Phase**:
- Phase 1 (Setup): 5 tasks
- Phase 2 (Foundational): 11 tasks (BLOCKS all user stories)
- Phase 3 (US1): 15 tasks (3 tests + 12 implementation)
- Phase 4 (US2): 20 tasks (6 tests + 14 implementation)
- Phase 5 (US3): 10 tasks (2 tests + 8 implementation)
- Phase 6 (US7): 14 tasks (2 tests + 12 implementation)
- Phase 7 (US4): 15 tasks (4 tests + 11 implementation)
- Phase 8 (US5): 5 tasks (2 tests + 3 implementation)
- Phase 9 (US6): 4 tasks (2 tests + 2 implementation)
- Phase 10 (Polish): 9 tasks

**MVP Scope (Phase 1-6)**: 75 tasks
**Post-MVP (Phase 7-10)**: 37 tasks

**By Story**:
- US1 (doc-init, P1): 15 tasks
- US2 (doc-update, P1): 20 tasks
- US3 (install, P1): 10 tasks
- US7 (LLM transform, P1): 14 tasks
- US4 (integration, P2): 15 tasks
- US5 (audience, P3): 5 tasks
- US6 (version history, P3): 4 tasks
- Setup + Foundational + Polish: 25 tasks

**Parallelizable Tasks**: 47 tasks (marked with [P])
**Sequential Tasks**: 65 tasks

**Test Tasks**: 27 tasks (TDD required - write FIRST)
**Implementation Tasks**: 85 tasks

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability (US1, US2, US3, US7, US4, US5, US6)
- No [Story] label = Setup/Foundational/Polish phase tasks
- Each user story should be independently completable and testable
- Verify tests FAIL before implementing (TDD required by constitution C010)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- **MVP Definition**: Phase 3-6 (User Stories 1, 2, 3, 7) = 75 tasks
- **LLM Transform Default**: US7 enables LLM transformation by default, `--no-llm-transform` flag for opt-out (Session 2025-10-16 decision)
