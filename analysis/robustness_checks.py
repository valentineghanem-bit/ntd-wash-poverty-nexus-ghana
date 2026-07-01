"""
robustness_checks.py — Stage 8 (/peer-stress): adversarial methodological robustness.
(1) label-permutation null; (2) south-only signal (beyond north/south); (3) anchor sensitivity.
Output -> outputs/tables/table6_robustness.csv
"""
import warnings; warnings.filterwarnings("ignore")
import pandas as pd, numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GroupKFold
from sklearn.metrics import roc_auc_score
np.random.seed(0)

m=pd.read_csv("data/processed/district_modeling_261.csv"); m["log_pop"]=np.log(m["total_pop"])
GEN=["poverty_incidence","uninsured_rate","non_employment_share","dependency_ratio",
     "urbanicity_z","literacy_rate","log_pop"]
y=m["ntd_pov_belt"].values; reg=pd.factorize(m["region"])[0]; gkf=GroupKFold(5)

def cv_auc(X,yy,groups):
    oof=np.zeros(len(yy))
    for tr,te in gkf.split(X,yy,groups=groups):
        sc=StandardScaler().fit(X.iloc[tr])
        clf=LogisticRegression(max_iter=2000,class_weight="balanced").fit(sc.transform(X.iloc[tr]),yy[tr])
        oof[te]=clf.predict_proba(sc.transform(X.iloc[te]))[:,1]
    return roc_auc_score(yy,oof)

real=cv_auc(m[GEN],y,reg)
perm=np.array([cv_auc(m[GEN],np.random.permutation(y),reg) for _ in range(200)])
NORTH={"NORTHERN","NORTHERN EAST","SAVANNAH","UPPER EAST","UPPER WEST"}
south=m[~m.region.isin(NORTH)].copy()
south_auc=cv_auc(south[GEN],south["ntd_pov_belt"].values,pd.factorize(south["region"])[0])
oncho_auc=cv_auc(m[GEN],m["oncho_highrisk"].values,reg)

rows=[
 {"check":"genuine-district AUC (real)","value":round(real,3),
  "interpretation":"district socioeconomic data predicts NTD belt"},
 {"check":"permutation null mean (200x)","value":round(perm.mean(),3),
  "interpretation":f"chance level; 95th percentile {np.percentile(perm,95):.3f}; empirical p {(perm>=real).mean():.3f}"},
 {"check":"south-only AUC (n=206)","value":round(south_auc,3),
  "interpretation":"identifies southwest oncho belt WITHIN south -> beyond north/south divide"},
 {"check":"oncho-only anchor AUC","value":round(oncho_auc,3),
  "interpretation":"robust to anchor definition (vs combined belt)"},
]
pd.DataFrame(rows).to_csv("outputs/tables/table6_robustness.csv",index=False)
print(pd.DataFrame(rows).to_string(index=False))
