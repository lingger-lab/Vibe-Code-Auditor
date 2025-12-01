"""Streamlit UI for Vibe-Code Auditor.

This module provides a web-based user interface for non-technical users
to perform code analysis through a simple 3-click workflow:
1. Select folder
2. Start analysis
3. View results
"""

import streamlit as st
from pathlib import Path
import time
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


def render_header():
    """Render the application header."""
    st.title("🔍 Vibe-Code Auditor")
    st.markdown("**AI 기반 코드 품질 분석 도구** - 간단한 3단계로 프로젝트를 분석하세요!")
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

        # Manual path input
        project_path = st.text_input(
            "프로젝트 폴더 경로",
            placeholder="C:/Users/YourName/project",
            help="분석할 프로젝트의 전체 경로를 입력하세요"
        )

        # Quick access to common locations
        with st.expander("📂 빠른 경로 선택"):
            desktop = str(Path.home() / "Desktop")
            documents = str(Path.home() / "Documents")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🖥️ 바탕화면", use_container_width=True):
                    st.session_state.quick_path = desktop
                    st.rerun()
            with col2:
                if st.button("📁 문서", use_container_width=True):
                    st.session_state.quick_path = documents
                    st.rerun()

            if st.button("🏠 홈 디렉토리", use_container_width=True):
                st.session_state.quick_path = str(Path.home())
                st.rerun()

        # Apply quick path if selected
        if 'quick_path' in st.session_state and not project_path:
            project_path = st.session_state.quick_path

        st.caption("💡 Tip: 탐색기에서 폴더를 복사하여 붙여넣으세요")

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
            use_container_width=True,
            disabled=not project_path or st.session_state.analysis_running
        )

        # History viewer button
        if project_path and Path(project_path).exists():
            st.divider()
            st.subheader("📜 히스토리")
            show_history = st.button(
                "📈 히스토리 보기",
                use_container_width=True
            )
        else:
            show_history = False

        return {
            'project_path': project_path,
            'mode': mode,
            'skip_ai': skip_ai,
            'use_cache': use_cache,
            'save_history': save_history,
            'start_button': start_button,
            'show_history': show_history
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

    col1, col2 = st.columns(2)

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
            use_container_width=True
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
                use_container_width=True
            )
        except Exception as e:
            st.error(f"HTML 생성 실패: {e}")


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
            if st.button("◀ 이전", disabled=st.session_state.page_number == 0, use_container_width=True, key=f"prev_{title}"):
                st.session_state.page_number = max(0, st.session_state.page_number - 1)
                st.rerun()
        with col_next:
            if st.button("다음 ▶", disabled=st.session_state.page_number >= total_pages - 1, use_container_width=True, key=f"next_{title}"):
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

            st.plotly_chart(fig, use_container_width=True)

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
            st.dataframe(df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"히스토리 로드 실패: {e}")


def render_results_summary(results: Dict[str, Any], project_path: Path, mode: str):
    """
    Render analysis results summary.

    Args:
        results: Analysis results dictionary
        project_path: Project path
        mode: Analysis mode
    """
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

        st.plotly_chart(fig, use_container_width=True)
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

    if not ai_results:
        st.info("AI 분석이 건너뛰어졌거나 결과가 없습니다.")
        return

    insights = ai_results.get('insights', [])

    if not insights:
        st.success("AI 분석에서 특별한 이슈를 발견하지 못했습니다! 🎉")
        return

    st.write(f"**총 {len(insights)}개 인사이트 발견**")

    for idx, insight in enumerate(insights, 1):
        severity_emoji = {
            'critical': '🔴',
            'warning': '🟡',
            'info': '🟢'
        }.get(insight.get('severity', 'info'), '⚪')

        with st.expander(f"{idx}. {severity_emoji} {insight.get('category', 'General')}: {insight.get('message', 'No message')[:80]}..."):
            st.write(f"**카테고리**: {insight.get('category', 'N/A')}")
            st.write(f"**심각도**: {insight.get('severity', 'N/A')}")
            st.write(f"**메시지**: {insight.get('message', 'N/A')}")

            if insight.get('recommendation'):
                st.info(f"💡 **권장사항**: {insight['recommendation']}")


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

    st.plotly_chart(fig, use_container_width=True)

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

            # Trigger rerun to update UI
            st.rerun()

    # Display progress or results
    if st.session_state.analysis_running:
        st.header("⏳ 분석 진행 중...")
        render_progress_display()
    elif config.get('show_history') and config['project_path']:
        # Show history viewer
        render_history_viewer(Path(config['project_path']))
    elif st.session_state.analysis_results:
        render_results_summary(
            st.session_state.analysis_results,
            Path(config['project_path']),
            config['mode']
        )
    else:
        # Welcome screen
        st.info("👈 왼쪽 사이드바에서 프로젝트를 선택하고 분석을 시작하세요!")

        st.subheader("📖 사용 방법")
        st.markdown("""
        1. **프로젝트 선택**: 분석할 프로젝트 폴더 경로를 입력하세요
        2. **분석 관점 선택**: 배포 관점 또는 개인 사용 관점을 선택하세요
        3. **분석 시작**: '🚀 분석 시작' 버튼을 클릭하세요

        ### ✨ 새로운 기능
        - 📂 **빠른 경로 선택**: 바탕화면, 문서 폴더 빠른 접근
        - 📄 **결과 다운로드**: JSON/HTML 형식으로 저장
        - 📈 **히스토리 뷰어**: 과거 분석 결과 및 추세 확인
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
