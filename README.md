# Spatial Epidemiology of Neglected Tropical Diseases and the WASH–Poverty Nexus in Ghana

[![CI](https://github.com/valentineghanem-bit/ntd-wash-poverty-nexus-ghana/actions/workflows/ci.yml/badge.svg)](https://github.com/valentineghanem-bit/ntd-wash-poverty-nexus-ghana/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/) [![ORCID](https://img.shields.io/badge/ORCID-0009--0002--8332--0220-green.svg)](https://orcid.org/0009-0002-8332-0220)

A reproducible, district-level (261 MMDA) analysis of the WASH–poverty **NTD-receptivity** surface across Ghana, its spatial clustering, and an interpretable machine-learning model predicting documented NTD endemicity from socioeconomic determinants.

**Author:** Valentine Golden Ghanem · Ghana COCOBOD Cocoa Clinic, Accra, Ghana; University of Cape Coast (PhD candidate) · ORCID [0009-0002-8332-0220](https://orcid.org/0009-0002-8332-0220) · valentineghanem@gmail.com

## 1. Overview
Neglected tropical diseases (NTDs) are diseases of poverty. This study maps a district-level composite **NTD WASH–Poverty Receptivity Index (NWPRI)**, tests for spatial clustering (Global/Local Moran's I, relative-risk KDE), and asks whether socioeconomic and WASH determinants predict documented NTD endemicity — the socioeconomic layer absent from prior Ghana NTD risk mapping. Findings are framed as a **gradient of WASH/poverty dependence** (direct for trachoma/yaws, poverty-correlated for onchocerciasis, environmental for Buruli ulcer).

## 2. Key findings
- Genuine-district deprivation is strongly spatially clustered (Moran's I = 0.66, p = 0.001); 31 High-High receptivity hotspots in the northern savannah.
- 100% of hotspots fall within the documented onchocerciasis/trachoma poverty-belt (vs 5% of Low-Low districts).
- Socioeconomic determinants predict belt membership at AUC 0.90 (district-only 0.87; permutation p < 0.001), above the environment-only benchmark (0.76).
- Buruli ulcer is a southern environmental exception (median poverty 17.6% vs 33.0% in the belt).

## 3. Data sources
| Source | Level | Use | Access |
|--------|-------|-----|--------|
| Ghana Statistical Service 2021 PHC | District (261) | poverty, literacy, insurance, demography, centroids | [statsghana.gov.gh](https://statsghana.gov.gh) |
| Ghana DHS 2022 (DHS Program) | Region (16) | improved water, sanitation, open defecation | [dhsprogram.com](https://dhsprogram.com) |
| WHO-GHO / WHO-ESPEN | National | NTD endemicity, elimination status, workforce | [espen.afro.who.int](https://espen.afro.who.int) |
| GSS/DHIS2 boundaries | 260 polygons | mapping (261→260 crosswalk) | [statsghana.gov.gh](https://statsghana.gov.gh) |

All sources are public and de-identified. See `data/processed/variable_provenance.csv` (data dictionary).

## 4. Repository structure
```
analysis/     reproducible pipeline (build_master → build_ntd_anchor → spatial_analysis → ml_receptivity → robustness_checks)
data/         raw/ (public inputs) · processed/ (master CSVs + data dictionary)
outputs/      figures/ (300 dpi) · tables/
dashboard/    interactive HI-EI dashboard (self-contained HTML)
poster/       A0 research poster (self-contained HTML)
docs/         crosswalk + technical notes
qa/           Q1 gate, 6-pass QA, QA badge, sync report
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
Poverty incidence, literacy, insurance, non-employment, dependency, urbanicity, log-population (genuine district) + region-broadcast WASH (open defecation, sanitation/water deficit; flagged). NWPRI excluded as a feature.
### 7.3 Models & validation
CART, random forest, L2-logistic under region-blocked stratified spatial cross-validation.
### 7.4 Performance
Logistic AUC 0.90; genuine-district-only 0.87; Brier 0.12; calibrated. Permutation null p < 0.001; south-only AUC 0.74.
### 7.5 Interpretability
SHAP (TreeSHAP); WASH deficits dominate (~79% importance). Poverty/literacy collinearity caveated.
### 7.6 Intended use & caveats
A prioritisation surface for integrated NTD–WASH targeting. **Associational, not causal or individual-level; ecological (MAUP applies).** Buruli ulcer is an environmental exception outside the belt.

## 8. Limitations
NTD anchor is region-resolved and literature-derived (no public district NTD surveillance) → a *receptivity/ecological* study, not district incidence. Region-broadcast WASH inflates autocorrelation (genuine-district measures anchor inference). MAUP applies; cross-sectional; no external temporal validation.

## 8a. Dashboard & poster — view or download
| Artefact | View on GitHub | Live preview | Direct download (raw HTML) |
|----------|----------------|--------------|-----------------------------|
| Interactive dashboard | [View](https://github.com/valentineghanem-bit/ntd-wash-poverty-nexus-ghana/blob/main/dashboard/NTD_WASH_Poverty_Ghana_Dashboard.html) | [Preview](https://htmlpreview.github.io/?https://github.com/valentineghanem-bit/ntd-wash-poverty-nexus-ghana/blob/main/dashboard/NTD_WASH_Poverty_Ghana_Dashboard.html) | [Download](https://raw.githubusercontent.com/valentineghanem-bit/ntd-wash-poverty-nexus-ghana/main/dashboard/NTD_WASH_Poverty_Ghana_Dashboard.html) |
| Conference poster (A0, HTML) | [View](https://github.com/valentineghanem-bit/ntd-wash-poverty-nexus-ghana/blob/main/poster/NTD_WASH_Poverty_Ghana_Poster.html) | [Preview](https://htmlpreview.github.io/?https://github.com/valentineghanem-bit/ntd-wash-poverty-nexus-ghana/blob/main/poster/NTD_WASH_Poverty_Ghana_Poster.html) | [Download](https://raw.githubusercontent.com/valentineghanem-bit/ntd-wash-poverty-nexus-ghana/main/poster/NTD_WASH_Poverty_Ghana_Poster.html) |

> **Tip:** both files are fully self-contained — ECharts and the map geometry are inlined — so they render **offline** with no server. The poster is print-ready at A0 (841 × 1189 mm). Open a downloaded copy with `start dashboard\NTD_WASH_Poverty_Ghana_Dashboard.html` (Windows), `open …` (macOS) or `xdg-open …` (Linux). Built with the bespoke HI-EI pipeline (inline ECharts + inline SVG; supersedes the legacy 60 KB ceiling).

## 9. Ethics
Public, de-identified, aggregate secondary data (WHO-GHO/ESPEN, DHS Program, World Bank, Ghana Statistical Service); no human participants. Exempt from full review under Ghana Health Service Ethics Review Committee guidance on secondary use of anonymised public data.

## 10. Deliverables
Manuscript (not committed, per policy) · interactive dashboard · A0 poster · FAIR master dataset · this repository.

## 11. Citation
Ghanem, V. G. (2026). *Spatial Epidemiology of Neglected Tropical Diseases and the WASH–Poverty Nexus in Ghana.* GitHub. https://github.com/valentineghanem-bit/ntd-wash-poverty-nexus-ghana. See `CITATION.cff`. Archived release DOI via Zenodo (on publication).

## 12. License
Code: MIT. Data/derived outputs: CC-BY-4.0. See `LICENSE`.

## 13. Author & Contact
**Valentine Golden Ghanem**
Ghana COCOBOD Cocoa Clinic, Accra, Ghana; University of Cape Coast (PhD candidate)
Email: valentineghanem@gmail.com
ORCID: [0009-0002-8332-0220](https://orcid.org/0009-0002-8332-0220)

## 14. Acknowledgements
The author thanks WHO-ESPEN, the DHS Program and ICF, and the Ghana Statistical Service for open data. Spatial analysis used esda and libpysal; machine learning used scikit-learn and SHAP with region-blocked spatial cross-validation.
