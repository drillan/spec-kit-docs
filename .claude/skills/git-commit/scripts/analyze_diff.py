#!/usr/bin/env python3
"""
Git diff分析スクリプト

ステージされた変更を分析し、以下の情報を抽出：
- 変更ファイル一覧
- 追加/削除行数
- ファイルタイプ
- 変更パターン（新規/修正/削除/リネーム）
"""

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class FileChange:
    """ファイル変更情報"""

    path: str
    status: str  # 'A'=新規, 'M'=修正, 'D'=削除, 'R'=リネーム
    additions: int
    deletions: int
    file_type: str  # 拡張子ベース


@dataclass
class ChangeAnalysis:
    """変更分析結果"""

    files: list[FileChange]
    total_additions: int
    total_deletions: int
    new_files_count: int
    modified_files_count: int
    deleted_files_count: int


def run_git_command(args: list[str]) -> str:
    """gitコマンドを実行して結果を取得"""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: Git command failed: {e}", file=sys.stderr)
        print(f"stderr: {e.stderr}", file=sys.stderr)
        sys.exit(1)


def get_file_type(filepath: str) -> str:
    """ファイルパスから種類を判定"""
    path = Path(filepath)
    ext = path.suffix.lower()

    # 拡張子ベースの分類
    type_mapping = {
        # プログラミング言語
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".jsx": "javascript",
        ".tsx": "typescript",
        ".java": "java",
        ".go": "go",
        ".rs": "rust",
        ".c": "c",
        ".cpp": "cpp",
        ".rb": "ruby",
        ".php": "php",
        # ドキュメント
        ".md": "markdown",
        ".rst": "restructuredtext",
        ".txt": "text",
        # 設定ファイル
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".toml": "toml",
        ".xml": "xml",
        ".ini": "ini",
        # Web
        ".html": "html",
        ".css": "css",
        ".scss": "scss",
        # データ
        ".sql": "sql",
        ".csv": "csv",
        # その他
        ".sh": "shell",
        ".bash": "shell",
        ".dockerfile": "dockerfile",
    }

    # 特殊なファイル名
    name_mapping = {
        "dockerfile": "dockerfile",
        "makefile": "makefile",
        "package.json": "package_manager",
        "requirements.txt": "package_manager",
        "pyproject.toml": "package_manager",
        "cargo.toml": "package_manager",
        ".gitignore": "git_config",
        ".gitlab-ci.yml": "ci_config",
    }

    filename_lower = path.name.lower()
    if filename_lower in name_mapping:
        return name_mapping[filename_lower]

    return type_mapping.get(ext, "other")


def parse_diff_stat(diff_stat: str) -> list[FileChange]:
    """git diff --stat の出力を解析"""
    changes = []
    lines = diff_stat.strip().split("\n")

    for line in lines[:-1]:  # 最後の行はサマリーなので除外
        if not line.strip():
            continue

        # フォーマット: " path/to/file.ext | 10 +++++-----"
        parts = line.split("|")
        if len(parts) != 2:
            continue

        filepath = parts[0].strip()
        stats = parts[1].strip()

        # +と-の数を数える
        additions = stats.count("+")
        deletions = stats.count("-")

        changes.append(
            FileChange(
                path=filepath,
                status="M",  # デフォルトは修正
                additions=additions,
                deletions=deletions,
                file_type=get_file_type(filepath),
            )
        )

    return changes


def get_file_status(filepath: str) -> str:
    """ファイルのgitステータスを取得"""
    status_output = run_git_command(["diff", "--staged", "--name-status"])

    for line in status_output.strip().split("\n"):
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) >= 2:
            status = parts[0]
            file_path = parts[1]
            if file_path == filepath:
                return status[0]  # 'A', 'M', 'D', 'R' など

    return "M"  # デフォルト


def analyze_staged_changes() -> ChangeAnalysis:
    """ステージされた変更を分析"""
    # ステージされたファイルがあるか確認
    status_output = run_git_command(["diff", "--staged", "--name-only"])
    if not status_output.strip():
        print("Error: No staged changes found. Run 'git add' first.", file=sys.stderr)
        sys.exit(1)

    # git diff --stat で統計情報取得
    diff_stat = run_git_command(["diff", "--staged", "--stat"])
    changes = parse_diff_stat(diff_stat)

    # 各ファイルのステータスを取得
    for change in changes:
        change.status = get_file_status(change.path)

    # 集計
    total_additions = sum(c.additions for c in changes)
    total_deletions = sum(c.deletions for c in changes)
    new_files_count = sum(1 for c in changes if c.status == "A")
    modified_files_count = sum(1 for c in changes if c.status == "M")
    deleted_files_count = sum(1 for c in changes if c.status == "D")

    return ChangeAnalysis(
        files=changes,
        total_additions=total_additions,
        total_deletions=total_deletions,
        new_files_count=new_files_count,
        modified_files_count=modified_files_count,
        deleted_files_count=deleted_files_count,
    )


def main() -> None:
    """メイン処理"""
    analysis = analyze_staged_changes()

    # JSON形式で出力
    output = {
        "files": [
            {
                "path": c.path,
                "status": c.status,
                "additions": c.additions,
                "deletions": c.deletions,
                "file_type": c.file_type,
            }
            for c in analysis.files
        ],
        "summary": {
            "total_files": len(analysis.files),
            "total_additions": analysis.total_additions,
            "total_deletions": analysis.total_deletions,
            "new_files": analysis.new_files_count,
            "modified_files": analysis.modified_files_count,
            "deleted_files": analysis.deleted_files_count,
        },
    }

    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
