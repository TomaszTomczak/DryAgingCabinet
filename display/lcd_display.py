# import
import RPi.GPIO as GPIO
import os
import socket
import fcntl
import struct
import time
from time import gmtime, strftime
from display.lcd_printout import Printout

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

    def print_immediately(self, printout: Printout):
        pass

    def update_printout_data(self, printout: Printout):
        found = False
        for p in self.printouts:
            if printout.id == p.id:
                p = printout
                found = True
            if not found:
                self.printouts.append(printout)

    def update(self):
        pass

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

    def lcd_string(self, message, line):
        # Cast to string
        message = str(message)
        # Send string to display
        message = message.ljust(LCD_WIDTH, " ")
        self.lcd_byte(line, LCD_CMD)

        for i in range(LCD_WIDTH):
            self.lcd_byte(ord(message[i]), LCD_CHR)

    