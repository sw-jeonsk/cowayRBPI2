import RPi.GPIO as GPIO
import time


gpio = 12

GPIO.setmode(GPIO.BOARD)


GPIO.setup(gpio, GPIO.OUT)
GPIO.output(gpio, True)




try:
    print("ON ", gpio)
    while True:
        time.sleep(1)

except KeyboardInterrupt:
	GPIO.cleanup()
	print("Quit")



