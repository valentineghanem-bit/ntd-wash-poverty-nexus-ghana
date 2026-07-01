#!/usr/bin/env bash
set -euo pipefail
python analysis/build_master.py
python analysis/build_ntd_anchor.py
python analysis/build_data_dictionary.py
python analysis/spatial_analysis.py
python analysis/ml_receptivity.py
python analysis/robustness_checks.py
python analysis/profile_table1.py
echo "Pipeline complete: masters, anchor, spatial + ML outputs, figures, tables."

# --- dashboard + poster (separate bespoke/node step) ---
# python analysis/build_region_config.py                       # emit 16-region config
# node ../_system/bespoke/bespoke_gen.js ntd-wash              # generate dashboard.html + poster.html
# python analysis/inject_caveat.py                             # MANDATORY: add ecological/limitations box
