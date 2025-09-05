import requests

# Replace with your OpenWeatherMap API key
API_KEY = "60dcb93d75117fac216e6a7a18e79a47"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# Ask user for city name
city = input("Enter city name (example: Delhi or Delhi,IN): ")

# Make API request
params = {
    "q": city,
    "appid": API_KEY,
    "units": "metric"
}

response = requests.get(BASE_URL, params=params)
data = response.json()

if response.status_code == 200 and data.get("cod") != "404":
    print(f"\n✅ Weather in {data['name']}, {data['sys']['country']}")
    print(f"🌤  Condition: {data['weather'][0]['description'].title()}")
    print(f"🌡  Temperature: {data['main']['temp']}°C")
    print(f"💧 Humidity: {data['main']['humidity']}%")
    print(f"💨 Wind Speed: {data['wind']['speed']} m/s")
else:
    print("\n❌ City not found or API error!")
    print("API Response:", data)  # Debugging

