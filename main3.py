

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

    zone = [2,3,4,5]
    power = [2.0, 2.0, 2.0, 2.0]
    sumVolt = 0
    count = 0
    try:

        for _power, _zone in zip(power, zone):
            m_sol.ON(_zone, True)
            time.sleep(2)
            print("ZONE : " + str(_zone) + " POWER : " + str(_power) + " VOLT : " + str(sumVolt))

            while True:
                volt = m_psi.getVoltage()  
                sumVolt += volt
                count += 1
                print(str(volt))
                
                if count % 10 == 0:
                        
                    if sumVolt > _power:
                        m_sol.ON(1, True)
                        m_pump.pumpOFF(True)

                    else:
                        m_sol.OFF(1, True)
                        m_pump.pumpON(True)


                if abs(volt - _power) <= 0.1:
                    m_sol.OFF(1, True)
                    m_sol.OFF(_zone, True)
                    m_pump.pumpOFF(True)
                    break
                
                time.sleep(0.1)


    except KeyboardInterrupt:            
            GPIO.cleanup()




    
main()


