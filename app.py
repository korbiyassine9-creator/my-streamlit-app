import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from datetime import datetime
from fetch_wind import fetch_wind_data
from risk_engine import calculate_risk
from alert import get_all_messages
from utils import FACTORIES, PROTECTED_ZONES, CITY_POPULATIONS
from history import save_alerts, load_history, get_factory_ranking, get_summary_stats
from analysis import (
    detect_wind_anomaly,
    generate_natural_alert,
    generate_all_clear_message,
    run_12h_forecast,
    get_peak_danger_hour
)
from smoketank import get_all_tank_statuses
from language import t
from factory_profile import get_profile

# ── Global styles ─────────────────────────────────────────
st.set_page_config(
    page_title="WindGuard",
    page_icon="💨",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
/* ── Font & base ── */
html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
}

/* ── Hide default streamlit menu/footer ── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* ── Main background ── */
.stApp {
    background: linear-gradient(135deg, #0f1117 0%, #1a1f2e 50%, #0f1117 100%);
}

/* ── Top header bar ── */
.main-header {
    background: linear-gradient(90deg, #00b4d8, #0077b6);
    padding: 1.2rem 2rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    box-shadow: 0 4px 24px rgba(0,180,216,0.3);
}
.main-header h1 {
    color: white !important;
    font-size: 2rem !important;
    font-weight: 800 !important;
    margin: 0 !important;
    letter-spacing: 2px;
}
.main-header p {
    color: rgba(255,255,255,0.8) !important;
    margin: 0 !important;
    font-size: 0.9rem;
}

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #1e2535, #252d42);
    border: 1px solid rgba(0,180,216,0.2);
    border-radius: 16px;
    padding: 1rem 1.2rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.3);
}
[data-testid="metric-container"]:hover {
    border-color: rgba(0,180,216,0.5);
    box-shadow: 0 4px 20px rgba(0,180,216,0.2);
    transform: translateY(-2px);
    transition: all 0.2s ease;
}
[data-testid="stMetricLabel"] {
    color: rgba(255,255,255,0.6) !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 1px;
}
[data-testid="stMetricValue"] {
    color: #00b4d8 !important;
    font-size: 1.8rem !important;
    font-weight: 800 !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #1a1f2e;
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
    border: 1px solid rgba(0,180,216,0.15);
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: rgba(255,255,255,0.5) !important;
    border-radius: 10px;
    font-weight: 600;
    font-size: 0.85rem;
    padding: 0.5rem 1.2rem;
    transition: all 0.2s;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #00b4d8, #0077b6) !important;
    color: white !important;
    box-shadow: 0 2px 12px rgba(0,180,216,0.4);
}
.stTabs [data-baseweb="tab"]:hover {
    color: white !important;
    background: rgba(0,180,216,0.1) !important;
}

