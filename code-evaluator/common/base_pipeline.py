#!/usr/bin/env python3
import json
import os
import re
import shutil
from abc import ABC, abstractmethod
from typing import Any, Dict

from common.utils import calculate_metrics, categorize_warnings, create_initial_stats

class CompilationError(Exception):
    pass

class BasePipeline(ABC):
    def __init__(self, file_path: str, config: Dict[str, Any] | None = None, output_dir: str | None = None):
        self.file_path: str = os.path.abspath(file_path)
        self.config: Dict[str, Any] = config or {}
        self.filename: str = os.path.splitext(os.path.basename(file_path))[0]
        self.base_dir: str = os.path.abspath(output_dir) if output_dir else os.path.dirname(self.file_path)

        # Set by __enter__ via setup_workspace; only source_path is part of the base class contract
        self.source_path: str

        self.compiler_warnings_cache = None
        self.linter_warnings_cache = None

    def __enter__(self):
        _, self.source_path = self.setup_workspace()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cleanup_workspace()
        return False
    
    @abstractmethod
    def get_language(self) -> str:
        """Return the language name (e.g., 'c', 'rust')."""
        pass

    @abstractmethod
    def get_file_extension(self) -> str:
        """Return the file extension for this language (e.g., 'c', 'rs')."""
        pass
    
    @abstractmethod
    def get_function_pattern(self) -> str:
        pass

    @abstractmethod
    def get_main_function_pattern(self) -> str:
        pass   

    @abstractmethod
    def setup_workspace(self) -> tuple[str, str]:
        """
        Create workspace once, reuse for all tools.

        Returns:
            tuple[str, str]: (workspace_dir, source_path)
                - workspace_dir: temporary directory for pipeline operations
                - source_path: path to the main source file in workspace
        """
        pass

    @abstractmethod
    def preprocess(self) -> None:
        """
        Normalize code: remove comments, remove unused code, normalize encoding.
        Returns path to preprocessed output file.
        """
        pass

    @abstractmethod
    def align(self) -> None:
        """
        Auto-fix and format code.
        Returns path to aligned output file.
        """
        pass

    @abstractmethod
    def _check_compilation(self) -> tuple[bool, str]:
        """
        Check if source compiles. Used by base class for validation.
        Subclasses implement language-specific compilation checks.

        Returns:
            tuple: (compiled: bool, error: str | None)
                - compiled: True if code compiles, False otherwise
                - error: Error message if compilation failed, None if succeeded
        """
        pass

    @abstractmethod
    def get_parsed_compiler_warnings(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_parsed_linter_warnings(self) -> Dict[str, Any]:
        pass

    def save_report(self, report: Dict[str, Any], name: str = "pipeline-report") -> None:
        report_path = os.path.join(self.base_dir, f"{self.filename}-{name}.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

    def _evaluate(self) -> Dict[str, Any]:
        """
        Analyze code quality: compile warnings, linter issues, metrics.
        Returns stats dictionary with weighted penalties.
        """
        stats = create_initial_stats(self.file_path, self.get_language())
        
        with open(self.source_path, 'r', encoding='utf-8') as f:
            code = f.read()
            stats["has_main_function"] = bool(re.search(self.get_main_function_pattern(), code))

        compiler_warnings = self.get_parsed_compiler_warnings()
        linter_warnings = self.get_parsed_linter_warnings()
        compiler_category_scores, compiler_category_hits = categorize_warnings(
            compiler_warnings,
            self.config["compiler_warnings"]["categories"]
        )
        linter_category_scores, linter_category_hits = categorize_warnings(
            linter_warnings,
            self.config["linter_warnings"]["categories"]
        )

        multipliers = self.config.get("categories_multipliers", {})
        
        def calculate_weighted_penalty(scores_dict):
            return sum(
                scores_dict.get(cat, 0) * multipliers.get(cat, 1.0) 
                for cat in scores_dict
            )

        linter_total_penalty = calculate_weighted_penalty(linter_category_scores)
        compiler_total_penalty = calculate_weighted_penalty(compiler_category_scores)

        # 4. Process metrics (keywords, functions, etc.)
        function_pattern = self.get_function_pattern()
        metrics = calculate_metrics(
            self.source_path,
            self.config["keywords"],
            function_pattern
        )
        
        # 5. Assemble the final stats object
        stats["pass"] = True
        stats.update({
            **metrics,
            "linter_scores": {
                cat: {
                    "raw_penalty": linter_category_scores[cat],
                    "weighted_penalty": linter_category_scores[cat] * multipliers.get(cat, 1.0),
                    "hits": linter_category_hits[cat]
                }
                for cat in linter_category_scores.keys()
            },
            "compiler_scores": {
                cat: {
                    "raw_penalty": compiler_category_scores[cat],
                    "weighted_penalty": compiler_category_scores[cat] * multipliers.get(cat, 1.0),
                    "hits": compiler_category_hits[cat]
                }
                for cat in compiler_category_scores.keys()
            },
            "linter_total_penalty": linter_total_penalty,
            "compiler_total_penalty": compiler_total_penalty,
            "overall_code_penalty": linter_total_penalty + compiler_total_penalty,

            "raw_warnings": {
                "compiler_warnings": compiler_warnings,
                "linter_warnings": linter_warnings,
                "compiler_total_count": sum(compiler_warnings.values()),
                "linter_total_count": sum(linter_warnings.values())
            }
        })
        
        return stats

    STAGE_DEPS: Dict[str, list] = {
        "preprocess": [],
        "evaluate":   ["preprocess"],
        "align":      ["preprocess"],
    }

    # Full pipeline execution order: (stage_name, check_compilation_after)
    PIPELINE_STAGES: list = [
        ("preprocess", True),
        ("evaluate",   False),
        ("align",      True),
    ]

    def _save_current_output(self, name: str) -> None:
        file_extension = self.get_file_extension()
        output_path = os.path.join(self.base_dir, f"{self.filename}-{name}.{file_extension}")
        shutil.copy(self.source_path, output_path)

    @abstractmethod
    def _cleanup_workspace(self) -> None:
        pass

    def _run_stage_impl(self, stage: str, save_output: bool) -> Dict[str, Any]:
        if stage == "preprocess":
            self.preprocess()
            if save_output:
                self._save_current_output("preprocess")
            return {"stage": "preprocess", "file": self.file_path, "pass": True}
        elif stage == "align":
            self.align()
            if save_output:
                self._save_current_output("fix-aligned")
            return {"stage": "align", "file": self.file_path, "pass": True}
        elif stage == "evaluate":
            stats = self._evaluate()
            if save_output:
                self.save_report(stats, name="evaluate")
            return stats
        raise ValueError(f"Unknown stage: {stage!r}")

    def run_stage(self, stage: str) -> Dict[str, Any]:
        """Run a single named stage, automatically running prerequisites first."""
        if stage not in self.STAGE_DEPS:
            raise ValueError(f"Unknown stage: {stage!r}. Choose from: {sorted(self.STAGE_DEPS)}")
        try:
            for dep in self.STAGE_DEPS[stage]:
                self._run_stage_impl(dep, save_output=True)
            return self._run_stage_impl(stage, save_output=True)
        except Exception as e:
            return {"stage": stage, "file": self.file_path, "pass": False, "error": str(e)}

    def run_pipeline(self) -> Dict[str, Any]:
        """Run the full pipeline driven by PIPELINE_STAGES."""
        compile_checked_stages = {"preprocess", "align"}
        code_modify_stages = {
            name: {"run": False, "compiled": False, "error": None}
            for name, _ in self.PIPELINE_STAGES
            if name in compile_checked_stages
        }
        original_code: Dict[str, Any] = {"compiled": False, "error": None}
        report: Dict[str, Any] | None = None

        try:
            compiled, error = self._check_compilation()
            original_code["compiled"] = compiled
            original_code["error"] = error
            if not compiled:
                report = create_initial_stats(self.file_path, self.get_language())
                report["code_modify_stages"] = code_modify_stages
                report["original_code"] = original_code
                report["pass"] = False
                self.save_report(report)
                return report

            for stage, check_compilation in self.PIPELINE_STAGES:
                result = self._run_stage_impl(stage, save_output=True)
                if stage == "evaluate":
                    report = result
                    report["code_modify_stages"] = code_modify_stages
                    report["original_code"] = original_code

                if check_compilation:
                    compiled, error = self._check_compilation()
                    code_modify_stages[stage]["compiled"] = compiled
                    code_modify_stages[stage]["error"] = error
                    code_modify_stages[stage]["run"] = True
                    if not compiled:
                        if report is None:
                            report = create_initial_stats(self.file_path, self.get_language())
                            report["original_code"] = original_code
                        report["code_modify_stages"] = code_modify_stages
                        report["pass"] = False
                        self.save_report(report)
                        return report
                elif stage in code_modify_stages:
                    code_modify_stages[stage]["run"] = True

            if report is None:
                report = create_initial_stats(self.file_path, self.get_language())
                report["original_code"] = original_code
            report["code_modify_stages"] = code_modify_stages
            report["pass"] = True
            self.save_report(report)
            return report

        except Exception as e:
            if report is None:
                report = create_initial_stats(self.file_path, self.get_language())
            report["pass"] = False
            report["error"] = f"Unexpected error: {e}"
            report["code_modify_stages"] = code_modify_stages
            report["original_code"] = original_code
            self.save_report(report)
            return report
