#!/usr/bin/python
#--------------------------------------
#    ___  ___  _ ____
#   / _ \/ _ \(_) __/__  __ __
#  / , _/ ___/ /\ \/ _ \/ // /
# /_/|_/_/  /_/___/ .__/\_, /
#                /_/   /___/
#
#           bme280.py
#  Read data from a digital pressure sensor.
#
#  Official datasheet available from :
#  https://www.bosch-sensortec.com/bst/products/all_products/bme280
#
# Author : Matt Hawkins
# Date   : 21/01/2018
#
# https://www.raspberrypi-spy.co.uk/
#
#--------------------------------------
import smbus
import time
from ctypes import c_short
from ctypes import c_byte
from ctypes import c_ubyte
import w1thermsensor
import RPi.GPIO as GPIO
import Adafruit_DHT
import threading

GPIO.setmode(GPIO.BCM)
GPIO.setup(22, GPIO.OUT)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)
GPIO.output(22, GPIO.HIGH)
GPIO.output(27, GPIO.LOW)
GPIO.output(17, GPIO.LOW)

ambientH = 0
ambientT = 0

sensor = w1thermsensor.W1ThermSensor()
 
DEVICE = 0x76 # Default device I2C address


bus = smbus.SMBus(1) # Rev 2 Pi, Pi 2 & Pi 3 uses bus 1
                     # Rev 1 Pi uses bus 0

def getShort(data, index):
  # return two bytes from data as a signed 16-bit value
  return c_short((data[index+1] << 8) + data[index]).value

def getUShort(data, index):
  # return two bytes from data as an unsigned 16-bit value
  return (data[index+1] << 8) + data[index]

def getChar(data,index):
  # return one byte from data as a signed char
  result = data[index]
  if result > 127:
    result -= 256
  return result

def getUChar(data,index):
  # return one byte from data as an unsigned char
  result =  data[index] & 0xFF
  return result

def readBME280ID(addr=DEVICE):
  # Chip ID Register Address
  REG_ID     = 0xD0
  (chip_id, chip_version) = bus.read_i2c_block_data(addr, REG_ID, 2)
  return (chip_id, chip_version)

def readBME280All(addr=DEVICE):
  # Register Addresses
  REG_DATA = 0xF7
  REG_CONTROL = 0xF4
  REG_CONFIG  = 0xF5

  REG_CONTROL_HUM = 0xF2
  REG_HUM_MSB = 0xFD
  REG_HUM_LSB = 0xFE

  # Oversample setting - page 27
  OVERSAMPLE_TEMP = 2
  OVERSAMPLE_PRES = 2
  MODE = 1

  # Oversample setting for humidity register - page 26
  OVERSAMPLE_HUM = 2
  bus.write_byte_data(addr, REG_CONTROL_HUM, OVERSAMPLE_HUM)

  control = OVERSAMPLE_TEMP<<5 | OVERSAMPLE_PRES<<2 | MODE
  bus.write_byte_data(addr, REG_CONTROL, control)

  # Read blocks of calibration data from EEPROM
  # See Page 22 data sheet
  cal1 = bus.read_i2c_block_data(addr, 0x88, 24)
  cal2 = bus.read_i2c_block_data(addr, 0xA1, 1)
  cal3 = bus.read_i2c_block_data(addr, 0xE1, 7)

  # Convert byte data to word values
  dig_T1 = getUShort(cal1, 0)
  dig_T2 = getShort(cal1, 2)
  dig_T3 = getShort(cal1, 4)

  dig_P1 = getUShort(cal1, 6)
  dig_P2 = getShort(cal1, 8)
  dig_P3 = getShort(cal1, 10)
  dig_P4 = getShort(cal1, 12)
  dig_P5 = getShort(cal1, 14)
  dig_P6 = getShort(cal1, 16)
  dig_P7 = getShort(cal1, 18)
  dig_P8 = getShort(cal1, 20)
  dig_P9 = getShort(cal1, 22)

  dig_H1 = getUChar(cal2, 0)
  dig_H2 = getShort(cal3, 0)
  dig_H3 = getUChar(cal3, 2)

  dig_H4 = getChar(cal3, 3)
  dig_H4 = (dig_H4 << 24) >> 20
  dig_H4 = dig_H4 | (getChar(cal3, 4) & 0x0F)

  dig_H5 = getChar(cal3, 5)
  dig_H5 = (dig_H5 << 24) >> 20
  dig_H5 = dig_H5 | (getUChar(cal3, 4) >> 4 & 0x0F)

  dig_H6 = getChar(cal3, 6)

  # Wait in ms (Datasheet Appendix B: Measurement time and current calculation)
  wait_time = 1.25 + (2.3 * OVERSAMPLE_TEMP) + ((2.3 * OVERSAMPLE_PRES) + 0.575) + ((2.3 * OVERSAMPLE_HUM)+0.575)
  time.sleep(wait_time/1000)  # Wait the required time  

  # Read temperature/pressure/humidity
  data = bus.read_i2c_block_data(addr, REG_DATA, 8)
  pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
  temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
  hum_raw = (data[6] << 8) | data[7]

  #Refine temperature
  var1 = ((((temp_raw>>3)-(dig_T1<<1)))*(dig_T2)) >> 11
  var2 = (((((temp_raw>>4) - (dig_T1)) * ((temp_raw>>4) - (dig_T1))) >> 12) * (dig_T3)) >> 14
  t_fine = var1+var2
  temperature = float(((t_fine * 5) + 128) >> 8);

  # Refine pressure and adjust for temperature
  var1 = t_fine / 2.0 - 64000.0
  var2 = var1 * var1 * dig_P6 / 32768.0
  var2 = var2 + var1 * dig_P5 * 2.0
  var2 = var2 / 4.0 + dig_P4 * 65536.0
  var1 = (dig_P3 * var1 * var1 / 524288.0 + dig_P2 * var1) / 524288.0
  var1 = (1.0 + var1 / 32768.0) * dig_P1
  if var1 == 0:
    pressure=0
  else:
    pressure = 1048576.0 - pres_raw
    pressure = ((pressure - var2 / 4096.0) * 6250.0) / var1
    var1 = dig_P9 * pressure * pressure / 2147483648.0
    var2 = pressure * dig_P8 / 32768.0
    pressure = pressure + (var1 + var2 + dig_P7) / 16.0

  # Refine humidity
  humidity = t_fine - 76800.0
  humidity = (hum_raw - (dig_H4 * 64.0 + dig_H5 / 16384.0 * humidity)) * (dig_H2 / 65536.0 * (1.0 + dig_H6 / 67108864.0 * humidity * (1.0 + dig_H3 / 67108864.0 * humidity)))
  humidity = humidity * (1.0 - dig_H1 * humidity / 524288.0)
  if humidity > 100:
    humidity = 100
  elif humidity < 0:
    humidity = 0

  return temperature/100.0,pressure/100.0,humidity

