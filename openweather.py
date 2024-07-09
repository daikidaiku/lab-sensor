#coding: utf-8

import subprocess
# import RPi.GPIO as GPIO
#import dht11
import time
import datetime
from datetime import datetime
import requests
import json
import sys
import os
from dotenv import load_dotenv

# .envファイルの読み込み
load_dotenv()

# fukai80 = "暑くて汗が出る状態です。クーラーを付けた方が良いです。"
# fukai70 = "やや暑い状態です。"
# fukai65 = "快い状態です。"
# fukai55 = "肌寒い状態です。"
# fukai50 = "寒い状態です。"

API_KEY = os.getenv('OPENWEATHER_API_KEY')
api = "http://api.openweathermap.org/data/2.5/weather?q={city}&APPID={key}"

class GetOpenWeatherData():
    def get_sensor_data(self):
        city_name = "Yokohama-shi"
        url = api.format(city = city_name, key = API_KEY)
        response = requests.get(url)
        data = json.loads(response.text)
        k2c = lambda k: k - 273.15
        # print(data)
        # print(k2c)
        temp = k2c(data["main"]["temp"])
        hum = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        round_temp = round(temp,1)

        fukai = 0.81 * temp + 0.01 * hum * (0.99 * temp -14.3) + 46.3
        round_fukai = round(fukai)

        sensorValue = {
            'SensorType': 'OpenWeather',
            'Temperature': round_temp,
            'Humidity': hum,
            'Pressure': pressure,
            'THI': round_fukai
        }
        return sensorValue