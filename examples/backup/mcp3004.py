import spidev
import time

#Establish SPI connection with Bus 0, Device 0
spi = spidev.SpiDev()
spi.open(0,1)

def get_adc(channel):
    #Perform SPI transaction and store returned bits in 'r'
    r = spi.xfer([1, (8+channel)<<4, 0])
    #Filter data bits from returned bits
    adcout = ((r[1]&3) << 8) + r[2]
    #Return value from 0-1023
    return adcout

while True:
    print get_adc(0)
    time.sleep(1)
