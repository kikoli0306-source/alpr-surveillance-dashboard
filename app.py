"""
Public Safety Technology in Chicago — Mapping ALPR Cameras and Community Hardship
Layer-based spatial dashboard built with Streamlit + Plotly + GeoPandas.
"""
 
import os, json
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
 
try:
    import geopandas as gpd
    from shapely.geometry import Point
    HAS_GEO = True
except ImportError:
    HAS_GEO = False
 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
 
# ======================== PAGE ========================
st.set_page_config(page_title="ALPR Infrastructure — Chicago", layout="wide",
                   initial_sidebar_state="expanded")
 
# ======================== PALETTE ========================
P = dict(
    bg="#050A14", panel="#0B1120", card="rgba(15,23,42,0.86)", card2="#111827",
    border="rgba(56,189,248,0.22)", text="#E5E7EB", muted="#94A3B8",
    cyan="#38BDF8", blue="#2563EB", violet="#8B5CF6",
    amber="#F59E0B", red="#F87171", white="#F9FAFB",
)
 
OP_COLORS = {
    "Chicago Police Department": "#38BDF8",
    "Illinois State Police":     "#F59E0B",
    "Flock Safety":              "#34D399",
    "University of Chicago Police Department": "#A78BFA",
    "The Home Depot":            "#FB923C",
    "Unknown":                   "#6B7280",
}
 
PL = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(11,17,32,0.92)",
    font=dict(family="Inter, system-ui, sans-serif", color="#E5E7EB", size=13),
    margin=dict(l=30, r=20, t=36, b=30),
    hoverlabel=dict(bgcolor="#111827", font_size=13, font_color="#E5E7EB",
                    bordercolor="#334155"),
)
 
# ======================== CSS ========================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
:root{{--bg:{P["bg"]};--panel:{P["panel"]};--card:{P["card"]};--text:{P["text"]};
--muted:{P["muted"]};--cyan:{P["cyan"]};--blue:{P["blue"]};--violet:{P["violet"]};
--amber:{P["amber"]};--border:{P["border"]};}}
 
.stApp{{background:var(--bg)!important;color:var(--text)!important;
font-family:'Inter',system-ui,sans-serif!important;}}
 
/* sidebar */
section[data-testid="stSidebar"]{{background:var(--panel)!important;
border-right:1px solid var(--border);}}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span{{color:var(--text)!important;}}
 
/* multiselect tags — override red */
span[data-baseweb="tag"]{{background:#1E3A5F!important;
border:1px solid {P["cyan"]}!important;color:{P["text"]}!important;}}
span[data-baseweb="tag"] svg{{fill:{P["muted"]}!important;}}
 
h1{{font-family:'Space Grotesk','Inter',sans-serif!important;font-weight:700!important;
color:var(--text)!important;font-size:2rem!important;letter-spacing:-0.02em;}}
h2{{font-family:'Space Grotesk','Inter',sans-serif!important;font-weight:600!important;
color:var(--text)!important;font-size:1.3rem!important;}}
h3{{font-family:'Inter',sans-serif!important;font-weight:500!important;
color:var(--muted)!important;font-size:1rem!important;}}
 
div[data-testid="stMetric"]{{background:var(--card);border:1px solid var(--border);
border-radius:8px;padding:16px 18px;}}
div[data-testid="stMetric"] label{{color:var(--muted)!important;font-size:.75rem!important;
text-transform:uppercase;letter-spacing:.05em;}}
div[data-testid="stMetric"] div[data-testid="stMetricValue"]{{color:var(--cyan)!important;
font-family:'Space Grotesk','Inter',sans-serif!important;font-weight:600!important;}}
 
hr{{border-color:rgba(56,189,248,0.12)!important;}}
.stPlotlyChart{{border-radius:8px;overflow:hidden;}}
.stDeployButton{{display:none;}}
 
/* custom boxes */
.layer-tag{{font-size:.7rem;text-transform:uppercase;letter-spacing:.14em;
color:{P["cyan"]};font-weight:600;margin-bottom:2px;}}
.q-line{{color:{P["muted"]};font-style:italic;font-size:.93rem;margin-bottom:10px;}}
 
.read-box{{background:rgba(15,23,42,0.6);border:1px solid rgba(148,163,184,0.18);
padding:12px 16px;border-radius:6px;margin:8px 0 14px;color:{P["muted"]};
font-size:.84rem;line-height:1.55;}}
 
