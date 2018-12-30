import RPi.GPIO as GPIO


class relay():
    def __init__(self, _gpio):

        self.m_relayList = _gpio

        GPIO.setmode(GPIO.BOARD)

        for item in self.m_relayList:
            GPIO.setup(item,GPIO.OUT)
            GPIO.output(item, False)


    def relayON(self, index):
        print("RELAY INDEX ON ", index)
        GPIO.output(self.m_relayList[index-1], True)

    def relayOFF(self, index):
        print("RELAY INDEX OFF ", index)
        GPIO.output(self.m_relayList[index-1], False)

    def relayClose(self):
        GPIO.cleanup()