import RPi.GPIO as GPIO
import logging

class purifier():
    def __init__(self, _gpio):
        self.m_purifier = _gpio

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.m_purifier,GPIO.OUT)
        GPIO.output(self.m_purifier, False)


    def ON(self, log):
        if log:
            logging.info("PURIFIER ON")
        GPIO.output(self.m_purifier, True)

    def OFF(self, log):
        if log:
            logging.info("PURIFIER OFF")
        GPIO.output(self.m_purifier, False)

    def Close(self):
        GPIO.cleanup()
