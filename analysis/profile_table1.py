"""profile_table1.py — Stage 1 descriptive profiling + Table 1 for Project 18."""
import pandas as pd, numpy as np
from scipy import stats
OUT="outputs/tables/"
import os; os.makedirs(OUT, exist_ok=True)

a = pd.read_csv("data/processed/district_analytic_261.csv")

VARS = {
 "poverty_incidence":"Poverty incidence (%)",
 "poverty_intensity":"Poverty intensity (%)",
 "literacy_rate":"Literacy rate (%)",
 "uninsured_rate":"Uninsured (%)",
 "non_employment_share":"Non-employment share (%)",
 "dependency_ratio":"Dependency ratio (%)",
 "improved_water_pct_rgnbc":"Improved water (%, region)",
 "improved_sanitation_pct_rgnbc":"Improved sanitation (%, region)",
 "open_defecation_pct_rgnbc":"Open defecation (%, region)",
 "female_literacy_pct_rgnbc":"Female literacy (%, region)",
 "total_pop":"Total population",
}
rows=[]
for c,label in VARS.items():
    s = pd.to_numeric(a[c],errors="coerce").dropna()
    sk = stats.skew(s)
    rows.append({"variable":label,"n":len(s),"mean":round(s.mean(),2),"sd":round(s.std(),2),
                 "median":round(s.median(),2),"q1":round(s.quantile(.25),2),"q3":round(s.quantile(.75),2),
                 "min":round(s.min(),2),"max":round(s.max(),2),"skew":round(sk,2),
                 "resolution":"district" if not c.endswith("_rgnbc") else "region-broadcast"})
t1 = pd.DataFrame(rows)
t1.to_csv(OUT+"table1_district_descriptives.csv",index=False,encoding="utf-8")
print("=== TABLE 1 — district analytic frame (n=261) ===")
print(t1.to_string(index=False))

# urban vs rural split on genuine-district vars
print("\n=== Urban (Metro/Municipal) vs Rural (District) — genuine district vars ===")
for c in ["poverty_incidence","literacy_rate","uninsured_rate","non_employment_share"]:
    u=a[a.admin_urban_class==1][c]; r=a[a.admin_urban_class==0][c]
    t,p=stats.mannwhitneyu(u.dropna(),r.dropna())
    print(f"  {c:20s} urban={u.median():5.1f} rural={r.median():5.1f}  MWU p={p:.4g}")

# macro-zone (North = savannah belt) descriptive
NORTH={"NORTHERN","NORTHERN EAST","SAVANNAH","UPPER EAST","UPPER WEST"}
a["zone"]=np.where(a.region.isin(NORTH),"North (savannah)","South (forest/coastal)")
print("\n=== North vs South poverty & WASH (median) ===")
print(a.groupby("zone")[["poverty_incidence","literacy_rate","open_defecation_pct_rgnbc",
      "improved_sanitation_pct_rgnbc"]].median().round(1).to_string())

# top/bottom poverty districts
print("\n=== Highest-poverty districts ===")
print(a.nlargest(6,"poverty_incidence")[["district","region","poverty_incidence","literacy_rate"]].to_string(index=False))
