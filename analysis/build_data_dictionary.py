"""build_data_dictionary.py — FAIR data dictionary (variable_provenance.csv) for the master dataset.
One row per variable: definition, source, survey/year, units, resolution, range, transform."""
import pandas as pd, numpy as np

META = {  # variable : (definition, source, survey/year, units, resolution, transform)
 "district_id":("Sequential district identifier","Derived","2026","integer","district","assigned"),
 "district":("MMDA name (Metropolitan/Municipal/District Assembly)","Ghana Statistical Service","2021 PHC","text","district","—"),
 "region":("Administrative region (16, post-2022)","Ghana Statistical Service","2021 PHC","text","region","mapped to geojson"),
 "geojson_district":("Matched 260-polygon district name (map join)","GSS/DHIS2 boundary set","2022","text","district","crosswalk; 3 gap districts→parent"),
 "gap_merged_for_map":("Flag: district merged to parent polygon for mapping only","Derived","2026","0/1","district","—"),
 "urban_rural_class":("MMDA administrative class (Metropolitan/Municipal/District)","GSS","2021 PHC","category","district","—"),
 "admin_urban_class":("Administrative-urban flag (Metro/Municipal=1)","GSS","2021 PHC","0/1","district","binary map"),
 "urbanicity_z":("Urbanicity = standardised log population density","Derived (GSS + geojson area)","2021/2022","z-score","district","log then z"),
 "pop_density":("Population per km²","GSS + geojson area","2021/2022","persons/km²","district","total_pop/area"),
 "area_km2":("District polygon area","GSS/DHIS2 boundary set","2022","km²","district","m²→km²"),
 "lat":("District centroid latitude","GSS","2021 PHC","degrees","district","—"),
 "lon":("District centroid longitude","GSS","2021 PHC","degrees","district","—"),
 "total_pop":("Total population","GSS","2021 PHC","persons","district","—"),
 "poverty_incidence":("Multidimensional poverty incidence (Alkire-Foster)","GSS","2021 PHC","%","district","—"),
 "poverty_intensity":("Multidimensional poverty intensity (Alkire-Foster)","GSS","2021 PHC","%","district","—"),
 "illiteracy_rate":("Illiterate population share (whole-population; age-confounded)","GSS","2021 PHC","%","district","illiterate/total×100"),
 "literacy_rate":("Population literacy proxy","GSS","2021 PHC","%","district","100−illiteracy"),
 "uninsured_rate":("Uninsured population share (NHIS non-enrolment)","GSS","2021 PHC","%","district","uninsured/total×100"),
 "non_employment_share":("Non-employed share of labour-force-classified population (NOT ILO unemployment)","GSS","2021 PHC","%","district","unemployed/(emp+unemp)×100"),
 "dependency_ratio":("Age dependency ratio ((0-14 + 65+)/15-64)","GSS","2021 PHC","%","district","—"),
 "improved_water_pct_rgnbc":("Population using an improved water source (region, broadcast)","DHS Program","GDHS 2022","%","region→district","region value broadcast"),
 "improved_sanitation_pct_rgnbc":("Population with improved sanitation (region, broadcast)","DHS Program","GDHS 2022","%","region→district","broadcast"),
 "open_defecation_pct_rgnbc":("Population practising open defecation (region, broadcast)","DHS Program","GDHS 2022","%","region→district","broadcast"),
 "san_deficit":("Sanitation deficit = 100 − improved sanitation","DHS Program","GDHS 2022","%","region→district","100−improved"),
 "water_deficit":("Improved-water deficit = 100 − improved water","DHS Program","GDHS 2022","%","region→district","100−improved"),
 "female_literacy_pct_rgnbc":("Adult women literate (region, broadcast)","DHS Program","GDHS 2022","%","region→district","broadcast"),
 "nwpri_pca":("NTD WASH-Poverty Receptivity Index (PCA PC1, primary)","Derived","2026","z-score","district","PCA of 5 components"),
 "nwpri_equal":("NWPRI equal-weighted z-score (sensitivity)","Derived","2026","z-score","district","mean of z"),
 "genuine_dep_pca":("Genuine-district deprivation composite (PC1 of poverty/illiteracy/uninsured)","Derived","2026","z-score","district","PCA"),
 "ntd_pov_belt":("Documented poverty-associated NTD belt (oncho/trachoma), external anchor","WHO-ESPEN + literature (Ahiadorme 2026)","2024-2026","0/1","region→district","literature-ecological"),
 "oncho_highrisk":("Onchocerciasis high-risk region (Ahiadorme 2026 zones)","Literature","2026","0/1","region→district","mapped"),
 "buruli_focus":("Documented Buruli ulcer district focus (environmental)","Kenu 2014; Ablordey 2015","2014-2015","0/1","district","literature"),
 "ntd_anchor_resolution":("Resolution flag of NTD anchor","Derived","2026","text","—","—"),
 "ntd_anchor_confidence":("Confidence flag of NTD anchor","Derived","2026","text","—","—"),
 "surface_water_pct_rgnbc":("Population using surface water (region, broadcast)","DHS Program","GDHS 2022","%","region→district","broadcast"),
 "water_over30min_pct_rgnbc":("Population >30 min round-trip to water (region, broadcast)","DHS Program","GDHS 2022","%","region→district","broadcast"),
 "male_literacy_pct_rgnbc":("Adult men literate (region, broadcast)","DHS Program","GDHS 2022","%","region→district","broadcast"),
 "density_approx_flag":("Flag: pop density approximate (gap district shares parent area)","Derived","2026","0/1","district","—"),
 "nwpri_pc1_var":("Variance explained by NWPRI PC1","Derived","2026","proportion","dataset","PCA"),
 "trachoma_hist_endemic":("Historical trachoma endemic belt (pre-2018 elimination)","WHO 2018 + literature","2018","0/1","region→district","literature"),
}
df=pd.read_csv("data/processed/district_modeling_261.csv")
rows=[]
for c in df.columns:
    if c not in META:
        rows.append({"variable":c,"definition":"[UNDOCUMENTED]","source":"?","survey_year":"?",
                     "units":"?","resolution":"?","range":"","transform":"?"}); continue
    de,so,yr,un,rez,tr=META[c]
    s=pd.to_numeric(df[c],errors="coerce")
    rng=f"{s.min():.2f}–{s.max():.2f}" if s.notna().sum() and s.dtype!=object else \
        (f"{df[c].nunique()} categories" if df[c].dtype==object else "")
    rows.append({"variable":c,"definition":de,"source":so,"survey_year":yr,"units":un,
                 "resolution":rez,"range":rng,"transform":tr,"missing":int(df[c].isna().sum())})
dd=pd.DataFrame(rows)
dd.to_csv("data/processed/variable_provenance.csv",index=False,encoding="utf-8")
undoc=dd[dd.definition=="[UNDOCUMENTED]"]["variable"].tolist()
print(f"data dictionary: {len(dd)} variables documented -> data/processed/variable_provenance.csv")
print("undocumented:", undoc if undoc else "none")
print("total missing across dataset:", int(df.isna().sum().sum()))
