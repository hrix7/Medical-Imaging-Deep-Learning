"""Calculate the binary classification measures I used to review model performance."""
from __future__ import annotations
import argparse
import json
import numpy as np
import pandas as pd

def binary_metrics(target, prediction) -> dict[str, float | int]:
    truth = np.asarray(target, dtype=int)
    pred = np.asarray(prediction, dtype=int)
    if truth.shape != pred.shape or truth.ndim != 1:
        raise ValueError("target and prediction must be one-dimensional arrays of equal length")
    if not set(np.unique(truth)).issubset({0, 1}) or not set(np.unique(pred)).issubset({0, 1}):
        raise ValueError("target and prediction must contain only 0 and 1")
    tp = int(((truth == 1) & (pred == 1)).sum())
    tn = int(((truth == 0) & (pred == 0)).sum())
    fp = int(((truth == 0) & (pred == 1)).sum())
    fn = int(((truth == 1) & (pred == 0)).sum())
    safe = lambda numerator, denominator: float(numerator / denominator) if denominator else 0.0
    return {
        "samples": int(truth.size), "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "accuracy": safe(tp + tn, truth.size),
        "sensitivity": safe(tp, tp + fn),
        "specificity": safe(tn, tn + fp),
        "precision": safe(tp, tp + fp),
        "f1": safe(2 * tp, 2 * tp + fp + fn),
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", help="CSV containing target and prediction columns")
    args = parser.parse_args()
    frame = pd.read_csv(args.csv)
    print(json.dumps(binary_metrics(frame["target"], frame["prediction"]), indent=2))
