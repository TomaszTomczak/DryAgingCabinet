import sys
import Adafruit_DHT

def getHumidityAndTemperature(pin):
    humi, temp = Adafruit_DHT.read_retry(pin, Adafruit_DHT.sensor = Adafruit_DHT.DHT22)
    return (h,t)
