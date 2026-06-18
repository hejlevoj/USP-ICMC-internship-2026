"""
Split dataset.jsonl into train/val/test and save as JSON files.
Filters out outlier C samples (max 10k chars) to avoid one 129k-char anomaly.
"""

import json, os, random

random.seed(42)

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

records = []
with open(os.path.join(ROOT, 'data', 'dataset.jsonl')) as f:
    for line in f:
        r = json.loads(line.strip())
        # filter extreme outliers in C (the 129k sample skews tokenization badly)
        if len(r["c"]) <= 10000 and len(r["rust"]) <= 5000:
            records.append({"problem_id": r["problem_id"], "c": r["c"], "rust": r["rust"]})

print(f"Total after filtering: {len(records)}")

random.shuffle(records)

n_train = 1500
n_val   = 200
n_test  = min(300, len(records) - n_train - n_val)

train = records[:n_train]
val   = records[n_train:n_train + n_val]
test  = records[n_train + n_val:n_train + n_val + n_test]

print(f"Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")

for split, data in [("train", train), ("val", val), ("test", test)]:
    with open(os.path.join(ROOT, "data", f"data_{split}.json"), "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved data_{split}.json")
