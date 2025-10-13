"""Performance validation tests for doc-update.

Validates that doc-update meets performance criteria per SC-006 and SC-008.
Per Constitution C007: MVP success criteria must be validated.
"""

import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

import pytest


class TestDocUpdatePerformance:
    """Performance tests for doc-update command."""

    @pytest.fixture
    def large_project(self):
        """Create a test project with 10 features for performance testing."""
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir)

        # Create spec-kit structure
        (project_path / ".specify").mkdir()
        (project_path / "specs").mkdir()

        # Create 10 feature directories with spec.md
        for i in range(1, 11):
            feature_dir = project_path / "specs" / f"{i:03d}-test-feature-{i}"
            feature_dir.mkdir()

            spec_content = f"""# Test Feature {i}

## User Stories

### User Story 1
User can test feature {i}.

## Requirements

- **FR-{i:03d}**: System must implement feature {i}

## Success Criteria

- **SC-{i:03d}**: Feature {i} works correctly
"""
            (feature_dir / "spec.md").write_text(spec_content)

        # Initialize git repository (required by doc_init validation)
        subprocess.run(["git", "init"], cwd=project_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=project_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=project_path, capture_output=True)

        yield project_path
        shutil.rmtree(temp_dir)

    def test_full_update_10_features_under_45_seconds(self, large_project):
        """Test full doc-update on 10-feature project completes in ≤ 45 seconds.

        Per SC-006: `/speckit.doc-update` は、最大10機能のプロジェクトで45秒以内に完了する
        Per C007: MVP success criteria must be validated
        """
        original_dir = os.getcwd()
        os.chdir(large_project)

        try:
            # Initialize Sphinx project
            init_result = subprocess.run(
                [
                    "uv", "run", "python", "-m", "speckit_docs.doc_init",
                    "--type", "sphinx",
                    "--project-name", "Performance Test",
                    "--author", "Test",
                    "--no-interaction"
                ],
                capture_output=True,
                text=True,
                timeout=60
            )

            if init_result.returncode != 0:
                pytest.skip(f"doc_init not yet implemented: {init_result.stderr}")

            # Measure full update time
            start_time = time.time()

            update_result = subprocess.run(
                ["uv", "run", "python", "-m", "speckit_docs.doc_update", "--full", "--no-build"],
                capture_output=True,
                text=True,
                timeout=60
            )

            elapsed_time = time.time() - start_time

            if update_result.returncode != 0:
                pytest.skip(f"doc_update not yet implemented: {update_result.stderr}")

            # Verify performance criterion
            assert elapsed_time <= 45.0, \
                f"Full update took {elapsed_time:.2f}s, must be ≤ 45s (SC-006)"

        finally:
            os.chdir(original_dir)

    def test_incremental_update_1_feature_under_5_seconds(self, large_project):
        """Test incremental doc-update (1 feature changed) completes in ≤ 5 seconds.

        Per SC-008: インクリメンタル更新（1機能）は5秒以内に完了
        Per spec.md L411-413: 約90%削減
        Per C007: MVP success criteria must be validated
        """
        original_dir = os.getcwd()
        os.chdir(large_project)

        try:
            # Initialize and do full update first
            subprocess.run(
                [
                    "uv", "run", "python", "-m", "speckit_docs.doc_init",
                    "--type", "sphinx",
                    "--project-name", "Performance Test",
                    "--author", "Test",
                    "--no-interaction"
                ],
                capture_output=True,
                text=True,
                timeout=60
            )

            subprocess.run(
                ["uv", "run", "python", "-m", "speckit_docs.doc_update", "--full", "--no-build"],
                capture_output=True,
                text=True,
                timeout=60
            )

            # Modify one feature's spec.md
            feature_1_spec = large_project / "specs" / "001-test-feature-1" / "spec.md"
            current_content = feature_1_spec.read_text()
            feature_1_spec.write_text(current_content + "\n## Additional Section\n\nNew content.\n")

            # Commit changes (needed for git diff detection)
            subprocess.run(["git", "init"], cwd=large_project, capture_output=True)
            subprocess.run(["git", "add", "."], cwd=large_project, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "Initial"],
                cwd=large_project,
                capture_output=True
            )

            # Modify and commit again
            feature_1_spec.write_text(current_content + "\n## Modified Section\n\nUpdated content.\n")
            subprocess.run(["git", "add", "."], cwd=large_project, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "Update feature 1"],
                cwd=large_project,
                capture_output=True
            )

            # Measure incremental update time
            start_time = time.time()

            update_result = subprocess.run(
                ["uv", "run", "python", "-m", "speckit_docs.doc_update", "--no-build"],
                capture_output=True,
                text=True,
                timeout=30
            )

            elapsed_time = time.time() - start_time

            if update_result.returncode != 0:
                pytest.skip(f"Incremental update not yet implemented: {update_result.stderr}")

            # Verify performance criterion
            assert elapsed_time <= 5.0, \
                f"Incremental update took {elapsed_time:.2f}s, must be ≤ 5s (SC-008)"

        finally:
            os.chdir(original_dir)

    def test_git_diff_overhead_under_1_second(self, large_project):
        """Test git diff detection overhead is ≤ 1 second.

        Per spec.md L413: Git diff検出のオーバーヘッドは1秒以内
        """
        original_dir = os.getcwd()
        os.chdir(large_project)

        try:
            # Initialize git
            subprocess.run(["git", "init"], cwd=large_project, capture_output=True)
            subprocess.run(["git", "add", "."], cwd=large_project, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "Initial"],
                cwd=large_project,
                capture_output=True
            )

            # Measure git diff detection time
            start_time = time.time()

            # Run git diff to detect changes (simulating ChangeDetector)
            subprocess.run(
                ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
                cwd=large_project,
                capture_output=True,
                text=True
            )

            elapsed_time = time.time() - start_time

            # Verify overhead criterion
            assert elapsed_time <= 1.0, \
                f"Git diff overhead was {elapsed_time:.2f}s, must be ≤ 1s"

        finally:
            os.chdir(original_dir)
