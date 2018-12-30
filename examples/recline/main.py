import reclinerFoot
import reclinerHead
import time

count = 0
headGPIO = [32, 26]
footGPIO = [22, 18]
#recline....






 
def main():

    mainHEAD = reclinerHead.reclinerHead(headGPIO)
    mainFOOT = reclinerFoot.reclinerFoot(footGPIO)

    

    try:
        #mainHEAD.UP()
        mainHEAD.DOWN()

        #mainFOOT.UP()
        mainFOOT.DOWN()

        while count < 10:
            global count
            count += 1
            time.sleep(1)
        mainHEAD.headClose()
        mainFOOT.footClose()
        
    except KeyboardInterrupt:
        print("close")
        mainHEAD.headClose()
        mainFOOT.footClose()

if __name__ == "__main__":
    main()
