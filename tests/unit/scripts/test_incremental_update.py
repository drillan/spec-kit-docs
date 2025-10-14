"""Unit tests for incremental update functionality (T026)."""

from git import Repo

from speckit_docs.scripts.doc_update import main


class TestIncrementalUpdate:
    """Tests for incremental update with Git diff detection."""

    def test_incremental_update_detects_changed_features(self, tmp_path, monkeypatch):
        """Test that incremental update only processes changed features (FR-019)."""
        # Setup Git repository
        repo = Repo.init(tmp_path)
        repo.config_writer().set_value("user", "name", "Test User").release()
        repo.config_writer().set_value("user", "email", "test@example.com").release()

        monkeypatch.chdir(tmp_path)
        (tmp_path / ".specify").mkdir()

        # Create Sphinx docs directory
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "conf.py").write_text("# Sphinx config")
        (docs_dir / "index.md").write_text("# Documentation\n\n")

        # Create initial features
        (tmp_path / "specs" / "001-feature-one").mkdir(parents=True)
        (tmp_path / "specs" / "001-feature-one" / "spec.md").write_text(
            "# Feature One\n\nInitial version"
        )

        (tmp_path / "specs" / "002-feature-two").mkdir(parents=True)
        (tmp_path / "specs" / "002-feature-two" / "spec.md").write_text(
            "# Feature Two\n\nInitial version"
        )

        # Initial commit
        repo.index.add(["*"])
        repo.index.commit("Initial commit")

        # Run initial full update
        result = main(incremental=False)
        assert result == 0

        # Modify only one feature
        (tmp_path / "specs" / "001-feature-one" / "spec.md").write_text(
            "# Feature One\n\nUpdated version"
        )

        # Commit the change
        repo.index.add(["specs/001-feature-one/spec.md"])
        repo.index.commit("Update feature one")

        # Run incremental update
        result = main(incremental=True)

        # Should succeed
        assert result == 0

        # Feature one should be updated
        feature_one_content = (docs_dir / "feature-one.md").read_text()
        assert "Updated version" in feature_one_content

    def test_incremental_update_skips_if_no_changes(self, tmp_path, monkeypatch):
        """Test that incremental update skips if no changes detected."""
        # Setup Git repository
        repo = Repo.init(tmp_path)
        repo.config_writer().set_value("user", "name", "Test User").release()
        repo.config_writer().set_value("user", "email", "test@example.com").release()

        monkeypatch.chdir(tmp_path)
        (tmp_path / ".specify").mkdir()

        # Create Sphinx docs directory
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "conf.py").write_text("# Sphinx config")
        (docs_dir / "index.md").write_text("# Documentation\n\n")

        # Create feature
        (tmp_path / "specs" / "001-test-feature").mkdir(parents=True)
        (tmp_path / "specs" / "001-test-feature" / "spec.md").write_text("# Test Feature")

        # Initial commit
        repo.index.add(["*"])
        repo.index.commit("Initial commit")

        # Run incremental update with no changes
        result = main(incremental=True)

        # Should succeed and skip update
        assert result == 0

    def test_full_update_processes_all_features(self, tmp_path, monkeypatch):
        """Test that --full flag processes all features regardless of changes."""
        # Setup Git repository
        repo = Repo.init(tmp_path)
        repo.config_writer().set_value("user", "name", "Test User").release()
        repo.config_writer().set_value("user", "email", "test@example.com").release()

        monkeypatch.chdir(tmp_path)
        (tmp_path / ".specify").mkdir()

        # Create Sphinx docs directory
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "conf.py").write_text("# Sphinx config")
        (docs_dir / "index.md").write_text("# Documentation\n\n")

        # Create multiple features
        (tmp_path / "specs" / "001-feature-one").mkdir(parents=True)
        (tmp_path / "specs" / "001-feature-one" / "spec.md").write_text("# Feature One")

        (tmp_path / "specs" / "002-feature-two").mkdir(parents=True)
        (tmp_path / "specs" / "002-feature-two" / "spec.md").write_text("# Feature Two")

        # Initial commit
        repo.index.add(["*"])
        repo.index.commit("Initial commit")

        # Run full update
        result = main(incremental=False)

        # Should succeed
        assert result == 0

        # All features should be processed
        assert (docs_dir / "feature-one.md").exists()
        assert (docs_dir / "feature-two.md").exists()

    def test_incremental_update_handles_new_feature(self, tmp_path, monkeypatch):
        """Test that incremental update handles newly added features."""
        # Setup Git repository
        repo = Repo.init(tmp_path)
        repo.config_writer().set_value("user", "name", "Test User").release()
        repo.config_writer().set_value("user", "email", "test@example.com").release()

        monkeypatch.chdir(tmp_path)
        (tmp_path / ".specify").mkdir()

        # Create Sphinx docs directory
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "conf.py").write_text("# Sphinx config")
        (docs_dir / "index.md").write_text("# Documentation\n\n")

        # Create initial feature
        (tmp_path / "specs" / "001-feature-one").mkdir(parents=True)
        (tmp_path / "specs" / "001-feature-one" / "spec.md").write_text("# Feature One")

        # Initial commit
        repo.index.add(["*"])
        repo.index.commit("Initial commit")

        # Add new feature
        (tmp_path / "specs" / "002-new-feature").mkdir(parents=True)
        (tmp_path / "specs" / "002-new-feature" / "spec.md").write_text("# New Feature")

        # Commit the new feature
        repo.index.add(["specs/002-new-feature"])
        repo.index.commit("Add new feature")

        # Run incremental update
        result = main(incremental=True)

        # Should succeed
        assert result == 0

        # New feature should be generated
        assert (docs_dir / "new-feature.md").exists()

    def test_incremental_update_first_commit(self, tmp_path, monkeypatch):
        """Test incremental update on first commit (no HEAD~1)."""
        # Setup Git repository (no commits yet)
        repo = Repo.init(tmp_path)
        repo.config_writer().set_value("user", "name", "Test User").release()
        repo.config_writer().set_value("user", "email", "test@example.com").release()

        monkeypatch.chdir(tmp_path)
        (tmp_path / ".specify").mkdir()

        # Create Sphinx docs directory
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "conf.py").write_text("# Sphinx config")
        (docs_dir / "index.md").write_text("# Documentation\n\n")

        # Create feature
        (tmp_path / "specs" / "001-test-feature").mkdir(parents=True)
        (tmp_path / "specs" / "001-test-feature" / "spec.md").write_text("# Test Feature")

        # Add but don't commit yet
        repo.index.add(["*"])

        # Run incremental update (should fall back to full update)
        result = main(incremental=True)

        # Should succeed (falls back to full update since no commits)
        assert result == 0
