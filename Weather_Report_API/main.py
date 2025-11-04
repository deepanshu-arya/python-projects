from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
import requests
from datetime import datetime
from typing import Optional

# -----------------------------------------------------------
# Title       : Weather Report API
# Description : Fetches live weather data for any given city
# Author      : Deepanshu
# -----------------------------------------------------------

app = FastAPI(
    title="🌤️ Weather Report API",
    description="A simple FastAPI service to fetch live weather details using OpenWeatherMap API.",
    version="2.0.0"
)

# -----------------------------------------------------------
# Helper Function: Get Weather Data
# -----------------------------------------------------------
def get_weather(api_key: str, city: str) -> Optional[dict]:
    """
    Fetch the current weather for the given city using OpenWeatherMap API.

    Args:
        api_key (str): Your OpenWeatherMap API key.
        city (str): City name to fetch the weather data for.

    Returns:
        dict: Parsed weather data (temperature, humidity, etc.)
    """
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": "metric"}

    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
    except requests.Timeout:
        raise HTTPException(status_code=408, detail="⏰ Request timed out. Please try again.")
    except requests.ConnectionError:
        raise HTTPException(status_code=503, detail="⚠️ Network error. Check your connection.")
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"❌ Unexpected error: {e}")

    data = response.json()

    if data.get("cod") != 200:
        raise HTTPException(status_code=404, detail=f"City not found: {data.get('message')}")

    # Extract and return clean weather data
    return {
        "city": data.get("name"),
        "country": data["sys"]["country"],
        "temperature": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"],
        "weather_description": data["weather"][0]["description"].capitalize(),
        "time": datetime.utcfromtimestamp(data["dt"]).strftime("%Y-%m-%d %H:%M:%S (UTC)")
    }


# -----------------------------------------------------------
# Home Route
# -----------------------------------------------------------
@app.get("/", tags=["Root"])
def home():
    """
    Welcome message for the API root.
    """
    return {
        "message": "Welcome to 🌤️ Weather Report API!",
        "usage": "Use /weather?api_key=YOUR_KEY&city=CityName to fetch live weather data.",
        "developer": "Deepanshu"
    }


# -----------------------------------------------------------
# Main Endpoint: Fetch Weather Data
# -----------------------------------------------------------
@app.get("/weather", tags=["Weather"])
def weather(
    api_key: str = Query(..., description="Your OpenWeatherMap API key"),
    city: str = Query(..., description="City name to fetch weather for")
):
    """
    Fetch live weather details for a given city.
    """
    weather_info = get_weather(api_key, city)
    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "requested_city": city,
            "data": weather_info,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }
    )


# -----------------------------------------------------------
# Custom Error Handlers
# -----------------------------------------------------------
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc):
    """
    Custom error handler for better readability.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "message": exc.detail,
            "path": str(request.url)
        },
    )


@app.get("/health", tags=["System"])
def health_check():
    """
    Simple endpoint to check API health.
    """
    return {"status": "✅ OK", "message": "Weather API is running smoothly."}