.interp-box{{background:var(--card);border-left:3px solid {P["cyan"]};
padding:14px 18px;border-radius:0 6px 6px 0;margin:12px 0 22px;
color:{P["text"]};font-size:.9rem;line-height:1.6;}}
 
.caution-box{{background:rgba(15,23,42,0.5);border-left:3px solid {P["amber"]};
padding:10px 16px;border-radius:0 6px 6px 0;margin:6px 0 12px;
color:{P["muted"]};font-size:.82rem;line-height:1.5;}}
 
.method-card{{background:var(--card);border:1px solid var(--border);
padding:18px 22px;border-radius:8px;margin:14px 0;color:{P["text"]};
font-size:.9rem;line-height:1.65;}}
 
.lim-card{{background:var(--card);border:1px solid var(--border);
padding:14px 16px;border-radius:8px;min-height:100px;}}
.lim-card h4{{color:{P["cyan"]};font-size:.85rem;margin:0 0 6px;font-weight:600;}}
.lim-card p{{color:{P["muted"]};font-size:.82rem;line-height:1.5;margin:0;}}
 
.explorer-card{{background:var(--card);border:1px solid {P["cyan"]};
padding:20px 24px;border-radius:10px;margin:14px 0;}}
.explorer-card h3{{color:{P["cyan"]}!important;margin-bottom:12px;}}
.explorer-stat{{display:inline-block;min-width:140px;margin:6px 12px 6px 0;}}
.explorer-stat .val{{color:{P["cyan"]};font-size:1.15rem;font-weight:600;
font-family:'Space Grotesk',sans-serif;}}
.explorer-stat .lbl{{color:{P["muted"]};font-size:.72rem;text-transform:uppercase;
letter-spacing:.04em;}}
</style>
""", unsafe_allow_html=True)
 
# ======================== HELPERS ========================
def layer(tag, title, question=None):
    st.markdown(f'<div class="layer-tag">{tag}</div>', unsafe_allow_html=True)
    st.markdown(f"## {title}")
    if question:
        st.markdown(f'<div class="q-line">{question}</div>', unsafe_allow_html=True)
 
def read_box(t):
    st.markdown(f'<div class="read-box"><strong>How to read this</strong><br>{t}</div>',
                unsafe_allow_html=True)
def interp_box(t):
    st.markdown(f'<div class="interp-box"><strong>Interpretation</strong><br>{t}</div>',
                unsafe_allow_html=True)
def caution_box(t):
    st.markdown(f'<div class="caution-box">{t}</div>', unsafe_allow_html=True)
 
# ======================== DATA ========================
@st.cache_data(show_spinner="Loading datasets ...")
def load_data():
    # 1 — ALPR cameras
    alpr = pd.read_csv(os.path.join(BASE_DIR, "data", "chicago-alprs.csv"))
    alpr.columns = alpr.columns.str.strip()
    alpr.rename(columns={"@id": "camera_id", "@lat": "lat", "@lon": "lon"}, inplace=True)
    alpr["lat"] = pd.to_numeric(alpr["lat"], errors="coerce")
    alpr["lon"] = pd.to_numeric(alpr["lon"], errors="coerce")
    alpr.dropna(subset=["lat", "lon"], inplace=True)
    alpr["operator"] = alpr["operator"].fillna("Unknown").replace("", "Unknown")
    if "surveillance:type" in alpr.columns:
        alpr.rename(columns={"surveillance:type": "surveillance_type"}, inplace=True)
 
    # 2 — Community boundaries
    gj_path  = os.path.join(BASE_DIR, "data", "communities.geojson")
    csv_path = os.path.join(BASE_DIR, "data", "community_boundaries.csv")
    if HAS_GEO and os.path.exists(gj_path):
        gdf = gpd.read_file(gj_path).to_crs("EPSG:4326")
        rn = {}
        for c in gdf.columns:
            if c.lower() == "area_numbe": rn[c] = "AREA_NUMBE"
            elif c.lower() == "community": rn[c] = "COMMUNITY"
        gdf.rename(columns=rn, inplace=True)
        gdf["AREA_NUMBE"] = gdf["AREA_NUMBE"].astype(str)
    elif HAS_GEO and os.path.exists(csv_path):
        from shapely import wkt as _wkt
        _c = pd.read_csv(csv_path); _c.columns = _c.columns.str.strip()
        _c["geometry"] = _c["the_geom"].apply(_wkt.loads)
        gdf = gpd.GeoDataFrame(_c, geometry="geometry", crs="EPSG:4326")
        gdf["AREA_NUMBE"] = gdf["AREA_NUMBE"].astype(str)
    else:
        gdf = None
 
    # 3 — Socioeconomic
    socio = pd.read_csv(os.path.join(BASE_DIR, "data", "socioeconomic_indicators.csv"))
    socio.columns = socio.columns.str.strip()
    socio.rename(columns=lambda c: c.strip(), inplace=True)
    socio.rename(columns={"Community Area Number": "AREA_NUMBE",
                          "COMMUNITY AREA NAME": "COMMUNITY"}, inplace=True)
    socio["AREA_NUMBE"] = pd.to_numeric(socio["AREA_NUMBE"], errors="coerce")
    socio = socio.dropna(subset=["AREA_NUMBE"])
    socio["AREA_NUMBE"] = socio["AREA_NUMBE"].astype(int).astype(str)
    for col in ["HARDSHIP INDEX", "PERCENT HOUSEHOLDS BELOW POVERTY",
                "PERCENT AGED 16+ UNEMPLOYED", "PER CAPITA INCOME"]:
        if col in socio.columns:
            socio[col] = pd.to_numeric(socio[col], errors="coerce")
 
    # 4 — Spatial join + area + centroids
    geojson_obj = None
    if gdf is not None:
        pts = [Point(xy) for xy in zip(alpr["lon"], alpr["lat"])]
        gdf_a = gpd.GeoDataFrame(alpr, geometry=pts, crs="EPSG:4326")
        joined = gpd.sjoin(gdf_a, gdf[["AREA_NUMBE", "COMMUNITY", "geometry"]],
                           how="left", predicate="within")
        alpr = pd.DataFrame(joined.drop(columns="geometry"))
        proj = gdf.to_crs(epsg=3435)
        gdf["AREA_SQ_MI"] = proj.geometry.area / 27_878_400
        cen = gpd.GeoSeries(proj.geometry.centroid, crs="EPSG:3435").to_crs("EPSG:4326")
        gdf["clat"] = cen.y; gdf["clon"] = cen.x
        geojson_obj = json.loads(gdf[["AREA_NUMBE", "COMMUNITY", "geometry"]].to_json())
    else:
        alpr["AREA_NUMBE"] = np.nan; alpr["COMMUNITY"] = np.nan
 
    # 5 — Aggregate
    if alpr["AREA_NUMBE"].notna().any():
        cc = (alpr.dropna(subset=["AREA_NUMBE"])
                  .groupby("AREA_NUMBE").size().reset_index(name="ALPR_COUNT"))
    else:
        cc = pd.DataFrame(columns=["AREA_NUMBE", "ALPR_COUNT"])
    merged = socio.merge(cc, on="AREA_NUMBE", how="left")
    merged["ALPR_COUNT"] = merged["ALPR_COUNT"].fillna(0).astype(int)
    merged = merged[merged["COMMUNITY"].notna() & (merged["COMMUNITY"].str.upper() != "CHICAGO")]
    if gdf is not None and "AREA_SQ_MI" in gdf.columns:
        extra = pd.DataFrame(gdf[["AREA_NUMBE", "AREA_SQ_MI", "clat", "clon"]]
                             .drop(columns="geometry", errors="ignore"))
        merged = merged.merge(extra, on="AREA_NUMBE", how="left")
        merged["ALPR_DENSITY"] = np.where(
            merged["AREA_SQ_MI"] > 0,
            (merged["ALPR_COUNT"] / merged["AREA_SQ_MI"]).round(2), 0)
    else:
        merged["AREA_SQ_MI"] = np.nan; merged["ALPR_DENSITY"] = np.nan
        merged["clat"] = np.nan; merged["clon"] = np.nan
 
    # Operator stats per community
    op_by_area = (alpr.dropna(subset=["AREA_NUMBE"])
                      .groupby("AREA_NUMBE")["operator"]
                      .agg(dominant=lambda x: x.mode().iloc[0] if len(x) > 0 else "Unknown",
                           unknown_count=lambda x: (x == "Unknown").sum())
                      .reset_index())
    merged = merged.merge(op_by_area, on="AREA_NUMBE", how="left")
    merged["dominant"] = merged["dominant"].fillna("—")
    merged["unknown_count"] = merged["unknown_count"].fillna(0).astype(int)
 
    return alpr, merged, geojson_obj
 
alpr_df, community_df, geojson_data = load_data()
 
# ======================== SIDEBAR ========================
st.sidebar.markdown("### Controls")
 
all_ops = sorted(alpr_df["operator"].unique())
sel_ops = st.sidebar.multiselect("Operator filter", all_ops, default=all_ops,
    help="Select camera operators to include.")
 
cam_measure = st.sidebar.radio("Camera measure",
    ["Raw ALPR count", "ALPR cameras per sq mi"], index=0,
    help="Raw count or density normalised by community area size.")
mcol = "ALPR_COUNT" if cam_measure == "Raw ALPR count" else "ALPR_DENSITY"
mlbl = "ALPR Cameras" if mcol == "ALPR_COUNT" else "ALPR / sq mi"
 
ind_opts = ["HARDSHIP INDEX", "PERCENT HOUSEHOLDS BELOW POVERTY",
            "PERCENT AGED 16+ UNEMPLOYED", "PER CAPITA INCOME"]
sel_ind = st.sidebar.selectbox("Socioeconomic indicator", ind_opts, index=0,
    help="Indicator shown on the right comparison map and used in the scatter plot.")
 
hmin = int(community_df["HARDSHIP INDEX"].min(skipna=True))
hmax = int(community_df["HARDSHIP INDEX"].max(skipna=True))
h_range = st.sidebar.slider("Hardship index range", hmin, hmax, (hmin, hmax),
    help="Filter communities by Hardship Index.")
 
st.sidebar.markdown("---")
st.sidebar.markdown("##### Community Explorer")
comm_list = ["None"] + sorted(community_df["COMMUNITY"].dropna().unique())
sel_comm = st.sidebar.selectbox("Select a community", comm_list, index=0,
    help="Choose a community to inspect in detail.")
 
st.sidebar.markdown("---")
st.sidebar.caption("Data: ALPR camera records / Chicago community boundaries / "
                   "Selected socioeconomic indicators")
 
# ======================== FILTERS ========================
f_alpr = alpr_df[alpr_df["operator"].isin(sel_ops)].copy()
f_comm = community_df[
    (community_df["HARDSHIP INDEX"] >= h_range[0]) &
    (community_df["HARDSHIP INDEX"] <= h_range[1])
].copy()
 
# ======================== OPENING ========================
st.markdown("# Public Safety Technology in Chicago")
st.markdown("### Mapping ALPR Cameras and Community Hardship")
st.markdown("_How are ALPR cameras distributed across Chicago community areas, "
            "and how does this distribution relate to community-level socioeconomic hardship?_")
 
st.markdown("""<div class="method-card">
This dashboard visualises recorded automated license plate reader (ALPR) camera locations
in Chicago and compares their distribution with community-level socioeconomic indicators.
The goal is not to prove causation, but to make spatial patterns of public safety technology
visible and interpretable.<br><br>
<strong>Data + Method</strong><br>
Three datasets are used: ALPR camera point locations, Chicago community area boundaries, and
selected socioeconomic indicators. Camera points were spatially joined to community area
polygons, aggregated by community, and compared with hardship, poverty, unemployment, and
income indicators.
</div>""", unsafe_allow_html=True)
 
caution_box("Counts reflect recorded camera locations in the dataset, not a complete "
            "official inventory.")
 
# ---- Metrics ----
tot = len(f_alpr)
mtch = int(f_alpr["AREA_NUMBE"].notna().sum())
ncomm = int(f_comm.shape[0])
if not f_comm.empty:
    tr = f_comm.loc[f_comm["ALPR_COUNT"].idxmax()]
    tname, tn = tr["COMMUNITY"], int(tr["ALPR_COUNT"])
else:
    tname, tn = "N/A", 0
avgh = round(f_comm["HARDSHIP INDEX"].mean(), 1) if not f_comm.empty else "—"
 
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Recorded cameras", f"{tot:,}")
c2.metric("Matched to areas", f"{mtch:,}")
c3.metric("Community areas", ncomm)
c4.metric("Highest count", f"{tname} ({tn})")
c5.metric("Avg hardship", avgh)
st.markdown("---")
 
# =================== LAYER 01 ===================
layer("Layer 01", "Camera Point Layer",
      "Where are ALPR cameras physically recorded in Chicago?")
 
read_box("Each point represents a recorded ALPR camera. Use the operator filter "
         "to compare public, private, institutional, and unknown operators. "
         "Hover over a point to inspect the camera record.")
 
fig1 = px.scatter_mapbox(
    f_alpr, lat="lat", lon="lon", color="operator",
    color_discrete_map=OP_COLORS,
    hover_data={"camera_id": True, "operator": True, "direction": True,
                "COMMUNITY": True, "lat": ":.4f", "lon": ":.4f"},
    labels={"COMMUNITY": "Community Area", "camera_id": "Camera ID"},
    zoom=10, center={"lat": 41.82, "lon": -87.68}, height=540,
)
fig1.update_layout(mapbox_style="carto-darkmatter", **PL,
                   legend=dict(title="Operator", bgcolor="rgba(11,17,32,0.9)",
                               font=dict(color="#E5E7EB")))
st.plotly_chart(fig1, use_container_width=True)
 
interp_box("The point map makes camera placement visible as infrastructure rather "
           "than isolated devices. The distribution is clustered along corridors "
           "and selected urban areas, not evenly spread across the city. Because "
           "this map shows raw point locations, it is useful for seeing clusters, "
           "but it should not be read as a normalised measure of surveillance exposure.")
st.markdown("---")
 
# =================== LAYER 02 ===================
layer("Layer 02", "Community Aggregation Layer",
      "Which community areas contain more recorded ALPR cameras?")
 
read_box("The left map shows camera concentration by community area. The right map "
         "shows the selected socioeconomic indicator. Read the maps as a spatial "
         "comparison, not as proof of causation.")
caution_box("Raw counts show where cameras are recorded. Density helps reduce the "
            "visual bias created by community areas of different sizes.")
 
if geojson_data and not f_comm.empty:
    lc, rc = st.columns(2)
    with lc:
        st.markdown(f"**Recorded Camera Concentration** ({mlbl})")
        fl = px.choropleth_mapbox(
            f_comm, geojson=geojson_data,
            locations="AREA_NUMBE", featureidkey="properties.AREA_NUMBE",
            color=mcol,
            color_continuous_scale=["#050A14", "#1e3a5f", "#38BDF8", "#F59E0B"],
            hover_name="COMMUNITY",
            hover_data={mcol: True, "HARDSHIP INDEX": True, "AREA_NUMBE": False},
            labels={mcol: mlbl, "HARDSHIP INDEX": "Hardship"},
            zoom=9.3, center={"lat": 41.83, "lon": -87.7},
            opacity=0.78, height=480,
        )
        fl.update_layout(mapbox_style="carto-darkmatter", **PL,
                         coloraxis_colorbar=dict(title=mlbl, tickfont=dict(color="#94A3B8")))
        st.plotly_chart(fl, use_container_width=True)
    with rc:
        st.markdown(f"**Socioeconomic Context** ({sel_ind.title()})")
        rev = sel_ind == "PER CAPITA INCOME"
        cs = (["#F59E0B", "#38BDF8", "#1e3a5f", "#050A14"] if rev
              else ["#050A14", "#1e3a5f", "#38BDF8", "#F59E0B"])
        fr = px.choropleth_mapbox(
            f_comm, geojson=geojson_data,
            locations="AREA_NUMBE", featureidkey="properties.AREA_NUMBE",
            color=sel_ind, color_continuous_scale=cs,
            hover_name="COMMUNITY",
            hover_data={sel_ind: True, "ALPR_COUNT": True, "AREA_NUMBE": False},
            labels={sel_ind: sel_ind.title(), "ALPR_COUNT": "ALPR Cameras"},
            zoom=9.3, center={"lat": 41.83, "lon": -87.7},
            opacity=0.78, height=480,
        )
        fr.update_layout(mapbox_style="carto-darkmatter", **PL,
                         coloraxis_colorbar=dict(title="Value", tickfont=dict(color="#94A3B8")))
        st.plotly_chart(fr, use_container_width=True)
 
    interp_box("The side-by-side maps show overlap, but not equivalence. The geography "
               "of ALPR camera concentration and the geography of hardship do not perfectly "
               "match, which supports a cautious interpretation rather than a causal claim.")
st.markdown("---")
 
# =================== LAYER 03 ===================
layer("Layer 03", "Hardship Alignment Layer",
      "Does community hardship align with ALPR camera concentration?")
 
read_box("Each point is a community area. The vertical and horizontal reference lines "
         "split the chart at the median hardship and median camera measure, creating "
         "four interpretive quadrants.")
 
if not f_comm.empty:
    med_h = f_comm["HARDSHIP INDEX"].median()
    med_c = f_comm[mcol].median()
 
    fig3 = px.scatter(
        f_comm, x="HARDSHIP INDEX", y=mcol, hover_name="COMMUNITY",
        hover_data={"ALPR_COUNT": True, "HARDSHIP INDEX": True,
                    "PERCENT HOUSEHOLDS BELOW POVERTY": True,
                    "PERCENT AGED 16+ UNEMPLOYED": True,
                    "PER CAPITA INCOME": True},
        labels={"HARDSHIP INDEX": "Hardship Index", mcol: mlbl},
        size=mcol, size_max=20,
        color="HARDSHIP INDEX",
        color_continuous_scale=["#1e3a5f", "#8B5CF6", "#F59E0B"],
        height=500,
    )
 
    # Highlight selected community
    if sel_comm != "None":
        sel_row = f_comm[f_comm["COMMUNITY"] == sel_comm]
        if not sel_row.empty:
            fig3.add_trace(go.Scatter(
                x=sel_row["HARDSHIP INDEX"], y=sel_row[mcol],
                mode="markers+text", text=[sel_comm],
                textposition="top center", textfont=dict(color="#38BDF8", size=11),
                marker=dict(size=18, color="rgba(0,0,0,0)",
                            line=dict(width=2.5, color="#38BDF8")),
                showlegend=False, hoverinfo="skip",
            ))
 
    fig3.add_hline(y=med_c, line_dash="dot", line_color="#334155", line_width=1,
                   annotation_text=f"Median {mlbl}", annotation_position="top left",
                   annotation_font=dict(color="#6B7280", size=10))
    fig3.add_vline(x=med_h, line_dash="dot", line_color="#334155", line_width=1,
                   annotation_text="Median Hardship", annotation_position="top right",
                   annotation_font=dict(color="#6B7280", size=10))
 
    xr = f_comm["HARDSHIP INDEX"].max() - f_comm["HARDSHIP INDEX"].min()
    yr = f_comm[mcol].max() - f_comm[mcol].min()
    quads = [
        dict(x=med_h - xr*0.28, y=med_c + yr*0.38, text="Low hardship / High cameras"),
        dict(x=med_h + xr*0.28, y=med_c + yr*0.38, text="High hardship / High cameras"),
        dict(x=med_h - xr*0.28, y=max(0, med_c - yr*0.22), text="Low hardship / Low cameras"),
        dict(x=med_h + xr*0.28, y=max(0, med_c - yr*0.22), text="High hardship / Low cameras"),
    ]
    for q in quads:
        q.update(showarrow=False, font=dict(size=9.5, color="#6B7280"))
    fig3.update_layout(**PL, annotations=quads,
                       xaxis=dict(gridcolor="rgba(51,65,85,0.25)", zeroline=False),
                       yaxis=dict(gridcolor="rgba(51,65,85,0.25)", zeroline=False),
                       coloraxis_colorbar=dict(title="Hardship", tickfont=dict(color="#94A3B8")))
    fig3.update_traces(marker=dict(line=dict(width=0.7, color="#0B1120")))
    st.plotly_chart(fig3, use_container_width=True)
 
    caution_box("Focus area: communities in the upper-right quadrant combine above-median "
                "hardship with above-median ALPR count.")
 
    interp_box("The quadrant view separates communities into interpretive groups. "
               "The upper-right quadrant identifies communities where above-median "
               "hardship overlaps with above-median camera count. This does not prove "
               "targeting, but it shows where surveillance exposure and socioeconomic "
               "vulnerability intersect. The broader scatter does not show a simple "
               "positive relationship between hardship and ALPR count.")
st.markdown("---")
 
# =================== LAYER 04 ===================
layer("Layer 04", "Community Burden Layer",
      "Which communities stand out when camera count and hardship are read together?")
 
read_box("Circle size represents camera presence. Colour represents hardship. "
         "This view keeps geography in the background while making community-level "
         "camera burden easier to compare without the area-size bias of choropleths.")
 
if (not f_comm.empty and f_comm["clat"].notna().any() and f_comm[mcol].max() > 0):
    sym = f_comm[f_comm[mcol] > 0].copy()
    fig4 = px.scatter_mapbox(
        sym, lat="clat", lon="clon", size=mcol, size_max=34,
        color="HARDSHIP INDEX",
        color_continuous_scale=["#1e3a5f", "#8B5CF6", "#F59E0B"],
        hover_name="COMMUNITY",
        hover_data={mcol: True, "HARDSHIP INDEX": True,
                    "PERCENT HOUSEHOLDS BELOW POVERTY": True,
                    "PER CAPITA INCOME": True, "clat": False, "clon": False},
        labels={mcol: mlbl, "HARDSHIP INDEX": "Hardship"},
        zoom=9.8, center={"lat": 41.83, "lon": -87.7}, height=520,
    )
 
    # Highlight selected community
    if sel_comm != "None":
        sr = sym[sym["COMMUNITY"] == sel_comm]
        if not sr.empty:
            fig4.add_trace(go.Scattermapbox(
                lat=sr["clat"], lon=sr["clon"], mode="markers",
                marker=dict(size=28, color="#38BDF8", opacity=0.35),
                showlegend=False, hoverinfo="skip",
            ))
 
    fig4.update_layout(mapbox_style="carto-darkmatter", **PL,
                       coloraxis_colorbar=dict(title="Hardship",
                                               tickfont=dict(color="#94A3B8")))
    st.plotly_chart(fig4, use_container_width=True)
 
    interp_box("This symbol map shows community-level camera burden without relying "
               "only on polygon shading. Larger circles mark communities with more "
               "recorded ALPR cameras, while warmer colours indicate higher hardship. "
               "The most important areas are where both appear together.")
st.markdown("---")
 
# =================== LAYER 05 ===================
layer("Layer 05", "Operator Ecosystem Layer",
      "Which operators appear in the ALPR dataset?")
 
read_box("Bars show how many ALPR records are associated with each operator label. "
         "Missing operator information is grouped as Unknown.")
 
known = int((f_alpr["operator"] != "Unknown").sum())
unknown = int((f_alpr["operator"] == "Unknown").sum())
unk_pct = round(unknown / max(len(f_alpr), 1) * 100, 1)
 
mc1, mc2, mc3 = st.columns(3)
mc1.metric("Known operator records", f"{known:,}")
mc2.metric("Unknown operator records", f"{unknown:,}")
mc3.metric("Unknown share", f"{unk_pct}%")
 
caution_box("Unknown does not mean unmonitored. It means the public record does not "
            "include operator information for those cameras.")
 
opc = (f_alpr.groupby("operator").size().reset_index(name="count")
             .sort_values("count", ascending=True))
fig5 = px.bar(opc, x="count", y="operator", orientation="h",
              color="operator", color_discrete_map=OP_COLORS,
              labels={"count": "Camera Records", "operator": "Operator"},
              height=320)
fig5.update_layout(**PL, showlegend=False,
                   xaxis=dict(gridcolor="rgba(51,65,85,0.25)"),
                   yaxis=dict(tickfont=dict(size=12)))
st.plotly_chart(fig5, use_container_width=True)
 
interp_box("The operator field shows that ALPR infrastructure is not represented by "
           "a single institution. The dataset includes public, private, institutional, "
           "and unknown operators, supporting the framing of ALPR as part of a broader "
           "public safety technology ecosystem. Operator metadata is incomplete and "
           "must be interpreted cautiously.")
st.markdown("---")
 
# =================== LAYER 06 ===================
layer("Layer 06", "Ranked Exposure Layer",
      "Which community areas have the highest recorded ALPR presence?")
 
read_box(f"Bars show recorded ALPR camera counts ({mlbl}); colour shows hardship index.")
 
if not f_comm.empty:
    t15 = f_comm.nlargest(15, mcol).sort_values(mcol, ascending=True)
    fig6 = px.bar(t15, x=mcol, y="COMMUNITY", orientation="h",
                  color="HARDSHIP INDEX",
                  color_continuous_scale=["#1e3a5f", "#8B5CF6", "#F59E0B"],
                  hover_data={"ALPR_COUNT": True, "HARDSHIP INDEX": True,
                              "PERCENT HOUSEHOLDS BELOW POVERTY": True,
                              "PER CAPITA INCOME": True},
                  labels={mcol: mlbl, "COMMUNITY": "Community Area",
                          "HARDSHIP INDEX": "Hardship"},
                  height=480)
    fig6.update_layout(**PL, yaxis=dict(tickfont=dict(size=11)),
                       xaxis=dict(gridcolor="rgba(51,65,85,0.25)"),
                       coloraxis_colorbar=dict(title="Hardship",
                                               tickfont=dict(color="#94A3B8")))
    st.plotly_chart(fig6, use_container_width=True)
 
    interp_box("Central/high-traffic communities and high-hardship communities both "
               "appear in the top group. This mixed ranking shows that camera-heavy "
               "areas are socially different from one another. Near North Side, "
               "West Town, Lincoln Park, and the Loop have high counts, but "
               "high-hardship communities such as Austin, Fuller Park, and "
               "West Garfield Park also appear.")
st.markdown("---")
 
# =================== COMMUNITY EXPLORER ===================
layer("Explorer", "Selected Community Explorer",
      "Inspect a single community area in detail.")
 
if sel_comm != "None":
    row = community_df[community_df["COMMUNITY"] == sel_comm]
    if not row.empty:
        r = row.iloc[0]
        st.markdown(f"""<div class="explorer-card">
