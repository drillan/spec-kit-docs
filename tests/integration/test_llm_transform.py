"""Integration tests for LLM transform workflow (T063).

This module tests the complete LLM transform workflow including:
- Successful transformation
- Cache reuse
- Error handling

Tests are written before implementation (TDD, C010).
"""

from pathlib import Path

import pytest

from speckit_docs.utils.cache import LLMTransformCache, compute_content_hash


class TestLLMTransformWorkflow:
    """Integration tests for LLM transform workflow (CHK025-CHK028)."""

    @pytest.fixture
    def temp_cache_dir(self, tmp_path: Path) -> Path:
        """Create temporary cache directory."""
        cache_dir = tmp_path / ".claude" / ".cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir

    @pytest.fixture
    def cache_file(self, temp_cache_dir: Path) -> Path:
        """Create cache file path."""
        return temp_cache_dir / "llm-transforms.json"

    @pytest.fixture
    def cache(self, cache_file: Path) -> LLMTransformCache:
        """Create LLMTransformCache instance."""
        return LLMTransformCache(cache_file)

    def test_successful_transform(self, cache: LLMTransformCache):
        """Test successful LLM transformation workflow (CHK026)."""
        # Given: Original content
        original_content = "FR-001: System MUST detect all feature directories"

        # When: Transform content (simulated)
        transformed_content = "ユーザーは、すべての機能ディレクトリを自動検出できます"
        content_hash = compute_content_hash(original_content)

        # Store in cache
        cache.set_cached_transform(content_hash, original_content, transformed_content)
        cache.save_cache()

        # Then: Cache should contain the transformation
        assert cache.get_cached_transform(content_hash) == transformed_content

        # Verify persistence
        new_cache = LLMTransformCache(cache._cache_file)
        new_cache.load_cache()
        assert new_cache.get_cached_transform(content_hash) == transformed_content

    def test_cache_reuse(self, cache: LLMTransformCache):
        """Test cache reuse for unchanged content (CHK027)."""
        # Given: Content already in cache
        original_content = "FR-002: System MUST generate documentation"
        transformed_content = "ユーザーは、仕様からドキュメントを生成できます"
        content_hash = compute_content_hash(original_content)

        cache.set_cached_transform(content_hash, original_content, transformed_content)
        cache.save_cache()

        # When: Same content is requested again
        cached_result = cache.get_cached_transform(content_hash)

        # Then: Should return cached transformation without re-transformation
        assert cached_result == transformed_content

    def test_cache_miss_for_modified_content(self, cache: LLMTransformCache):
        """Test cache miss when content is modified."""
        # Given: Original content in cache
        original_content = "FR-003: System MUST support Sphinx and MkDocs"
        transformed_content = "ユーザーは、SphinxとMkDocsを選択できます"
        original_hash = compute_content_hash(original_content)

        cache.set_cached_transform(original_hash, original_content, transformed_content)

        # When: Content is modified
        modified_content = "FR-003: System MUST support Sphinx, MkDocs, and Docusaurus"
        modified_hash = compute_content_hash(modified_content)

        # Then: Cache miss for modified content
        assert modified_hash != original_hash
        assert cache.get_cached_transform(modified_hash) is None

        # But original content still in cache
        assert cache.get_cached_transform(original_hash) == transformed_content

    def test_error_handling(self, cache_file: Path):
        """Test error handling for corrupted cache file (CHK028)."""
        # Given: Corrupted cache file
        cache_file.write_text("{ invalid json content")

        # When: Loading cache
        cache = LLMTransformCache(cache_file)
        cache.load_cache()

        # Then: Should gracefully handle error (empty cache)
        assert cache._cache == {}

        # Should be able to continue with new entries
        test_hash = compute_content_hash("test")
        cache.set_cached_transform(test_hash, "test", "transformed")
        assert cache.get_cached_transform(test_hash) == "transformed"

    def test_multiple_features_cache_workflow(self, cache: LLMTransformCache):
        """Test workflow with multiple features."""
        # Given: Multiple features to transform
        features = [
            ("FR-001: Feature 1", "機能1の説明"),
            ("FR-002: Feature 2", "機能2の説明"),
            ("FR-003: Feature 3", "機能3の説明"),
        ]

        # When: Transform and cache all features
        for original, transformed in features:
            content_hash = compute_content_hash(original)
            cache.set_cached_transform(content_hash, original, transformed)

        cache.save_cache()

        # Then: All transformations should be cached
        for original, transformed in features:
            content_hash = compute_content_hash(original)
            assert cache.get_cached_transform(content_hash) == transformed

        # Verify cache file contains all entries
        new_cache = LLMTransformCache(cache._cache_file)
        new_cache.load_cache()
        assert len(new_cache._cache) == 3

    def test_cache_statistics(self, cache: LLMTransformCache):
        """Test cache hit/miss statistics tracking."""
        # Setup: Add some entries to cache
        entries = {
            "content1": ("original1", "transformed1"),
            "content2": ("original2", "transformed2"),
        }

        for content, (original, transformed) in entries.items():
            content_hash = compute_content_hash(original)
            cache.set_cached_transform(content_hash, original, transformed)

        # Test cache hits
        hits = 0
        for content, (original, _) in entries.items():
            content_hash = compute_content_hash(original)
            if cache.get_cached_transform(content_hash) is not None:
                hits += 1

        assert hits == 2  # All should be hits

        # Test cache miss
        new_hash = compute_content_hash("new_content")
        assert cache.get_cached_transform(new_hash) is None
