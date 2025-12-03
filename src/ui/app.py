"""Streamlit UI for Vibe-Code Auditor.

This module provides a web-based user interface for non-technical users
to perform code analysis through a simple 3-click workflow:
1. Select folder
2. Start analysis
3. View results
"""

import streamlit as st
from pathlib import Path
from typing import Optional, Dict, Any
import sys
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.analyzer_engine import AnalyzerEngine, AnalysisProgress
from src.config.settings import ANALYSIS_MODES
from src.utils.logger import setup_logger
from src.reporters.json_reporter import JSONReporter
from src.reporters.html_reporter import HTMLReporter
from src.reporters.pdf_reporter import PDFReporter

logger = setup_logger(__name__)


# Page configuration
st.set_page_config(
    page_title="Vibe-Code Auditor",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)


def init_session_state():
    """Initialize Streamlit session state variables."""
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'analysis_running' not in st.session_state:
        st.session_state.analysis_running = False
    if 'progress' not in st.session_state:
        st.session_state.progress = AnalysisProgress()
    if 'page_number' not in st.session_state:
        st.session_state.page_number = 0
    if 'items_per_page' not in st.session_state:
        st.session_state.items_per_page = 20
    if 'current_view' not in st.session_state:
        st.session_state.current_view = 'main'
    if 'project_path' not in st.session_state:
        st.session_state.project_path = ""


def render_header():
    """Render the application header."""
    st.title("🔍 Vibe-Code Auditor")
    st.markdown("**AI 기반 코드 품질 분석 도구** - 간단한 3단계로 프로젝트를 분석하세요!")
    st.divider()


def render_navigation(project_path: str = ""):
    """Render top navigation bar."""
    # Only show navigation if we have analysis results or are viewing secondary pages
    if st.session_state.analysis_results or st.session_state.current_view != 'main':
        st.markdown("### 📍 네비게이션")

        # Navigation buttons
        cols = st.columns(5)
        
        # 프로젝트 경로 확인 (session_state 또는 파라미터에서)
        has_project_path = bool(st.session_state.project_path or project_path)

        with cols[0]:
            if st.button("🏠 메인", width='stretch',
                        type="primary" if st.session_state.current_view == 'main' else "secondary"):
                st.session_state.current_view = 'main'
                st.rerun()

        with cols[1]:
            if st.button("📊 분석 결과", width='stretch',
                        type="primary" if st.session_state.current_view == 'results' else "secondary",
                        disabled=not st.session_state.analysis_results):
                st.session_state.current_view = 'results'
                st.rerun()

        with cols[2]:
            if st.button("📈 히스토리", width='stretch',
                        type="primary" if st.session_state.current_view == 'history' else "secondary",
                        disabled=not has_project_path):
                st.session_state.current_view = 'history'
                st.rerun()

        with cols[3]:
            if st.button("🔄 비교", width='stretch',
                        type="primary" if st.session_state.current_view == 'comparison' else "secondary",
                        disabled=not has_project_path):
                st.session_state.current_view = 'comparison'
                st.rerun()

        with cols[4]:
            if st.button("🌳 폴더 구조", width='stretch',
                        type="primary" if st.session_state.current_view == 'tree' else "secondary",
                        disabled=not has_project_path):
                st.session_state.current_view = 'tree'
                st.rerun()

        st.divider()


