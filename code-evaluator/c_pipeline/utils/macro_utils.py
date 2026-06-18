#!/usr/bin/env python3
import re
from typing import Dict, Set, Tuple


def remove_unused_c_macros(code: str) -> str:
    macros = _parse_c_macros(code)
    if not macros:
        return code

    # Find which macros are used
    used_macros = _find_used_macros(code, macros)

    # Remove unused macros
    return _filter_macros(code, macros, used_macros)


def _parse_c_macros(code: str) -> Dict[str, Tuple[int, int, str]]:
    macros = {}

    # Match #define directives (handling multi-line macros with backslash continuation)
    pattern = r'^\s*#\s*define\s+(\w+)(?:\([^)]*\))?\s*.*?(?:\\\n.*?)*?(?=\n(?!\s*\\))'

    for match in re.finditer(pattern, code, flags=re.MULTILINE):
        macro_name = match.group(1)
        start_pos = match.start()
        end_pos = match.end()
        full_text = code[start_pos:end_pos]
        macros[macro_name] = (start_pos, end_pos, full_text)

    return macros


def _find_used_macros(code: str, macros: Dict[str, Tuple[int, int, str]]) -> Set[str]:
    used = set()

    for macro_name, (start_pos, end_pos, _) in macros.items():
        # Search for the macro name as a whole word, but exclude the definition itself
        pattern = r'\b' + re.escape(macro_name) + r'\b'

        # Search in code before and after the macro definition
        code_before = code[:start_pos]
        code_after = code[end_pos:]

        if re.search(pattern, code_before) or re.search(pattern, code_after):
            used.add(macro_name)

    return used


def _filter_macros(code: str, macros: Dict[str, Tuple[int, int, str]], used: Set[str]) -> str:
    remove_ranges = []

    for macro_name, (start, end, _) in macros.items():
        if macro_name not in used:
            # Include the newline after the macro definition
            if end < len(code) and code[end] == '\n':
                end += 1
            remove_ranges.append((start, end))

    if not remove_ranges:
        return code

    # Sort by start position (descending) to remove from end to start
    remove_ranges.sort(reverse=True)

    result = code
    for start, end in remove_ranges:
        result = result[:start] + result[end:]

    return result
