"""Small, dependency-light segmentation metrics."""
from __future__ import annotations
import numpy as np

def _binary(array, threshold: float) -> np.ndarray:
    return np.asarray(array, dtype=float) >= threshold

def dice_score(prediction, target, threshold: float = 0.5, eps: float = 1e-7) -> float:
    pred = _binary(prediction, threshold)
    truth = _binary(target, threshold)
    intersection = np.logical_and(pred, truth).sum()
    return float((2.0 * intersection + eps) / (pred.sum() + truth.sum() + eps))

def iou_score(prediction, target, threshold: float = 0.5, eps: float = 1e-7) -> float:
    pred = _binary(prediction, threshold)
    truth = _binary(target, threshold)
    intersection = np.logical_and(pred, truth).sum()
    union = np.logical_or(pred, truth).sum()
    return float((intersection + eps) / (union + eps))
