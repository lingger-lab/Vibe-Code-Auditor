"""
Launcher script for Vibe-Code Auditor UI mode.

This script launches the Streamlit web interface for non-technical users.
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Launch the Streamlit UI."""
    # Get the path to the Streamlit app
    app_path = Path(__file__).parent / "src" / "ui" / "app.py"

    if not app_path.exists():
        print(f"Error: UI app not found at {app_path}")
        sys.exit(1)

    print("🚀 Starting Vibe-Code Auditor UI...")
    print(f"📂 App location: {app_path}")
    print("\n" + "=" * 60)
    print("The web interface will open in your browser automatically.")
    print("Press Ctrl+C to stop the server.")
    print("=" * 60 + "\n")

    # Launch Streamlit
    try:
        subprocess.run([
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(app_path),
            "--server.headless=false",
            "--browser.gatherUsageStats=false"
        ], check=True)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down UI server...")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error launching UI: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("\n❌ Streamlit not found. Please install it:")
        print("   pip install streamlit")
        sys.exit(1)


if __name__ == "__main__":
    main()
