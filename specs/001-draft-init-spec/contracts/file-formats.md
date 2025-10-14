# File Format Contracts: spec-kit-docs

**Feature**: spec-kit-docs
**Date**: 2025-10-12
**Phase**: 1 - Interface Contracts
**Type**: File Format Specifications
**Source**: [spec.md](../spec.md) | [data-model.md](../data-model.md)

## Overview

このドキュメントは、spec-kit-docsが生成するファイルの形式仕様を定義します。これらの仕様は、生成されたファイルが正しいフォーマットであることを保証するためのコントラクトとして機能します。

---

## 1. Sphinx Configuration (conf.py)

### File Path
`docs/conf.py`

### Format
Python設定ファイル

### Template
`src/speckit_docs/templates/sphinx/conf.py.j2`

### Required Fields

```python
# Project information
project = "{{ project_name }}"
copyright = "{{ year }}, {{ author }}"
author = "{{ author }}"
version = "{{ version }}"
release = "{{ version }}"

# General configuration
extensions = [
    'myst_parser',              # FR-005a: MyST Markdown support
    'sphinx.ext.autodoc',       # Optional: API documentation
    'sphinx.ext.viewcode',      # Optional: Source code links
    'sphinx.ext.napoleon',      # Optional: Google/NumPy docstring support
]

# Source file configuration
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',          # FR-005a: Markdown support
}

# MyST Parser configuration (FR-005a)
myst_enable_extensions = [
    "colon_fence",              # ::: fence for directives
    "deflist",                  # Definition lists
    "tasklist",                 # - [ ] task lists
    "attrs_inline",             # {#id .class} attributes
]

# Exclude patterns
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# HTML output configuration
html_theme = 'alabaster'        # Default theme
html_static_path = ['_static']

# Internationalization
language = '{{ language }}'     # Default: 'ja'
```

### Validation Rules

- [ ] `project`は非空文字列
- [ ] `extensions`に`'myst_parser'`が含まれる（FR-005a）
- [ ] `source_suffix`に`'.md': 'markdown'`が含まれる（FR-005a）
- [ ] `myst_enable_extensions`が定義されている（FR-005a）
- [ ] Python構文として正しい（`compile()`でエラーなし）

### Example

```python
# Project information
project = "my-spec-kit-project"
copyright = "2025, John Doe"
author = "John Doe"
version = "0.1.0"
release = "0.1.0"

# General configuration
extensions = [
    'myst_parser',
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
]

# Source file configuration
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# MyST Parser configuration
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "tasklist",
    "attrs_inline",
]

# Exclude patterns
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# HTML output configuration
html_theme = 'alabaster'
html_static_path = ['_static']

# Internationalization
language = 'ja'
```

**Source Requirements**: FR-005, FR-005a

---

## 2. Sphinx Index (index.md)

### File Path
`docs/index.md`

### Format
MyST Markdown

### Template
`src/speckit_docs/templates/sphinx/index.md.j2`

### Structure

```markdown
# {{ project_name }} ドキュメント

{{ description }}

## 機能一覧

```{toctree}
:maxdepth: 2
:caption: Features

{% for feature in features %}
{{ feature.file_name }}
{% endfor %}
```

## インデックス

* {ref}`genindex`
* {ref}`search`
```

### Validation Rules

- [ ] 見出し（`#`）が存在する
- [ ] `` ```{toctree}`` ディレクティブが存在する（MyST構文）
- [ ] `:maxdepth:`オプションが定義されている
- [ ] 各機能が1行ずつリストされている
- [ ] 有効なMarkdown構文

### Example (Flat Structure, 3 features)

```markdown
# my-spec-kit-project ドキュメント

このプロジェクトは、spec-kitを使用して開発されています。

## 機能一覧

```{toctree}
:maxdepth: 2
:caption: Features

user-auth
api-integration
payment-gateway
```

## インデックス

* {ref}`genindex`
* {ref}`search`
```

### Example (Comprehensive Structure, 8 features)

```markdown
# my-spec-kit-project ドキュメント

