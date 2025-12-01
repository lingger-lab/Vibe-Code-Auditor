"""CLI reporter for displaying analysis results using Rich library."""

from typing import Dict, Any, Optional, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich import box

from src.config.settings import SEVERITY_LEVELS, ANALYSIS_MODES


class CLIReporter:
    """Generates formatted CLI reports using Rich library."""

    def __init__(self, mode: str):
        """
        Initialize the CLI reporter.

        Args:
            mode: Analysis mode ('deployment' or 'personal')
        """
        self.mode = mode
        self.console = Console()
        self.mode_config = ANALYSIS_MODES[mode]

    def _create_summary_table(self, static_results: Dict[str, Any], ai_results: Optional[Dict[str, Any]]) -> Table:
        """
        Create a summary table of analysis results.

        Args:
            static_results: Results from static analysis
            ai_results: Results from AI analysis (optional)

        Returns:
            Rich Table object
        """
        table = Table(title="분석 요약", box=box.ROUNDED)
        table.add_column("항목", style="cyan", no_wrap=True)
        table.add_column("값", style="magenta")

        # Static analysis summary
        static_summary = static_results.get('summary', {})
        total_static = static_summary.get('total_issues', 0)
        static_by_severity = static_summary.get('by_severity', {})

        table.add_row("정적 분석 이슈", str(total_static))
        table.add_row(
            f"  {SEVERITY_LEVELS['critical']['emoji']} Critical",
            str(static_by_severity.get('critical', 0))
        )
        table.add_row(
            f"  {SEVERITY_LEVELS['warning']['emoji']} Warning",
            str(static_by_severity.get('warning', 0))
        )
        table.add_row(
            f"  {SEVERITY_LEVELS['info']['emoji']} Info",
            str(static_by_severity.get('info', 0))
        )

        # AI analysis summary
        if ai_results and 'error' not in ai_results:
            ai_summary = ai_results.get('summary', {})
            total_ai = ai_summary.get('total_issues', 0)
            ai_by_severity = ai_summary.get('by_severity', {})

            table.add_row("AI 분석 이슈", str(total_ai))
            table.add_row(
                f"  {SEVERITY_LEVELS['critical']['emoji']} Critical",
                str(ai_by_severity.get('critical', 0))
            )
            table.add_row(
                f"  {SEVERITY_LEVELS['warning']['emoji']} Warning",
                str(ai_by_severity.get('warning', 0))
            )
            table.add_row(
                f"  {SEVERITY_LEVELS['info']['emoji']} Info",
                str(ai_by_severity.get('info', 0))
            )

        return table

    def _display_static_issues(self, static_results: Dict[str, Any]):
        """
        Display static analysis issues.

        Args:
            static_results: Results from static analysis
        """
        issues = static_results.get('issues', [])

        if not issues:
            self.console.print("[green]✓ 정적 분석에서 이슈를 발견하지 못했습니다.[/green]\n")
            return

        # Group issues by severity
        issues_by_severity = {
            'critical': [],
            'warning': [],
            'info': []
        }

        for issue in issues:
            severity = issue.get('severity', 'info')
            if severity in issues_by_severity:
                issues_by_severity[severity].append(issue)

        # Display issues by severity (prioritized by mode)
        priorities = self.mode_config['priorities']

        # Map priorities to severity focus
        if 'security' in priorities or 'performance' in priorities:
            order = ['critical', 'warning', 'info']
        else:
            order = ['warning', 'info', 'critical']

        for severity in order:
            severity_issues = issues_by_severity[severity]
            if not severity_issues:
                continue

            emoji = SEVERITY_LEVELS[severity]['emoji']
            color = SEVERITY_LEVELS[severity]['color']
            count = len(severity_issues)

            self.console.print(f"\n[bold {color}]{emoji} {severity.upper()} ({count})[/bold {color}]")

            for issue in severity_issues[:10]:  # Limit to 10 issues per severity
                tool = issue.get('tool', 'unknown')
                message = issue.get('message', 'No message')
                file_path = issue.get('file', '')
                line = issue.get('line', '')

                if file_path and line:
                    self.console.print(f"  [{color}]•[/{color}] {message}")
                    self.console.print(f"    위치: {file_path}:{line}")
                elif file_path:
                    self.console.print(f"  [{color}]•[/{color}] {message}")
                    self.console.print(f"    파일: {file_path}")
                else:
                    self.console.print(f"  [{color}]•[/{color}] {message}")

                # Show suggestion if available
                if 'suggestion' in issue:
                    self.console.print(f"    💡 {issue['suggestion']}")

            if len(severity_issues) > 10:
                remaining = len(severity_issues) - 10
                self.console.print(f"  [dim]... 그 외 {remaining}개 이슈[/dim]")

    def _display_ai_issues(self, ai_results: Dict[str, Any]):
        """
        Display AI analysis issues.

        Args:
            ai_results: Results from AI analysis
        """
        if 'error' in ai_results:
            self.console.print(f"[yellow]⚠ AI 분석 오류: {ai_results['error']}[/yellow]\n")
            return

        issues = ai_results.get('issues', [])

        if not issues:
            self.console.print("[green]✓ AI 분석에서 이슈를 발견하지 못했습니다.[/green]\n")
            return

        # Group by severity
        issues_by_severity = {
            'critical': [],
            'warning': [],
            'info': []
        }

        for issue in issues:
            severity = issue.get('severity', 'info')
            if severity in issues_by_severity:
                issues_by_severity[severity].append(issue)

        # Display by severity
        for severity in ['critical', 'warning', 'info']:
            severity_issues = issues_by_severity[severity]
            if not severity_issues:
                continue

            emoji = SEVERITY_LEVELS[severity]['emoji']
            color = SEVERITY_LEVELS[severity]['color']
            count = len(severity_issues)

            self.console.print(f"\n[bold {color}]{emoji} {severity.upper()} ({count})[/bold {color}]")

            for issue in severity_issues:
                title = issue.get('title', 'No title')
                details = issue.get('details', [])

                self.console.print(f"\n  [bold {color}]▸ {title}[/bold {color}]")

                for detail in details:
                    self.console.print(f"    {detail}")

    def generate_report(self, static_results: Dict[str, Any], ai_results: Optional[Dict[str, Any]] = None):
        """
        Generate and display the complete analysis report.

        Args:
            static_results: Results from static analysis
            ai_results: Results from AI analysis (optional)
        """
        # Display header
        self.console.print(Panel.fit(
            f"[bold cyan]코드 분석 리포트[/bold cyan]\n분석 관점: {self.mode_config['name']}",
            border_style="cyan"
        ))

        # Display summary table
        summary_table = self._create_summary_table(static_results, ai_results)
        self.console.print(summary_table)

        # Display static analysis issues
        self.console.print("\n[bold cyan]━━━ 정적 분석 결과 ━━━[/bold cyan]")
        self._display_static_issues(static_results)

        # Display AI analysis issues
        if ai_results:
            self.console.print("\n\n[bold cyan]━━━ AI 코드 리뷰 결과 ━━━[/bold cyan]")
            self._display_ai_issues(ai_results)

        # Display recommendations
        self.console.print("\n[bold cyan]━━━ 권장 사항 ━━━[/bold cyan]")

        if self.mode == 'deployment':
            recommendations = [
                "🔒 Critical 보안 이슈를 최우선으로 해결하세요",
                "⚡ 성능 관련 Warning을 검토하세요",
                "🔄 CI/CD 파이프라인에 정적 분석 도구를 통합하세요",
                "📝 배포 전 모든 Critical 이슈를 해결하세요"
            ]
        else:
            recommendations = [
                "📖 코드 가독성 개선을 위해 Info 이슈를 검토하세요",
                "♻️ 중복 코드를 리팩토링하세요",
                "📚 주석과 문서화를 개선하세요",
                "🧹 코드 스타일을 일관되게 유지하세요"
            ]

        for rec in recommendations:
            self.console.print(f"  • {rec}")
