# Chest X-ray manifest and split-integrity gate

Implemented November 19, 2026. This is data plumbing for future chest X-ray work, not a trained disease detector. The generated examples are geometric gradients, not synthetic anatomy or patient radiographs. Existing historical README scores remain historical and are not results of this pipeline.

## Setup and reproduce

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
python scripts/build_cxr_fixture.py data/synthetic-cxr
mkdir -p outputs
python -m src.cxr_manifest data/synthetic-cxr/manifest.csv \
  --source data/synthetic-cxr/source.json --data-root data/synthetic-cxr \
  > outputs/cxr-audit.json
```

The same fixture and audit repeated in the same environment must produce identical JSON. The daily, push and pull-request GitHub workflow runs the full tests and repeats this check; it uploads only a synthetic aggregate/image-hash report. It never downloads real datasets, fits models or pushes code. Daily source development remains handled by the existing portfolio automation.

## Exact CSV contract

`image_id,patient_id,study_id,path,split,view,label`

- IDs must be nonempty dataset-provided **pseudonymous** IDs using letters/digits/underscore/dot/hyphen, at most 128 characters. Never put names, birth dates or hospital record numbers here. This validator does not anonymize data.
- A manifest describes one dataset release and **one explicitly named finding**. Multilabel import is future work; do not collapse multiple findings into this one label field.
- Splits: `train`, `validation`, `test`. The tool audits declared splits; it does not reassign official splits or select a test set.
- Views: `PA`, `AP`, `LATERAL`, `UNKNOWN`. Unknown view is explicit rather than inferred from image pixels.
- Labels: `positive`, `negative`, `uncertain`, `missing`. Blank, numeric or ambiguous labels fail. An adapter must explicitly map its reviewed dataset definition; no default uncertain/missing-to-negative conversion exists.
- Paths are normalized, root-relative POSIX paths. Absolute paths, traversal, Windows paths and symlinks escaping the root fail. Only local grayscale PNG (8/16-bit) or grayscale JPEG is supported. DICOM, RGB and conversion/windowing are out of scope.

Provenance JSON requires exactly `dataset_id`, `version`, `source_url` (HTTPS), `license`, `data_kind` (`synthetic` or `public`), and `target_name`, all explicit nonempty strings. This records declarations and hashes; it does not certify legal clearance. Dataset import must separately document access terms, mapping, checksums and patient grouping before use.

## What fails

- Any patient or study appearing in more than one split; any study assigned to different patients.
- Repeated image IDs; exact file-byte duplicates or identical decoded integer pixels, including losslessly re-encoded PNGs with different file hashes. Duplicates are rejected even within a split to avoid unnoticed duplicate weighting.
- Missing/corrupt/unsupported images, malformed schema or labels, unsafe paths, images over default limits (16,777,216 pixels or 100,000,000 bytes). Python API resource limits may be set explicitly and must be positive integers.

Multiple different images/views in one patient/study **within the same split** are allowed. One or two splits may be absent for a partial audit; the output is not a training-readiness approval.

## Outputs and interpretation

Exit 0: checks passed. Exit 1: report contains violations. Exit 2: invalid input schema/provenance/root. Reports include manifest/provenance/validator SHA-256, image byte and canonical decoded-pixel SHA-256, dimensions, raw integer min/max, per-split label-state counts and row-number issue groups. They omit patient/study IDs and source image paths. A constant image raises a quality warning without fabricating a clinical quality judgment.

`passed: true` only means these checks passed. `training_readiness` always remains `not_assessed`. No observed disease accuracy, sensitivity or AUROC is generated here.

## Limits and privacy

Declared patient IDs can be wrong, and near-duplicate crops/resizes, lossy re-encodings, unknown cross-dataset patient overlap and label leakage are not detected. No burned-in text/identifier inspection, DICOM metadata parsing, image orientation correction, calibration, official split validation or clinical validation is performed. Raw integer ranges are not normalized and must not be compared across bit depths as physiological quantities.

Real manifests, hashes and reports can remain sensitive/linkable. Keep them under ignored `data/` or `outputs/` outside public commits; ignore rules do not anonymize content or prevent force-add. Review provenance strings and reports before any sharing. Only generated test fixtures run in CI. Public-image integration remains a separate, documented data-access step.

## Study-label review gate (November 20)

For this one-finding manifest, a study containing both definitive `positive` and `negative` rows now fails with `study_conflicting_definitive_labels` and the implicated CSV row numbers. This is a conservative review gate, not proof that annotations are erroneous: image-level labels across different views can legitimately disagree. Review the official annotation granularity and mapping before adapting those datasets; do not silently vote, overwrite labels or relabel held-out images to pass. Uncertain/missing rows are excluded from this definitive-conflict comparison and remain counted in their own states. Different studies belonging to the same patient may have different labels within a split. Patient/study split-leakage checks still apply independently.
