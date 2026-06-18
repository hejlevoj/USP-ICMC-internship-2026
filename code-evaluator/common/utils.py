#!/usr/bin/env python3
import os
import json
import re
from collections import Counter
from typing import Dict

def load_config(config_path):
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, 'r') as f:
        config = json.load(f)

    return config

def detect_language(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    return {'.c': 'c', '.rs': 'rust'}.get(ext)

def strip_leading_blank_lines(code: str) -> str:
    return code.lstrip('\n')

def strip_above_first_function(code: str, function_pattern: str) -> str:
    match = re.search(function_pattern, code)
    if match:
        code = code[match.start():]
    return strip_leading_blank_lines(code)

def remove_comments(code):
    """Remove C-style comments from code (// and /* */)."""
    code = re.sub(r'//.*?$', '', code, flags=re.MULTILINE)
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    return code

def normalize_file(file_path):
    encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    code = None
    
    for encoding in encodings_to_try:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                code = f.read()
            break
        except (UnicodeDecodeError, LookupError):
            continue
    
    if code is None:
        with open(file_path, 'rb') as f:
            code = f.read().decode('utf-8', errors='replace')
    
    code = code.replace('\r\n', '\n').replace('\r', '\n')
    
    with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(code)

def strip_comments_and_strings(code: str) -> str:
    result = []
    i = 0
    while i < len(code):
        if i < len(code) - 1 and code[i:i+2] == '//':
            while i < len(code) and code[i] != '\n':
                result.append(' ')
                i += 1
            continue
        if i < len(code) - 1 and code[i:i+2] == '/*':
            result.append(' ')
            result.append(' ')
            i += 2
            while i < len(code) - 1:
                if code[i:i+2] == '*/':
                    result.append(' ')
                    result.append(' ')
                    i += 2
                    break
                result.append(' ' if code[i] != '\n' else '\n')
                i += 1
            continue
        if code[i] == '"':
            result.append(' ')
            i += 1
            while i < len(code):
                if code[i] == '\\' and i + 1 < len(code):
                    result.append(' ')
                    result.append(' ')
                    i += 2
                elif code[i] == '"':
                    result.append(' ')
                    i += 1
                    break
                else:
                    result.append(' ')
                    i += 1
            continue
        if code[i] == "'":
            result.append(' ')
            i += 1
            while i < len(code):
                if code[i] == '\\' and i + 1 < len(code):
                    result.append(' ')
                    result.append(' ')
                    i += 2
                elif code[i] == "'":
                    result.append(' ')
                    i += 1
                    break
                else:
                    result.append(' ')
                    i += 1
            continue
        result.append(code[i])
        i += 1
    return ''.join(result)


def remove_strings_from_code(code) -> str:
    clean_code = re.sub(r'"[^"]*"', '""', code)
    clean_code = re.sub(r"'[^']*'", "''", clean_code)
    return clean_code

def calculate_metrics(file_path, weights, fn_pattern):
    with open(file_path, 'r') as f:
        code = f.read()

    code = remove_strings_from_code(code)

    lines = [l for l in code.splitlines() if l.strip()]
    loc = len(lines)
    num_functions = len(re.findall(fn_pattern, code))

    multi_char = sorted(
        (re.escape(k) for k in weights if len(k) > 1 and not k.isidentifier()),
        key=len, reverse=True
    )
    pattern = '|'.join(multi_char + [r'\w+', r'[^\w\s]'])
    tokens = re.findall(pattern, code)
    token_count = len(tokens)
    
    keyword_hits = Counter(t for t in tokens if t in weights)
    
    pos_score = 0
    neg_score = 0
    
    for token, count in keyword_hits.items():
        weight = weights[token]
        if weight > 0:
            pos_score += weight * count
        else:
            neg_score += abs(weight) * count

    pos_intensity = (pos_score / token_count) * 100 if token_count else 0
    neg_intensity = (neg_score / token_count) * 100 if token_count else 0

    return {
        "lines_of_code": len([l for l in code.splitlines() if l.strip()]),
        "function_count": num_functions,
        "keywords": {
            "pos_intensity": round(pos_intensity, 2),
            "neg_intensity": round(neg_intensity, 2),
            "net_score": round(pos_intensity - neg_intensity, 2),
            "details": {
                "positive_hits": {t: c for t, c in keyword_hits.items() if weights[t] > 0},
                "negative_hits": {t: c for t, c in keyword_hits.items() if weights[t] < 0}
            }
        }

    }

def categorize_warnings(warnings_dict: Dict[str, int], categories_config: Dict[str, Dict[str, float]]):
    category_scores = {cat: 0.0 for cat in categories_config}
    category_hits = {cat: {} for cat in categories_config}

    for warning_id, count in warnings_dict.items():
        for category, weights in categories_config.items():
            if warning_id in weights:
                weight = weights[warning_id]
                category_scores[category] += weight * count
                category_hits[category][warning_id] = count
                break

    return category_scores, category_hits

def create_initial_stats(file_path, language):
    return {
        "file": file_path,
        "language": language,
        "has_main_function": False,
        "pass":False,
        "lines_of_code": 0,
        "function_count": 0,
        "linter_scores": {},
        "compiler_scores": {},
        "linter_total_penalty": 0,
        "compiler_total_penalty": 0,
    }
