from datetime import datetime

def send_alert(alert):
    """Returns a formatted warning message as a string"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""
⚠️ EMISSION ALERT — {timestamp}
🏭 Factory     : {alert['factory']}
🎯 Risk zone   : {alert['target_zone']} ({alert['zone_type']})
📊 Risk score  : {alert['risk_score']}/100
💨 Wind        : {alert['wind_speed']} km/h from {alert['wind_direction']}°
📏 Distance    : {alert['distance_km']} km
⏱️  Time ahead  : {alert['hours_ahead']} hours
🚨 Action      : Reduce emissions / activate storage tank
"""

def send_all_clear(factory_name):
    """Returns a formatted all-clear message as a string"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""
✅ ALL CLEAR — {timestamp}
🏭 Factory     : {factory_name}
💡 Status      : Wind not carrying emissions toward any protected zone
🔄 Next check  : In 1 hour
"""

def get_all_messages(results, factories):
    """
    Returns two lists:
    - warning_messages for factories at risk
    - clear_messages for safe factories
    """
    warning_messages = []
    clear_messages   = []

    factories_at_risk = set(a["factory"] for a in results)

    for alert in results:
        warning_messages.append(send_alert(alert))

    for factory in factories:
        if factory["name"] not in factories_at_risk:
            clear_messages.append(send_all_clear(factory["name"]))

    return warning_messages, clear_messages