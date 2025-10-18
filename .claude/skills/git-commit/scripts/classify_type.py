#!/usr/bin/env python3
"""
Conventional Commits Type分類スクリプト

変更分析結果からコミットタイプ（feat, fix, docs等）とスコープを判定
"""

import json
import sys
from pathlib import Path
from typing import Any


def load_analysis() -> dict[str, Any]:
    """analyze_diff.pyの出力（JSON）を読み込み"""
    try:
        data = json.load(sys.stdin)
        return data
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)


def classify_type(analysis: dict[str, Any]) -> list[str]:
    """
    変更内容からコミットタイプを判定（複数候補を返す）

    優先順位の高い順に判定：
    1. テストファイルのみ → test
    2. ドキュメントのみ → docs
    3. CI設定ファイル → ci
    4. パッケージ管理ファイル → build
    5. 新規ファイル追加 → feat
    6. ファイル名に"fix"/"bug" → fix
    7. デフォルト → chore
    """
    files = analysis["files"]
    summary = analysis["summary"]

    if not files:
        print("Error: No files in analysis", file=sys.stderr)
        sys.exit(1)

    candidates = []
    file_types = [f["file_type"] for f in files]
    file_paths = [f["path"] for f in files]
    statuses = [f["status"] for f in files]

    # 1. テストファイルのみ
    test_indicators = ["test", "/tests/", "_test.", "test_"]
    if all(
        any(indicator in path.lower() for indicator in test_indicators)
        for path in file_paths
    ):
        candidates.append("test")

    # 2. ドキュメントのみ
    doc_types = {"markdown", "restructuredtext", "text"}
    if all(ft in doc_types for ft in file_types):
        candidates.append("docs")

    # 3. CI設定ファイル
    ci_indicators = [".github/workflows/", ".gitlab-ci", "ci.yml", "ci.yaml"]
    if any(any(ci in path.lower() for ci in ci_indicators) for path in file_paths):
        candidates.append("ci")

    # 4. パッケージ管理ファイル
    if "package_manager" in file_types:
        candidates.append("build")

    # 5. 新規ファイル追加
    if summary["new_files"] > 0 and "feat" not in candidates:
        candidates.append("feat")

    # 6. ファイル名に"fix"/"bug"を含む
    fix_indicators = ["fix", "bug", "patch"]
    if any(
        any(indicator in path.lower() for indicator in fix_indicators)
        for path in file_paths
    ):
        candidates.append("fix")

    # 7. refactor判定（既存ファイルの大幅変更）
    if (
        summary["modified_files"] > 0
        and summary["new_files"] == 0
        and all(s == "M" for s in statuses)
    ):
        # 追加と削除が両方ある場合はリファクタリングの可能性
        if summary["total_additions"] > 10 and summary["total_deletions"] > 10:
            candidates.append("refactor")

    # 8. style判定（設定ファイルや軽微な変更）
    style_indicators = [".editorconfig", ".prettierrc", "style", "format"]
    if any(
        any(indicator in path.lower() for indicator in style_indicators)
        for path in file_paths
    ):
        candidates.append("style")

    # デフォルト: chore（他に該当がない場合）
    if not candidates:
        candidates.append("chore")

    # 重複を除去しつつ順序を保持
    seen = set()
    unique_candidates = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            unique_candidates.append(c)

    return unique_candidates[:3]  # 最大3候補まで


