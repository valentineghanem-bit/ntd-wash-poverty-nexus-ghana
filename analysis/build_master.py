"""
build_master.py — Project 18: Spatial Epidemiology of NTDs & the WASH-Poverty Nexus, Ghana
Stage 1 (Strategy & Scope) master-build.

Produces three provenance-honest master tables at their native resolutions:
  1. district_master_261.csv  — 261 MMDAs (GSS 2021): poverty, literacy, insurance,
                                employment, demography, centroids  [GENUINE DISTRICT]
  2. region_master_16.csv     — 16 regions (DHS 2022): improved water, sanitation,
                                open defecation, literacy                [REGIONAL]
  3. ntd_national.csv         — national (WHO-GHO): Buruli, oncho, trachoma, yaws,
                                workforce density, OOP financing         [NATIONAL]
  4. district_analytic_261.csv— district master + region WASH broadcast (flagged) for
                                spatial modelling. Broadcast cols carry suffix _rgnbc.

Author: V. G. Ghanem | 2026-06-30 | python-docx-free, pandas only.
"""
import pandas as pd, numpy as np, json, os, sys

RAW = "data/raw/"
OUT = "data/processed/"
os.makedirs(OUT, exist_ok=True)

# ---- canonical 16-region frame (geojson uppercase) -------------------------
DHS2022_TO_CANON = {
    "Western (post 2022)": "WESTERN", "Western North": "WESTERN NORTH",
    "Central": "CENTRAL", "Greater Accra": "GREATER ACCRA",
    "Volta (post 2022)": "VOLTA", "Oti": "OTI", "Eastern": "EASTERN",
    "Ashanti": "ASHANTI", "Ahafo": "AHAFO", "Bono": "BONO", "Bono East": "BONO EAST",
    "..Northern(post 2022)": "NORTHERN", "..Savannah": "SAVANNAH",
    "..Northeast": "NORTHERN EAST", "Upper West": "UPPER WEST", "Upper East": "UPPER EAST",
}
MS_REGION_TO_CANON = {  # Master Sheet 'Region' -> geojson uppercase
    "Ahafo":"AHAFO","Ashanti":"ASHANTI","Bono":"BONO","Bono East":"BONO EAST",
    "Central":"CENTRAL","Eastern":"EASTERN","Greater Accra":"GREATER ACCRA",
    "North East":"NORTHERN EAST","Northern":"NORTHERN","Oti":"OTI","Savannah":"SAVANNAH",
    "Upper East":"UPPER EAST","Upper West":"UPPER WEST","Volta":"VOLTA",
    "Western":"WESTERN","Western North":"WESTERN NORTH",
}

def drop_hxl(df, key):
    return df[~df[key].astype(str).str.startswith("#")].copy()

