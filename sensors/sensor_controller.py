class SensorController:
    sensors = []
    def __init__(self):
        pass
    def configure(self, config):
        for c in configuration:
            if c['type'] == 'dht22':
                pass #need to implement some class for this sensor
