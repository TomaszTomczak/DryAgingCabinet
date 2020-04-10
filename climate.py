import sensors.sensor_dht22 as sens
import threading
import time

class climate:
    temperature = 0
    humidity = 0

    def __init__(self):
        print("climate created")
        pass

    def start(self):
        print("climate controll start")
        self.updateThread = threading.Thread(target=self.update)
        self.updateThread.daemon = True
        self.updateThread.start()

    def update(self):
        while 1:
            humi, temp = sens.getHumidityAndTemperature(4)
            self.temperature = temp
            self.humidity = humi
            print("data from second sensor: "+str(sens.getHumidityAndTemperatureDHT11(17)))
            time.sleep(5)

    def getTemperature(self):
        return self.temperature

    def getHumidity(self):
        return self.humidity
