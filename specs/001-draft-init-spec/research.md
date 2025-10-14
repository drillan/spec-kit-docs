# Research: spec-kit-docs

**作成日**: 2025-10-13
**機能**: 001-draft-init-spec
**フェーズ**: Phase 0 - Research

## Overview

本調査は、spec-kit-docs機能の実装計画（plan.md）を策定する前に、技術的決定事項について業界標準とベストプラクティスを調査し、Constitution（憲章）の原則に沿った理想的な設計アプローチを明確にすることを目的としています。

調査対象:
- Python CLI Tool Distribution（パッケージング、typer選択）
- Template System Design（Jinja2、importlib.resources）
- Sphinx MyST Integration（MyST Markdown構文、conf.py設定）
- MkDocs Configuration（Material theme、nav構造）
- Git Change Detection（git diff戦略、インクリメンタル更新）
- spec-kit Integration Pattern（本家spec-kitのパターン分析）
- Testing Strategy（TDD、pytest、カバレッジ目標）

---

## R001: Python CLI Tool Distribution

### 調査内容

- **pyproject.toml + src-layout**: Pythonパッケージング業界標準（2025年現在）
- **Typer CLI Framework**: 本家spec-kitと同じフレームワーク
- **uv tool install**: Git URLからの直接インストール戦略
- **importlib.resources**: テンプレートファイルの配布方法

### Decision

**選択したアプローチ**: Typer + pyproject.toml + src-layout + importlib.resources

### Rationale

#### Typer採用理由

1. **Constitution I準拠（spec-kit Integration First）**: 本家spec-kitがTyperを使用しており、`specify-cli`に依存することで既にTyperが依存ツリーに存在。新たな依存関係追加なし
2. **型ヒントのネイティブサポート**: Python 3.11+の型ヒント（`int`、`str`、`bool`等）を直接使用でき、mypy互換（Constitution C006: 堅牢コード品質に準拠）
3. **DRY原則（Constitution C012）**: 本家spec-kitのTyperパターン（`typer.confirm()`、`typer.Option()`等）を再利用可能
4. **Phase 2計画との整合**: `specify-cli`から`StepTracker`/`console`再利用を計画しており、Typer前提で一貫性を保つ

#### パッケージング戦略

- **src-layout**: 業界標準パターン（`src/speckit_docs/`）でテスト分離を明確化
- **pyproject.toml**: PEP 621準拠のメタデータ定義（setuptools/hatchling使用）
- **entry point**: `[project.scripts]`で`speckit-docs = "speckit_docs.cli:app"`を定義
- **Git URL直接指定**: PyPI公開はMVP範囲外。`uv tool install speckit-docs --from git+https://github.com/drillan/spec-kit-docs.git`で配布（本家spec-kitと一貫）

#### テンプレート配布

- **importlib.resources.files() API（Python 3.9+）**: レガシーAPI（`read_text`、`open_binary`等）ではなく、モダンな`files()`を使用
- **パッケージ内配置**: `src/speckit_docs/commands/`および`src/speckit_docs/scripts/`に配置
- **オフライン動作**: パッケージに含まれるためネットワーク不要（CI/CD環境対応）

### Implementation Example

```python
# pyproject.toml
[project]
name = "speckit-docs"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "typer>=0.9.0",
    "specify-cli @ git+https://github.com/github/spec-kit.git",
    "sphinx>=7.0",
    "myst-parser>=2.0",
    "mkdocs>=1.5",
    "jinja2>=3.1",
    "GitPython>=3.1",
]

[project.scripts]
speckit-docs = "speckit_docs.cli:app"

# src/speckit_docs/cli.py
import typer
from pathlib import Path

app = typer.Typer()

@app.command()
def install(
    force: bool = typer.Option(False, "--force", help="Overwrite existing files"),
):
    """Install spec-kit-docs extension to current spec-kit project."""
    from importlib.resources import files

    # spec-kitプロジェクト検証
    if not Path(".specify").is_dir():
        typer.echo("Error: Not a spec-kit project.")
        raise typer.Exit(code=1)

    # テンプレートコピー
    commands = files('speckit_docs.commands')
    for cmd in ['speckit.doc-init.md', 'speckit.doc-update.md']:
        source = commands.joinpath(cmd).read_text()
        target = Path(".claude/commands") / cmd

        if target.exists() and not force:
            if not typer.confirm(f"{cmd} exists. Overwrite?"):
                continue

        target.write_text(source)
        typer.echo(f"✓ Installed {cmd}")
```

### Alternatives Considered