<h3>{r['COMMUNITY']}</h3>
<div class="explorer-stat"><div class="val">{int(r['ALPR_COUNT'])}</div>
<div class="lbl">ALPR cameras</div></div>
<div class="explorer-stat"><div class="val">{r.get('ALPR_DENSITY','—')}</div>
<div class="lbl">Per sq mi</div></div>
<div class="explorer-stat"><div class="val">{r.get('HARDSHIP INDEX','—')}</div>
<div class="lbl">Hardship index</div></div>
<div class="explorer-stat"><div class="val">{r.get('PERCENT HOUSEHOLDS BELOW POVERTY','—')}%</div>
<div class="lbl">Below poverty</div></div>
<div class="explorer-stat"><div class="val">{r.get('PERCENT AGED 16+ UNEMPLOYED','—')}%</div>
<div class="lbl">Unemployed 16+</div></div>
<div class="explorer-stat"><div class="val">${int(r.get('PER CAPITA INCOME',0)):,}</div>
<div class="lbl">Per capita income</div></div>
<div class="explorer-stat"><div class="val">{r.get('dominant','—')}</div>
<div class="lbl">Dominant operator</div></div>
<div class="explorer-stat"><div class="val">{int(r.get('unknown_count',0))}</div>
<div class="lbl">Unknown-operator records</div></div>
</div>""", unsafe_allow_html=True)
    else:
        st.info("Community not found in current filter range.")
else:
    st.markdown('<div class="read-box">Select a community area from the sidebar '
                'to inspect its camera and socioeconomic profile.</div>',
                unsafe_allow_html=True)
 
st.markdown("---")
 
# =================== LIMITATIONS ===================
layer("Data Considerations", "Limitations and Scope")
 
lims = [
    ("Data Coverage", "The dataset may not include every installed camera."),
    ("Raw Count Bias", "Raw counts are not normalised by population, road length, "
     "traffic volume, or commercial activity."),
    ("Operator Missingness", "Many records do not include operator labels."),
    ("Temporal Mismatch", "Socioeconomic indicators may not match the camera data period."),
    ("Presence, Not Use", "The dashboard maps camera locations, not how captured data "
     "is stored, shared, or used after collection."),
    ("Aggregation Limits", "Community-level analysis can hide block-level differences."),
]
cols = st.columns(3)
for i, (title, desc) in enumerate(lims):
    with cols[i % 3]:
        st.markdown(f'<div class="lim-card"><h4>{title}</h4><p>{desc}</p></div>',
                    unsafe_allow_html=True)
 
st.markdown("---")
st.caption("Built with Streamlit  |  Data Visualization Final Project  |  2026")