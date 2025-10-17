# Compliance Checklist - 仕様違反・憲章違反チェック

**Purpose**: LLM変換機能実装の仕様準拠と憲章原則準拠を検証する

**Created**: 2025-10-17

**Target**: バックエンド実装（doc_update.py、feature_page.py、コマンドテンプレート）

**Severity Focus**: CRITICAL + HIGH（仕様要件の直接違反）

---

## Requirement Completeness - 必須要件の実装

- [ ] CHK001 - FR-038eで必須と定義された`transformed_content`パラメータは、doc_update.pyで`typer.Option(...)`として必須定義されているか？ [Critical, Spec §FR-038e]
- [ ] CHK002 - transformed_contentパラメータが提供されない場合、doc_update.pyは明確なエラーメッセージ「--transformed-contentパラメータは必須です。LLM変換を実行してから.specify/scripts/docs/doc_update.pyを呼び出してください」を表示して終了する要件が実装されているか？ [Critical, Spec §FR-038e]
- [ ] CHK003 - FR-038bで定義された「LLM変換処理中にエラーが発生した場合、プロセスを中断する」要件は、コマンドテンプレートまたは実装コードで保証されているか？ [Critical, Spec §FR-038b]
- [ ] CHK004 - FR-038cで定義された4つの品質チェック（空文字列、最小文字数、エラーパターン、Markdownリンター）は、すべて実装されているか？ [High, Spec §FR-038c]
- [ ] CHK005 - FR-038で定義されたコンテンツソース選択ロジック（README.md/QUICKSTART.md統合、spec.md最小限抽出）は、コマンドテンプレートで明示的に記述されているか？ [High, Spec §FR-038]

## Requirement Clarity - 憲章原則「Primary Data Non-Assumption」準拠

- [ ] CHK006 - 憲章の「Primary Data Non-Assumption Principle」に違反する「Implicit Fallback Prohibition（暗黙のフォールバック禁止）」要件が遵守されているか？具体的には、LLM変換失敗時に自動的に元のファイルをコピーする処理は存在しないか？ [Critical, Constitution + Spec §FR-038b]
- [ ] CHK007 - feature_page.py:84-85のフォールバック処理（`else: spec_doc = self._parse_document(...)`）は、FR-038bの「フォールバック動作は行わない（憲章準拠）」要件に違反していないか？ [Critical, Code Line 84-85 vs Spec §FR-038b]
- [ ] CHK008 - doc_update.py:54のtransformed_contentパラメータ定義（`Path | None = typer.Option(None, ...)`）は、FR-038eの「必須パラメータ（`typer.Option(...)`）として定義されなければならない」要件に違反していないか？ [Critical, Code Line 54 vs Spec §FR-038e]
- [ ] CHK009 - Session 2025-10-17 Q2の決定「Option A - プロセスを完全に中断（厳格なエラーハンドリング）」理由「(1) 憲章の『Primary Data Non-Assumption Principle』に完全準拠」は、実装コードで保証されているか？ [Critical, Spec §Session 2025-10-17 Q2]

## Requirement Consistency - 仕様とコード実装の整合性

- [ ] CHK010 - doc_update.pyのパラメータヘルプテキスト「FR-038e: REQUIRED」は、実際のパラメータ定義（必須 vs オプショナル）と一致しているか？ [High, Code Line 55 vs Line 54]
- [ ] CHK011 - feature_page.py:75-85のコメント「T072, FR-038g」は正しい仕様参照か？FR-038gは`--quick`フラグに関する要件であり、フォールバック動作を正当化する根拠ではないのではないか？ [High, Code Comment vs Spec §FR-038g]
- [ ] CHK012 - CLAUDE.mdの「FR-038e: transformed_contentパラメータを必須化（doc_update.py）」記載は、実際のdoc_update.py実装と一致しているか？ [High, CLAUDE.md Line 109 vs Code]
- [ ] CHK013 - 仕様（Session 2025-10-16）で「LLM変換をデフォルトの挙動にすべきか？ → A: Yes - LLM変換を常に有効化する」と決定されたにもかかわらず、フォールバック処理が実装されているのは矛盾していないか？ [Critical, Spec §Session 2025-10-16 vs Code]

