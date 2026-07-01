"""
spatial_analysis.py — Stage 6: spatial epidemiology of the WASH-poverty NTD-receptivity surface.
Queen-contiguity Moran's I + FDR-LISA + poverty-weighted KDE + choropleths + NTD overlay.
Outputs -> outputs/figures/ (PNG, colourblind-safe) and outputs/tables/ (CSV).
"""
import warnings; warnings.filterwarnings("ignore")
import pandas as pd, numpy as np, geopandas as gpd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from libpysal.weights import Queen, KNN
from libpysal.weights.util import attach_islands
from esda.moran import Moran, Moran_Local
from scipy.stats import gaussian_kde
np.random.seed(42)

FIG="outputs/figures/"; TAB="outputs/tables/"
import os; [os.makedirs(p,exist_ok=True) for p in (FIG,TAB)]

# ---- load + merge analytic to 260 polygons (population-weighted for 3 gap districts) -----
gdf = gpd.read_file("data/raw/Ghana_New_260_District.geojson")[["DISTRICT","geometry"]]
gdf["DISTRICT"]=gdf["DISTRICT"].str.upper()
m = pd.read_csv("data/processed/district_modeling_261.csv")
m["gj"]=m["geojson_district"].str.upper()
WMEAN=["nwpri_pca","genuine_dep_pca","poverty_incidence","open_defecation_pct_rgnbc",
       "san_deficit","water_deficit","uninsured_rate","literacy_rate"]
MAXAGG=["ntd_pov_belt","buruli_focus","oncho_highrisk"]
def wmean(g,c):
    w=g["total_pop"]; return np.average(g[c],weights=w) if w.sum()>0 else g[c].mean()
rows=[]
for gj,g in m.groupby("gj"):
    r={"gj":gj}
    for c in WMEAN: r[c]=wmean(g,c)
    for c in MAXAGG: r[c]=int(g[c].max())
    r["total_pop"]=g["total_pop"].sum(); r["n_mmda"]=len(g)
    rows.append(r)
poly=gpd.GeoDataFrame(pd.DataFrame(rows).merge(gdf,left_on="gj",right_on="DISTRICT",how="left"),
                      geometry="geometry",crs=gdf.crs)
print("polygons:",len(poly),"| unmatched geom:",int(poly.geometry.isna().sum()))

# ---- spatial weights: Queen contiguity; attach islands via nearest neighbour ------------
Wq=Queen.from_dataframe(poly,use_index=False)
if len(Wq.islands):
    W=attach_islands(Wq, KNN.from_dataframe(poly,k=1))   # connect island polygons (coastal/lake)
    print(f"attached {len(Wq.islands)} island(s) via nearest neighbour")
else:
    W=Wq
W.transform="r"
print("avg neighbours:",round(W.mean_neighbors,2),"| islands:",len(W.islands))

# ---- Global Moran's I --------------------------------------------------------------------
from _labels import lab as _lab
mi=[]
for c in ["genuine_dep_pca","nwpri_pca","poverty_incidence","open_defecation_pct_rgnbc",
          "san_deficit","uninsured_rate"]:
    mc=Moran(poly[c].values,W,permutations=999)
    mi.append({"variable":_lab(c),"morans_I":round(mc.I,3),"E[I]":round(mc.EI,3),
               "z":round(mc.z_sim,2),"p_sim":round(mc.p_sim,3),
               "primary":"Yes" if c=="genuine_dep_pca" else ""})
mi=pd.DataFrame(mi); mi.to_csv(TAB+"table2_global_morans_i.csv",index=False)
print("\n=== Global Moran's I ===\n",mi.to_string(index=False))

