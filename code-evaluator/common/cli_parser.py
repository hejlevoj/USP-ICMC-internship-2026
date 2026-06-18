#!/usr/bin/env python3
import sys
import os
from typing import Tuple, Optional

def parse_cli_args(script_name: str, file_extension: str, description: str) -> Tuple[str, str]:
    """
    Parse command-line arguments for aligner/evaluator scripts.
    
    Args:
        script_name: Name of the script (e.g., "c_aligner.py")
        file_extension: Expected file extension (e.g., ".c", ".rs")
        description: Short description of what the script does
    
    Returns:
        Tuple of (file_path, output_dir)
        - file_path: Path to the input file
        - output_dir: Output directory (empty string if not specified)
    
    Exits with error message if validation fails.
    """
    # Check for minimum arguments
    if len(sys.argv) < 2:
        print(f"Usage: {script_name} <file{file_extension}> [output_dir]")
        print(f"\n{description}")
        print("\nArguments:")
        print(f"  file{file_extension:<8} - The {file_extension[1:].upper()} file to process")
        print(f"  output_dir  - (Optional) Directory to save the output file(s)")
        print(f"                If not specified, saves to the same directory as the input file")
        sys.exit(1)
    
    file_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else ""
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} does not exist")
        sys.exit(1)
    
    if not file_path.endswith(file_extension):
        print(f"Error: {file_path} is not a {file_extension[1:].upper()} file ({file_extension} extension expected)")
        sys.exit(1)
    
    if output_dir and not os.path.isdir(output_dir):
        print(f"Error: {output_dir} is not a valid directory")
        sys.exit(1)
    
    return file_path, output_dir
