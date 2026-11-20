# Development log

## 2026-11-19 — Chest X-ray manifest and leakage-checking foundation

Implemented a local, one-finding CSV/provenance audit with explicit positive/negative/uncertain/missing states; patient/study cross-split rejection; study ownership/image identity checks; exact byte and canonical decoded-pixel duplicates; safe root-relative paths; grayscale PNG/JPEG decode/dimension/raw-range checks and resource bounds. Reports omit patient/study IDs and image paths, preserving row-number evidence and source/data/code hashes. Constant images are warnings. Audit success is not training readiness, legal clearance, anonymization or disease performance.

Added original geometric synthetic fixtures, setup/schema/privacy documentation, ordered backlog, dependency declarations (including previously undeclared pandas used by the existing classification CLI), and daily/push/PR read-only GitHub validation with SHA-pinned actions. No patient images, restricted manifests, trained models or hand-entered performance metrics are included. Full tests, independent repeat-fixture audit, syntax and diff checks run before publication; hosted CI is followed after pushing.

Reviewed the four active labs plus signal-processing and tissue repository trees/provenance at exact commits recorded in docs/DATASET_AUDIT.md. They contain generated/illustrative examples or utilities, not a reusable chest X-ray dataset. Reviewed official CheXpert, its linked GitHub test-label release, MIMIC-CXR-JPG and candidate EEG/ECG/gait sources. Documented unresolved access/terms, label semantics, mismatched modalities and missing checksum/adapter work rather than downloading unreviewed data. Other repositories were not modified.

Pre-push validation: 35 tests passed with `python -m pytest -q`; two independently generated synthetic directories produced byte-identical audit JSON; compileall and diff checks passed. actionlint was unavailable; workflow pin/permission/trigger policy tests passed. No real-data download or clinical accuracy evaluation was run.

## 2026-11-20 — Study-label consistency and refreshed dataset inventory

Added a conservative one-finding study-label review gate for simultaneous positive/negative rows, with row-only evidence. Unknown states remain explicit and different studies may differ. Documented legitimate view-specific disagreements and the need to review official annotation granularity rather than automatically reconcile labels. Added six state-pair tests and a longitudinal-study boundary case. Existing tests continue to cover file/pixel duplicates, patient/study leakage, schema/path/decoder failures and deterministic synthetic audits.

Rechecked six current GitHub trees and the four labs' provenance files; updated exact reviewed commits in docs/DATASET_AUDIT.md. Found synthetic/illustrative data and utilities, no reusable chest X-ray images. External access/terms findings remain dated November 19; no acquisition, agreement acceptance, training or clinical metrics. Existing daily read-only workflow and active daily portfolio development already include this track.

Pre-push: full suite 42 passed; independently generated fixtures produce identical audit JSON; Python compilation and git diff checks passed. Workflow trigger/permission/action-pin tests passed. No website interaction changed in this increment.
