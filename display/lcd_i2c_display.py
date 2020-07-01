# import
import RPi.GPIO as GPIO
import os
import socket
import fcntl
import struct
import time
from time import gmtime, strftime
from display.lcd_printout import Printout
from copy import copy
import display.I2C_LCD_driver as I2C_LCD_driver
from time import *

# To config file:
#"displays" : 
#    [
#        {
#            "type" : "LCD",
#            "id" : "lcd1",
#            "interface" : "i2c",
#            "position": 
#            {
#                "RS": 7,
#                "E":  8,
#                "D4" : 25,
#                "D5" : 24,
#                "D6" : 23,
#                "D7" : 18
#            }
#        }
#    ],



# Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80  # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0  # LCD RAM address for the 2nd line

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

class LcdI2CDisplay:

    printouts = []
    immediately = False

    current_counter_index = 0
    printout_time = 0
    im_printout_time = 0
    current_printout = Printout("","","",0)
    
    disp = 0

    def __init__(self, config):
        print("config file below")
        print(config)

        self.disp = I2C_LCD_driver.lcd()
        print("display id "+ self.display_id+" created")

    def print_immediately(self, printout: Printout):
        self.immediately = True
        self.immediately_printout = printout

    def update_printout_data(self, printout: Printout):
        found = False
        for p in range(len(self.printouts)):
            if self.printouts[p].id == printout.id:
                self.printouts[p] = printout
                found = True
        if not found:
            self.printouts.append(printout)

    def update(self): # this method should be invoke every 1s 
        #print("LCD update")
        #print("length: ",len(self.printouts), self.printout_time)
        if self.immediately:
            self.lcd_clear()
            self.lcd_string(self.immediately_printout)
            if self.im_printout_time < self.immediately_printout.duration:
                self.im_printout_time += 1
            else:
                self.im_printout_time = 0
                self.immediately = False
        else:
            
            if len(self.printouts) > 0 and self.current_counter_index < len(self.printouts):
                
                self.lcd_string(self.printouts[self.current_counter_index])

                if self.printout_time < self.printouts[self.current_counter_index].duration:
                    self.printout_time += 1
                else:
                    self.printout_time = 0
                    if len(self.printouts)-1 == self.current_counter_index:
                        self.current_counter_index = 0
                    else:
                        self.current_counter_index += 1
                

    def lcd_init(self):
        self.disp.lcd_clear()

    def lcd_clear(self):
        self.disp.lcd_clear()

    def lcd_string(self, printout: Printout):
        
        if not self.current_printout == printout:
            self.current_printout = copy(printout)
            self.lcd_clear()
        
        # Cast to string
        message1 = str(printout.firstLine)
        message2 = str(printout.secondLine)
        self.disp.lcd_display_string(message1, 1)
        self.disp.lcd_display_string(message2, 2)
        

    