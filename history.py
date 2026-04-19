import csv
import os
import pandas as pd
from datetime import datetime

HISTORY_FILE = "data/alert_history.csv"

COLUMNS = [
    "timestamp",
    "factory",
    "target_zone",
    "zone_type",
    "risk_score",
    "distance_km",
    "wind_speed",
    "wind_direction",
    "hours_ahead",
    "smoke_lat",
    "smoke_lon"
]

def init_history():
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNS)
            writer.writeheader()

def save_alerts(results):
    init_history()
    if not results:
        return
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(HISTORY_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        for alert in results:
            writer.writerow({
                "timestamp":      timestamp,
                "factory":        alert["factory"],
                "target_zone":    alert["target_zone"],
                "zone_type":      alert["zone_type"],
                "risk_score":     alert["risk_score"],
                "distance_km":    alert["distance_km"],
                "wind_speed":     alert["wind_speed"],
                "wind_direction": alert["wind_direction"],
                "hours_ahead":    alert["hours_ahead"],
                "smoke_lat":      alert["smoke_lat"],
                "smoke_lon":      alert["smoke_lon"],
            })

def load_history():
    init_history()
    try:
        df = pd.read_csv(HISTORY_FILE)
        if df.empty:
            return pd.DataFrame(columns=COLUMNS)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df.sort_values("timestamp", ascending=False)
    except Exception:
        return pd.DataFrame(columns=COLUMNS)

def get_factory_ranking():
    df = load_history()
    if df.empty:
        return pd.DataFrame(columns=["Factory", "Total Alerts", "Avg Risk Score", "Last Alert"])
    ranking = (
        df.groupby("factory")
        .agg(
            total_alerts=("factory", "count"),
            avg_risk=("risk_score", "mean"),
            last_alert=("timestamp", "max")
        )
        .reset_index()
        .sort_values("total_alerts", ascending=False)
    )
    ranking.columns = ["Factory", "Total Alerts", "Avg Risk Score", "Last Alert"]
    ranking["Avg Risk Score"] = ranking["Avg Risk Score"].round(1)
    return ranking

def get_summary_stats():
    df = load_history()
    if df.empty:
        return {
            "total_alerts":          0,
            "unique_factories":      0,
            "avg_risk":              0,
            "highest_risk":          0,
            "most_affected_zone":    "N/A",
            "most_alerted_factory":  "N/A",
        }
    return {
        "total_alerts":          len(df),
        "unique_factories":      df["factory"].nunique(),
        "avg_risk":              round(df["risk_score"].mean(), 1),
        "highest_risk":          int(df["risk_score"].max()),
        "most_affected_zone":    df["target_zone"].value_counts().idxmax(),
        "most_alerted_factory":  df["factory"].value_counts().idxmax(),
    }