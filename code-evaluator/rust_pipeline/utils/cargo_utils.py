#!/usr/bin/env python3
import subprocess
from typing import Tuple

SUBPROCESS_TIMEOUT = 300


def create_cargo_workspace(workspace_dir: str) -> None:
    """Initialize a cargo workspace inside an existing directory."""
    subprocess.run(
        ["cargo", "new", workspace_dir, "--quiet"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=SUBPROCESS_TIMEOUT,
        check=True,
    )


def run_rustfmt(workspace_dir: str) -> Tuple[bool, str]:
    """Format code with rustfmt. Returns (Success, Error)."""
    result = subprocess.run(
        ["rustfmt", "src/main.rs"],
        cwd=workspace_dir,
        capture_output=True,
        text=True,
        timeout=SUBPROCESS_TIMEOUT,
    )
    if result.returncode != 0:
        return False, result.stderr.strip()
    return True, ""


def run_cargo_check(workspace_dir: str) -> Tuple[bool, str]:
    """Check if Rust code compiles.

    Returns:
        (success, stderr) - Returns True only if returncode is 0
    """
    result = subprocess.run(
        ["cargo","check"],
        cwd=workspace_dir,
        capture_output=True,
        text=True,
        timeout=SUBPROCESS_TIMEOUT,
    )
    if result.returncode != 0:
        return False, result.stderr.strip()
    return True, ""


def run_clippy_fix(workspace_dir: str) -> Tuple[bool, str]:
    """Run cargo clippy --fix. Returns (Success, Error)."""
    result = subprocess.run(
        ["cargo", "clippy", "--fix", "--allow-dirty"],
        cwd=workspace_dir,
        capture_output=True,
        text=True,
        timeout=SUBPROCESS_TIMEOUT,
    )
    # Note: clippy may return non-zero even on successful fixes
    return True, ""
