#!/usr/bin/env python3

import os
import sys
import argparse
from common.utils import load_config


def run_pipeline_on_file(file_path, config, stages, output_dir=None):
    """Routes a single file to the appropriate C or Rust pipeline and runs specified stages."""
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext == ".c":
        from c_pipeline.c_pipeline import CPipeline
        pipeline_class = CPipeline
    elif ext == ".rs":
        from rust_pipeline.rust_pipeline import RustPipeline
        pipeline_class = RustPipeline
    else:
        return

    print(f"--> Processing: {file_path}")

    with pipeline_class(file_path, config, output_dir) as pipeline:
        if "all" in stages:
            result = pipeline.run_pipeline()
            if result.get("pass") is False:
                print(f"    [FAILED] {result.get('error') or 'compilation failed'}")
                sys.exit(1)
        else:
            for stage in stages:
                print(f"    Running stage: {stage}")
                result = pipeline.run_stage(stage)
                if result.get("pass") is False:
                    print(f"    [FAILED] {result.get('error') or 'stage failed'}")
                    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Process C (.c) or Rust (.rs) source files through a configurable pipeline.\n"
            "Accepts a single file or a directory of source files.\n"
            "\n"
            "Stages (run in dependency order automatically):\n"
            "  preprocess  Normalize code: remove comments, unused functions/macros, format.\n"
            "  evaluate    Analyze code quality: warnings, keyword metrics, line counts. Saves a JSON report.\n"
            "  align       Auto-fix linter warnings and reformat. Requires preprocess.\n"
            "  all         Run the full pipeline: preprocess → evaluate → align. (default)\n"
            "\n"
            "Each stage saves its output as <filename>-<stage>.<ext> next to the input file (or in -o DIR).\n"
            "Config file is optional for preprocess, align, and strip stages.\n"
            "When running a stage that has prerequisites, they run silently first (no output saved).\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "path",
        help="Input file (.c, .rs) or directory containing source files"
    )

    parser.add_argument(
        "config",
        nargs="?",
        default=None,
        help="Path to configuration JSON file. Required for --stage evaluate or --stage all."
    )

    parser.add_argument(
        "--stage",
        choices=["preprocess", "align", "evaluate", "all"],
        default="all",
        help="Stage to run (default: all)"
    )

    parser.add_argument(
        "-o", "--output",
        default=None,
        metavar="DIR",
        help="Directory to write output files to (default: same directory as input file)"
    )

    args = parser.parse_args()

    config = None
    if args.stage in ("evaluate", "all"):
        if not args.config:
            parser.error(f"--stage {args.stage} requires a config file argument")
        config = load_config(args.config)
    elif args.config:
        config = load_config(args.config)

    if not os.path.exists(args.path):
        print(f"Error: Path '{args.path}' does not exist.")
        return

    if args.output:
        os.makedirs(args.output, exist_ok=True)

    files_to_process = []

    if os.path.isdir(args.path):
        for f in os.listdir(args.path):
            if f.lower().endswith(('.c', '.rs')):
                files_to_process.append(os.path.join(args.path, f))

        if not files_to_process:
            print(f"No valid .c or .rs files found in directory: {args.path}")
            return
    else:
        files_to_process.append(args.path)

    for file_path in files_to_process:
        run_pipeline_on_file(file_path, config, [args.stage], args.output)


if __name__ == "__main__":
    main()