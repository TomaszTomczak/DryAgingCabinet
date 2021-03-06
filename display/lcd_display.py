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

# To config file:
#"displays" : 
#    [
#        {
#            "type" : "LCD",
#            "id" : "lcd1",
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

class LcdDisplay:

    printouts = []
    immediately = False

    current_counter_index = 0
    printout_time = 0
    im_printout_time = 0
    current_printout = Printout("","","",0)
    
    def __init__(self, config):
        print("config file below")
        print(config)
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
        self.LCD_E = config['position']['E']
        
        self.LCD_RS = config['position']['RS']
        self.LCD_D4 = config['position']['D4']
        self.LCD_D5 = config['position']['D5']
        self.LCD_D6 = config['position']['D6']
        self.LCD_D7 = config['position']['D7']

        GPIO.setup(self.LCD_E, GPIO.OUT)  # E
        GPIO.setup(self.LCD_RS, GPIO.OUT)  # RS
        GPIO.setup(self.LCD_D4, GPIO.OUT)  # DB4
        GPIO.setup(self.LCD_D5, GPIO.OUT)  # DB5
        GPIO.setup(self.LCD_D6, GPIO.OUT)  # DB6
        GPIO.setup(self.LCD_D7, GPIO.OUT)  # DB7
        self.display_id = config['id']
        self.lcd_init()  # Initialise display
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
        # Initialise display
        self.lcd_byte(0x33, LCD_CMD)  # 110011 Initialise
        self.lcd_byte(0x32, LCD_CMD)  # 110010 Initialise
        self.lcd_byte(0x06, LCD_CMD)  # 000110 Cursor move direction
        self.lcd_byte(0x0C, LCD_CMD)  # 001100 Display On,Cursor Off, Blink Off
        # 101000 Data length, number of lines, font size
        self.lcd_byte(0x28, LCD_CMD)
        self.lcd_byte(0x01, LCD_CMD)  # 000001 Clear display
        time.sleep(E_DELAY)

    def lcd_byte(self, bits, mode):

        GPIO.output(self.LCD_RS, mode)  # RS
        # High bits
        GPIO.output(self.LCD_D4, False)
        GPIO.output(self.LCD_D5, False)
        GPIO.output(self.LCD_D6, False)
        GPIO.output(self.LCD_D7, False)
        if bits & 0x10 == 0x10:
            GPIO.output(self.LCD_D4, True)
        if bits & 0x20 == 0x20:
            GPIO.output(self.LCD_D5, True)
        if bits & 0x40 == 0x40:
            GPIO.output(self.LCD_D6, True)
        if bits & 0x80 == 0x80:
            GPIO.output(self.LCD_D7, True)

        # Toggle 'Enable' pin
        self.lcd_toggle_enable()

        # Low bits
        GPIO.output(self.LCD_D4, False)
        GPIO.output(self.LCD_D5, False)
        GPIO.output(self.LCD_D6, False)
        GPIO.output(self.LCD_D7, False)
        if bits & 0x01 == 0x01:
            GPIO.output(self.LCD_D4, True)
        if bits & 0x02 == 0x02:
            GPIO.output(self.LCD_D5, True)
        if bits & 0x04 == 0x04:
            GPIO.output(self.LCD_D6, True)
        if bits & 0x08 == 0x08:
            GPIO.output(self.LCD_D7, True)

        # Toggle 'Enable' pin
        self.lcd_toggle_enable()

    def lcd_toggle_enable(self):
        # Toggle enable
        time.sleep(E_DELAY)
        GPIO.output(self.LCD_E, True)
        time.sleep(E_PULSE)
        GPIO.output(self.LCD_E, False)
        time.sleep(E_DELAY)

    def lcd_clear(self):
        self.lcd_byte(0x01, LCD_CMD)

    def lcd_string(self, printout: Printout):
        
        if not self.current_printout == printout:
            self.current_printout = copy(printout)
            self.lcd_clear()
        
        # Cast to string
        message1 = str(printout.firstLine)
        message2 = str(printout.secondLine)
        # Send string to display
        # print("> "+message)
        message1 = message1.ljust(LCD_WIDTH, " ")
        message2 = message2.ljust(LCD_WIDTH, " ")

        self.lcd_byte(LCD_LINE_1, LCD_CMD)
        for i in range(LCD_WIDTH):
            self.lcd_byte(ord(message1[i]), LCD_CHR)
        self.lcd_byte(LCD_LINE_2, LCD_CMD)
        for i in range(LCD_WIDTH):
            self.lcd_byte(ord(message2[i]), LCD_CHR)

    