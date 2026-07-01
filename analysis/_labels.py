"""Shared publication labels — maps machine variable/column names to readable labels.
Used by spatial_analysis, ml_receptivity, robustness_checks, assemble_docx so NO raw
snake_case appears in any Q1 figure or table."""
PRETTY = {
 "poverty_incidence":"Poverty incidence (%)","poverty_intensity":"Poverty intensity (%)",
 "uninsured_rate":"Uninsured (%)","non_employment_share":"Non-employment (%)",
 "dependency_ratio":"Dependency ratio (%)","urbanicity_z":"Urbanicity (z)",
 "literacy_rate":"Literacy (%)","illiteracy_rate":"Illiteracy (%)","log_pop":"log(population)",
 "total_pop":"Total population","pop_density":"Population density (/km²)",
 "open_defecation_pct_rgnbc":"Open defecation (%, region)","open_defecation_pct":"Open defecation (%)",
 "san_deficit":"Sanitation deficit (%, region)","water_deficit":"Improved-water deficit (%, region)",
 "improved_sanitation_pct_rgnbc":"Improved sanitation (%, region)","improved_water_pct_rgnbc":"Improved water (%, region)",
 "female_literacy_pct_rgnbc":"Female literacy (%, region)","surface_water_pct":"Surface water (%)",
 "water_over30min_pct":"Water >30 min (%)",
 "genuine_dep_pca":"Deprivation (district PC1)","nwpri_pca":"NWPRI (PC1)","nwpri_equal":"NWPRI (equal-weight)",
 "ntd_pov_belt":"NTD poverty-belt","oncho_highrisk":"Onchocerciasis high-risk","buruli_focus":"Buruli focus",
 # table headers
 "variable":"Variable","morans_I":"Moran's I","E[I]":"E[I]","z":"z","p_sim":"p","primary":"Primary",
 "model":"Model","AUC_pooledOOF":"AUC (pooled OOF)","bal_acc":"Balanced accuracy",
 "sensitivity":"Sensitivity","specificity":"Specificity","Brier":"Brier score",
 "AUC_genuine_only":"AUC (district-only)","feature":"Feature","importance":"Importance",
 "check":"Check","value":"Value","interpretation":"Interpretation",
 "gj":"District","lisa":"LISA cluster","lisa_p_fdr":"FDR p","n":"n","mean":"Mean","sd":"SD",
 "median":"Median","q1":"Q1","q3":"Q3","min":"Min","max":"Max","skew":"Skew","resolution":"Resolution",
 "district":"District","region":"Region",
}
def lab(x): return PRETTY.get(x, x.replace("_"," ").strip().capitalize())
def relabel_cols(df):
    return df.rename(columns={c: PRETTY.get(c, c.replace("_"," ").strip()) for c in df.columns})