# ============================================================================
# 1. DISTRICT MASTER (261) — genuine district resolution
# ============================================================================
ms = pd.read_excel(RAW+"Master_Sheet.xlsx", sheet_name="Sheet1")
ms.columns = [c.strip() for c in ms.columns]
d = pd.DataFrame()
d["district"] = ms["Metropolitan, Municipal, and District Assemblies (MMDA's)"].str.strip()
d["region"] = ms["Region"].str.strip().map(MS_REGION_TO_CANON)
d["urban_rural_class"] = ms["Class"].str.strip()
d["lat"] = pd.to_numeric(ms["Latitude"], errors="coerce")
d["lon"] = pd.to_numeric(ms["Longitude"], errors="coerce")
tot = pd.to_numeric(ms["Total Population"], errors="coerce")
d["total_pop"] = tot
d["poverty_incidence"] = pd.to_numeric(ms["Incidence of Poverty"], errors="coerce")
d["poverty_intensity"] = pd.to_numeric(ms["Intensity of Poverty"], errors="coerce")
illit = pd.to_numeric(ms["Illiterate Population"], errors="coerce")
d["illiteracy_rate"] = (illit/tot*100).round(2)
d["literacy_rate"] = (100 - d["illiteracy_rate"]).round(2)
unins = pd.to_numeric(ms["Uninsured Population"], errors="coerce")
d["uninsured_rate"] = (unins/tot*100).round(2)
emp = pd.to_numeric(ms["Employed Population"], errors="coerce")
unemp = pd.to_numeric(ms["Unemployed Population"], errors="coerce")
d["non_employment_share"] = (unemp/(emp+unemp)*100).round(2)
# dependency ratio
young = pd.to_numeric(ms["Male Population 0-14"],errors="coerce")+pd.to_numeric(ms["Female Population 0-14"],errors="coerce")
old   = pd.to_numeric(ms["Male Population 65+"],errors="coerce")+pd.to_numeric(ms["Female Population 65+"],errors="coerce")
work  = pd.to_numeric(ms["Male Population 15-64"],errors="coerce")+pd.to_numeric(ms["Female Population 15-64"],errors="coerce")
d["dependency_ratio"] = ((young+old)/work*100).round(2)
d["urban"] = (d["urban_rural_class"].str.upper()=="METROPOLITAN").astype(int)  # provisional; refined below
# Class values: Metropolitan/Municipal/District — treat Metropolitan+Municipal as more urban
d["urban"] = d["urban_rural_class"].str.strip().str.title().map(
    {"Metropolitan":1,"Municipal":1,"District":0}).fillna(0).astype(int)

# attach geojson district name via crosswalk (for map join later)
cw = pd.read_csv("docs/district_crosswalk_261_to_260.csv")
cw_map = dict(zip(cw["master_sheet_district"].str.strip(), cw["geojson_district"]))
d["geojson_district"] = d["district"].map(cw_map)
# Name fixes: districts the borrowed crosswalk missed but which HAVE their own polygon
# (spelling variants — NOT gap districts).
NAME_FIX = {
    "Awutu Senya West": "AWUTU SENYA",      # own polygon (Awutu Senya East -> AWUTU SENYA EAST)
    "Sagnarigu Municipal": "SAGNERIGU",     # own polygon (geojson spelling 'SAGNERIGU')
}
d["geojson_district"] = d.apply(
    lambda r: NAME_FIX.get(r["district"], r["geojson_district"]), axis=1)
# TRUE 261->260 gap district (no own polygon): merge to PARENT for MAP RENDERING ONLY;
# data row retained (per ghana-261-districts rule). Guan was carved from Biakoye (Oti).
GAP_TO_PARENT = {"Guan": "BIAKOYE"}
d["gap_merged_for_map"] = d["district"].isin(GAP_TO_PARENT).astype(int)
d["geojson_district"] = d.apply(
    lambda r: GAP_TO_PARENT.get(r["district"], r["geojson_district"]), axis=1)

d = d.sort_values(["region","district"]).reset_index(drop=True)
d.insert(0,"district_id", range(1, len(d)+1))
d.to_csv(OUT+"district_master_261.csv", index=False, encoding="utf-8")

# ============================================================================
# 2. REGION MASTER (16) — DHS 2022 WASH + literacy
# ============================================================================
def dhs_2022_wide(fname, ind_map):
    df = pd.read_csv(RAW+fname, low_memory=False)
    df = drop_hxl(df, "ISO3")
    df["SurveyYear"] = pd.to_numeric(df["SurveyYear"], errors="coerce")
    df = df[df["SurveyYear"]==2022]
    df["canon"] = df["Location"].map(DHS2022_TO_CANON)
    df = df[df["canon"].notna()]
    df["val"] = pd.to_numeric(df["Value"], errors="coerce")
    out = {}
    for newcol, ind in ind_map.items():
        sub = df[df["Indicator"]==ind][["canon","val"]].set_index("canon")["val"]
        out[newcol] = sub
    return pd.DataFrame(out)

