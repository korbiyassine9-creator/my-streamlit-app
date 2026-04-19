import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Monastir coordinates
MONASTIR_LAT = 35.7643
MONASTIR_LON = 10.8113

def fetch_wind_data(lat=MONASTIR_LAT, lon=MONASTIR_LON):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ["wind_speed_10m", "wind_direction_10m", "temperature_2m"],
        "current": ["wind_speed_10m", "wind_direction_10m"],
        "wind_speed_unit": "kmh",
        "forecast_days": 1
    }
    
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    
    # Current wind
    current = response.Current()
    current_wind_speed = current.Variables(0).Value()
    current_wind_direction = current.Variables(1).Value()
    
    # Hourly forecast
    hourly = response.Hourly()
    hourly_df = pd.DataFrame({
        "time": pd.date_range(
            start=pd.Timestamp(hourly.Time(), unit="s"),
            end=pd.Timestamp(hourly.TimeEnd(), unit="s"),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        ),
        "wind_speed": hourly.Variables(0).ValuesAsNumpy(),
        "wind_direction": hourly.Variables(1).ValuesAsNumpy(),
        "temperature": hourly.Variables(2).ValuesAsNumpy(),
    })
    
    return {
        "current_speed": round(current_wind_speed, 1),
        "current_direction": round(current_wind_direction, 1),
        "forecast": hourly_df
    }

if __name__ == "__main__":
    data = fetch_wind_data()
    print(f"Current wind: {data['current_speed']} km/h from {data['current_direction']}°")
    print(data['forecast'].head())