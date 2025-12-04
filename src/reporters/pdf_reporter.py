"""
PDF Reporter
Generates PDF format analysis reports using ReportLab
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import platform
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO


class PDFReporter:
    """Generate PDF reports for code analysis results"""

    def __init__(self, mode: str = "deployment"):
        """
        Initialize PDF reporter

        Args:
            mode: Analysis mode (deployment or personal)
        """
        self.mode = mode
        self.styles = getSampleStyleSheet()
        self._register_korean_font()
        self._setup_custom_styles()

    def _register_korean_font(self) -> None:
        """
        Register a font that supports Korean characters.
        
        플랫폼별로 한글 폰트 경로를 시도합니다:
        - Windows: Malgun Gothic (맑은 고딕)
        - Linux/macOS: 시스템 기본 한글 폰트 또는 기본 폰트 사용
        """
        self.base_font_name = self.styles["Normal"].fontName  # 기본값 설정
        
        # 플랫폼별 폰트 경로 시도
        font_paths = []
        
        if platform.system() == "Windows":
            # Windows 기본 한글 폰트 경로
            font_paths = [
                r"C:\Windows\Fonts\malgun.ttf",
                r"C:\Windows\Fonts\gulim.ttc",
            ]
        elif platform.system() == "Linux":
            # Linux 시스템 폰트 경로 (Streamlit Cloud 등)
            font_paths = [
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            ]
        elif platform.system() == "Darwin":  # macOS
            font_paths = [
                "/System/Library/Fonts/AppleGothic.ttf",
                "/Library/Fonts/AppleGothic.ttf",
            ]
        
        # 폰트 경로를 순차적으로 시도
        for font_path in font_paths:
            try:
                if os.path.exists(font_path):
                    font_name = "KoreanFont"
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    self.base_font_name = font_name
                    break
            except (OSError, IOError, Exception):
                # 폰트 등록 실패 시 다음 경로 시도
                continue
        
        # 기본 Normal 스타일에도 한글 폰트를 적용해, 별도 스타일을 쓰지 않는 본문도 깨지지 않게 함
        self.styles["Normal"].fontName = self.base_font_name

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            fontName=self.base_font_name,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))

        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            fontName=self.base_font_name,
            textColor=colors.HexColor('#2ca02c'),
            spaceAfter=12,
            spaceBefore=12
        ))

        # Issue title style
        self.styles.add(ParagraphStyle(
            name='IssueTitle',
            parent=self.styles['Heading3'],
            fontSize=12,
            fontName=self.base_font_name,
            textColor=colors.HexColor('#d62728'),
            spaceAfter=6
        ))

    def generate_report(
        self,
        results: Dict[str, Any],
        project_path: Path,
        output_path: Path
    ) -> None:
        """
        Generate PDF report

        Args:
            results: Analysis results dictionary
            project_path: Path to analyzed project
            output_path: Path to save PDF report
        """
        # Create document
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        # Build content
        story = []

        # Title page
        story.extend(self._build_title_page(project_path))

        # Summary section
        story.extend(self._build_summary_section(results))

        # Language detection section
        story.extend(self._build_language_section(results.get('languages', [])))

        # Static analysis section
        static_results = results.get('static_results', {})
        if static_results:
            story.extend(self._build_static_analysis_section(static_results))

        # AI analysis section
        ai_results = results.get('ai_results')
        if ai_results:
            story.extend(self._build_ai_analysis_section(ai_results))

        # Build PDF
        doc.build(story)

    def generate_report_to_bytes(
        self,
        results: Dict[str, Any],
        project_path: Path
    ) -> bytes:
        """
        Generate PDF report to memory (BytesIO).

        Args:
            results: Analysis results dictionary
            project_path: Path to analyzed project

        Returns:
            PDF content as bytes
        """
        # Create BytesIO buffer
        buffer = BytesIO()

        # Create document in memory
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        # Build content
        story = []

        # Title page
        story.extend(self._build_title_page(project_path))

        # Summary section
        story.extend(self._build_summary_section(results))

        # Language detection section
        story.extend(self._build_language_section(results.get('languages', [])))

        # Static analysis section
        static_results = results.get('static_results', {})
        if static_results:
            story.extend(self._build_static_analysis_section(static_results))

        # AI analysis section
        ai_results = results.get('ai_results')
        if ai_results:
            story.extend(self._build_ai_analysis_section(ai_results))

        # Build PDF
        doc.build(story)

        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes

    def _build_title_page(self, project_path: Path) -> List:
        """Build title page"""
        story = []

        # Title
        title = Paragraph(
            "Vibe-Code Auditor<br/>Analysis Report",
            self.styles['CustomTitle']
        )
        story.append(title)
        story.append(Spacer(1, 0.3 * inch))

        # Metadata table
        metadata = [
            ['Project Path:', str(project_path)],
            ['Analysis Mode:', self.mode.capitalize()],
            ['Report Date:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Tool Version:', 'v1.10.0']
        ]

        table = Table(metadata, colWidths=[2 * inch, 4.5 * inch])
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), self.base_font_name, 10),
            ('FONT', (0, 0), (0, -1), self.base_font_name, 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1f77b4')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12)
        ]))

        story.append(table)
        story.append(PageBreak())

        return story

    def _build_summary_section(self, results: Dict[str, Any]) -> List:
        """Build summary section"""
        story = []

        # Section header
        header = Paragraph("Executive Summary", self.styles['SectionHeader'])
        story.append(header)

        # Calculate statistics
        # JSON 리포터와 일관성을 맞추기 위해 정적 분석 + AI 분석 요약을 함께 사용
        static_results = results.get('static_results', {})
        ai_results = results.get('ai_results')

        static_summary = static_results.get('summary', {})
        static_by_severity = static_summary.get('by_severity', {})

        # static 기준 값
        static_total = static_summary.get('total_issues', len(static_results.get('issues', [])))
        static_critical = static_by_severity.get('critical', 0)
        static_warning = static_by_severity.get('warning', 0)
        static_info = static_by_severity.get('info', 0)

        # AI 기준 값
        ai_total = 0
        ai_critical = 0
        ai_warning = 0
        ai_info = 0

        if ai_results and 'summary' in ai_results:
            ai_summary = ai_results['summary']
            ai_total = ai_summary.get('total_issues', 0)
            ai_by_severity = ai_summary.get('by_severity', {})
            ai_critical = ai_by_severity.get('critical', 0)
            ai_warning = ai_by_severity.get('warning', 0)
            ai_info = ai_by_severity.get('info', 0)

        total_issues = static_total + ai_total
        critical_count = static_critical + ai_critical
        warning_count = static_warning + ai_warning
        info_count = static_info + ai_info

        languages = results.get('languages', [])
        language_count = len(languages)

        # Summary table
        summary_data = [
            ['Metric', 'Count'],
            ['Languages Detected', str(language_count)],
            ['Total Issues (Static + AI)', str(total_issues)],
            ['Critical Issues', str(critical_count)],
            ['Warnings', str(warning_count)],
            ['Informational', str(info_count)]
        ]

        table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONT', (0, 0), (-1, 0), self.base_font_name, 12),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            # Data rows
            ('FONT', (0, 1), (-1, -1), self.base_font_name, 10),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
        ]))

        story.append(table)
        story.append(Spacer(1, 0.5 * inch))

        return story

    def _build_language_section(self, languages: List[str]) -> List:
        """Build language detection section"""
        story = []

        # Section header
        header = Paragraph("Detected Languages", self.styles['SectionHeader'])
        story.append(header)

        if not languages:
            text = Paragraph("No languages detected.", self.styles['Normal'])
            story.append(text)
        else:
            # Language list
            lang_text = ", ".join(sorted(languages))
            text = Paragraph(f"<b>Languages:</b> {lang_text}", self.styles['Normal'])
            story.append(text)

        story.append(Spacer(1, 0.3 * inch))

        return story

    def _build_static_analysis_section(self, static_results: Dict[str, Any]) -> List:
        """Build static analysis section"""
        story = []

        # Section header
        header = Paragraph("Static Analysis Results", self.styles['SectionHeader'])
        story.append(header)

        issues = static_results.get('issues', [])

        if not issues:
            text = Paragraph("No issues found.", self.styles['Normal'])
            story.append(text)
            return story

        # Group issues by severity
        critical_issues = [i for i in issues if i.get('severity') == 'critical']
        warning_issues = [i for i in issues if i.get('severity') == 'warning']
        info_issues = [i for i in issues if i.get('severity') == 'info']

        # Critical issues (최대 20개까지 상세 표시)
        if critical_issues:
            story.append(Paragraph(
                f"Critical Issues ({len(critical_issues)})",
                self.styles['IssueTitle']
            ))
            story.extend(self._build_issue_table(critical_issues[:20]))
            if len(critical_issues) > 20:
                story.append(Paragraph(
                    f"<i>... and {len(critical_issues) - 20} more critical issues</i>",
                    self.styles['Normal']
                ))
            story.append(Spacer(1, 0.2 * inch))

        # Warnings (최대 10개까지 상세 표시)
        if warning_issues:
            story.append(Paragraph(
                f"Warnings ({len(warning_issues)})",
                self.styles['IssueTitle']
            ))
            story.extend(self._build_issue_table(warning_issues[:10]))
            if len(warning_issues) > 10:
                story.append(Paragraph(
                    f"<i>... and {len(warning_issues) - 10} more warnings</i>",
                    self.styles['Normal']
                ))
            story.append(Spacer(1, 0.2 * inch))

        # Info issues (최대 5개까지 상세 표시)
        if info_issues:
            story.append(Paragraph(
                f"Informational ({len(info_issues)})",
                self.styles['IssueTitle']
            ))
            story.extend(self._build_issue_table(info_issues[:5]))
            if len(info_issues) > 5:
                story.append(Paragraph(
                    f"<i>... and {len(info_issues) - 5} more informational issues</i>",
                    self.styles['Normal']
                ))

        story.append(Spacer(1, 0.3 * inch))

        return story

    def _build_issue_table(self, issues: List[Dict[str, Any]]) -> List:
        """Build issue table"""
        story = []

        if not issues:
            return story

        # Build table data
        data = [['File', 'Line', 'Tool', 'Message']]

        for issue in issues:
            file_path = issue.get('file', 'N/A')
            # Truncate long paths
            if len(file_path) > 40:
                file_path = '...' + file_path[-37:]

            line = str(issue.get('line', 'N/A'))
            tool = issue.get('tool', 'N/A')

            message = issue.get('message', 'No message')
            # Truncate long messages
            if len(message) > 60:
                message = message[:57] + '...'

            data.append([file_path, line, tool, message])

        # Create table
        table = Table(data, colWidths=[2 * inch, 0.5 * inch, 1 * inch, 3 * inch])
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ca02c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONT', (0, 0), (-1, 0), self.base_font_name, 9),
            # Data
            ('FONT', (0, 1), (-1, -1), self.base_font_name, 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))

        story.append(table)
        story.append(Spacer(1, 0.1 * inch))

        return story

    def _build_ai_analysis_section(self, ai_results: Dict[str, Any]) -> List:
        """Build AI analysis section"""
        story = []

        # Section header
        header = Paragraph("AI Code Review", self.styles['SectionHeader'])
        story.append(header)

        # Issues
        issues = ai_results.get('issues', [])
        if issues:
            story.append(Paragraph(
                f"AI-Detected Issues ({len(issues)})",
                self.styles['IssueTitle']
            ))

            # 심각도별 그룹핑 (HTML/JSON, UI와 동일한 구조)
            issues_by_severity = {
                'critical': [],
                'warning': [],
                'info': []
            }

            for issue in issues:
                severity = issue.get('severity', 'info').lower()
                if severity in issues_by_severity:
                    issues_by_severity[severity].append(issue)
                else:
                    issues_by_severity['info'].append(issue)

            severity_order = ['critical', 'warning', 'info']

            for severity in severity_order:
                severity_issues = issues_by_severity[severity]
                if not severity_issues:
                    continue

                # Severity 섹션 헤더
                severity_title = {
                    'critical': 'Critical',
                    'warning': 'Warning',
                    'info': 'Info'
                }.get(severity, severity.upper())

                story.append(Spacer(1, 0.15 * inch))
                story.append(Paragraph(
                    f"{severity_title} Issues ({len(severity_issues)})",
                    self.styles['IssueTitle']
                ))

                # 심각도별 상세 표시 개수 제한: critical=20, warning=10, info=5
                if severity == 'critical':
                    max_items = 20
                elif severity == 'warning':
                    max_items = 10
                else:
                    max_items = 5

                # 각 섹션당 최대 N개만 상세 표시
                for i, issue in enumerate(severity_issues[:max_items], 1):
                    raw_title = (issue.get('title') or 'No title')
                    details = issue.get('details', []) or []

                    # Markdown 표(| ... |), 코드펜스(```), 언어 태그만 있는 줄 제거
                    filtered_details: List[str] = []
                    for line in details:
                        stripped = line.strip()
                        if not stripped:
                            continue
                        if stripped.startswith('|'):
                            continue
                        if stripped.startswith('```'):
                            continue
                        if stripped in {'python', 'bash', 'sh', 'json', 'yaml'}:
                            continue
                        filtered_details.append(line)

                    # 제목이 표/마스킹이고 실제 설명 줄이 있을 때만 첫 번째 줄을 제목으로 승격
                    promote_to_detail_title = (
                        (raw_title.strip().startswith('|') or raw_title.replace('■', '').strip() == '')
                        and bool(filtered_details)
                    )

                    if promote_to_detail_title:
                        title = filtered_details[0][:80]
                        body_lines = filtered_details[1:]
                    else:
                        if raw_title.strip().startswith('|') or raw_title.replace('■', '').strip() == '':
                            title = 'AI 분석 이슈'
                        else:
                            title = raw_title
                        body_lines = filtered_details

                    details_text = "<br/>".join(body_lines) if body_lines else ""
                    issue_text = f"<b>{i}. {title}</b>"
                    if details_text:
                        issue_text = issue_text + f"<br/>{details_text}"

                    para = Paragraph(issue_text, self.styles['Normal'])
                    story.append(para)
                    story.append(Spacer(1, 0.1 * inch))

                if len(severity_issues) > max_items:
                    story.append(Paragraph(
                        f"<i>... and {len(severity_issues) - max_items} more {severity_title.lower()} issues</i>",
                        self.styles['Normal']
                    ))

        # 현재 ai_results에는 recommendations 필드가 없으므로,
        # 향후 확장을 위해 구조만 남겨두고 기본적으로는 사용하지 않습니다.

        story.append(Spacer(1, 0.3 * inch))

        return story
