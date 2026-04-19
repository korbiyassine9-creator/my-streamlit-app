import numpy as np
import pandas as pd
from datetime import datetime

def compass(deg):
    dirs = ["N","NNE","NE","ENE","E","ESE","SE","SSE",
            "S","SSW","SW","WSW","W","WNW","NW","NNW"]
    return dirs[round(deg / 22.5) % 16]

# ── 1. ANOMALY DETECTION ──────────────────────────────────

def detect_wind_anomaly(forecast_df):
    anomalies = []
    speeds     = forecast_df["wind_speed"].values
    directions = forecast_df["wind_direction"].values

    for i in range(1, len(speeds)):
        speed_change = abs(speeds[i] - speeds[i-1])
        dir_change   = abs(directions[i] - directions[i-1])
        if dir_change > 180:
            dir_change = 360 - dir_change

        if speed_change >= 15:
            anomalies.append({
                "type":     "speed",
                "time":     str(forecast_df["time"].iloc[i]),
                "message":  f"⚡ Sudden wind speed jump: "
                            f"{round(speeds[i-1])} → {round(speeds[i])} km/h "
                            f"at {forecast_df['time'].iloc[i].strftime('%H:%M')}",
                "severity": "high" if speed_change >= 25 else "medium"
            })

        if dir_change >= 45:
            anomalies.append({
                "type":     "direction",
                "time":     str(forecast_df["time"].iloc[i]),
                "message":  f"🔄 Sudden wind direction shift: "
                            f"{round(directions[i-1])}° → {round(directions[i])}° "
                            f"at {forecast_df['time'].iloc[i].strftime('%H:%M')}",
                "severity": "high" if dir_change >= 90 else "medium"
            })

    return anomalies


# ── 2. NATURAL LANGUAGE ALERTS ────────────────────────────

def generate_natural_alert(alert):
    risk    = alert["risk_score"]
    speed   = alert["wind_speed"]
    direc   = alert["wind_direction"]
    dist    = alert["distance_km"]
    hours   = alert["hours_ahead"]
    zone    = alert["target_zone"]
    ztype   = alert["zone_type"]
    factory = alert["factory"]

    if risk >= 70:
        level     = "CRITICAL"
        emoji     = "🔴"
        urgency   = "Immediate action required"
        reduction = "100% — activate emergency storage tank immediately"
    elif risk >= 40:
        level     = "HIGH"
        emoji     = "🟠"
        urgency   = "Action recommended within 30 minutes"
        reduction = "60% — reduce stack output and activate buffer storage"
    else:
        level     = "MODERATE"
        emoji     = "🟡"
        urgency   = "Monitor closely"
        reduction = "30% — reduce stack output as precaution"

    zone_label = {
        "city":   "residential area",
        "forest": "natural reserve or agricultural zone",
    }.get(ztype, "protected zone")

    return (
        f"{emoji} **{level} RISK — {factory}**\n\n"
        f"Wind is blowing at **{speed} km/h** from the **{compass(direc)}** "
        f"({direc}°). Smoke will reach **{zone}** — a {zone_label} — "
        f"in approximately **{hours} hour(s)**, "
        f"landing **{dist} km** from the protected boundary.\n\n"
        f"**Risk score:** {risk}/100\n\n"
        f"**{urgency}**\n\n"
        f"**Recommended emission reduction:** {reduction}"
    )


def generate_all_clear_message(factory_name, wind_speed, wind_direction):
    return (
        f"✅ **All clear — {factory_name}**\n\n"
        f"Current wind ({wind_speed} km/h from "
        f"{compass(wind_direction)}, {wind_direction}°) "
        f"is not directing emissions toward any protected zone. "
        f"Normal operations may continue. "
        f"Next check in 1 hour."
    )


# ── 3. 12-HOUR FORECAST SIMULATION ───────────────────────

def run_12h_forecast(forecast_df, hours_ahead=12):
    from risk_engine import calculate_risk

    rows = []
    forecast_slice = forecast_df.head(hours_ahead)

    for i, row in forecast_slice.iterrows():
        hour_results = calculate_risk(
            wind_speed=row["wind_speed"],
            wind_direction=row["wind_direction"],
            hours=1
        )

        max_risk    = max((a["risk_score"] for a in hour_results), default=0)
        alert_count = len(hour_results)
        factories   = list(set(a["factory"] for a in hour_results))

        rows.append({
            "time":           row["time"],
            "wind_speed":     round(row["wind_speed"], 1),
            "wind_direction": round(row["wind_direction"], 1),
            "max_risk":       max_risk,
            "alert_count":    alert_count,
            "factories":      ", ".join(factories) if factories else "None",
        })

    return pd.DataFrame(rows)


def get_peak_danger_hour(forecast_df, hours_ahead=12):
    df = run_12h_forecast(forecast_df, hours_ahead)
    if df.empty or df["max_risk"].max() == 0:
        return None
    return df.loc[df["max_risk"].idxmax()]