"""History tracking system for Vibe-Code Auditor."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class HistoryTracker:
    """Tracks analysis history over time."""

    def __init__(self, project_path: Path):
        """
        Initialize history tracker.

        Args:
            project_path: Path to the project being analyzed
        """
        self.project_path = project_path
        self.history_dir = project_path / '.vibe-auditor-history'
        self.history_file = self.history_dir / 'history.json'
        self._ensure_history_dir()

    def _ensure_history_dir(self) -> None:
        """Create history directory if it doesn't exist."""
        try:
            self.history_dir.mkdir(parents=True, exist_ok=True)
            logger.debug(f"History directory ensured at {self.history_dir}")
        except Exception as e:
            logger.error(f"Failed to create history directory: {e}", exc_info=True)

    def save_result(
        self,
        mode: str,
        static_results: Dict[str, Any],
        ai_results: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Save analysis result to history.

        Args:
            mode: Analysis mode (deployment or personal)
            static_results: Static analysis results
            ai_results: AI analysis results (optional)
        """
        logger.info("Saving analysis result to history")

        # Load existing history
        history = self._load_history()

        # Create new entry
        entry = {
            'timestamp': datetime.now().isoformat(),
            'mode': mode,
            'summary': {
                'total_issues': (
                    static_results.get('summary', {}).get('total_issues', 0) +
                    (ai_results.get('summary', {}).get('total_issues', 0) if ai_results else 0)
                ),
                'static_issues': static_results.get('summary', {}).get('total_issues', 0),
                'ai_issues': ai_results.get('summary', {}).get('total_issues', 0) if ai_results else 0,
                'by_severity': self._aggregate_severity(static_results, ai_results),
            },
        }

        # Add to history
        history.append(entry)

        # Save to file
        self._save_history(history)

        logger.info("Analysis result saved to history (total entries: %d)", len(history))

    def _aggregate_severity(
        self,
        static_results: Dict[str, Any],
        ai_results: Optional[Dict[str, Any]]
    ) -> Dict[str, int]:
        """
        Aggregate severity counts from both static and AI results.

        Args:
            static_results: Static analysis results
            ai_results: AI analysis results (optional)

        Returns:
            Aggregated severity counts
        """
        static_severity = static_results.get('summary', {}).get('by_severity', {})
        ai_severity = ai_results.get('summary', {}).get('by_severity', {}) if ai_results else {}

        return {
            'critical': static_severity.get('critical', 0) + ai_severity.get('critical', 0),
            'warning': static_severity.get('warning', 0) + ai_severity.get('warning', 0),
            'info': static_severity.get('info', 0) + ai_severity.get('info', 0),
        }

    def _load_history(self) -> List[Dict[str, Any]]:
        """
        Load history from file.

        Returns:
            List of history entries
        """
        if not self.history_file.exists():
            logger.debug("No history file found, starting fresh")
            return []

        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            logger.debug("Loaded %d history entries", len(history))
            return history
        except json.JSONDecodeError as e:
            logger.error("Failed to parse history file: %s", e, exc_info=True)
            return []
        except (IOError, OSError) as e:
            logger.error("Failed to load history: %s", e, exc_info=True)
            return []

    def _save_history(self, history: List[Dict[str, Any]]) -> None:
        """
        Save history to file.

        Args:
            history: List of history entries
        """
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            logger.debug("Saved %d history entries", len(history))
        except (IOError, OSError, PermissionError) as e:
            logger.error("Failed to save history: %s", e, exc_info=True)
            raise

    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get analysis history.

        Args:
            limit: Maximum number of entries to return (most recent first)

        Returns:
            List of history entries
        """
        history = self._load_history()

        # Sort by timestamp (most recent first)
        history.sort(key=lambda x: x['timestamp'], reverse=True)

        if limit:
            history = history[:limit]

        return history

    def get_trend_data(self) -> Dict[str, Any]:
        """
        Get trend analysis data.

        Returns:
            Trend data including issue counts over time
        """
        history = self._load_history()

        if not history:
            return {
                'total_runs': 0,
                'trend': 'no_data',
                'current_issues': 0,
                'previous_issues': 0,
                'change': 0,
            }

        # Sort by timestamp (oldest first for trend analysis)
        history.sort(key=lambda x: x['timestamp'])

        total_runs = len(history)
        current = history[-1]
        previous = history[-2] if len(history) > 1 else None

        current_issues = current['summary']['total_issues']
        previous_issues = previous['summary']['total_issues'] if previous else current_issues
        change = current_issues - previous_issues

        if change < 0:
            trend = 'improving'
        elif change > 0:
            trend = 'declining'
        else:
            trend = 'stable'

        return {
            'total_runs': total_runs,
            'trend': trend,
            'current_issues': current_issues,
            'previous_issues': previous_issues,
            'change': change,
            'change_percent': round((change / previous_issues * 100) if previous_issues > 0 else 0, 1),
            'timeline': [
                {
                    'timestamp': entry['timestamp'],
                    'total_issues': entry['summary']['total_issues'],
                    'critical': entry['summary']['by_severity']['critical'],
                    'warning': entry['summary']['by_severity']['warning'],
                    'info': entry['summary']['by_severity']['info'],
                }
                for entry in history
            ],
        }

    def clear_history(self) -> None:
        """Clear all history data."""
        logger.warning("Clearing all history data")
        try:
            if self.history_file.exists():
                self.history_file.unlink()
                logger.info("History data cleared")
        except (OSError, PermissionError) as e:
            logger.error("Failed to clear history: %s", e, exc_info=True)
            raise

    def export_history(self, output_path: Path) -> None:
        """
        Export history to a file.

        Args:
            output_path: Path to save exported history
        """
        logger.info("Exporting history to %s", output_path)

        history = self._load_history()
        trend_data = self.get_trend_data()

        export_data = {
            'project_path': str(self.project_path),
            'export_timestamp': datetime.now().isoformat(),
            'total_runs': len(history),
            'trend': trend_data,
            'history': history,
        }

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            logger.info("History exported to %s", output_path)
        except (IOError, OSError, PermissionError) as e:
            logger.error("Failed to export history: %s", e, exc_info=True)
            raise