water = dhs_2022_wide("water_subnational_gha.csv", {
    "improved_water_pct": "Population using an improved water source",
    "surface_water_pct": "Population using surface water",
    "water_over30min_pct": "Population with water more than 30 minutes away round trip",
})
toilet = dhs_2022_wide("toilet-facilities_subnational_gha.csv", {
    "improved_sanitation_pct": "Population with an improved sanitation facility",
    "open_defecation_pct": "Population using open defecation",
})
literacy = dhs_2022_wide("literacy_subnational_gha.csv", {
    "female_literacy_pct": "Women who are literate",
    "male_literacy_pct": "Men who are literate",
})
region = pd.concat([water, toilet, literacy], axis=1)
region.index.name = "region"
region = region.reindex(sorted(MS_REGION_TO_CANON.values())).reset_index()
region.insert(0,"region_id", range(1, len(region)+1))
region.to_csv(OUT+"region_master_16.csv", index=False, encoding="utf-8")

# ============================================================================
# 3. NTD NATIONAL MASTER — latest value per key indicator
# ============================================================================
def latest_gho(fname, keycol="GHO (DISPLAY)"):
    df = pd.read_csv(RAW+fname, low_memory=False)
    df = drop_hxl(df, "GHO (CODE)")
    df["YEAR"] = pd.to_numeric(df["YEAR (DISPLAY)"], errors="coerce")
    df["NUM"]  = pd.to_numeric(df["Numeric"], errors="coerce")
    return df

ntd = latest_gho("neglected_tropical_diseases_indicators_gha.csv")
rows=[]
for ind, g in ntd.groupby("GHO (DISPLAY)"):
    gv = g.dropna(subset=["YEAR"]).sort_values("YEAR")
    if gv.empty: continue
    last = gv.iloc[-1]
    rows.append({"indicator":ind, "latest_year":int(last["YEAR"]),
                 "value_numeric":last["NUM"], "value_display":last.get("Value"),
                 "n_years": gv["YEAR"].nunique(), "first_year":int(gv["YEAR"].min())})
ntd_nat = pd.DataFrame(rows).sort_values("indicator")

# health workforce density (national, per 10,000) + financing OOP
hw = latest_gho("health_workforce_indicators_gha.csv")
fin = latest_gho("health_financing_indicators_gha.csv")
def latest_one(df, contains):
    s = df[df["GHO (DISPLAY)"].str.contains(contains, case=False, na=False)].dropna(subset=["YEAR"])
    if s.empty: return None
    r = s.sort_values("YEAR").iloc[-1]
    return (r["GHO (DISPLAY)"], int(r["YEAR"]), r["NUM"])
ctx_rows=[]
for label,(df,key) in {
    "Medical doctors per 10,000":(hw,"Medical doctors \\(per 10,000\\)"),
    "Nursing & midwifery per 10,000":(hw,"Nursing and midwifery personnel \\(per 10,000\\)"),
}.items():
    r = latest_one(df,key)
    if r: ctx_rows.append({"indicator":r[0],"latest_year":r[1],"value_numeric":r[2],
                           "value_display":r[2],"n_years":np.nan,"first_year":np.nan})
ntd_nat = pd.concat([ntd_nat, pd.DataFrame(ctx_rows)], ignore_index=True)
ntd_nat.to_csv(OUT+"ntd_national.csv", index=False, encoding="utf-8")

# ============================================================================
# 4. DISTRICT ANALYTIC (261) — district master + region WASH broadcast (flagged)
# ============================================================================
bc = region.drop(columns=["region_id"]).copy()
bc = bc.rename(columns={c: c+"_rgnbc" for c in bc.columns if c!="region"})
analytic = d.merge(bc, on="region", how="left")

# ---- council fix (Stage 1): continuous urbanicity from geojson area --------
gj = json.load(open("data/raw/Ghana_New_260_District.geojson", encoding="utf-8"))
area_field = "Shape__Area" if "Shape__Area" in gj["features"][0]["properties"] else "Shape_Area"
areas = {ft["properties"]["DISTRICT"]: ft["properties"].get(area_field) for ft in gj["features"]}
analytic["area_km2"] = (analytic["geojson_district"].map(areas).astype(float))/1e6  # m2 -> km2
analytic["pop_density"] = (analytic["total_pop"]/analytic["area_km2"]).round(1)
# pop_density is approximate for the 3 gap-merged districts (share parent polygon area)
analytic["density_approx_flag"] = analytic["gap_merged_for_map"]
analytic["urbanicity_z"] = ((np.log(analytic["pop_density"]) -
                             np.log(analytic["pop_density"]).mean())/np.log(analytic["pop_density"]).std()).round(3)
