from datetime import datetime

TANK_CAPACITY_M3 = 1000

FACTORY_TANKS = {
    "Zone industrielle Moknine":   {"capacity": 1000, "fill_rate_per_hour": 45},
    "Zone industrielle Teboulba":  {"capacity": 800,  "fill_rate_per_hour": 35},
    "Zone industrielle Ksibet":    {"capacity": 600,  "fill_rate_per_hour": 25},
    "Zone industrielle Monastir":  {"capacity": 1500, "fill_rate_per_hour": 60},
    "Zone industrielle Mahdia":    {"capacity": 900,  "fill_rate_per_hour": 40},
    "Zone industrielle Sahline":   {"capacity": 700,  "fill_rate_per_hour": 30},
}

def get_tank_status(factory_name, alert_hours=0):
    """
    Simulate tank fill level.
    Returns fill percentage, status color, and recommendation.
    """
    tank = FACTORY_TANKS.get(factory_name, {
        "capacity": 800, "fill_rate_per_hour": 35
    })

    now   = datetime.now()
    hours = now.hour + now.minute / 60
    base_fill = (hours % 24) * tank["fill_rate_per_hour"]

    if alert_hours > 0:
        base_fill += tank["fill_rate_per_hour"] * alert_hours

    fill_m3  = min(base_fill, tank["capacity"])
    fill_pct = round((fill_m3 / tank["capacity"]) * 100)

    if fill_pct >= 90:
        status       = "CRITICAL"
        color        = "red"
        emoji        = "🔴"
        action       = "STOP all emissions immediately — tank at capacity"
        hours_left   = 0
    elif fill_pct >= 70:
        status       = "WARNING"
        color        = "orange"
        emoji        = "🟠"
        hours_left   = round((tank["capacity"] - fill_m3) / tank["fill_rate_per_hour"], 1)
        action       = f"Reduce emissions by 60% — only {hours_left}h of storage left"
    elif fill_pct >= 40:
        status       = "MODERATE"
        color        = "yellow"
        emoji        = "🟡"
        hours_left   = round((tank["capacity"] - fill_m3) / tank["fill_rate_per_hour"], 1)
        action       = f"Monitor tank — {hours_left}h of storage remaining"
    else:
        status       = "OK"
        color        = "green"
        emoji        = "✅"
        hours_left   = round((tank["capacity"] - fill_m3) / tank["fill_rate_per_hour"], 1)
        action       = f"Tank normal — {hours_left}h of storage available"

    return {
        "factory":    factory_name,
        "fill_pct":   fill_pct,
        "fill_m3":    round(fill_m3),
        "capacity":   tank["capacity"],
        "status":     status,
        "color":      color,
        "emoji":      emoji,
        "action":     action,
        "hours_left": hours_left if fill_pct < 90 else 0,
    }

def get_all_tank_statuses(alerted_factories=None):
    if alerted_factories is None:
        alerted_factories = set()
    return [
        get_tank_status(name, alert_hours=3 if name in alerted_factories else 0)
        for name in FACTORY_TANKS
    ]