- **argparse**: Python標準ライブラリだが、型ヒントサポートが弱く、本家spec-kitとの一貫性がない（却下理由: Constitution I違反）
- **Click**: Typerの基盤ライブラリだが、型ヒント不要。本家spec-kitがTyperを選択した理由（型安全性）と矛盾（却下理由: 一貫性・型安全性）
- **GitHubからのダウンロード方式**: spec-kitが使用するが、大量ファイル配布向け。spec-kit-docsは少数ファイル（2コマンド定義+スクリプト）でimportlib.resourcesが適切（却下理由: 過剰、オフライン動作、パッケージング標準）

### Constitution Alignment

- **C001（ルール遵守）**: 本家spec-kitパターンを歪曲せず忠実に再現
- **C004（理想実装ファースト）**: Typerの型安全性を最初から活用、段階的移行なし
- **C012（DRY原則）**: 本家spec-kitの既存パターンを再利用
- **Core Principle I（spec-kit Integration First）**: 本家spec-kitとの完全一貫性を最優先

---

## R002: Template System Design

### 調査内容

- **Jinja2 Templating Engine**: Pythonエコシステムで業界標準のテンプレートエンジン
- **importlib.resources.files() API**: モダンなパッケージデータアクセス方法
- **Template Organization**: ファイルシステムローダー vs パッケージローダー

### Decision

**選択したアプローチ**: Jinja2 + importlib.resources.files() + PackageLoaderパターン

### Rationale

#### Jinja2採用理由

1. **業界標準**: Sphinx、MkDocs、Flaskなど主要プロジェクトで広く採用
2. **セキュリティ**: XSS攻撃に対する自動エスケープ機能を標準装備
3. **柔軟性**: テンプレート継承、マクロ、フィルター、条件分岐・ループをサポート
4. **ドキュメント生成実績**: Sphinx自身がJinja2を内部使用しており、ドキュメント生成タスクに最適

#### テンプレート配置戦略

```python
from importlib.resources import files
from jinja2 import Environment, PackageLoader

# モダンAPI使用例（Python 3.9+）
templates_path = files('speckit_docs.templates')
conf_py_template = templates_path.joinpath('sphinx_conf.py.j2').read_text()

# Jinja2統合
env = Environment(
    loader=PackageLoader('speckit_docs', 'templates'),
    autoescape=True,  # セキュリティ: 自動エスケープ有効
    trim_blocks=True,
    lstrip_blocks=True
)
template = env.get_template('sphinx/conf.py.j2')
rendered = template.render(
    project_name="My Project",
    author="Author Name",
    version="1.0.0"
)
```

#### テンプレートファイル構造

```
src/speckit_docs/
├── templates/
│   ├── sphinx/
│   │   ├── conf.py.j2
│   │   ├── index.md.j2
│   │   └── Makefile.j2
│   ├── mkdocs/
│   │   ├── mkdocs.yml.j2
│   │   └── index.md.j2
│   └── features/
│       └── feature_page.md.j2
├── commands/
│   ├── speckit.doc-init.md
│   └── speckit.doc-update.md
└── scripts/
    ├── doc_init.py
    └── doc_update.py
```

### Implementation Example

```python
# Jinja2テンプレート例: sphinx/conf.py.j2
project = "{{ project_name }}"
copyright = "{{ year }}, {{ author }}"
author = "{{ author }}"
version = "{{ version }}"

extensions = [
    "myst_parser",
]

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "tasklist",
    "attrs_inline",
]

# Jinja2テンプレート使用例
from jinja2 import Environment, PackageLoader
from datetime import datetime

env = Environment(loader=PackageLoader('speckit_docs', 'templates'))
template = env.get_template('sphinx/conf.py.j2')

conf_content = template.render(
    project_name="spec-kit-docs",
    author="Author Name",
    version="0.1.0",
    year=datetime.now().year
)

(Path("docs") / "conf.py").write_text(conf_content)
```

### Alternatives Considered

- **string.Template**: Python標準だが機能が貧弱。複雑なロジック（条件分岐、ループ）が困難（却下理由: 機能不足）
- **f-strings**: シンプルだがテンプレート外部化が困難。コードとテンプレートの分離原則に反する（却下理由: 保守性低下）
- **Mako**: 高速だがセキュリティリスク。Pythonコード直接埋め込み可能で危険（却下理由: Constitution C006違反）

### Constitution Alignment

- **C006（堅牢コード品質）**: Jinja2の自動エスケープでセキュリティ確保
- **C011（データ正確性）**: テンプレート変数の型安全性をJinja2で検証
- **Core Principle III（Extensibility & Modularity）**: テンプレートを外部化し、新しいドキュメントツール追加を容易化

---

## R003: Sphinx MyST Integration

### 調査内容

- **MyST Markdown**: reStructuredTextの代替として業界標準化しつつあるMarkdown拡張
- **myst-parser**: SphinxでMyST Markdownをサポートする公式拡張
- **Optional Syntax Extensions**: MyST独自の高度な機能（admonitions、toctree等）

