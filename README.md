# Spatial epidemiology of neglected tropical diseases and the WASH–poverty nexus in Ghana

**Ecological receptivity mapping and an interpretable machine-learning model across 261 districts**

[![CI](https://github.com/valentineghanem-bit/ntd-wash-poverty-nexus-ghana/actions/workflows/ci.yml/badge.svg)](https://github.com/valentineghanem-bit/ntd-wash-poverty-nexus-ghana/actions/workflows/ci.yml)
&nbsp;Reporting: STROBE + RECORD + TRIPOD+AI &nbsp;·&nbsp; License: MIT &nbsp;·&nbsp; [ORCID 0009-0002-8332-0220](https://orcid.org/0009-0002-8332-0220)

---

## 1. Overview

This repository contains the full, reproducible analysis behind an ecological study of the water,
sanitation and hygiene (WASH)–poverty nexus underlying neglected tropical diseases (NTDs) across **all 261
districts of Ghana**. Using the 2021 Ghana Population and Housing Census (district-level poverty, literacy,
insurance; 261 districts) linked to the 2022 Ghana Demographic and Health Survey (region-level WASH; 16
regions) and WHO-GHO/ESPEN national NTD data, it builds a district **NTD WASH–Poverty Receptivity Index
(NWPRI)**, characterises its spatial structure, and tests whether socioeconomic determinants predict
documented NTD endemicity — the socioeconomic layer absent from prior Ghana NTD risk mapping. The design is
explicitly **ecological** and methodologically candid: *receptivity* denotes conditions conducive to NTD
transmission, not observed incidence; WASH is region-resolved and broadcast to districts, so district
poverty/literacy anchor inference.

**Author:** Valentine Golden Ghanem · Ghana COCOBOD Cocoa Clinic, Accra, Ghana · ORCID 0009-0002-8332-0220.

## 2. Key findings

- District deprivation was strongly spatially clustered (**Global Moran's I = 0.66, z = 15.9, p = 0.001**),
  with **31 High-High LISA receptivity hotspots** forming a contiguous northern savannah block.
- A marked **North–South gradient**: northern-belt districts averaged 44.7% poverty, 70.6% open defecation
  and 49.0% literacy versus 23.6%, 9.3% and 76.5% in the south.
- **100% of High-High hotspots fell within the documented onchocerciasis/trachoma poverty-belt** versus 5%
  of Low-Low districts — the receptivity surface recovers NTD geography from socioeconomic data alone.
- Under region-blocked spatial cross-validation, **logistic regression (AUC 0.90; district-data-only 0.87,
  permutation p < 0.001; south-only 0.74)** predicted belt membership, exceeding the environment-only Ghana
  benchmark (0.76); WASH deficits dominated the predictors.
- **Buruli ulcer is a southern environmental exception** (median district poverty 17.6% vs 33.0% in the
  belt; 0% within it) — WASH/poverty dependence is a gradient, not a uniform nexus.

## 3. Study design

Cross-sectional, ecological (small-area), multi-scale study; **261 districts of Ghana**. Reporting follows
STROBE (observational studies), RECORD (routinely-collected health data) and TRIPOD+AI (prediction model).
The modelled construct is district NTD *receptivity*; the external outcome anchor is the documented
poverty-associated NTD belt (onchocerciasis/trachoma), region-resolved and literature/ESPEN-derived because
district-level NTD surveillance is not public. Ecological fallacy, the modifiable areal unit problem (MAUP),
and region-broadcast WASH inflating autocorrelation are declared limitations.

## 4. Data sources

| Source | Unit | Used for |
|---|---|---|
| 2021 Ghana Population & Housing Census (GSS) | District (261) | Poverty incidence/intensity, illiteracy, uninsured, employment, age structure, centroids |
| 2022 Ghana DHS (StatCompiler) | Region (16) | Improved water, improved sanitation, open defecation, literacy |
| WHO-GHO / WHO-ESPEN | Country | NTD endemicity, elimination status, treatment coverage, workforce (context + anchor) |
| 2022 district boundaries (GSS/DHIS2) | 260 polygons | Choropleth + spatial weights (261→260 crosswalk; Guan the sole gap) |

All inputs are public and de-identified; the linked analytical dataset is included under `data/processed/`.

## 5. Repository structure

```
.
├── data/
│   ├── raw/          public inputs (WHO-GHO/ESPEN CSVs, DHS subnational, GSS Master Sheet, boundary GeoJSON)
│   └── processed/    district_master_261 · district_analytic_261 · district_modeling_261 (with NTD anchor)
│                     · region_master_16 · ntd_national · variable_provenance.csv (data dictionary)
├── analysis/         build_master · build_ntd_anchor · build_data_dictionary · spatial_analysis
│                     · ml_receptivity · robustness_checks · profile_table1 · _labels
├── outputs/          figures/ (fig2–fig8, 300 dpi) · tables/ (table1–table6)
├── dashboard/        NTD_WASH_Poverty_Ghana_Dashboard.html (self-contained, inline ECharts)
├── poster/           NTD_WASH_Poverty_Ghana_Poster.html (A0 conference poster)
├── docs/             district_crosswalk_261_to_260.csv + technical notes
├── tests/            test_master_csv.py (8 tests)
├── qa/               q1_gate.py · qa_6pass.py · QA_PASSED_2026-06-30.txt · SYNC_REPORT
├── .github/workflows/ci.yml
├── CITATION.cff · LICENSE · README.md · requirements.txt · run_all.sh · .gitignore
```

## 6. Methods / pipeline

1. **Master datasets** (`build_master.py`) — GSS census → 261-district poverty/literacy/insurance/demography
   + centroids; DHS 2022 → 16-region WASH; NWPRI via PCA (PC1); genuine-district vs region-broadcast flagged.
2. **NTD anchor** (`build_ntd_anchor.py`) — external, disease-ecology-stratified endemicity label
   (oncho/trachoma poverty belt; Buruli southern foci) — the ML target, not derived from the predictors.
3. **Spatial** (`spatial_analysis.py`) — queen contiguity; Global Moran's I; FDR-adjusted Local Moran's I;
   relative-risk (Kelsall–Diggle) KDE; choropleths; NTD overlay (999 permutations).
4. **Machine learning** (`ml_receptivity.py`) — CART, random forest, L2-logistic on determinant features
   (NWPRI excluded, leakage-guarded); **region-blocked stratified spatial CV**; AUC, sensitivity, specificity,
   Brier + calibration; SHAP; a genuine-district-only model isolates the true district signal.
5. **Robustness + descriptives** (`robustness_checks.py`, `profile_table1.py`) — permutation null,
   south-only test, anchor sensitivity; Table 1.

## 7. Reproducibility

```bash
pip install -r requirements.txt          # CI-installable (Python 3.11+)
bash run_all.sh                          # build masters → anchor → dictionary → spatial → ML → robustness → Table 1
python qa/q1_gate.py                     # 19-check manuscript Q1 gate
python qa/qa_6pass.py                    # 6-pass QA
pytest tests/ -v                          # 8 dataset-integrity tests
```

Random seed fixed at `SEED = 42`. Software: Python 3.11, pandas, GeoPandas, libpysal, esda, scikit-learn,
SHAP, statsmodels. Continuous integration (`.github/workflows/ci.yml`) installs dependencies, compiles all
scripts, rebuilds the datasets, and runs the test suite.

## 8. Outputs

- `data/processed/district_modeling_261.csv` — analytical dataset (261 rows, NTD anchor + NWPRI).
- `outputs/figures/` — NWPRI choropleth, LISA cluster map, relative-risk KDE, NTD overlay, ROC/calibration,
  SHAP summary, CART tree (fig2–fig8, 300 dpi, colourblind-safe).
- `outputs/tables/` — Table 1 (descriptives), Global Moran's I, LISA hotspots, ML performance,
  feature importance, robustness checks.

## 9. Dashboard & poster — view or download

Both are self-contained offline HTML files (**inline ECharts + inline map geometry** — no CDN, no server).

| Artefact | View on GitHub | Live preview | Direct download (raw HTML) |
|---|---|---|---|
| Interactive dashboard | [View](https://github.com/valentineghanem-bit/ntd-wash-poverty-nexus-ghana/blob/main/dashboard/NTD_WASH_Poverty_Ghana_Dashboard.html) | [Preview](https://htmlpreview.github.io/?https://github.com/valentineghanem-bit/ntd-wash-poverty-nexus-ghana/blob/main/dashboard/NTD_WASH_Poverty_Ghana_Dashboard.html) | [Download](https://raw.githubusercontent.com/valentineghanem-bit/ntd-wash-poverty-nexus-ghana/main/dashboard/NTD_WASH_Poverty_Ghana_Dashboard.html) |
| Conference poster (A0, HTML) | [View](https://github.com/valentineghanem-bit/ntd-wash-poverty-nexus-ghana/blob/main/poster/NTD_WASH_Poverty_Ghana_Poster.html) | [Preview](https://htmlpreview.github.io/?https://github.com/valentineghanem-bit/ntd-wash-poverty-nexus-ghana/blob/main/poster/NTD_WASH_Poverty_Ghana_Poster.html) | [Download](https://raw.githubusercontent.com/valentineghanem-bit/ntd-wash-poverty-nexus-ghana/main/poster/NTD_WASH_Poverty_Ghana_Poster.html) |

> **Tip:** both files are fully self-contained — ECharts and the map geometry are inlined — so they render **offline** with no server or network. The poster is print-ready at A0 (841 × 1189 mm). Open a downloaded copy with `start dashboard\NTD_WASH_Poverty_Ghana_Dashboard.html` (Windows), `open …` (macOS) or `xdg-open …` (Linux). Built with the bespoke HI-EI pipeline (inline ECharts + inline SVG; supersedes the legacy 60 KB ceiling).

## 10. Data dictionary

See [`data/processed/variable_provenance.csv`](data/processed/variable_provenance.csv) — definition, source,
survey/year, units, resolution, range and transform for all 40 variables of the analytical dataset,
including the ecological-unit note (genuine-district vs region-broadcast fields).

## 11. Analytical verification

- `pytest tests/` — 8 checks on the committed dataset (261 rows, 16 regions, no missing key fields, poverty
  bounds, binary/balanced NTD belt, 6 Buruli foci, complete data dictionary).
- `python qa/q1_gate.py` — 19-check Q1 gate (300 dpi figures, embedded readable tables, ≥35 Vancouver refs,
  reporting statements). `python qa/qa_6pass.py` — 8-panel QA; badge [`qa/QA_PASSED_2026-06-30.txt`](qa/QA_PASSED_2026-06-30.txt).
- Dashboard + poster render verified headlessly (Playwright/Chrome). All headline numbers (0.66, 0.90, 31,
  100%) reconciled across dataset, dashboard and poster.

## 12. Citation

See [`CITATION.cff`](CITATION.cff). Ghanem VG. *Spatial epidemiology of neglected tropical diseases and the
WASH–poverty nexus in Ghana: ecological receptivity mapping and an interpretable machine-learning model
across 261 districts.* 2026. ORCID 0009-0002-8332-0220. **Target journal:** *PLOS Neglected Tropical
Diseases* / *Infectious Diseases of Poverty* (Q1).

## 13. License & ethics

MIT License (see [`LICENSE`](LICENSE)); source datasets retain their original terms. Secondary analysis of
de-identified, publicly available aggregate data (WHO-GHO/ESPEN, DHS Program, GSS); a consent waiver
applies (Ghana Health Service Ethics Review Committee guidance on secondary use of anonymised public data).

## 14. Acknowledgements & contact

WHO-ESPEN, the DHS Program and ICF, and the Ghana Statistical Service for open data; WHO Global Health
Observatory. Spatial analysis used esda and libpysal; machine learning used scikit-learn and SHAP.
Contact: Valentine Golden Ghanem — valentineghanem@gmail.com · ORCID 0009-0002-8332-0220.
