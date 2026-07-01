"""
ml_receptivity.py — Stage 6: ML prediction of documented NTD poverty-belt from WASH-poverty
determinants (the socioeconomic layer Ahiadorme 2026 omitted). Non-circular: target = external
NTD anchor; NWPRI excluded as a feature. Region-blocked spatial CV. CART/RF/logistic + SHAP.
"""
import warnings; warnings.filterwarnings("ignore")
import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GroupKFold
from sklearn.metrics import (roc_auc_score,balanced_accuracy_score,recall_score,
                             brier_score_loss,roc_curve)
from sklearn.calibration import calibration_curve
np.random.seed(42)
FIG="outputs/figures/"; TAB="outputs/tables/"
import os; [os.makedirs(p,exist_ok=True) for p in (FIG,TAB)]

m=pd.read_csv("data/processed/district_modeling_261.csv")
m["log_pop"]=np.log(m["total_pop"])
FEATURES=["poverty_incidence","uninsured_rate","non_employment_share","dependency_ratio",
          "urbanicity_z","literacy_rate","log_pop",
          "open_defecation_pct_rgnbc","san_deficit","water_deficit"]
y=m["ntd_pov_belt"].values
X=m[FEATURES].copy()

# region-blocked spatial CV: 16 regions -> 5 grouped spatial folds
regions=m["region"].values
reg_codes=pd.factorize(regions)[0]
gkf=GroupKFold(n_splits=5)

models={
 "CART":DecisionTreeClassifier(max_depth=4,min_samples_leaf=12,random_state=42,class_weight="balanced"),
 "Random Forest":RandomForestClassifier(n_estimators=600,max_depth=None,min_samples_leaf=4,
                                        random_state=42,class_weight="balanced",n_jobs=-1),
 "Logistic (L2)":LogisticRegression(max_iter=2000,class_weight="balanced"),
}
rows=[]; roc_store={}; cal_store={}
for name,clf in models.items():
    bas=[];sens=[];specs=[];briers=[];oof=np.zeros(len(y));oofp=np.zeros(len(y))
    for tr,te in gkf.split(X,y,groups=reg_codes):
        Xtr,Xte=X.iloc[tr],X.iloc[te]
        if name=="Logistic (L2)":
            sc=StandardScaler().fit(Xtr); Xtr=sc.transform(Xtr); Xte=sc.transform(Xte)
        clf.fit(Xtr,y[tr]); p=clf.predict_proba(Xte)[:,1]; pred=(p>=0.5).astype(int)
        oof[te]=pred; oofp[te]=p
        bas.append(balanced_accuracy_score(y[te],pred))
        sens.append(recall_score(y[te],pred,pos_label=1)); specs.append(recall_score(y[te],pred,pos_label=0))
        briers.append(brier_score_loss(y[te],p))
    # region-blocked folds can be single-class -> per-fold AUC undefined; use POOLED out-of-fold AUC
    pooled_auc=roc_auc_score(y,oofp)
    rows.append({"model":name,"AUC_pooledOOF":f"{pooled_auc:.3f}",
                 "bal_acc":f"{np.mean(bas):.3f}±{np.std(bas):.3f}",
                 "sensitivity":f"{np.mean(sens):.3f}","specificity":f"{np.mean(specs):.3f}",
                 "Brier":f"{np.mean(briers):.3f}","AUC_mean":pooled_auc})
    roc_store[name]=(y.copy(),oofp.copy()); cal_store[name]=(y.copy(),oofp.copy())
res=pd.DataFrame(rows).sort_values("AUC_mean",ascending=False)
res.drop(columns="AUC_mean").to_csv(TAB+"table4_ml_performance.csv",index=False)
print("=== ML performance (region-blocked spatial CV, 5 folds) ===")
print(res.drop(columns="AUC_mean").to_string(index=False))
best=res.iloc[0]["model"]; print("\nBest model:",best)

# ---- council Stage-6 fix: GENUINE-DISTRICT-ONLY model (no broadcast WASH) -------------
# isolates the truly district-level predictive contribution from the region-level WASH signal.
GENUINE=["poverty_incidence","uninsured_rate","non_employment_share","dependency_ratio",
         "urbanicity_z","literacy_rate","log_pop"]
Xg=m[GENUINE]
grows=[]
for name,clf in models.items():
    oofp=np.zeros(len(y))
    for tr,te in gkf.split(Xg,y,groups=reg_codes):
        Xt,Xv=Xg.iloc[tr],Xg.iloc[te]
        if name=="Logistic (L2)":
            sc=StandardScaler().fit(Xt); Xt=sc.transform(Xt); Xv=sc.transform(Xv)
        clf.fit(Xt,y[tr]); oofp[te]=clf.predict_proba(Xv)[:,1]
    grows.append({"model":name,"AUC_genuine_only":round(roc_auc_score(y,oofp),3)})