### Decision

**選択したアプローチ**: Sphinx + myst-parser + Optional Extensions有効化

### Rationale

#### MyST Markdown採用理由（spec.mdで明確化済み）

1. **spec-kitとの形式統一**: すべてのソースファイル（spec.md、plan.md、tasks.md）がMarkdownであり、変換ロジック不要
2. **学習コスト削減**: reStructuredText構文の習得が不要
3. **手動編集の利便性**: 生成後のドキュメントをユーザーが編集する際の利便性向上
4. **業界標準化**: MyST Markdownは業界標準となりつつあり、Sphinxのほぼ全機能をサポート

#### conf.py設定（理想実装）

```python
# conf.py
project = "{{ project_name }}"
copyright = "{{ year }}, {{ author }}"
author = "{{ author }}"
version = "{{ version }}"
release = "{{ version }}"

# MyST Parser設定
extensions = [
    "myst_parser",
]

# ファイル形式サポート
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# MyST拡張機能有効化
myst_enable_extensions = [
    "colon_fence",    # :::構文でディレクティブ
    "deflist",        # 定義リスト
    "tasklist",       # [ ] チェックボックス
    "attrs_inline",   # {#id .class}属性指定
    "dollarmath",     # $数式$
    "fieldlist",      # :field: value
]

# 見出しアンカー自動生成
myst_heading_anchors = 3  # h1-h3まで自動ID付与

# toctreeの深さ
master_doc = 'index'
```

#### MyST Markdown構文（主要パターン）

```markdown
# MyST Admonition（注記）
:::{note}
これは注記です。欠落ファイルの警告に使用します。
:::

:::{warning}
これは警告です。破壊的変更の通知に使用します。
:::

# MyST toctree（目次）
```{toctree}
:maxdepth: 2
:caption: Features

features/user-auth.md
features/api-integration.md
```

# MyST Cross-reference（相互参照）
{doc}`/features/user-auth` でリンク（拡張子なし）

# MyST Directive（汎用）
```{admonition} カスタムタイトル
:class: tip

カスタムアドモニションの内容
```
```

### Implementation Example

```python
# Sphinx初期化時のconf.py生成
from jinja2 import Environment, PackageLoader
from datetime import datetime

env = Environment(loader=PackageLoader('speckit_docs', 'templates'))
template = env.get_template('sphinx/conf.py.j2')

conf_content = template.render(
    project_name="My Documentation",
    author="Author Name",
    version="1.0.0",
    year=datetime.now().year,
    language="ja"
)

conf_py_path = Path("docs") / "conf.py"
conf_py_path.write_text(conf_content)
```

### Alternatives Considered

- **reStructuredText (.rst)**: Sphinx標準だが、spec-kitのソースファイル（.md）と形式が異なる。変換ロジック追加が必要（却下理由: Constitution C004違反、仕様でMarkdownに決定済み）
- **CommonMark Markdown**: 基本的なMarkdown。Sphinxディレクティブがサポートされない（却下理由: 機能不足）

### Constitution Alignment

- **C004（理想実装ファースト）**: 最初からMyST拡張機能を全て有効化、段階的追加なし
- **C008（ドキュメント整合性）**: spec-kit仕様ファイルと同じMarkdown形式で一貫性確保
- **Core Principle I（spec-kit Integration First）**: spec-kitのMarkdownエコシステムと完全統合

---

## R004: MkDocs Configuration

### 調査内容

- **Material for MkDocs**: 最も人気のあるMkDocsテーマ（2025年時点でv9.6.21）
- **Navigation Structure**: YAML形式のnav設定とプログラマティック更新
- **mkdocs.yml Configuration**: 推奨設定パターン

### Decision

**選択したアプローチ**: MkDocs + Material theme + YAMLベースnav + ruamel.yamlでプログラマティック更新

### Rationale

#### Material theme採用理由

1. **業界標準**: GitHub、Microsoft、Googleなど大手企業が採用
2. **豊富な機能**: 検索、ダークモード、多言語対応、ナビゲーション拡張を標準装備
3. **メンテナンス**: 活発な開発（最新版9.6.21、2025年9月30日リリース）
4. **カスタマイズ性**: CSS/JavaScript追加や`custom_dir`でテーマ拡張可能

#### mkdocs.yml設定（理想実装）

