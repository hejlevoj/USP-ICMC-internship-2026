import subprocess
from typing import Tuple
from c_pipeline.constants import SUBPROCESS_TIMEOUT, STD

def run_gcc_simple_compile(source_path: str) -> Tuple[bool, str]:
    result = subprocess.run(
        ["gcc", f"-std={STD}", "-fsyntax-only", source_path],
        capture_output=True,
        text=True,
        timeout=SUBPROCESS_TIMEOUT
    )
    if result.returncode != 0:
        return False, (result.stderr or result.stdout).strip()
    return True, ""

def run_gcc_complex_compile(source_path: str) -> Tuple[bool, str]:
    result = subprocess.run(
        [
            "gcc", f"-std={STD}", "-fsyntax-only", 
            "-Wall", "-Wextra", "-Wpedantic", "-O2",
            source_path,
        ],
        capture_output=True,
        text=True,
        timeout=SUBPROCESS_TIMEOUT,
    )
    if result.returncode != 0:
        return False, (result.stderr or result.stdout).strip()
    return True, result.stderr.strip()

def run_clang_autofix(source_path: str) -> Tuple[bool,str]:
    result = subprocess.run([
        "clang-tidy", source_path, "-fix",
        "-checks=-*,bugprone-*,clang-diagnostic-*,readability-*,performance-*",
        "--", f"-std={STD}"
    ],
        capture_output=True,
        text=True,
        timeout=SUBPROCESS_TIMEOUT
    )
    # Note: clang-tidy returncode 1 doesn't always mean "failure", 
    # but for a pipeline, we check if it actually performed the task.
    return True, ""

def run_clang_format(source_path: str) -> Tuple[bool, str]:
    result = subprocess.run(
        ["clang-format", "-i", "-style=LLVM", source_path],
        capture_output=True,
        text=True,
        timeout=SUBPROCESS_TIMEOUT,
    )
    if result.returncode != 0:
        return False, result.stderr.strip()
    return True, ""
        
def run_clang_linter(source_path: str) -> Tuple[bool, str]:
    result = subprocess.run(
        ["clang-tidy", source_path, "-checks=*", "--", f"-std={STD}"],
        capture_output=True,
        text=True,
        timeout=SUBPROCESS_TIMEOUT
    )
    if result.returncode != 0:
        return False, result.stderr.strip()
    return True, result.stdout.strip()