/* ── Sliders ── */
[data-testid="stSlider"] > div > div > div > div {
    background: linear-gradient(90deg, #00b4d8, #0077b6) !important;
}
[data-testid="stSlider"] > div > div > div > div > div {
    background: white !important;
    border: 3px solid #00b4d8 !important;
    box-shadow: 0 0 8px rgba(0,180,216,0.5) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #00b4d8, #0077b6) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 1.5rem !important;
    box-shadow: 0 3px 12px rgba(0,180,216,0.4) !important;
    transition: all 0.2s !important;
    letter-spacing: 0.5px;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(0,180,216,0.5) !important;
}
.stButton > button:active {
    transform: translateY(0px) !important;
}

/* ── Download button ── */
.stDownloadButton > button {
    background: linear-gradient(135deg, #2ecc71, #27ae60) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    box-shadow: 0 3px 12px rgba(46,204,113,0.3) !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
    background: #1e2535 !important;
    border: 1px solid rgba(0,180,216,0.3) !important;
    border-radius: 10px !important;
    color: white !important;
}

/* ── Multiselect ── */
[data-testid="stMultiSelect"] > div > div {
    background: #1e2535 !important;
    border: 1px solid rgba(0,180,216,0.3) !important;
    border-radius: 10px !important;
}

/* ── Alert boxes ── */
.stAlert {
    border-radius: 12px !important;
    border-left-width: 4px !important;
    font-weight: 500;
}

/* ── Success box ── */
[data-testid="stSuccess"] {
    background: rgba(46,204,113,0.1) !important;
    border-color: #2ecc71 !important;
    border-radius: 12px !important;
}

/* ── Error box ── */
[data-testid="stError"] {
    background: rgba(231,76,60,0.1) !important;
    border-color: #e74c3c !important;
    border-radius: 12px !important;
}

/* ── Warning box ── */
[data-testid="stWarning"] {
    background: rgba(243,156,18,0.1) !important;
    border-color: #f39c12 !important;
    border-radius: 12px !important;
}

/* ── Info box ── */
[data-testid="stInfo"] {
    background: rgba(0,180,216,0.1) !important;
    border-color: #00b4d8 !important;
    border-radius: 12px !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    border: 1px solid rgba(0,180,216,0.2) !important;
    overflow: hidden;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #1a1f2e 100%) !important;
    border-right: 1px solid rgba(0,180,216,0.15) !important;
}
[data-testid="stSidebar"] .stSelectbox label {
    color: rgba(255,255,255,0.7) !important;
}

/* ── Divider ── */
hr {
    border-color: rgba(0,180,216,0.15) !important;
}

/* ── Subheaders ── */
h2, h3 {
    color: white !important;
    font-weight: 700 !important;
}

/* ── Section card wrapper ── */
.section-card {
    background: linear-gradient(135deg, #1e2535, #252d42);
    border: 1px solid rgba(0,180,216,0.15);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

/* ── Status badge ── */
.badge-critical { 
    background: linear-gradient(135deg,#e74c3c,#c0392b);
    color:white; padding:4px 12px; border-radius:20px;
    font-weight:700; font-size:0.8rem;
}
.badge-warning { 
    background: linear-gradient(135deg,#f39c12,#e67e22);
    color:white; padding:4px 12px; border-radius:20px;
    font-weight:700; font-size:0.8rem;
}
.badge-ok { 
    background: linear-gradient(135deg,#2ecc71,#27ae60);
    color:white; padding:4px 12px; border-radius:20px;
    font-weight:700; font-size:0.8rem;
}

/* ── Tank progress bar ── */
.tank-bar-container {
    background: rgba(255,255,255,0.1);
    border-radius: 8px;
    height: 12px;
    overflow: hidden;
    margin: 6px 0;
}
.tank-bar-fill {
    height: 100%;
    border-radius: 8px;
    transition: width 0.5s ease;
}

/* ── Spinner ── */
[data-testid="stSpinner"] {
    color: #00b4d8 !important;
}

/* ── Charts ── */
[data-testid="stArrowVegaLiteChart"] {
    border-radius: 12px;
    overflow: hidden;
}

/* ── Caption text ── */
[data-testid="stCaptionContainer"] {
    color: rgba(255,255,255,0.4) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center; padding: 1rem 0;'>
        <div style='font-size:3rem;'>💨</div>
        <h2 style='color:#00b4d8; margin:0; font-size:1.5rem; font-weight:800;'>WindGuard</h2>
        <p style='color:rgba(255,255,255,0.5); font-size:0.8rem; margin:0;'>
            Emission Alert System
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    lang = st.selectbox(
        "🌐 Language / Langue / اللغة",
        options=["en", "fr", "ar"],
        format_func=lambda x: {
            "en": "🇬🇧 English",
            "fr": "🇫🇷 Français",
            "ar": "🇹🇳 العربية"
        }[x]
    )

    st.divider()

    st.markdown(f"""
    <p style='color:rgba(255,255,255,0.5); font-size:0.75rem; 
              text-transform:uppercase; letter-spacing:1px; margin-bottom:0.5rem;'>
        🏭 {t('monitored', lang)}
    </p>
    """, unsafe_allow_html=True)

    for f in FACTORIES:
        risk_emoji = "🔴" if "Monastir" in f["name"] else "🟡"
        st.markdown(f"""
        <div style='background:rgba(0,180,216,0.05); border:1px solid rgba(0,180,216,0.1);
                    border-radius:8px; padding:6px 10px; margin-bottom:4px;
                    font-size:0.8rem; color:rgba(255,255,255,0.7);'>
            {risk_emoji} {f['name'].replace('Zone industrielle ', '')}
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.markdown(f"""
    <p style='color:rgba(255,255,255,0.3); font-size:0.75rem; text-align:center;'>
        🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}
    </p>
    """, unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────
st.markdown(f"""
<div class='main-header'>
    <div style='font-size:2.5rem;'>💨</div>
    <div>
        <h1>{t('title', lang)}</h1>
        <p>{t('caption', lang)}</p>
    </div>
    <div style='margin-left:auto; text-align:right;'>
        <div style='background:rgba(255,255,255,0.15); border-radius:20px;
                    padding:4px 16px; color:white; font-size:0.8rem; font-weight:600;'>
            🟢 SYSTEM ONLINE
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Fetch wind data once ──────────────────────────────────
with st.spinner("Fetching live wind data..."):
    wind_data         = fetch_wind_data()
current_speed         = wind_data["current_speed"]
current_direction     = wind_data["current_direction"]
forecast_df           = wind_data["forecast"]

def compass(deg):
    dirs = ["N","NNE","NE","ENE","E","ESE","SE","SSE",
            "S","SSW","SW","WSW","W","WNW","NW","NNW"]
    return dirs[round(deg / 22.5) % 16]

def build_map(results, hours, key):
    m       = folium.Map(
        location=[35.65, 10.90],
        zoom_start=10,
        tiles="CartoDB dark_matter"
    )
    alerted = set(a["factory"] for a in results)

    for zone in PROTECTED_ZONES:
        color = "red" if any(
            a["target_zone"] == zone["name"] for a in results
        ) else "green"
        folium.Circle(
            location=[zone["lat"], zone["lon"]],
            radius=zone["radius_km"] * 1000,
            color=color,
            fill=True,
            fill_opacity=0.2,
            tooltip=f"🛡️ {zone['name']} ({zone['type']})"
        ).add_to(m)
        folium.Marker(
            location=[zone["lat"], zone["lon"]],
            tooltip=zone["name"],
            icon=folium.Icon(
                color="red" if color == "red" else "green",
                icon="leaf", prefix="fa"
            )
        ).add_to(m)

    for factory in FACTORIES:
        at_risk = factory["name"] in alerted
        folium.Marker(
            location=[factory["lat"], factory["lon"]],
            tooltip=f"🏭 {factory['name']}",
            icon=folium.Icon(
                color="red" if at_risk else "blue",
                icon="industry", prefix="fa"
            )
        ).add_to(m)

    for alert in results:
        folium.PolyLine(
            locations=[
                [alert["factory_lat"], alert["factory_lon"]],
                [alert["smoke_lat"],   alert["smoke_lon"]]
            ],
            color="#ff4444",
            weight=3,
            opacity=0.8,
            tooltip=f"⚠️ {alert['factory']} → {alert['target_zone']} | {alert['risk_score']}/100"
        ).add_to(m)
        folium.CircleMarker(
            location=[alert["smoke_lat"], alert["smoke_lon"]],
            radius=12,
            color="#ff8800",
            fill=True,
            fill_color="#ff8800",
            fill_opacity=0.7,
            tooltip=f"💨 Smoke lands here in {hours}h"
        ).add_to(m)

    return st_folium(m, width=None, height=460, key=key,
                     returned_objects=[])

def metric_card(label, value, color="#00b4d8"):
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#1e2535,#252d42);
                border:1px solid {color}33; border-radius:16px;
                padding:1rem 1.2rem; text-align:center;
                box-shadow:0 2px 12px rgba(0,0,0,0.3);'>
        <div style='color:rgba(255,255,255,0.5); font-size:0.75rem;
                    font-weight:700; text-transform:uppercase;
                    letter-spacing:1px; margin-bottom:4px;'>{label}</div>
        <div style='color:{color}; font-size:1.8rem; font-weight:800;'>{value}</div>
    </div>
    """, unsafe_allow_html=True)

def section_header(icon, title):
    st.markdown(f"""
    <div style='display:flex; align-items:center; gap:10px;
                margin:1.5rem 0 1rem 0;'>
        <div style='background:linear-gradient(135deg,#00b4d8,#0077b6);
                    border-radius:10px; padding:6px 10px;
                    font-size:1.2rem;'>{icon}</div>
        <h3 style='color:white; margin:0; font-size:1.1rem;
                   font-weight:700;'>{title}</h3>
    </div>
    """, unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    t("tab_live",     lang),
    t("tab_whatif",   lang),
    t("tab_history",  lang),
    t("tab_analysis", lang),
    t("tab_tanks",    lang),
])


# ════════════════════════════════════════════════════════════
# TAB 1 — LIVE MONITOR
# ════════════════════════════════════════════════════════════
with tab1:

    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card(t("wind_speed", lang),     f"{current_speed} km/h")
    with c2: metric_card(t("wind_direction", lang), f"{current_direction}°  {compass(current_direction)}", "#a855f7")
    with c3: metric_card(t("factories", lang),      len(FACTORIES), "#f39c12")
    with c4: metric_card(t("protected_zones", lang),len(PROTECTED_ZONES), "#2ecc71")

    st.divider()

    hours   = st.slider(
        f"⏱️ {t('forecast_horizon', lang)}",
        1, 12, 3, key="live_hours"
    )
    results = calculate_risk(current_speed, current_direction, hours)
    warning_messages, clear_messages = get_all_messages(results, FACTORIES)
    alerted_factories = set(a["factory"] for a in results)
    protected_people  = sum(
        CITY_POPULATIONS.get(a["target_zone"], 0) for a in results
    )

    p1, p2, p3 = st.columns(3)
    with p1: metric_card(t("people_at_risk", lang),  f"{protected_people:,}", "#e74c3c")
    with p2: metric_card(t("factories_risk", lang),  len(alerted_factories),  "#f39c12")
    with p3: metric_card(t("safe_factories", lang),  len(FACTORIES) - len(alerted_factories), "#2ecc71")

    st.divider()

    if results:
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,rgba(231,76,60,0.15),rgba(192,57,43,0.1));
                    border:2px solid #e74c3c; border-radius:14px;
                    padding:1rem 1.5rem; margin:1rem 0;
                    display:flex; align-items:center; gap:12px;'>
            <div style='font-size:1.8rem;'>🚨</div>
            <div>
                <div style='color:#e74c3c; font-weight:800; font-size:1rem;'>
                    {len(results)} {t('alert_banner', lang)}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        save_alerts(results)
    else:
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,rgba(46,204,113,0.15),rgba(39,174,96,0.1));
                    border:2px solid #2ecc71; border-radius:14px;
                    padding:1rem 1.5rem; margin:1rem 0;
                    display:flex; align-items:center; gap:12px;'>
            <div style='font-size:1.8rem;'>✅</div>
            <div style='color:#2ecc71; font-weight:700;'>
                {t('all_clear', lang)}
            </div>
        </div>
        """, unsafe_allow_html=True)

    left, right = st.columns([3, 2])

    with left:
        section_header("🗺️", t("live_map", lang))
        build_map(results, hours, key="live_map")

    with right:
        section_header("🚨", t("warning_alerts", lang))
        if warning_messages:
            for msg in warning_messages:
                st.error(msg)
        else:
            st.success(t("no_warnings", lang))

        st.divider()
        section_header("✅", t("safe_panel", lang))
        for msg in clear_messages:
            st.success(msg)

    if results:
        st.divider()
        section_header("📋", t("alert_details", lang))
        df = pd.DataFrame(results)[[
            "factory", "target_zone", "zone_type",
            "risk_score", "distance_km", "wind_speed", "wind_direction"
        ]]
        df.columns = [
            t("factories", lang), t("protected_zones", lang), "Type",
            "Risk Score", f"{t('distance', lang)} (km)",
            "Wind (km/h)", "Dir (°)"
        ]
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()
    section_header("📈", t("forecast_chart", lang))
    st.line_chart(
        forecast_df.set_index("time")["wind_speed"],
        use_container_width=True,
        color="#00b4d8"
    )

    st.markdown(f"""
    <p style='text-align:center; color:rgba(255,255,255,0.3);
              font-size:0.75rem; margin-top:1rem;'>
        {t('last_updated', lang)}: {datetime.now().strftime('%Y-%m-%d %H:%M')} | WindGuard v2.0
    </p>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# TAB 3 — ALERT HISTORY
# ════════════════════════════════════════════════════════════
with tab3:

    section_header("📜", t("alert_history", lang))
    st.markdown(f"<p style='color:rgba(255,255,255,0.4);'>{t('history_caption', lang)}</p>",
                unsafe_allow_html=True)

    stats = get_summary_stats()

    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card(t("total_alerts", lang),        stats["total_alerts"],        "#e74c3c")
    with c2: metric_card(t("factories_triggered", lang), stats["unique_factories"],     "#f39c12")
    with c3: metric_card(t("avg_risk", lang),             stats["avg_risk"],             "#00b4d8")
    with c4: metric_card(t("highest_risk", lang),         stats["highest_risk"],         "#a855f7")

    st.divider()

    c5, c6 = st.columns(2)
    with c5:
        st.info(f"🎯 {t('most_affected', lang)}: **{stats['most_affected_zone']}**")
    with c6:
        st.warning(f"🏭 {t('most_alerted', lang)}: **{stats['most_alerted_factory']}**")

    st.divider()

    section_header("🏆", t("factory_ranking", lang))
    ranking = get_factory_ranking()
    if ranking.empty:
        st.info(f"ℹ️ {t('no_risk', lang)}")
    else:
        st.dataframe(ranking, use_container_width=True, hide_index=True)

    st.divider()
    section_header("📋", t("full_log", lang))
    history_df = load_history()

    if history_df.empty:
        st.info(f"ℹ️ {t('history_caption', lang)}")
    else:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            factory_filter = st.multiselect(
                t("filter_factory", lang),
                options=history_df["factory"].unique().tolist(),
                default=[]
            )
        with col_f2:
            zone_filter = st.multiselect(
                t("filter_zone", lang),
                options=history_df["zone_type"].unique().tolist(),
                default=[]
            )

        filtered = history_df.copy()
        if factory_filter:
            filtered = filtered[filtered["factory"].isin(factory_filter)]
        if zone_filter:
            filtered = filtered[filtered["zone_type"].isin(zone_filter)]

        st.dataframe(
            filtered[[
                "timestamp", "factory", "target_zone", "zone_type",
                "risk_score", "distance_km", "wind_speed", "wind_direction"
            ]].rename(columns={
                "timestamp":      "Time",
                "factory":        t("factories", lang),
                "target_zone":    t("protected_zones", lang),
                "zone_type":      "Type",
                "risk_score":     "Risk Score",
                "distance_km":    f"{t('distance', lang)} (km)",
                "wind_speed":     "Wind (km/h)",
                "wind_direction": "Dir (°)"
            }),
            use_container_width=True,
            hide_index=True
        )

        if len(filtered) > 1:
            st.divider()
            section_header("📈", t("risk_score_time", lang))
            st.line_chart(
                filtered.set_index("timestamp")["risk_score"],
                use_container_width=True,
                color="#e74c3c"
            )

        st.divider()
        csv_data = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            label=f"⬇️ {t('download_csv', lang)}",
            data=csv_data,
            file_name=f"windguard_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )


# ════════════════════════════════════════════════════════════
# TAB 4 — ANALYSIS
# ════════════════════════════════════════════════════════════
with tab4:

    section_header("🔬", t("advanced_analysis", lang))

    # ── Anomaly detection ─────────────────────────────────
    section_header("⚡", t("anomaly_title", lang))
    anomalies = detect_wind_anomaly(forecast_df)

    if not anomalies:
        st.success(f"✅ {t('no_anomaly', lang)}")
    else:
        st.warning(f"⚠️ {len(anomalies)} {t('anomalies_found', lang)}")
        for a in anomalies:
            if a["severity"] == "high":
                st.error(a["message"])
            else:
                st.warning(a["message"])

    st.divider()

    # ── Natural language alerts ───────────────────────────
    section_header("💬", t("nl_alerts", lang))
    nl_results = calculate_risk(current_speed, current_direction, 3)

    if nl_results:
        for alert in nl_results:
            risk  = alert["risk_score"]
            color = "#e74c3c" if risk >= 70 else "#f39c12" if risk >= 40 else "#f1c40f"
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,rgba(30,37,53,0.9),rgba(37,45,66,0.9));
                        border-left:4px solid {color}; border-radius:12px;
                        padding:1rem 1.5rem; margin-bottom:1rem;'>
                <p style='color:white; margin:0; line-height:1.7;'>
                    {generate_natural_alert(alert).replace(chr(10), '<br>')}
                </p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success(f"✅ {t('all_safe', lang)}")
        for factory in FACTORIES:
            st.success(generate_all_clear_message(
                factory["name"], current_speed, current_direction
            ))

    st.divider()

    # ── 12-hour forecast ──────────────────────────────────
    section_header("🕐", t("forecast_12h", lang))
    with st.spinner("Running 12-hour simulation..."):
        forecast_risk_df = run_12h_forecast(forecast_df, hours_ahead=12)
        peak             = get_peak_danger_hour(forecast_df, hours_ahead=12)

    if peak is not None and peak["max_risk"] > 0:
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,rgba(231,76,60,0.15),rgba(192,57,43,0.1));
                    border:2px solid #e74c3c; border-radius:14px;
                    padding:1rem 1.5rem; margin:1rem 0;'>
            <span style='color:#e74c3c; font-weight:800;'>🔴 {t('peak_danger', lang)}</span>
            <b style='color:white;'> {pd.Timestamp(peak['time']).strftime('%H:%M')}</b>
            — {t('max_risk', lang)}: <b style='color:#e74c3c;'>{int(peak['max_risk'])}/100</b>
            | Wind: {peak['wind_speed']} km/h | {peak['factories']}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.success(f"✅ {t('no_peak', lang)}")

    if not forecast_risk_df.empty:
        section_header("📊", t("risk_per_hour", lang))
        st.area_chart(
            forecast_risk_df.set_index("time")["max_risk"],
            use_container_width=True,
            color="#e74c3c"
        )

        section_header("📋", t("hourly_table", lang))
        display_df = forecast_risk_df.copy()
        display_df["time"] = pd.to_datetime(
            display_df["time"]
        ).dt.strftime("%H:%M")
        display_df.columns = [
            "Time", "Wind (km/h)", "Dir (°)",
            "Max Risk", "Alerts", t("factories", lang)
        ]
        st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.divider()

    # ── Factory profiles ──────────────────────────────────
    section_header("🏭", t("factory_profiles", lang))
    selected = st.selectbox(
        t("select_factory", lang),
        options=[f["name"] for f in FACTORIES]
    )

    if selected:
        profile = get_profile(selected)
        risk_colors = {
            "Critique": "#e74c3c",
            "Élevé":    "#f39c12",
            "Modéré":   "#f1c40f",
            "Faible":   "#2ecc71",
            "N/A":      "#888"
        }
        rc = risk_colors.get(profile["risk_level"], "#888")

        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#1e2535,#252d42);
                    border:1px solid rgba(0,180,216,0.2); border-radius:16px;
                    padding:1.5rem; margin-top:1rem;'>
            <div style='display:grid; grid-template-columns:1fr 1fr; gap:12px;'>
                <div>
                    <div style='color:rgba(255,255,255,0.4); font-size:0.75rem;
                                text-transform:uppercase; letter-spacing:1px;'>
                        {t('sector', lang)}</div>
                    <div style='color:#00b4d8; font-weight:700;'>{profile['sector']}</div>
                </div>
                <div>
                    <div style='color:rgba(255,255,255,0.4); font-size:0.75rem;
                                text-transform:uppercase; letter-spacing:1px;'>
                        {t('employees', lang)}</div>
                    <div style='color:white; font-weight:700;'>{profile['employees']:,}</div>
                </div>
                <div>
                    <div style='color:rgba(255,255,255,0.4); font-size:0.75rem;
                                text-transform:uppercase; letter-spacing:1px;'>
                        {t('daily_emissions', lang)}</div>
                    <div style='color:#f39c12; font-weight:700;'>{profile['daily_emissions']}</div>
                </div>
                <div>
                    <div style='color:rgba(255,255,255,0.4); font-size:0.75rem;
                                text-transform:uppercase; letter-spacing:1px;'>
                        {t('main_pollutants', lang)}</div>
                    <div style='color:#e74c3c; font-weight:700;'>{profile['main_pollutants']}</div>
                </div>
                <div>
                    <div style='color:rgba(255,255,255,0.4); font-size:0.75rem;
                                text-transform:uppercase; letter-spacing:1px;'>
                        {t('operating_hours', lang)}</div>
                    <div style='color:white; font-weight:700;'>{profile['operating_hours']}</div>
                </div>
                <div>
                    <div style='color:rgba(255,255,255,0.4); font-size:0.75rem;
                                text-transform:uppercase; letter-spacing:1px;'>
                        {t('risk_level', lang)}</div>
                    <div style='color:{rc}; font-weight:800;'>{profile['risk_level']}</div>
                </div>
            </div>
            <div style='margin-top:1rem; padding-top:1rem;
                        border-top:1px solid rgba(255,255,255,0.07);
                        color:rgba(255,255,255,0.6); font-size:0.9rem;
                        line-height:1.6;'>
                {profile['description']}
            </div>
        </div>
        """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# TAB 5 — SMOKE TANKS
# ════════════════════════════════════════════════════════════
with tab5:

    section_header("🛢️", t("tank_monitor", lang))
    st.markdown(
        f"<p style='color:rgba(255,255,255,0.4);'>{t('tank_caption', lang)}</p>",
        unsafe_allow_html=True
    )

    live_results  = calculate_risk(current_speed, current_direction, 3)
    live_alerted  = set(a["factory"] for a in live_results)
    tank_statuses = get_all_tank_statuses(live_alerted)

    critical = sum(1 for tk in tank_statuses if tk["status"] == "CRITICAL")
    warning  = sum(1 for tk in tank_statuses if tk["status"] == "WARNING")
    ok       = sum(1 for tk in tank_statuses if tk["status"] in ["OK", "MODERATE"])

    m1, m2, m3 = st.columns(3)
    with m1: metric_card(t("critical_tanks", lang), critical, "#e74c3c")
    with m2: metric_card(t("warning_tanks", lang),  warning,  "#f39c12")
    with m3: metric_card(t("normal_tanks", lang),   ok,       "#2ecc71")

    st.divider()

    for tk in tank_statuses:
        pct   = tk["fill_pct"]
        color = (
            "#e74c3c" if pct >= 90 else
            "#f39c12" if pct >= 70 else
            "#f1c40f" if pct >= 40 else
            "#2ecc71"
        )
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#1e2535,#252d42);
                    border:1px solid {color}33; border-left:4px solid {color};
                    border-radius:14px; padding:1.2rem 1.5rem; margin-bottom:0.75rem;'>
            <div style='display:flex; justify-content:space-between;
                        align-items:center; margin-bottom:10px;'>
                <div>
                    <span style='color:white; font-weight:800; font-size:1rem;'>
                        {tk['emoji']} {tk['factory']}
                    </span>
                    <span style='margin-left:10px; background:{color}22;
                                 color:{color}; border:1px solid {color}44;
                                 border-radius:20px; padding:2px 10px;
                                 font-size:0.75rem; font-weight:700;'>
                        {tk['status']}
                    </span>
                </div>
                <div style='color:{color}; font-size:1.4rem; font-weight:900;'>
                    {pct}%
                </div>
            </div>
            <div style='background:rgba(255,255,255,0.08); border-radius:8px;
                        height:10px; overflow:hidden; margin-bottom:10px;'>
                <div style='width:{pct}%; height:100%; border-radius:8px;
                            background:linear-gradient(90deg,{color}aa,{color});
                            transition:width 0.5s ease;'></div>
            </div>
            <div style='display:flex; justify-content:space-between;'>
                <span style='color:rgba(255,255,255,0.5); font-size:0.8rem;'>
                    {tk['fill_m3']} / {tk['capacity']} m³
                </span>
                <span style='color:{color}; font-size:0.8rem; font-weight:600;'>
                    {tk['action']}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    section_header("📉", t("reduction_calc", lang))
    st.markdown(
        f"<p style='color:rgba(255,255,255,0.4);'>{t('reduction_caption', lang)}</p>",
        unsafe_allow_html=True
    )

    if live_results:
        for alert in live_results:
            risk     = alert["risk_score"]
            factory  = alert["factory"]
            distance = alert["distance_km"]
            speed    = alert["wind_speed"]

            if risk >= 70:
                cut_pct      = 100
                hours_to_act = 0
                color        = "#e74c3c"
            elif risk >= 40:
                cut_pct      = 60
                hours_to_act = round(distance / speed, 1) if speed > 0 else 0
                color        = "#f39c12"
            else:
                cut_pct      = 30
                hours_to_act = round(distance / speed, 1) if speed > 0 else 0
                color        = "#f1c40f"

            st.markdown(f"""
            <div style='background:linear-gradient(135deg,#1e2535,#252d42);
                        border-left:4px solid {color}; border-radius:12px;
                        padding:1rem 1.5rem; margin-bottom:0.75rem;'>
                <div style='color:{color}; font-weight:800; margin-bottom:6px;'>
                    🏭 {factory}
                </div>
                <div style='color:rgba(255,255,255,0.7); font-size:0.9rem; line-height:1.7;'>
                    {t('reduce_by', lang)}
                    <b style='color:{color};'>{cut_pct}%</b>
                    {t('within', lang)}
                    <b style='color:white;'>{hours_to_act}h</b>
                    {t('to_prevent', lang)}
                    <b style='color:#00b4d8;'>{alert['target_zone']}</b>
                    <br>
                    {t('current_risk', lang)}: <b>{risk}/100</b>
                    &nbsp;|&nbsp;
                    {t('distance', lang)}: <b>{distance} km</b>
                    &nbsp;|&nbsp;
                    Wind: <b>{speed} km/h</b>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success(f"✅ {t('no_reduction', lang)}")
