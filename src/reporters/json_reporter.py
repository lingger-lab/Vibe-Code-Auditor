"""JSON report generator for Vibe-Code Auditor."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class JSONReporter:
    """Generates JSON-formatted analysis reports."""

    def __init__(self, mode: str):
        """
        Initialize JSON reporter.

        Args:
            mode: Analysis mode ('deployment' or 'personal')
        """
        self.mode = mode

    def generate_report(
        self,
        static_results: Dict[str, Any],
        ai_results: Optional[Dict[str, Any]],
        project_path: Path,
        output_file: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Generate JSON report.

        Args:
            static_results: Static analysis results
            ai_results: AI analysis results (optional)
            project_path: Path to analyzed project
            output_file: Optional path to save JSON file

        Returns:
            Dictionary with complete analysis report
        """
        logger.info("Generating JSON report")

        report = {
            "metadata": {
                "tool": "Vibe-Code Auditor",
                "version": "1.10.0",
                "timestamp": datetime.now().isoformat(),
                "project_path": str(project_path),
                "analysis_mode": self.mode
            },
            "summary": self._generate_summary(static_results, ai_results),
            "static_analysis": self._format_static_results(static_results),
            "ai_analysis": self._format_ai_results(ai_results) if ai_results else None
        }

        # Save to file if specified
        if output_file:
            self._save_to_file(report, output_file)

        logger.info("JSON report generated with %d total issues", report['summary']['total_issues'])
        return report

    def _generate_summary(
        self,
        static_results: Dict[str, Any],
        ai_results: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate summary section."""
        static_summary = static_results.get('summary', {})
        static_total = static_summary.get('total_issues', 0)
        static_severity = static_summary.get('by_severity', {})

        ai_total = 0
        ai_severity = {'critical': 0, 'warning': 0, 'info': 0}

        if ai_results and 'summary' in ai_results:
            ai_summary = ai_results['summary']
            ai_total = ai_summary.get('total_issues', 0)
            ai_severity = ai_summary.get('by_severity', ai_severity)

        return {
            "total_issues": static_total + ai_total,
            "static_issues": static_total,
            "ai_issues": ai_total,
            "by_severity": {
                "critical": static_severity.get('critical', 0) + ai_severity.get('critical', 0),
                "warning": static_severity.get('warning', 0) + ai_severity.get('warning', 0),
                "info": static_severity.get('info', 0) + ai_severity.get('info', 0)
            }
        }

    def _format_static_results(self, static_results: Dict[str, Any]) -> Dict[str, Any]:
        """Format static analysis results with priority sorting."""
        issues = static_results.get('issues', [])
        
        # 우선순위별로 이슈 정렬: critical -> warning -> info
        sorted_issues = self._sort_issues_by_priority(issues)
        
        return {
            "mode": static_results.get('mode'),
            "languages": static_results.get('languages', []),
            "issues": sorted_issues,
            "summary": static_results.get('summary', {})
        }

    def _format_ai_results(self, ai_results: Dict[str, Any]) -> Dict[str, Any]:
        """Format AI analysis results with priority sorting."""
        issues = ai_results.get('issues', [])
        
        # 우선순위별로 이슈 정렬: critical -> warning -> info
        sorted_issues = self._sort_issues_by_priority(issues)
        
        return {
            "mode": ai_results.get('mode'),
            "issues": sorted_issues,
            "summary": ai_results.get('summary', {}),
            "error": ai_results.get('error')
        }

    def _sort_issues_by_priority(self, issues: list) -> list:
        """
        Sort issues by priority: critical -> warning -> info.
        
        Args:
            issues: List of issue dictionaries
            
        Returns:
            Sorted list of issues by priority
        """
        if not issues:
            return []
        
        # 우선순위 매핑 (낮은 숫자가 높은 우선순위)
        priority_map = {
            'critical': 1,
            'warning': 2,
            'info': 3
        }
        
        def get_priority(issue: Dict[str, Any]) -> int:
            """Get priority value for an issue."""
            severity = issue.get('severity', 'info').lower()
            return priority_map.get(severity, 3)  # 기본값은 info
        
        # 우선순위별로 정렬
        sorted_issues = sorted(issues, key=get_priority)
        
        return sorted_issues

    def _save_to_file(self, report: Dict[str, Any], output_file: Path) -> None:
        """
        Save report to JSON file.

        Args:
            report: Report dictionary
            output_file: Output file path
        """
        try:
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            logger.info("JSON report saved to %s", output_file)

        except (IOError, OSError, PermissionError) as e:
            logger.error("Failed to save JSON report: %s", e, exc_info=True)
            raise