def main():
  mode = "initial"
  fanmode = "freezing"
  freeze = True
  fanon = False

  iter = 0
 # (chip_id, chip_version) = readBME280ID()
 # print( "Chip ID     :", chip_id)
 # print( "Version     :", chip_version)
  while 1:
    temperature,pressure,humidity = readBME280All()

 # print ("Temperature : ", temperature, "C")
 # print ("Pressure : ", pressure, "hPa")
 # print ("Humidity : ", humidity, "%")
#  while 1:
    iter+=1
    coldPlateTemp = sensor.get_temperature()

    #if iter%2==0:
    #  GPIO.output(22, GPIO.HIGH)
    #else:
    #  GPIO.output(22, GPIO.LOW)

    #if iter%3==0:
    #  GPIO.output(17, GPIO.HIGH)
    #  GPIO.output(27, GPIO.LOW)
    #else:
    #  GPIO.output(17, GPIO.LOW)
    #  GPIO.output(27, GPIO.HIGH)
    targetColdPlateTemp = -10.0
    targetInsideTemp = 4.0


    if coldPlateTemp > -2.0 and mode == "initial":
      freeze = True #GPIO.output(22, GPIO.LOW) #mrozimy
    else:
      mode = "staycold"
  
    if mode == "staycold":
      if coldPlateTemp > -7.5:
        freeze = True#GPIO.output(22, GPIO.LOW) #mrozimy
      else:
        if coldPlateTemp<-13.0:
          freeze = False#GPIO.output(22, GPIO.HIGH) #nie mrozimy


    
      #fan steering
    if mode == "staycold":
      if fanmode == "freezing":
        if temperature <3.5:
          fanon = False#fanoff
          fanmode = "heating"
        else:
          fanon = True
      else: #heating
        if temperature > 4.5:
          fanmode = "freezing"
          fanon = True
        else:
          fanon = False

    if freeze:
      GPIO.output(22, GPIO.LOW)
    else:
      GPIO.output(22, GPIO.HIGH)

    if fanon:
      GPIO.output(17, GPIO.HIGH)
    else:
      GPIO.output(17, GPIO.LOW)
    

    if humidity < 80.0:
      GPIO.output(27, GPIO.HIGH)
    if humidity > 85.0:
      GPIO.output(27, GPIO.LOW)


    #print (iter," T: ",temperature," H: ", humidity,"\t cold plate temp: ",coldPlateTemp,"\tfan: ",fanon,"\tfreeze:",freeze,"at:",ambientT)
    print (iter,"\t",round(temperature,2),"\t", round(humidity,2),"\t\t",round(coldPlateTemp,2),"\t\t",int(fanon),"\t",int(freeze),"\t",round(ambientT,2))
    #print ("ambient temperature: ",ambientT,"\t ambient humidity",ambientH)   
    time.sleep(1)

def ambientMeasurements():
  global ambientH
  global ambientT
  while True:
    h, t = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 26)
    ambientT = t
    ambientH = h
    if ambientH is None or ambientT is None:
      print("sensor problem")
    #print("readings",t,"h",h)

    time.sleep(2)

if __name__=="__main__":
  try:
    x = threading.Thread(target=ambientMeasurements)
    x.daemon = True
    x.start()
    main()
  except Exception as e:
    print(e)
  except KeyboardInterrupt:  
    pass
  finally:
    GPIO.cleanup() # this ensures a clean exit  