def render_sidebar() -> Dict[str, Any]:
    """
    Render the sidebar with analysis configuration.

    Returns:
        Dictionary containing user configuration
    """
    with st.sidebar:
        st.header("⚙️ 분석 설정")

        # Project path selection with file browser
        st.subheader("1️⃣ 프로젝트 선택")

        # Initialize project_path from session state
        if 'project_path' not in st.session_state:
            st.session_state.project_path = ""

        # Quick access to common locations
        with st.expander("📂 빠른 경로 선택", expanded=True):
            import subprocess
            import platform
            import tkinter as tk
            from tkinter import filedialog

            desktop = str(Path.home() / "Desktop")
            documents = str(Path.home() / "Documents")
            home = str(Path.home())

            def select_folder_dialog(initial_dir=None):
                """Open folder selection dialog and return selected path"""
                try:
                    # Create a root window and hide it
                    root = tk.Tk()
                    root.withdraw()
                    root.wm_attributes('-topmost', 1)

                    # Open folder selection dialog
                    folder_path = filedialog.askdirectory(
                        parent=root,
                        initialdir=initial_dir if initial_dir else str(Path.home()),
                        title="분석할 프로젝트 폴더를 선택하세요"
                    )

                    root.destroy()
                    return folder_path if folder_path else None
                except Exception as e:  # pylint: disable=broad-exception-caught
                    # 파일 선택 대화상자는 OS/환경에 따라 다양한 예외가 발생할 수 있으므로
                    # 최상위에서 한 번만 잡고 사용자에게 오류 메시지를 보여줍니다.
                    st.error(f"폴더 선택 실패: {e}")
                    return None

            st.caption("📌 아래 버튼을 클릭하면 폴더 선택 창이 열립니다")

            # Folder browser button (primary action)
            if st.button("📁 폴더 선택", width='stretch', type="primary", key="btn_browse"):
                selected_path = select_folder_dialog()
                if selected_path:
                    st.session_state.project_path = selected_path
                    st.rerun()

            st.divider()
            st.caption("⚡ 또는 빠른 경로로 바로 이동:")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🖥️ 바탕화면", width='stretch', key="btn_desktop"):
                    selected_path = select_folder_dialog(desktop)
                    if selected_path:
                        st.session_state.project_path = selected_path
                        st.rerun()
            with col2:
                if st.button("📁 문서", width='stretch', key="btn_documents"):
                    selected_path = select_folder_dialog(documents)
                    if selected_path:
                        st.session_state.project_path = selected_path
                        st.rerun()

            if st.button("🏠 홈 디렉토리", width='stretch', key="btn_home"):
                selected_path = select_folder_dialog(home)
                if selected_path:
                    st.session_state.project_path = selected_path
                    st.rerun()

            st.caption("💡 폴더 선택 창에서 원하는 프로젝트 폴더를 선택하면 자동으로 경로가 입력됩니다")

        # Manual path input (uses session state directly as key)
        project_path = st.text_input(
            "프로젝트 폴더 경로",
            placeholder="예: C:/Users/YourName/Desktop/my-project",
            help="분석할 프로젝트의 전체 경로를 입력하세요. 위의 빠른 경로 버튼을 사용하거나 직접 입력할 수 있습니다.",
            key="project_path"
        )

        st.divider()

        # Analysis mode
        st.subheader("2️⃣ 분석 관점")
        mode = st.radio(
            "분석 모드 선택",
            options=['deployment', 'personal'],
            format_func=lambda x: f"{'🚀 배포 관점' if x == 'deployment' else '👤 개인 사용 관점'}",
            help="배포 관점: 보안, 성능, 확장성 중심 | 개인 관점: 가독성, 유지보수성 중심"
        )

        mode_info = ANALYSIS_MODES[mode]
        st.info(f"**우선순위**: {', '.join(mode_info['priorities'])}")

        st.divider()

        # Advanced options
        with st.expander("🔧 고급 옵션"):
            skip_ai = st.checkbox(
                "AI 분석 건너뛰기",
                value=False,
                help="정적 분석만 수행 (빠른 분석)"
            )

            use_cache = st.checkbox(
                "캐시 사용",
                value=True,
                help="이전 분석 결과 재사용 (99% 속도 향상)"
            )

            save_history = st.checkbox(
                "히스토리 저장",
                value=True,
                help="분석 결과를 히스토리에 저장"
            )

        st.divider()

        # Action button
        st.subheader("3️⃣ 분석 시작")
        start_button = st.button(
            "🚀 분석 시작",
            type="primary",
            width='stretch',
            disabled=not project_path or st.session_state.analysis_running
        )

        # History viewer button
        if project_path and Path(project_path).exists():
            st.divider()
            st.subheader("📜 히스토리 & 도구")

            col1, col2 = st.columns(2)
            with col1:
                show_history = st.button(
                    "📈 히스토리",
                    width='stretch'
                )
            with col2:
                show_comparison = st.button(
                    "🔄 비교",
                    width='stretch'
                )

            show_tree = st.button(
                "🌳 폴더 구조",
                width='stretch'
            )
        else:
            show_history = False
            show_comparison = False
            show_tree = False

        return {
            'project_path': project_path,
            'mode': mode,
            'skip_ai': skip_ai,
            'use_cache': use_cache,
            'save_history': save_history,
            'start_button': start_button,
            'show_history': show_history,
            'show_comparison': show_comparison,
            'show_tree': show_tree
        }


def render_progress_display():
    """Render real-time progress display."""
    progress = st.session_state.progress

    # Progress bar
    progress_bar = st.progress(progress.percentage / 100)

    # Status message
    if progress.error:
        st.error(f"❌ 오류: {progress.error}")
    elif progress.completed:
        st.success("✅ 분석 완료!")
    else:
        # Stage-based messages
        stage_messages = {
            'validation': '🔍 요구사항 확인 중...',
            'detection': f'🔎 언어 감지 중... {len(progress.languages) if progress.languages else 0}개 언어 발견',
            'static_analysis': '⚙️ 정적 분석 실행 중...',
            'ai_analysis': '🤖 AI 코드 리뷰 진행 중...',
            'finalization': '📝 결과 저장 중...',
        }

        message = stage_messages.get(progress.stage, progress.message)
        st.info(f"{message} ({progress.percentage}%)")

    return progress_bar


