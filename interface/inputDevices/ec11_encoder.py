import RPi.GPIO as GPIO
import time
from input_controller import InputDevice
from input_controller import InputEvent
from queue import Queue

class InputEncoderEC11(InputDevice):
    outcome = [0,1,-1,0,-1,0,0,1,1,0,0,-1,0,-1,1,0]
   
    last_AB = 0b00
    lastCounter = 0
    counter = 0
    co = 0
    realValue=0

    def __init__(self, config):
        self.inputA = config["position"]["A"]
        self.inputB = config["position"]["B"]
        self.inputC = config["position"]["C"]
        self.id = config["id"]
        GPIO.setwarnings(False)    # Ignore warning
        GPIO.setmode(GPIO.BCM)   

        GPIO.setup(self.inputA,GPIO.IN) #A
        GPIO.setup(self.inputB,GPIO.IN) #B
        GPIO.setup(self.inputC,GPIO.IN) #switch (chyba)

    def update(self, eventQueue: Queue):
        A = GPIO.input(self.inputA)
        B = GPIO.input(self.inputB)
        SW = GPIO.input(self.inputC)
        current_AB = (A<<1) | B
        position = (self.last_AB<<2) | current_AB
        self.counter += self.outcome[position]
        self.last_AB = current_AB
        if co%100 == 0:
            if lastCounter < counter:
                realValue += 1
                lastCounter = counter
                eventQueue.put_nowait(InputEvent(self.id,"up"))
            elif lastCounter > counter:
                realValue -= 1
                lastCounter = counter
                eventQueue.put_nowait(InputEvent(self.id,"down"))
            co = 0
        co+=1
