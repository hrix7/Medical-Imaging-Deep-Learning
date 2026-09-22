# Medical Imaging Deep Learning

Reusable foundations and portfolio documentation for chest X-ray segmentation, localization, and detection experiments.

## Included workstreams

- Lung segmentation with U-Net/UPerNet-style models
- Multi-class segmentation
- Abnormality localization and nodule detection
- Faster R-CNN with ResNet50-FPN
- DICOM preprocessing and dataset validation
- SLURM/HPC experiment patterns

Reported course-project results include lung Dice ≈ 0.892, multi-class Dice ≈ 0.788, and localization IoU ≈ 0.745. These values are documented outcomes and are not reproduced by the starter code alone.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest
```

## Data policy

No medical images are included. Obtain datasets from their official sources and follow their licenses, data-use agreements, and de-identification requirements.

## Structure

- `src/metrics.py`: transparent Dice and IoU implementations
- `tests/`: unit tests
- `hpc/`: example SLURM configuration
- `docs/`: dataset and experiment documentation

## Disclaimer

Research and educational code only; not for clinical use.

## License

MIT for repository-authored code and documentation.