def render_download_buttons(results: Dict[str, Any], project_path: Path, mode: str):
    """
    Render download buttons for results.

    Args:
        results: Analysis results
        project_path: Project path
        mode: Analysis mode
    """
    st.subheader("💾 결과 다운로드")

    col1, col2, col3 = st.columns(3)

    with col1:
        # JSON download
        json_data = {
            'timestamp': datetime.now().isoformat(),
            'project_path': str(project_path),
            'mode': mode,
            'languages': results.get('languages', []),
            'static_results': results.get('static_results', {}),
            'ai_results': results.get('ai_results')
        }

        json_str = json.dumps(json_data, indent=2, ensure_ascii=False)

        st.download_button(
            label="📄 JSON 다운로드",
            data=json_str,
            file_name=f"vibe-audit-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json",
            mime="application/json",
            width='stretch'
        )

    with col2:
        # HTML download
        try:
            html_reporter = HTMLReporter(mode)

            # Generate HTML in memory
            temp_path = Path("temp_report.html")
            html_reporter.generate_report(
                results['static_results'],
                results.get('ai_results'),
                project_path,
                temp_path
            )

            # Read generated HTML
            with open(temp_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            # Clean up temp file
            temp_path.unlink(missing_ok=True)

            st.download_button(
                label="📊 HTML 다운로드",
                data=html_content,
                file_name=f"vibe-audit-{datetime.now().strftime('%Y%m%d-%H%M%S')}.html",
                mime="text/html",
                width='stretch'
            )
        except Exception as e:
            st.error(f"HTML 생성 실패: {e}")

    with col3:
        # PDF download
        try:
            pdf_reporter = PDFReporter(mode)

            # Generate PDF directly to memory (BytesIO)
            pdf_content = pdf_reporter.generate_report_to_bytes(
                results,
                project_path
            )

            st.download_button(
                label="📑 PDF 다운로드",
                data=pdf_content,
                file_name=f"vibe-audit-{datetime.now().strftime('%Y%m%d-%H%M%S')}.pdf",
                mime="application/pdf",
                width='stretch'
            )
        except Exception as e:
            st.error(f"PDF 생성 실패: {e}")


def render_paginated_issues(issues: list, title: str):
    """
    Render paginated issue list.

    Args:
        issues: List of issues
        title: Section title
    """
    if not issues:
        st.success(f"{title}에서 이슈를 발견하지 못했습니다! 🎉")
        return

    # Pagination controls
    items_per_page = st.session_state.items_per_page
    total_pages = (len(issues) - 1) // items_per_page + 1

    col1, col2, col3 = st.columns([2, 3, 2])

    with col1:
        new_items = st.selectbox(
            "페이지당 항목 수",
            options=[10, 20, 50, 100],
            index=1,
            key=f"items_select_{title}"
        )
        if new_items != st.session_state.items_per_page:
            st.session_state.items_per_page = new_items
            st.session_state.page_number = 0
            st.rerun()

    with col2:
        st.write(f"**총 {len(issues)}개 이슈** (페이지 {st.session_state.page_number + 1}/{total_pages})")

    with col3:
        col_prev, col_next = st.columns(2)
        with col_prev:
            if st.button("◀ 이전", disabled=st.session_state.page_number == 0, width='stretch', key=f"prev_{title}"):
                st.session_state.page_number = max(0, st.session_state.page_number - 1)
                st.rerun()
        with col_next:
            if st.button("다음 ▶", disabled=st.session_state.page_number >= total_pages - 1, width='stretch', key=f"next_{title}"):
                st.session_state.page_number = min(total_pages - 1, st.session_state.page_number + 1)
                st.rerun()

    st.divider()

    # Calculate pagination
    start_idx = st.session_state.page_number * items_per_page
    end_idx = min(start_idx + items_per_page, len(issues))
    page_issues = issues[start_idx:end_idx]

    # Display issues
    for idx, issue in enumerate(page_issues, start=start_idx + 1):
        severity_emoji = {
            'critical': '🔴',
            'warning': '🟡',
            'info': '🟢'
        }.get(issue.get('severity', 'info'), '⚪')

        with st.expander(f"{idx}. {severity_emoji} {issue.get('message', 'No message')[:100]}..."):
            st.write(f"**파일**: {issue.get('file', 'N/A')}")
            st.write(f"**라인**: {issue.get('line', 'N/A')}")
            st.write(f"**도구**: {issue.get('tool', 'N/A')}")
            st.write(f"**심각도**: {issue.get('severity', 'N/A')}")
            st.write(f"**메시지**: {issue.get('message', 'N/A')}")


def render_history_viewer(project_path: Path):
    """
    Render history comparison viewer.

    Args:
        project_path: Project path
    """
    # Back button
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("🏠 메인으로", type="secondary", width='stretch'):
            st.session_state.current_view = 'main'
            st.rerun()

    st.header("📈 분석 히스토리")

    try:
        engine = AnalyzerEngine(project_path)
        trend_data = engine.get_trend_data()

        if trend_data['total_runs'] == 0:
            st.info("아직 분석 히스토리가 없습니다.")
            return

        # Summary
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("총 분석 횟수", trend_data['total_runs'])

        with col2:
            st.metric("현재 이슈", trend_data['current_issues'])

        with col3:
            change = trend_data['change']
            st.metric("변화량", f"{change:+d}", delta=f"{trend_data['change_percent']:+.1f}%")

        with col4:
            trend_emoji = {
                'improving': '📈 개선 중',
                'declining': '📉 악화 중',
                'stable': '➡️ 안정'
            }.get(trend_data['trend'], '➡️ 안정')
            st.metric("추세", trend_emoji)

        st.divider()

        # Timeline chart
        timeline = trend_data.get('timeline', [])
        if timeline:
            import plotly.graph_objects as go

            timestamps = [datetime.fromisoformat(e['timestamp']).strftime('%m/%d %H:%M') for e in timeline[-20:]]
            critical = [e['critical'] for e in timeline[-20:]]
            warning = [e['warning'] for e in timeline[-20:]]
            info_count = [e['info'] for e in timeline[-20:]]

            fig = go.Figure()

            fig.add_trace(go.Scatter(x=timestamps, y=critical, name='Critical', line=dict(color='red'), stackgroup='one'))
            fig.add_trace(go.Scatter(x=timestamps, y=warning, name='Warning', line=dict(color='orange'), stackgroup='one'))
            fig.add_trace(go.Scatter(x=timestamps, y=info_count, name='Info', line=dict(color='green'), stackgroup='one'))

            fig.update_layout(
                title="이슈 추이 (최근 20회)",
                xaxis_title="시간",
                yaxis_title="이슈 개수",
                hovermode='x unified',
                height=400
            )

            st.plotly_chart(fig, width='stretch')

        # Recent history table
        st.subheader("최근 분석 기록")

        history_data = []
        for entry in timeline[-10:]:
            history_data.append({
                '시간': datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d %H:%M'),
                '총 이슈': entry['total_issues'],
                'Critical': entry['critical'],
                'Warning': entry['warning'],
                'Info': entry['info']
            })

        if history_data:
            import pandas as pd
            df = pd.DataFrame(history_data)
            st.dataframe(df, width='stretch', hide_index=True)

    except Exception as e:
        st.error(f"히스토리 로드 실패: {e}")


def render_comparison_mode(project_path: Path):
    """
    Render comparison mode for comparing two analysis results.

    Args:
        project_path: Project path
    """
    # Back button
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("🏠 메인으로", type="secondary", width='stretch', key="comparison_back"):
            st.session_state.current_view = 'main'
            st.rerun()

    st.header("🔄 분석 결과 비교")

    try:
        engine = AnalyzerEngine(project_path)
        trend_data = engine.get_trend_data()
        timeline = trend_data.get('timeline', [])

        if len(timeline) < 2:
            st.info("비교하려면 최소 2개의 분석 결과가 필요합니다.")
            st.write("먼저 프로젝트를 여러 번 분석해주세요.")
            return

        # Select two analysis results to compare
        st.subheader("비교할 분석 결과 선택")

        col1, col2 = st.columns(2)

        # Format timeline entries for selectbox
        timeline_options = [
            f"{datetime.fromisoformat(e['timestamp']).strftime('%Y-%m-%d %H:%M')} (총 {e['total_issues']}개 이슈)"
            for e in timeline
        ]

        with col1:
            st.write("**이전 분석 (기준)**")
            baseline_idx = st.selectbox(
                "이전 분석 선택",
                range(len(timeline)),
                format_func=lambda i: timeline_options[i],
                index=max(0, len(timeline) - 2),
                key="baseline_select"
            )

        with col2:
            st.write("**최근 분석 (비교 대상)**")
            current_idx = st.selectbox(
                "최근 분석 선택",
                range(len(timeline)),
                format_func=lambda i: timeline_options[i],
                index=len(timeline) - 1,
                key="current_select"
            )

        if baseline_idx == current_idx:
            st.warning("⚠️ 서로 다른 분석 결과를 선택해주세요.")
            return

        baseline = timeline[baseline_idx]
        current = timeline[current_idx]

        st.divider()

        # Comparison summary
        st.subheader("📊 비교 요약")

        col1, col2, col3, col4 = st.columns(4)

        total_change = current['total_issues'] - baseline['total_issues']
        critical_change = current['critical'] - baseline['critical']
        warning_change = current['warning'] - baseline['warning']
        info_change = current['info'] - baseline['info']

        with col1:
            st.metric(
                "총 이슈",
                current['total_issues'],
                delta=total_change,
                delta_color="inverse"
            )

        with col2:
            st.metric(
                "Critical",
                current['critical'],
                delta=critical_change,
                delta_color="inverse"
            )

        with col3:
            st.metric(
                "Warning",
                current['warning'],
                delta=warning_change,
                delta_color="inverse"
            )

        with col4:
            st.metric(
                "Info",
                current['info'],
                delta=info_change,
                delta_color="inverse"
            )

        st.divider()

        # Detailed comparison chart
        st.subheader("📈 상세 비교")

        import plotly.graph_objects as go

        categories = ['Critical', 'Warning', 'Info']
        baseline_values = [baseline['critical'], baseline['warning'], baseline['info']]
        current_values = [current['critical'], current['warning'], current['info']]

        fig = go.Figure(data=[
            go.Bar(name='이전', x=categories, y=baseline_values, marker_color='lightblue'),
            go.Bar(name='최근', x=categories, y=current_values, marker_color='darkblue')
        ])

        fig.update_layout(
            title="심각도별 이슈 비교",
            xaxis_title="심각도",
            yaxis_title="이슈 개수",
            barmode='group',
            height=400
        )

        st.plotly_chart(fig, width='stretch')

        # Analysis
        st.subheader("💡 분석")

        if total_change < 0:
            st.success(f"✅ 총 {abs(total_change)}개의 이슈가 해결되었습니다! 코드 품질이 개선되었습니다.")
        elif total_change > 0:
            st.error(f"⚠️ 총 {total_change}개의 새로운 이슈가 발견되었습니다. 코드 리뷰가 필요합니다.")
        else:
            st.info("ℹ️ 이슈 개수에 변화가 없습니다.")

        # Detailed breakdown
        with st.expander("📋 상세 변화 내역"):
            st.write("### Critical 이슈")
            if critical_change < 0:
                st.write(f"- ✅ {abs(critical_change)}개 해결")
            elif critical_change > 0:
                st.write(f"- ❌ {critical_change}개 추가")
            else:
                st.write("- ➡️ 변화 없음")

            st.write("### Warning 이슈")
            if warning_change < 0:
                st.write(f"- ✅ {abs(warning_change)}개 해결")
            elif warning_change > 0:
                st.write(f"- ❌ {warning_change}개 추가")
            else:
                st.write("- ➡️ 변화 없음")

            st.write("### Info 이슈")
            if info_change < 0:
                st.write(f"- ✅ {abs(info_change)}개 해결")
            elif info_change > 0:
                st.write(f"- ❌ {info_change}개 추가")
            else:
                st.write("- ➡️ 변화 없음")

    except Exception as e:
        st.error(f"비교 모드 로드 실패: {e}")


def render_folder_tree(project_path: Path):
    """
    Render folder tree viewer.

    Args:
        project_path: Project path
    """
    # Back button
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("🏠 메인으로", type="secondary", width='stretch', key="tree_back"):
            st.session_state.current_view = 'main'
            st.rerun()

    st.header("🌳 프로젝트 폴더 구조")

    st.info("프로젝트의 폴더 구조를 표시합니다. 분석 대상 파일을 확인할 수 있습니다.")

    try:
        # File extensions for analysis
        analyzable_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx',
            '.go', '.rs', '.php', '.rb', '.kt',
            '.swift', '.cs', '.java'
        }

        # Exclude directories
        exclude_dirs = {
            'node_modules', '__pycache__', '.git', '.venv',
            'venv', 'env', 'dist', 'build', '.idea',
            '.vscode', 'coverage', '.pytest_cache'
        }

        def build_tree(path: Path, prefix: str = "", is_last: bool = True, depth: int = 0, max_depth: int = 5):
            """Build tree structure recursively"""
            if depth > max_depth:
                return []

            lines = []

            if not path.exists():
                return lines

            # Current item
            connector = "└── " if is_last else "├── "
            name = path.name

            # Check if analyzable
            is_analyzable = path.is_file() and path.suffix in analyzable_extensions
            icon = "📄" if path.is_file() else "📁"
            suffix = " ⭐" if is_analyzable else ""

            lines.append(f"{prefix}{connector}{icon} {name}{suffix}")

            # Process children if directory
            if path.is_dir() and name not in exclude_dirs:
                # Get children
                try:
                    children = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name))
                    # Limit children to avoid too many items
                    if len(children) > 50:
                        children = children[:50]
                        has_more = True
                    else:
                        has_more = False

                    extension = "    " if is_last else "│   "

                    for i, child in enumerate(children):
                        is_last_child = (i == len(children) - 1) and not has_more
                        lines.extend(build_tree(
                            child,
                            prefix + extension,
                            is_last_child,
                            depth + 1,
                            max_depth
                        ))

                    if has_more:
                        lines.append(f"{prefix}{extension}└── ... ({len(list(path.iterdir())) - 50} more items)")

                except PermissionError:
                    pass

            return lines

        # Build tree
        tree_lines = [f"📁 {project_path.name}"]
        try:
            children = sorted(project_path.iterdir(), key=lambda p: (not p.is_dir(), p.name))

            for i, child in enumerate(children):
                is_last = (i == len(children) - 1)
                tree_lines.extend(build_tree(child, "", is_last, depth=1, max_depth=4))

        except PermissionError:
            st.error("프로젝트 폴더에 접근할 수 없습니다.")
            return

        # Display tree
        st.code("\n".join(tree_lines), language="text")

        # Statistics
        st.divider()
        st.subheader("📊 파일 통계")

        # Count files
        total_files = 0
        analyzable_files = 0
        file_counts = {}

        for file_path in project_path.rglob("*"):
            if file_path.is_file():
                # Skip excluded directories
                if any(excl in file_path.parts for excl in exclude_dirs):
                    continue

                total_files += 1

                ext = file_path.suffix
                if ext in analyzable_extensions:
                    analyzable_files += 1
                    file_counts[ext] = file_counts.get(ext, 0) + 1

        col1, col2 = st.columns(2)

        with col1:
            st.metric("총 파일 수", total_files)

        with col2:
            st.metric("분석 가능 파일", analyzable_files)

        # File type breakdown
        if file_counts:
            st.write("**파일 유형별 분포**")
            for ext, count in sorted(file_counts.items(), key=lambda x: x[1], reverse=True):
                st.write(f"- `{ext}`: {count}개")

        st.info("⭐ 표시된 파일은 분석 대상 파일입니다.")

    except Exception as e:
        st.error(f"폴더 구조 표시 실패: {e}")


