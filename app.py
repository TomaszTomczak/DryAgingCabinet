from flask import Flask
from DryAgingCabinet.sensor import sensor
import os

app = Flask(__name__)

def getCPUtemperature():
  res = os.popen("vcgencmd measure_temp").readline()
  return(res.replace("temp=","").replace("'C\n",""))

def getRoomTemperature():
    humidity, temperature = sensor.getHumidityAndTemperature(4) # 4 pin
    return temperature

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/statistics')
def stats():
    #data = "CPU temperature ", getCPUtemperature()
    return os.popen("vcgencmd measure_temp").readline()

@app.route('/room')
def stats():
    #data = "CPU temperature ", getCPUtemperature()
    return getRoomTemperature()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')