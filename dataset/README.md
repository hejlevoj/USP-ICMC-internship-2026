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

Difficulty is assigned based on the cosine similarity between the zero-shot `SFR-Embedding-Code-400M_R` embeddings of the C and Rust implementations — without any finetuning. SFR is used rather than UniXcoder to avoid a methodological dependency: using the same model family to both define difficulty tiers and measure finetuning improvement would make "hard" pairs hard by definition for UniXcoder. SFR is independently trained on a different corpus.

Thresholds are quantile-based over the full 1886-pair distribution (SFR sim: mean=0.823, std=0.062):

| Category | SFR similarity range | Count |
|----------|---------------------|-------|
| Easy | ≥ 0.868 | 472 (25%) |
| Medium | 0.781 – 0.868 | 943 (50%) |
| Hard | < 0.781 | 471 (25%) |

This categorization is origin-agnostic — it avoids comparing difficulty ratings across sources since AtCoder and Codeforces use incompatible rating scales.

---

## Sources

| Source | Problems | Style |
|--------|----------|-------|
| XcodeEval (Codeforces) | ~1018 | Competitive, systems-heavy |
| CodeNet (AtCoder) | ~839 | Competitive, algorithmic |
| common-algorithms | 29 | Textbook reference implementations |

---

## Cleaning Applied

127 entries were removed from the original 2013-entry dataset:

| Reason | Removed |
|--------|---------|
| Confirmed mis-pairs | 2 |
| AtCoder easy/hard near-duplicates (description sim > 0.90) | 69 |
| Suspicious similar pairs (0.80–0.90) | 54 |
| Length ratio outlier (190× C/Rust ratio) | 1 |
| Implementation divergence (structurally different algorithms) | 1 |

All entry-point function names are normalized to `solution` in both C and Rust.

---

## Related Repositories

| Repository | Description |
|------------|-------------|
| `github-finetune/` | Finetunes `unixcoder-base` on this dataset using LoRA adaptation. Achieves MRR@10=0.729 on the 300-pair test set. |
| `github-dataset-categorization/` | Script that computes per-pair SFR-Embedding-Code-400M_R zero-shot similarity and assigns easy/medium/hard categories. Reproduces the `difficulty` field. |
| `github-description-similarity/` | Embeds problem descriptions with OpenAI `text-embedding-3-large` and detects near-duplicate and suspicious problem pairs. |
