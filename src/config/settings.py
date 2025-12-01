"""Configuration settings for Vibe-Code Auditor."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = "claude-opus-4-5-20251101"

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
