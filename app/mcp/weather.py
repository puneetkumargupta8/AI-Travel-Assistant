import requests
from pydantic import BaseModel
from typing import List


class WeatherDay(BaseModel):
    date: str
    max_temp: float
    min_temp: float
    precipitation: float


class WeatherOutput(BaseModel):
    forecast: List[WeatherDay]


def get_delhi_weather() -> WeatherOutput:

    # Delhi coordinates
    lat = 28.6139
    lon = 77.2090

    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
        "&timezone=auto"
    )

    response = requests.get(url)
    data = response.json()

    forecast = []

    for i in range(min(3, len(data["daily"]["time"]))):
        forecast.append(
            WeatherDay(
                date=data["daily"]["time"][i],
                max_temp=data["daily"]["temperature_2m_max"][i],
                min_temp=data["daily"]["temperature_2m_min"][i],
                precipitation=data["daily"]["precipitation_sum"][i]
            )
        )

    return WeatherOutput(forecast=forecast)