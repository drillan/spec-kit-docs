"""Unit tests for LLM transform cache (T062).

This module tests the LLMTransformCache class and compute_content_hash() function.
Tests are written before implementation (TDD, C010).
"""

import json
from pathlib import Path

import pytest

from speckit_docs.utils.cache import LLMTransformCache, compute_content_hash


class TestComputeContentHash:
    """Test compute_content_hash() function (T065)."""

    def test_compute_content_hash_basic(self):
        """Test MD5 hash generation for simple content."""
        content = "Hello, World!"
        hash_result = compute_content_hash(content)

        # MD5 hash should be 32 hex characters
        assert len(hash_result) == 32
        assert all(c in "0123456789abcdef" for c in hash_result)

        # Same content should produce same hash
        assert compute_content_hash(content) == hash_result

    def test_compute_content_hash_different_content(self):
        """Test that different content produces different hashes."""
        content1 = "Hello, World!"
        content2 = "Hello, World"  # Missing exclamation mark

        hash1 = compute_content_hash(content1)
        hash2 = compute_content_hash(content2)

        assert hash1 != hash2

    def test_compute_content_hash_empty_string(self):
        """Test hash generation for empty string."""
        content = ""
        hash_result = compute_content_hash(content)

        # Empty string should still produce a valid hash
        assert len(hash_result) == 32
        assert all(c in "0123456789abcdef" for c in hash_result)

    def test_compute_content_hash_unicode(self):
        """Test hash generation for Unicode content."""
        content = "こんにちは、世界！"
        hash_result = compute_content_hash(content)

        # Unicode content should produce valid hash
        assert len(hash_result) == 32
        assert all(c in "0123456789abcdef" for c in hash_result)

        # Same Unicode content should produce same hash
        assert compute_content_hash(content) == hash_result


class TestLLMTransformCache:
    """Test LLMTransformCache class (T064)."""

    @pytest.fixture
    def cache_file(self, tmp_path: Path) -> Path:
        """Create temporary cache file path."""
        return tmp_path / ".claude" / ".cache" / "llm-transforms.json"

    @pytest.fixture
    def cache(self, cache_file: Path) -> LLMTransformCache:
        """Create LLMTransformCache instance."""
        return LLMTransformCache(cache_file)

    def test_load_cache_empty(self, cache: LLMTransformCache):
        """Test loading cache when file doesn't exist."""
        cache.load_cache()

        # Cache should be empty dictionary
        assert cache._cache == {}

    def test_load_cache_existing(self, cache_file: Path, cache: LLMTransformCache):
        """Test loading cache when file exists with valid JSON."""
        # Create cache file with test data
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        test_data = {
            "abc123": {
                "original_content": "Test content",
                "transformed_content": "Transformed test content",
                "timestamp": "2025-10-17T12:00:00",
            }
        }
        cache_file.write_text(json.dumps(test_data))

        cache.load_cache()

        # Cache should contain test data
        assert cache._cache == test_data

    def test_load_cache_invalid_json(self, cache_file: Path, cache: LLMTransformCache):
        """Test loading cache when file contains invalid JSON."""
        # Create cache file with invalid JSON
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cache_file.write_text("invalid json content")

        cache.load_cache()

        # Cache should be empty dictionary (graceful handling)
        assert cache._cache == {}

    def test_save_cache_creates_directory(self, cache_file: Path, cache: LLMTransformCache):
        """Test that save_cache() creates parent directory if it doesn't exist."""
        # Add test entry
        cache._cache["test123"] = {
            "original_content": "Test",
            "transformed_content": "Transformed",
            "timestamp": "2025-10-17T12:00:00",
        }

        cache.save_cache()

        # Directory should be created
        assert cache_file.parent.exists()

        # File should exist with correct content
        assert cache_file.exists()
        saved_data = json.loads(cache_file.read_text())
        assert saved_data == cache._cache

    def test_get_cached_transform_hit(self, cache: LLMTransformCache):
        """Test cache hit (CHK023)."""
        # Setup cache
        content_hash = "abc123"
        cache._cache[content_hash] = {
            "original_content": "Test content",
            "transformed_content": "Transformed test content",
            "timestamp": "2025-10-17T12:00:00",
        }

        result = cache.get_cached_transform(content_hash)

        assert result == "Transformed test content"

    def test_get_cached_transform_miss(self, cache: LLMTransformCache):
        """Test cache miss (CHK023)."""
        # Cache is empty
        result = cache.get_cached_transform("nonexistent_hash")

        assert result is None

    def test_set_cached_transform(self, cache: LLMTransformCache):
        """Test setting cache entry."""
        content_hash = "xyz789"
        original_content = "Original content"
        transformed_content = "Transformed content"

        cache.set_cached_transform(content_hash, original_content, transformed_content)

        # Cache should contain the new entry
        assert content_hash in cache._cache
        entry = cache._cache[content_hash]
        assert entry["original_content"] == original_content
        assert entry["transformed_content"] == transformed_content
        assert "timestamp" in entry

    def test_md5_hash_validation(self, cache: LLMTransformCache):
        """Test MD5 hash validation (CHK024)."""
        original_content = "Test content for MD5 validation"
        expected_hash = compute_content_hash(original_content)

        # Set cache entry with computed hash
        cache.set_cached_transform(expected_hash, original_content, "Transformed")

        # Retrieve using the same hash
        result = cache.get_cached_transform(expected_hash)
        assert result == "Transformed"

        # Different content should have different hash
        different_content = "Different content"
        different_hash = compute_content_hash(different_content)
        assert different_hash != expected_hash

        # Cache miss for different hash
        assert cache.get_cached_transform(different_hash) is None
