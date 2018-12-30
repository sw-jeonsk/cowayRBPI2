import RPi.GPIO as GPIO
import time


PUMP_EN = 7

GPIO.setmode(GPIO.BOARD)


GPIO.setup(PUMP_EN, GPIO.OUT)
GPIO.output(PUMP_EN, False)


#GPIO.output(DOOR_EN[0], True)
#GPIO.output(DOOR_EN[1], True)
#GPIO.output(PUMP_EN, True)
#GPIO.output(DOOR_EN[3], True)


try:
    print("pump ON")
    while True:
        time.sleep(1)

except KeyboardInterrupt:
	GPIO.cleanup()
	print("Quit")



