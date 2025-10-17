"""LLM transform cache management (T064-T065).

This module provides caching functionality for LLM-transformed content to enable
incremental updates. Transformations are cached using MD5 hashes of original content
and stored in JSON format.

Implements FR-038e (Git diff integration with cache reuse for unchanged features).
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path


def compute_content_hash(content: str) -> str:
    """Compute MD5 hash of content (T065).

    Args:
        content: Original content to hash

    Returns:
        MD5 hash as 32-character hexadecimal string

    Example:
        >>> compute_content_hash("Hello, World!")
        '65a8e27d8879283831b664bd8b7f0ad4'
    """
    return hashlib.md5(content.encode("utf-8")).hexdigest()


class LLMTransformCache:
    """LLM transform cache manager (T064).

    Manages a persistent cache of LLM-transformed content, stored in
    .claude/.cache/llm-transforms.json. Cache entries are keyed by MD5
    hash of original content to enable fast lookups.

    Attributes:
        _cache_file: Path to cache JSON file
        _cache: In-memory cache dictionary

    Example:
        >>> cache = LLMTransformCache(Path(".claude/.cache/llm-transforms.json"))
        >>> cache.load_cache()
        >>> content_hash = compute_content_hash("original content")
        >>> cache.set_cached_transform(content_hash, "original", "transformed")
        >>> cache.save_cache()
        >>> result = cache.get_cached_transform(content_hash)
        >>> print(result)
        'transformed'
    """

    def __init__(self, cache_file: Path) -> None:
        """Initialize cache manager.

        Args:
            cache_file: Path to cache JSON file (typically .claude/.cache/llm-transforms.json)
        """
        self._cache_file = cache_file
        self._cache: dict[str, dict[str, str]] = {}

    def load_cache(self) -> None:
        """Load cache from JSON file (CHK003).

        If file doesn't exist or contains invalid JSON, initializes empty cache.
        This gracefully handles missing or corrupted cache files (CHK028).
        """
        if not self._cache_file.exists():
            self._cache = {}
            return

        try:
            with open(self._cache_file, encoding="utf-8") as f:
                self._cache = json.load(f)
        except (OSError, json.JSONDecodeError):
            # Gracefully handle corrupted cache file
            self._cache = {}

    def save_cache(self) -> None:
        """Save cache to JSON file (CHK004).

        Creates parent directory if it doesn't exist. Writes cache in human-readable
        JSON format with 2-space indentation.
        """
        self._cache_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self._cache_file, "w", encoding="utf-8") as f:
            json.dump(self._cache, f, indent=2, ensure_ascii=False)

    def get_cached_transform(self, content_hash: str) -> str | None:
        """Get cached transformation for given content hash (CHK005, CHK023).

        Args:
            content_hash: MD5 hash of original content

        Returns:
            Transformed content if cached, None if cache miss
        """
        entry = self._cache.get(content_hash)
        if entry is None:
            return None

        return entry.get("transformed_content")

    def set_cached_transform(
        self, content_hash: str, original_content: str, transformed_content: str
    ) -> None:
        """Set cached transformation for given content hash (CHK006).

        Args:
            content_hash: MD5 hash of original content
            original_content: Original content (for reference)
            transformed_content: LLM-transformed content
        """
        self._cache[content_hash] = {
            "original_content": original_content,
            "transformed_content": transformed_content,
            "timestamp": datetime.now().isoformat(),
        }
