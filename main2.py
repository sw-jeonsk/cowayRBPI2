

from gpio import psi
from gpio import pump
from gpio import sol
import RPi.GPIO as GPIO
import time
import constant



def main():
    m_psi = psi.psi()
    m_sol = sol.sol(constant.solGPIO)
    m_pump = pump.pump(constant.pumpGPIO)


    try:
        m_sol.ON(4, True)
        m_pump.pumpON(True)

        while True:
            volt = m_psi.getVoltage()

            print("value : " + str(volt))

            time.sleep(0.1)


    except KeyboardInterrupt:            
            GPIO.cleanup()




    
main()


