# Contract: handle_dependencies()

**Feature**: 001-draft-init-spec (Session 2025-10-15追加)
**Module**: `src/speckit_docs/utils/dependencies.py`
**Function**: `handle_dependencies()`

## Overview

依存関係自動インストール機能（FR-008b～FR-008e）の中核となる関数です。条件チェック、ユーザー承認、`uv add`実行、エラーハンドリング、代替方法提示のすべてを担当します。

## Function Signature

```python
def handle_dependencies(
    doc_type: str,
    auto_install: bool,
    no_install: bool,
    project_root: Path,
    console: Console,
) -> DependencyResult:
    """依存関係のチェックとインストールを処理する。

    Args:
        doc_type: "sphinx" または "mkdocs"
        auto_install: --auto-installフラグ（CI/CD用、確認スキップ）
        no_install: --no-installフラグ（依存関係チェックスキップ）
        project_root: プロジェクトルートパス
        console: rich.console.Console（進捗表示用）

    Returns:
        DependencyResult: status, message, installed_packagesを含む

    Raises:
        ValueError: doc_typeが"sphinx"または"mkdocs"以外の場合
        SpecKitDocsError: 予期しないエラーが発生した場合
    """
```

## Input Specification

### doc_type (str)

- **Type**: `str`
- **Allowed Values**: `"sphinx"` | `"mkdocs"`
- **Description**: ドキュメントツールの種類を指定
- **Validation**:
  - 値が`"sphinx"`または`"mkdocs"`でない場合、`ValueError`を発生させる
- **Example**: `"sphinx"`

### auto_install (bool)

- **Type**: `bool`
- **Description**: CI/CD環境での非対話的実行を制御
- **Behavior**:
  - `True`: ユーザー確認をスキップして自動インストール
  - `False`: ユーザーに確認プロンプトを表示
- **Requirement**: FR-008e（`--auto-install`フラグ）
- **Example**: `True` (CI/CD環境), `False` (通常実行)

### no_install (bool)

- **Type**: `bool`
- **Description**: 依存関係チェックとインストールをすべてスキップ
- **Behavior**:
  - `True`: 即座に`DependencyResult(status="skipped", message="--no-install指定のためスキップ")`を返す
  - `False`: 通常のインストールフローを実行
- **Requirement**: FR-008e（`--no-install`フラグ）
- **Example**: `False` (通常実行), `True` (手動管理)

### project_root (Path)

- **Type**: `pathlib.Path`
- **Description**: プロジェクトルートディレクトリの絶対パス
- **Validation**:
  - 実際に存在するディレクトリでなければならない
  - `pyproject.toml`の存在確認に使用される（`project_root / "pyproject.toml"`）
- **Example**: `Path("/home/user/my-project")`

### console (Console)

- **Type**: `rich.console.Console`
- **Description**: 進捗表示とユーザーフィードバック用のコンソールオブジェクト
- **Usage**:
  - 情報メッセージ: `console.print("[green]✓[/green] メッセージ")`
  - エラーメッセージ: `console.print("[red]✗[/red] メッセージ")`
  - 警告メッセージ: `console.print("[yellow]警告:[/yellow] メッセージ")`
- **Example**: `Console()`

## Output Specification

### DependencyResult

```python
@dataclass(frozen=True)
class DependencyResult:
    status: Literal["installed", "skipped", "failed", "not_needed"]
    message: str
    installed_packages: list[str] = field(default_factory=list)
```

#### status: Literal["installed", "skipped", "failed", "not_needed"]

- **"installed"**: 自動インストールが成功した
  - `installed_packages`は空でない
  - `message`は"インストール成功"
- **"skipped"**: ユーザーが拒否、または`--no-install`フラグが指定された
  - `installed_packages`は空
  - `message`は拒否理由（"ユーザーが拒否"、"--no-install指定のためスキップ"等）
- **"failed"**: インストール失敗（条件不満足またはuv addエラー）
  - `installed_packages`は空
  - `message`は失敗理由（"pyproject.toml不在"、"uvコマンド不在"、"uv add失敗: <stderr>"等）
- **"not_needed"**: パッケージが既にインストール済み
  - `installed_packages`は空
  - `message`は"すべてのパッケージがインストール済み"

#### message: str

- **Type**: `str`
- **Description**: ステータスの詳細メッセージ（ユーザーへのフィードバック用）
- **Examples**:
  - "インストール成功"
  - "ユーザーが拒否"
  - "pyproject.toml不在"
  - "uvコマンド不在"
  - "uv add失敗: <stderr>"
  - "すべてのパッケージがインストール済み"

#### installed_packages: list[str]