gdf_=pd.DataFrame(grows).sort_values("AUC_genuine_only",ascending=False)
gdf_.to_csv(TAB+"table4b_ml_genuine_district_only.csv",index=False)
print("\n=== Genuine-district-only ML (no broadcast WASH; region-blocked CV) ===")
print(gdf_.to_string(index=False))

# ---- fit best (RF) on full data for SHAP + importance --------------------------------
from _labels import lab as _lab0
rf=models["Random Forest"].fit(X,y)
imp=pd.DataFrame({"feature":[_lab0(f) for f in FEATURES],
                  "importance":rf.feature_importances_.round(3)}).sort_values("importance",ascending=False)
imp.to_csv(TAB+"table5_feature_importance.csv",index=False)
print("\n=== RF feature importance ===\n",imp.to_string(index=False))

# SHAP — robust 2D positive-class matrix + readable feature names
try:
    import shap
    from _labels import lab
    Xp=X.rename(columns={c:lab(c) for c in X.columns})
    expl=shap.TreeExplainer(rf); sv=expl.shap_values(X)
    sv1 = sv[1] if isinstance(sv,list) else (sv[:,:,1] if getattr(sv,"ndim",2)==3 else sv)
    assert sv1.shape==Xp.shape, f"SHAP shape {sv1.shape} != X {Xp.shape}"
    plt.figure(figsize=(7.5,5))
    shap.summary_plot(sv1,Xp,show=False,max_display=10,plot_type="dot",color_bar_label="Feature value")
    plt.xlabel("SHAP value (impact on NTD poverty-belt prediction)",fontsize=10)
    plt.tight_layout(); plt.savefig(FIG+"fig7_shap_summary.png",dpi=300,bbox_inches="tight"); plt.close()
    print(f"SHAP figure written (matrix {sv1.shape}, {Xp.shape[1]} features).")
except Exception as e:
    print("SHAP FAILED:",e); raise

# ---- Fig 6: ROC + calibration ---------------------------------------------------------
fig,(ax1,ax2)=plt.subplots(1,2,figsize=(11,4.5))
OK={"CART":("#0072B2","-"),"Random Forest":("#E69F00","--"),"Logistic (L2)":("#009E73","-.")}  # Okabe-Ito
for name,(yt,pp) in roc_store.items():
    fpr,tpr,_=roc_curve(yt,pp); col,ls=OK.get(name,("#000","-"))
    ax1.plot(fpr,tpr,color=col,linestyle=ls,lw=2,label=f"{name} (AUC = {roc_auc_score(yt,pp):.2f})")
ax1.plot([0,1],[0,1],":",color="#888"); ax1.set_xlabel("1 − specificity"); ax1.set_ylabel("Sensitivity")
ax1.set_title("ROC (out-of-fold, region-blocked CV)"); ax1.legend(fontsize=8,loc="lower right")
yt,pp=cal_store[best]; frac,mean=calibration_curve(yt,pp,n_bins=8)
ax2.plot(mean,frac,"o-",color="#0072B2",label=best); ax2.plot([0,1],[0,1],":",color="#888",label="Perfect calibration")
ax2.set_xlabel("Mean predicted probability"); ax2.set_ylabel("Observed fraction"); ax2.set_title("Calibration")
ax2.legend(fontsize=8,loc="upper left")
fig.savefig(FIG+"fig6_roc_calibration.png",dpi=300,bbox_inches="tight"); plt.close(fig)

# ---- Fig 8: CART tree (interpretable) — readable feature names ------------------------
from _labels import lab as _lab
cart=models["CART"].fit(X,y)
fig,ax=plt.subplots(figsize=(14,7.5))
plot_tree(cart,feature_names=[_lab(f) for f in FEATURES],class_names=["Non-belt","NTD belt"],
          filled=True,rounded=True,fontsize=7,impurity=False,proportion=True,ax=ax)
fig.savefig(FIG+"fig8_cart_tree.png",dpi=300,bbox_inches="tight"); plt.close(fig)

# ---- Buruli contrast (disease-ecology check) -----------------------------------------
bf=m[m.buruli_focus==1]; belt=m[m.ntd_pov_belt==1]
print(f"\n=== Disease-ecology contrast ===")
print(f"Poverty incidence — Buruli foci (south): median {bf.poverty_incidence.median():.1f}% "
      f"vs NTD poverty-belt: {belt.poverty_incidence.median():.1f}% vs national {m.poverty_incidence.median():.1f}%")
print(f"Buruli foci in poverty-belt: {bf.ntd_pov_belt.mean()*100:.0f}%  (low => environmentally driven, not poverty)")
print("\nFigures:",sorted([f for f in os.listdir(FIG) if f.endswith('.png')]))
