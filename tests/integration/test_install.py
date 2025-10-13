"""Integration tests for install functionality (T014)."""

import subprocess

from speckit_docs.cli.install_handler import install_handler


class TestInstallIntegration:
    """End-to-end integration tests for install command."""

    def test_install_end_to_end(self, tmp_path, monkeypatch):
        """Test install command end-to-end with all file copying."""
        # Create spec-kit project structure
        (tmp_path / ".specify").mkdir()
        (tmp_path / ".claude").mkdir()
        monkeypatch.chdir(tmp_path)

        # Execute install command
        install_handler(force=True)

        # Verify command templates were copied
        assert (tmp_path / ".claude" / "commands" / "doc-init.md").exists()
        assert (tmp_path / ".claude" / "commands" / "doc-update.md").exists()

        # Verify command template content
        doc_init_content = (tmp_path / ".claude" / "commands" / "doc-init.md").read_text()
        assert "[Active Rules: C001-C014]" in doc_init_content
        assert "CRITICAL原則" in doc_init_content
        assert "/doc-init" in doc_init_content

        # Verify backend scripts were copied
        assert (tmp_path / ".specify" / "scripts" / "docs" / "doc_init.py").exists()
        assert (tmp_path / ".specify" / "scripts" / "docs" / "doc_update.py").exists()
        assert (tmp_path / ".specify" / "scripts" / "docs" / "__init__.py").exists()

        # Verify scripts are executable
        result = subprocess.run(
            [
                "uv",
                "run",
                "python",
                tmp_path / ".specify" / "scripts" / "docs" / "doc_init.py",
                "--help",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "--type" in result.stdout or "sphinx" in result.stdout

        result = subprocess.run(
            [
                "uv",
                "run",
                "python",
                tmp_path / ".specify" / "scripts" / "docs" / "doc_update.py",
                "--help",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "--incremental" in result.stdout or "full" in result.stdout

    def test_install_creates_directories(self, tmp_path, monkeypatch):
        """Test that install command creates necessary directories."""
        # Create only base directories
        (tmp_path / ".specify").mkdir()
        (tmp_path / ".claude").mkdir()
        monkeypatch.chdir(tmp_path)

        # Execute install command
        install_handler(force=True)

        # Verify subdirectories were created
        assert (tmp_path / ".claude" / "commands").exists()
        assert (tmp_path / ".specify" / "scripts" / "docs").exists()

    def test_install_preserves_existing_files_with_force(self, tmp_path, monkeypatch):
        """Test that force=True overwrites existing files."""
        # Create project structure with existing files
        (tmp_path / ".specify").mkdir()
        (tmp_path / ".claude").mkdir()
        (tmp_path / ".claude" / "commands").mkdir()

        existing_file = tmp_path / ".claude" / "commands" / "doc-init.md"
        existing_file.write_text("old content")
        monkeypatch.chdir(tmp_path)

        # Execute install command with force
        install_handler(force=True)

        # Verify file was overwritten
        new_content = existing_file.read_text()
        assert new_content != "old content"
        assert "[Active Rules: C001-C014]" in new_content

    def test_install_script_functionality(self, tmp_path, monkeypatch):
        """Test that installed scripts have correct functionality."""
        # Setup and install
        (tmp_path / ".specify").mkdir()
        (tmp_path / ".claude").mkdir()
        monkeypatch.chdir(tmp_path)

        install_handler(force=True)

        # Test doc_init.py with various arguments
        script_path = tmp_path / ".specify" / "scripts" / "docs" / "doc_init.py"
        result = subprocess.run(
            [
                "uv",
                "run",
                "python",
                str(script_path),
                "--type",
                "sphinx",
                "--project-name",
                "TestProject",
                "--version",
                "1.0.0",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "sphinx" in result.stdout.lower()
        assert "ドキュメントプロジェクトの初期化が完了しました" in result.stdout

        # Test doc_update.py with arguments
        script_path = tmp_path / ".specify" / "scripts" / "docs" / "doc_update.py"
        result = subprocess.run(
            ["uv", "run", "python", str(script_path), "--full"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "フル" in result.stdout or "full" in result.stdout.lower()
