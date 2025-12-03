"""Static code analysis module using various linting and security tools."""

import subprocess
import json
from pathlib import Path
from typing import List, Dict, Any
import shutil

from src.config.settings import STATIC_ANALYSIS_TOOLS
from src.utils.logger import setup_logger
from src.utils.cache_manager import CacheManager

# Module logger
logger = setup_logger(__name__)


class StaticAnalyzer:
    """Runs static analysis tools based on detected languages."""

    def __init__(self, project_path: Path, languages: List[str], mode: str, use_cache: bool = True):
        """
        Initialize the static analyzer.

        Args:
            project_path: Path to the project directory
            languages: List of detected programming languages
            mode: Analysis mode ('deployment' or 'personal')
            use_cache: Whether to use result caching
        """
        self.project_path = project_path
        self.languages = languages
        self.mode = mode
        self.use_cache = use_cache
        self.cache_manager = CacheManager(project_path) if use_cache else None
        self.results = {
            'pylint': [],
            'eslint': [],
            'semgrep': [],
            'jscpd': []
        }

    def _check_tool_installed(self, tool_name: str) -> bool:
        """
        Check if a tool is installed and available.

        Args:
            tool_name: Name of the tool to check

        Returns:
            True if tool is installed, False otherwise
        """
        tool_config = STATIC_ANALYSIS_TOOLS.get(tool_name)
        if not tool_config:
            return False

        command = tool_config['command']
        return shutil.which(command) is not None

    def _run_pylint(self) -> List[Dict[str, Any]]:
        """
        Run Pylint analysis on Python files.

        Returns:
            List of issues found by Pylint
        """
        if 'python' not in self.languages:
            return []

        if not self._check_tool_installed('pylint'):
            return [{
                'tool': 'pylint',
                'severity': 'warning',
                'message': 'Pylint is not installed',
                'suggestion': STATIC_ANALYSIS_TOOLS['pylint']['install_hint']
            }]

        try:
            logger.info("Running Pylint on %s", self.project_path)

            # Run pylint with JSON output and improved error handling
            result = subprocess.run(
                ['pylint', str(self.project_path), '--output-format=json', '--recursive=y'],
                capture_output=True,
                text=True,
                timeout=300,  # Increased timeout to 5 minutes
                check=False  # Don't raise on non-zero exit code
            )

            if result.stdout:
                try:
                    pylint_output = json.loads(result.stdout)
                    issues = []

                    for item in pylint_output:
                        severity = self._map_pylint_severity(item.get('type', 'info'))
                        issues.append({
                            'tool': 'pylint',
                            'file': item.get('path', 'unknown'),
                            'line': item.get('line', 0),
                            'severity': severity,
                            'message': item.get('message', ''),
                            'symbol': item.get('symbol', ''),
                            'message_id': item.get('message-id', '')
                        })

                    logger.info("Pylint found %d issues", len(issues))
                    return issues

                except json.JSONDecodeError as e:
                    logger.error("Failed to parse Pylint JSON output: %s", e)
                    return [{
                        'tool': 'pylint',
                        'severity': 'warning',
                        'message': 'Pylint output parsing failed'
                    }]

        except subprocess.TimeoutExpired:
            logger.warning("Pylint timed out after 300 seconds for %s", self.project_path)
            return [{
                'tool': 'pylint',
                'severity': 'warning',
                'message': 'Pylint analysis timed out (>5 minutes)',
                'suggestion': 'Try analyzing a smaller directory or use --skip-ai flag'
            }]
        except FileNotFoundError:
            logger.error("Pylint executable not found in PATH")
            return [{
                'tool': 'pylint',
                'severity': 'warning',
                'message': 'Pylint is not installed or not in PATH',
                'suggestion': STATIC_ANALYSIS_TOOLS['pylint']['install_hint']
            }]
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Pylint analysis failed with unexpected error: %s", e, exc_info=True)
            return [{
                'tool': 'pylint',
                'severity': 'warning',
                'message': f'Pylint analysis failed: {str(e)}'
            }]

        return []

    def _run_semgrep(self) -> List[Dict[str, Any]]:
        """
        Run Semgrep security analysis.

        Returns:
            List of security issues found by Semgrep
        """
        if not self._check_tool_installed('semgrep'):
            return [{
                'tool': 'semgrep',
                'severity': 'warning',
                'message': 'Semgrep is not installed',
                'suggestion': STATIC_ANALYSIS_TOOLS['semgrep']['install_hint']
            }]

        try:
            logger.info("Running Semgrep security scan on %s", self.project_path)

            # Run semgrep with auto config and improved error handling
            result = subprocess.run(
                ['semgrep', 'scan', '--config=auto', '--json', str(self.project_path)],
                capture_output=True,
                text=True,
                timeout=300,  # Increased timeout for large projects
                check=False
            )

            if result.stdout:
                try:
                    semgrep_output = json.loads(result.stdout)
                    issues = []

                    for finding in semgrep_output.get('results', []):
                        issues.append({
                            'tool': 'semgrep',
                            'file': finding.get('path', 'unknown'),
                            'line': finding.get('start', {}).get('line', 0),
                            'severity': self._map_semgrep_severity(finding.get('extra', {}).get('severity', 'INFO')),
                            'message': finding.get('extra', {}).get('message', ''),
                            'rule_id': finding.get('check_id', '')
                        })

                    logger.info("Semgrep found %d security issues", len(issues))
                    return issues

                except json.JSONDecodeError as e:
                    logger.error("Failed to parse Semgrep JSON output: %s", e)
                    return [{
                        'tool': 'semgrep',
                        'severity': 'warning',
                        'message': 'Semgrep output parsing failed'
                    }]

        except subprocess.TimeoutExpired:
            logger.warning("Semgrep timed out after 300 seconds for %s", self.project_path)
            return [{
                'tool': 'semgrep',
                'severity': 'warning',
                'message': 'Semgrep analysis timed out (>5 minutes)',
                'suggestion': 'Try analyzing a smaller directory'
            }]
        except FileNotFoundError:
            logger.error("Semgrep executable not found in PATH")
            return [{
                'tool': 'semgrep',
                'severity': 'info',
                'message': 'Semgrep is not installed (not available on Windows natively)',
                'suggestion': STATIC_ANALYSIS_TOOLS['semgrep']['install_hint']
            }]
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Semgrep analysis failed with unexpected error: %s", e, exc_info=True)
            return [{
                'tool': 'semgrep',
                'severity': 'warning',
                'message': f'Semgrep analysis failed: {str(e)}'
            }]

        return []

    def _run_jscpd(self) -> List[Dict[str, Any]]:
        """
        Run jscpd for code duplication detection.

        Returns:
            List of code duplication issues
        """
        if not self._check_tool_installed('jscpd'):
            return [{
                'tool': 'jscpd',
                'severity': 'info',
                'message': 'jscpd is not installed',
                'suggestion': STATIC_ANALYSIS_TOOLS['jscpd']['install_hint']
            }]

        try:
            logger.info("Running jscpd code duplication detection on %s", self.project_path)

            # Run jscpd with JSON output and improved error handling
            result = subprocess.run(
                ['jscpd', str(self.project_path), '--format', 'json', '--silent'],
                capture_output=True,
                text=True,
                timeout=180,
                check=False
            )

            if result.stdout:
                try:
                    jscpd_output = json.loads(result.stdout)
                    duplicates = jscpd_output.get('duplicates', [])

                    if duplicates:
                        issues = [{
                            'tool': 'jscpd',
                            'severity': 'warning',
                            'message': f'Found {len(duplicates)} code duplication(s)',
                            'duplicates_count': len(duplicates),
                            'statistics': jscpd_output.get('statistics', {})
                        }]
                        logger.info("jscpd found %d code duplications", len(duplicates))
                        return issues
                    else:
                        logger.info("jscpd found no code duplications")

                except json.JSONDecodeError:
                    # jscpd might not output valid JSON if no duplicates found
                    logger.debug("jscpd did not return valid JSON (possibly no duplicates)")
                    pass

        except subprocess.TimeoutExpired:
            logger.warning("jscpd timed out after 180 seconds for %s", self.project_path)
            return [{
                'tool': 'jscpd',
                'severity': 'info',
                'message': 'jscpd analysis timed out',
                'suggestion': 'Try analyzing a smaller directory'
            }]
        except FileNotFoundError:
            logger.error("jscpd executable not found in PATH")
            return [{
                'tool': 'jscpd',
                'severity': 'info',
                'message': 'jscpd is not installed',
                'suggestion': STATIC_ANALYSIS_TOOLS['jscpd']['install_hint']
            }]
        except Exception as e:  # pylint: disable=broad-except
            logger.error("jscpd analysis failed with unexpected error: %s", e, exc_info=True)
            return [{
                'tool': 'jscpd',
                'severity': 'info',
                'message': f'jscpd analysis failed: {str(e)}'
            }]

        return []

    def _run_staticcheck(self) -> List[Dict[str, Any]]:
        """
        Run staticcheck for Go code analysis.

        Returns:
            List of issues found by staticcheck
        """
        if not self._check_tool_installed('staticcheck'):
            return [{
                'tool': 'staticcheck',
                'severity': 'info',
                'message': 'staticcheck is not installed',
                'suggestion': STATIC_ANALYSIS_TOOLS['staticcheck']['install_hint']
            }]

        try:
            logger.info("Running staticcheck on Go code in %s", self.project_path)

            result = subprocess.run(
                ['staticcheck', '-f', 'json', './...'],
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=300,
                check=False
            )

            if result.stdout:
                try:
                    issues = []
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            item = json.loads(line)
                            issues.append({
                                'tool': 'staticcheck',
                                'file': item.get('location', {}).get('file', 'unknown'),
                                'line': item.get('location', {}).get('line', 0),
                                'severity': 'warning',
                                'message': item.get('message', ''),
                                'code': item.get('code', '')
                            })

                    logger.info("staticcheck found %d issues", len(issues))
                    return issues

                except json.JSONDecodeError:
                    return []

        except subprocess.TimeoutExpired:
            logger.warning("staticcheck timed out")
            return [{'tool': 'staticcheck', 'severity': 'warning', 'message': 'Analysis timed out'}]
        except FileNotFoundError:
            return [{'tool': 'staticcheck', 'severity': 'info', 'message': 'staticcheck not found'}]
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("staticcheck failed: %s", e)
            return [{'tool': 'staticcheck', 'severity': 'warning', 'message': f'Analysis failed: {str(e)}'}]

        return []

    def _run_clippy(self) -> List[Dict[str, Any]]:
        """
        Run Cargo clippy for Rust code analysis.

        Returns:
            List of issues found by clippy
        """
        if not self._check_tool_installed('cargo'):
            return [{
                'tool': 'clippy',
                'severity': 'info',
                'message': 'Cargo/Rust is not installed',
                'suggestion': STATIC_ANALYSIS_TOOLS['clippy']['install_hint']
            }]

        try:
            logger.info("Running cargo clippy on Rust code in %s", self.project_path)

            result = subprocess.run(
                ['cargo', 'clippy', '--message-format=json', '--', '-D', 'warnings'],
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=300,
                check=False
            )

            if result.stdout:
                try:
                    issues = []
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            try:
                                item = json.loads(line)
                                if item.get('reason') == 'compiler-message':
                                    message = item.get('message', {})
                                    spans = message.get('spans', [])
                                    if spans:
                                        span = spans[0]
                                        severity = 'warning' if message.get('level') == 'warning' else 'info'
                                        issues.append({
                                            'tool': 'clippy',
                                            'file': span.get('file_name', 'unknown'),
                                            'line': span.get('line_start', 0),
                                            'severity': severity,
                                            'message': message.get('message', ''),
                                            'code': message.get('code', {}).get('code', '')
                                        })
                            except json.JSONDecodeError:
                                continue

                    logger.info("clippy found %d issues", len(issues))
                    return issues

                except (ValueError, KeyError, IndexError):  # JSON 파싱 오류 등
                    return []

        except subprocess.TimeoutExpired:
            logger.warning("clippy timed out")
            return [{'tool': 'clippy', 'severity': 'warning', 'message': 'Analysis timed out'}]
        except FileNotFoundError:
            return [{'tool': 'clippy', 'severity': 'info', 'message': 'cargo/clippy not found'}]
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("clippy failed: %s", e)
            return [{'tool': 'clippy', 'severity': 'warning', 'message': f'Analysis failed: {str(e)}'}]

        return []

    def _run_phpstan(self) -> List[Dict[str, Any]]:
        """
        Run PHPStan for PHP code analysis.

        Returns:
            List of issues found by PHPStan
        """
        if not self._check_tool_installed('phpstan'):
            return [{
                'tool': 'phpstan',
                'severity': 'info',
                'message': 'PHPStan is not installed',
                'suggestion': STATIC_ANALYSIS_TOOLS['phpstan']['install_hint']
            }]

        try:
            logger.info("Running PHPStan on PHP code in %s", self.project_path)

            result = subprocess.run(
                ['phpstan', 'analyse', '--error-format=json', '.'],
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=300,
                check=False
            )

            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    issues = []

                    for file, file_errors in data.get('files', {}).items():
                        for error in file_errors.get('messages', []):
                            issues.append({
                                'tool': 'phpstan',
                                'file': file,
                                'line': error.get('line', 0),
                                'severity': 'warning',
                                'message': error.get('message', '')
                            })

                    logger.info("PHPStan found %d issues", len(issues))
                    return issues

                except json.JSONDecodeError:
                    return []

        except subprocess.TimeoutExpired:
            logger.warning("PHPStan timed out")
            return [{'tool': 'phpstan', 'severity': 'warning', 'message': 'Analysis timed out'}]
        except FileNotFoundError:
            return [{'tool': 'phpstan', 'severity': 'info', 'message': 'PHPStan not found'}]
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("PHPStan failed: %s", e)
            return [{'tool': 'phpstan', 'severity': 'warning', 'message': f'Analysis failed: {str(e)}'}]

        return []

    def _run_rubocop(self) -> List[Dict[str, Any]]:
        """
        Run RuboCop for Ruby code analysis.

        Returns:
            List of issues found by RuboCop
        """
        if not self._check_tool_installed('rubocop'):
            return [{
                'tool': 'rubocop',
                'severity': 'info',
                'message': 'RuboCop is not installed',
                'suggestion': STATIC_ANALYSIS_TOOLS['rubocop']['install_hint']
            }]

        try:
            logger.info("Running RuboCop on Ruby code in %s", self.project_path)

            result = subprocess.run(
                ['rubocop', '--format', 'json', '.'],
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=300,
                check=False
            )

            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    issues = []

                    for file_data in data.get('files', []):
                        for offense in file_data.get('offenses', []):
                            severity = 'warning' if offense.get('severity') in ['error', 'warning'] else 'info'
                            issues.append({
                                'tool': 'rubocop',
                                'file': file_data.get('path', 'unknown'),
                                'line': offense.get('location', {}).get('line', 0),
                                'severity': severity,
                                'message': offense.get('message', ''),
                                'cop_name': offense.get('cop_name', '')
                            })

                    logger.info("RuboCop found %d issues", len(issues))
                    return issues

                except json.JSONDecodeError:
                    return []

        except subprocess.TimeoutExpired:
            logger.warning("RuboCop timed out")
            return [{'tool': 'rubocop', 'severity': 'warning', 'message': 'Analysis timed out'}]
        except FileNotFoundError:
            return [{'tool': 'rubocop', 'severity': 'info', 'message': 'RuboCop not found'}]
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("RuboCop failed: %s", e)
            return [{'tool': 'rubocop', 'severity': 'warning', 'message': f'Analysis failed: {str(e)}'}]

        return []

    def _run_ktlint(self) -> List[Dict[str, Any]]:
        """
        Run ktlint for Kotlin code analysis.

        Returns:
            List of issues found by ktlint
        """
        if not self._check_tool_installed('ktlint'):
            return [{
                'tool': 'ktlint',
                'severity': 'info',
                'message': 'ktlint is not installed',
                'suggestion': STATIC_ANALYSIS_TOOLS['ktlint']['install_hint']
            }]

        try:
            logger.info("Running ktlint on Kotlin code in %s", self.project_path)

            result = subprocess.run(
                ['ktlint', '--reporter=json', '**/*.kt'],
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=300,
                check=False
            )

            if result.stdout:
                try:
                    # ktlint JSON format is array of objects
                    data = json.loads(result.stdout)
                    issues = []

                    for item in data:
                        issues.append({
                            'tool': 'ktlint',
                            'file': item.get('file', 'unknown'),
                            'line': item.get('line', 0),
                            'column': item.get('column', 0),
                            'severity': 'warning',
                            'message': item.get('message', ''),
                            'rule': item.get('rule', '')
                        })

                    logger.info("ktlint found %d issues", len(issues))
                    return issues

                except json.JSONDecodeError:
                    return []

        except subprocess.TimeoutExpired:
            logger.warning("ktlint timed out")
            return [{'tool': 'ktlint', 'severity': 'warning', 'message': 'Analysis timed out'}]
        except FileNotFoundError:
            return [{'tool': 'ktlint', 'severity': 'info', 'message': 'ktlint not found'}]
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("ktlint failed: %s", e)
            return [{'tool': 'ktlint', 'severity': 'warning', 'message': f'Analysis failed: {str(e)}'}]

        return []

    def _run_swiftlint(self) -> List[Dict[str, Any]]:
        """
        Run SwiftLint for Swift code analysis.

        Returns:
            List of issues found by SwiftLint
        """
        if not self._check_tool_installed('swiftlint'):
            return [{
                'tool': 'swiftlint',
                'severity': 'info',
                'message': 'SwiftLint is not installed',
                'suggestion': STATIC_ANALYSIS_TOOLS['swiftlint']['install_hint']
            }]

        try:
            logger.info("Running SwiftLint on Swift code in %s", self.project_path)

            result = subprocess.run(
                ['swiftlint', 'lint', '--reporter', 'json'],
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=300,
                check=False
            )

            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    issues = []

                    for item in data:
                        severity_map = {'error': 'critical', 'warning': 'warning'}
                        severity = severity_map.get(item.get('severity', 'warning').lower(), 'warning')

                        issues.append({
                            'tool': 'swiftlint',
                            'file': item.get('file', 'unknown'),
                            'line': item.get('line', 0),
                            'column': item.get('character', 0),
                            'severity': severity,
                            'message': item.get('reason', ''),
                            'rule_id': item.get('rule_id', '')
                        })

                    logger.info("SwiftLint found %d issues", len(issues))
                    return issues

                except json.JSONDecodeError:
                    return []

        except subprocess.TimeoutExpired:
            logger.warning("SwiftLint timed out")
            return [{'tool': 'swiftlint', 'severity': 'warning', 'message': 'Analysis timed out'}]
        except FileNotFoundError:
            return [{'tool': 'swiftlint', 'severity': 'info', 'message': 'SwiftLint not found'}]
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("SwiftLint failed: %s", e)
            return [{'tool': 'swiftlint', 'severity': 'warning', 'message': f'Analysis failed: {str(e)}'}]

        return []

    def _run_dotnet_build(self) -> List[Dict[str, Any]]:
        """
        Run dotnet build for C# code analysis (using Roslyn analyzers).

        Returns:
            List of issues found by Roslyn analyzers
        """
        if not self._check_tool_installed('dotnet'):
            return [{
                'tool': 'roslyn',
                'severity': 'info',
                'message': '.NET SDK is not installed',
                'suggestion': STATIC_ANALYSIS_TOOLS['roslyn']['install_hint']
            }]

        try:
            logger.info("Running dotnet build on C# code in %s", self.project_path)

            # First, try to find .csproj or .sln files
            csproj_files = list(self.project_path.rglob('*.csproj'))
            sln_files = list(self.project_path.rglob('*.sln'))

            if not csproj_files and not sln_files:
                return [{
                    'tool': 'roslyn',
                    'severity': 'info',
                    'message': 'No .csproj or .sln files found'
                }]

            # Run dotnet build with diagnostic output
            target = str(sln_files[0]) if sln_files else str(csproj_files[0])

            result = subprocess.run(
                ['dotnet', 'build', target, '/p:TreatWarningsAsErrors=false'],
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=300,
                check=False
            )

            issues = []
            # Parse build output for warnings and errors
            for line in result.stdout.split('\n') + result.stderr.split('\n'):
                # Look for standard MSBuild diagnostic format
                # Example: Program.cs(10,5): warning CS0219: The variable 'x' is assigned but its value is never used
                if ': warning ' in line or ': error ' in line:
                    parts = line.split(': ')
                    if len(parts) >= 3:
                        location = parts[0].strip()
                        severity_type = parts[1].strip()
                        message = ': '.join(parts[2:]).strip()

                        # Extract file and line number
                        file_path = 'unknown'
                        line_num = 0
                        if '(' in location:
                            file_path = location.split('(')[0]
                            try:
                                line_num = int(location.split('(')[1].split(',')[0])
                            except ValueError:
                                # 줄 번호 파싱 실패 시 0으로 유지
                                line_num = 0

                        severity = 'critical' if 'error' in severity_type else 'warning'
                        issues.append({
                            'tool': 'roslyn',
                            'file': file_path,
                            'line': line_num,
                            'severity': severity,
                            'message': message
                        })

            logger.info("Roslyn analyzers found %d issues", len(issues))
            return issues

        except subprocess.TimeoutExpired:
            logger.warning("dotnet build timed out")
            return [{'tool': 'roslyn', 'severity': 'warning', 'message': 'Analysis timed out'}]
        except FileNotFoundError:
            return [{'tool': 'roslyn', 'severity': 'info', 'message': '.NET SDK not found'}]
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("dotnet build failed: %s", e)
            return [{'tool': 'roslyn', 'severity': 'warning', 'message': f'Analysis failed: {str(e)}'}]

        return []

    def _map_pylint_severity(self, pylint_type: str) -> str:
        """Map Pylint message type to our severity levels."""
        severity_map = {
            'error': 'critical',
            'fatal': 'critical',
            'warning': 'warning',
            'refactor': 'info',
            'convention': 'info',
            'info': 'info'
        }
        return severity_map.get(pylint_type.lower(), 'info')

    def _map_semgrep_severity(self, semgrep_severity: str) -> str:
        """Map Semgrep severity to our severity levels."""
        severity_map = {
            'ERROR': 'critical',
            'WARNING': 'warning',
            'INFO': 'info'
        }
        return severity_map.get(semgrep_severity.upper(), 'info')

    def analyze(self) -> Dict[str, Any]:
        """
        Run all applicable static analysis tools (with caching support).

        Returns:
            Dictionary containing analysis results from all tools
        """
        # Check cache first
        cache_key = f"static_analysis_{self.mode}"

        if self.use_cache and self.cache_manager:
            # Collect all code files for cache validation
            project_files = list(self.project_path.rglob('*'))
            project_files = [f for f in project_files if f.is_file()]

            cached_result = self.cache_manager.get_cached_result(cache_key, project_files)
            if cached_result:
                logger.info("Using cached static analysis results")
                return cached_result

        logger.info("Running static analysis (no cache)")

        results = {
            'mode': self.mode,
            'languages': self.languages,
            'issues': []
        }

        # Run Pylint for Python projects
        if 'python' in self.languages:
            pylint_issues = self._run_pylint()
            results['issues'].extend(pylint_issues)

        # Run staticcheck for Go projects
        if 'go' in self.languages:
            staticcheck_issues = self._run_staticcheck()
            results['issues'].extend(staticcheck_issues)

        # Run clippy for Rust projects
        if 'rust' in self.languages:
            clippy_issues = self._run_clippy()
            results['issues'].extend(clippy_issues)

        # Run PHPStan for PHP projects
        if 'php' in self.languages:
            phpstan_issues = self._run_phpstan()
            results['issues'].extend(phpstan_issues)

        # Run RuboCop for Ruby projects
        if 'ruby' in self.languages:
            rubocop_issues = self._run_rubocop()
            results['issues'].extend(rubocop_issues)

        # Run ktlint for Kotlin projects
        if 'kotlin' in self.languages:
            ktlint_issues = self._run_ktlint()
            results['issues'].extend(ktlint_issues)

        # Run SwiftLint for Swift projects
        if 'swift' in self.languages:
            swiftlint_issues = self._run_swiftlint()
            results['issues'].extend(swiftlint_issues)

        # Run dotnet build for C# projects (Roslyn analyzers)
        if 'csharp' in self.languages:
            roslyn_issues = self._run_dotnet_build()
            results['issues'].extend(roslyn_issues)

        # Run Semgrep for security analysis (if deployment mode and installed)
        if self.mode == 'deployment':
            if self._check_tool_installed('semgrep'):
                semgrep_issues = self._run_semgrep()
                results['issues'].extend(semgrep_issues)
            else:
                # Semgrep not available (normal on Windows)
                results['issues'].append({
                    'tool': 'semgrep',
                    'severity': 'info',
                    'message': 'Semgrep is not available on Windows. For security scanning, use WSL or Linux.',
                    'suggestion': 'Install WSL: https://aka.ms/wsl or use Linux/macOS'
                })

        # Run jscpd for duplication detection (if personal mode)
        if self.mode == 'personal':
            jscpd_issues = self._run_jscpd()
            results['issues'].extend(jscpd_issues)

        # Count issues by severity
        severity_counts = {'critical': 0, 'warning': 0, 'info': 0}
        for issue in results['issues']:
            severity = issue.get('severity', 'info')
            if severity in severity_counts:
                severity_counts[severity] += 1

        results['summary'] = {
            'total_issues': len(results['issues']),
            'by_severity': severity_counts
        }

        # Save to cache
        if self.use_cache and self.cache_manager:
            project_files = list(self.project_path.rglob('*'))
            project_files = [f for f in project_files if f.is_file()]
            self.cache_manager.save_result(cache_key, results, project_files)

        return results
