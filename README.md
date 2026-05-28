https://alpr-surveillance-dashboard-axawcpzaowmvest455ladk.streamlit.app/

# 1 — Public Safety Technology in Chicago

This folder contains a Streamlit dashboard for mapping recorded ALPR camera locations in Chicago and comparing community-level camera concentration with socioeconomic indicators.

## Files
- `app.py` — Streamlit dashboard
- `requirements.txt` — Python dependencies
- `data/` — cleaned dashboard data
- `assets/dashboard_screenshot.png` — screenshot for the README

## Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Data
- `data/chicago-alprs.csv` — recorded ALPR camera point locations
- `data/community_boundaries.csv` — Chicago community area boundary source data
- `data/communities.geojson` — GeoJSON version of the community boundaries used for mapping
- `data/socioeconomic_indicators.csv` — selected socioeconomic indicators by community area

## Dashboard
The dashboard includes:
- an ALPR camera point map
- side-by-side community maps for camera concentration and socioeconomic context
- a hardship/camera quadrant scatter plot
- a proportional symbol map
- an operator composition chart
- a ranked chart of high-exposure community areas
- a selected community explorer

## Notes
The dashboard maps recorded camera presence, not how camera data is stored, shared, or used after collection. It shows spatial patterns and associations, not causal relationships.
# alpr-surveillance-dashboard
