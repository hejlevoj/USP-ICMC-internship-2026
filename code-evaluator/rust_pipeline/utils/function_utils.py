#!/usr/bin/env python3
import re
from typing import Dict, Set, Tuple
from common.utils import strip_comments_and_strings as _strip_c_comments_and_strings


def remove_unused_rust_functions(code: str) -> str:
    functions = _parse_rust_functions(code)

    if not functions:
        return code

    # Build call graph
    call_graph = _build_call_graph(functions)

    # Find reachable functions starting from main and all pub functions
    reachable = set()

    # Start from main if it exists
    if 'main' in functions:
        reachable.update(_find_reachable_functions(call_graph, 'main'))

    # Add all public functions and their dependencies
    for func_name, (_, _, _, is_pub) in functions.items():
        if is_pub:
            reachable.add(func_name)
            reachable.update(_find_reachable_functions(call_graph, func_name))

    # If no main and no pub functions, keep everything (library without pub exports)
    if not reachable:
        return code

    return _filter_functions(code, functions, reachable)


def _parse_rust_functions(code: str) -> Dict[str, Tuple[int, int, str, bool]]:
    functions = {}

    # Pattern to match Rust function definitions
    # Matches: [pub] [async] [unsafe] [extern] fn name[<generics>](params) [-> return_type] {
    pattern = r'\b(pub\s+)?(?:async\s+)?(?:unsafe\s+)?(?:extern\s+(?:"[^"]*"\s+)?)?fn\s+(\w+)\s*(?:<[^>]*>)?\s*\([^)]*\)(?:\s*->\s*[^{]+)?\s*\{'

    for match in re.finditer(pattern, code):
        is_pub = match.group(1) is not None
        func_name = match.group(2)
        start_pos = match.start()

        # Find matching closing brace
        brace_count = 1
        pos = match.end()

        while pos < len(code) and brace_count > 0:
            if code[pos] == '{':
                brace_count += 1
            elif code[pos] == '}':
                brace_count -= 1
            pos += 1

        if brace_count == 0:
            end_pos = pos
            body = code[start_pos:end_pos]
            functions[func_name] = (start_pos, end_pos, body, is_pub)

    return functions


def _strip_comments_and_strings(code: str) -> str:
    # First blank out raw string literals r#"..."# (not valid C syntax)
    def blank_raw_strings(s: str) -> str:
        result = list(s)
        i = 0
        while i < len(s):
            if s[i] == 'r' and i + 1 < len(s) and s[i+1] == '#':
                j = i + 1
                hash_count = 0
                while j < len(s) and s[j] == '#':
                    hash_count += 1
                    j += 1
                if j < len(s) and s[j] == '"':
                    end_pattern = '"' + '#' * hash_count
                    k = j + 1
                    while k < len(s):
                        if s[k:k+len(end_pattern)] == end_pattern:
                            for idx in range(i, k + len(end_pattern)):
                                if result[idx] != '\n':
                                    result[idx] = ' '
                            i = k + len(end_pattern)
                            break
                        k += 1
                    else:
                        i += 1
                    continue
            i += 1
        return ''.join(result)

    return _strip_c_comments_and_strings(blank_raw_strings(code))


def _build_call_graph(functions: Dict[str, Tuple[int, int, str, bool]]) -> Dict[str, Set[str]]:
    call_graph = {}

    for func_name, (_, _, body, _) in functions.items():
        called_funcs = set()

        # Strip comments and strings to avoid false positives
        clean_body = _strip_comments_and_strings(body)

        # Search for function calls within the function body
        for other_func_name in functions.keys():
            if other_func_name != func_name:
                # Match the function name as a whole word
                # In Rust, functions can be called with:
                # - func_name()
                # - func_name::<Type>()
                # - module::func_name()
                # - &func_name (function pointer)
                pattern = r'(?:\b' + re.escape(other_func_name) + r'\s*(?:\(|::|<)|&\s*' + re.escape(other_func_name) + r'\b)'
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


def _filter_functions(code: str, functions: Dict[str, Tuple[int, int, str, bool]], reachable: Set[str]) -> str:
    remove_ranges = []
    for func_name, (start, end, _, _) in functions.items():
        if func_name not in reachable:
            remove_ranges.append((start, end))

    if not remove_ranges:
        return code

    # Sort in reverse order to remove from end to start
    remove_ranges.sort(reverse=True)

    result = code
    for start, end in remove_ranges:
        result = result[:start] + result[end:]

    return result