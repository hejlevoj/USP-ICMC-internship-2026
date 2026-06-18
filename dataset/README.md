# C↔Rust Dataset

1886 competitive programming problems each implemented in C and Rust, cleaned and categorized for cross-language code similarity research.

---

## Schema

Each entry in `dataset_cleaned.jsonl` is a JSON object with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `problem_id` | string | Zero-padded sequential ID (`0001`–`1886`) |
| `problem_description` | string | Full problem statement (HTML or plain text) |
| `c_code` | string | C implementation, entry point normalized to `solution()` |
| `rust_code` | string | Rust implementation, entry point normalized to `fn solution()` |
| `difficulty` | string | `"easy"` / `"medium"` / `"hard"` |

---

## Difficulty Categorization

Difficulty is assigned based on the cosine similarity between the zero-shot `unixcoder-base` embeddings of the C and Rust implementations — without any finetuning. Pairs where the baseline model already finds the two implementations similar are **easy** (near-literal translations). Pairs where the implementations are structurally divergent despite solving the same problem are **hard**.

Thresholds are quantile-based over the full 1886-pair distribution (mean=0.730, std=0.092):

| Category | Similarity range | Count |
|----------|-----------------|-------|
| Easy | ≥ 0.797 | 472 (25%) |
| Medium | 0.678 – 0.797 | 942 (50%) |
| Hard | < 0.678 | 472 (25%) |

This categorization is origin-agnostic — it avoids comparing difficulty ratings across sources since AtCoder and Codeforces use incompatible rating scales.

---

## Sources

| Source | Problems | Style |
|--------|----------|-------|
| XcodeEval (Codeforces) | ~1018 | Competitive, systems-heavy |
| CodeNet (AtCoder) | ~839 | Competitive, algorithmic |
| common-algorithms | 29 | Textbook reference implementations |

---
All entry-point function names are normalized to `solution` in both C and Rust.
