"""
Evaluation utilities for cross-language code similarity.

Metrics:
  - mean positive cosine similarity
  - mean negative cosine similarity (random pairs from different problems)
  - MRR@10  (mean reciprocal rank: given a C query, rank all Rust candidates)
  - R@1, R@5 (recall at k)
  - AP gap = mean_pos_sim - mean_neg_sim
"""

import json
import numpy as np
import torch
from torch import nn


def cosine_sim_matrix(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Compute pairwise cosine similarity between rows of a and b."""
    a = a / (np.linalg.norm(a, axis=1, keepdims=True) + 1e-9)
    b = b / (np.linalg.norm(b, axis=1, keepdims=True) + 1e-9)
    return a @ b.T  # (N, N)


def evaluate_embeddings(c_embs: np.ndarray, rust_embs: np.ndarray, split_name: str = "test") -> dict:
    """
    c_embs[i] and rust_embs[i] are a positive pair (same problem).
    All other (i, j) with i != j are negatives.
    """
    N = len(c_embs)
    sim = cosine_sim_matrix(c_embs, rust_embs)  # (N, N), sim[i, i] = positive

    pos_sims = sim[np.arange(N), np.arange(N)]
    # mean negative = mean of all off-diagonal entries
    mask = ~np.eye(N, dtype=bool)
    neg_sims = sim[mask]

    mean_pos = float(pos_sims.mean())
    mean_neg = float(neg_sims.mean())
    gap = mean_pos - mean_neg

    # MRR@10, R@1, R@5: query = C, retrieve from Rust pool
    ranks = []
    r1_hits = 0
    r5_hits = 0
    for i in range(N):
        row = sim[i]  # similarity of c_embs[i] to all rust_embs
        # rank of the true positive (index i)
        rank = int((row > row[i]).sum()) + 1  # 1-indexed
        ranks.append(rank)
        if rank <= 1:
            r1_hits += 1
        if rank <= 5:
            r5_hits += 1

    mrr = float(np.mean([1.0 / r for r in ranks]))
    r1 = r1_hits / N
    r5 = r5_hits / N

    results = {
        "split": split_name,
        "n": N,
        "mean_pos_sim": round(mean_pos, 4),
        "mean_neg_sim": round(mean_neg, 4),
        "sim_gap": round(gap, 4),
        "MRR@10": round(mrr, 4),
        "R@1": round(r1, 4),
        "R@5": round(r5, 4),
    }
    return results


def print_results(results: dict):
    print(f"\n{'='*50}")
    print(f"Evaluation on {results['split']} ({results['n']} pairs)")
    print(f"{'='*50}")
    print(f"  mean pos similarity : {results['mean_pos_sim']:.4f}")
    print(f"  mean neg similarity : {results['mean_neg_sim']:.4f}")
    print(f"  similarity gap      : {results['sim_gap']:.4f}")
    print(f"  MRR@10              : {results['MRR@10']:.4f}")
    print(f"  R@1                 : {results['R@1']:.4f}")
    print(f"  R@5                 : {results['R@5']:.4f}")
    print(f"{'='*50}\n")