## Acceptance Criteria Quality - 受入基準の実装

- [ ] CHK014 - SC-023「LLM変換失敗時、100%のケースで明確なエラーメッセージが表示され、プロセスが中断される。フォールバック動作は行わない（憲章準拠）」は、現在の実装で100%保証されているか？ [Critical, Spec §SC-023]
- [ ] CHK015 - AC-003「LLM変換が失敗した場合、エラーメッセージが明確に表示され、プロセス全体が中断される。他の機能の処理も行わず、フォールバック動作も行わない」は、実装で満たされているか？ [Critical, Spec §AC-003 (Example 3)]
- [ ] CHK016 - SC-023bで定義された4つの品質チェック（空文字列、50文字未満、エラーパターン、Markdown構文エラー）が不正コンテンツを検出した場合、100%のケースでプロセスが中断される要件は実装されているか？ [High, Spec §SC-023b]

## Scenario Coverage - エラーハンドリングシナリオ

- [ ] CHK017 - transformed_contentパラメータが未提供の場合のエラーハンドリングシナリオは、実装に存在するか？（doc_update.py:70-77参照） [High, Code Line 70-77 vs Spec §FR-038e]
- [ ] CHK018 - LLM変換が完全に失敗した場合（anthropic APIエラー等）のエラーハンドリング要件は、コマンドテンプレートまたはllm_transform.pyで定義されているか？ [High, Gap]
- [ ] CHK019 - README.md/QUICKSTART.md不整合検出失敗時（FR-038-integ-a）のエラーハンドリング要件は、仕様通りに「プロセス全体を中断」する実装になっているか？ [High, Spec §FR-038-integ-a]
- [ ] CHK020 - セクション優先順位判定失敗時（FR-038-integ-b）のエラーハンドリング要件は、仕様通りに「プロセス全体を中断」する実装になっているか？ [High, Spec §FR-038-integ-b]

## Edge Case Coverage - 境界条件の定義

- [ ] CHK021 - transformed_content JSONファイルが存在しない場合（FileNotFoundError）、doc_update.pyはフォールバックせずにエラーで中断するか？（現在のCode Line 160-161は警告のみで継続している） [High, Code Line 160-161 vs Spec §FR-038b]
- [ ] CHK022 - transformed_content JSONファイルの解析が失敗した場合（JSONDecodeError）、doc_update.pyはフォールバックせずにエラーで中断するか？（現在のCode Line 162-163は警告のみで継続している） [High, Code Line 162-163 vs Spec §FR-038b]
- [ ] CHK023 - transformed_content_map内に特定機能のデータが存在しない場合、feature_page.py:73-85はフォールバック動作（元のファイルコピー）を実行していないか？ [Critical, Code Line 73-85 vs Spec §FR-038b]
- [ ] CHK024 - spec.mdから最小限抽出が失敗した場合（必須セクション欠如）のエラーハンドリング要件「明確なエラーメッセージを表示し、プロセスを中断する」は実装されているか？ [High, Spec §FR-038]

## Non-Functional Requirements - コーディング規約準拠

- [ ] CHK025 - CLAUDE.mdの「エラーハンドリング: すべてのエラーは`SpecKitDocsError`例外として発生させ、エラーメッセージに『ファイルパス』『エラー種類』『推奨アクション』を含める（C002準拠）」要件は、doc_update.py、feature_page.pyで遵守されているか？ [High, CLAUDE.md Line 92]
- [ ] CHK026 - CLAUDE.mdの「DRY原則: 重複実装を避け、既存のユーティリティ、ライブラリ、抽象ベースクラスを確認する」要件は、フォールバック処理の重複実装（feature_page.py:84-85とdoc_update.py:160-163）で違反していないか？ [Medium, CLAUDE.md Line 93]
- [ ] CHK027 - CLAUDE.mdの「TDD必須: 実装前にテストを書き、Red-Green-Refactorサイクルに従う（C010準拠）」要件は、フォールバック処理の実装で遵守されているか？フォールバック処理のテストは存在するか？ [Medium, CLAUDE.md Line 94]

