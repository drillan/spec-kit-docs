# Research: spec-kit-docs技術選択

**Feature**: spec-kit-docs - AI駆動型ドキュメント生成システム
**Date**: 2025-10-12
**Phase**: 0 - Research & Technical Decisions

## Overview

この研究文書は、spec-kit-docs実装における主要な技術的決定とその根拠を記録します。

## 1. ドキュメント形式の選択：Markdown + myst-parser

### Decision
SphinxプロジェクトでreStructuredText (.rst)ではなく**Markdown (.md) + myst-parser**をデフォルト形式とする。

### Rationale
1. **フォーマット統一**: spec-kitの全ソースファイル（spec.md, plan.md, tasks.md）がMarkdownであり、形式を統一することで変換ロジックが不要
2. **学習コスト削減**: reStructuredText構文の習得が不要。ユーザーはMarkdownのみを学習すれば良い
3. **手動編集の利便性**: 生成後のドキュメントをユーザーが手動編集する際、Markdownの方が圧倒的に編集しやすい
4. **業界標準**: MyST Markdownは業界標準となりつつあり、Jupyter Book等で広く採用されている
5. **Sphinx機能のサポート**: myst-parserはSphinxのほぼ全機能（アドモニション、toctree等）をサポート

### Alternatives Considered
- **reStructuredText**: Sphinxのネイティブフォーマットだが、spec.mdからの変換が必要、学習コストが高い
- **Pandocで変換**: Markdown→rST変換は可能だが、追加依存関係と変換エラーのリスク

### Implementation Notes
- `conf.py`に`myst_parser`拡張を追加
- `source_suffix`に`.md`を含める
- MyST拡張機能（colon_fence、deflist、tasklist、attrs_inline）を有効化

---

## 2. 変更検出方法：Git diff

### Decision
インクリメンタル更新での変更検出に**Git diff**を使用（ファイルタイムスタンプやハッシュではなく）。

### Rationale
1. **spec-kitワークフローとの整合**: spec-kitプロジェクトは既にGitリポジトリであることが前提
2. **信頼性**: ファイルを開いただけでタイムスタンプが変更されることがない
3. **差分の可視化**: 何が変更されたかを正確に追跡できる
4. **シンプル**: 別途キャッシュファイルを管理する必要がない

### Alternatives Considered
- **ファイルタイムスタンプ**: ファイルを開いただけで変更として検出される可能性
- **ハッシュ（MD5/SHA256）**: 追加の計算コストとキャッシュファイル管理が必要
- **キャッシュファイル**: 前回処理内容の保存が必要、管理複雑

### Implementation Notes
- `GitPython`ライブラリを使用
- `git diff --name-only HEAD~1 HEAD`で変更ファイルを検出
- `.specify/specs/`配下の変更のみをフィルタリング

---

## 3. アーキテクチャパターン：Strategy Pattern (Generator)

### Decision
Sphinx/MkDocsの実装に**Strategy Pattern**を使用。共通インターフェース（`BaseGenerator`）を定義し、各ツール固有の実装を分離。

### Rationale
1. **拡張性**: 将来的にDocusaurus、VitePressなどの追加が容易
2. **テスタビリティ**: 各ジェネレーターを独立してテスト可能
3. **保守性**: Sphinx/MkDocsの変更が他方に影響しない
4. **SOLID原則**: Open/Closed Principle（拡張に開いて、修正に閉じている）

### Alternatives Considered
- **if/elseで分岐**: シンプルだが、3つ目のツール追加時に複雑化
- **プラグインシステム**: 過剰設計、現時点では不要

### Implementation Notes
```python
class BaseGenerator(ABC):
    @abstractmethod
    def init_project(self, config: Dict) -> None: pass

    @abstractmethod
    def update_docs(self, features: List[Feature]) -> None: pass

    @abstractmethod
    def validate_project(self) -> bool: pass

class SphinxGenerator(BaseGenerator): ...
class MkDocsGenerator(BaseGenerator): ...
```

---

## 4. ディレクトリ構造の動的決定

### Decision
機能数に基づいて**動的にディレクトリ構造を決定**：
- 5機能以下：フラット構造（`docs/` 直下）
- 6機能以上：包括的構造（`docs/features/`, `docs/guides/`, etc.）

### Rationale
1. **スケーラビリティ**: 小規模プロジェクトはシンプル、大規模プロジェクトは整理された構造
2. **ユーザー体験**: 少数の機能で過剰な階層は不要
3. **柔軟性**: プロジェクトの成長に応じて自動的に最適な構造を提供

### Alternatives Considered
- **常にフラット**: 大規模プロジェクトで管理困難
- **常に階層構造**: 小規模プロジェクトで過剰
- **ユーザーに選択させる**: 追加の意思決定負担

### Implementation Notes
```python
def determine_structure(feature_count: int) -> str:
    return "flat" if feature_count <= 5 else "comprehensive"
```

---

## 5. Markdown解析ライブラリ：markdown-it-py

### Decision
**markdown-it-py**を使用してMarkdownを解析（`python-markdown`ではなく）。

### Rationale
1. **MyST互換性**: MyST Markdownとの互換性が高い
2. **拡張性**: プラグインシステムで拡張機能を追加可能
3. **パフォーマンス**: CommonMarkに準拠し、高速
4. **メンテナンス**: 活発に開発されている

### Alternatives Considered
- **python-markdown**: 拡張機能が豊富だが、MyST構文との互換性が低い
- **mistune**: 軽量だが、プラグインシステムが弱い
- **正規表現で独自実装**: 保守困難、エッジケース対応が不十分

