# Dataset Difficulty Categorization with UniXcoder

Categorizes C↔Rust problem pairs into difficulty tiers (easy / medium / hard) based on how similar the zero-shot UniXcoder embeddings of the C and Rust implementations already are — without any finetuning.

## Idea

Pairs where `unixcoder-base` already assigns high cosine similarity are **easy** — the implementations are structurally close enough for a generic code model to find them similar (near-literal translations). Pairs with low similarity are **hard** — the implementations diverge structurally and require the model to learn a more significant cross-language remapping.

Thresholds are quantile-based (25/50/25 split) so bins are always balanced regardless of the distribution shape.

| Category | Threshold | Share |
|----------|-----------|-------|
| Easy | sim ≥ p75 | 25% |
| Medium | p25 ≤ sim < p75 | 50% |
| Hard | sim < p25 | 25% |

This categorization is origin-agnostic — it avoids comparing difficulty ratings across sources (AtCoder vs Codeforces ratings are incompatible scales).

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
python categorize.py
```

Input: `data/dataset_cleaned.jsonl` — each entry must have `problem_id`, `c_code`, `rust_code`.

Output:
- `outputs/similarity_scores.json` — per-problem cosine similarity and assigned category
- `outputs/categories.json` — `{problem_id: "easy"|"medium"|"hard"}` mapping

## Results (on 1886-problem cleaned dataset)

| Category | Sim range | Count |
|----------|-----------|-------|
| Easy | ≥ 0.797 | 472 (25%) |
| Medium | 0.678–0.797 | 942 (50%) |
| Hard | < 0.678 | 472 (25%) |

Distribution: mean=0.730, std=0.092, min=0.330, max=0.935.
