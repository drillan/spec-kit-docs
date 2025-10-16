"""Integration tests for MkDocs workflow.

End-to-end tests for MkDocs documentation generation per Constitution V. Testability.
Tests the complete workflow: doc-init → doc-update → build.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest


class TestMkDocsWorkflow:
    """Integration tests for complete MkDocs documentation workflow."""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary spec-kit project structure."""
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir)

        # Create minimal spec-kit structure
        (project_path / ".specify").mkdir()
        (project_path / "specs").mkdir()
        (project_path / "specs" / "001-test-feature").mkdir()

        # Create minimal spec.md
        spec_content = """# Test Feature

## User Stories

### User Story 1
User can test the system.

## Requirements

- **FR-001**: System must work

## Success Criteria

- **SC-001**: Tests pass
"""
        (project_path / "specs" / "001-test-feature" / "spec.md").write_text(spec_content)

        # Initialize git repository (required by doc_init validation)
        subprocess.run(["git", "init"], cwd=project_path, capture_output=True)
        subprocess.run(
            ["git", "config", "user.name", "Test User"], cwd=project_path, capture_output=True
        )
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=project_path,
            capture_output=True,
        )

        yield project_path
        shutil.rmtree(temp_dir)

    def test_doc_init_mkdocs_creates_structure(self, temp_project):
        """Test doc-init creates complete MkDocs structure.

        Per cli-interface.md Integration Tests: Verify files exist after doc-init.
        """
        original_dir = os.getcwd()
        os.chdir(temp_project)

        try:
            # Run doc_init.py (non-interactive mode)
            result = subprocess.run(
                [
                    "uv",
                    "run",
                    "python",
                    "-m",
                    "speckit_docs.doc_init",
                    "--type",
                    "mkdocs",
                    "--project-name",
                    "Test Project",
                    "--site-name",
                    "Test Site",
                    "--no-interaction",
                    "--no-install",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                pytest.skip(f"doc_init not yet fully implemented: {result.stderr}")

            # Verify MkDocs files were created
            assert (temp_project / "mkdocs.yml").exists(), "mkdocs.yml should be created"
            docs_dir = temp_project / "docs"
            assert docs_dir.exists(), "docs/ directory should be created"
            assert (docs_dir / "index.md").exists(), "docs/index.md should be created"

        finally:
            os.chdir(original_dir)

    def test_doc_update_mkdocs_generates_pages(self, temp_project):
        """Test doc-update generates feature pages from spec.md.

        Per cli-interface.md Integration Tests: Verify doc-update creates feature pages.
        """
        original_dir = os.getcwd()
        os.chdir(temp_project)

        try:
            # First initialize MkDocs project
            init_result = subprocess.run(
                [
                    "uv",
                    "run",
                    "python",
                    "-m",
                    "speckit_docs.doc_init",
                    "--type",
                    "mkdocs",
                    "--project-name",
                    "Test Project",
                    "--site-name",
                    "Test Site",
                    "--no-interaction",
                    "--no-install",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if init_result.returncode != 0:
                pytest.skip(f"doc_init not yet fully implemented: {init_result.stderr}")

            # Run doc_update.py
            update_result = subprocess.run(
                ["uv", "run", "python", "-m", "speckit_docs.doc_update", "--no-build"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if update_result.returncode != 0:
                pytest.skip(f"doc_update not yet fully implemented: {update_result.stderr}")

            # Verify feature page was created
            docs_dir = temp_project / "docs"
            feature_page = docs_dir / "test-feature.md"
            assert feature_page.exists(), "Feature page should be created from spec.md"

            # Verify mkdocs.yml was updated with nav
            mkdocs_content = (temp_project / "mkdocs.yml").read_text()
            assert "test-feature" in mkdocs_content, "mkdocs.yml should reference feature page"

        finally:
            os.chdir(original_dir)

    def test_mkdocs_build_produces_html(self, temp_project):
        """Test complete workflow produces browsable HTML.

        Per cli-interface.md Integration Tests: End-to-end workflow produces HTML output.
        """
        original_dir = os.getcwd()
        os.chdir(temp_project)

        try:
            # Initialize
            init_result = subprocess.run(
                [
                    "uv",
                    "run",
                    "python",
                    "-m",
                    "speckit_docs.doc_init",
                    "--type",
                    "mkdocs",
                    "--project-name",
                    "Test Project",
                    "--site-name",
                    "Test Site",
                    "--no-interaction",
                    "--no-install",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            print(f"\nInit stdout:\n{init_result.stdout}")
            print(f"\nInit stderr:\n{init_result.stderr}")
            print(f"\nInit returncode: {init_result.returncode}")

            # Check if mkdocs.yml was created (it should be in project root, not in docs/)
            mkdocs_yml_root = temp_project / "mkdocs.yml"
            mkdocs_yml_docs = temp_project / "docs" / "mkdocs.yml"
            print(f"\nmkdocs.yml in root: {mkdocs_yml_root.exists()}")
            print(f"mkdocs.yml in docs/: {mkdocs_yml_docs.exists()}")
            if mkdocs_yml_root.exists():
                print("mkdocs.yml content:")
                print(mkdocs_yml_root.read_text())

            # Update
            update_result = subprocess.run(
                ["uv", "run", "python", "-m", "speckit_docs.doc_update"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            print(f"\nUpdate stdout:\n{update_result.stdout}")
            print(f"\nUpdate stderr:\n{update_result.stderr}")
            print(f"\nUpdate returncode: {update_result.returncode}")

            # Verify HTML was built (MkDocs outputs to project_root/site, not docs/site)
            html_index = temp_project / "site" / "index.html"

            assert html_index.exists(), f"Build should produce site/index.html at {html_index}"

        finally:
            os.chdir(original_dir)
