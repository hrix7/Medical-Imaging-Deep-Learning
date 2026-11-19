# Development log

## 2026-11-19 — Chest X-ray manifest and leakage-checking foundation

Implemented a local, one-finding CSV/provenance audit with explicit positive/negative/uncertain/missing states; patient/study cross-split rejection; study ownership/image identity checks; exact byte and canonical decoded-pixel duplicates; safe root-relative paths; grayscale PNG/JPEG decode/dimension/raw-range checks and resource bounds. Reports omit patient/study IDs and image paths, preserving row-number evidence and source/data/code hashes. Constant images are warnings. Audit success is not training readiness, legal clearance, anonymization or disease performance.

Added original geometric synthetic fixtures, setup/schema/privacy documentation, ordered backlog, dependency declarations (including previously undeclared pandas used by the existing classification CLI), and daily/push/PR read-only GitHub validation with SHA-pinned actions. No patient images, restricted manifests, trained models or hand-entered performance metrics are included. Full tests, independent repeat-fixture audit, syntax and diff checks run before publication; hosted CI is followed after pushing.

Reviewed the four active labs plus signal-processing and tissue repository trees/provenance at exact commits recorded in docs/DATASET_AUDIT.md. They contain generated/illustrative examples or utilities, not a reusable chest X-ray dataset. Reviewed official CheXpert, its linked GitHub test-label release, MIMIC-CXR-JPG and candidate EEG/ECG/gait sources. Documented unresolved access/terms, label semantics, mismatched modalities and missing checksum/adapter work rather than downloading unreviewed data. Other repositories were not modified.

Pre-push validation: 35 tests passed with `python -m pytest -q`; two independently generated synthetic directories produced byte-identical audit JSON; compileall and diff checks passed. actionlint was unavailable; workflow pin/permission/trigger policy tests passed. No real-data download or clinical accuracy evaluation was run.
