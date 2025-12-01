"""Configuration file loader for Vibe-Code Auditor."""

from pathlib import Path
from typing import Dict, Any, Optional
import yaml

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ConfigLoader:
    """Loads and validates configuration from .vibe-auditor.yml file."""

    DEFAULT_CONFIG = {
        'analysis': {
            'mode': 'deployment',
            'skip_ai': False,
            'languages': [],  # Auto-detect if empty
        },
        'tools': {
            'pylint': {
                'enabled': True,
                'timeout': 300,
            },
            'semgrep': {
                'enabled': True,
                'timeout': 300,
            },
            'jscpd': {
                'enabled': True,
                'timeout': 180,
            },
            'eslint': {
                'enabled': True,
            },
        },
        'output': {
            'format': 'cli',  # cli, json, html
            'path': None,
            'verbose': False,
            'quiet': False,
        },
        'exclude': {
            'dirs': [
                'node_modules',
                'venv',
                'env',
                '.venv',
                '__pycache__',
                '.git',
                'dist',
                'build',
                '.idea',
                '.vscode',
            ],
            'files': [
                '*.min.js',
                '*.bundle.js',
                '*.pyc',
            ],
        },
    }

    def __init__(self, project_path: Path):
        """
        Initialize config loader.

        Args:
            project_path: Path to the project to analyze
        """
        self.project_path = project_path
        self.config_file = project_path / '.vibe-auditor.yml'
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file or use defaults.

        Returns:
            Configuration dictionary
        """
        if self.config_file.exists():
            logger.info(f"Loading configuration from {self.config_file}")
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f) or {}

                # Merge with defaults
                config = self._deep_merge(self.DEFAULT_CONFIG.copy(), user_config)
                logger.info("Configuration loaded successfully")
                return config

            except yaml.YAMLError as e:
                logger.error(f"Failed to parse YAML config: {e}", exc_info=True)
                logger.warning("Using default configuration")
                return self.DEFAULT_CONFIG.copy()
            except Exception as e:
                logger.error(f"Failed to load config: {e}", exc_info=True)
                logger.warning("Using default configuration")
                return self.DEFAULT_CONFIG.copy()
        else:
            logger.debug(f"No config file found at {self.config_file}, using defaults")
            return self.DEFAULT_CONFIG.copy()

    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """
        Deep merge two dictionaries.

        Args:
            base: Base dictionary
            override: Dictionary to merge into base

        Returns:
            Merged dictionary
        """
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-separated key.

        Args:
            key: Dot-separated key (e.g., 'analysis.mode')
            default: Default value if key not found

        Returns:
            Configuration value

        Example:
            >>> config.get('analysis.mode')
            'deployment'
            >>> config.get('tools.pylint.timeout')
            300
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def save_template(self, output_path: Optional[Path] = None) -> Path:
        """
        Save configuration template file.

        Args:
            output_path: Path to save template (default: .vibe-auditor.yml.example)

        Returns:
            Path to saved template file
        """
        if output_path is None:
            output_path = self.project_path / '.vibe-auditor.yml.example'

        logger.info(f"Saving configuration template to {output_path}")

        template_content = """# Vibe-Code Auditor Configuration File
# Place this file as .vibe-auditor.yml in your project root

# Analysis settings
analysis:
  mode: deployment  # deployment or personal
  skip_ai: false    # Skip AI analysis (static only)
  languages: []     # Auto-detect if empty, or specify: [python, javascript, typescript]

# Tool configuration
tools:
  pylint:
    enabled: true
    timeout: 300  # seconds

  semgrep:
    enabled: true
    timeout: 300

  jscpd:
    enabled: true
    timeout: 180

  eslint:
    enabled: true

# Output settings
output:
  format: cli       # cli, json, or html
  path: null        # Output file path (e.g., report.json)
  verbose: false    # Enable verbose logging
  quiet: false      # Enable quiet mode (errors only)

# Exclude patterns
exclude:
  dirs:
    - node_modules
    - venv
    - env
    - .venv
    - __pycache__
    - .git
    - dist
    - build
    - .idea
    - .vscode
  files:
    - "*.min.js"
    - "*.bundle.js"
    - "*.pyc"
"""

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(template_content)

            logger.info(f"Configuration template saved to {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to save template: {e}", exc_info=True)
            raise

    def validate(self) -> bool:
        """
        Validate configuration.

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        # Validate mode
        mode = self.get('analysis.mode')
        if mode not in ['deployment', 'personal']:
            raise ValueError(f"Invalid analysis mode: {mode}. Must be 'deployment' or 'personal'")

        # Validate output format
        output_format = self.get('output.format')
        if output_format not in ['cli', 'json', 'html']:
            raise ValueError(f"Invalid output format: {output_format}. Must be 'cli', 'json', or 'html'")

        # Validate timeouts
        for tool in ['pylint', 'semgrep', 'jscpd']:
            timeout = self.get(f'tools.{tool}.timeout')
            if timeout is not None and (not isinstance(timeout, int) or timeout <= 0):
                raise ValueError(f"Invalid timeout for {tool}: {timeout}. Must be a positive integer")

        logger.debug("Configuration validation passed")
        return True

    def to_dict(self) -> Dict[str, Any]:
        """
        Get configuration as dictionary.

        Returns:
            Configuration dictionary
        """
        return self.config.copy()