# ---- LISA (primary: genuine_dep_pca), FDR-adjusted -------------------------------------
PRIM="genuine_dep_pca"
lm=Moran_Local(poly[PRIM].values,W,permutations=999,seed=42)
from statsmodels.stats.multitest import multipletests
sig=multipletests(lm.p_sim,alpha=0.05,method="fdr_bh")[0]
qlab={1:"High-High",2:"Low-High",3:"Low-Low",4:"High-Low"}
poly["lisa"]=np.where(sig,[qlab.get(q,"NS") for q in lm.q],"Not significant")
poly["lisa_p_fdr"]=multipletests(lm.p_sim,alpha=0.05,method="fdr_bh")[1].round(4)
lisa_counts=poly["lisa"].value_counts()
print("\n=== LISA clusters (genuine deprivation, FDR<0.05) ===\n",lisa_counts.to_string())
# HH hotspot districts table (readable)
hh=poly[poly.lisa=="High-High"][["gj","genuine_dep_pca","poverty_incidence","ntd_pov_belt"]].copy()
hh=hh.sort_values("genuine_dep_pca",ascending=False)
hh["gj"]=hh["gj"].str.title()
hh["genuine_dep_pca"]=hh["genuine_dep_pca"].round(2); hh["poverty_incidence"]=hh["poverty_incidence"].round(1)
hh["ntd_pov_belt"]=hh["ntd_pov_belt"].map({1:"Yes",0:"No"})
hh.to_csv(TAB+"table3_lisa_HH_hotspots.csv",index=False)
poly[["gj","lisa","lisa_p_fdr","genuine_dep_pca","nwpri_pca","ntd_pov_belt","buruli_focus"]].to_csv(
    TAB+"table3_lisa_full.csv",index=False)

# ---- overlay concordance: LISA HH vs documented NTD poverty-belt ------------------------
hh_in_belt=poly[(poly.lisa=="High-High")]["ntd_pov_belt"].mean()
ll_in_belt=poly[(poly.lisa=="Low-Low")]["ntd_pov_belt"].mean()
print(f"\nConcordance: HH receptivity hotspots in documented NTD poverty-belt = {hh_in_belt*100:.0f}%")
print(f"            LL (low-receptivity) in NTD poverty-belt              = {ll_in_belt*100:.0f}%")

# ============================ FIGURES (colourblind-safe) ================================
def save(fig,name): fig.savefig(FIG+name,dpi=300,bbox_inches="tight"); plt.close(fig)
def north_arrow(ax):
    ax.annotate("N",xy=(0.94,0.95),xytext=(0.94,0.86),xycoords="axes fraction",
                ha="center",va="center",fontsize=11,fontweight="bold",
                arrowprops=dict(arrowstyle="-|>",color="#333",lw=1.6))

# Fig 2 — NWPRI receptivity choropleth
fig,ax=plt.subplots(figsize=(7,8))
poly.plot(column="nwpri_pca",scheme="quantiles",k=5,cmap="YlOrBr",legend=True,
          edgecolor="white",linewidth=0.2,ax=ax,
          legend_kwds={"title":"NWPRI (z)\nquintiles","loc":"lower left","fontsize":8})
ax.set_title("NTD WASH–Poverty Receptivity Index across 261 Ghanaian districts",fontsize=11,weight="bold")
north_arrow(ax); ax.axis("off"); save(fig,"fig2_nwpri_choropleth.png")

# Fig 3 — LISA cluster map (explicit legend handles so the key always renders)
import matplotlib.patches as mpatch
cmap_lisa={"High-High":"#b2182b","Low-Low":"#2166ac","High-Low":"#ef8a62",
           "Low-High":"#67a9cf","Not significant":"#e0e0e0"}
fig,ax=plt.subplots(figsize=(7,8))
for lab,col in cmap_lisa.items():
    sub=poly[poly.lisa==lab]
    if len(sub): sub.plot(ax=ax,color=col,edgecolor="white",linewidth=0.2)
handles=[mpatch.Patch(facecolor=col,edgecolor="#999",label=f"{lab} (n={(poly.lisa==lab).sum()})")
         for lab,col in cmap_lisa.items() if (poly.lisa==lab).sum()>0]