- **Type**: `list[str]`
- **Description**: インストールされたパッケージのリスト（バージョン制約含む）
- **Constraint**: `status="installed"`の場合のみ空でない
- **Examples**:
  - `["sphinx>=7.0", "myst-parser>=2.0"]` (Sphinx)
  - `["mkdocs>=1.5", "mkdocs-material>=9.0"]` (MkDocs)

## Behavior Specification

### 処理フロー

```
1. no_installフラグチェック
   ├─ True → return DependencyResult(status="skipped", message="--no-install指定のためスキップ")
   └─ False → 2へ

2. pyproject.toml存在確認
   ├─ 存在しない → show_alternative_methods() → return DependencyResult(status="failed", message="pyproject.toml不在")
   └─ 存在する → 3へ

3. uvコマンド確認
   ├─ 利用不可 → show_alternative_methods() → return DependencyResult(status="failed", message="uvコマンド不在")
   └─ 利用可能 → 4へ

4. パッケージインストール済み確認
   ├─ すべてインストール済み → return DependencyResult(status="not_needed", message="すべてのパッケージがインストール済み")
   └─ 未インストール → 5へ

5. ユーザー承認取得（auto_install=Falseの場合のみ）
   ├─ パッケージ情報表示
   ├─ 実行コマンド表示
   ├─ pyproject.toml変更警告
   ├─ typer.confirm("インストールを続行しますか？", default=True)
   │   ├─ ユーザーが拒否 → show_alternative_methods() → return DependencyResult(status="skipped", message="ユーザーが拒否")
   │   └─ ユーザーが承認 → 6へ
   └─ auto_install=True → 6へ（確認スキップ）

6. uv addでインストール実行
   ├─ subprocess.run(["uv", "add"] + packages, timeout=300)
   ├─ returncode == 0 → return DependencyResult(status="installed", message="インストール成功", installed_packages=packages)
   ├─ returncode != 0 → show_alternative_methods() → return DependencyResult(status="failed", message=f"uv add失敗: {stderr}")
   ├─ TimeoutExpired → show_alternative_methods() → return DependencyResult(status="failed", message="タイムアウト")
   └─ FileNotFoundError → show_alternative_methods() → return DependencyResult(status="failed", message="uvコマンド不在")
```

### エラーハンドリング

#### ValueError (doc_type検証エラー)

```python
if doc_type not in ["sphinx", "mkdocs"]:
    raise ValueError(f"Invalid doc_type: {doc_type}. Must be 'sphinx' or 'mkdocs'")
```

#### subprocess.TimeoutExpired (uvタイムアウト)

```python
except subprocess.TimeoutExpired:
    console.print("[red]✗[/red] インストールがタイムアウトしました（5分超過）")
    show_alternative_methods(doc_type, console, project_root)
    return DependencyResult(status="failed", message="タイムアウト")
```

#### FileNotFoundError (uvコマンド不在)

```python
except FileNotFoundError:
    console.print("[red]✗[/red] uvコマンドが見つかりません")
    show_alternative_methods(doc_type, console, project_root)
    return DependencyResult(status="failed", message="uvコマンド不在")
```

## Pre-conditions

1. **doc_type検証**: `doc_type`は`"sphinx"`または`"mkdocs"`でなければならない
2. **project_root検証**: `project_root`は実際に存在するディレクトリでなければならない
3. **console初期化**: `console`は有効な`rich.console.Console`インスタンスでなければならない

## Post-conditions

### status="installed"の場合

1. パッケージが`pyproject.toml`に追加されている
2. パッケージが実際にインストールされている（`importlib.util.find_spec()`で確認可能）
3. `installed_packages`リストが空でない

### status="failed"の場合

1. `show_alternative_methods()`が呼び出されている
2. エラーメッセージがconsoleに表示されている
3. 代替方法（方法1: 手動インストール、方法2: spec-kitワークフロー）が表示されている

### status="skipped"の場合

1. インストールが実行されていない
2. `pyproject.toml`が変更されていない
3. スキップ理由がmessageに記録されている

### status="not_needed"の場合

1. すべての必要なパッケージが既にインストールされている
2. 新しいインストールが実行されていない

## Requirements Traceability

| Requirement | Implementation |
|-------------|----------------|
| FR-008b | 条件チェック（pyproject.toml存在、uvコマンド利用可能、`--no-install`未指定、パッケージ未インストール） |
| FR-008c | ユーザー承認プロンプト（パッケージリスト、実行コマンド、警告、`typer.confirm(default=True)`） |
| FR-008d | `show_alternative_methods()`呼び出し（条件不満足時またはuv add失敗時） |
| FR-008e | `--auto-install`/`--no-install`フラグサポート、uv add失敗時のエラー詳細と代替方法表示 |
| SC-002b | timeout=300秒、90%成功率目標（外部要因10%許容） |

