import psi
import pump
import time
import sol
def main():
    #INIT
    min = 1.3
    max = 1.94
    pumpGPIO = 7
    solGPIO= [11,13,15,29,31,33,35,37]
    mainPSI = psi.psi()
    mainPUMP = pump.pump(pumpGPIO)
    mainSOL = sol.sol(solGPIO)

    solOpenIndex = [2]
    
    try:
        
        print("MAIN START")

        mainSOL.multiON(solOpenIndex) 
        while(True):
            volt = mainPSI.getVoltage()
            if(volt >= min):
                mainPUMP.pumpOFF()
                print("now VOLT : ", volt)
                mainSOL.multiOFF(solOpenIndex) 
                break;
            else:
                mainPUMP.pumpON()

            time.sleep(0.01)

        while(True):
            volt = mainPSI.getVoltage()
            print("VOLT : ", volt)
            time.sleep(1)

    except KeyboardInterrupt:
        mainPSI.spiClose()
        mainPUMP.pumpClose()

main()
