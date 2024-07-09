#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import Freenove_DHT as DHT
DHTPin = 7     #define the pin of DHT11

class GetDHT11Data():
    # センサデータを取り出してdict形式に変換
    def get_sensor_data(self):
        
        dht = DHT.DHT(DHTPin)   #create a DHT class object
        chk = dht.readDHT11()
        temp = dht.temperature
        hum = dht.humidity
        fukai = 0.81 * temp + 0.01 * hum * (0.99 * temp -14.3) + 46.3
        round_fukai = round(fukai)


        #dict型に格納
        sensorValue = {
            'SensorType': 'DHT11',
            'Temperature': temp,
            'Humidity': hum,
            'THI': round_fukai
        }
        GPIO.cleanup()
        return sensorValue

