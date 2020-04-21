import RPi.GPIO as GPIO
import time

outcome = [0,1,-1,0,-1,0,0,1,1,0,0,-1,0,-1,1,0]
# rot_enc_table[]= {0,1,-1,0,-1,0,0,1,1,0,0,-1,0,-1,1,0};
last_AB = 0b00
lastCounter = 0
counter = 0
if __name__ == '__main__':

    GPIO.setwarnings(False)    # Ignore warning for now
    GPIO.setmode(GPIO.BCM)   

    GPIO.setup(27,GPIO.IN) #A
    GPIO.setup(22,GPIO.IN) #B
    GPIO.setup(10,GPIO.IN) #switch (chyba)

#check every 10 loops if value was changed and step it. It will buffer output and reduce noise

    while True:
        A = GPIO.input(27)
        B = GPIO.input(22)
        SW = GPIO.input(10)
        current_AB = (A<<1) | B
        position = (last_AB<<2) | current_AB
        counter += outcome[position]
        last_AB = current_AB

        outStr = "A: "+str(A)+" B: "+str(B)+" SW: "+str(SW) + "counter: "+ str(counter)
        if not counter == lastCounter:
            print(outStr)
            lastCounter = counter
        time.sleep(0.001)



