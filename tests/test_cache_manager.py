"""Tests for cache_manager module."""

import pytest
from pathlib import Path
from datetime import datetime, timedelta
from src.utils.cache_manager import CacheManager


@pytest.mark.unit
class TestCacheManager:
    """Test cases for CacheManager class."""

    def test_init(self, temp_project_dir):
        """Test CacheManager initialization."""
        cache_mgr = CacheManager(temp_project_dir)

        assert cache_mgr.project_path == temp_project_dir
        assert cache_mgr.cache_dir == temp_project_dir / '.vibe-auditor-cache'
        assert cache_mgr.cache_file == temp_project_dir / '.vibe-auditor-cache' / 'cache.json'
        assert cache_mgr.cache_ttl == timedelta(hours=24)

    def test_ensure_cache_dir(self, temp_project_dir):
        """Test cache directory creation."""
        cache_mgr = CacheManager(temp_project_dir)

        assert cache_mgr.cache_dir.exists()
        assert cache_mgr.cache_dir.is_dir()

    def test_save_and_get_cached_result(self, temp_project_dir):
        """Test saving and retrieving cached results."""
        cache_mgr = CacheManager(temp_project_dir)

        cache_key = "test_analysis"
        test_result = {"issues": [], "total": 0}

        # Save result
        cache_mgr.save_result(cache_key, test_result)

        # Retrieve result
        cached = cache_mgr.get_cached_result(cache_key)

        assert cached is not None
        assert cached == test_result

    def test_cache_miss(self, temp_project_dir):
        """Test cache miss for non-existent key."""
        cache_mgr = CacheManager(temp_project_dir)

        cached = cache_mgr.get_cached_result("non_existent_key")

        assert cached is None

    def test_cache_invalidation_with_file_changes(self, temp_project_dir, sample_python_file):
        """Test cache invalidation when project files change."""
        cache_mgr = CacheManager(temp_project_dir)

        cache_key = "test_analysis"
        test_result = {"issues": [], "total": 0}
        project_files = [sample_python_file]

        # Save result with project files
        cache_mgr.save_result(cache_key, test_result, project_files)

        # Get cached result with same files
        cached = cache_mgr.get_cached_result(cache_key, project_files)
        assert cached is not None

        # Modify file
        sample_python_file.write_text("# Modified content")

        # Cache should be invalidated
        cached_after_change = cache_mgr.get_cached_result(cache_key, project_files)
        assert cached_after_change is None

    def test_cache_ttl_expiration(self, temp_project_dir):
        """Test cache expiration based on TTL."""
        # Create cache manager with 0-hour TTL
        cache_mgr = CacheManager(temp_project_dir, cache_ttl_hours=0)

        cache_key = "test_analysis"
        test_result = {"issues": [], "total": 0}

        # Save result
        cache_mgr.save_result(cache_key, test_result)

        # Should be expired immediately
        cached = cache_mgr.get_cached_result(cache_key)
        assert cached is None

    def test_invalidate_specific_key(self, temp_project_dir):
        """Test invalidating a specific cache key."""
        cache_mgr = CacheManager(temp_project_dir)

        # Save multiple keys
        cache_mgr.save_result("key1", {"data": 1})
        cache_mgr.save_result("key2", {"data": 2})

        # Invalidate key1
        cache_mgr.invalidate("key1")

        # key1 should be invalidated, key2 should still exist
        assert cache_mgr.get_cached_result("key1") is None
        assert cache_mgr.get_cached_result("key2") is not None

    def test_invalidate_all(self, temp_project_dir):
        """Test invalidating all cache."""
        cache_mgr = CacheManager(temp_project_dir)

        # Save some keys
        cache_mgr.save_result("key1", {"data": 1})
        cache_mgr.save_result("key2", {"data": 2})

        # Invalidate all
        cache_mgr.invalidate()

        # Cache file should be deleted
        assert not cache_mgr.cache_file.exists()

    def test_get_cache_stats(self, temp_project_dir):
        """Test getting cache statistics."""
        cache_mgr = CacheManager(temp_project_dir)

        # Save some entries
        cache_mgr.save_result("key1", {"data": 1})
        cache_mgr.save_result("key2", {"data": 2})

        stats = cache_mgr.get_cache_stats()

        assert stats['total_entries'] == 2
        assert len(stats['entries']) == 2
        assert all('key' in entry for entry in stats['entries'])
        assert all('timestamp' in entry for entry in stats['entries'])
        assert all('age_hours' in entry for entry in stats['entries'])

    def test_cleanup_expired(self, temp_project_dir):
        """Test cleanup of expired cache entries."""
        # Create cache manager with 0-hour TTL
        cache_mgr = CacheManager(temp_project_dir, cache_ttl_hours=0)

        # Save entries
        cache_mgr.save_result("key1", {"data": 1})
        cache_mgr.save_result("key2", {"data": 2})

        # Run cleanup
        removed_count = cache_mgr.cleanup_expired()

        assert removed_count == 2

    def test_project_hash_computation(self, temp_project_dir, sample_python_file):
        """Test project hash computation."""
        cache_mgr = CacheManager(temp_project_dir)

        project_files = [sample_python_file]

        # Compute hash twice - should be same
        hash1 = cache_mgr._compute_project_hash(project_files)
        hash2 = cache_mgr._compute_project_hash(project_files)

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 hash length