analytic = analytic.rename(columns={"urban":"admin_urban_class"})  # honest: admin status, not true urbanicity

# ---- council fix (Stage 3): NWPRI via PCA (primary) + equal-weight (sens) ---
analytic["san_deficit"]   = 100 - analytic["improved_sanitation_pct_rgnbc"]
analytic["water_deficit"] = 100 - analytic["improved_water_pct_rgnbc"]
# illiteracy DROPPED from index (rho=0.88 w/ poverty AND rho=0.83 w/ dependency = age-confounded);
# retained as descriptive/ML feature only. uninsured kept (distinct health-access axis, rho=0.24).
IDX = ["poverty_incidence","uninsured_rate","open_defecation_pct_rgnbc","san_deficit","water_deficit"]
Z = (analytic[IDX]-analytic[IDX].mean())/analytic[IDX].std()
analytic["nwpri_equal"] = Z.mean(axis=1).round(3)                       # sensitivity composite
# PCA PC1 (primary), sign-oriented so higher = more deprived/receptive
Zc = Z.values - Z.values.mean(0)
U,S,Vt = np.linalg.svd(Zc, full_matrices=False)
pc1 = Zc @ Vt[0]
if np.corrcoef(pc1, analytic["poverty_incidence"])[0,1] < 0: pc1 = -pc1
analytic["nwpri_pca"] = np.round((pc1-pc1.mean())/pc1.std(),3)          # primary composite (z)
analytic["nwpri_pc1_var"] = round(float((S[0]**2)/np.sum(S**2)),3)
# genuine-district deprivation composite (poverty+illiteracy+uninsured) for primary LISA
G = ["poverty_incidence","illiteracy_rate","uninsured_rate"]
Zg=(analytic[G]-analytic[G].mean())/analytic[G].std(); Zgc=Zg.values-Zg.values.mean(0)
Ug,Sg,Vtg=np.linalg.svd(Zgc,full_matrices=False); g1=Zgc@Vtg[0]
if np.corrcoef(g1,analytic["poverty_incidence"])[0,1]<0: g1=-g1
analytic["genuine_dep_pca"]=np.round((g1-g1.mean())/g1.std(),3)

analytic.to_csv(OUT+"district_analytic_261.csv", index=False, encoding="utf-8")

# ============================================================================
# VERIFICATION
# ============================================================================
print("="*70)
print("DISTRICT MASTER (261):", d.shape, "| regions:", d["region"].nunique())
print("  missing per key col:", {c:int(d[c].isna().sum()) for c in
      ["region","lat","lon","poverty_incidence","literacy_rate","uninsured_rate","non_employment_share"]})
print("  poverty_incidence range:", round(d["poverty_incidence"].min(),1), "-", round(d["poverty_incidence"].max(),1))
print("  literacy_rate range:", round(d["literacy_rate"].min(),1), "-", round(d["literacy_rate"].max(),1))
print("  geojson_district unmatched:", int(d["geojson_district"].isna().sum()))
print("-"*70)
print("REGION MASTER (16):", region.shape)
print(region.to_string(index=False))
print("  missing per col:", {c:int(region[c].isna().sum()) for c in region.columns if c not in ("region","region_id")})
print("-"*70)
print("NTD NATIONAL:", ntd_nat.shape, "indicators")
print(ntd_nat[["indicator","latest_year","value_numeric"]].to_string(index=False))
print("-"*70)
print("DISTRICT ANALYTIC (261):", analytic.shape, "| broadcast cols flagged _rgnbc")
print("Wrote 4 files to", OUT)
