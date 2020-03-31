from flask import Flask
import sensors.sensor_dht22 as sens
import os
import threading
import time
import display.lcd as lcd


VAL = 0

l = lcd.lcd_display()

app = Flask(__name__)

def getCPUtemperature():
  res = os.popen("vcgencmd measure_temp").readline()
  return(res.replace("temp=","").replace("'C\n",""))

def getRoomTemperature():
    humidity, temperature = sens.getHumidityAndTemperature(4) # 4 pin
    return temperature

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/statistics')
def stats():
    #data = "CPU temperature ", getCPUtemperature()
    return os.popen("vcgencmd measure_temp").readline()

@app.route('/t')
def ttt():
    #data = "CPU temperature ", getCPUtemperature()
    return str(VAL)

@app.route('/room')
def roomTemperature():
    #data = "CPU temperature ", getCPUtemperature()
    humi, temp = sens.getHumidityAndTemperature(4)
    humi = round(humi,2)
    temp = round(temp,2)
    l.lcd_string("H: "+str(humi),lcd.LCD_LINE_1)
    l.lcd_string("T: "+str(temp),lcd.LCD_LINE_2)
    return 'Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temp, humi)

def tfunc():
    while 1:
        global VAL
        print('dupa' + str(VAL))
        VAL+=1
        time.sleep(10)

if __name__ == '__main__':

    x = threading.Thread(target=tfunc)
    x.daemon = True
    x.start()
    app.run(debug=True, host='0.0.0.0')