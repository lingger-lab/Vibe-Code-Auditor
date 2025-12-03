"""Configuration settings for Vibe-Code Auditor."""

import os
from pathlib import Path
from typing import Optional, Tuple

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
# 환경 변수에서 읽은 값을 공백 제거 후 문자열로 정규화
ANTHROPIC_API_KEY: str = (os.getenv("ANTHROPIC_API_KEY") or "").strip()
CLAUDE_MODEL = "claude-opus-4-5-20251101"


def validate_api_key() -> Tuple[bool, Optional[str]]:
    """
    ANTHROPIC_API_KEY 환경 변수의 존재 여부와 형식을 검증합니다.

    Returns:
        (is_valid, error_message)
    """
    if not ANTHROPIC_API_KEY:
        return False, (
            "ANTHROPIC_API_KEY 환경 변수가 설정되지 않았습니다. "
            ".env 파일을 확인하거나 --skip-ai 옵션을 사용하세요."
        )

    # 기본 형식 검증: 접두어와 최소 길이
    if not ANTHROPIC_API_KEY.startswith(("sk-ant-", "sk-")):
        return False, (
            "ANTHROPIC_API_KEY 값 형식이 올바르지 않습니다. "
            "'sk-' 또는 'sk-ant-'로 시작하는 유효한 키인지 확인하세요."
        )

    if len(ANTHROPIC_API_KEY) < 20:
        return False, "ANTHROPIC_API_KEY 값 길이가 너무 짧습니다. 전체 키를 정확히 입력해주세요."

    return True, None

# Analysis Modes
ANALYSIS_MODES = {
    "deployment": {
        "name": "배포 관점",
        "priorities": ["security", "performance", "scalability", "ci_cd"],
        "description": "보안, 성능, 확장성, CI/CD 검증 우선"
    },
    "personal": {
        "name": "자가 사용 관점",
        "priorities": ["readability", "maintainability", "duplication"],
        "description": "가독성, 유지보수성, 코드 중복 제거 우선"
    }
}

# File and Directory Settings
DEFAULT_EXCLUDE_PATTERNS = [
    "node_modules",
    "venv",
    ".venv",
    "env",
    ".git",
    "__pycache__",
    "*.pyc",
    ".pytest_cache",
    "build",
    "dist",
    "*.egg-info"
]

MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))

# Language Detection Patterns
LANGUAGE_PATTERNS = {
    "python": {
        "extensions": [".py"],
        "files": ["requirements.txt", "setup.py", "pyproject.toml"],
        "analyzer": "pylint"
    },
    "javascript": {
        "extensions": [".js", ".jsx"],
        "files": ["package.json"],
        "analyzer": "eslint"
    },
    "typescript": {
        "extensions": [".ts", ".tsx"],
        "files": ["tsconfig.json"],
        "analyzer": "eslint"
    },
    "go": {
        "extensions": [".go"],
        "files": ["go.mod", "go.sum"],
        "analyzer": "staticcheck"
    },
    "rust": {
        "extensions": [".rs"],
        "files": ["Cargo.toml", "Cargo.lock"],
        "analyzer": "clippy"
    },
    "java": {
        "extensions": [".java"],
        "files": ["pom.xml", "build.gradle", "build.gradle.kts"],
        "analyzer": "spotbugs"
    },
    "php": {
        "extensions": [".php"],
        "files": ["composer.json"],
        "analyzer": "phpstan"
    },
    "csharp": {
        "extensions": [".cs"],
        "files": [".csproj", ".sln"],
        "analyzer": "roslyn"
    },
    "ruby": {
        "extensions": [".rb"],
        "files": ["Gemfile"],
        "analyzer": "rubocop"
    },
    "kotlin": {
        "extensions": [".kt", ".kts"],
        "files": ["build.gradle.kts"],
        "analyzer": "ktlint"
    },
    "swift": {
        "extensions": [".swift"],
        "files": ["Package.swift"],
        "analyzer": "swiftlint"
    }
}

# Analysis Tools
STATIC_ANALYSIS_TOOLS = {
    "pylint": {
        "command": "pylint",
        "languages": ["python"],
        "install_hint": "pip install pylint==3.3.2",
        "output_format": "json"
    },
    "eslint": {
        "command": "eslint",
        "languages": ["javascript", "typescript"],
        "install_hint": "npm install -g eslint",
        "output_format": "json"
    },
    "semgrep": {
        "command": "semgrep",
        "languages": ["all"],
        "install_hint": "pip install semgrep==1.100.0",
        "output_format": "json"
    },
    "jscpd": {
        "command": "jscpd",
        "languages": ["all"],
        "install_hint": "npm install -g jscpd",
        "output_format": "json"
    },
    "staticcheck": {
        "command": "staticcheck",
        "languages": ["go"],
        "install_hint": "go install honnef.co/go/tools/cmd/staticcheck@latest",
        "output_format": "json"
    },
    "golangci-lint": {
        "command": "golangci-lint",
        "languages": ["go"],
        "install_hint": "curl -sSfL https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh | sh -s -- -b $(go env GOPATH)/bin",
        "output_format": "json"
    },
    "clippy": {
        "command": "cargo",
        "languages": ["rust"],
        "install_hint": "rustup component add clippy",
        "output_format": "json",
        "subcommand": "clippy"
    },
    "cargo-audit": {
        "command": "cargo",
        "languages": ["rust"],
        "install_hint": "cargo install cargo-audit",
        "output_format": "json",
        "subcommand": "audit"
    },
    "spotbugs": {
        "command": "spotbugs",
        "languages": ["java"],
        "install_hint": "Download from https://spotbugs.github.io/",
        "output_format": "xml"
    },
    "pmd": {
        "command": "pmd",
        "languages": ["java"],
        "install_hint": "Download from https://pmd.github.io/",
        "output_format": "json"
    },
    "phpstan": {
        "command": "phpstan",
        "languages": ["php"],
        "install_hint": "composer require --dev phpstan/phpstan",
        "output_format": "json"
    },
    "psalm": {
        "command": "psalm",
        "languages": ["php"],
        "install_hint": "composer require --dev vimeo/psalm",
        "output_format": "json"
    },
    "roslyn": {
        "command": "dotnet",
        "languages": ["csharp"],
        "install_hint": "Built-in with .NET SDK",
        "output_format": "json",
        "subcommand": "build"
    },
    "rubocop": {
        "command": "rubocop",
        "languages": ["ruby"],
        "install_hint": "gem install rubocop",
        "output_format": "json"
    },
    "ktlint": {
        "command": "ktlint",
        "languages": ["kotlin"],
        "install_hint": "brew install ktlint or download from https://ktlint.github.io/",
        "output_format": "json"
    },
    "swiftlint": {
        "command": "swiftlint",
        "languages": ["swift"],
        "install_hint": "brew install swiftlint",
        "output_format": "json"
    }
}

# Issue Severity Levels
SEVERITY_LEVELS = {
    "critical": {
        "emoji": "🔴",
        "color": "red",
        "weight": 100
    },
    "warning": {
        "emoji": "🟡",
        "color": "yellow",
        "weight": 50
    },
    "info": {
        "emoji": "🟢",
        "color": "green",
        "weight": 10
    }
}
