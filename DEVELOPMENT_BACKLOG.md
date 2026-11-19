# Chest X-ray development backlog

## Completed — 2026-11-19

- Local image manifest/provenance audit with explicit label states, patient/study split leakage checks, file and decoded-pixel duplicates, image decoding/size/range checks and privacy-conscious reports.
- Original geometric fixture generator, full tests and read-only pinned-action daily/push/PR CI with repeat-audit verification.
- Repository/dataset inventory and official-source candidate review in docs/DATASET_AUDIT.md. No real-data acquisition or disease-performance claims.

## Ordered next work

1. Select an authorized chest X-ray release, complete terms/access/checksum/label review and implement a tested dataset-specific manifest adapter preserving official patient splits and uncertainty/missing states.
2. Add patient-ID mapping validation, label-consistency audit and image near-duplicate candidate review without leaking held-out labels into fitting.
3. Predeclare one finding and a small training-only baseline; use validation for thresholds and keep test data untouched.
4. Add measured per-label confusion, AUROC/AUPRC degeneracy rules and patient-level uncertainty before expanding disease labels.
5. Add verified, permission-cleared chest X-ray data-quality/evaluation views to the existing portfolio website. Generic synthetic score demos are not disease detection.

Keep the other four active labs developing. No paid compute, dataset agreements, restricted images or clinical deployment are authorized by this roadmap alone.
