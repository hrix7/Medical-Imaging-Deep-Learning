"""Local PNG/JPEG manifest audit. No downloads, split assignment or model fitting."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import warnings
import numpy as np
from PIL import Image

COLUMNS = ['image_id', 'patient_id', 'study_id', 'path', 'split', 'view', 'label']
LABELS = ('negative', 'positive', 'uncertain', 'missing')
SPLITS = ('train', 'validation', 'test')
VIEWS = ('PA', 'AP', 'LATERAL', 'UNKNOWN')
IDENTIFIER = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,127}\Z')
META_KEYS = {'dataset_id', 'version', 'source_url', 'license', 'data_kind', 'target_name'}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_source(path: Path) -> tuple[dict, str]:
    raw = path.read_bytes()
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate provenance key')
            result[key] = value
        return result
    meta = json.loads(raw, object_pairs_hook=unique)
    if not isinstance(meta, dict) or set(meta) != META_KEYS:
        raise ValueError('Exact provenance fields required')
    if any(not isinstance(v, str) or not v.strip() or v != v.strip() for v in meta.values()):
        raise ValueError('Nonempty provenance strings without surrounding whitespace required')
    if meta['data_kind'] not in ('synthetic', 'public') or not meta['source_url'].startswith('https://'):
        raise ValueError('Explicit synthetic/public kind and HTTPS source URL required')
    return meta, sha256(raw)


def read_rows(path: Path) -> tuple[list[dict], str]:
    raw = path.read_bytes()
    reader = csv.DictReader(io.StringIO(raw.decode('utf-8-sig'), newline=''))
    if reader.fieldnames != COLUMNS:
        raise ValueError('Exact ordered CSV columns required: ' + ','.join(COLUMNS))
    rows = list(reader)
    if not rows:
        raise ValueError('Manifest must contain at least one image')
    return rows, sha256(raw)


def local_path(root: Path, relative: str) -> Path:
    p = PurePosixPath(relative)
    if not relative or '\\' in relative or ':' in relative or p.is_absolute() or '..' in p.parts or p.as_posix() != relative:
        raise ValueError('Normalized root-relative POSIX path required')
    resolved = (root / relative).resolve(strict=True)
    if not resolved.is_relative_to(root) or not resolved.is_file():
        raise ValueError('Regular image file inside data root required')
    return resolved


def inspect_image(path: Path, max_pixels: int, max_bytes: int) -> dict:
    if path.stat().st_size > max_bytes:
        raise ValueError('Image exceeds file-size limit')
    raw = path.read_bytes()
    with warnings.catch_warnings():
        warnings.simplefilter('error', Image.DecompressionBombWarning)
        with Image.open(io.BytesIO(raw)) as image:
            if image.format not in ('PNG', 'JPEG') or image.mode not in ('L', 'I;16', 'I;16L', 'I;16B'):
                raise ValueError('Only grayscale 8/16-bit PNG or grayscale JPEG supported')
            width, height = image.size
            if width * height > max_pixels:
                raise ValueError('Image exceeds pixel-count limit')
            image.verify()
        with Image.open(io.BytesIO(raw)) as image:
            pixels = np.asarray(image)
            if pixels.ndim != 2 or pixels.dtype.kind not in 'ui' or pixels.min() < 0 or pixels.max() > 65535:
                raise ValueError('Finite unsigned grayscale samples required')
            # Canonical integer samples, dimensions and byte order: catches re-encoding.
            decoded = width.to_bytes(8, 'big') + height.to_bytes(8, 'big') + pixels.astype('<u2').tobytes()
            return dict(width=width, height=height, minimum=int(pixels.min()), maximum=int(pixels.max()),
                        file_sha256=sha256(raw), pixel_sha256=sha256(decoded))


def audit(manifest: Path, source: Path, data_root: Path, *, max_pixels=16_777_216, max_bytes=100_000_000) -> dict:
    if type(max_pixels) is not int or type(max_bytes) is not int or min(max_pixels, max_bytes) < 1:
        raise ValueError('Positive integer image resource limits required')
    meta, source_hash = read_source(source)
    rows, manifest_hash = read_rows(manifest)
    root = data_root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError('Image root must be a directory')
    issues, quality = [], []
    groups = {k: defaultdict(list) for k in ('image_id', 'patient_id', 'study_id', 'file_sha256', 'pixel_sha256')}
    inspections = []
    counts = {split: Counter({label: 0 for label in LABELS}) for split in SPLITS}
    def issue(code, indices):
        issues.append(dict(code=code, rows=sorted(indices)))
    for index, row in enumerate(rows, start=2):
        if set(row) != set(COLUMNS) or any(not isinstance(v, str) or not v or v != v.strip() for v in row.values()):
            issue('malformed_row', [index]); continue
        if any(not IDENTIFIER.fullmatch(row[key]) for key in ('image_id', 'patient_id', 'study_id')):
            issue('invalid_identifier', [index]); continue
        if row['split'] not in SPLITS or row['view'] not in VIEWS or row['label'] not in LABELS:
            issue('invalid_split_view_or_label', [index]); continue
        counts[row['split']][row['label']] += 1
        for key in ('image_id', 'patient_id', 'study_id'):
            groups[key][row[key]].append((index, row['split'], row['patient_id']))
        try:
            path = local_path(root, row['path'])
            info = inspect_image(path, max_pixels, max_bytes)
        except (OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning, SyntaxError):
            # Never include source paths/identifiers or decoder messages in reports.
            issue('unreadable_unsupported_or_outside_root_image', [index]); continue
        inspections.append(dict(row=index, **info))
        for key in ('file_sha256', 'pixel_sha256'):
            groups[key][info[key]].append((index, row['split'], row['patient_id']))
        if info['minimum'] == info['maximum']:
            quality.append(dict(code='constant_image', rows=[index]))
    for key in ('image_id', 'patient_id', 'study_id', 'file_sha256', 'pixel_sha256'):
        for records in groups[key].values():
            indices = [r[0] for r in records]
            if key == 'image_id' and len(records) > 1:
                issue('duplicate_image_id', indices)
            if key == 'study_id' and len({r[2] for r in records}) > 1:
                issue('study_assigned_to_multiple_patients', indices)
            if key in ('patient_id', 'study_id') and len({r[1] for r in records}) > 1:
                issue(key + '_cross_split_leakage', indices)
            if key in ('file_sha256', 'pixel_sha256') and len(records) > 1:
                issue('duplicate_' + key.removesuffix('_sha256'), indices)
    issues.sort(key=lambda i: (i['code'], i['rows']))
    return dict(schema_version=1, data_kind=meta['data_kind'], target_name=meta['target_name'],
                passed=not issues, training_readiness='not_assessed', rows=len(rows), decoded_images=len(inspections),
                split_label_counts={k: dict(v) for k, v in counts.items()},
                provenance=dict(dataset_id=meta['dataset_id'], version=meta['version'], source_sha256=source_hash,
                                manifest_sha256=manifest_hash, validator_sha256=sha256(Path(__file__).read_bytes())),
                images=inspections, issues=issues, quality_warnings=quality,
                limitations=['Declared patient/study IDs must come from a reviewed dataset mapping; identifiers cannot prove identity.',
                             'Exact file and decoded-pixel duplicates only; crops, resizes and near-duplicates are not detected.',
                             'PNG/JPEG only; no DICOM handling or burned-in identifier screening.',
                             'Declared labels and provenance are not verified clinical truth or license approval.',
                             'Quality warnings are engineering checks, not validated clinical image-quality assessment.'])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--data-root', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = audit(args.manifest, args.source, args.data_root)
    except (OSError, ValueError):
        parser.exit(2, 'Invalid manifest, provenance or data-root input; no identifiers are logged.\n')
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