def extract_scope(analysis: dict[str, Any]) -> str | None:
    """
    ディレクトリ構造からスコープを抽出

    例:
    - src/auth/* → "auth"
    - src/api/* → "api"
    - docs/* → None（ドキュメントはスコープ不要）
    - tests/* → None（テストはスコープ不要）
    """
    files = analysis["files"]
    if not files:
        return None

    file_paths = [f["path"] for f in files]

    # 除外パターン
    exclude_dirs = {"tests", "test", "docs", ".github", ".gitlab", "scripts"}

    # 共通ディレクトリを探す
    path_parts_list = [Path(p).parts for p in file_paths]

    # 最も共通する階層を見つける
    if not path_parts_list:
        return None

    # 全ファイルの最初のディレクトリを取得
    first_dirs = {parts[0] for parts in path_parts_list if len(parts) > 1}

    # 除外ディレクトリをフィルタ
    first_dirs = {d for d in first_dirs if d.lower() not in exclude_dirs}

    if not first_dirs:
        return None

    # 単一のディレクトリに集中している場合
    if len(first_dirs) == 1:
        first_dir = list(first_dirs)[0]

        # src/ 配下の場合、さらに深い階層をスコープに
        if first_dir == "src" and all(len(parts) > 1 for parts in path_parts_list):
            second_dirs = {parts[1] for parts in path_parts_list if len(parts) > 1}
            if len(second_dirs) == 1:
                return list(second_dirs)[0]

        return first_dir

    return None


def detect_breaking_changes(analysis: dict[str, Any]) -> bool:
    """
    Breaking Changesの可能性を検出

    以下のパターンをチェック：
    - 大量の削除（既存機能の削除の可能性）
    - APIファイルの変更
    - 設定ファイルのスキーマ変更
    """
    summary = analysis["summary"]
    files = analysis["files"]

    # 大量の削除（100行以上）
    if summary["total_deletions"] > 100:
        return True

    # APIファイルの変更
    api_indicators = ["api/", "/api.", "endpoint", "route"]
    if any(
        any(indicator in f["path"].lower() for indicator in api_indicators)
        for f in files
    ):
        # かつ、削除が多い場合
        if summary["total_deletions"] > 20:
            return True

    # 設定ファイルの大幅変更
    config_types = {"json", "yaml", "toml", "xml"}
    config_files = [f for f in files if f["file_type"] in config_types]
    if config_files:
        config_deletions = sum(f["deletions"] for f in config_files)
        if config_deletions > 10:
            return True

    return False


def generate_subject_suggestion(
    analysis: dict[str, Any], commit_type: str, scope: str | None
) -> str:
    """
    Subjectの提案を生成

    例:
    - feat(auth): add OAuth2 login support
    - fix(api): handle null response
    - docs: update installation guide
    """
    files = analysis["files"]
    summary = analysis["summary"]

    # ファイルパスから簡潔な説明を生成
    if summary["new_files"] > 0:
        # 新規ファイルの場合
        new_files = [f for f in files if f["status"] == "A"]
        if new_files:
            first_new = Path(new_files[0]["path"])
            action = "add"
            target = first_new.stem.replace("_", " ").replace("-", " ")
            return f"{action} {target}"

    elif commit_type == "fix":
        return "fix critical bug"

    elif commit_type == "docs":
        doc_files = [f for f in files if f["file_type"] in {"markdown", "text"}]
        if doc_files:
            doc_name = Path(doc_files[0]["path"]).stem
            return f"update {doc_name}"

    elif commit_type == "test":
        return "add tests"

    elif commit_type == "refactor":
        if scope:
            return f"refactor {scope} module"
        return "refactor code structure"

    # デフォルト
    if summary["modified_files"] > 0:
        return "update implementation"

    return "misc changes"


def main() -> None:
    """メイン処理"""
    # 標準入力からJSON読み込み
    analysis = load_analysis()

    # Type候補を生成
    type_candidates = classify_type(analysis)

    # Scope抽出
    scope = extract_scope(analysis)

    # Breaking Changes検出
    has_breaking = detect_breaking_changes(analysis)

    # Subject提案生成
    subject_suggestion = generate_subject_suggestion(
        analysis, type_candidates[0], scope
    )

    # 結果をJSON出力
    output = {
        "type_candidates": type_candidates,
        "scope": scope,
        "has_breaking_changes": has_breaking,
        "subject_suggestion": subject_suggestion,
        "recommended_format": (
            f"{type_candidates[0]}"
            + (f"({scope})" if scope else "")
            + ("!" if has_breaking else "")
            + f": {subject_suggestion}"
        ),
    }

    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
