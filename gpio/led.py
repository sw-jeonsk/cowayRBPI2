import RPi.GPIO as GPIO
import time
import logging


class led():
    def __init__(self, _gpio, _frequency):

        self.m_ledgpio = _gpio

        GPIO.setmode(GPIO.BOARD)

        GPIO.setup(self.m_ledgpio,GPIO.OUT)
        self.m_pwm = GPIO.PWM(self.m_ledgpio, _frequency)
        GPIO.output(self.m_ledgpio , False)
        self.PWMStart(0)

    def PWMStart(self, value):
        self.m_pwm.start(value)        
    
    def PWMStop(self):
        self.m_pwm.stop()

    def ledPWM(self, dc):
        self.m_pwm.ChangeDutyCycle(dc)    
    
    def ledON(self):
        logging.info("LED INDEX ON")

        for dc in range(0, 101, 2):
            self.m_pwm.ChangeDutyCycle(dc)
            time.sleep(0.4)

    def ledOFF(self):
        logging.info("LED INDEX OFF")
        for dc in range(100, -1, -1):
            self.m_pwm.ChangeDutyCycle(dc)
            time.sleep(0.8)

    def ledClose(self):
        self.PWMStop()
        GPIO.cleanup()
