"""Core analyzer engine for Vibe-Code Auditor.

This module provides a unified analysis engine that can be used by both CLI and UI interfaces.
It handles language detection, static analysis, AI analysis, and progress reporting.
"""

from pathlib import Path
from typing import Optional, Dict, Any, Callable, List
import logging

from src.config.settings import ANTHROPIC_API_KEY, validate_api_key
from src.detectors.language_detector import LanguageDetector
from src.analyzers.static_analyzer import StaticAnalyzer
from src.analyzers.ai_analyzer import AIAnalyzer
from src.utils.history_tracker import HistoryTracker

logger = logging.getLogger(__name__)


class AnalysisProgress:
    """Container for analysis progress information."""

    def __init__(self):
        self.stage: str = ""
        self.message: str = ""
        self.percentage: int = 0
        self.languages: List[str] = []
        self.static_results: Optional[Dict[str, Any]] = None
        self.ai_results: Optional[Dict[str, Any]] = None
        self.completed: bool = False
        self.error: Optional[str] = None


class AnalyzerEngine:
    """
    Unified analysis engine for code auditing.

    This engine can be used by both CLI and UI interfaces to perform
    language detection, static analysis, and AI-powered code review.

    Attributes:
        project_path: Path to the project to analyze
        mode: Analysis mode ('deployment' or 'personal')
        skip_ai: Whether to skip AI analysis
        use_cache: Whether to use result caching
        save_history: Whether to save results to history
        progress_callback: Optional callback for progress updates
    """

    def __init__(
        self,
        project_path: Path,
        mode: str = 'deployment',
        skip_ai: bool = False,
        use_cache: bool = True,
        save_history: bool = True,
        progress_callback: Optional[Callable[[AnalysisProgress], None]] = None
    ):
        """
        Initialize the analyzer engine.

        Args:
            project_path: Path to the project to analyze
            mode: Analysis mode ('deployment' or 'personal')
            skip_ai: Whether to skip AI analysis
            use_cache: Whether to use result caching
            save_history: Whether to save results to history
            progress_callback: Optional callback function for progress updates
        """
        self.project_path = Path(project_path)
        self.mode = mode
        self.skip_ai = skip_ai
        self.use_cache = use_cache
        self.save_history = save_history
        self.progress_callback = progress_callback

        self._progress = AnalysisProgress()

        logger.debug("AnalyzerEngine initialized: path=%s, mode=%s, skip_ai=%s", project_path, mode, skip_ai)

    def _update_progress(
        self,
        stage: str,
        message: str,
        percentage: int,
        **kwargs
    ):
        """
        Update progress and call the callback if provided.

        Args:
            stage: Current stage of analysis
            message: Progress message
            percentage: Progress percentage (0-100)
            **kwargs: Additional progress data
        """
        self._progress.stage = stage
        self._progress.message = message
        self._progress.percentage = percentage

        for key, value in kwargs.items():
            setattr(self._progress, key, value)

        if self.progress_callback:
            try:
                self.progress_callback(self._progress)
            except Exception as e:  # pylint: disable=broad-except
                logger.warning("Progress callback failed: %s", e)

    def validate_requirements(self) -> tuple[bool, Optional[str]]:
        """
        Validate that all requirements are met for analysis.

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if project path exists
        if not self.project_path.exists():
            return False, f"Project path does not exist: {self.project_path}"

        if not self.project_path.is_dir():
            return False, f"Project path is not a directory: {self.project_path}"

        # Check API key if AI analysis is requested
        if not self.skip_ai:
            is_valid_key, key_error = validate_api_key()
            if not is_valid_key:
                return False, key_error

        return True, None

    def analyze(self) -> Dict[str, Any]:
        """
        Run the complete analysis pipeline.

        Returns:
            Dictionary containing analysis results with keys:
            - languages: List of detected languages
            - static_results: Static analysis results
            - ai_results: AI analysis results (or None if skipped)
            - project_path: Path to analyzed project
            - mode: Analysis mode used

        Raises:
            ValueError: If requirements validation fails
            RuntimeError: If analysis fails
        """
        try:
            # Validate requirements
            self._update_progress("validation", "Validating requirements...", 0)
            is_valid, error = self.validate_requirements()
            if not is_valid:
                self._progress.error = error
                self._progress.completed = True
                if self.progress_callback:
                    self.progress_callback(self._progress)
                raise ValueError(error)

            # Step 1: Detect languages
            self._update_progress("detection", "Detecting project languages...", 10)
            logger.info("Starting language detection")

            detector = LanguageDetector(self.project_path)
            languages = detector.detect()

            if not languages:
                error_msg = "No analyzable code files found"
                self._progress.error = error_msg
                self._progress.completed = True
                if self.progress_callback:
                    self.progress_callback(self._progress)
                raise RuntimeError(error_msg)

            logger.info("Detected languages: %s", languages)
            self._update_progress(
                "detection",
                f"Detected {len(languages)} language(s)",
                20,
                languages=languages
            )

            # Step 2: Run static analysis
            self._update_progress("static_analysis", "Running static analysis...", 30)
            logger.info("Starting static analysis")

            static_analyzer = StaticAnalyzer(
                self.project_path,
                languages,
                self.mode,
                use_cache=self.use_cache
            )
            static_results = static_analyzer.analyze()

            logger.info("Static analysis completed: %d issues found", len(static_results.get('issues', [])))
            self._update_progress(
                "static_analysis",
                "Static analysis completed",
                60,
                static_results=static_results
            )

            # Step 3: Run AI analysis (if not skipped)
            ai_results = None
            if not self.skip_ai:
                self._update_progress("ai_analysis", "Running AI code review...", 70)
                logger.info("Starting AI analysis")

                ai_analyzer = AIAnalyzer(self.project_path, self.mode)
                ai_results = ai_analyzer.analyze()

                logger.info("AI analysis completed")
                self._update_progress(
                    "ai_analysis",
                    "AI analysis completed",
                    90,
                    ai_results=ai_results
                )
            else:
                logger.info("AI analysis skipped")
                self._update_progress("ai_analysis", "AI analysis skipped", 90)

            # Step 4: Save to history (if enabled)
            if self.save_history:
                self._update_progress("finalization", "Saving to history...", 95)
                try:
                    history_tracker = HistoryTracker(self.project_path)
                    history_tracker.save_result(self.mode, static_results, ai_results)
                    logger.debug("Analysis result saved to history")
                except Exception as e:  # pylint: disable=broad-except
                    logger.warning("Failed to save history: %s", e)
                    # Don't fail the whole analysis just because history failed

            # Finalize
            result = {
                'languages': languages,
                'static_results': static_results,
                'ai_results': ai_results,
                'project_path': str(self.project_path),
                'mode': self.mode
            }

            self._update_progress(
                "completed",
                "Analysis completed successfully",
                100,
                completed=True
            )

            logger.info("Analysis pipeline completed successfully")
            return result

        except Exception as e:  # pylint: disable=broad-except
            logger.error("Analysis failed: %s", e, exc_info=True)
            self._progress.error = str(e)
            self._progress.completed = True
            if self.progress_callback:
                self.progress_callback(self._progress)
            raise

    def get_trend_data(self) -> Dict[str, Any]:
        """
        Get historical trend data for the project.

        Returns:
            Dictionary containing trend information
        """
        history_tracker = HistoryTracker(self.project_path)
        return history_tracker.get_trend_data()

    def clear_cache(self):
        """Clear the analysis cache for the project."""
        from src.utils.cache_manager import CacheManager
        cache_mgr = CacheManager(self.project_path)
        cache_mgr.invalidate()
        logger.info("Cache cleared")
