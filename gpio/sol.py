import RPi.GPIO as GPIO
import logging
class sol():
    def __init__(self, gpioList):
        self.m_List = gpioList

        GPIO.setmode(GPIO.BOARD)

        for item in self.m_List:
            GPIO.setup(item,GPIO.OUT)
            GPIO.output(item, False)

    def multiON(self, list):
        for item in list:
            #logging.info(str(item) +  " SOL OPEN")
            GPIO.output(self.m_List[item - 1], True)

    def multiOFF(self, list):
        for item in list:
            #logging.info(str(item) +  " SOL CLOSE")
            GPIO.output(self.m_List[item - 1], False)

    def ON(self, index, _log):
        if _log:
            logging.info(str(index) +  " SOL ON")

        GPIO.output(self.m_List[index - 1], True)

    def OFF(self, index, _log):
        if _log:
            logging.info(str(index) +  " SOL OFF")

        GPIO.output(self.m_List[index - 1], False)

