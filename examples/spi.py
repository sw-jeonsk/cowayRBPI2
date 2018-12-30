import spidev
spi = spidev.SpiDev()
spi.open(0,1)
result = spi.xfer([0, 1, 2, 3, 4, 5, 0xA, 0xB, 0xC, 0xD, 0xE])
print(result)