def render_results_summary(results: Dict[str, Any], project_path: Path, mode: str):
    """
    Render analysis results summary.

    Args:
        results: Analysis results dictionary
        project_path: Project path
        mode: Analysis mode
    """
    # Action buttons at top
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        if st.button("🔄 새 분석 시작", type="primary", width='stretch'):
            st.session_state.analysis_results = None
            st.session_state.current_view = 'main'
            st.session_state.page_number = 0
            st.rerun()
    with col2:
        if st.button("📈 히스토리 보기", type="secondary", width='stretch'):
            st.session_state.current_view = 'history'
            st.rerun()
    with col3:
        if st.button("🔄 결과 비교", type="secondary", width='stretch'):
            st.session_state.current_view = 'comparison'
            st.rerun()

    st.divider()
    st.header("📊 분석 결과")

    # Extract data
    languages = results.get('languages', [])
    static_results = results.get('static_results', {})
    ai_results = results.get('ai_results')

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="감지된 언어",
            value=len(languages),
            delta=None
        )

    static_issues = static_results.get('issues', [])
    critical_count = sum(1 for issue in static_issues if issue.get('severity') == 'critical')
    warning_count = sum(1 for issue in static_issues if issue.get('severity') == 'warning')
    info_count = sum(1 for issue in static_issues if issue.get('severity') == 'info')

    with col2:
        st.metric(
            label="🔴 Critical",
            value=critical_count,
            delta=None
        )

    with col3:
        st.metric(
            label="🟡 Warning",
            value=warning_count,
            delta=None
        )

    with col4:
        st.metric(
            label="🟢 Info",
            value=info_count,
            delta=None
        )

    st.divider()

    # Download buttons
    render_download_buttons(results, project_path, mode)

    st.divider()

    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 요약",
        "⚙️ 정적 분석",
        "🤖 AI 분석",
        "📈 언어 분포"
    ])

    with tab1:
        render_summary_tab(results)

    with tab2:
        render_static_analysis_tab(static_results)

    with tab3:
        render_ai_analysis_tab(ai_results)

    with tab4:
        render_languages_tab(languages, static_issues)


