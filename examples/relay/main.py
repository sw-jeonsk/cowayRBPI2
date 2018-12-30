import relay
import sys
import time
relayGPIO = [22, 18, 16, 38]

def main(sys1):

    mainRELAY = relay.relay(relayGPIO)

    mainRELAY.relayON(int(sys1))
    

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        mainRELAY.relayOFF(int(sys1))
        mainRELAY.relayClose()        

if __name__ == "__main__":
    main(sys.argv[1])