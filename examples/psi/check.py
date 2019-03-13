

import psi
import pump
import sol
import RPi.GPIO as GPIO
import time
import constant
import logging
#logging.basicConfig(filename='/home/pi/Desktop/github/cowayRBPI2/examples/psi/log/psiCheck.log', 
#filemode='a', level=logging.DEBUG, format='[%(asctime)s][%(levelname)s] %(message)s')


def main():
    m_psi = psi.psi()
    m_sol = sol.sol(constant.solGPIO)
    m_pump = pump.pump(constant.pumpGPIO)

    zone = [2,3,4,5]
    power = [2.0, 2.0, 2.0, 2.0]
    sumVolt = 0
    count = 0
    try:
        m_sol.ON(5,True)
        #m_sol.ON(5,True)
        #m_pump.pumpON(True)

        while True:

            volt = m_psi.getVoltage()  
            test_3 = m_psi.test_3()  

            print("VOLT : " + str(volt) + " TEST_3 : " + str(test_3))
            
            
            time.sleep(0.5)


    except KeyboardInterrupt:            
            GPIO.cleanup()




    
main()