### Implementation Notes
- セクション見出しの抽出
- リスト、テーブル、コードブロックの構造化
- MyST固有のディレクティブ（` ```{note}`等）のサポート

---

## 6. テンプレートエンジン：Jinja2

### Decision
**Jinja2**を使用して設定ファイルとドキュメントファイルを生成。

### Rationale
1. **Pythonエコシステム標準**: 広く使用されている
2. **可読性**: テンプレート構文が明確
3. **機能性**: 条件分岐、ループ、フィルター等が豊富
4. **セキュリティ**: 自動エスケープ機能

### Alternatives Considered
- **f-string**: シンプルだが、複雑なロジックには不向き
- **string.Template**: 機能が限定的
- **独自テンプレート**: 車輪の再発明

### Implementation Notes
- `templates/sphinx/conf.py.j2`: Sphinx設定テンプレート
- `templates/mkdocs/mkdocs.yml.j2`: MkDocs設定テンプレート
- 変数: `project_name`, `author`, `version`, `features`

---

## 7. CLI インターフェース：argparse

### Decision
**argparse**（標準ライブラリ）を使用してCLIインターフェースを実装。

### Rationale
1. **標準ライブラリ**: 追加依存なし
2. **十分な機能**: サブコマンド、オプション、ヘルプ生成
3. **シンプル**: 過剰な機能なし

### Alternatives Considered
- **Click**: 人気だが、追加依存が発生
- **Typer**: モダンだが、追加依存が発生
- **docopt**: 宣言的だが、柔軟性に欠ける

### Implementation Notes
```python
parser = argparse.ArgumentParser(description='spec-kit-docs')
subparsers = parser.add_subparsers(dest='command')

# doc-init
init_parser = subparsers.add_parser('doc-init')
init_parser.add_argument('--type', choices=['sphinx', 'mkdocs'])

# doc-update
update_parser = subparsers.add_parser('doc-update')
```

---

## 8. エラーハンドリング戦略

### Decision
**明確なエラーメッセージ + 次のステップ提案**のパターンを採用。

### Rationale
1. **ユーザー体験**: エラーの原因と解決方法が明確
2. **要件**: FR-033で明確なエラーメッセージが要件
3. **デバッグ容易性**: エラーログにコンテキスト情報を含める

### Implementation Notes
```python
class SpecKitDocsError(Exception):
    def __init__(self, message: str, suggestion: str):
        self.message = message
        self.suggestion = suggestion
        super().__init__(f"{message}\n\n💡 Suggestion: {suggestion}")

# Usage
if not Path('.specify').exists():
    raise SpecKitDocsError(
        "spec-kitプロジェクトではありません。",
        "最初に 'specify init' を実行してください。"
    )
```

---

## 9. パフォーマンス最適化戦略

### Decision
- **インクリメンタル更新**: Git diffで変更ファイルのみ再処理
- **並列処理は不要**: 典型的なプロジェクト（1-20機能）では逐次処理で十分

### Rationale
1. **成功基準**: SC-006で45秒以内（10機能）が目標、並列化なしで達成可能
2. **シンプル**: マルチプロセス/スレッドの複雑さを回避
3. **I/O バウンド**: ファイル読み書きが主なので、並列化の恩恵が少ない

### Alternatives Considered
- **concurrent.futures**: 50機能以上で検討
- **async/await**: I/Oバウンドだが、現時点では過剰

### Implementation Notes
- Git diffで変更されたfeatureのみを処理
- 50機能以上の場合は進行状況表示（`tqdm`等）

---

## 10. パッケージ管理：pyproject.toml + uv

### Decision
**pyproject.toml**（PEP 621）でパッケージメタデータを定義し、**uv**で依存関係を管理。

### Rationale
1. **モダンスタンダード**: setup.pyの後継、Python 3.11+推奨
2. **統一設定**: ビルド、依存関係、ツール設定を1ファイルで管理
3. **高速**: uvは高速な依存関係解決

### Implementation Notes
```toml
[project]
name = "speckit-docs"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "sphinx>=7.0",
    "myst-parser>=2.0",
    "mkdocs>=1.5",
    "markdown-it-py>=3.0",
    "GitPython>=3.1",
    "Jinja2>=3.1",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-cov", "black", "ruff"]
```

---

## Summary

| Decision Area | Choice | Key Reason |
|--------------|--------|------------|
| Sphinx形式 | Markdown + myst-parser | フォーマット統一、学習コスト削減 |
| 変更検出 | Git diff | spec-kitワークフローとの整合 |
| アーキテクチャ | Strategy Pattern | 拡張性、保守性 |
| ディレクトリ構造 | 動的決定（5機能閾値） | スケーラビリティ、UX |
| Markdown解析 | markdown-it-py | MyST互換性 |
| テンプレート | Jinja2 | Python標準、機能性 |
| CLI | argparse | 標準ライブラリ、シンプル |
| エラーハンドリング | 明確なメッセージ + 提案 | UX、要件対応 |
| パフォーマンス | インクリメンタル更新 | 十分、シンプル |
| パッケージ管理 | pyproject.toml + uv | モダン、高速 |

---

## Next Steps

Phase 1に進み、以下を生成：
1. **data-model.md**: 主要エンティティの定義
2. **contracts/**: CLIインターフェース仕様
3. **quickstart.md**: インストールと基本使用方法
