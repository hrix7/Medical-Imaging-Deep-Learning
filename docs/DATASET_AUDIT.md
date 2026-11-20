# Repository and dataset audit

Rechecked November 20, 2026 (six repository trees; four synthetic provenance documents). Read-only inspection of the listed default-branch trees and provenance/README files. This is a scoped inventory, not proof that every repository or historical file has been reviewed. No third-party data downloaded or license agreement accepted.

## Existing portfolio repositories

| Repository | Exact reviewed commit | Dataset finding |
|---|---|---|
| [AutoEEG-Research-Lab](https://github.com/hrix7/AutoEEG-Research-Lab) | `8cb0b8dcd810d0ff18e8f0532ef41a946383f4ba` | Generated EEG-like CSV; provenance explicitly says no public/patient data. |
| [CardioAI-Continuous-Benchmark](https://github.com/hrix7/CardioAI-Continuous-Benchmark) | `994697d61eaf0cfeb6400d359fe0f3c16f039fba` | Generated subject RR CSV; not a real ECG dataset. |
| [Biomedical-Digital-Twin](https://github.com/hrix7/Biomedical-Digital-Twin) | `659482b4b984a84f63d90d69bacf83731acae8f6` | Generated Windkessel flow/pressure CSV; not patient measurements. |
| [Wearable-Gait-Fall-Risk-System](https://github.com/hrix7/Wearable-Gait-Fall-Risk-System) | `e65514f74d2dcd74f7f5dcfd125c08a8d37a35dd` | Synthetic acceleration benchmark and teaching examples; not participant recordings. |
| [Biomedical-Signal-Processing](https://github.com/hrix7/Biomedical-Signal-Processing) | `778f359cf2d4a9a6348c3a77e6df7a79e44c7b54` | Signal utilities/input-format documentation; no reusable recording dataset found in current tree. |
| [3D-Pressure-Sore-Tissue-Model](https://github.com/hrix7/3D-Pressure-Sore-Tissue-Model) | `c9210b7a44e82fe03fd55f9f21e87485df088747` | Sanitized example CSV mixing one documented case and illustrative values; not chest X-ray data or a complete FEA export. |

The Medical-Imaging-Deep-Learning repository was inspected before this increment at commit `87b2869e1c9543b779c3618e060b5acbc0102af2`. It supplied metric utilities, tests and an HPC template, not published dataset-specific notebooks, patient images or model weights. Public README historical training numbers are not newly verified results. Other non-BME repositories were listed to locate relevant projects but not exhaustively searched or modified.

Official external dataset-source findings below were reviewed November 19; the November 20 refresh did not re-verify access terms or acquire data.

## Official chest X-ray sources checked

- **CheXpert:** [official Stanford description](https://stanfordmlgroup.github.io/competitions/chexpert/) documents report-derived observations and blank/0/-1/1 label states. It links the current [Stanford AIMI/Redivis distribution](https://stanford.redivis.com/datasets/5yyj-1a9f6ap0x). That distribution page did not expose readable terms to this session; access agreement, precise release and redistribution rights remain unresolved. Do not infer license from a public GitHub README, leaderboard or paper.
- **Official GitHub test-label release:** [rajpurkarlab/cheXpert-test-set-labels](https://github.com/rajpurkarlab/cheXpert-test-set-labels) was reached through Stanford's official page. It describes a released test-set annotation collection and links images separately. This is held-out evaluation material, not a convenient training dataset. No test annotations/images were imported, no thresholds were tuned on them and no license clearance is implied.
- **MIMIC-CXR-JPG 2.1.0:** [official release](https://physionet.org/content/mimic-cxr-jpg/2.1.0/) and [license](https://physionet.org/content/mimic-cxr-jpg/view-license/2.1.0/). The release lists credentialed access, signed DUA, required CITI training and PhysioNet Credentialed Health Data License 1.5.0. Access is not available merely because associated code is public on GitHub. No credentials, agreement acceptance or data acquisition was attempted. Its mapping and official patient/study splits must be reviewed before writing an adapter.

No chest X-ray dataset is selected or cleared for integration yet. No file-level source data checksums have been verified because no real images were acquired. The new tool computes file/pixel checksums for authorized local inputs; this does not substitute for checking an official release checksum manifest. The immediate next step is choosing an accessible release and documenting its precise terms/version/mapping, then implementing a tested adapter without changing uncertainty into negative labels.

## Candidates for the other active projects

These are **candidate extensions**, not integrated datasets or completed real-data benchmarks. Official pages and linked licenses were checked on the date above. Each listed PhysioNet release currently displays open access under Open Data Commons Attribution License v1.0; attribution and other license obligations still apply. Check source files/checksums and subject mappings before ingestion; keep real data and synthetic reports separate.

| Project | Candidate official release | Suitability and remaining work |
|---|---|---|
| EEG | [EEG Motor Movement/Imagery 1.0.0](https://physionet.org/content/eegmmidb/1.0.0/) · [license](https://physionet.org/content/eegmmidb/view-license/1.0.0/) | EEG/subject-grouped recording format requires channel, unit, task and split review. It does not provide the synthetic benchmark's independently known injected-artifact truth or seizure labels. |
| CardioAI | [MIT-BIH Arrhythmia Database 1.0.0](https://physionet.org/content/mitdb/1.0.0/) · [license](https://physionet.org/content/mitdb/view-license/1.0.0/) | Requires a reviewed WFDB/R-peak/annotation-to-RR adapter and patient grouping. Record IDs must not automatically be treated as unique patients. Generator regular/irregular labels are not clinical annotation mappings. |
| Gait | [Gait in Neurodegenerative Disease 1.0.0](https://physionet.org/content/gaitndd/1.0.0/) · [license](https://physionet.org/content/gaitndd/view-license/1.0.0/) | Force-sensitive-resistor signals and derived stride time series, not acceleration magnitude. Useful for a separate stride-analysis extension after subject/units/event mapping review; not direct validation of the synthetic acceleration detector or fall prediction. |
| Digital Twin | No directly suitable paired flow/pressure calibration dataset established in this review | Do not substitute an arbitrary ECG/pressure dataset for the model's required flow/pressure channels, aligned units, initial conditions and consent/access review. Continue synthetic analytic checks until a suitable source is verified. |

The public pages are source evidence; their literature/model scores are not this portfolio's measured performance. No other upstream repository was changed just to record a dataset suggestion. This audit is kept with the chest X-ray foundation so the daily portfolio schedule can follow up coherently.
