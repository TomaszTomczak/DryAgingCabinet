from sensors.sensor_dht import SensorDHT

class SensorController:
    sensors = {}
    def __init__(self):
        pass
    def configure(self, config):
        for c in config['sensors']:
            self.sensors[c['id']] = SensorDHT(c)
    def getReadings(self, id):
        return self.sensors[id].getReadings()
