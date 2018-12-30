import RPi.GPIO as GPIO
import time


class led():
    def __init__(self, _gpio, _frequency):

        self.m_ledgpio = _gpio

        GPIO.setmode(GPIO.BOARD)

        GPIO.setup(self.m_ledgpio,GPIO.OUT)
        self.m_pwm = GPIO.PWM(self.m_ledgpio, _frequency)
        GPIO.output(self.m_ledgpio , False)

        self.m_pwm.start(100)
    def ledON(self):
        print("LED INDEX ON ", self.m_ledgpio)

        for dc in range(0, 101, 2):
            self.m_pwm.ChangeDutyCycle(dc)
            time.sleep(0.4)

    def ledOFF(self):
        print("LED INDEX OFF ", self.m_ledgpio)
        for dc in range(100, -1, -1):
            self.m_pwm.ChangeDutyCycle(dc)
            time.sleep(0.8)

    def ledClose(self):
        self.m_pwm.stop()
        GPIO.cleanup()