このプロジェクトは、spec-kitを使用して開発されています。

## 機能一覧

```{toctree}
:maxdepth: 2
:caption: Features

features/user-auth
features/api-integration
features/payment-gateway
features/notification-system
features/analytics-dashboard
features/admin-panel
features/export-functionality
features/search-engine
```

## ガイド

```{toctree}
:maxdepth: 1
:caption: Guides

guides/getting-started
guides/configuration
```

## API リファレンス

```{toctree}
:maxdepth: 1
:caption: API

api/reference
```

## アーキテクチャ

```{toctree}
:maxdepth: 1
:caption: Architecture

architecture/overview
```

## インデックス

* {ref}`genindex`
* {ref}`search`
```

**Source Requirements**: FR-005, FR-013

---

## 3. Sphinx Makefile (Makefile)

### File Path
`docs/Makefile`

### Format
Makefile（Linux/macOS用）

### Template
`src/speckit_docs/templates/sphinx/Makefile.j2`

### Content

```makefile
# Minimal Makefile for Sphinx documentation

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
```

### Validation Rules

- [ ] `SPHINXBUILD`変数が定義されている
- [ ] `SOURCEDIR`と`BUILDDIR`が定義されている
- [ ] `help`ターゲットが存在する
- [ ] キャッチオール（`%`）ターゲットが存在する
- [ ] 有効なMakefile構文

**Source Requirements**: FR-005

---

## 4. Sphinx Windows Batch (make.bat)

### File Path
`docs/make.bat`

### Format
Windows Batch Script

### Template
`src/speckit_docs/templates/sphinx/make.bat.j2`

### Content

```batch
@ECHO OFF

pushd %~dp0

REM Command file for Sphinx documentation

if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)
set SOURCEDIR=.
set BUILDDIR=_build

%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 (
	echo.
	echo.The 'sphinx-build' command was not found. Make sure you have Sphinx
	echo.installed, then set the SPHINXBUILD environment variable to point
	echo.to the full path of the 'sphinx-build' executable. Alternatively you
	echo.may add the Sphinx directory to PATH.
	echo.
	echo.If you don't have Sphinx installed, grab it from
	echo.https://www.sphinx-doc.org/
	exit /b 1
)

if "%1" == "" goto help

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%

:end
popd
```

### Validation Rules

- [ ] `SPHINXBUILD`変数が定義されている
- [ ] `SOURCEDIR`と`BUILDDIR`が定義されている
- [ ] エラーレベルチェック（9009）が存在する
- [ ] ヘルプターゲットが存在する

**Source Requirements**: FR-005

---

## 5. MkDocs Configuration (mkdocs.yml)

### File Path
`docs/mkdocs.yml`

### Format
YAML

### Template
`src/speckit_docs/templates/mkdocs/mkdocs.yml.j2`

### Required Fields

```yaml
site_name: {{ project_name }}
site_author: {{ author }}
site_description: {{ description }}

theme:
  name: material  # または 'readthedocs'
  language: {{ language }}  # Default: 'ja'

nav:
  - Home: index.md
{% for feature in features %}
  - {{ feature.title }}: {{ feature.file_name }}
{% endfor %}

markdown_extensions:
  - admonition          # Note, Warning等のブロック
  - codehilite          # シンタックスハイライト
  - toc:
      permalink: true   # 見出しアンカー
  - def_list            # 定義リスト
  - tables              # テーブル

plugins:
  - search              # 検索機能
```

### Validation Rules

- [ ] `site_name`が非空文字列
- [ ] `theme.name`が定義されている
- [ ] `nav`が定義されており、少なくとも`index.md`を含む
- [ ] `markdown_extensions`に基本拡張が含まれる
- [ ] 有効なYAML構文

### Example (Flat Structure, 3 features)

```yaml
site_name: my-spec-kit-project
site_author: John Doe
site_description: A spec-kit project

theme:
  name: material
  language: ja

