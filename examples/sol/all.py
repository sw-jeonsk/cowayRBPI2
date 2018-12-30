import sys
import RPi.GPIO as GPIO
import time


sol= [11,13,15,29,31,33,35,37]

def main():
    GPIO.setmode(GPIO.BOARD)

    for s in sol:
        GPIO.setup(s, GPIO.OUT)
        GPIO.output(s, True)



    try:
        print("ALL SOL OPEN")
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        GPIO.cleanup()
        print("Quit")

if __name__ == "__main__":
    main()
