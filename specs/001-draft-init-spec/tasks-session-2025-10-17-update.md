# Tasks Update: Session 2025-10-17 Content Filtering Strategy

**Session Date**: 2025-10-17
**Decision**: Session 2025-10-17 (Content Filtering Strategy) - plan.md と tasks.md をエンドユーザー向けドキュメントから除外

## 新しいタスク（Session 2025-10-17対応）

以下のタスクを既存のtasks.mdに追加する必要があります:

### Phase 7: Polish & Cross-Cutting Concerns (Session 2025-10-17追加)

**Purpose**: Session 2025-10-17 Content Filtering Strategy対応

- [ ] T085 [P] [Session-2025-10-17] テンプレート修正: src/speckit_docs/templates/feature-page.md.jinja2から`{% if plan_content %}`ブロックと`{% if tasks_content %}`ブロックを完全に削除し、Feature Filesセクションのみ保持（元の仕様書へのリンク提供）
- [ ] T086 [P] [Session-2025-10-17] FeaturePageGenerator修正: src/speckit_docs/generators/feature_page.pyの`generate_pages()`メソッド内で`plan_doc = None`、`tasks_doc = None`を設定し、plan.md/tasks.mdの読み込みを完全にスキップ（87-111行目を修正）
- [ ] T087 [P] [Session-2025-10-17] DocumentGenerator修正: src/speckit_docs/generators/document.pyの`generate_feature_page()`メソッドで、plan_doc/tasks_docパラメータがNoneの場合でもエラーにならないことを確認
- [ ] T088 [P] [Session-2025-10-17] 契約テスト更新: tests/contract/test_doc_update_command.pyに「生成されたドキュメントにplan.mdとtasks.mdの内容が含まれないことを確認」テストを追加
- [ ] T089 [P] [Session-2025-10-17] 統合テスト更新: tests/integration/test_sphinx_generation.pyとtest_mkdocs_generation.pyに「plan.md/tasks.mdの技術的詳細が含まれていない」assertion追加
- [ ] T090 [P] [Session-2025-10-17] 受け入れシナリオ検証: User Story 2の新しい受け入れシナリオ（LLM変換済みコンテンツ含む、plan.md/tasks.md除外）が満たされることを検証

## 実装の優先順位

| タスク | 優先度 | 実装難易度 | 効果 |
|--------|--------|------------|------|
| T085 | P0（最優先） | 低 | 即座に問題を解決 |
| T086 | P0（最優先） | 低 | パフォーマンス改善 |
| T087 | P1 | 低 | エラーハンドリング |
| T088 | P1 | 中 | 品質保証 |
| T089 | P1 | 中 | 品質保証 |
| T090 | P2 | 中 | 仕様準拠確認 |

## 実装の詳細

### T085: テンプレート修正

**ファイル**: `src/speckit_docs/templates/feature-page.md.jinja2`

**変更前**（22-46行目）:
```jinja2
{% if plan_content %}
## Implementation Plan
{{ plan_content }}
---
{% else %}
> **Note**: Implementation plan (plan.md) is not yet available for this feature.
---
{% endif %}

{% if tasks_content %}
## Implementation Tasks
{{ tasks_content }}
---
{% else %}
> **Note**: Implementation tasks (tasks.md) have not been generated for this feature yet.
---
{% endif %}
```

**変更後**:
```jinja2
{# FR-XXX: plan.md and tasks.md are excluded from end-user documentation #}
{# Developer-facing information is available via the original spec files linked below #}
```

### T086: FeaturePageGenerator修正

**ファイル**: `src/speckit_docs/generators/feature_page.py`

**変更箇所**: `generate_pages` メソッド（87-111行目）

**変更前**:
```python
# Parse plan.md (optional, FR-016) with LLM-transformed content if available
if transformed and transformed.get("plan_content") and feature.plan_file:
    plan_doc = Document(...)
elif feature.plan_file and feature.plan_file.exists():
    plan_doc = self._parse_document(feature.plan_file, DocumentType.PLAN)
else:
    plan_doc = None

# Parse tasks.md (optional, FR-017) with LLM-transformed content if available
if transformed and transformed.get("tasks_content") and feature.tasks_file:
    tasks_doc = Document(...)
elif feature.tasks_file and feature.tasks_file.exists():
    tasks_doc = self._parse_document(feature.tasks_file, DocumentType.TASKS)
else:
    tasks_doc = None
```

**変更後**:
```python
# Session 2025-10-17: plan.md and tasks.md are excluded from end-user documentation
# FR-016 (deleted), FR-017 (deleted): Developer-facing information is available
# via links in the Feature Files section
plan_doc = None
tasks_doc = None
```

### T088: 契約テスト追加

**ファイル**: `tests/contract/test_doc_update_command.py`

**追加テスト**:
```python
def test_generated_doc_excludes_plan_and_tasks():
    """生成されたドキュメントに plan.md と tasks.md の内容が含まれないことを確認

    Session 2025-10-17 Content Filtering Strategy対応
    """
    # Setup: plan.md と tasks.md を含む機能を作成
    # Execute: /speckit.doc-update を実行
    # Assert:
    #   - "## Implementation Plan" が存在しない
    #   - "## Implementation Tasks" が存在しない
    #   - plan.md の固有文字列（例: "Phase 0", "Constitution Check"）が存在しない
    #   - tasks.md の固有文字列（例: "T001", "Checkpoint"）が存在しない
    #   - "## Feature Files" セクションは存在する
    #   - spec.md/plan.md/tasks.mdへのリンクが存在する
```

## 移行計画

### 既存ドキュメントへの影響

**変更内容**:
- 次回の `/speckit.doc-update` 実行時、既存のドキュメントから "Implementation Plan" と "Implementation Tasks" セクションが**削除**される

**対策**:
- これは**意図した動作**（エンドユーザー向けドキュメントから開発者向け情報を除外）
- 開発者向けには元の spec.md / plan.md / tasks.md へのアクセスを保証（Feature Filesセクション経由）

## 検証基準

T085-T090完了後、以下を検証:

1. ✅ 生成されたドキュメントに "## Implementation Plan" セクションが存在しない
2. ✅ 生成されたドキュメントに "## Implementation Tasks" セクションが存在しない
3. ✅ "## Feature Files" セクションが存在し、spec.md/plan.md/tasks.mdへのリンクが含まれる
4. ✅ LLM変換済みのユーザーフレンドリーなコンテンツ（機能の目的、使い方、価値）が含まれる
5. ✅ 契約テストと統合テストが全てパスする
