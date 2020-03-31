import sys
import Adafruit_DHT

def getHumidityAndTemperature(pin):
    return Adafruit_DHT.read_retry(pin, sensor = Adafruit_DHT.DHT22)
