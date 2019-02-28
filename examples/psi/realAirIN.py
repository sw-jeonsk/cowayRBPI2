

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
    power = [2.5, 2.5, 2.5, 2.5]
    sumVolt = 0
    count = 0
    air = "OUT"
    voltList = []
    
    try:

        for _power, _zone in zip(power, zone):
            m_sol.ON(_zone, True)
            time.sleep(1)
            
            for i in range(0,5):
                volt = m_psi.getVoltage()
                voltList.append(volt)
                time.sleep(0.1)


            avg_volt = average(voltList)   
                
            print("ZONE : " + str(_zone) + " POWER : " + str(_power) + " VOLT : " + str(avg_volt))
            count = 0
            
            if (_power > avg_volt):
                print("IN")
                m_pump.pumpON(True)
                m_sol.OFF(1, True)
                air = "IN"
            else :
                print("OUT")
                m_pump.pumpOFF(True)
                m_sol.ON(1, True)
                air = "OUT"

            voltList = [] 
            while True:
                volt = m_psi.getVoltage()  
                
                if(len(voltList) == 5):
                    del voltList[0]
                    voltList.append(volt)
                    
                    avg_volt = average(voltList)
                
                if air == "IN":
                    if(volt - _power) > 0:
                        m_pump.pumpOFF(True)
                        m_sol.OFF(1, True)
                        break
                    
                if air == "OUT":
                    if(volt - _power) < 0:
                        m_pump.pumpOFF(True)
                        m_sol.OFF(1, True)
                        break

                    
                    
                voltList.append(volt)
                
                print(str(volt))
                
                time.sleep(0.01)


    except KeyboardInterrupt:            
            GPIO.cleanup()


def average(_list):
    value = 0
    for item in _list:
        value += item
        
    return round(value/len(_list), 1)

main()


