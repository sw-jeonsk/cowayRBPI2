import RPi.GPIO as GPIO


class pump():
    def __init__(self, _gpio):

        self.m_pump = _gpio

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.m_pump,GPIO.OUT)
        GPIO.output(self.m_pump, False)


    def pumpON(self):
        GPIO.output(self.m_pump, True)

    def pumpOFF(self):
        GPIO.output(self.m_pump, False)

    def pumpClose(self):
        GPIO.cleanup()