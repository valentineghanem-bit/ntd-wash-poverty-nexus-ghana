"""build_region_config.py — emit 16-region JSON for the bespoke dashboard/poster generator.
v = region mean poverty incidence (%) [NTD-receptivity proxy]; x = region open defecation (%);
lisa = region-level Local Moran's I class on v."""
import warnings; warnings.filterwarnings("ignore")
import pandas as pd, numpy as np, geopandas as gpd, json, os
from libpysal.weights import Queen
from esda.moran import Moran_Local

SHORT={'GREATER ACCRA':'Gr.Accra','ASHANTI':'Ashanti','CENTRAL':'Central','EASTERN':'Eastern','WESTERN':'Western',
 'VOLTA':'Volta','BONO':'Bono','AHAFO':'Ahafo','BONO EAST':'Bono E','OTI':'Oti','WESTERN NORTH':'W.North',
 'UPPER EAST':'Upper East','UPPER WEST':'Upper West','NORTHERN':'Northern','SAVANNAH':'Savannah','NORTHERN EAST':'N.East'}

m=pd.read_csv("data/processed/district_modeling_261.csv")
reg=m.groupby("region").apply(lambda g: pd.Series({
    "poverty": np.average(g.poverty_incidence,weights=g.total_pop),
    "opendef": g.open_defecation_pct_rgnbc.iloc[0],   # region-level (broadcast) value
})).reset_index()

# region polygons -> queen weights -> region LISA on poverty
gdf=gpd.read_file("data/raw/Ghana_New_260_District.geojson")[["REGION","geometry"]]
gdf["REGION"]=gdf["REGION"].str.upper()
rg=gdf.dissolve(by="REGION").reset_index().merge(reg,left_on="REGION",right_on="region",how="inner")
rg=rg.sort_values("REGION").reset_index(drop=True)
W=Queen.from_dataframe(rg,use_index=False); W.transform="r"
lm=Moran_Local(rg["poverty"].values,W,permutations=999,seed=42)
qmap={1:"HH",2:"LH",3:"LL",4:"HL"}
rg["lisa"]=[qmap[q] if p<0.10 else "NS" for q,p in zip(lm.q,lm.p_sim)]  # 0.10 for 16-unit power

out=[]
for _,r in rg.iterrows():
    out.append({"name":r["REGION"],"short":SHORT.get(r["REGION"],r["REGION"]),
                "v":round(float(r["poverty"]),1),"lisa":r["lisa"],"x":round(float(r["opendef"]),1)})
TMP=os.path.expanduser(r"C:/Users/VGhanem/AppData/Local/Temp")
json.dump(out,open(TMP+"/ntd-wash_regions.json","w"),indent=1)
json.dump(out,open("dashboard/ntd-wash_regions.json","w"),indent=1) if os.path.isdir("dashboard") else None
print(f"wrote {len(out)} regions -> {TMP}/ntd-wash_regions.json")
print("LISA classes:", pd.Series([o['lisa'] for o in out]).value_counts().to_dict())
print("poverty range:", min(o['v'] for o in out),"-",max(o['v'] for o in out))