nav:
  - Home: index.md
  - User Authentication: user-auth.md
  - API Integration: api-integration.md
  - Payment Gateway: payment-gateway.md

markdown_extensions:
  - admonition
  - codehilite
  - toc:
      permalink: true
  - def_list
  - tables

plugins:
  - search
```

### Example (Comprehensive Structure, 8 features)

```yaml
site_name: my-spec-kit-project
site_author: John Doe
site_description: A spec-kit project

theme:
  name: material
  language: ja

nav:
  - Home: index.md
  - Features:
      - User Authentication: features/user-auth.md
      - API Integration: features/api-integration.md
      - Payment Gateway: features/payment-gateway.md
      - Notification System: features/notification-system.md
      - Analytics Dashboard: features/analytics-dashboard.md
      - Admin Panel: features/admin-panel.md
      - Export Functionality: features/export-functionality.md
      - Search Engine: features/search-engine.md
  - Guides:
      - Getting Started: guides/getting-started.md
      - Configuration: guides/configuration.md
  - API:
      - Reference: api/reference.md
  - Architecture:
      - Overview: architecture/overview.md

markdown_extensions:
  - admonition
  - codehilite
  - toc:
      permalink: true
  - def_list
  - tables

plugins:
  - search
```

**Source Requirements**: FR-006, FR-014

---

## 6. MkDocs Index (index.md)

### File Path
`docs/index.md`

### Format
Markdown

### Template
`src/speckit_docs/templates/mkdocs/index.md.j2`

### Structure

```markdown
# {{ project_name }}

{{ description }}

## 機能一覧

{% for feature in features %}
- [{{ feature.title }}]({{ feature.file_name }})
{% endfor %}

## はじめに

このドキュメントは、spec-kitプロジェクトから自動生成されています。

詳細は、[Getting Started](guides/getting-started.md) を参照してください。
```

### Validation Rules

- [ ] 見出し（`#`）が存在する
- [ ] 機能へのリンクが存在する
- [ ] 有効なMarkdown構文

### Example (Flat Structure)

```markdown
# my-spec-kit-project

A spec-kit project

## 機能一覧

- [User Authentication](user-auth.md)
- [API Integration](api-integration.md)
- [Payment Gateway](payment-gateway.md)

## はじめに

このドキュメントは、spec-kitプロジェクトから自動生成されています。
```

**Source Requirements**: FR-006

---

## 7. Feature Document (Sphinx, *.md)

### File Path
`docs/{feature-name}.md` (Flat) or `docs/features/{feature-name}.md` (Comprehensive)

### Format
MyST Markdown

### Source
`.specify/specs/{###-feature-name}/spec.md`

### Structure

```markdown
# {{ feature.title }}

{{ feature.description }}

## 概要

{{ spec.overview }}

## ユーザーシナリオ

{{ spec.user_scenarios }}

## 機能要件

{{ spec.functional_requirements }}

## 非機能要件

{{ spec.non_functional_requirements }}

## 受け入れ基準

{{ spec.acceptance_criteria }}

## 成功基準

{{ spec.success_criteria }}

---

*このドキュメントは `.specify/specs/{{ feature.id }}-{{ feature.name }}/spec.md` から自動生成されています。*
```

### Validation Rules

- [ ] 少なくとも1つの見出し（`#`）が存在する
- [ ] 有効なMarkdown構文
- [ ] MyST Markdownディレクティブが正しく使用されている
- [ ] セクション階層が適切（`#` → `##` → `###`）

### File Naming Convention

- 機能ディレクトリ名: `001-user-auth`
- 生成ファイル名: `user-auth.md`（番号を除去、FR-013）

**Source Requirements**: FR-008, FR-013

---

## 8. Feature Document (MkDocs, *.md)

### File Path
`docs/{feature-name}.md` (Flat) or `docs/features/{feature-name}.md` (Comprehensive)

### Format
Markdown

### Source
`.specify/specs/{###-feature-name}/spec.md`

### Structure