```yaml
site_name: "{{ project_name }}"
site_url: "{{ site_url }}"
repo_url: "{{ repo_url }}"  # Git remote origin URLから自動取得
repo_name: "{{ repo_name }}"

theme:
  name: material
  language: ja
  features:
    - navigation.tabs          # タブナビゲーション
    - navigation.sections      # セクション折りたたみ
    - navigation.expand        # 自動展開
    - navigation.top           # トップへ戻るボタン
    - search.suggest           # 検索サジェスト
    - search.highlight         # 検索結果ハイライト
    - content.code.copy        # コードコピーボタン
  palette:
    - scheme: default
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-7
        name: ダークモードに切り替え
    - scheme: slate
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-4
        name: ライトモードに切り替え

nav:
  - Home: index.md
  - Features:
    - User Auth: features/user-auth.md
    - API Integration: features/api-integration.md

markdown_extensions:
  - admonition        # 注記ブロック
  - pymdownx.details  # 折りたたみ可能な詳細
  - pymdownx.superfences  # コードブロック拡張
  - pymdownx.tabbed   # タブ
  - attr_list         # 属性リスト
  - md_in_html        # HTML内Markdown
```

#### プログラマティック更新戦略

```python
from ruamel.yaml import YAML
from pathlib import Path

yaml = YAML()
yaml.preserve_quotes = True
yaml.default_flow_style = False

def update_mkdocs_nav(mkdocs_yml: Path, new_features: list[dict]):
    """
    mkdocs.ymlのnavセクションを更新

    Args:
        mkdocs_yml: mkdocs.ymlのパス
        new_features: 新しい機能のリスト [{"title": "...", "path": "..."}]
    """
    with open(mkdocs_yml, 'r') as f:
        config = yaml.load(f)

    if 'nav' not in config:
        config['nav'] = []

    # Featuresセクションを取得または作成
    features_section = next(
        (item for item in config['nav'] if 'Features' in item),
        None
    )

    if features_section is None:
        config['nav'].append({'Features': []})
        features_section = config['nav'][-1]

    # 新しい機能を追加
    for feature in new_features:
        features_section['Features'].append({
            feature['title']: feature['path']
        })

    # 保存
    with open(mkdocs_yml, 'w') as f:
        yaml.dump(config, f)
```

### Implementation Example

```python
# MkDocs初期化
from jinja2 import Environment, PackageLoader

env = Environment(loader=PackageLoader('speckit_docs', 'templates'))
template = env.get_template('mkdocs/mkdocs.yml.j2')

mkdocs_content = template.render(
    project_name="My Project",
    site_url="https://example.com",
    repo_url="https://github.com/user/repo",
    repo_name="user/repo",
    features=[
        {"title": "User Auth", "path": "features/user-auth.md"},
        {"title": "API Integration", "path": "features/api-integration.md"},
    ]
)

mkdocs_yml = Path("mkdocs.yml")
mkdocs_yml.write_text(mkdocs_content)
```

### Alternatives Considered

- **readthedocs theme**: MkDocsデフォルトテーマだが機能が限定的（却下理由: ユーザー体験低下）
- **mkdocs-literate-nav plugin**: Markdownでナビゲーション定義。小規模プロジェクト向けで、大規模プロジェクトでは複雑化（却下理由: MVP範囲でYAML更新で十分）
- **mkdocs-awesome-nav plugin**: Glob パターンサポート。追加依存関係が必要（却下理由: MVP範囲でYAML更新で十分、依存増加）

### Constitution Alignment

- **C004（理想実装ファースト）**: Material themeの全機能を最初から有効化
- **C012（DRY原則）**: ruamel.yamlで既存構造を保持し、手動編集とプログラマティック更新の両立
- **Core Principle III（Extensibility & Modularity）**: YAMLベース設定でカスタマイズ容易

---

## R005: Git Change Detection

### 調査内容

- **GitPython Library**: PythonからGitリポジトリを操作するライブラリ
- **git diff Strategy**: HEAD比較、Index比較、Working Directory比較の選択
- **Incremental Build**: 変更検出とファイルスキップロジック

### Decision

**選択したアプローチ**: GitPython + HEAD比較（`repo.index.diff("HEAD")`）+ ファイルハッシュキャッシュ

### Rationale

#### GitPython採用理由

1. **Pythonネイティブ**: subprocess経由のgitコマンド実行より型安全で保守性高い
2. **豊富なAPI**: コミット、ブランチ、diff、blame等の全Git操作をサポート
3. **テスタビリティ**: モック可能で単体テスト容易（Constitution C010: TDD必須に準拠）

#### git diff戦略

