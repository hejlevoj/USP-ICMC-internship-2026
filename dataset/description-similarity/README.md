# Problem Description Similarity Analysis

Computes pairwise semantic similarity between competitive programming problem descriptions using OpenAI `text-embedding-3-large` (3072-dim). Used to detect near-duplicate and suspicious problem pairs in a C↔Rust dataset.

## What it does

- Embeds all problem descriptions via the OpenAI API (raw, no cleaning or truncation)
- Computes the full N×N pairwise cosine similarity matrix
- Reports near-duplicates (sim > 0.90), suspicious pairs (0.80–0.90), and per-origin statistics
- Saves results to `outputs/description_similarity_openai.json`

## Setup

```bash
pip install -r requirements.txt
```

Place your OpenAI API key in `api-key.txt` (single line).

Update the `API_KEY_FILE` path in `description_similarity_openai.py` to point to your key file.

## Usage

```bash
python description_similarity_openai.py
```

Input: `data/dataset.jsonl` — each entry must have `problem_id`, `problem_description`, `origin`.

Output: `outputs/description_similarity_openai.json` with global stats, per-origin breakdown, near-duplicate pairs, and suspicious pairs.

## Results (on 2013-problem C↔Rust dataset)

| Metric | Value |
|--------|-------|
| Mean pairwise similarity | 0.333 |
| Near-duplicates (sim > 0.90) | 69 pairs — 135 problems (6.7%) |
| Suspicious (0.80–0.90) | 78 pairs — 110 problems (5.5%) |
| Clearly unique | 1878 problems (93.3%) |

Near-duplicates are almost entirely AtCoder contest easy/hard variant pairs with identical problem statements but different input constraints.
