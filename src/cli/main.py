"""Main CLI entry point for Vibe-Code Auditor."""

import sys
from datetime import datetime
from pathlib import Path
import click
from rich.console import Console

from typing import Optional

from src.config.settings import ANALYSIS_MODES, ANTHROPIC_API_KEY
from src.config.config_loader import ConfigLoader
from src.detectors.language_detector import LanguageDetector
from src.analyzers.static_analyzer import StaticAnalyzer
from src.analyzers.ai_analyzer import AIAnalyzer
from src.reporters.cli_reporter import CLIReporter
from src.reporters.json_reporter import JSONReporter
from src.reporters.html_reporter import HTMLReporter
from src.utils.logger import setup_logger
from src.utils.history_tracker import HistoryTracker
from src.utils.cache_manager import CacheManager

console = Console()
logger = setup_logger(__name__)


@click.command()
@click.option(
    '--path',
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    required=True,
    help='로컬 프로젝트 폴더 경로'
)
@click.option(
    '--mode',
    type=click.Choice(['deployment', 'personal'], case_sensitive=False),
    required=False,
    help='분석 관점 (deployment: 배포 관점, personal: 자가 사용 관점)'
)
@click.option(
    '--skip-ai',
    is_flag=True,
    default=False,
    help='AI 분석 건너뛰기 (정적 분석만 수행)'
)
@click.option(
    '--verbose',
    '-v',
    is_flag=True,
    default=False,
    help='상세한 로그 출력 (디버깅용)'
)
@click.option(
    '--quiet',
    '-q',
    is_flag=True,
    default=False,
    help='로그 출력 최소화 (에러만 표시)'
)
@click.option(
    '--output',
    '-o',
    type=click.Path(path_type=Path),
    help='리포트 저장 경로 (예: report.json, report.html)'
)
@click.option(
    '--format',
    '-f',
    type=click.Choice(['json', 'html'], case_sensitive=False),
    help='리포트 형식 (json 또는 html)'
)
@click.option(
    '--config',
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
    help='설정 파일 경로 (기본: .vibe-auditor.yml)'
)
@click.option(
    '--init-config',
    is_flag=True,
    default=False,
    help='설정 파일 템플릿 생성'
)
@click.option(
    '--no-history',
    is_flag=True,
    default=False,
    help='히스토리 추적 비활성화'
)
@click.option(
    '--show-history',
    is_flag=True,
    default=False,
    help='분석 히스토리 및 트렌드 표시'
)
@click.option(
    '--no-cache',
    is_flag=True,
    default=False,
    help='결과 캐싱 비활성화 (항상 새로 분석)'
)
@click.option(
    '--clear-cache',
    is_flag=True,
    default=False,
    help='캐시 데이터 삭제'
)
def audit(path: Path, mode: Optional[str], skip_ai: bool, verbose: bool, quiet: bool, output: Optional[Path], format: Optional[str], config: Optional[Path], init_config: bool, no_history: bool, show_history: bool, no_cache: bool, clear_cache: bool):
    """
    Vibe-Code Auditor: AI + 정적 분석 기반 코드 감사 도구

    바이브코딩으로 개발한 프로젝트의 코드 품질, 보안, 최적화 상태를 점검합니다.
    """
    console.print("\n[bold cyan]🔍 Vibe-Code Auditor v1.1[/bold cyan]\n")

    # Handle --show-history flag
    if show_history:
        history_tracker = HistoryTracker(path)
        trend_data = history_tracker.get_trend_data()

        if trend_data['total_runs'] == 0:
            console.print("[yellow]아직 분석 히스토리가 없습니다.[/yellow]\n")
            return

        console.print(f"[bold cyan]📈 분석 히스토리 ({path.name})[/bold cyan]\n")
        console.print(f"[bold]총 분석 횟수:[/bold] {trend_data['total_runs']}")
        console.print(f"[bold]현재 이슈:[/bold] {trend_data['current_issues']}")
        console.print(f"[bold]이전 이슈:[/bold] {trend_data['previous_issues']}")

        change = trend_data['change']
        if trend_data['trend'] == 'improving':
            console.print(f"[bold green]추세:[/bold green] 개선 중 ({change:+d} 이슈, {trend_data['change_percent']:+.1f}%)")
        elif trend_data['trend'] == 'declining':
            console.print(f"[bold red]추세:[/bold red] 악화 중 ({change:+d} 이슈, {trend_data['change_percent']:+.1f}%)")
        else:
            console.print(f"[bold yellow]추세:[/bold yellow] 안정")

        console.print("\n[bold]최근 분석 기록:[/bold]")
        for i, entry in enumerate(trend_data['timeline'][-10:], 1):
            timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d %H:%M')
            console.print(
                f"  {i}. {timestamp} - "
                f"Total: {entry['total_issues']} "
                f"(🔴{entry['critical']} 🟡{entry['warning']} 🟢{entry['info']})"
            )

        console.print()
        return

    # Handle --clear-cache flag
    if clear_cache:
        cache_mgr = CacheManager(path)
        cache_mgr.invalidate()
        console.print("[green]✓ 캐시 데이터가 삭제되었습니다.[/green]\n")
        return

    # Handle --init-config flag
    if init_config:
        config_loader = ConfigLoader(path)
        template_path = config_loader.save_template()
        console.print(f"[green]✓ 설정 파일 템플릿 생성됨:[/green] {template_path}")
        console.print("\n다음 단계:")
        console.print(f"1. {template_path}를 .vibe-auditor.yml로 복사하세요")
        console.print("2. 필요에 따라 설정을 수정하세요")
        console.print("3. 분석 시 자동으로 설정이 적용됩니다\n")
        return

    # Load configuration
    if config:
        # Custom config file path
        logger.info(f"Loading configuration from {config}")
        # We need to load this config file manually
        import yaml
        try:
            with open(config, 'r', encoding='utf-8') as f:
                user_config = yaml.safe_load(f) or {}
            config_loader = ConfigLoader(path)
            config_loader.config = config_loader._deep_merge(config_loader.DEFAULT_CONFIG.copy(), user_config)
        except Exception as e:
            console.print(f"[bold red]❌ 설정 파일 로드 실패:[/bold red] {e}\n")
            sys.exit(1)
    else:
        # Try to load from default location
        config_loader = ConfigLoader(path)

    # CLI arguments override config file
    if mode is None:
        mode = config_loader.get('analysis.mode', 'deployment')
    if not skip_ai:
        skip_ai = config_loader.get('analysis.skip_ai', False)
    if output is None:
        output_path_str = config_loader.get('output.path')
        if output_path_str:
            output = Path(output_path_str)
    if format is None:
        format = config_loader.get('output.format', 'cli')
        if format == 'cli':
            format = None  # CLI is default, not a file format
    if not verbose and not quiet:
        verbose = config_loader.get('output.verbose', False)
        quiet = config_loader.get('output.quiet', False)

    # Set log level based on verbosity
    import logging
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled")
    elif quiet:
        logging.getLogger().setLevel(logging.ERROR)
        logger.setLevel(logging.ERROR)
    else:
        logging.getLogger().setLevel(logging.WARNING)
        logger.setLevel(logging.WARNING)

    logger.debug(f"Final configuration: mode={mode}, skip_ai={skip_ai}, output={output}, format={format}")

    # Validate API key if AI analysis is requested
    if not skip_ai and not ANTHROPIC_API_KEY:
        console.print("[bold red]❌ 오류: ANTHROPIC_API_KEY가 설정되지 않았습니다.[/bold red]")
        console.print("\n다음 단계를 따라주세요:")
        console.print("1. 프로젝트 루트에 .env 파일을 생성하세요")
        console.print("2. .env.example 파일을 참고하여 API 키를 설정하세요")
        console.print("   ANTHROPIC_API_KEY=your_api_key_here")
        console.print("\n또는 --skip-ai 플래그를 사용하여 정적 분석만 수행할 수 있습니다.\n")
        sys.exit(1)

    # Display analysis info
    mode_info = ANALYSIS_MODES[mode]
    console.print(f"[bold]📁 분석 경로:[/bold] {path}")
    console.print(f"[bold]🎯 분석 관점:[/bold] {mode_info['name']}")
    console.print(f"[bold]📊 우선순위:[/bold] {', '.join(mode_info['priorities'])}\n")

    # Step 1: Detect languages
    console.print("[bold yellow]1️⃣ 프로젝트 언어 감지 중...[/bold yellow]")
    detector = LanguageDetector(path)
    languages = detector.detect()

    if not languages:
        console.print("[bold red]❌ 분석 가능한 코드 파일을 찾을 수 없습니다.[/bold red]\n")
        sys.exit(1)

    console.print(f"[green]✓ 감지된 언어:[/green] {', '.join(languages)}\n")

    # Step 2: Run static analysis
    console.print("[bold yellow]2️⃣ 정적 분석 실행 중...[/bold yellow]")
    use_cache = not no_cache
    static_analyzer = StaticAnalyzer(path, languages, mode, use_cache=use_cache)
    static_results = static_analyzer.analyze()
    console.print(f"[green]✓ 정적 분석 완료[/green]\n")

    # Step 3: Run AI analysis (if not skipped)
    ai_results = None
    if not skip_ai:
        console.print("[bold yellow]3️⃣ AI 코드 리뷰 실행 중...[/bold yellow]")
        ai_analyzer = AIAnalyzer(path, mode)
        ai_results = ai_analyzer.analyze()
        console.print(f"[green]✓ AI 분석 완료[/green]\n")
    else:
        console.print("[bold yellow]3️⃣ AI 분석 건너뜀[/bold yellow]\n")

    # Step 4: Generate report
    console.print("[bold cyan]📋 분석 결과 리포트[/bold cyan]\n")

    # Always show CLI report
    reporter = CLIReporter(mode)
    reporter.generate_report(static_results, ai_results)

    # Save to file if requested
    if output:
        # Determine format
        report_format = format
        if not report_format:
            # Infer from file extension
            ext = output.suffix.lower()
            if ext == '.json':
                report_format = 'json'
            elif ext == '.html':
                report_format = 'html'
            else:
                console.print(f"[bold red]❌ 지원하지 않는 파일 형식:[/bold red] {ext}")
                console.print("지원 형식: .json, .html\n")
                sys.exit(1)

        logger.info(f"Saving {report_format.upper()} report to {output}")

        if report_format == 'json':
            json_reporter = JSONReporter(mode)
            json_reporter.generate_report(static_results, ai_results, path, output)
            console.print(f"\n[green]✓ JSON 리포트 저장됨:[/green] {output}")
        elif report_format == 'html':
            html_reporter = HTMLReporter(mode)
            html_reporter.generate_report(static_results, ai_results, path, output)
            console.print(f"\n[green]✓ HTML 리포트 저장됨:[/green] {output}")

    # Save to history (unless --no-history is set)
    if not no_history:
        try:
            history_tracker = HistoryTracker(path)
            history_tracker.save_result(mode, static_results, ai_results)
            logger.debug("Analysis result saved to history")
        except Exception as e:
            logger.warning(f"Failed to save history: {e}")
            # Don't fail the whole analysis just because history failed

    console.print("\n[bold green]✅ 분석 완료![/bold green]\n")


def main():
    """Entry point for CLI."""
    try:
        audit()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]분석이 중단되었습니다.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]❌ 오류 발생:[/bold red] {str(e)}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()
