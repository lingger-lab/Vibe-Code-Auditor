"""
PDF Reporter
Generates PDF format analysis reports using ReportLab
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT


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
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))

        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2ca02c'),
            spaceAfter=12,
            spaceBefore=12
        ))

        # Issue title style
        self.styles.add(ParagraphStyle(
            name='IssueTitle',
            parent=self.styles['Heading3'],
            fontSize=12,
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
            ['Tool Version:', 'v1.9.0']
        ]

        table = Table(metadata, colWidths=[2 * inch, 4.5 * inch])
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
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
        static_results = results.get('static_results', {})
        issues = static_results.get('issues', [])

        critical_count = sum(1 for i in issues if i.get('severity') == 'critical')
        warning_count = sum(1 for i in issues if i.get('severity') == 'warning')
        info_count = sum(1 for i in issues if i.get('severity') == 'info')
        total_issues = len(issues)

        languages = results.get('languages', [])
        language_count = len(languages)

        # Summary table
        summary_data = [
            ['Metric', 'Count'],
            ['Languages Detected', str(language_count)],
            ['Total Issues Found', str(total_issues)],
            ['Critical Issues', str(critical_count)],
            ['Warnings', str(warning_count)],
            ['Informational', str(info_count)]
        ]

        table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 12),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            # Data rows
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
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

        # Critical issues
        if critical_issues:
            story.append(Paragraph(
                f"Critical Issues ({len(critical_issues)})",
                self.styles['IssueTitle']
            ))
            story.extend(self._build_issue_table(critical_issues[:10]))  # Limit to 10
            if len(critical_issues) > 10:
                story.append(Paragraph(
                    f"<i>... and {len(critical_issues) - 10} more critical issues</i>",
                    self.styles['Normal']
                ))
            story.append(Spacer(1, 0.2 * inch))

        # Warnings
        if warning_issues:
            story.append(Paragraph(
                f"Warnings ({len(warning_issues)})",
                self.styles['IssueTitle']
            ))
            story.extend(self._build_issue_table(warning_issues[:10]))  # Limit to 10
            if len(warning_issues) > 10:
                story.append(Paragraph(
                    f"<i>... and {len(warning_issues) - 10} more warnings</i>",
                    self.styles['Normal']
                ))
            story.append(Spacer(1, 0.2 * inch))

        # Info issues
        if info_issues:
            story.append(Paragraph(
                f"Informational ({len(info_issues)})",
                self.styles['IssueTitle']
            ))
            story.extend(self._build_issue_table(info_issues[:10]))  # Limit to 10
            if len(info_issues) > 10:
                story.append(Paragraph(
                    f"<i>... and {len(info_issues) - 10} more informational issues</i>",
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
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 9),
            # Data
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 8),
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

            for i, issue in enumerate(issues[:5], 1):  # Limit to 5
                severity = issue.get('severity', 'info').upper()
                message = issue.get('issue', 'No description')

                issue_text = f"<b>{i}. [{severity}]</b> {message}"
                para = Paragraph(issue_text, self.styles['Normal'])
                story.append(para)
                story.append(Spacer(1, 0.1 * inch))

            if len(issues) > 5:
                story.append(Paragraph(
                    f"<i>... and {len(issues) - 5} more AI-detected issues</i>",
                    self.styles['Normal']
                ))

        # Recommendations
        recommendations = ai_results.get('recommendations', [])
        if recommendations:
            story.append(Spacer(1, 0.2 * inch))
            story.append(Paragraph("Recommendations", self.styles['IssueTitle']))

            for i, rec in enumerate(recommendations[:5], 1):  # Limit to 5
                rec_text = f"{i}. {rec}"
                para = Paragraph(rec_text, self.styles['Normal'])
                story.append(para)
                story.append(Spacer(1, 0.1 * inch))

            if len(recommendations) > 5:
                story.append(Paragraph(
                    f"<i>... and {len(recommendations) - 5} more recommendations</i>",
                    self.styles['Normal']
                ))

        story.append(Spacer(1, 0.3 * inch))

        return story