def render_summary_tab(results: Dict[str, Any]):
    """Render summary tab."""
    st.subheader("프로젝트 개요")

    languages = results.get('languages', [])
    st.write(f"**감지된 언어**: {', '.join(languages)}")
    st.write(f"**분석 모드**: {results.get('mode', 'N/A')}")
    st.write(f"**프로젝트 경로**: {results.get('project_path', 'N/A')}")

    st.divider()

    # Issue severity distribution
    static_results = results.get('static_results', {})
    static_issues = static_results.get('issues', [])

    if static_issues:
        st.subheader("이슈 심각도 분포")

        severity_counts = {
            'critical': sum(1 for i in static_issues if i.get('severity') == 'critical'),
            'warning': sum(1 for i in static_issues if i.get('severity') == 'warning'),
            'info': sum(1 for i in static_issues if i.get('severity') == 'info'),
        }

        # Plotly bar chart
        import plotly.graph_objects as go

        fig = go.Figure(data=[
            go.Bar(
                x=['Critical', 'Warning', 'Info'],
                y=[severity_counts['critical'], severity_counts['warning'], severity_counts['info']],
                marker_color=['#ff4444', '#ffbb33', '#00C851']
            )
        ])

        fig.update_layout(
            title="심각도별 이슈 개수",
            xaxis_title="심각도",
            yaxis_title="이슈 개수",
            height=400
        )

        st.plotly_chart(fig, width='stretch')
    else:
        st.info("발견된 이슈가 없습니다! 🎉")


