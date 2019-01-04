import Queue
import json
import threading
import socket


frequency = 1000
duty      = 1 #interval
pumpDELAY = 5 #second
InitDelay = 20 #second

ledGPIO = 12
pumpGPIO = 7
solGPIO= [11,13,15,29,31,33,35,37,40]
headGPIO = [32, 26]
footGPIO = [22, 18]
purifierGPIO = 16

#bedTime
reclinerUpDelay = 27 #second
reclinerDownDelay = 27 #second
reclinerHeadDownDelay = 15 #second
reclinerFootDownDelay = 15 #second
bedTimeBrightStart = 100
bedTimeBrightEnd = 0

#alignment
zonTime = 30    #second
analysisDelay = 5 #second
open_zone_1 = 6 #second
open_zone_2 = 6 #second
open_zone_3 = 7 #second
open_zone_4 = 7 #second
zone_interval = 1 #second

######control
modeStopDelay = 5 #second
zoneSoftDelay = 5 #second
zoneHardDelay = 5 #second
MeasureDelay = 1 #second
resetDelay    = 10 #second

#wakeup
reclinerHeadUpDelay = 15 #second
reclinerFootUpDelay = 15 #second
wakeUpBrightStart = 0
wakeUpBrightEnd = 100

#recliner
maxUpDelay = 27 #second
maxDownDelay = 27 #second

#recliner
maxHeadUpTime   = 5 #second
maxHeadDownTime = 5 #second
maxFootUpTime   = 5 #second
maxFootDownTime = 5 #second

#led 
ledBright = 80

ZONE = {"zone_1": 2, "zone_2": 3, "zone_3": 4, "zone_4": 5}
minPSI = 0.8
maxPSI = 2.2

#media
IDLE = "/home/pi/Desktop/github/media/idle.mov"
BEDTIME = "/home/pi/Desktop/github/media/bedtime.mov"
ALIGNMENT = "/home/pi/Desktop/github/media/alignment.mov"
WAKEUP = "/home/pi/Desktop/github/media/wakeup.mov"
CONFIGPATH = "/home/pi/Desktop/github/cowayRBPI2/config.csv"
class joB:
    def __init__(self, _json, _socket, _sendData ):
        self.m_JSON = _json
        self.m_socket = _socket
        self.m_JSON['res'] = _sendData
    def CLIENT(self):

        sendData = json.dumps(self.m_JSON) + "\n"
        self.m_socket.sendall(sendData)    

    def CMD(self):
        return self.m_JSON['cmd']

    def POWER(self):
        return self.m_JSON['power']   


headValue = 0
feetValue = 0


class Data:
    def __init__(self):
        global headValue, feetValue
        self.m_Data = {}
        self.m_Data['zone_1'] = "soft"
        self.m_Data['zone_2'] = "soft"
        self.m_Data['zone_3'] = "soft"
        self.m_Data['zone_4'] = "soft"

        self.m_Data['headValue'] = headValue
        self.m_Data['feetValue'] = feetValue
        self.m_Data['led'] = "off"   
        self.m_Data['purifier'] = "off"    

    def change(self, cmd, value):
        self.m_Data[cmd] = value        
    
    def value(self, cmd):
        return self.m_Data[cmd]


lock = threading.Lock()
jobQ = Queue.deque()        
