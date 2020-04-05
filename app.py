from flask import Flask
import sensors.sensor_dht22 as sens
import os
import threading
import time
import display.lcd as lcd
from climate import climate as clmt
import display.display_controller as lcd_controller
import json



VAL = 0

l = lcd.lcd_display()

app = Flask(__name__)
c = clmt()


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
    humi = round(c.getHumidity(),2)
    temp = round(c.getTemperature(),2)

    l.lcd_clear()
    l.lcd_string("H: "+str(humi),lcd.LCD_LINE_1)
    l.lcd_string("T: "+str(temp),lcd.LCD_LINE_2)
    return 'Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temp, humi)

def tfunc():
    while 1:
        humi = round(c.getHumidity(),2)
        temp = round(c.getTemperature(),2)
        l.lcd_string("Humidity: "+str(humi)+"%",lcd.LCD_LINE_1)
        l.lcd_string("Temp: "+str(temp)+"*",lcd.LCD_LINE_2)
        print(humi,temp)
        time.sleep(5)

if __name__ == '__main__':

    #load configuration
    with open("config.json", "r") as read_file:
        data = json.load(read_file)
    print(data["displays"])

    lcdcont = lcd_controller.DisplayController(data["displays"])
    lcdcont.add_printout("lcd1",lcd_controller.Printout("test", "test1", "test2", 15))
   
    x = threading.Thread(target=tfunc)
    x.daemon = True
    x.start()
    c.start()
    app.run(debug=True, host='0.0.0.0')