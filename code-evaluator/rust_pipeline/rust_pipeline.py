#!/usr/bin/env python3
import os
import shutil
import tempfile
from typing import Dict, override

from common.base_pipeline import BasePipeline, CompilationError
from common.utils import normalize_file, remove_comments, strip_leading_blank_lines
from rust_pipeline.utils.allow_statement_utils import remove_rust_allow_attributes
from rust_pipeline.utils.cargo_utils import create_cargo_workspace, run_rustfmt, run_cargo_check, run_clippy_fix
from rust_pipeline.utils.clippy_utils import run_clippy, parse_clippy_compiler_warnings, parse_clippy_linter_warnings
from rust_pipeline.utils.function_utils import remove_unused_rust_functions

SUBPROCESS_TIMEOUT = 300

class RustPipeline(BasePipeline):

    @override
    def get_language(self) -> str:
        return "rust"

    @override
    def get_file_extension(self) -> str:
        return "rs"

    @override
    def get_function_pattern(self) -> str:
        return r'\bfn\s+\w+'

    @override
    def get_main_function_pattern(self) -> str:
        return r'\bfn\s+main\s*\('

    @override
    def setup_workspace(self) -> tuple[str, str]:
        """
        Creates a temporary workspace and populates it with a 
        Cargo.toml derived from the config file.
        """
        self._tmpdir = tempfile.TemporaryDirectory()
        self._workspace_root = os.path.join(self._tmpdir.name, "workspace")

        create_cargo_workspace(self._workspace_root)

        cargo_toml_path = os.path.join(self._workspace_root, "Cargo.toml")
        custom_cargo_toml = self.config.get("cargo_config")
        if custom_cargo_toml:
            with open(cargo_toml_path, 'w', encoding='utf-8') as f:
                f.write(custom_cargo_toml)

        source_path = os.path.join(self._workspace_root, "src", "main.rs")
        shutil.copy(self.file_path, source_path)
        os.chmod(source_path, 0o644)

        return self._workspace_root, source_path

    @override
    def _cleanup_workspace(self) -> None:
        tmp = getattr(self, "_tmpdir", None)
        if tmp:
            # Small delay can help prevent 'Directory not empty' errors on some OS
            import time
            time.sleep(0.1)
            tmp.cleanup()
            
    @override
    def preprocess(self) -> None:
        """Normalize Rust code: remove comments, unused functions."""

        # 1. Normalize file encoding and line endings
        normalize_file(self.source_path)

        with open(self.source_path, 'r', encoding='utf-8') as f:
            code = f.read()
            
            # 2. Remove allow statements
            code = remove_rust_allow_attributes(code)
            # 3. Remove comments
            code = remove_comments(code)
            # 4. Remove unused functions
            code = remove_unused_rust_functions(code)
            code = strip_leading_blank_lines(code)

        # 5. Write back
        with open(self.source_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(code)

        # 6. Format code with rustfmt
        run_rustfmt(self._workspace_root)
    
    @override
    def align(self) -> None:
        """Auto-fix and format Rust code."""
        # Run cargo clippy --fix
        run_clippy_fix(self._workspace_root)

        # Format code with rustfmt
        run_rustfmt(self._workspace_root)

        # 

    @override
    def get_parsed_compiler_warnings(self) -> Dict[str, int]:
        """Get compiler warnings from clippy output."""
        # Run clippy once and cache the output
        if not hasattr(self, '_clippy_output'):
            success, output = run_clippy(self._workspace_root)
            if not success:
                raise CompilationError(f"Running clippy failed: {output}")
            self._clippy_output = output

        return parse_clippy_compiler_warnings(self._clippy_output)

    @override
    def get_parsed_linter_warnings(self) -> Dict[str, int]:
        """Get clippy linter warnings from clippy output."""
        # Reuse cached clippy output
        if not hasattr(self, '_clippy_output'):
            success, output = run_clippy(self._workspace_root)
            if not success:
                raise CompilationError(f"Running clippy failed: {output}")
            self._clippy_output = output

        return parse_clippy_linter_warnings(self._clippy_output)

    @override
    def _check_compilation(self) -> tuple[bool, str]:
        compiled, error = run_cargo_check(self._workspace_root)
        error_str = " | ".join(
            line for line in error.splitlines()
            if line.startswith("error")
        )       
        return compiled,error_str
