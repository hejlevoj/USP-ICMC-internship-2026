#!/usr/bin/env python3
import re
from typing import Dict
from common.utils import remove_strings_from_code

SUBPROCESS_TIMEOUT = 300


def custom_goto_analysis(source_path: str) -> Dict[str, int]:
    with open(source_path, "r") as f:
        code = f.read()

    # Remove string and character literals to avoid false positives
    code = remove_strings_from_code(code)

    goto_pattern = re.compile(r"\bgoto\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*;")
    goto_count = len(goto_pattern.findall(code))

    if goto_count > 0:
        return {"custom-goto-statement": goto_count}
    return {}

def parse_gcc_output(stderr: str) -> dict[str, int]:
    warning_counts = {}
    warning_pattern = re.compile(r"\[-W([\w-]+)(?:=\d*)?\]")
    for line in stderr.splitlines():
        if "warning:" in line:
            match = warning_pattern.search(line)
            if match:
                warning_flag = f"-W{match.group(1)}"
                warning_counts[warning_flag] = warning_counts.get(warning_flag, 0) + 1
    return warning_counts

def parse_clang_tidy_output(stdout: str) -> dict[str, int]:
    lint_counts: dict[str, int] = {}
    # Matches brackets at the very end of a line, potentially followed by whitespace
    lint_pattern = re.compile(r"\[([\w\-\.,]+)\]\s*$")
    
    for line in stdout.splitlines():
        if "warning:" in line:
            # We look for the match specifically at the end of the line
            match = lint_pattern.search(line)
            if match:
                # Group 1 contains the string inside the brackets
                lint_ids = match.group(1)
                for lint_id in lint_ids.split(","):
                    lint_id = lint_id.strip()
                    if lint_id:
                        lint_counts[lint_id] = lint_counts.get(lint_id, 0) + 1

    return lint_counts


from common.utils import categorize_warnings
