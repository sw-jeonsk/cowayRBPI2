import led
import time
ledGPIO = 12
frequency = 1000

def main():

    mainLED = led.led(ledGPIO, frequency)

    

    try:
        while True:
            mainLED.ledON()
            time.sleep(5)
            mainLED.ledOFF()

    except KeyboardInterrupt:
        print("close")
        mainLED.ledClose()        

if __name__ == "__main__":
    main()