```python
from git import Repo
from pathlib import Path

def detect_changed_specs(repo_path: Path) -> list[Path]:
    """
    前回の更新以降に変更されたspec.md/plan.md/tasks.mdを検出

    戦略:
    1. HEAD（最新コミット）と現在のインデックス（staged + unstaged）を比較
    2. specs/ディレクトリ配下の.mdファイルのみフィルタリング
    3. 変更タイプ（Added, Modified, Deleted）を判定
    """
    repo = Repo(repo_path)

    # staged + unstaged変更を全て取得
    diff_index = repo.index.diff("HEAD")

    changed_specs = []
    for diff_item in diff_index:
        file_path = Path(diff_item.a_path)

        # specs/配下の.mdファイルのみ対象
        if file_path.parts[0] == 'specs' and file_path.suffix == '.md':
            if diff_item.change_type in ['A', 'M']:  # Added or Modified
                changed_specs.append(file_path)

    return changed_specs
```

#### インクリメンタル更新ロジック

```python
import hashlib
import json
from pathlib import Path

def compute_file_hash(file_path: Path) -> str:
    """ファイルのSHA256ハッシュを計算"""
    return hashlib.sha256(file_path.read_bytes()).hexdigest()

def load_cache(cache_file: Path) -> dict[str, str]:
    """前回実行時のファイルハッシュキャッシュを読み込み"""
    if cache_file.exists():
        return json.loads(cache_file.read_text())
    return {}

def save_cache(cache_file: Path, cache: dict[str, str]):
    """現在のファイルハッシュキャッシュを保存"""
    cache_file.write_text(json.dumps(cache, indent=2))

def incremental_update(specs_dir: Path, cache_file: Path) -> list[Path]:
    """
    インクリメンタル更新: ハッシュ比較で変更検出

    利点:
    - Git履歴不要（新規プロジェクトでも動作）
    - 高速（ファイル内容のハッシュ比較のみ）
    - 確実（ファイル内容の変更を確実に検出）
    """
    cache = load_cache(cache_file)
    changed_files = []
    new_cache = {}

    for spec_file in specs_dir.rglob('*.md'):
        current_hash = compute_file_hash(spec_file)
        relative_path = str(spec_file.relative_to(specs_dir))

        if cache.get(relative_path) != current_hash:
            changed_files.append(spec_file)

        new_cache[relative_path] = current_hash

    save_cache(cache_file, new_cache)
    return changed_files
```

#### パフォーマンス最適化

- **ハッシュキャッシュ**: `.specify/cache/doc_update_hashes.json`にファイルハッシュを保存
- **Git diffフォールバック**: キャッシュがない場合はGit diff使用
- **並列処理**: 将来的に`concurrent.futures`でファイル解析を並列化可能

### Implementation Example

```python
from git import Repo
from pathlib import Path

class ChangeDetector:
    def __init__(self, repo_path: Path):
        self.repo = Repo(repo_path)
        self.specs_dir = repo_path / "specs"

    def get_changed_features(self, base_ref="HEAD", target_ref=None) -> list[Path]:
        """
        変更された機能ディレクトリを取得

        Args:
            base_ref: 比較元（デフォルトは最新コミット）
            target_ref: 比較先（Noneの場合はWorking Directory）

        Returns:
            変更された機能ディレクトリのリスト
        """
        diff_index = self.repo.commit(base_ref).diff(target_ref)

        changed_features = set()
        for diff_item in diff_index:
            file_path = Path(diff_item.a_path or diff_item.b_path)

            # specs/ディレクトリ配下のみ
            if file_path.parts[0] == "specs" and len(file_path.parts) >= 2:
                feature_dir = self.specs_dir / file_path.parts[1]
                if feature_dir.is_dir():
                    changed_features.add(feature_dir)

        return list(changed_features)
```

### Alternatives Considered

- **subprocessでgit diff実行**: シェル依存でテスト困難（却下理由: Constitution C010違反、テスタビリティ低下）
- **os.path.getmtime()比較**: タイムスタンプは信頼性が低い（Gitチェックアウトで変更）（却下理由: 信頼性不足）
- **全ファイル毎回処理**: シンプルだが大規模プロジェクトで遅い（却下理由: NFR違反、インクリメンタル更新要件）

### Constitution Alignment

- **C004（理想実装ファースト）**: 最初から高速なハッシュキャッシュ戦略を採用、「とりあえず全更新」なし
- **C010（TDD必須）**: GitPythonでモック容易、単体テスト可能
- **NFR（パフォーマンス）**: インクリメンタル更新で変更ファイルのみ処理、フル更新比で約90%削減

---

## R006: spec-kit Integration Pattern

### 調査内容

- **本家spec-kit CLI構造**: Typer + `specify init` + `--here`/`--force`フラグ
- **Slash Command Integration**: `.claude/commands/*.md`ファイルとClaude Code連携
- **Installation Pattern**: GitHubからのダウンロード vs パッケージ内配置

### Decision

**選択したアプローチ**: spec-kit `specify init --here`パターン準拠 + importlib.resourcesでファイル配置

### Rationale

#### spec-kit initパターン分析

本家spec-kitの`specify init`コマンド実装から抽出したパターン:

