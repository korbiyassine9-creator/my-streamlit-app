import math
from utils import FACTORIES, PROTECTED_ZONES

def degrees_to_radians(deg):
    return deg * math.pi / 180

def calculate_distance_km(lat1, lon1, lat2, lon2):
    """Haversine formula — gives real distance between two coordinates"""
    R = 6371
    dlat = degrees_to_radians(lat2 - lat1)
    dlon = degrees_to_radians(lon2 - lon1)
    a = (math.sin(dlat/2)**2 +
         math.cos(degrees_to_radians(lat1)) *
         math.cos(degrees_to_radians(lat2)) *
         math.sin(dlon/2)**2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def get_wind_endpoint(factory_lat, factory_lon, wind_direction_deg, wind_speed_kmh, hours=3):
    """
    Calculate where the wind carries smoke after X hours.
    Wind direction in meteorology = where wind comes FROM.
    We reverse it to get where smoke GOES.
    """
    travel_km = wind_speed_kmh * hours
    # Convert to where smoke travels TO
    bearing = degrees_to_radians((wind_direction_deg + 180) % 360)
    R = 6371
    lat1 = degrees_to_radians(factory_lat)
    lon1 = degrees_to_radians(factory_lon)

    lat2 = math.asin(
        math.sin(lat1) * math.cos(travel_km/R) +
        math.cos(lat1) * math.sin(travel_km/R) * math.cos(bearing)
    )
    lon2 = lon1 + math.atan2(
        math.sin(bearing) * math.sin(travel_km/R) * math.cos(lat1),
        math.cos(travel_km/R) - math.sin(lat1) * math.sin(lat2)
    )

    return math.degrees(lat2), math.degrees(lon2)

def calculate_risk(wind_speed, wind_direction, hours=3):
    """
    For each factory, check if smoke endpoint lands near a protected zone.
    Returns list of alerts with risk scores.
    """
    alerts = []

    for factory in FACTORIES:
        # Where will smoke be in X hours?
        smoke_lat, smoke_lon = get_wind_endpoint(
            factory["lat"], factory["lon"],
            wind_direction, wind_speed, hours
        )

        for zone in PROTECTED_ZONES:
            dist = calculate_distance_km(smoke_lat, smoke_lon, zone["lat"], zone["lon"])

            # Risk score: closer = higher risk, faster wind = higher risk
            if dist < zone["radius_km"] + 5:  # within danger range
                risk_score = max(0, min(100, int(
                    (1 - dist / (zone["radius_km"] + 5)) * 70 +
                    (wind_speed / 60) * 30
                )))

                if risk_score > 20:
                    alerts.append({
                        "factory": factory["name"],
                        "factory_lat": factory["lat"],
                        "factory_lon": factory["lon"],
                        "smoke_lat": smoke_lat,
                        "smoke_lon": smoke_lon,
                        "target_zone": zone["name"],
                        "zone_type": zone["type"],
                        "distance_km": round(dist, 2),
                        "risk_score": risk_score,
                        "wind_speed": wind_speed,
                        "wind_direction": wind_direction,
                        "hours_ahead": hours,
                    })

    # Sort by highest risk first
    alerts.sort(key=lambda x: x["risk_score"], reverse=True)
    return alerts


if __name__ == "__main__":
    from alert import run_alerts
    
    print("🔍 WindGuard — running risk analysis...")
    print(f"   Wind: 25 km/h from 300°\n")
    
    results = calculate_risk(wind_speed=25, wind_direction=300)
    run_alerts(results)