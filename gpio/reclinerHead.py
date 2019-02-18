import RPi.GPIO as GPIO
import logging

class reclinerHead():
    def __init__(self, reclinerGPIO):
        
        self.reclinerUP = reclinerGPIO[0]
        self.reclinerDOWN = reclinerGPIO[1]

        GPIO.setmode(GPIO.BOARD)

        GPIO.setup(self.reclinerUP,GPIO.OUT)
        GPIO.setup(self.reclinerDOWN,GPIO.OUT)
        GPIO.output(self.reclinerUP, False)
        GPIO.output(self.reclinerDOWN, False)

    def UP(self):
        GPIO.output(self.reclinerUP, True)

    def STOP(self):
        GPIO.output(self.reclinerUP, False)
        GPIO.output(self.reclinerDOWN, False)

    def DOWN(self):
        GPIO.output(self.reclinerDOWN, True)

    def headClose(self):
        GPIO.cleanup()
