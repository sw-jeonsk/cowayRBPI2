

import psi
import pump
import sol 
import RPi.GPIO as GPIO
import time
import constant



def main():
    m_psi = psi.psi()
    m_sol = sol.sol(constant.solGPIO)
    m_pump = pump.pump(constant.pumpGPIO)


    try:
        m_sol.ON(5, True)
        m_pump.pumpON(True)
        psi = 1.0

        while True:
            test_1 = m_psi.test_1()
            psi = m_psi.test_3()

            print("test_1 : " + str(test_1) + " test_3 " + str(psi))

            time.sleep(0.01)


    except KeyboardInterrupt:            
            GPIO.cleanup()




    
main()


