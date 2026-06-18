"""
Dataset difficulty categorization using UniXcoder zero-shot embeddings.

For each C↔Rust pair in the dataset, computes the cosine similarity between
the C and Rust embeddings produced by unixcoder-base with no finetuning.
Assigns each problem to a difficulty category based on similarity quantiles:

  easy   — top 25%    (sim >= p75, implementations already close)
  medium — middle 50% (p25 <= sim < p75)
  hard   — bottom 25% (sim < p25, implementations structurally divergent)

Output:
  outputs/similarity_scores.json   — per-problem cosine similarity scores
  outputs/categories.json          — problem_id -> "easy" | "medium" | "hard"
"""

import json
import os
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel

os.chdir(os.path.dirname(os.path.abspath(__file__)))

DATASET   = "data/dataset_cleaned.jsonl"
MODEL_ID  = "microsoft/unixcoder-base"
MAX_LEN   = 512
BATCH     = 32
OUTPUT_SCORES = "outputs/similarity_scores.json"
OUTPUT_CATS   = "outputs/categories.json"

# ── load model ────────────────────────────────────────────────────────────────

print(f"Loading {MODEL_ID} ...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model     = AutoModel.from_pretrained(MODEL_ID)
model.eval()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
print(f"Device: {device}")

# ── load dataset ──────────────────────────────────────────────────────────────

with open(DATASET) as f:
    entries = [json.loads(l) for l in f if l.strip()]
print(f"Loaded {len(entries)} entries")

pids       = [e["problem_id"]   for e in entries]
c_texts    = [e["c_code"]       for e in entries]
rust_texts = [e["rust_code"]    for e in entries]

# ── encode ────────────────────────────────────────────────────────────────────

def encode(texts):
    all_embs = []
    for i in range(0, len(texts), BATCH):
        batch = texts[i:i + BATCH]
        enc = tokenizer(
            batch,
            padding=True,
            truncation=True,
            max_length=MAX_LEN,
            return_tensors="pt",
        ).to(device)
        with torch.no_grad():
            out = model(**enc)
        # mean pool over non-padding tokens
        mask = enc["attention_mask"].unsqueeze(-1).float()
        emb  = (out.last_hidden_state * mask).sum(1) / mask.sum(1)
        emb  = torch.nn.functional.normalize(emb, dim=-1)
        all_embs.append(emb.cpu().numpy())
        print(f"  encoded {min(i + BATCH, len(texts))}/{len(texts)}")
    return np.vstack(all_embs)

print("\nEncoding C snippets ...")
c_embs   = encode(c_texts)
print("\nEncoding Rust snippets ...")
rust_embs = encode(rust_texts)

# ── per-pair cosine similarity ────────────────────────────────────────────────

sims = (c_embs * rust_embs).sum(axis=1)  # dot product of unit vectors = cosine sim

print(f"\nSimilarity distribution:")
print(f"  mean={sims.mean():.4f}  std={sims.std():.4f}")
print(f"  min={sims.min():.4f}  p25={np.percentile(sims,25):.4f}  "
      f"p50={np.percentile(sims,50):.4f}  p75={np.percentile(sims,75):.4f}  "
      f"max={sims.max():.4f}")

# ── assign categories ─────────────────────────────────────────────────────────

p25 = float(np.percentile(sims, 25))
p75 = float(np.percentile(sims, 75))

def assign(sim):
    if sim >= p75:   return "easy"
    if sim >= p25:   return "medium"
    return "hard"

categories = {pid: assign(float(s)) for pid, s in zip(pids, sims)}

from collections import Counter
dist = Counter(categories.values())
print(f"\nCategory distribution:")
for cat in ["easy", "medium", "hard"]:
    print(f"  {cat}: {dist[cat]} ({100*dist[cat]/len(entries):.1f}%)")

print(f"\nThresholds: easy >= {p75:.4f}, hard < {p25:.4f}")

# ── save ──────────────────────────────────────────────────────────────────────

scores = [
    {"problem_id": pid, "similarity": float(s), "category": categories[pid]}
    for pid, s in zip(pids, sims)
]
with open(OUTPUT_SCORES, "w") as f:
    json.dump(scores, f, indent=2)

with open(OUTPUT_CATS, "w") as f:
    json.dump(categories, f, indent=2)

print(f"\nSaved {OUTPUT_SCORES}")
print(f"Saved {OUTPUT_CATS}")
