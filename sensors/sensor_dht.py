import sys
import Adafruit_DHT


#it is good idea to implement abstract class to provide interface for each sensor
class SensorDHT:
    def __init__(self, config):
        if(config['type']=='dht11'):
            self.sensor_type = Adafruit_DHT.DHT11
        elif config['type']=='dht22':
            self.sensor_type = Adafruit_DHT.DHT22
        self.id = config['id']
        self.position = config['position']
    
    def getReadings(self):
        '''this will return humidity and temperature tuple'''
        humi, temp = Adafruit_DHT.read_retry(self.sensor_type, self.position)
        if temp is None or humi is None:
            raise Exception("Sensor data reading error")
        return humi, temp
