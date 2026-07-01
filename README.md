# Spatial Epidemiology of Neglected Tropical Diseases and the WASH–Poverty Nexus in Ghana

A reproducible, district-level (261 MMDA) analysis of the WASH–poverty **NTD-receptivity** surface across Ghana, its spatial clustering, and an interpretable machine-learning model predicting documented NTD endemicity from socioeconomic determinants.

![CI](https://github.com/valentineghanem-bit/ntd-wash-poverty-nexus-ghana/actions/workflows/ci.yml/badge.svg)

## 1. Overview
Neglected tropical diseases (NTDs) are diseases of poverty. This study maps a district-level composite **NTD WASH–Poverty Receptivity Index (NWPRI)**, tests for spatial clustering (Global/Local Moran's I, relative-risk KDE), and asks whether socioeconomic and WASH determinants predict documented NTD endemicity — the socioeconomic layer absent from prior Ghana NTD risk mapping. Findings are framed as a **gradient of WASH/poverty dependence** (direct for trachoma/yaws, poverty-correlated for onchocerciasis, environmental for Buruli ulcer).

## 2. Key findings
- Genuine-district deprivation is strongly spatially clustered (Moran's I = 0.66, p = 0.001); 31 High-High receptivity hotspots in the northern savannah.
- 100% of hotspots fall within the documented onchocerciasis/trachoma poverty-belt (vs 5% of Low-Low districts).
- Socioeconomic determinants predict belt membership at AUC 0.90 (district-only 0.87; permutation p < 0.001), above the environment-only benchmark (0.76).
- Buruli ulcer is a southern environmental exception (median poverty 17.6% vs 33.0% in the belt).

## 3. Data sources
| Source | Level | Use |
|--------|-------|-----|
| Ghana Statistical Service 2021 PHC | District (261) | poverty, literacy, insurance, demography, centroids |
| Ghana DHS 2022 (DHS Program) | Region (16) | improved water, sanitation, open defecation |
| WHO-GHO / WHO-ESPEN | National | NTD endemicity, elimination status, workforce |
| GSS/DHIS2 boundaries | 260 polygons | mapping (261→260 crosswalk) |

All sources are public and de-identified. See `data/processed/variable_provenance.csv` (data dictionary).

## 4. Repository structure
```
analysis/     reproducible pipeline (build_master → build_ntd_anchor → spatial_analysis → ml_receptivity → robustness_checks)
data/         raw/ (public inputs) · processed/ (master CSVs + data dictionary)
outputs/      figures/ (300 dpi) · tables/
dashboard/    interactive HI-EI dashboard (dashboard.html)
poster/       A0 research poster (poster.html)
docs/         datalog, methodology, stage records
qa/           Q1 gate, 6-pass QA, council records, QA badge
```

## 5. Reproduce
```bash
pip install -r requirements.txt
bash run_all.sh          # builds masters, anchor, spatial + ML outputs, figures, tables
python qa/q1_gate.py     # manuscript Q1 gate (19 checks)
python qa/qa_6pass.py    # 6-pass QA
```

## 6. Methods
Ecological, cross-sectional, multi-scale design. Queen-contiguity Global Moran's I + FDR-adjusted Local Moran's I; relative-risk (Kelsall–Diggle) KDE; CART / random forest / L2-logistic under **region-blocked stratified spatial cross-validation**; SHAP; label-permutation null. Reporting per STROBE, RECORD and TRIPOD+AI.

## 7. Machine-learning model card
### 7.1 Target
Documented poverty-associated NTD-endemic district (onchocerciasis/trachoma belt) — an external, literature/ESPEN-derived anchor, not disease incidence.
### 7.2 Predictors
Poverty incidence, literacy, insurance, non-employment, dependency, urbanicity, log-population (genuine district) + region-broadcast WASH (open defecation, sanitation/water deficit; flagged). NWPRI excluded as a feature (no leakage).
### 7.3 Models & validation
CART, random forest, L2-logistic under **region-blocked stratified spatial cross-validation** (held-out region groups).
### 7.4 Performance
Logistic AUC 0.90; genuine-district-only 0.87; Brier 0.12; calibrated. Permutation null p < 0.001; south-only AUC 0.74 (signal beyond north/south).
### 7.5 Interpretability
SHAP (TreeSHAP); WASH deficits dominate (~79% importance). Poverty/literacy collinearity caveated.
### 7.6 Intended use & caveats
A prioritisation surface for integrated NTD–WASH targeting. **Associational, not causal or individual-level; ecological (MAUP applies).** Buruli ulcer is an environmental exception outside the belt.

## 8. Limitations
NTD anchor is region-resolved and literature-derived (no public district NTD surveillance) → a *receptivity/ecological* study, not district incidence. Region-broadcast WASH inflates autocorrelation (genuine-district measures anchor inference). MAUP applies; cross-sectional; no external temporal validation.

## 8a. Asset registry
| Asset | Path |
|-------|------|
| Interactive dashboard | `dashboard/dashboard.html` |
| A0 research poster | `poster/poster.html` |
| Master analytic dataset | `data/processed/district_analytic_261.csv` |
| Modeling dataset (with NTD anchor) | `data/processed/district_modeling_261.csv` |
| Data dictionary | `data/processed/variable_provenance.csv` |
| Figures (300 dpi) | `outputs/figures/fig2–fig8_*.png` |
| Result tables | `outputs/tables/table1–table6_*.csv` |
| QA badge | `qa/QA_PASSED_2026-06-30.txt` |

## 9. Ethics
Public, de-identified, aggregate secondary data; no human participants. Exempt from full review under Ghana Health Service Ethics Review Committee guidance.

## 10. Deliverables
Manuscript (not committed, per policy) · interactive dashboard · A0 poster · FAIR master dataset · this repository.

## 11. Citation
See `CITATION.cff`. Archived release DOI via Zenodo (on publication).

## 12. License
Code: MIT. Data/derived outputs: CC-BY-4.0. See `LICENSE`.

## 13. Author
Valentine Golden Ghanem — COCOBOD / University of Cape Coast. ORCID: (to add).

## 14. Acknowledgements
WHO-ESPEN, the DHS Program, and the Ghana Statistical Service for open data.
