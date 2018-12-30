import RPi.GPIO as GPIO
import logging
class sol():
    def __init__(self, gpioList):
        self.m_List = gpioList
        self.m_outlet = gpioList[0]
        GPIO.setmode(GPIO.BOARD)

        for item in self.m_List:
            GPIO.setup(item,GPIO.OUT)
            GPIO.output(item, False)

    def multiON(self, list):
        for item in list:
            logging.info(str(item) + " SOL OPEN")
            GPIO.output(self.m_List[item - 1], True)

    def multiOFF(self, list):
        for item in list:
            logging.info(str(item), " SOL CLOSE")
            GPIO.output(self.m_List[item - 1], False)

    def ON(self, index):
        logging.info(str(index) + " SOL OPEN")
        GPIO.output(self.m_List[index - 1], True)

    def OFF(self, index):
        logging.info(str(index) + " SOL CLOSE")
        GPIO.output(self.m_List[index - 1], False)

    def OUTLET(self):
        logging.info(str(self.m_outlet) + " OUTLET OPEN")
        GPIO.output(self.m_outlet, False) 