def render_static_analysis_tab(static_results: Dict[str, Any]):
    """Render static analysis results tab with pagination."""
    st.subheader("정적 분석 결과")

    issues = static_results.get('issues', [])

    if not issues:
        st.success("정적 분석에서 이슈를 발견하지 못했습니다! 🎉")
        return

    # Reset page number when changing filters
    if 'last_severity_filter' not in st.session_state:
        st.session_state.last_severity_filter = ['critical', 'warning', 'info']

    # Filter by severity
    severity_filter = st.multiselect(
        "심각도 필터",
        options=['critical', 'warning', 'info'],
        default=['critical', 'warning', 'info'],
        format_func=lambda x: f"{'🔴 Critical' if x == 'critical' else '🟡 Warning' if x == 'warning' else '🟢 Info'}"
    )

    # Reset page if filter changed
    if severity_filter != st.session_state.last_severity_filter:
        st.session_state.page_number = 0
        st.session_state.last_severity_filter = severity_filter

    filtered_issues = [i for i in issues if i.get('severity') in severity_filter]

    # Render paginated issues
    render_paginated_issues(filtered_issues, "정적 분석")


def render_ai_analysis_tab(ai_results: Optional[Dict[str, Any]]):
    """Render AI analysis results tab."""
    st.subheader("AI 코드 리뷰 결과")

    # 결과 자체가 없거나 skip 된 경우
    if not ai_results:
        st.info("AI 분석이 건너뛰어졌거나 결과가 없습니다.")
        return

    # API 오류/타임아웃 등으로 실패한 경우
    if ai_results.get("error"):
        st.warning(f"AI 분석 중 오류가 발생했습니다: {ai_results['error']}")
        st.info("🔑 API 키 설정, 네트워크 연결, 타임아웃 설정 등을 확인해 주세요.")
        return

    issues = ai_results.get("issues", [])

    if not issues:
        st.success("AI 분석에서 특별한 이슈를 발견하지 못했습니다! 🎉")
        return

    st.write(f"**총 {len(issues)}개 AI 이슈 발견**")

    # 심각도별 이슈 그룹핑 (HTML/JSON과 동일한 구조 사용)
    issues_by_severity = {
        "critical": [],
        "warning": [],
        "info": [],
    }

    for issue in issues:
        severity = issue.get("severity", "info").lower()
        if severity in issues_by_severity:
            issues_by_severity[severity].append(issue)
        else:
            issues_by_severity["info"].append(issue)

    severity_order = ["critical", "warning", "info"]
    severity_labels = {
        "critical": "🔴 Critical",
        "warning": "🟡 Warning",
        "info": "🟢 Info",
    }

    for severity in severity_order:
        severity_issues = issues_by_severity[severity]
        if not severity_issues:
            continue

        st.markdown(f"### {severity_labels[severity]} ({len(severity_issues)}개)")

        for idx, issue in enumerate(severity_issues, 1):
            raw_title = issue.get("title", "No title") or "No title"
            details = issue.get("details", []) or []

            # Markdown 표(| ... |), 코드펜스(```), 언어 태그만 있는 줄은 제거
            filtered_details = []
            for line in details:
                stripped = line.strip()
                if not stripped:
                    continue
                if stripped.startswith("|"):
                    continue
                if stripped.startswith("```"):
                    continue
                if stripped in {"python", "bash", "sh", "json", "yaml"}:
                    continue
                filtered_details.append(line)

            # 제목이 표/마스킹이고 실제 설명 줄이 있을 때만 첫 번째 줄을 제목으로 승격
            promote_to_detail_title = (
                (raw_title.strip().startswith("|") or raw_title.replace("■", "").strip() == "")
                and bool(filtered_details)
            )

            if promote_to_detail_title:
                title = filtered_details[0][:80]
                body_lines = filtered_details[1:]
            else:
                # 승격 불가하고 제목이 여전히 표/마스킹 뿐이면, 안전한 기본 제목 사용
                if raw_title.strip().startswith("|") or raw_title.replace("■", "").strip() == "":
                    title = "AI 분석 이슈"
                else:
                    title = raw_title
                body_lines = filtered_details

            # 한 이슈를 하나의 expander로 묶어서 상세 설명 표시
            with st.expander(f"{idx}. {title}"):
                if body_lines:
                    for line in body_lines:
                        st.write(f"- {line}")
                else:
                    st.write("세부 설명이 없습니다.")


