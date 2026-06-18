#!/usr/bin/env python3
import os
import re
import tempfile
import shutil
from typing import Dict, override

from c_pipeline.utils.clang_utils import run_clang_autofix, run_clang_format, run_gcc_complex_compile, run_clang_linter, run_gcc_simple_compile
from common.base_pipeline import BasePipeline, CompilationError
from common.utils import normalize_file, remove_comments, strip_leading_blank_lines
from c_pipeline.utils.function_utils import remove_unused_c_functions
from c_pipeline.utils.macro_utils import remove_unused_c_macros
from c_pipeline.utils.warning_utils import custom_goto_analysis, parse_gcc_output, parse_clang_tidy_output

class CPipeline(BasePipeline):

    @override
    def get_language(self) -> str:
        return "c"

    @override
    def get_file_extension(self) -> str:
        return "c"

    @override
    def get_function_pattern(self) -> str:
        # Relies on clang-format (LLVM style): function definitions start at column 0,
        # while control flow blocks (if/while/for) are always indented inside a function.
        return r'(?m)^[a-zA-Z_][\w\s\*]*\w\s*\([^)]*\)\s*\{'
    
    @override
    def get_main_function_pattern(self) -> str:
        pattern = r'\bmain\s*\('
        return pattern

    @override
    def setup_workspace(self) -> tuple[str, str]:
        self._tmpdir = tempfile.TemporaryDirectory()
        self._workspace_root = self._tmpdir.name

        source_path = os.path.join(self._workspace_root, "main.c")
        shutil.copy(self.file_path, source_path)
        os.chmod(source_path, 0o644)

        return self._workspace_root, source_path

    @override  
    def _cleanup_workspace(self) -> None:
        tmp = getattr(self, "_tmpdir", None)
        if tmp:
            tmp.cleanup()
            return
        
        workspace = getattr(self, "_workspace_root", None)
        if workspace and os.path.exists(workspace):
            shutil.rmtree(workspace)

    @override
    def preprocess(self) -> None:
        """Normalize C code. Base class handles validation and rollback."""
        # 1. Normalize file encoding and line endings
        normalize_file(self.source_path)

        # 2. Read code
        with open(self.source_path, 'r', encoding='utf-8') as f:
            code = f.read()

        # 3. Remove comments
        code = remove_comments(code)
        
        code = remove_unused_c_functions(code)

        code = remove_unused_c_macros(code)
        code = strip_leading_blank_lines(code)

        # 4. Write back
        with open(self.source_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(code)

        # 5. Format code with clang-format
        run_clang_format(self.source_path)

    @override
    def align(self) -> None:
        """Auto-fix and format C code. Base class handles validation and rollback."""
        # 1. Run clang-tidy autofix
        run_clang_autofix(source_path=self.source_path)

        # 2. Re-format (autofix can break formatting)
        run_clang_format(source_path=self.source_path)
        
    @override
    def get_parsed_compiler_warnings(self) -> Dict[str, int]:
        compiled, stderr = run_gcc_complex_compile(source_path=self.source_path)
        if not compiled:
            raise CompilationError(f"Running GCC failed: {stderr}")
        return parse_gcc_output(stderr=stderr)

    @override
    def get_parsed_linter_warnings(self) -> Dict[str, int]:
        succ, output = run_clang_linter(source_path=self.source_path)
        if not succ:
            raise CompilationError(f"Running clang failed: {output}")

        linter_warnings = parse_clang_tidy_output(output)
        linter_warnings.update(custom_goto_analysis(self.source_path))
        return linter_warnings
    
    @override
    def _check_compilation(self) -> tuple[bool, str]:
        compiled, err = run_gcc_simple_compile(self.source_path)
        error_pattern = re.compile(r"\berror\b", re.IGNORECASE)
        
        error_str = " | ".join(
            line.strip() for line in err.splitlines()
            if error_pattern.search(line)
        )   
        return compiled,error_str        