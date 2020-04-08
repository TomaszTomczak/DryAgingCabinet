from flask import Flask
import sensors.sensor_dht22 as sens
import os
import threading
import time

from climate import climate as clmt
import display.display_controller as lcd_controller
import json



VAL = 0

lcdcont = lcd_controller.DisplayController()
climatePrintout = lcd_controller.Printout("tempandhum", "", "", 4)
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

    
    return 'Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temp, humi)

def tfunc():
    while 1:
        humi = round(c.getHumidity(),2)
        temp = round(c.getTemperature(),2)
        tstr = "Temp: "+str(temp)+"*"
        hstr = "Humidity: "+str(humi)+"%"
        #lcdcont.update_printout_data('lcd1',lcd_controller.Printout("temperature", tstr , hstr, 2))
        climatePrintout.firstLine=tstr
        climatePrintout.secondLine=hstr
        lcdcont.update()
        print(humi,temp)
        time.sleep(5)

if __name__ == '__main__':

    #load configuration
    with open("config.json", "r") as read_file:
        data = json.load(read_file)
    print(data["displays"])


    lcdcont.configure(data["displays"])
    lcdcont.update_printout_data('lcd1',lcd_controller.Printout("test", "test1", "test2", 2))
    lcdcont.update_printout_data('lcd1',lcd_controller.Printout("test123", "test55", "test66", 3))
    lcdcont.update_printout_data('lcd1',climatePrintout)
    print(lcdcont.get_displays_id())
    x = threading.Thread(target=tfunc)
    x.daemon = True
    x.start()
    c.start()
    app.run(debug=True, host='0.0.0.0')