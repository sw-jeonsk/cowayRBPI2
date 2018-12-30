import RPi.GPIO as GPIO
import logging


class reclinerFoot():
    def __init__(self, reclinerGPIO):
        
        self.reclinerUP = reclinerGPIO[0]
        self.reclinerDOWN = reclinerGPIO[1]

        GPIO.setmode(GPIO.BOARD)

        GPIO.setup(self.reclinerUP,GPIO.OUT)
        GPIO.setup(self.reclinerDOWN,GPIO.OUT)
        GPIO.output(self.reclinerUP, False)
        GPIO.output(self.reclinerDOWN, False)

    def UP(self):
        logging.info("FOOT UP")
        GPIO.output(self.reclinerUP, True)

    def STOP(self):
        logging.info("FOOT STOP")
        GPIO.output(self.reclinerUP, False)
        GPIO.output(self.reclinerDOWN, False)

    def DOWN(self):
        logging.info("FOOT DOWN")
        GPIO.output(self.reclinerDOWN, True)

    def footClose(self):
        GPIO.cleanup()
