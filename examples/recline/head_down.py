import reclinerFoot
import reclinerHead
import time

count = 0
headGPIO = [32, 26]
footGPIO = [22, 18]
#recline....






 
def main():
    global count

    mainHEAD = reclinerHead.reclinerHead(headGPIO)
    mainFOOT = reclinerFoot.reclinerFoot(footGPIO)

    

    try:
        mainHEAD.DOWN()


        while True:
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
