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

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.analyzer_engine import AnalyzerEngine, AnalysisProgress
from src.config.settings import ANALYSIS_MODES
from src.utils.logger import setup_logger

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

        # Project path selection
        st.subheader("1️⃣ 프로젝트 선택")
        project_path = st.text_input(
            "프로젝트 폴더 경로",
            placeholder="C:/Users/YourName/project",
            help="분석할 프로젝트의 전체 경로를 입력하세요"
        )

        # Browse button hint
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

        return {
            'project_path': project_path,
            'mode': mode,
            'skip_ai': skip_ai,
            'use_cache': use_cache,
            'save_history': save_history,
            'start_button': start_button
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


def render_results_summary(results: Dict[str, Any]):
    """
    Render analysis results summary.

    Args:
        results: Analysis results dictionary
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

        # Simple bar chart
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
    """Render static analysis results tab."""
    st.subheader("정적 분석 결과")

    issues = static_results.get('issues', [])

    if not issues:
        st.success("정적 분석에서 이슈를 발견하지 못했습니다! 🎉")
        return

    # Filter by severity
    severity_filter = st.multiselect(
        "심각도 필터",
        options=['critical', 'warning', 'info'],
        default=['critical', 'warning', 'info'],
        format_func=lambda x: f"{'🔴 Critical' if x == 'critical' else '🟡 Warning' if x == 'warning' else '🟢 Info'}"
    )

    filtered_issues = [i for i in issues if i.get('severity') in severity_filter]

    st.write(f"**총 {len(filtered_issues)}개 이슈 발견**")

    # Display issues
    for idx, issue in enumerate(filtered_issues[:50], 1):  # Limit to 50 for performance
        severity_emoji = {
            'critical': '🔴',
            'warning': '🟡',
            'info': '🟢'
        }.get(issue.get('severity', 'info'), '⚪')

        with st.expander(f"{severity_emoji} {issue.get('message', 'No message')[:100]}..."):
            st.write(f"**파일**: {issue.get('file', 'N/A')}")
            st.write(f"**라인**: {issue.get('line', 'N/A')}")
            st.write(f"**도구**: {issue.get('tool', 'N/A')}")
            st.write(f"**메시지**: {issue.get('message', 'N/A')}")

    if len(filtered_issues) > 50:
        st.info(f"처음 50개 이슈만 표시됩니다. 전체 {len(filtered_issues)}개 이슈가 있습니다.")


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

        with st.expander(f"{severity_emoji} {insight.get('category', 'General')}: {insight.get('message', 'No message')[:80]}..."):
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

    # Display as simple table
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
    elif st.session_state.analysis_results:
        render_results_summary(st.session_state.analysis_results)
    else:
        # Welcome screen
        st.info("👈 왼쪽 사이드바에서 프로젝트를 선택하고 분석을 시작하세요!")

        st.subheader("📖 사용 방법")
        st.markdown("""
        1. **프로젝트 선택**: 분석할 프로젝트 폴더 경로를 입력하세요
        2. **분석 관점 선택**: 배포 관점 또는 개인 사용 관점을 선택하세요
        3. **분석 시작**: '🚀 분석 시작' 버튼을 클릭하세요

        ### 지원 언어
        Python, JavaScript, TypeScript, Go, Rust, PHP, Ruby, Kotlin, Swift, C#, Java

        ### 분석 도구
        - 정적 분석: Pylint, ESLint, staticcheck, clippy, PHPStan, RuboCop 등 15+ 도구
        - AI 분석: Claude API 기반 코드 리뷰
        """)


if __name__ == "__main__":
    main()
