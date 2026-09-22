import numpy as np
from src.metrics import dice_score, iou_score

def test_perfect_overlap():
    mask = np.array([[1, 0], [0, 1]])
    assert dice_score(mask, mask) == 1.0
    assert iou_score(mask, mask) == 1.0

def test_no_overlap_is_near_zero():
    pred = np.array([[1, 0]])
    target = np.array([[0, 1]])
    assert dice_score(pred, target) < 1e-6
    assert iou_score(pred, target) < 1e-6
