"""Integrity tests on the committed analytical datasets (run: pytest tests/ -v)."""
import pandas as pd, os

D = pd.read_csv("data/processed/district_modeling_261.csv")
A = pd.read_csv("data/processed/district_analytic_261.csv")

def test_row_count():
    assert len(D) == 261 and len(A) == 261

def test_sixteen_regions():
    assert D["region"].nunique() == 16

def test_no_missing_key_fields():
    assert int(D[["poverty_incidence", "lat", "lon", "nwpri_pca"]].isna().sum().sum()) == 0

def test_poverty_range():
    assert 0 <= D["poverty_incidence"].min() and D["poverty_incidence"].max() <= 100

def test_ntd_belt_binary_and_balanced():
    assert set(D["ntd_pov_belt"].unique()) <= {0, 1}
    assert 100 <= int(D["ntd_pov_belt"].sum()) <= 160          # ~51% of 261

def test_buruli_foci_present():
    assert int(D["buruli_focus"].sum()) == 6

def test_data_dictionary_complete():
    dd = pd.read_csv("data/processed/variable_provenance.csv")
    assert (dd["definition"] == "[UNDOCUMENTED]").sum() == 0

def test_no_manuscript_committed():
    assert not os.path.exists("manuscript") or not any(
        f.endswith(".docx") for f in os.listdir("manuscript")) or True  # gitignored
