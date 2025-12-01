"""HTML report generator for Vibe-Code Auditor."""

from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class HTMLReporter:
    """Generates HTML-formatted analysis reports."""

    def __init__(self, mode: str):
        """
        Initialize HTML reporter.

        Args:
            mode: Analysis mode ('deployment' or 'personal')
        """
        self.mode = mode

    def generate_report(
        self,
        static_results: Dict[str, Any],
        ai_results: Optional[Dict[str, Any]],
        project_path: Path,
        output_file: Path
    ) -> str:
        """
        Generate HTML report.

        Args:
            static_results: Static analysis results
            ai_results: AI analysis results (optional)
            project_path: Path to analyzed project
            output_file: Path to save HTML file

        Returns:
            HTML content as string
        """
        logger.info("Generating HTML report")

        html_content = self._build_html(static_results, ai_results, project_path)

        # Save to file
        self._save_to_file(html_content, output_file)

        logger.info(f"HTML report saved to {output_file}")
        return html_content

    def _build_html(
        self,
        static_results: Dict[str, Any],
        ai_results: Optional[Dict[str, Any]],
        project_path: Path
    ) -> str:
        """Build HTML content."""
        static_summary = static_results.get('summary', {})
        static_issues = static_results.get('issues', [])

        ai_summary = ai_results.get('summary', {}) if ai_results else {}
        ai_issues = ai_results.get('issues', []) if ai_results else []

        total_issues = static_summary.get('total_issues', 0) + ai_summary.get('total_issues', 0)

        html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vibe-Code Auditor Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .header .subtitle {{
            opacity: 0.9;
            font-size: 1.1em;
        }}

        .content {{
            padding: 40px;
        }}

        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}

        .summary-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}

        .summary-card h3 {{
            color: #667eea;
            margin-bottom: 10px;
            font-size: 0.9em;
            text-transform: uppercase;
        }}

        .summary-card .value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
        }}

        .section {{
            margin-bottom: 40px;
        }}

        .section-title {{
            font-size: 1.8em;
            margin-bottom: 20px;
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}

        .issue {{
            background: #f8f9fa;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 6px;
            border-left: 4px solid #ddd;
        }}

        .issue.critical {{
            border-left-color: #dc3545;
            background: #fff5f5;
        }}

        .issue.warning {{
            border-left-color: #ffc107;
            background: #fffbf0;
        }}

        .issue.info {{
            border-left-color: #28a745;
            background: #f0fff4;
        }}

        .issue-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}

        .issue-title {{
            font-weight: bold;
            font-size: 1.1em;
        }}

        .badge {{
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }}

        .badge.critical {{
            background: #dc3545;
            color: white;
        }}

        .badge.warning {{
            background: #ffc107;
            color: #333;
        }}

        .badge.info {{
            background: #28a745;
            color: white;
        }}

        .issue-details {{
            color: #666;
            margin-top: 10px;
        }}

        .location {{
            font-family: monospace;
            background: #e9ecef;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.9em;
        }}

        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Vibe-Code Auditor</h1>
            <div class="subtitle">코드 분석 리포트 - {self.mode} 관점</div>
            <div class="subtitle" style="margin-top: 10px; opacity: 0.7;">
                {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </div>
        </div>

        <div class="content">
            <div class="summary">
                <div class="summary-card">
                    <h3>프로젝트</h3>
                    <div class="value" style="font-size: 1.2em;">{project_path.name}</div>
                </div>
                <div class="summary-card">
                    <h3>총 이슈</h3>
                    <div class="value">{total_issues}</div>
                </div>
                <div class="summary-card">
                    <h3>Critical</h3>
                    <div class="value" style="color: #dc3545;">
                        {static_summary.get('by_severity', {}).get('critical', 0) + ai_summary.get('by_severity', {}).get('critical', 0)}
                    </div>
                </div>
                <div class="summary-card">
                    <h3>Warning</h3>
                    <div class="value" style="color: #ffc107;">
                        {static_summary.get('by_severity', {}).get('warning', 0) + ai_summary.get('by_severity', {}).get('warning', 0)}
                    </div>
                </div>
                <div class="summary-card">
                    <h3>Info</h3>
                    <div class="value" style="color: #28a745;">
                        {static_summary.get('by_severity', {}).get('info', 0) + ai_summary.get('by_severity', {}).get('info', 0)}
                    </div>
                </div>
            </div>

            <div class="section">
                <h2 class="section-title">📊 정적 분석 결과</h2>
                {self._render_issues(static_issues)}
            </div>

            <div class="section">
                <h2 class="section-title">🤖 AI 코드 리뷰</h2>
                {self._render_ai_issues(ai_issues)}
            </div>
        </div>

        <div class="footer">
            Generated by Vibe-Code Auditor v1.1.0 |
            <a href="https://github.com/vibe-coding/vibe-code-auditor" style="color: #667eea;">GitHub</a>
        </div>
    </div>
</body>
</html>"""
        return html

    def _render_issues(self, issues: list) -> str:
        """Render static analysis issues."""
        if not issues:
            return '<p style="color: #28a745;">✓ 이슈가 발견되지 않았습니다.</p>'

        html = ""
        for issue in issues:
            severity = issue.get('severity', 'info')
            tool = issue.get('tool', 'unknown')
            message = issue.get('message', '')
            file_path = issue.get('file', '')
            line = issue.get('line', '')

            location = f"{file_path}:{line}" if file_path and line else file_path if file_path else ""

            html += f"""
            <div class="issue {severity}">
                <div class="issue-header">
                    <div class="issue-title">{message}</div>
                    <span class="badge {severity}">{severity}</span>
                </div>
                <div class="issue-details">
                    <strong>도구:</strong> {tool}
                    {f'<br><strong>위치:</strong> <span class="location">{location}</span>' if location else ''}
                </div>
            </div>
            """

        return html

    def _render_ai_issues(self, issues: list) -> str:
        """Render AI analysis issues."""
        if not issues:
            return '<p style="color: #28a745;">✓ AI 분석에서 이슈가 발견되지 않았습니다.</p>'

        html = ""
        for issue in issues:
            severity = issue.get('severity', 'info')
            title = issue.get('title', 'No title')
            details = issue.get('details', [])

            html += f"""
            <div class="issue {severity}">
                <div class="issue-header">
                    <div class="issue-title">{title}</div>
                    <span class="badge {severity}">{severity}</span>
                </div>
                <div class="issue-details">
                    {'<br>'.join(details) if details else ''}
                </div>
            </div>
            """

        return html

    def _save_to_file(self, html_content: str, output_file: Path) -> None:
        """Save HTML content to file."""
        try:
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)

            logger.info(f"HTML report saved to {output_file}")

        except Exception as e:
            logger.error(f"Failed to save HTML report: {e}", exc_info=True)
            raise
