#!/usr/bin/env python3
import json
import os
import subprocess
from typing import Dict

SUBPROCESS_TIMEOUT = 300


def run_clippy(workspace_dir: str) -> tuple[bool, str]:
    current_env = os.environ.copy()

    current_env["RUSTFLAGS"] = "--cap-lints warn"

    cmd = [
        "cargo", "clippy",
        "--message-format=json",
        "--",
        "-W", "clippy::all",
        "-W", "clippy::pedantic"
    ]

    result = subprocess.run(
        cmd, 
        env=current_env, 
        capture_output=True, 
        text=True
    )

    result = subprocess.run(
        cmd,
        cwd=workspace_dir,
        capture_output=True,
        text=True,
        timeout=SUBPROCESS_TIMEOUT,
    )
    print(result)
    if result.returncode != 0:
        return False, (result.stderr or result.stdout).strip()

    return True, result.stdout


def parse_clippy_compiler_warnings(clippy_stdout: str) -> Dict[str, int]:
    compiler_warnings = {}

    for line in clippy_stdout.splitlines():
        data = json.loads(line)
        message_obj = data.get("message", {})
        if message_obj.get("level") == "warning":
            code_id = message_obj.get("code", {}).get("code")
            if code_id and not code_id.startswith("clippy::"):
                compiler_warnings[code_id] = compiler_warnings.get(code_id, 0) + 1

    return compiler_warnings


def parse_clippy_linter_warnings(clippy_stdout: str) -> Dict[str, int]:
    clippy_warnings = {}

    for line in clippy_stdout.splitlines():
        try:
            data = json.loads(line)
            message_obj = data.get("message", {})

            if message_obj.get("level") == "warning":
                code_id = message_obj.get("code", {}).get("code")
                if code_id and code_id.startswith("clippy::"):
                    clippy_warnings[code_id] = clippy_warnings.get(code_id, 0) + 1
        except Exception:
            continue

    return clippy_warnings