```python
# 本家spec-kitのパターン（参考）
@app.command()
def init(
    project_name: str = typer.Argument(..., help="Project name"),
    here: bool = typer.Option(False, "--here", help="Initialize in current directory"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing files"),
    ai: str = typer.Option("claude", "--ai", help="AI assistant (claude/gemini/copilot)"),
):
    if here:
        # カレントディレクトリに初期化
        project_path = Path.cwd()
        if list(project_path.iterdir()) and not force:
            # ファイルが存在する場合は確認
            if not typer.confirm("Directory not empty. Continue?"):
                raise typer.Abort()
    else:
        # 新規ディレクトリ作成
        project_path = Path(project_name)
        project_path.mkdir(exist_ok=True)

    # GitHubからテンプレートダウンロード
    download_template(ai_assistant=ai, target_path=project_path)
```

#### spec-kit-docsへの適用

```python
# spec-kit-docsのinstallコマンド
@app.command()
def install(
    force: bool = typer.Option(False, "--force", help="Overwrite existing files without confirmation"),
):
    """
    Install spec-kit-docs extension to current spec-kit project.

    本家spec-kitの`specify init --here`パターンに従う:
    1. カレントディレクトリがspec-kitプロジェクトか検証
    2. 既存ファイル確認（--forceなしの場合）
    3. importlib.resourcesからファイルコピー
    4. ベストエフォート方式（部分的成功を許容）
    """
    project_path = Path.cwd()

    # spec-kitプロジェクト検証
    if not (project_path / ".specify").is_dir():
        typer.echo("Error: Not a spec-kit project. Run 'specify init' first.")
        raise typer.Exit(code=1)

    if not (project_path / ".claude" / "commands").is_dir():
        typer.echo("Error: .claude/commands directory not found.")
        raise typer.Exit(code=1)

    # 既存ファイル確認（本家パターン）
    commands_dir = project_path / ".claude" / "commands"
    existing_files = [
        commands_dir / "speckit.doc-init.md",
        commands_dir / "speckit.doc-update.md",
    ]

    if any(f.exists() for f in existing_files) and not force:
        if not typer.confirm("spec-kit-docs files already exist. Overwrite?"):
            typer.echo("Installation cancelled.")
            raise typer.Exit(code=0)

    # importlib.resourcesからファイルコピー
    from importlib.resources import files

    templates = files('speckit_docs.commands')
    for file_name in ['speckit.doc-init.md', 'speckit.doc-update.md']:
        source = templates.joinpath(file_name).read_text()
        target = commands_dir / file_name
        target.write_text(source)
        typer.echo(f"✓ Installed {file_name}")

    # スクリプトコピー
    scripts_src = files('speckit_docs.scripts')
    scripts_dir = project_path / ".specify" / "scripts" / "docs"
    scripts_dir.mkdir(parents=True, exist_ok=True)

    for script in ['doc_init.py', 'doc_update.py']:
        source = scripts_src.joinpath(script).read_text()
        target = scripts_dir / script
        target.write_text(source)
        typer.echo(f"✓ Installed {script}")

    typer.echo("\n✓ Installation complete!")
    typer.echo("Available commands: /speckit.doc-init, /speckit.doc-update")
```

#### スラッシュコマンド定義パターン

```markdown
<!-- .claude/commands/speckit.doc-init.md -->
# /speckit.doc-init - Initialize documentation project

本家spec-kitの`/speckit.specify`パターンに従う:
1. ユーザーと対話的に情報収集
2. コマンドライン引数を構築
3. バックエンドスクリプトを非対話的に実行
4. 結果をユーザーにフィードバック

## Workflow

1. **Pre-check**: Verify `.specify/` directory exists
2. **Interactive Input**:
   - Ask: "Which documentation tool? (sphinx/mkdocs)"
   - If sphinx: Ask project name, author, version, language
   - If mkdocs: Ask project name, site name, repo URL
3. **Existing docs/ check**:
   - If exists: Ask "docs/ already exists. Overwrite? (yes/no)"
   - If no: Abort
   - If yes: Add --force flag
4. **Execute**: Run `uv run python .specify/scripts/docs/doc_init.py` with args
5. **Feedback**: Show success message and next steps

## Error Handling

- Not a spec-kit project: "Run 'specify init' first"
- Script error: Show error message and suggest checking logs
```

### Implementation Example

