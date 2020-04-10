import RPi.GPIO as GPIO
import time

outcome = [0,-1,1,0,-1,0,0,1,1,0,0,-1,0,-1,1,0]
last_AB = 0b00
counter = 0
if __name__ == '__main__':

    GPIO.setwarnings(False)    # Ignore warning for now
    GPIO.setmode(GPIO.BCM)   

    GPIO.setup(17,GPIO.IN) #A
    GPIO.setup(27,GPIO.IN) #B
    GPIO.setup(22,GPIO.IN) #switch (chyba)

    while True:
        A = GPIO.input(17)
        B = GPIO.input(27)
        SW = GPIO.input(22)
        current_AB = (A<<1) | B
        position = (last_AB<<2) | current_AB
        counter += outcome[position]
        last_AB = current_AB

        outStr = "A: "+str(A)+" B: "+str(B)+" SW: "+str(SW) + "counter: "+ str(counter)
        print(outStr)
        time.sleep(0.001)



