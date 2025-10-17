# Consistency Checklist: `--no-llm-transform` Flag Removal Decision

**Purpose**: Validate consistency between the spec.md decision to completely remove `--no-llm-transform` flag and actual implementation/documentation.

**Created**: 2025-10-17
**Feature**: 001-draft-init-spec
**Focus**: Spec-Implementation Consistency Validation

---

## Requirement Completeness

- [ ] CHK001 - Are all code locations that reference `--no-llm-transform` identified in the spec? [Completeness, Gap]
- [ ] CHK002 - Are removal requirements defined for all implementation artifacts (code, docs, tests, templates)? [Coverage, Spec §研究セッション決定39]
- [ ] CHK003 - Are requirements specified for removing related features (cache functionality, `--clear-cache` flag)? [Completeness, Spec §Q3回答]

## Requirement Clarity

- [ ] CHK004 - Is "complete removal" defined with specific artifacts to be deleted? [Clarity, Spec §Q1回答 Option A]
- [ ] CHK005 - Are the boundaries clear between what should be removed vs. retained? [Clarity, Spec §Q3回答 Option B]
- [ ] CHK006 - Is the rationale for removal documented with measurable user value criteria? [Clarity, Spec §Q1回答理由(1)-(4)]

## Requirement Consistency

- [ ] CHK007 - Do spec.md, plan.md, and research.md consistently specify complete removal? [Consistency, Cross-Artifact]
- [ ] CHK008 - Does the implementation in `doc_update.py:57-58` contradict the spec.md decision? [Conflict, Implementation vs Spec]
- [ ] CHK009 - Do command templates in `speckit.doc-update.md:46,166,169` conflict with removal requirements? [Conflict, Documentation vs Spec]
- [ ] CHK010 - Do tasks.md references (T041, T072) align with the removal decision timeline? [Consistency, Spec §研究セッション vs Tasks]
- [ ] CHK011 - Are error message recommendations in spec.md (§Q2回答) consistent with removal decision? [Conflict, Spec §Q2 mentions `--no-llm-transform` as fallback option]

## Acceptance Criteria Quality

- [ ] CHK012 - Can "flag is completely removed" be objectively verified? [Measurability, Spec §Q1回答]
- [ ] CHK013 - Are specific file paths defined for validation (doc_update.py, speckit.doc-update.md, tests)? [Measurability]
- [ ] CHK014 - Is the acceptance criteria for "no references remain" testable via grep/search? [Measurability]

## Scenario Coverage

- [ ] CHK015 - Are requirements defined for migrating existing users who depend on `--no-llm-transform`? [Coverage, Migration Path, Gap]
- [ ] CHK016 - Are deprecation warnings or migration guides specified? [Coverage, User Communication, Gap]
- [ ] CHK017 - Are requirements defined for handling existing cached data from removed cache feature? [Coverage, Data Migration, Gap]

## Edge Case Coverage

- [ ] CHK018 - What happens to users who have `--no-llm-transform` in their scripts/CI pipelines? [Edge Case, Backward Compatibility, Gap]
- [ ] CHK019 - Are error messages defined when removed flag is used? [Edge Case, User Experience, Gap]
- [ ] CHK020 - Is behavior specified when old documentation references the removed flag? [Edge Case, Documentation Versioning, Gap]

## Non-Functional Requirements

- [ ] CHK021 - Are backward compatibility requirements (or explicit breaking change policy) defined? [NFR, Gap]
- [ ] CHK022 - Are documentation update requirements specified for user-facing guides? [NFR, Documentation Quality, Gap]
- [ ] CHK023 - Are test update/removal requirements defined for tests referencing removed flag? [NFR, Test Coverage, Gap]

## Dependencies & Assumptions

- [ ] CHK024 - Is the dependency between cache removal and flag removal explicitly documented? [Dependency, Spec §Q3回答]
- [ ] CHK025 - Is the assumption "users accept LLM-only mode" validated or documented as risk? [Assumption, Gap]
- [ ] CHK026 - Are external dependencies on this flag (if any) identified? [Dependency, Gap]

## Ambiguities & Conflicts

- [ ] CHK027 - Why does spec.md §Q2 recommend `--no-llm-transform` as error fallback if the flag is being removed? [Conflict, Spec §Q2回答 vs §Q1回答]
- [ ] CHK028 - Why does spec.md §89-94 describe `--no-llm-transform` behavior if it's being removed? [Ambiguity, Spec §Development Notes vs 研究セッション決定]
- [ ] CHK029 - Are the contradictory decisions (§89-94 preserve flag vs §106-108 remove flag) resolved? [Conflict, Spec Internal Inconsistency]
- [ ] CHK030 - Is there a clear decision timeline (when was removal decided vs when were earlier sections written)? [Ambiguity, Decision History, Gap]

## Implementation Validation

- [ ] CHK031 - Does `src/speckit_docs/scripts/doc_update.py:57-58` implementation contradict removal requirements? [Conflict, Code vs Spec]
- [ ] CHK032 - Do `src/speckit_docs/commands/speckit.doc-update.md` examples contradict removal requirements? [Conflict, Documentation vs Spec]
- [ ] CHK033 - Do `specs/001-draft-init-spec/tasks.md` T041/T072 contradict removal requirements? [Conflict, Tasks vs Spec]
- [ ] CHK034 - Are requirements defined for updating all 15+ files containing `--no-llm-transform` references? [Coverage, Implementation Scope]

## Traceability

- [ ] CHK035 - Is there a unique requirement ID for the flag removal decision? [Traceability, Gap]
- [ ] CHK036 - Are all code references traceable back to removal requirements? [Traceability, Gap]
- [ ] CHK037 - Is the decision rationale traceable to user stories/value proposition? [Traceability, Spec §Q1回答理由 → US Goal]

---

## Summary Statistics

- **Total Items**: 37
- **Categories**: 10
- **Traceability**: 25/37 items (68%) include spec references or gap markers
- **Primary Issues Identified**:
  1. **Spec Internal Conflict**: Early sections (§89-94) describe flag behavior, later sections (§106-108) mandate removal
  2. **Implementation Lag**: Code/docs still implement removed feature
  3. **Missing Migration Path**: No requirements for user migration/breaking change communication
  4. **Ambiguous Timeline**: Unclear when removal decision was made relative to earlier spec sections
