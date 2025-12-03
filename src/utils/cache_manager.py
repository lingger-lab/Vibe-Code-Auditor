"""Cache management system for Vibe-Code Auditor."""

import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class CacheManager:
    """Manages analysis result caching to avoid redundant processing."""

    def __init__(self, project_path: Path, cache_ttl_hours: int = 24):
        """
        Initialize cache manager.

        Args:
            project_path: Path to the project being analyzed
            cache_ttl_hours: Cache time-to-live in hours (default: 24)
        """
        self.project_path = project_path
        self.cache_dir = project_path / '.vibe-auditor-cache'
        self.cache_file = self.cache_dir / 'cache.json'
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        self._ensure_cache_dir()

    def _ensure_cache_dir(self) -> None:
        """Create cache directory if it doesn't exist."""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.debug("Cache directory ensured at %s", self.cache_dir)
        except (OSError, PermissionError) as e:
            logger.error("Failed to create cache directory: %s", e, exc_info=True)

    def _compute_file_hash(self, file_path: Path) -> str:
        """
        Compute SHA256 hash of a file.

        Args:
            file_path: Path to file

        Returns:
            SHA256 hash string
        """
        try:
            sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except (IOError, OSError) as e:
            logger.debug("Failed to hash %s: %s", file_path, e)
            return ""

    def _compute_project_hash(self, files: list[Path]) -> str:
        """
        Compute combined hash of all project files.

        Args:
            files: List of file paths

        Returns:
            Combined hash string
        """
        combined = []
        for file_path in sorted(files):
            try:
                # Include file path and modification time for quick check
                stat = file_path.stat()
                combined.append(f"{file_path}:{stat.st_mtime}:{stat.st_size}")
            except (OSError, PermissionError) as e:
                logger.debug("Failed to stat %s: %s", file_path, e)
                continue

        combined_str = '|'.join(combined)
        return hashlib.sha256(combined_str.encode()).hexdigest()

    def _load_cache(self) -> Dict[str, Any]:
        """
        Load cache from file.

        Returns:
            Cache data dictionary
        """
        if not self.cache_file.exists():
            logger.debug("No cache file found")
            return {}

        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            logger.debug("Loaded cache with %d entries", len(cache_data))
            return cache_data
        except json.JSONDecodeError as e:
            logger.error("Failed to parse cache file: %s", e, exc_info=True)
            return {}
        except (IOError, OSError) as e:
            logger.error("Failed to load cache: %s", e, exc_info=True)
            return {}

    def _save_cache(self, cache_data: Dict[str, Any]) -> None:
        """
        Save cache to file.

        Args:
            cache_data: Cache data dictionary
        """
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            logger.debug("Saved cache with %d entries", len(cache_data))
        except (IOError, OSError, PermissionError) as e:
            logger.error("Failed to save cache: %s", e, exc_info=True)
            raise

    def get_cached_result(
        self,
        cache_key: str,
        project_files: Optional[list[Path]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached analysis result if valid.

        Args:
            cache_key: Unique key for this analysis (e.g., 'static_analysis_deployment')
            project_files: List of project files to check for changes (optional)

        Returns:
            Cached result if valid, None otherwise
        """
        cache_data = self._load_cache()

        if cache_key not in cache_data:
            logger.debug("Cache miss: %s", cache_key)
            return None

        entry = cache_data[cache_key]

        # Check TTL
        cached_time = datetime.fromisoformat(entry['timestamp'])
        if datetime.now() - cached_time > self.cache_ttl:
            logger.debug("Cache expired: %s", cache_key)
            return None

        # Check if project files changed
        if project_files:
            current_hash = self._compute_project_hash(project_files)
            cached_hash = entry.get('project_hash', '')

            if current_hash != cached_hash:
                logger.debug("Cache invalidated (files changed): %s", cache_key)
                return None

        logger.info("Cache hit: %s", cache_key)
        return entry.get('result')

    def save_result(
        self,
        cache_key: str,
        result: Dict[str, Any],
        project_files: Optional[list[Path]] = None
    ) -> None:
        """
        Save analysis result to cache.

        Args:
            cache_key: Unique key for this analysis
            result: Analysis result to cache
            project_files: List of project files (for invalidation)
        """
        logger.debug("Saving result to cache: %s", cache_key)

        cache_data = self._load_cache()

        entry = {
            'timestamp': datetime.now().isoformat(),
            'result': result,
        }

        if project_files:
            entry['project_hash'] = self._compute_project_hash(project_files)

        cache_data[cache_key] = entry
        self._save_cache(cache_data)

        logger.info("Result cached: %s", cache_key)

    def invalidate(self, cache_key: Optional[str] = None) -> None:
        """
        Invalidate cache entry or entire cache.

        Args:
            cache_key: Specific key to invalidate, or None to clear all
        """
        if cache_key is None:
            logger.warning("Clearing entire cache")
            try:
                if self.cache_file.exists():
                    self.cache_file.unlink()
                    logger.info("Cache cleared")
            except Exception as e:
                logger.error("Failed to clear cache: %s", e, exc_info=True)
                raise
        else:
            logger.info("Invalidating cache: %s", cache_key)
            cache_data = self._load_cache()

            if cache_key in cache_data:
                del cache_data[cache_key]
                self._save_cache(cache_data)
                logger.info("Cache invalidated: %s", cache_key)

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Cache statistics dictionary
        """
        cache_data = self._load_cache()

        stats = {
            'total_entries': len(cache_data),
            'cache_file_size': self.cache_file.stat().st_size if self.cache_file.exists() else 0,
            'entries': []
        }

        for key, entry in cache_data.items():
            cached_time = datetime.fromisoformat(entry['timestamp'])
            age = datetime.now() - cached_time

            stats['entries'].append({
                'key': key,
                'timestamp': entry['timestamp'],
                'age_hours': age.total_seconds() / 3600,
                'is_expired': age > self.cache_ttl,
            })

        return stats

    def cleanup_expired(self) -> int:
        """
        Remove expired cache entries.

        Returns:
            Number of entries removed
        """
        logger.info("Cleaning up expired cache entries")

        cache_data = self._load_cache()
        original_count = len(cache_data)

        # Remove expired entries
        expired_keys = []
        for key, entry in cache_data.items():
            cached_time = datetime.fromisoformat(entry['timestamp'])
            if datetime.now() - cached_time > self.cache_ttl:
                expired_keys.append(key)

        for key in expired_keys:
            del cache_data[key]

        if expired_keys:
            self._save_cache(cache_data)

        removed_count = len(expired_keys)
        logger.info("Removed %d expired cache entries", removed_count)

        return removed_count
