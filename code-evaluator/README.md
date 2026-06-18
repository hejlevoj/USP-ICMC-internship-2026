# USP Pipeline

A static analysis pipeline for C and Rust source files. Normalizes code, evaluates quality metrics, and auto-fixes linter warnings.

## Requirements

**C pipeline:** `gcc`, `clang-tidy`, `clang-format`  
**Rust pipeline:** `cargo`, `rustfmt`, `clippy` (via `rustup component add clippy`)

## Usage

```
python run_pipeline.py <path> [config] [--stage STAGE] [-o OUTPUT_DIR]
```

`<path>` can be a single `.c`/`.rs` file or a directory (processes all matching files).  
`[config]` is required for `evaluate` and `all` stages.

### Stages

| Stage | Description | Requires config |
|---|---|---|
| `preprocess` | Remove comments, unused functions/macros, normalize encoding and formatting | No |
| `evaluate` | Analyze code quality — warnings, keyword scores, line counts. Saves a JSON report. | Yes |
| `align` | Auto-fix linter warnings and reformat | No |
| `all` | Run full pipeline: preprocess → evaluate → align *(default)* | Yes |

Each stage automatically runs its prerequisites (e.g. `align` silently runs `preprocess` first).

### Output files

All output is written next to the input file, or to `-o DIR` if specified:

| File | Stage |
|---|---|
| `<name>-preprocess.<ext>` | preprocess |
| `<name>-fix-aligned.<ext>` | align |
| `<name>-pipeline-report.json` | all |
| `<name>-evaluate.json` | evaluate |

### Examples

```bash
# Full pipeline on a single C file
python run_pipeline.py main.c c_pipeline/c-config.json

# Full pipeline on a Rust file, output to separate directory
python run_pipeline.py solution.rs rust_pipeline/rust-config.json -o out/

# Only preprocess (no config needed)
python run_pipeline.py main.c --stage preprocess

# Only evaluate
python run_pipeline.py main.c c_pipeline/c-config.json --stage evaluate

# Process an entire directory
python run_pipeline.py submissions/ rust_pipeline/rust-config.json
```

## Pipeline report

When running `--stage all`, a `<name>-pipeline-report.json` is saved with:

```json
{
  "file": "...",
  "language": "c",
  "pass": true,
  "has_main_function": true,
  "lines_of_code": 120,
  "function_count": 5,
  "keywords": {
    "pos_intensity": 3.4,
    "neg_intensity": 0.8,
    "net_score": 2.6,
    "details": { "positive_hits": {...}, "negative_hits": {...} }
  },
  "linter_scores": { "<category>": { "raw_penalty": 0, "weighted_penalty": 0, "hits": {} } },
  "compiler_scores": { "<category>": { "raw_penalty": 0, "weighted_penalty": 0, "hits": {} } },
  "linter_total_penalty": 0,
  "compiler_total_penalty": 0,
  "overall_code_penalty": 0,
  "raw_warnings": { "compiler_warnings": {}, "linter_warnings": {}, ... },
  "original_code": { "compiled": true, "error": null },
  "code_modify_stages": {
    "preprocess": { "run": true, "compiled": true, "error": null },
    "align":      { "run": true, "compiled": true, "error": null }
  }
}
```

`"pass": false` means the file failed to compile at some stage — check `original_code` and `code_modify_stages` for where it failed.

## Config file

Both `c_pipeline/c-config.json` and `rust_pipeline/rust-config.json` follow the same structure.

### `keywords`

Token-level scoring. Positive weights reward idiomatic constructs; negative weights penalize dangerous patterns.

```json
"keywords": {
  "malloc": 6,
  "goto": -8
}
```

### `categories_multipliers`

Scales the raw penalty of each warning category in the final score.

```json
"categories_multipliers": {
  "critical_safety": 10,
  "maintenance_and_style": 0.2
}
```

### `linter_warnings` / `compiler_warnings`

Maps individual warning IDs to raw penalty weights, grouped by category.

```json
"linter_warnings": {
  "categories": {
    "critical_safety": {
      "clang-analyzer-core.NullDereference": 100
    }
  }
}
```

**Final score per category:** `sum(weight × count)` for each triggered warning, then multiplied by the category multiplier. `overall_code_penalty` is the sum across all categories.

### Rust-specific: `cargo_config`

Optionally include a raw TOML string to override the generated `Cargo.toml`:

```json
"cargo_config": "[package]\nname = \"solution\"\nversion = \"0.1.0\"\nedition = \"2021\"\n"
```

