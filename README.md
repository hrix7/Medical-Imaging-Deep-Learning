# Deep Learning for Medical Image Analysis

I built this collection of chest X-ray learning pipelines during my graduate work at Arizona State University under Dr. Jianming Liang. My work covered classification, lung segmentation, multi-class segmentation, and lesion localization/detection, together with reproducible GPU training on ASU's Sol cluster.

## Work I completed

- Prepared chest X-ray inputs and masks for model training and evaluation.
- Built classification and segmentation pipelines in PyTorch.
- Used U-Net-based methods for lung segmentation and achieved a Dice score of approximately 0.89.
- Reached 95% accuracy in the chest X-ray classification work summarized on my resume.
- Implemented UPerNet with a ResNet-101 backbone for multi-class segmentation, with Dice = 0.43 and IoU = 0.27 in that experiment.
- Implemented Faster R-CNN with a ResNet50-FPN backbone for NODE21 lesion localization.
- Trained the detection model for 30 epochs and monitored stable convergence.
- Ran experiments with SLURM on an NVIDIA A100 80 GB GPU.

## Repository features

- `src/metrics.py` implements binary Dice and IoU calculations.
- `src/classification_metrics.py` calculates accuracy, sensitivity, specificity, precision, and F1 from binary predictions.
- `tests/test_metrics.py` checks perfect-overlap and no-overlap cases.
- `hpc/train.slurm` shows the reusable SLURM job structure I used for GPU training.
- `docs/DATA_POLICY.md` explains why medical datasets are not redistributed here.

## Run the code

```bash
python -m pip install -r requirements.txt
pytest
python src/classification_metrics.py labels.csv
```

The classification CSV must contain `target` and `prediction` columns. Dataset-specific training notebooks and model weights will only be added when their sharing terms allow it.

## Tools

Python, PyTorch, U-Net, UPerNet, ResNet-101, Faster R-CNN, ResNet50-FPN, NumPy, OpenCV, DICOM, SLURM, CUDA.

## Author and Project Setting

**Author:** Hritika Adhikary  
**Project:** Graduate Medical Image Analysis Project  
**Institution:** Arizona State University  
**Faculty Advisor:** Dr. Jianming Liang  
**Period:** Fall 2025

## Rights

Copyright (c) 2026 Hritika Adhikary. All rights reserved. See [LICENSE](LICENSE).