def render_languages_tab(languages: list, issues: list):
    """Render languages distribution tab."""
    st.subheader("언어별 분석")

    if not languages:
        st.info("감지된 언어가 없습니다.")
        return

    # Count issues per language
    language_issues = {}
    for lang in languages:
        language_issues[lang] = sum(
            1 for issue in issues
            if lang.lower() in issue.get('file', '').lower()
        )

    # Pie chart
    import plotly.graph_objects as go

    fig = go.Figure(data=[go.Pie(
        labels=list(language_issues.keys()),
        values=list(language_issues.values()),
        hole=.3
    )])

    fig.update_layout(
        title="언어별 이슈 분포",
        height=400
    )

    st.plotly_chart(fig, width='stretch')

    # Table
    st.write("**언어별 이슈 개수**")
    for lang, count in language_issues.items():
        st.write(f"- **{lang}**: {count}개 이슈")


def run_analysis(config: Dict[str, Any]):
    """
    Run analysis with the given configuration.

    Args:
        config: Analysis configuration dictionary
    """
    st.session_state.analysis_running = True
    st.session_state.progress = AnalysisProgress()
    st.session_state.page_number = 0  # Reset pagination

    # Progress callback
    def progress_callback(progress: AnalysisProgress):
        st.session_state.progress = progress

    try:
        # Create analyzer engine
        engine = AnalyzerEngine(
            project_path=Path(config['project_path']),
            mode=config['mode'],
            skip_ai=config['skip_ai'],
            use_cache=config['use_cache'],
            save_history=config['save_history'],
            progress_callback=progress_callback
        )

        # Run analysis
        results = engine.analyze()

        # Store results
        st.session_state.analysis_results = results

    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        st.session_state.progress.error = str(e)
        st.session_state.progress.completed = True

    finally:
        st.session_state.analysis_running = False