## Example Usage

### 成功ケース（auto_install=False）

```python
from pathlib import Path
from rich.console import Console

console = Console()
result = handle_dependencies(
    doc_type="sphinx",
    auto_install=False,
    no_install=False,
    project_root=Path("/home/user/my-project"),
    console=console,
)

# Output: DependencyResult(status="installed", message="インストール成功", installed_packages=["sphinx>=7.0", "myst-parser>=2.0"])
assert result.status == "installed"
assert "sphinx" in result.installed_packages[0]
```

### 失敗ケース（pyproject.toml不在）

```python
result = handle_dependencies(
    doc_type="mkdocs",
    auto_install=True,
    no_install=False,
    project_root=Path("/home/user/no-pyproject"),
    console=console,
)

# Output: DependencyResult(status="failed", message="pyproject.toml不在", installed_packages=[])
assert result.status == "failed"
assert "pyproject.toml不在" in result.message
assert result.installed_packages == []
```

### スキップケース（--no-install）

```python
result = handle_dependencies(
    doc_type="sphinx",
    auto_install=False,
    no_install=True,
    project_root=Path("/home/user/my-project"),
    console=console,
)

# Output: DependencyResult(status="skipped", message="--no-install指定のためスキップ", installed_packages=[])
assert result.status == "skipped"
assert "--no-install" in result.message
```

### 不要ケース（パッケージ既インストール）

```python
# 前提: sphinx>=7.0とmyst-parser>=2.0が既にインストール済み
result = handle_dependencies(
    doc_type="sphinx",
    auto_install=False,
    no_install=False,
    project_root=Path("/home/user/my-project"),
    console=console,
)

# Output: DependencyResult(status="not_needed", message="すべてのパッケージがインストール済み", installed_packages=[])
assert result.status == "not_needed"
assert "インストール済み" in result.message
```

## Test Coverage

### 単体テスト

1. `test_handle_dependencies_success`: 正常系（pyproject.toml存在、uv利用可能、インストール成功）
2. `test_handle_dependencies_no_pyproject`: pyproject.toml不在 → `status="failed"`
3. `test_handle_dependencies_uv_not_found`: uvコマンド不在 → `status="failed"`
4. `test_handle_dependencies_already_installed`: パッケージ既インストール → `status="not_needed"`
5. `test_handle_dependencies_no_install_flag`: `--no-install`フラグ → `status="skipped"`
6. `test_handle_dependencies_auto_install_flag`: `--auto-install`フラグ → 確認スキップ
7. `test_handle_dependencies_timeout`: uv addタイムアウト → `status="failed"`
8. `test_handle_dependencies_uv_add_failed`: uv add失敗（returncode != 0） → `status="failed"`
9. `test_handle_dependencies_user_declined`: ユーザー承認拒否 → `status="skipped"`
10. `test_handle_dependencies_invalid_doc_type`: doc_type不正 → `ValueError`

### 統合テスト

1. `test_integration_handle_dependencies_with_real_uv`: 実際のuvコマンドでインストール
2. `test_integration_handle_dependencies_with_pyproject`: pyproject.toml実在環境でテスト

### カバレッジ目標

- `handle_dependencies()`: 95%以上
- すべての分岐（条件チェック、エラーハンドリング）をカバー

## Dependencies

### Internal

- `get_required_packages(doc_type: str) -> list[str]`: doc_typeに応じたパッケージリストを返す
- `show_alternative_methods(doc_type: str, console: Console, project_root: Path) -> None`: 代替インストール方法を表示
- `detect_package_managers(project_root: Path, doc_type: str) -> list[tuple[str, str]]`: 利用可能なパッケージマネージャーを検出
- `DependencyResult`: 戻り値のデータクラス

### External

- `pathlib.Path`: ファイルパス操作
- `subprocess.run()`: uvコマンド実行
- `shutil.which()`: uvコマンド存在確認
- `importlib.util.find_spec()`: パッケージインストール確認
- `typer.confirm()`: ユーザー承認プロンプト
- `rich.console.Console`: 進捗表示

## Notes

1. **決定的動作**: 同じ入力→同じ出力（V. Testability準拠）
2. **C002準拠**: エラー迂回絶対禁止、明確なエラー+代替方法提示
3. **C012準拠**: typer.confirm()再利用（本家spec-kitパターン）
4. **非対話的実行**: auto_install=Trueでユーザー確認スキップ（CI/CD対応）
5. **タイムアウト**: 300秒（5分）でネットワーク遅延を許容しつつ、無限待機を回避