同じくspec.mdから生成されますが、MkDocs用のMarkdown（MyST構文なし）に変換します。

```markdown
# {{ feature.title }}

{{ feature.description }}

## 概要

{{ spec.overview }}

## ユーザーシナリオ

{{ spec.user_scenarios }}

## 機能要件

{{ spec.functional_requirements }}

## 非機能要件

{{ spec.non_functional_requirements }}

## 受け入れ基準

{{ spec.acceptance_criteria }}

## 成功基準

{{ spec.success_criteria }}

---

*このドキュメントは `.specify/specs/{{ feature.id }}-{{ feature.name }}/spec.md` から自動生成されています。*
```

### Admonition Conversion

MyST構文 → MkDocs構文の変換例:

**MyST (Sphinx)**:
```markdown
```{note}
これは注意書きです。
```
```

**MkDocs**:
```markdown
!!! note
    これは注意書きです。
```

**Source Requirements**: FR-008, FR-014

---

## 9. .gitignore

### File Path
`docs/.gitignore`

### Format
Plain Text

### Content (Sphinx)

```
# Sphinx build outputs
_build/
_static/
_templates/

# OS files
.DS_Store
Thumbs.db
```

### Content (MkDocs)

```
# MkDocs build outputs
site/

# OS files
.DS_Store
Thumbs.db
```

### Validation Rules

- [ ] ビルド出力ディレクトリが含まれる（`_build/` or `site/`）
- [ ] OSファイルが含まれる（`.DS_Store`, `Thumbs.db`）

**Source Requirements**: FR-005, FR-006 (implied)

---

## Contract Testing

### Validation Approach

すべての生成ファイルに対して、以下の検証を実行します:

1. **構文検証**: ファイル形式が正しいか（Python/YAML/Markdown）
2. **必須フィールド検証**: 必須項目が含まれているか
3. **参照整合性検証**: ファイル間の参照が正しいか（index → feature files）
4. **命名規則検証**: ファイル名が規則に従っているか

### Test Implementation

**pytest example**:
```python
def test_sphinx_conf_py_format():
    """conf.pyがPython構文として正しいことを検証"""
    with open("docs/conf.py") as f:
        content = f.read()

    # Python構文チェック
    compile(content, "conf.py", "exec")

    # 必須フィールドチェック
    assert "myst_parser" in content
    assert "source_suffix" in content
    assert "myst_enable_extensions" in content

def test_sphinx_index_md_format():
    """index.mdが有効なMarkdownであることを検証"""
    with open("docs/index.md") as f:
        content = f.read()

    # toctreeディレクティブの存在確認
    assert "```{toctree}" in content
    assert ":maxdepth:" in content

def test_mkdocs_yml_format():
    """mkdocs.ymlが有効なYAMLであることを検証"""
    import yaml

    with open("docs/mkdocs.yml") as f:
        config = yaml.safe_load(f)

    # 必須フィールドチェック
    assert "site_name" in config
    assert "theme" in config
    assert "nav" in config
    assert config["nav"][0] == {"Home": "index.md"}

def test_feature_file_naming():
    """機能ファイル名が規則に従っていることを検証"""
    import os

    files = os.listdir("docs/features")

    for file in files:
        # 番号が含まれていないことを確認
        assert not file[0].isdigit()

        # .md拡張子であることを確認
        assert file.endswith(".md")
```

---

## Summary

このファイル形式仕様は、spec-kit-docsが生成する9種類のファイルフォーマットを定義しています。主要な設計決定:

1. **Sphinx: Markdown + myst-parser**: reStructuredTextではなくMarkdownを使用（FR-005a）
2. **動的構造**: 機能数に応じてFlat/Comprehensive構造を切り替え
3. **ファイル命名規則**: 番号を除いた説明的な名前（FR-013）
4. **MyST → MkDocs変換**: アドモニション構文の変換対応
5. **コントラクトテスト**: すべての生成ファイルの検証

これらの仕様に基づいて、実装フェーズではJinja2テンプレートとファイル生成ロジックを実装します。