ax.legend(handles=handles,title="LISA cluster (FDR < 0.05)",loc="lower left",fontsize=8,title_fontsize=9,frameon=True)
ax.set_title("Local clusters of NTD receptivity (Local Moran's I)",fontsize=11,weight="bold")
north_arrow(ax); ax.axis("off"); save(fig,"fig3_lisa_clusters.png")

# Fig 4 — RELATIVE-RISK kernel density (Kelsall-Diggle): poverty-weighted / unweighted.
# Removes the centroid-sampling-density artefact so the surface reflects poverty INTENSITY,
# not where districts happen to be small/dense. Masked to the populated interior.
cent=m.dropna(subset=["lon","lat"]).copy()
xy=np.vstack([cent["lon"],cent["lat"]]); wts=cent["poverty_incidence"].values
kde_w=gaussian_kde(xy,weights=wts); kde_u=gaussian_kde(xy)
xmin,xmax=cent.lon.min()-0.2,cent.lon.max()+0.2; ymin,ymax=cent.lat.min()-0.2,cent.lat.max()+0.2
xx,yy=np.mgrid[xmin:xmax:240j,ymin:ymax:240j]
grid=np.vstack([xx.ravel(),yy.ravel()])
du=kde_u(grid); dw=kde_w(grid)
rr=np.where(du>np.percentile(du,35), dw/du, np.nan).reshape(xx.shape)  # mask only sparse exterior
fig,ax=plt.subplots(figsize=(7,8))
poly.boundary.plot(ax=ax,color="#888",linewidth=0.3)
cf=ax.contourf(xx,yy,rr,levels=12,cmap="YlOrBr",alpha=0.8)
plt.colorbar(cf,ax=ax,shrink=0.5,label="Relative poverty intensity (weighted / unweighted KDE)")
ax.set_title("Relative-risk kernel density of poverty intensity",fontsize=11,weight="bold")
ax.set_xlim(xmin,xmax); ax.set_ylim(ymin,ymax); ax.axis("off"); save(fig,"fig4_kde_poverty.png")
pk=np.unravel_index(np.nanargmax(rr),rr.shape)
print(f"KDE relative-risk peak at lat {yy[pk]:.2f}, lon {xx[pk]:.2f} (north if lat>9)")

# Fig 5 — overlay: LISA HH hotspots vs documented NTD poverty-belt + Buruli foci
fig,ax=plt.subplots(figsize=(7,8))
poly.plot(ax=ax,color="#f7f7f7",edgecolor="#ccc",linewidth=0.2)
poly[poly.ntd_pov_belt==1].plot(ax=ax,color="#fdd0a2",edgecolor="white",linewidth=0.2,label="Documented NTD poverty-belt")
poly[poly.lisa=="High-High"].boundary.plot(ax=ax,color="#b2182b",linewidth=1.1)
poly[poly.buruli_focus==1].plot(ax=ax,color="#1b7837",edgecolor="k",linewidth=0.3,label="Buruli focus (environmental)")
import matplotlib.patches as mp
hand=[mp.Patch(color="#fdd0a2",label="NTD poverty-belt (oncho/trachoma)"),
      mp.Patch(edgecolor="#b2182b",facecolor="none",label="LISA HH receptivity hotspot"),
      mp.Patch(color="#1b7837",label="Buruli focus (south, environmental)")]
ax.legend(handles=hand,loc="lower left",fontsize=8)
ax.set_title("Spatial overlay: receptivity hotspots vs documented NTD endemicity",fontsize=11,weight="bold")
north_arrow(ax); ax.axis("off"); save(fig,"fig5_ntd_overlay.png")

print("\nFigures written:",sorted([f for f in os.listdir(FIG) if f.endswith('.png')]))
poly.drop(columns="geometry").to_csv(TAB+"polygon_level_260.csv",index=False)
