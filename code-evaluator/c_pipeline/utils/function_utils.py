import re
from typing import Dict, Set, Tuple, List
from common.utils import strip_comments_and_strings as _strip_comments_and_strings


def remove_unused_macros(source_code: str) -> str:
    macros = _parse_macros(source_code)

    if not macros:
        return source_code

    used_macros = _find_used_macros(source_code, macros)

    return _filter_macros(source_code, macros, used_macros)


def remove_unused_c_functions(source_code: str) -> str:
    functions = _parse_c_functions(source_code)

    if not functions:
        return source_code

    # If main doesn't exist, keep all functions
    if 'main' not in functions:
        return source_code

    call_graph = _build_call_graph(functions)
    reachable = _find_reachable_functions(call_graph, 'main')

    return _filter_functions(source_code, functions, reachable)


def _parse_c_functions(source_code: str) -> Dict[str, Tuple[int, int, str]]:
    functions = {}

    # Pattern to match C function definitions at file level
    # Matches: [storage] [modifiers] return_type [*...] function_name(parameters) { ... }
    # Storage: static, extern, inline
    # Modifiers: const
    # Return type: int, void, char, struct/enum Type, typedef'd types
    pattern = r'(?:^|\n)\s*(?:static\s+)?(?:inline\s+)?(?:const\s+)?(?:struct\s+|enum\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s*(\*+)?\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*\{'

    for match in re.finditer(pattern, source_code, re.MULTILINE):
        return_type = match.group(1)
        pointer = match.group(2) if match.group(2) else ''
        func_name = match.group(3)

        # Skip type keywords that might be mistaken for return types
        keywords = {'if', 'while', 'for', 'switch', 'return', 'sizeof', 'else', 'do'}
        if return_type in keywords or func_name in keywords:
            continue

        func_start = match.start()
        # Skip leading newline if present
        if func_start < len(source_code) and source_code[func_start] == '\n':
            func_start += 1

        # Check if we're already inside a function by checking if there are unclosed braces before this point
        # Count braces from start to this position
        open_braces = source_code[:func_start].count('{')
        close_braces = source_code[:func_start].count('}')

        # If braces are balanced, we're at file level (top level)
        # If not balanced, we're inside a function (nested code)
        if open_braces != close_braces:
            continue

        # Find the matching closing brace
        brace_start = match.end() - 1  # Position of opening '{'

        brace_count = 1
        pos = brace_start + 1

        while pos < len(source_code) and brace_count > 0:
            if source_code[pos] == '{':
                brace_count += 1
            elif source_code[pos] == '}':
                brace_count -= 1
            pos += 1

        if brace_count == 0:
            func_end = pos
            body = source_code[func_start:func_end]
            functions[func_name] = (func_start, func_end, body)

    return functions


def _build_call_graph(functions: Dict[str, Tuple[int, int, str]]) -> Dict[str, Set[str]]:
    call_graph = {}

    for func_name, (_, _, body) in functions.items():
        called_funcs = set()

        # Strip comments and strings to avoid false positives
        clean_body = _strip_comments_and_strings(body)

        # Search for function calls within the function body
        for other_func_name in functions.keys():
            if other_func_name != func_name:
                # Match the function name as a whole word
                # Also match &function_name for function pointers
                pattern = r'(?:\b' + re.escape(other_func_name) + r'\s*\(|&\s*' + re.escape(other_func_name) + r'\b)'
                if re.search(pattern, clean_body):
                    called_funcs.add(other_func_name)

        call_graph[func_name] = called_funcs

    return call_graph


def _find_reachable_functions(call_graph: Dict[str, Set[str]], start: str) -> Set[str]:
    if start not in call_graph:
        return {start} if start else set()

    reachable = set()
    stack = [start]

    while stack:
        func = stack.pop()
        if func in reachable:
            continue

        reachable.add(func)

        if func in call_graph:
            for called in call_graph[func]:
                if called not in reachable:
                    stack.append(called)

    return reachable


def _filter_functions(source_code: str, functions: Dict[str, Tuple[int, int, str]], reachable: Set[str]) -> str:
    remove_ranges = []
    for func_name, (start, end, _) in functions.items():
        if func_name not in reachable:
            remove_ranges.append((start, end))

    if not remove_ranges:
        return source_code

    # Sort in reverse order to remove from end to start
    remove_ranges.sort(reverse=True)

    result = source_code
    for start, end in remove_ranges:
        result = result[:start] + result[end:]

    return result

def _parse_macros(source_code: str) -> Dict[str, Tuple[int, int, str]]:
    macros = {}

    # Pattern to match #define directives
    # Matches both simple defines and function-like macros
    # #define NAME
    # #define NAME value
    # #define NAME(args) replacement
    pattern = r'^\s*#\s*define\s+([A-Z_][A-Z0-9_]*)'

    lines = source_code.split('\n')
    line_positions = []
    pos = 0

    # Build a map of line start positions
    for line in lines:
        line_positions.append(pos)
        pos += len(line) + 1  # +1 for newline

    for i, line in enumerate(lines):
        match = re.match(pattern, line)
        if match:
            macro_name = match.group(1)
            line_start = line_positions[i]

            # Handle multi-line macros (lines ending with \)
            j = i
            while j < len(lines) and lines[j].rstrip().endswith('\\'):
                j += 1

            # Calculate end position
            if j < len(lines):
                line_end = line_positions[j] + len(lines[j]) + 1
            else:
                line_end = len(source_code)

            full_definition = '\n'.join(lines[i:j+1])
            macros[macro_name] = (line_start, line_end, full_definition)

    return macros


def _find_used_macros(source_code: str, macros: Dict[str, Tuple[int, int, str]]) -> Set[str]:
    used = set()

    # Strip comments and strings to avoid false positives
    clean_code = _strip_comments_and_strings(source_code)

    for macro_name, (start, end, definition) in macros.items():
        # Create code without this macro definition
        code_without_macro = clean_code[:start] + ' ' * (end - start) + clean_code[end:]

        # Look for usage of this macro
        # Match as whole word, but not in #define line itself
        pattern = r'\b' + re.escape(macro_name) + r'\b'

        if re.search(pattern, code_without_macro):
            used.add(macro_name)

    return used


def _filter_macros(source_code: str, macros: Dict[str, Tuple[int, int, str]], used: Set[str]) -> str:
    remove_ranges = []
    for macro_name, (start, end, _) in macros.items():
        if macro_name not in used:
            remove_ranges.append((start, end))

    if not remove_ranges:
        return source_code

    # Sort in reverse order to remove from end to start
    remove_ranges.sort(reverse=True)

    result = source_code
    for start, end in remove_ranges:
        result = result[:start] + result[end:]

    return result