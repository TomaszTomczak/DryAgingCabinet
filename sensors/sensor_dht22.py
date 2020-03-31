import sys
import Adafruit_DHT

def getHumidityAndTemperature(pin):
    sensor = Adafruit_DHT.DHT22
    humi, temp = Adafruit_DHT.read_retry(sensor, pin)
    return (humi,temp)
