"""Tests for config_loader module."""

import pytest
from pathlib import Path
import yaml

from src.config.config_loader import ConfigLoader


@pytest.mark.unit
class TestConfigLoader:
    """Test cases for ConfigLoader class."""

    def test_init_no_config_file(self, temp_project_dir):
        """Test initialization without config file."""
        config_loader = ConfigLoader(temp_project_dir)

        assert config_loader.project_path == temp_project_dir
        assert config_loader.config_file == temp_project_dir / '.vibe-auditor.yml'
        assert config_loader.config is not None
        assert config_loader.config == ConfigLoader.DEFAULT_CONFIG

    def test_init_with_config_file(self, temp_project_dir):
        """Test initialization with existing config file."""
        # Create config file
        config_file = temp_project_dir / '.vibe-auditor.yml'
        config_content = """
analysis:
  mode: personal
  skip_ai: true
"""
        config_file.write_text(config_content)

        config_loader = ConfigLoader(temp_project_dir)

        assert config_loader.config['analysis']['mode'] == 'personal'
        assert config_loader.config['analysis']['skip_ai'] is True

    def test_load_config_with_invalid_yaml(self, temp_project_dir):
        """Test loading config with invalid YAML syntax."""
        config_file = temp_project_dir / '.vibe-auditor.yml'
        config_file.write_text("invalid: yaml: syntax: here:")

        # Should fall back to defaults on YAML error
        config_loader = ConfigLoader(temp_project_dir)

        assert config_loader.config == ConfigLoader.DEFAULT_CONFIG

    def test_deep_merge_simple(self, temp_project_dir):
        """Test deep merge with simple values."""
        config_loader = ConfigLoader(temp_project_dir)

        base = {'a': 1, 'b': 2}
        override = {'b': 3, 'c': 4}

        result = config_loader._deep_merge(base, override)

        assert result == {'a': 1, 'b': 3, 'c': 4}

    def test_deep_merge_nested(self, temp_project_dir):
        """Test deep merge with nested dictionaries."""
        config_loader = ConfigLoader(temp_project_dir)

        base = {
            'analysis': {
                'mode': 'deployment',
                'skip_ai': False
            },
            'output': {
                'format': 'cli'
            }
        }
        override = {
            'analysis': {
                'mode': 'personal'
            }
        }

        result = config_loader._deep_merge(base, override)

        assert result['analysis']['mode'] == 'personal'
        assert result['analysis']['skip_ai'] is False  # Preserved from base
        assert result['output']['format'] == 'cli'

    def test_get_simple_key(self, temp_project_dir):
        """Test getting configuration with simple key."""
        config_file = temp_project_dir / '.vibe-auditor.yml'
        config_file.write_text("analysis:\n  mode: personal")

        config_loader = ConfigLoader(temp_project_dir)

        mode = config_loader.get('analysis.mode')
        assert mode == 'personal'

    def test_get_nested_key(self, temp_project_dir):
        """Test getting configuration with nested key."""
        config_file = temp_project_dir / '.vibe-auditor.yml'
        config_file.write_text("tools:\n  pylint:\n    timeout: 500")

        config_loader = ConfigLoader(temp_project_dir)

        timeout = config_loader.get('tools.pylint.timeout')
        assert timeout == 500

    def test_get_missing_key_with_default(self, temp_project_dir):
        """Test getting missing key returns default value."""
        config_loader = ConfigLoader(temp_project_dir)

        value = config_loader.get('non.existent.key', 'default_value')
        assert value == 'default_value'

    def test_get_missing_key_without_default(self, temp_project_dir):
        """Test getting missing key without default returns None."""
        config_loader = ConfigLoader(temp_project_dir)

        value = config_loader.get('non.existent.key')
        assert value is None

    def test_save_template_default_path(self, temp_project_dir):
        """Test saving template to default path."""
        config_loader = ConfigLoader(temp_project_dir)

        template_path = config_loader.save_template()

        assert template_path.exists()
        assert template_path == temp_project_dir / '.vibe-auditor.yml.example'

        # Check content
        content = template_path.read_text()
        assert 'Vibe-Code Auditor Configuration File' in content
        assert 'mode: deployment' in content
        assert 'pylint:' in content

    def test_save_template_custom_path(self, temp_project_dir):
        """Test saving template to custom path."""
        config_loader = ConfigLoader(temp_project_dir)
        custom_path = temp_project_dir / 'custom-config.yml'

        template_path = config_loader.save_template(custom_path)

        assert template_path.exists()
        assert template_path == custom_path

    def test_validate_valid_config(self, temp_project_dir):
        """Test validation with valid configuration."""
        config_file = temp_project_dir / '.vibe-auditor.yml'
        config_file.write_text("""
analysis:
  mode: deployment
output:
  format: json
tools:
  pylint:
    timeout: 300
""")

        config_loader = ConfigLoader(temp_project_dir)

        # Should not raise exception
        assert config_loader.validate() is True

    def test_validate_invalid_mode(self, temp_project_dir):
        """Test validation with invalid mode."""
        config_file = temp_project_dir / '.vibe-auditor.yml'
        config_file.write_text("analysis:\n  mode: invalid_mode")

        config_loader = ConfigLoader(temp_project_dir)

        with pytest.raises(ValueError, match="Invalid analysis mode"):
            config_loader.validate()

    def test_validate_invalid_output_format(self, temp_project_dir):
        """Test validation with invalid output format."""
        config_file = temp_project_dir / '.vibe-auditor.yml'
        config_file.write_text("output:\n  format: xml")

        config_loader = ConfigLoader(temp_project_dir)

        with pytest.raises(ValueError, match="Invalid output format"):
            config_loader.validate()

    def test_validate_invalid_timeout(self, temp_project_dir):
        """Test validation with invalid timeout."""
        config_file = temp_project_dir / '.vibe-auditor.yml'
        config_file.write_text("tools:\n  pylint:\n    timeout: -100")

        config_loader = ConfigLoader(temp_project_dir)

        with pytest.raises(ValueError, match="Invalid timeout"):
            config_loader.validate()

    def test_validate_non_integer_timeout(self, temp_project_dir):
        """Test validation with non-integer timeout."""
        config_file = temp_project_dir / '.vibe-auditor.yml'
        config_file.write_text("tools:\n  semgrep:\n    timeout: 'not_a_number'")

        config_loader = ConfigLoader(temp_project_dir)

        with pytest.raises(ValueError, match="Invalid timeout"):
            config_loader.validate()

    def test_to_dict(self, temp_project_dir):
        """Test converting config to dictionary."""
        config_file = temp_project_dir / '.vibe-auditor.yml'
        config_file.write_text("analysis:\n  mode: personal")

        config_loader = ConfigLoader(temp_project_dir)

        config_dict = config_loader.to_dict()

        assert isinstance(config_dict, dict)
        assert config_dict['analysis']['mode'] == 'personal'

    def test_empty_config_file(self, temp_project_dir):
        """Test loading empty config file."""
        config_file = temp_project_dir / '.vibe-auditor.yml'
        config_file.write_text("")

        config_loader = ConfigLoader(temp_project_dir)

        # Should use defaults
        assert config_loader.config == ConfigLoader.DEFAULT_CONFIG

    def test_config_merge_preserves_defaults(self, temp_project_dir):
        """Test that partial config merges with defaults."""
        config_file = temp_project_dir / '.vibe-auditor.yml'
        config_file.write_text("""
analysis:
  mode: personal
""")

        config_loader = ConfigLoader(temp_project_dir)

        # Custom value
        assert config_loader.get('analysis.mode') == 'personal'

        # Default values preserved
        assert config_loader.get('analysis.skip_ai') is False
        assert config_loader.get('tools.pylint.enabled') is True
        assert config_loader.get('output.format') == 'cli'

    def test_load_config_exception_handling(self, temp_project_dir):
        """Test exception handling during config load."""
        config_file = temp_project_dir / '.vibe-auditor.yml'

        # Create a file that will cause read errors (e.g., directory with same name)
        config_file.mkdir()

        config_loader = ConfigLoader(temp_project_dir)

        # Should fall back to defaults
        assert config_loader.config == ConfigLoader.DEFAULT_CONFIG

    def test_exclude_patterns_in_default_config(self, temp_project_dir):
        """Test that exclude patterns are present in default config."""
        config_loader = ConfigLoader(temp_project_dir)

        exclude_dirs = config_loader.get('exclude.dirs')
        exclude_files = config_loader.get('exclude.files')

        assert 'node_modules' in exclude_dirs
        assert 'venv' in exclude_dirs
        assert '*.min.js' in exclude_files