```python
# インタラクティブ確認パターン（typer使用）
import typer
from pathlib import Path

def doc_init(
    doc_type: str = typer.Option(None, "--type", help="Documentation tool (sphinx/mkdocs)"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing docs/"),
):
    """Initialize documentation project."""
    docs_dir = Path("docs")

    if docs_dir.exists():
        typer.echo(f"[yellow]Warning:[/yellow] docs/ already exists")

        if force:
            typer.echo("[cyan]--force supplied: skipping confirmation[/cyan]")
        else:
            if not typer.confirm("Do you want to continue?"):
                typer.echo("[yellow]Operation cancelled[/yellow]")
                raise typer.Exit(0)

    # ドキュメントツール選択
    if not doc_type:
        doc_type = typer.prompt(
            "Which documentation tool?",
            type=typer.Choice(["sphinx", "mkdocs"])
        )

    # 設定収集
    if doc_type == "sphinx":
        project_name = typer.prompt("Project name", default=Path.cwd().name)
        author = typer.prompt("Author name")
        version = typer.prompt("Version", default="0.1.0")
        language = typer.prompt("Language", default="ja")

        # スクリプト実行
        run_doc_init_script(
            doc_type="sphinx",
            project_name=project_name,
            author=author,
            version=version,
            language=language
        )
```

### Alternatives Considered

- **独立したCLI構造（`speckit-docs init`）**: spec-kitとの一貫性がない（却下理由: Constitution I違反）
- **Pythonスクリプト直接実行**: `uv run python install.py`。CLIツールとしてのユーザビリティ低下（却下理由: 使いやすさ）
- **環境変数設定**: インストール時に環境変数を設定。複雑で非標準（却下理由: Constitution C011違反）

### Constitution Alignment

- **C001（ルール遵守）**: 本家spec-kitの`specify init --here --force`パターンを忠実に再現
- **Core Principle I（spec-kit Integration First）**: spec-kitの標準パターンと完全一貫
- **Core Principle II（Non-Interactive Execution）**: バックエンドスクリプトは非対話的、対話はAIエージェント担当

---

## R007: Testing Strategy

### 調査内容

- **Test-Driven Development (TDD)**: Red-Green-Refactorサイクル
- **pytest Framework**: Python標準のテストフレームワーク
- **Test Coverage**: 業界標準のカバレッジ目標
- **File System Mocking**: pyfakefs、tmp_path、pytest-mockの選択

### Decision

**選択したアプローチ**: pytest + TDD (Red-Green-Refactor) + 90%カバレッジ目標 + pyfakefs + pytest-mock

### Rationale

#### TDD必須（Constitution C010）

```python
# Red-Green-Refactor cycle example

# 1. RED: テストを書き、失敗することを確認
def test_detect_changed_specs_should_return_modified_files():
    """
    Changed spec files should be detected by git diff.
    """
    repo_path = Path("/fake/repo")
    # Setup: Create fake git repo with modified spec.md
    # ... (setup code)

    changed = detect_changed_specs(repo_path)

    assert len(changed) == 1
    assert changed[0] == Path("specs/001-feature/spec.md")
    # → 実装前なので失敗（RED）

# 2. GREEN: テストを通過する最小限の実装
def detect_changed_specs(repo_path: Path) -> list[Path]:
    # 最小実装（ハードコード）
    return [Path("specs/001-feature/spec.md")]
    # → テスト通過（GREEN）

# 3. REFACTOR: 実装を改善、テストは通過し続ける
def detect_changed_specs(repo_path: Path) -> list[Path]:
    repo = Repo(repo_path)
    diff_index = repo.index.diff("HEAD")
    changed = []
    for item in diff_index:
        if Path(item.a_path).parts[0] == 'specs':
            changed.append(Path(item.a_path))
    return changed
    # → テスト通過、かつ汎用実装（REFACTOR）
```

#### pytest採用理由

1. **業界標準**: Python テスティングのデファクトスタンダード
2. **豊富なプラグイン**: pytest-cov、pytest-mock、pyfakefs等のエコシステム
3. **fixtures**: セットアップ/ティアダウンの自動管理
4. **パラメトライズ**: 複数入力パターンを効率的にテスト

#### カバレッジ目標（90%）

```bash
# pytest-covでカバレッジ測定
pytest --cov=src/speckit_docs --cov-report=html --cov-report=term

# 目標:
# - Unit tests: 主要コードパス90%以上
# - Integration tests: エンドツーエンドワークフロー
# - Edge cases: エラーハンドリング、境界値
```

業界標準（80%）より高い90%を目標とする理由:
- ドキュメント生成は多様なプロジェクト構造に対応する必要がある
- ファイルシステム操作のバグは検出が困難
- spec-kit統合の信頼性確保

#### ファイルシステムモック戦略