## Dependencies & Assumptions - 依存関係と前提条件

- [ ] CHK028 - feature_page.py:84-85のコメント「T072, FR-038g」は、タスク定義tasks.mdのT072と整合しているか？T072の実際の要件は何か？ [High, Code Comment vs tasks.md]
- [ ] CHK029 - doc_update.py:146-164のLLM変換コンテンツ読み込み処理は、コマンドテンプレート（speckit.doc-update.md）のStep 1「LLM変換実行」が実行されることを前提としているか？前提が満たされない場合の動作は明確か？ [High, Code vs Command Template]
- [ ] CHK030 - FR-038eで定義された「コマンド定義がLLM変換を実行し忘れた場合に即座にエラーで検知できるようにする」目的は、現在のパラメータ定義（Optional）で達成できているか？ [Critical, Spec §FR-038e Purpose]

## Ambiguities & Conflicts - 曖昧さと矛盾

- [ ] CHK031 - feature_page.py:50のdocstringで「Optional mapping of feature directory names to transformed content」と記載されているが、FR-038eの「必須パラメータ」要件と矛盾していないか？ [High, Code Docstring vs Spec §FR-038e]
- [ ] CHK032 - feature_page.py:73の条件判定`if transformed and transformed.get("spec_content")`は、「LLM変換は常に実行される」要件（Session 2025-10-16）と矛盾していないか？ [High, Code Line 73 vs Spec §Session 2025-10-16]
- [ ] CHK033 - doc_update.py:160-163の警告メッセージ「元のコンテンツを使用します」は、FR-038bの「フォールバック動作は行わない」要件と矛盾していないか？ [Critical, Code Line 160-163 vs Spec §FR-038b]
- [ ] CHK034 - Session 2025-10-17 Q1の決定「Option A - `--no-llm-transform`フラグを完全に削除し、LLM変換のみをサポート」に従って、すべてのフォールバック処理も削除されるべきではないか？ [Critical, Spec §Session 2025-10-17 Q1]

## Implementation Consistency - 実装の一貫性

- [ ] CHK035 - doc_update.py:70-77のtransformed_content必須チェックは、実際のパラメータ定義（Line 54: `Path | None`）と一致していないが、この矛盾は意図的か？ [Critical, Code Line 54 vs Line 70-77]
- [ ] CHK036 - feature_page.pyとdoc_update.pyの両方でフォールバック動作が実装されているが、この重複は意図的か？DRY原則に違反していないか？ [Medium, Code Duplication]
- [ ] CHK037 - llm_transform.pyのselect_content_source()関数が存在するにもかかわらず、feature_page.pyでフォールバック処理が実装されているのは、責務分離原則に違反していないか？ [Medium, Architecture Pattern]

## Traceability - トレーサビリティ

- [ ] CHK038 - feature_page.py:84-85のコメント「Use original content (T072, FR-038g)」は、spec.mdで定義された要件と正しくトレースできるか？FR-038gは`--quick`フラグに関する要件であり、フォールバック動作を定義していないのではないか？ [High, Traceability]
- [ ] CHK039 - doc_update.py:54のヘルプテキスト「FR-038e: REQUIRED」は、FR-038eの要件「必須パラメータ（`typer.Option(...)`）として定義されなければならない」と整合しているか？ [High, Traceability]
- [ ] CHK040 - CLAUDE.mdの「FR-038e: transformed_contentパラメータを必須化（doc_update.py）」記載は、実装が完了していることを示しているが、実際のコードは未完了ではないか？ [Critical, Documentation vs Code]

---

**Summary**: 40項目（CRITICAL: 17, HIGH: 21, MEDIUM: 2）

**Focus Areas**:
- FR-038シリーズ（LLM変換機能）の仕様準拠
- 憲章原則「Primary Data Non-Assumption」の遵守
- フォールバック動作の完全排除

**Key Findings**:
- フォールバック処理（feature_page.py:84-85, doc_update.py:160-163）が憲章違反の可能性
- transformed_contentパラメータの定義が仕様（必須）と実装（Optional）で不一致
- エラーハンドリング戦略が「プロセス全体中断」ではなく「警告で継続」になっている箇所が複数存在
