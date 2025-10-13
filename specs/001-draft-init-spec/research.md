# Research: spec-kit-docs技術選択

**Feature**: spec-kit-docs - AI駆動型ドキュメント生成システム
**Date**: 2025-10-12 (初版), 2025-10-13 (更新)
**Phase**: 0 - Research & Technical Decisions

## Overview

この研究文書は、spec-kit-docs実装における主要な技術的決定とその根拠を記録します。

**更新内容（2025-10-13）**:
- specify-cliからの機能再利用に関する詳細調査を追加
- importlib.resourcesの使用パターンを追加
- Git diffとGitPythonの実装詳細を追加
- インタラクティブ確認パターンの実装例を追加

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

## 11. specify-cliからの機能再利用（2025-10-13追加）

### Decision
specify-cliをGit URL依存として参照し、**StepTrackerクラス**と**consoleモジュール**を再利用する。

### Rationale
1. **統一UX**: spec-kit本家と同じCLI UIを提供
2. **保守コスト削減**: プログレストラッカーを独自実装する必要なし
3. **Richベース**: 既にRichライブラリを活用した洗練されたUI実装
4. **エコシステム統合**: spec-kitプロジェクト間での一貫性

### Alternatives Considered
- **独自実装**: 保守コスト増加、一貫性の欠如
- **tqdm**: シンプルだが、Richベースの洗練されたUIには劣る
- **単純なprint**: UXの低下

### Implementation Notes

#### pyproject.tomlでのGit URL依存（PEP 440準拠）
```toml
[project]
dependencies = [
    "specify-cli @ git+https://github.com/github/spec-kit.git@main#subdirectory=src/specify_cli"
]

[tool.hatch.metadata]
allow-direct-references = true
```

**注意**: Hatchビルドバックエンドを使用する場合、`allow-direct-references = true`の設定が必須。

#### StepTrackerの使用パターン
```python
from specify_cli import StepTracker, console
from rich.live import Live

# ステップトラッカーの初期化
tracker = StepTracker("Initialize Documentation Project")

# ステップの追加（pending状態で）
tracker.add("scan", "Scan features")
tracker.add("structure", "Determine structure")
tracker.add("init", "Initialize project")

# Live UIとの統合
with Live(tracker.render(), console=console, refresh_per_second=8, transient=True) as live:
    tracker.attach_refresh(lambda: live.update(tracker.render()))

    # 処理の開始
    tracker.start("scan", "scanning specs/ directory")
    # ... 処理 ...
    tracker.complete("scan", "5 features found")

    # エラー処理
    try:
        # ... 処理 ...
        tracker.complete("init", "project ready")
    except Exception as e:
        tracker.error("init", str(e))

# Live終了後、最終状態を表示
console.print(tracker.render())
```

#### インタラクティブ確認パターン（specify init --here参考）

**参照**: `/home/driller/repo/spec-kit/src/specify_cli/__init__.py` 行844-854

```python
import typer
from rich.console import Console

console = Console()

def doc_init(
    force: bool = typer.Option(False, "--force", help="Skip confirmation"),
):
    docs_dir = Path("docs")

    if docs_dir.exists():
        console.print(f"[yellow]Warning:[/yellow] docs/ already exists")

        if force:
            console.print("[cyan]--force supplied: skipping confirmation[/cyan]")
        else:
            response = typer.confirm("Do you want to continue?")
            if not response:
                console.print("[yellow]Operation cancelled[/yellow]")
                raise typer.Exit(0)
```

**フラグの優先順位**: `--force` > interactive prompt > `--no-interaction` (default: abort)

### References
- `/home/driller/repo/spec-kit/src/specify_cli/__init__.py`
- Python Packaging Guide: Writing pyproject.toml (2025)
- Typer Documentation: Ask with Prompt (2025)

---

## 12. importlib.resourcesの使用パターン（2025-10-13追加）

### Decision
Python 3.11+の**importlib.resources.files()** APIを使用してパッケージ内テンプレートにアクセス。

### Rationale
1. **非推奨API回避**: `read_binary()`/`read_text()`はPython 3.11で非推奨
2. **統一インターフェース**: Traversableインターフェースで一貫性
3. **zipファイル対応**: パッケージがzipファイルとしてインストールされても動作
4. **パフォーマンス**: pkg_resourcesよりもオーバーヘッドが少ない

### Alternatives Considered
- **pkg_resources**: 非推奨、パフォーマンス問題
- **__file__ベースのパス操作**: zipインストールに非対応

### Implementation Notes

#### テンプレートファイルの読み取り
```python
from importlib.resources import files

# テキストファイルの読み取り
template_content = files('speckit_docs.templates.sphinx').joinpath('conf.py.j2').read_text()

# バイナリファイルの読み取り
data = files('speckit_docs').joinpath('data.bin').read_bytes()
```