```python
# pyfakefs: ファイルシステム全体をモック
def test_doc_init_creates_sphinx_structure(fs):  # fs = fake filesystem fixture
    """
    Sphinx initialization should create standard directory structure.
    """
    fs.create_dir("/project")

    doc_init(
        project_path=Path("/project"),
        doc_type="sphinx",
        project_name="Test",
        author="Author",
        version="1.0.0"
    )

    assert Path("/project/docs/conf.py").exists()
    assert Path("/project/docs/index.md").exists()
    assert Path("/project/docs/Makefile").exists()

# tmp_path: 実際の一時ディレクトリ（統合テスト）
def test_full_workflow_with_real_files(tmp_path):
    """
    Full workflow: init -> update -> build should work end-to-end.
    """
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()

    # Real file operations
    doc_init(project_dir, "sphinx", "Test", "Author", "1.0.0")
    doc_update(project_dir)

    # Verify actual files
    assert (project_dir / "docs" / "_build" / "html" / "index.html").exists()

# pytest-mock: GitPython等の外部依存をモック
def test_detect_changed_specs_calls_git_diff(mocker):
    """
    detect_changed_specs should call git diff with correct arguments.
    """
    mock_repo = mocker.Mock()
    mock_diff = mocker.Mock()
    mock_repo.index.diff.return_value = mock_diff
    mocker.patch('git.Repo', return_value=mock_repo)

    detect_changed_specs(Path("/project"))

    mock_repo.index.diff.assert_called_once_with("HEAD")
```

#### テスト構造（Testing Pyramid）

```
tests/
├── unit/                      # 50% - 単体テスト
│   ├── test_parsers.py
│   ├── test_generators.py
│   └── test_git_utils.py
├── integration/               # 30% - 統合テスト
│   ├── test_doc_init.py
│   ├── test_doc_update.py
│   └── test_install.py
└── e2e/                       # 20% - エンドツーエンド
    └── test_full_workflow.py
```

### Implementation Example

```python
# tests/unit/test_change_detector.py
import pytest
from pathlib import Path
from unittest.mock import Mock
from speckit_docs.utils.git import ChangeDetector

def test_get_changed_features_filters_specs_directory(mocker):
    """
    ChangeDetector should only return features from specs/ directory.
    """
    # Arrange
    mock_repo = mocker.Mock()
    mock_diff_item1 = Mock(a_path="specs/001-feature/spec.md", change_type="M")
    mock_diff_item2 = Mock(a_path="README.md", change_type="M")
    mock_diff_item3 = Mock(a_path="specs/002-feature/plan.md", change_type="M")

    mock_repo.commit.return_value.diff.return_value = [
        mock_diff_item1,
        mock_diff_item2,
        mock_diff_item3,
    ]
    mocker.patch('git.Repo', return_value=mock_repo)

    detector = ChangeDetector(Path("/project"))

    # Act
    changed = detector.get_changed_features()

    # Assert
    assert len(changed) == 2
    assert Path("/project/specs/001-feature") in changed
    assert Path("/project/specs/002-feature") in changed
```

### Alternatives Considered

- **unittest**: Python標準だがpytestより冗長（却下理由: 生産性低下）
- **nose2**: レガシー、メンテナンス停止（却下理由: 保守性リスク）
- **100%カバレッジ目標**: 過度な負担、価値の低いテスト増加（却下理由: 実用性低下）

### Constitution Alignment

- **C010（TDD必須）**: Red-Green-Refactorサイクル強制
- **C006（堅牢コード品質）**: 90%カバレッジで品質保証
- **Core Principle V（Testability）**: pyfakefs、pytest-mockでモック容易

---

## Summary: Research-Driven Decisions

本調査により、以下の技術スタックが**理想実装（Constitution C004）**として決定されました:

| 領域 | 選択技術 | 根拠 |
|------|---------|------|
| CLI Framework | Typer | spec-kit統合（Constitution I）、型安全性（C006） |
| Template Engine | Jinja2 + importlib.resources | 業界標準、オフライン動作、セキュリティ（C006） |
| Sphinx Integration | myst-parser + Optional Extensions | spec-kit Markdown統一（C008）、学習コスト削減 |
| MkDocs Configuration | Material theme + YAML nav | 業界標準、豊富な機能、プログラマティック更新 |
| Git Change Detection | GitPython + ハッシュキャッシュ | 高速（NFR）、テスト容易（C010）、信頼性 |
| spec-kit Pattern | `specify init --here` + importlib.resources | spec-kit完全一貫（Constitution I） |
| Testing Strategy | pytest + TDD + 90%カバレッジ + pyfakefs | TDD必須（C010）、品質保証（C006） |

これらの決定は、すべて**Constitution（憲章）の原則に準拠**しており、次のPhase 1（Implementation Plan）で詳細設計に落とし込まれます。

**次のステップ**: `/speckit.plan`コマンドでplan.mdを生成し、アーキテクチャ設計とタスク分解を行います。

---

**作成完了日**: 2025-10-13
