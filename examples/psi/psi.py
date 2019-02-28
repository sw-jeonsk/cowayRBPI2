import spidev
from time import sleep


# First open up SPI bus
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz=50000

# Initialize what sensor is where

class psi():

    def __init__(self):
        self.m_spi = spidev.SpiDev()    
        self.m_spi.open(0,0)
        self.m_spi.max_speed_hz = 50000
        self.m_channel = 0

    def read(self):
        # First pull the raw data from the chip
        rawData = self.m_spi.xfer([1, (8 + self.m_channel) << 4, 0])
        # Process the raw data into something we understand.
        processedData = ((rawData[1] & 3) << 8) + rawData[2]
        return processedData
    
    #original
    def convertVoltage(self, bitValue, decimalPlaces=2):
        voltage = (bitValue * 3.3) / float(1023)
        voltage = round(voltage, decimalPlaces)

        return voltage

        
    def getVoltage(self):
        data = self.read()
        voltage = self.convertVoltage(data)

        return voltage

    #1 : voltage 계산을 4.5로 변경 
    def test_1(self, decimalPlaces=2):
        data = self.read()
        voltage = (data * 4.5) / float(1023)
        voltage = round(voltage, decimalPlaces)
        return voltage  


    #2 : psi 계산 공식 적용
    def test_2(self, decimalPlaces=2):
        data = self.read()
        voltage = (data * 3.3) / float(1023)
        voltage = round(voltage, decimalPlaces)

        if (voltage < 0.5):
            psi = 0
        else:
            psi = round((voltage - 0.5) * 10 / 8, decimalPlaces)

        return psi      

    #3 : psi 계산 공식 적용  + voltage 계산을 4.5로 변경
    def test_3(self, decimalPlaces=2):
        data = self.read()
        voltage = (data * 4.5) / float(1023)
        voltage = round(voltage, decimalPlaces)

        if (voltage < 0.5):
            psi = 0
        else:
            psi = round((voltage - 0.5) * 10 / 8, decimalPlaces)

        return psi  


    def spiClose(self):
        self.m_spi.close()

# def getReading(channel):
#     # First pull the raw data from the chip
#     rawData = spi.xfer([1, (8 + channel) << 4, 0])
#     # Process the raw data into something we understand.
#     processedData = ((rawData[1] & 3) << 8) + rawData[2]
#     return processedData


# def convertVoltage(bitValue, decimalPlaces=2):
#     voltage = (bitValue * 3.3) / float(1023)
#     voltage = round(voltage, decimalPlaces)
#     return voltage


# def convertTemp(bitValue, decimalPlaces=2):
#     # Converts to degrees Celsius
#     temperature = ((bitValue * 330) / float(1023))
#     # 3300 mV / (10 mV/deg C) = 330
#     temperature = round(temperature, decimalPlaces)
#     return temperature
# try:
#     while (1):
#         tempData = getReading(tempChannel)
#         tempVoltage = convertVoltage(tempData)
#         temperature = convertTemp(tempData)
#         print ("Temp bitValue = {}; Voltage = {} V;".format
#            (tempData, tempVoltage))
#         sleep(sleepTime)
# except KeyboardInterrupt:
#     spi.close()
