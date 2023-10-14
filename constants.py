from datetime import timedelta, date

WEATHER_CONDITIONS = [
    "Weather",
    "Clear sky",
    "Partly cloudy",
    "Overcast",
    "Rain",
    "Light rain",
    "Heavy rain",
    "Showers",
    "Thunderstorm",
    "Snow",
    "Fog",
    "Mist",
    "Windy",
    "Hail",
    "Sleet",
    "Tornado",
    "Haze",
    "Dust",
    "Smoke",
    "Drizzle",
    "Blizzard",
    "Hurricane",
    "Tropical storm",
    "Sunny",
    "Cloudy",
    "Warm",
    "Wind",
]

CLOSE_DATES = {
    'yesterday': date.today() - timedelta(days=1),
    'today': date.today() - timedelta(days=0),
    'tomorrow': date.today() + timedelta(days=1)
}