#### テンプレートのコピー（ファイルシステムパスが必要な場合）
```python
from importlib.resources import files, as_file
import shutil

# as_file()コンテキストマネージャで実際のファイルパスを取得
source = files('speckit_docs.templates.sphinx').joinpath('Makefile.j2')
with as_file(source) as template_path:
    shutil.copy(template_path, '/destination/path')
```

#### Jinja2との統合（現在の実装）

**現在の実装**:
```python
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

# 開発時: __file__ベースのパス（エディタサポート、デバッグ容易）
template_dir = Path(__file__).parent.parent / "templates" / "sphinx"
jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))
```

**推奨実装（将来的な移行先）**:
```python
from jinja2 import Environment, PackageLoader

# PackageLoaderを使用（zipインストール対応）
jinja_env = Environment(loader=PackageLoader('speckit_docs', 'templates/sphinx'))
```

#### 実装のトレードオフ

| アプローチ | メリット | デメリット |
|-----------|---------|-----------|
| FileSystemLoader + `__file__` | エディタでジャンプ可能、デバッグ容易 | zipインストール非対応 |
| PackageLoader | zipインストール対応、適切なリソース管理 | エディタの補完が効かない場合がある |

**現状**: Phase 1ではFileSystemLoaderを使用。Phase 2でPackageLoaderへの移行を検討。

### References
- Python 3.11 Documentation: importlib.resources
- importlib-resources 6.5.3 Documentation
- Jinja2 Documentation: PackageLoader

---

## 13. Git diffを使用したインクリメンタル更新の詳細（2025-10-13追加）

### Decision
**GitPython**ライブラリを使用してGit diff経由で変更検出を実装（既に実装済み）。

### Rationale
1. **Pythonicなインターフェース**: subprocess実行よりも型安全で扱いやすい
2. **構造化アクセス**: diff情報へのプログラマティックなアクセス（change_type、a_path、b_path）
3. **spec-kitの前提**: プロジェクトは必ずGitリポジトリである
4. **既存実装**: `/home/driller/repo/spec-kit-docs/src/speckit_docs/utils/git.py`が存在

### Alternatives Considered
- **subprocess + git diff**: パース困難、エラー処理複雑
- **ファイルmtimeベース**: Git historyを無視、不正確
- **ハッシュキャッシュ**: 追加の管理コスト

### Implementation Notes

#### GitPythonでの変更ファイル検出パターン

```python
from git import Repo
from pathlib import Path

repo = Repo('/path/to/repo')

# 1. Unstagedの変更（Working Directory vs Index）
unstaged_changes = [item.a_path for item in repo.index.diff(None)]

# 2. Stagedの変更（Index vs HEAD）
staged_changes = [item.b_path for item in repo.index.diff("HEAD")]

# 3. コミット間の差分（HEAD~1 vs HEAD）
diff_index = repo.commit("HEAD~1").diff("HEAD")
changed_files = [item.b_path or item.a_path for item in diff_index]

# 4. パスフィルタ適用（specs/ディレクトリのみ）
specs_dir = Path(repo.working_dir) / "specs"
for diff_item in diff_index:
    file_path = diff_item.b_path or diff_item.a_path
    full_path = Path(repo.working_dir) / file_path
    if str(full_path).startswith(str(specs_dir)):
        # Process changed spec file
        pass
```

#### spec-kit-docs実装（既存コード）

**ChangeDetectorクラスの使用例**:
```python
from speckit_docs.utils.git import ChangeDetector

detector = ChangeDetector()

# 変更された機能を取得（spec.mdが変更されたもの）
changed_features = detector.get_changed_features(
    base_ref="HEAD~1",
    target_ref="HEAD"
)

# 変更があるかチェック
has_changes = detector.has_changes()
```

**実装の詳細**（`/home/driller/repo/spec-kit-docs/src/speckit_docs/utils/git.py`）:
- `GitRepository.get_changed_files()`: Git diff経由でファイルリスト取得
- `GitRepository.get_changed_spec_files()`: `specs/`配下の`spec.md`をフィルタ
- `ChangeDetector.get_changed_features()`: 変更されたFeatureオブジェクトを返す

#### エラー処理（初回コミットケース）

```python
try:
    changed_features = detector.get_changed_features()
except GitValidationError as e:
    print(f"エラー: {e.message}")
    print(f"提案: {e.suggestion}")
    # 初回コミット（HEAD~1が存在しない）の場合、全機能を更新
    if "HEAD~1" in str(e):
        scanner = FeatureScanner()
        changed_features = scanner.scan(require_spec=True)
```

### References
- GitPython Tutorial Documentation (3.1.45)
- Stack Overflow: Get changed files using gitpython (2025)
- `/home/driller/repo/spec-kit-docs/src/speckit_docs/utils/git.py`

---

## 14. Sphinx + myst-parserの詳細設定（2025-10-13更新）

### MyST拡張機能の完全リスト

MyST Parserが提供する拡張機能（デフォルトでは無効）:

- `amsmath` - LaTeX数式のAMSmath環境
- `attrs_inline` - インライン属性構文 `{#id .class}`
- `colon_fence` - コロンフェンス構文 `:::`
- `deflist` - 定義リスト
- `dollarmath` - ドル記号数式 `$...$`, `$$...$$`
- `fieldlist` - フィールドリスト
- `html_admonition` - HTML形式のadmonition
- `html_image` - HTML形式の画像タグ
- `linkify` - URLの自動リンク化
- `replacements` - 自動置換（em-dash、省略記号など）
- `smartquotes` - スマート引用符
- `strikethrough` - 打ち消し線 `~~text~~`
- `substitution` - 置換変数
- `tasklist` - タスクリスト `- [ ]`, `- [x]`

### conf.pyの完全設定例

```python
# 拡張機能の有効化
extensions = [
    'myst_parser',              # MyST Markdown support
    'sphinx.ext.autodoc',       # API documentation
    'sphinx.ext.viewcode',      # Source code links
    'sphinx.ext.napoleon',      # Google/NumPy docstring support
]

# ソースファイルの設定
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# MyST Markdown拡張機能
myst_enable_extensions = [
    "colon_fence",              # ::: fence for directives
    "deflist",                  # Definition lists
    "tasklist",                 # - [ ] task lists
    "attrs_inline",             # {#id .class} attributes
]
```

### References
- Sphinx Documentation: Markdown Support (2025)
- MyST Parser Documentation: Configuration (2025)
- MyST Parser Documentation: Syntax Extensions

---

## 15. MkDocs navの動的生成アプローチ（2025-10-13追加）

### アプローチ比較

| アプローチ | 実装難易度 | 柔軟性 | メンテナンス |
|-----------|-----------|-------|-------------|
| ビルトイン自動生成 | ⭐ | ⭐⭐ | ⭐⭐⭐ |
| Jinja2テンプレート | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| mkdocs-literate-nav | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| mkdocs-gen-files | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ |

### spec-kit-docs実装方針

**Phase 1（現在）**: Jinja2テンプレートで静的にnavを生成

```python
# GeneratorConfigにfeatures情報を含める
template = jinja_env.get_template("mkdocs.yml.j2")
config_content = template.render(
    site_name=config.site_name,
    repo_url=config.repo_url,
    features=features,  # Feature[]のリスト
)
```

**Phase 2（将来的）**: mkdocs-literate-navプラグインのサポート追加
**Phase 3（将来的）**: mkdocs-gen-filesでのビルド時動的生成

### References
- MkDocs Documentation: Configuration (2025)
- mkdocs-literate-nav Plugin (v0.6.2, 2025-03-18)
- mkdocs-gen-files Documentation

---

## Summary

| Decision Area | Choice | Key Reason |
|--------------|--------|------------|
| Sphinx形式 | Markdown + myst-parser | フォーマット統一、学習コスト削減 |
| 変更検出 | Git diff (GitPython) | spec-kitワークフローとの整合 |
| アーキテクチャ | Strategy Pattern | 拡張性、保守性 |
| ディレクトリ構造 | 動的決定（5機能閾値） | スケーラビリティ、UX |
| Markdown解析 | markdown-it-py | MyST互換性 |
| テンプレート | Jinja2 | Python標準、機能性 |
| CLI | argparse | 標準ライブラリ、シンプル |
| CLI UI（将来） | specify-cli (StepTracker) | 統一UX、保守コスト削減 |
| パッケージリソース | importlib.resources | Python 3.11+標準、zip対応 |
| エラーハンドリング | 明確なメッセージ + 提案 | UX、要件対応 |
| パフォーマンス | インクリメンタル更新 | 十分、シンプル |
| パッケージ管理 | pyproject.toml + uv | モダン、高速 |

---

## 実装フェーズ別の技術スタック

### Phase 1 (MVP) - 実装済み
- ✅ Jinja2テンプレート（FileSystemLoader + __file__）
- ✅ Sphinx + myst-parser設定
- ✅ MkDocs基本設定
- ✅ GitPythonでの変更検出
- ✅ インタラクティブ確認（input()ベース）
- ✅ argparse CLI

### Phase 2 - 次期リリース候補
- ⏳ specify-cliからStepTracker/console再利用（Git URL依存）
- ⏳ typer.confirm()統合
- ⏳ importlib.resources移行（PackageLoader）
- ⏳ mkdocs-literate-navプラグインサポート

### Phase 3 - 将来的な拡張
- 📋 mkdocs-gen-filesでの動的nav生成
- 📋 zipインストール対応の完全実装
- 📋 並列処理最適化（50機能以上）

---

## Next Steps

Phase 1に進み、以下を生成：
1. **data-model.md**: 主要エンティティの定義
2. **contracts/**: CLIインターフェース仕様
3. **quickstart.md**: インストールと基本使用方法
