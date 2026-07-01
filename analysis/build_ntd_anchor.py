"""
build_ntd_anchor.py — Stage 6: external, disease-ecology-stratified NTD endemicity anchor.

NO sub-national NTD case data exists (Stage 0). This builds a TRANSPARENT, literature-derived
ecological endemicity label per district, with an explicit confidence flag and source. It is an
external validation target — NOT derived from the poverty/WASH data (avoids circularity).

Primary anchor (poverty/WASH-associated, northern/riverine):
  - Onchocerciasis high-risk REGIONS from Ahiadorme, Asori & Manyeh 2026 (BMC Infect Dis,
    doi 10.1186/s12879-026-13415-2): "central-west, Volta Lake area, southwest, central-north".
  - Trachoma HISTORICAL endemic belt (pre-2018 elimination): northern savannah regions.
Contrast overlay (environmental/riverine, southern — NOT poverty-driven):
  - Buruli ulcer DISTRICT foci: Kenu 2014 (Densu R: Ga West/South, Akuapem South, Suhum),
    Ablordey 2015 (Ashanti: Asante Akim North, Amansie West).

Resolution: oncho/trachoma = REGION (broadcast to district, flagged); Buruli = DISTRICT.
Limitation carried explicitly in the manuscript.
"""
import pandas as pd, numpy as np

a = pd.read_csv("data/processed/district_analytic_261.csv")

# --- Onchocerciasis high-risk regions (Ahiadorme 2026 named zones -> canonical regions) ----
ONCHO_HIGH = {  # region : Ahiadorme zone rationale
 "BONO":"central-west","BONO EAST":"central-west / Volta-Lake","AHAFO":"central-west",
 "WESTERN":"southwest","WESTERN NORTH":"southwest",
 "OTI":"Volta-Lake","VOLTA":"Volta-Lake",
 "SAVANNAH":"central-north","NORTHERN":"central-north","NORTHERN EAST":"central-north",
 "UPPER WEST":"central-north","UPPER EAST":"central-north",
}  # lower-risk core: Greater Accra, Central, Eastern, Ashanti
a["oncho_highrisk"] = a["region"].isin(ONCHO_HIGH).astype(int)

# --- Trachoma historical endemic belt (pre-2018 elimination; northern savannah) -----------
TRACHOMA_HIST = {"NORTHERN","NORTHERN EAST","SAVANNAH","UPPER EAST","UPPER WEST"}
a["trachoma_hist_endemic"] = a["region"].isin(TRACHOMA_HIST).astype(int)

# --- PRIMARY poverty/WASH-associated NTD belt = oncho-high OR trachoma-historical ---------
a["ntd_pov_belt"] = ((a["oncho_highrisk"]==1) | (a["trachoma_hist_endemic"]==1)).astype(int)
a["ntd_anchor_resolution"] = "region-broadcast"   # honest flag
a["ntd_anchor_confidence"] = "moderate (literature-ecological)"

# --- Buruli ulcer DISTRICT foci (southern environmental contrast) -------------------------
BURULI_FOCI = {  # geojson_district (uppercase) : source
 "GA WEST MUNICIPAL":"Kenu2014","GA SOUTH MUNICIPAL":"Kenu2014",
 "AKUAPIM SOUTH":"Kenu2014","SUHUM MUNICIPAL":"Kenu2014",
 "ASANTE AKIM NORTH":"Ablordey2015","AMANSIE WEST":"Ablordey2015",
}
# fuzzy contains-match against geojson_district to tolerate naming variants
gd = a["geojson_district"].astype(str).str.upper()
def buruli_hit(name):
    keys=["GA WEST","GA SOUTH","AKWAPEM SOUTH","AKUAPIM SOUTH","AKWAPIM SOUTH",
          "SUHUM","ASANTE AKIM NORTH","AMANSIE WEST"]
    return int(any(k in name for k in keys))
a["buruli_focus"] = gd.map(buruli_hit)

# write to a SEPARATE modeling file (keeps district_analytic_261.csv canonical & idempotent)
a.to_csv("data/processed/district_modeling_261.csv", index=False, encoding="utf-8")

# verification
print("oncho_highrisk districts:", int(a.oncho_highrisk.sum()), "/", len(a),
      f"({a.oncho_highrisk.mean()*100:.0f}%)")
print("trachoma_hist_endemic   :", int(a.trachoma_hist_endemic.sum()))
print("ntd_pov_belt (PRIMARY)  :", int(a.ntd_pov_belt.sum()),
      f"({a.ntd_pov_belt.mean()*100:.0f}%)  -> ML target")
print("buruli_focus districts  :", int(a.buruli_focus.sum()),
      "->", a.loc[a.buruli_focus==1,"district"].tolist())
print("\nntd_pov_belt by zone:")
NORTH={"NORTHERN","NORTHERN EAST","SAVANNAH","UPPER EAST","UPPER WEST"}
a["zone"]=np.where(a.region.isin(NORTH),"North","South")
print(a.groupby("zone")["ntd_pov_belt"].mean().round(2).to_string())
