

from gpio import psi
from gpio import pump
from gpio import sol
import RPi.GPIO as GPIO
import time
import constant
import logging
logging.basicConfig(filename='/home/pi/Desktop/github/cowayRBPI2/examples/psi/log/psiCheck.log', 
filemode='a', level=logging.DEBUG, format='[%(asctime)s][%(levelname)s] %(message)s')


def main():
    m_psi = psi.psi()
    m_sol = sol.sol(constant.solGPIO)
    m_pump = pump.pump(constant.pumpGPIO)

    zone = [2,3,4,5]
    power = [2.0, 2.0, 2.0, 2.0]
    sumVolt = 0
    count = 0
    try:

        for _power, _zone in zip(power, zone):
            m_sol.ON(_zone, True)
            time.sleep(2)
            print("ZONE : " + str(_zone) + " POWER : " + str(_power) + " VOLT : " + str(sumVolt))

            count = 0

            while True:
                volt = m_psi.getVoltage()  
                
                print("zone : " + str(_zone - 1) + " " + str(volt))
                
                count += 1

                if(count > 50):
                    break
                
                time.sleep(0.1)


    except KeyboardInterrupt:            
            GPIO.cleanup()




    
main()


