import streamlit as st
import folium
from streamlit_folium import st_folium
from risk_engine import calculate_risk
from alert import get_all_messages
from utils import FACTORIES, PROTECTED_ZONES

def wind_direction_label(degrees):
    """Convert degrees to compass direction"""
    directions = [
        "N", "NNE", "NE", "ENE",
        "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW",
        "W", "WNW", "NW", "NNW"
    ]
    index = round(degrees / 22.5) % 16
    return directions[index]

def render_whatif():
    st.subheader("🧪 What-if Simulator")
    st.caption("Manually set wind conditions and instantly see what would happen")

    st.divider()

    # ── Controls ──────────────────────────────────────────
    col1, col2, col3 = st.columns(3)

    with col1:
        wind_speed = st.slider(
            "💨 Wind speed (km/h)",
            min_value=0,
            max_value=120,
            value=25,
            step=1
        )

    with col2:
        wind_direction = st.slider(
            "🧭 Wind direction (degrees)",
            min_value=0,
            max_value=359,
            value=300,
            step=1
        )

    with col3:
        hours = st.slider(
            "⏱️ Hours ahead",
            min_value=1,
            max_value=12,
            value=3,
            step=1
        )

    # ── Direction display ─────────────────────────────────
    compass = wind_direction_label(wind_direction)
    st.info(
        f"💨 Wind blowing at **{wind_speed} km/h** "
        f"from **{wind_direction}° ({compass})**  "
        f"— smoke will travel **{round(wind_speed * hours)} km** "
        f"in **{hours} hour(s)**"
    )

    # ── Run simulation ────────────────────────────────────
    results = calculate_risk(wind_speed, wind_direction, hours)
    warning_messages, clear_messages = get_all_messages(results, FACTORIES)

    st.divider()

    # ── Result banner ─────────────────────────────────────
    if wind_speed == 0:
        st.success("✅ Wind speed is zero — no smoke movement detected.")
        return

    if results:
        st.error(f"⚠️ {len(results)} zone(s) at risk under these conditions!")
    else:
        st.success("✅ No risk detected — smoke would not reach any protected zone.")

    # ── Two column layout ─────────────────────────────────
    left, right = st.columns([2, 1])

    with left:
        st.subheader("🗺️ Simulation Map")

        m = folium.Map(
            location=[35.65, 10.90],
            zoom_start=10,
            tiles="CartoDB positron"
        )

        # Protected zones
        for zone in PROTECTED_ZONES:
            folium.Circle(
                location=[zone["lat"], zone["lon"]],
                radius=zone["radius_km"] * 1000,
                color="green",
                fill=True,
                fill_opacity=0.15,
                tooltip=f"🛡️ {zone['name']}"
            ).add_to(m)
            folium.Marker(
                location=[zone["lat"], zone["lon"]],
                tooltip=zone["name"],
                icon=folium.Icon(color="green", icon="leaf", prefix="fa")
            ).add_to(m)

        # Factories
        alerted = set(a["factory"] for a in results)
        for factory in FACTORIES:
            folium.Marker(
                location=[factory["lat"], factory["lon"]],
                tooltip=f"🏭 {factory['name']}",
                icon=folium.Icon(
                    color="red" if factory["name"] in alerted else "blue",
                    icon="industry",
                    prefix="fa"
                )
            ).add_to(m)

        # Smoke trajectories
        for alert in results:
            folium.PolyLine(
                locations=[
                    [alert["factory_lat"], alert["factory_lon"]],
                    [alert["smoke_lat"], alert["smoke_lon"]]
                ],
                color="red",
                weight=3,
                opacity=0.7,
                tooltip=f"⚠️ {alert['factory']} → {alert['target_zone']} | Risk: {alert['risk_score']}/100"
            ).add_to(m)

            folium.CircleMarker(
                location=[alert["smoke_lat"], alert["smoke_lon"]],
                radius=10,
                color="orange",
                fill=True,
                fill_opacity=0.6,
                tooltip=f"💨 Smoke lands here in {hours}h"
            ).add_to(m)

        st_folium(m, width=700, height=420)

    with right:
        # ── Risk results ──────────────────────────────────
        st.subheader("📊 Simulation Results")

        if results:
            for a in results:
                color = "🔴" if a["risk_score"] >= 70 else "🟠" if a["risk_score"] >= 40 else "🟡"
                st.error(
                    f"{color} **{a['factory']}**\n\n"
                    f"→ {a['target_zone']}\n\n"
                    f"Risk: **{a['risk_score']}/100** | {a['distance_km']} km away"
                )
        else:
            st.success("No factories at risk under these conditions.")

        st.divider()

        # ── Scenario summary ──────────────────────────────
        st.subheader("📋 Scenario Summary")
        st.markdown(f"""
| Parameter | Value |
|-----------|-------|
| Wind speed | {wind_speed} km/h |
| Direction | {wind_direction}° ({compass}) |
| Forecast | {hours} hour(s) |
| Travel distance | {round(wind_speed * hours)} km |
| Factories checked | {len(FACTORIES)} |
| Zones at risk | {len(results)} |
| Safe factories | {len(FACTORIES) - len(alerted)} |
        """)