from sensors.sensor_controller import SensorController as SensorController
import threading
import time

class climate:
    temperature = 0
    humidity = 0
    

    def __init__(self):
        print("climate created")
        self.sensor_c = SensorController()

    def configure(self, configuration):
        self.sensor_c.configure(configuration)

    def start(self):
        print("climate control start")
        self.updateThread = threading.Thread(target=self.update)
        self.updateThread.daemon = True
        self.updateThread.start()

    def update(self):
        while 1:
            humi, temp = self.sensor_c.getReadings('sensor1')
            self.temperature = temp
            self.humidity = humi
            #print("data from second sensor: "+str(sens.getHumidityAndTemperatureDHT11(17)))
            time.sleep(5)

    def getTemperature(self):
        return self.temperature

    def getHumidity(self):
        return self.humidity
