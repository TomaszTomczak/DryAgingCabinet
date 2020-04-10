import RPi.GPIO as GPIO
import time

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
        outStr = "A: "+str(A)+" B: "+str(B)+" SW: "+str(SW)
        print(outStr)
        time.sleep(0.01)