def main():
    """Main Streamlit application."""
    init_session_state()
    render_header()
    
    # Sidebar configuration
    config = render_sidebar()
    
    # 주의: st.text_input(key="project_path")가 이미 session_state를 자동 관리하므로
    # 위젯 생성 후에는 session_state를 직접 수정할 수 없습니다.
    # config['project_path']는 위젯의 현재 값을 반환하므로 그대로 사용합니다.
    
    # 네비게이션 렌더링 (project_path 전달)
    render_navigation(config.get('project_path', ''))

    # Handle sidebar button clicks (legacy support)
    if config.get('show_history'):
        st.session_state.current_view = 'history'
        st.rerun()
    elif config.get('show_comparison'):
        st.session_state.current_view = 'comparison'
        st.rerun()
    elif config.get('show_tree'):
        st.session_state.current_view = 'tree'
        st.rerun()

    # Main content area
    if config['start_button']:
        # Validate project path
        project_path = Path(config['project_path'])
        if not project_path.exists():
            st.error(f"❌ 프로젝트 경로가 존재하지 않습니다: {config['project_path']}")
        elif not project_path.is_dir():
            st.error(f"❌ 유효한 디렉토리가 아닙니다: {config['project_path']}")
        else:
            # Run analysis
            with st.spinner('분석 중...'):
                run_analysis(config)

            # Set view to results and trigger rerun
            st.session_state.current_view = 'results'
            st.rerun()

    # Display content based on current_view
    if st.session_state.analysis_running:
        st.header("⏳ 분석 진행 중...")
        render_progress_display()
    elif st.session_state.current_view == 'history':
        # 프로젝트 경로 확인
        project_path_str = config.get('project_path') or st.session_state.project_path
        if project_path_str and Path(project_path_str).exists():
            render_history_viewer(Path(project_path_str))
        else:
            st.warning("⚠️ 프로젝트 경로를 먼저 설정해주세요.")
            st.info("👈 왼쪽 사이드바에서 프로젝트 폴더를 선택하세요.")
    elif st.session_state.current_view == 'comparison':
        # 프로젝트 경로 확인
        project_path_str = config.get('project_path') or st.session_state.project_path
        if project_path_str and Path(project_path_str).exists():
            render_comparison_mode(Path(project_path_str))
        else:
            st.warning("⚠️ 프로젝트 경로를 먼저 설정해주세요.")
            st.info("👈 왼쪽 사이드바에서 프로젝트 폴더를 선택하세요.")
    elif st.session_state.current_view == 'tree':
        # 프로젝트 경로 확인
        project_path_str = config.get('project_path') or st.session_state.project_path
        if project_path_str and Path(project_path_str).exists():
            render_folder_tree(Path(project_path_str))
        else:
            st.warning("⚠️ 프로젝트 경로를 먼저 설정해주세요.")
            st.info("👈 왼쪽 사이드바에서 프로젝트 폴더를 선택하세요.")
    elif st.session_state.current_view == 'results' and st.session_state.analysis_results:
        render_results_summary(
            st.session_state.analysis_results,
            Path(config.get('project_path', st.session_state.project_path)),
            config['mode']
        )
    elif st.session_state.current_view == 'main' or not st.session_state.analysis_results:
        # Welcome screen
        st.info("👈 왼쪽 사이드바에서 프로젝트를 선택하고 분석을 시작하세요!")

        st.subheader("📖 사용 방법")
        st.markdown("""
        1. **프로젝트 선택**: 분석할 프로젝트 폴더 경로를 입력하세요
        2. **분석 관점 선택**: 배포 관점 또는 개인 사용 관점을 선택하세요
        3. **분석 시작**: '🚀 분석 시작' 버튼을 클릭하세요

        ### ✨ v1.10.0 새로운 기능
        - 📍 **상단 네비게이션 바**: 메인, 분석 결과, 히스토리, 비교, 폴더 구조 간 빠른 이동
        - 🏠 **홈으로 돌아가기**: 모든 화면에서 메인 페이지로 쉽게 복귀
        - 🔄 **새 분석 시작**: 분석 결과 화면에서 바로 새로운 분석 시작
        - 📂 **빠른 경로 선택**: 바탕화면, 문서 폴더 빠른 접근
        - 📄 **결과 다운로드**: JSON/HTML/PDF 형식으로 저장
        - 📈 **히스토리 뷰어**: 과거 분석 결과 및 추세 확인
        - 🔄 **비교 모드**: 두 분석 결과 비교 및 개선/악화 추적
        - 🌳 **폴더 트리 뷰어**: 프로젝트 구조 및 분석 대상 파일 확인
        - 📊 **페이지네이션**: 대량 이슈도 편리하게 탐색 (10/20/50/100개씩)
        - 🔍 **고급 필터링**: 심각도별 이슈 필터링

        ### 지원 언어
        Python, JavaScript, TypeScript, Go, Rust, PHP, Ruby, Kotlin, Swift, C#, Java

        ### 분석 도구
        - 정적 분석: Pylint, ESLint, staticcheck, clippy, PHPStan, RuboCop 등 15+ 도구
        - AI 분석: Claude API 기반 코드 리뷰
        """)


if __name__ == "__main__":
    main()
