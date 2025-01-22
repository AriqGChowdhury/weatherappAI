import requests
import os

class WeatherAPI:
    def __init__(self, cityChosen, days):
        self.weather_api_key = os.environ.get("WEATHER_API")
        self.weather_api_url = "http://api.weatherapi.com/v1/forecast.json"
        self.invalid = False
        self.weather_forecast_param = {
            "key": self.weather_api_key,
            "q": cityChosen,
            "days": days,
            "alerts": "yes",
            "aqi": "yes",
            
        }
        self.response = requests.get(url=self.weather_api_url, params=self.weather_forecast_param).json()
        if 'error' in self.response:
            self.invalid = True

    def currentWeather(self):
        current_cityName = self.response['location']['name']
        current_temp = self.response['current']['temp_f']
        current_condition = self.response['current']['condition']['text']
        current_picture = self.response['current']['condition']['icon']
        current_wind = self.response['current']['wind_mph']
        current_feelsLike = self.response['current']['feelslike_f']

        current_weather = {
            "cityName": current_cityName,
            "currentTemp": f"{current_temp} degrees",
            "currentCondition": current_condition,
            "weatherIcon": current_picture,
            "windMPH": current_wind,
            "feelsLike": f"{current_feelsLike} degrees"
        }


        return current_weather
    
    def forecast(self):
    
        forecast_data_list = []
        for i in range(len(self.response['forecast']['forecastday'])):
            forecast_data = {
                "dates": self.response['forecast']['forecastday'][i]['date'],
                "maxTemp": self.response['forecast']['forecastday'][i]['day']['maxtemp_f'],
                "minTemp": self.response['forecast']['forecastday'][i]['day']['mintemp_f'],
                "avgTemp": self.response['forecast']['forecastday'][i]['day']['avgtemp_f'],
                "chance_of_snow": self.response['forecast']['forecastday'][i]['day']['daily_chance_of_snow'],
                "chance_of_rain": self.response['forecast']['forecastday'][i]['day']['daily_chance_of_rain'],
                "weather_condition": self.response['forecast']['forecastday'][i]['day']['condition']['text'],
                "condition_pic": self.response['forecast']['forecastday'][i]['day']['condition']['icon'],
                "sunrise": self.response['forecast']['forecastday'][i]['astro']['sunrise'],
                "sunset": self.response['forecast']['forecastday'][i]['astro']['sunset']
            }
            forecast_data_list.append(forecast_data)
            
        return forecast_data_list
    