

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

    zone = [2,3,4,5]
    power = [-1, -1, -1, 0.0]
    sumVolt = 0
    count = 0
    air = "OUT"
    voltList = []
    
    try:

        for _power, _zone in zip(power, zone):

            if _power == -1:
                continue
            m_sol.ON(_zone, True)
            time.sleep(1)
            
            for i in range(0,5):
                volt = m_psi.test_3()
                print(str(volt))
                voltList.append(volt)
                time.sleep(0.01)


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
                volt = m_psi.test_3()  
                
                if(len(voltList) == 10):
                    del voltList[0]
                    voltList.append(volt)
                    
                    avg_volt = average(voltList)
                    print(str(avg_volt))
                else:    
                    voltList.append(volt)
                
                if air == "IN":
                    if(avg_volt * 0.67  - _power) > 0:
                        m_pump.pumpOFF(True)
                        m_sol.OFF(1, True)
                        break
                    
                if air == "OUT":
                    if(avg_volt * 1.7 - _power) < 0 or (avg_volt <= 0.3):
                        m_pump.pumpOFF(True)
                        m_sol.OFF(1, True)
                        break


                    
                    
                #print(str(volt))
                
                time.sleep(0.01)


    except KeyboardInterrupt:            
            GPIO.cleanup()


def average(_list):
    value = 0
    for item in _list:
        value += item
        
    return round(value/len(_list), 1)

main()


