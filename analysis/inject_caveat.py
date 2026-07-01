"""inject_caveat.py — add the required ecological/associational caveat + limitations box to the
public-facing dashboard and poster (Q1 §2/§3). Non-destructive to the shared bespoke template.
Resolves the epid-council overclaim flag: 'receptivity' must not read as observed NTD incidence."""
import os

CAVEAT = ('<div style="margin:14px auto;max-width:1100px;padding:12px 16px;border-left:5px solid #117a65;'
 'background:#eafaf4;color:#0b3d2e;font:13px/1.5 system-ui,Segoe UI,Roboto,sans-serif;border-radius:4px;">'
 '<b>Interpretation &amp; limitations.</b> This is an <b>ecological receptivity surface — not observed NTD '
 'incidence.</b> It maps the socio-environmental conditions conducive to NTD transmission and persistence '
 '(poverty and WASH deprivation), validated against a <b>region-resolved, literature-derived NTD endemicity '
 'anchor</b> (WHO-ESPEN and published foci), because district-level NTD surveillance data are not public. '
 'Regional WASH indicators are broadcast to districts. Associations are ecological and correlational — '
 '<b>not causal or individual-level</b> (modifiable areal unit problem applies). Onchocerciasis is '
 'poverty-associated but vector/riverine-driven; Buruli ulcer is an environmental exception outside the '
 'poverty belt.</div>')

for f in ["dashboard/dashboard.html","poster/poster.html"]:
    if not os.path.exists(f): continue
    h=open(f,encoding="utf-8").read()
    if "ecological receptivity surface — not observed" in h:
        print(f"  {f}: caveat already present"); continue
    if "</body>" in h:
        h=h.replace("</body>", CAVEAT+"\n</body>",1)
    else:
        h=h+CAVEAT
    open(f,"w",encoding="utf-8").write(h)
    print(f"  {f}: caveat/limitations box injected ({len(h)//1024}KB)")
