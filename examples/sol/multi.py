import sys
import RPi.GPIO as GPIO
import time


sol= [11,13,15,29,31,33,35,37]

def main(strNumber1, strNumber2):
    index1 = int(strNumber1) - 1
    index2 = int(strNumber2) - 1
    GPIO.setmode(GPIO.BOARD)

    for s in sol:
        GPIO.setup(s, GPIO.OUT)
        GPIO.output(s, False)

    GPIO.output(sol[index1], True)
    GPIO.output(sol[index2], True)


    try:
        print(strNumber1," SOL OPEN  ",sol[index1] )
        print(strNumber2," SOL OPEN  ",sol[index2] )
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        GPIO.cleanup()
        print("Quit")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
