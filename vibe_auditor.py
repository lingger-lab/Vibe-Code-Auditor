"""
Vibe-Code Auditor Unified Launcher
Choose between CLI mode or UI mode
"""

import sys
import subprocess
from pathlib import Path


def print_banner():
    """Print application banner"""
    print("=" * 60)
    print("  Vibe-Code Auditor v1.9.0")
    print("  AI 기반 코드 품질 분석 플랫폼")
    print("=" * 60)
    print()


def print_menu():
    """Print mode selection menu"""
    print("모드 선택:")
    print("  1. CLI 모드 (개발자용 - 빠른 분석)")
    print("  2. UI 모드 (모든 사용자 - 웹 인터페이스)")
    print("  3. 종료")
    print()


def launch_cli():
    """Launch CLI mode"""
    print("\n🖥️  CLI 모드를 시작합니다...")
    print("사용법: python -m src.cli.main --path <project_path> --mode <deployment|personal>")
    print()

    # Import and run CLI
    try:
        from src.cli import main as cli_main
        # Pass remaining arguments to CLI
        sys.argv = ['vibe_auditor'] + sys.argv[1:]
        cli_main.main()
    except Exception as e:
        print(f"❌ CLI 모드 실행 오류: {e}")
        print("다음 명령어로 직접 실행해보세요:")
        print("  python -m src.cli.main --path ./project --mode deployment")


def launch_ui():
    """Launch UI mode"""
    print("\n🌐 UI 모드를 시작합니다...")
    print("브라우저가 자동으로 열립니다 (http://localhost:8501)")
    print()

    # Launch Streamlit UI
    app_path = Path(__file__).parent / "src" / "ui" / "app.py"

    try:
        subprocess.run([
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(app_path),
            "--server.headless=true"
        ])
    except KeyboardInterrupt:
        print("\n\n✅ UI 모드를 종료합니다.")
    except Exception as e:
        print(f"❌ UI 모드 실행 오류: {e}")
        print("다음 명령어로 직접 실행해보세요:")
        print("  python run_ui.py")


def main():
    """Main entry point"""
    # If command line arguments are provided, assume CLI mode
    if len(sys.argv) > 1:
        launch_cli()
        return

    # Interactive mode selection
    print_banner()
    print_menu()

    try:
        choice = input("선택 (1-3): ").strip()

        if choice == "1":
            launch_cli()
        elif choice == "2":
            launch_ui()
        elif choice == "3":
            print("\n👋 종료합니다.")
            sys.exit(0)
        else:
            print("\n❌ 잘못된 선택입니다. 1, 2, 또는 3을 입력하세요.")
            input("Enter 키를 눌러 계속...")
            main()
    except KeyboardInterrupt:
        print("\n\n👋 종료합니다.")
        sys.exit(0)
    except EOFError:
        print("\n\n👋 종료합니다.")
        sys.exit(0)


if __name__ == "__main__":
    main()
