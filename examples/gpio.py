import RPi.GPIO as GPIO
import time


pump = 7
sol = 29
sol1 = 31

GPIO.setmode(GPIO.BOARD)


GPIO.setup(pump, GPIO.OUT)
GPIO.setup(sol, GPIO.OUT)
GPIO.setup(sol1, GPIO.OUT)
GPIO.output(pump, False)
GPIO.output(sol, False)
GPIO.output(sol1, False)
GPIO.cleanup()



