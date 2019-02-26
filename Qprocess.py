# -*- coding: utf-8 -*- 
# asdfasdfasdfasd
import socket
import threading
import time
import constant
import json
import logging
import datetime
# import media

from gpio import psi
from gpio import sol
from gpio import pump
from gpio import reclinerFoot
from gpio import reclinerHead
from gpio import led
from gpio import purifier
#15:00
class Qprocess(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        #GPIO define...
        self.m_psi = psi.psi()
        self.m_sol = sol.sol(constant.solGPIO)
        self.m_pump = pump.pump(constant.pumpGPIO)
        self.m_reclinerFoot = reclinerFoot.reclinerFoot(constant.footGPIO) 
        self.m_reclinerHead = reclinerHead.reclinerHead(constant.headGPIO) 
        self.m_led = led.led(constant.ledGPIO, constant.frequency)
        self.m_purifier = purifier.purifier(constant.purifierGPIO)
        self.m_Data = constant.Data()
        self.m_isMode = False
        self.m_StartTime = 0
        self.m_EndTime = 0

        self.m_isOperation = False

        self.headMode = False
        self.footMode = False
        self.m_count = 0
        self.m_zoneFlag = {"1":False, "2":False, "3":False, "4":False}


        #self.DeviceInit()
        # self.m_media = media.media()
    def DeviceInit(self):
        
        logging.info("device init start.....")
        #zone init....
        if self.m_Data.value("zone_1") == "soft":
            self.m_sol.multiON([1,2,3,4,5])
        else:
            self.m_pump.pumpON(True)
            self.m_sol.multiON([2,3,4,5])

        if self.m_Data.value("purifier") == "on":
            self.m_purifier.ON(True)
        else:
            self.m_purifier.OFF(True)
        
        if self.m_Data.value("led") == "on":
            self.m_led.ledPWM(constant.ledBright)
        else:
            self.m_led.ledPWM(0)


        for i in range(0, constant.InitDelay):
            time.sleep(1)
        
        logging.info("device init end.....")


    def run(self):

        logging.info("Qprocess Running..")

        while(True):

            constant.lock.acquire()
            jobQ_length= len(constant.jobQ)

            if(jobQ_length != 0):

                unit = constant.jobQ.pop()

                cmd = unit.CMD()
                power = unit.POWER()
                logging.info('cmd : ' + cmd + " power : " + power)

                if "zone_" in cmd:

                    #THREAD가 아닌거 
                    seperate = cmd.split("_")
                    self.zoneEvent(cmd, power, seperate[1])
                    logging.info("send zone response") #jordan
                    unit.CLIENT()

                elif "air" in cmd:
                    zone = unit.ZONE()
                    self.alignEvent(power, zone)
                    unit.CLIENT()
                    

                elif "reset" in cmd:
                    self.resetEvent()
                    unit.CLIENT()

                elif "head" in cmd:

                    if(self.headMode == False and self.m_isOperation == False):

                        self.m_isOperation = True
                        self.headMode = True  
                        time.sleep(2)
                        #시작 단계일듯...
                        self.m_StartTime = datetime.datetime.now()
                        thread = threading.Thread(target=self.headEvent, args=(cmd, power))
                        thread.start()             
                        
                    elif(self.headMode == True):
                        self.headMode = False

                        time.sleep(2)
                        self.m_EndTime = datetime.datetime.now()

                        thread = threading.Thread(target=self.headEvent, args=(cmd, power))
                        thread.start()       

                elif "foot" in cmd:


                    if(self.footMode == False and self.m_isOperation == False):
                        self.footMode= True
                        self.m_isOperation = True
                        time.sleep(2)
                        #시작 단계일듯...
                        thread = threading.Thread(target=self.footEvent, args=(cmd, power))
                        thread.start()             
                        
                    elif(self.footMode == True):
                        self.footMode = False
                    

                        time.sleep(2)
                        self.m_EndTime = datetime.datetime.now()

                        thread = threading.Thread(target=self.footEvent, args=(cmd, power))
                        thread.start()   
                    
                         
                elif "light" in cmd:
                    self.lightEvent(power)

                elif "purifier" in cmd:
                    self.purifierEvent(power)

                elif "bedtime" in cmd:

                    if(self.m_isMode):
                        self.m_isMode = False
                         
                        unit.CLIENT() 
                    else:
                        self.m_isMode = True
                        thread = threading.Thread(target=self.bedtimeEvent, args=(power, unit))
                        thread.start()             

                elif "alignment" in cmd:
                    
                    if(self.m_isMode):
                        self.m_isMode = False

                        # thread = threading.Thread(target=self.alignEvent, args=(power, unit))
                        # thread.start()  
                        # 
                        unit.CLIENT() 
                    else:
                        time.sleep(1)
                        zone = unit.ZONE()
                        thread = threading.Thread(target=self.alignEvent, args=(power, zone))
                        thread.start()   
                        
                elif "wakeup" in cmd:
                    if(self.m_isMode):

                        self.m_isMode = False
                        unit.CLIENT()       

                    else:
                        time.sleep(1)
                        thread = threading.Thread(target=self.wakeupEvent, args=(power, unit))
                        thread.start()             

            if(self.m_count >= 100):
                volt = self.m_psi.getVoltage()
                logging.info("NOW PSI : " + str(volt))
                self.m_count = 0
            constant.lock.release()


            self.m_count += 1    
            time.sleep(0.1)
        logging.info('Queue process thread the END')
    
    #zone_1 -> sol_2
    #zone_2 -> sol_3
    #zone_3 -> sol_4
    #zone_4 -> sol_
    #thread로 동작하도록 구현 (PSI 값을 비교하여 break)
    def zoneEvent(self, _cmd, _power, _index):

        log = True
        self.m_zoneFlag[_index] = True
        count = 0   #jordan
        
        self.m_sol.ON(constant.ZONE[_cmd], True)

        time.sleep(constant.MeasureDelay)

        volt = self.m_psi.getVoltage()

        if abs(_power - volt) >= constant.ValueInterval:
            if _power > volt:

                self.m_sol.ON(1, log)
                while count < 150:

                    volt = self.m_psi.getVoltage()

                    if volt >= _power:
                        break
                    count += 1
                    time.sleep(0.1) 
            else:
                self.m_pump.pumpON(log)
                while count < 150:

                    volt = self.m_psi.getVoltage()

                    if volt <= _power:
                        break
                        
                    count += 1
                    time.sleep(0.1)    

        self.m_sol.OFF(1, True)
        self.m_sol.OFF(constant.ZONE[_cmd], True)
        self.m_pump.pumpOFF(True)            
        self.m_zoneFlag[_index] = False
        logging.info(_cmd + " zone END")

    def resetEvent(self):
        self.m_sol.multiON([1,2,3,4,5])

        time.sleep(constant.resetDelay)

        self.m_Data.change("zone_1", "soft")
        self.m_Data.change("zone_2", "soft")
        self.m_Data.change("zone_3", "soft")
        self.m_Data.change("zone_4", "soft")

        self.m_sol.multiOFF([1,2,3,4,5])
    
    # count동작시키기, 리클라이너 하나씩 동작시키기 
    def headEvent(self, _cmd, _power):
        
        self.m_reclinerHead.STOP()

        if _cmd == "head":

            if _power != "stop":

                if _power == "up":

                    self.m_reclinerHead.UP()
                    logging.info("head up")

                    for i in range(0, (constant.HeadDelay) * 10):
                        if(self.headMode == False):
                            break

                        
                        time.sleep(0.1)
                    self.m_reclinerHead.STOP()
                    logging.info("head stop")
                            

                elif _power == "down":

                    logging.info("head down")
                    self.m_reclinerHead.DOWN()

                    for i in range(0, (constant.HeadDelay-constant.HeadInterval) * 10):
                        if(self.headMode == False):
                            break

                        time.sleep(0.1)
                    
                    self.m_reclinerHead.STOP()   
                    logging.info("head stop")



        self.headMode = False 
        self.m_isOperation = False
        self.m_reclinerHead.STOP()
        logging.info("headevent end " + _cmd)
 
    def footEvent(self, _cmd, _power):
        
        self.m_reclinerFoot.STOP()
        self.footMode= True  
        # stopEvent = True

        if _cmd == "foot":

            if _power != "stop":

                if _power == "up":


                    logging.info("Foot up" )

                    self.m_reclinerFoot.UP()

                    for i in range(0, constant.FootDelay * 10):
                        if(self.footMode == False):
                            break

                        time.sleep(0.1)
                    self.m_reclinerFoot.STOP()
                    logging.info("Foot  stop" )

                elif _power == "down":

                    self.m_reclinerFoot.DOWN()
                    logging.info("foot down")

                    for i in range(0, (constant.FootDelay - constant.FootInterval) * 10):

                        if(self.footMode == False):
                            break
                       
                        time.sleep(0.1)
                    logging.info("foot stop")
                    self.m_reclinerFoot.STOP() 

            

        self.footMode = False 
        self.m_isOperation = False
        self.m_reclinerFoot.STOP()

    def bedtimeEvent(self, _power, _object):
        
        start = constant.bedTimeBrightStart
        end = constant.bedTimeBrightEnd
        stopEvent = True

        self.m_isMode = True
        if(_power == "start"):
            logging.info("------------bed Time Start-------------")

            self.m_reclinerFoot.DOWN()
            logging.info("foot down")
            stopEvent = True

            for i in range(0, (constant.FootDelay-constant.FootInterval) * 10):
                if self.m_isMode:

                    if(i%2 == 0 and start >= 0): 
                        self.m_led.ledPWM(start)
                        start = start - constant.duty 
                    time.sleep(0.1)    
                else:
                    break
                
            logging.info("foot stop")
            self.m_reclinerFoot.STOP()
            
            for i in range(0, constant.WaitTime * 10):
                if self.m_isMode == False:
                    break
                time.sleep(0.1)

            logging.info("head down")

            self.m_reclinerHead.DOWN()

            for i in range(0, (constant.HeadDelay-constant.HeadInterval) * 10):
                if self.m_isMode:
                    if(i%2 == 0 and start >= 0): 
                        self.m_led.ledPWM(start)
                        start = start - constant.duty   

                    time.sleep(0.1)
                else:
                    break

            logging.info("head stop")

            self.m_reclinerHead.STOP() 

            for i in range(0, constant.WaitTime * 10): 
                if self.m_isMode == False:
                    break
                time.sleep(0.1)



        # elif _power == "stop":
        #     logging.info("------------bed Time Stop-------------")


        #     self.m_reclinerFoot.STOP()
        #     self.m_reclinerHead.STOP()    
        #     #   
        #     self.m_led.ledPWM(100)
        #     _object.CLIENT()
        
        self.m_reclinerHead.STOP()         
        self.m_reclinerFoot.STOP()
        self.m_isMode = False                 
        logging.info("bedTime : " + _power + " END")

    def wakeupEvent(self, _power, _object):

        start = constant.wakeUpBrightStart
        end = constant.wakeUpBrightEnd
        self.m_isMode = True
        self.m_reclinerHead.STOP()
        self.m_reclinerFoot.STOP()
        stopEvent = True
        if(_power == "start" ):

            logging.info("------------wake Up Start-------------")
            
            self.m_StartTime = datetime.datetime.now()
            logging.info("head recliner up")
            self.m_reclinerHead.UP()

            for i in range(0, constant.HeadDelay * 10):
                if self.m_isMode:
                    
                    if(i%2 == 0 and  start  <= 100 ): 
                        self.m_led.ledPWM(start)
                        start = start + constant.duty   
                    time.sleep(0.1)
                else:
                    break

            logging.info("head recliner stop")

            self.m_reclinerHead.STOP()

            for i in range(0, constant.WaitTime * 10):
                if self.m_isMode == False:
                    break
                time.sleep(0.1)


            logging.info("foot recliner up")
            self.m_reclinerFoot.UP()


            for i in range(0, constant.FootDelay * 10):
                if self.m_isMode:
                    
                    if(i%2 == 0 and  start  <= 100 ): 
                        self.m_led.ledPWM(start)
                        start = start + constant.duty  

                    time.sleep(0.1)
                else:
                    break
            logging.info("foot recliner stop")
            self.m_reclinerFoot.STOP()
            self.m_reclinerHead.STOP()         
            self.m_reclinerFoot.STOP()

            for i in range(0, constant.WaitTime * 10):
                if self.m_isMode == False:
                    break
                time.sleep(0.1)


        # elif _power == "stop":

        #     logging.info("------------wake Up Stop-------------")

        #     self.m_reclinerHead.STOP()         
        #     self.m_reclinerFoot.STOP()  


            
        #     self.m_led.ledPWM(0)
        #     _object.CLIENT()

        self.m_reclinerHead.STOP()         
        self.m_reclinerFoot.STOP()  

        self.m_isMode = False                 
        logging.info("WAKEUP : "+ _power + " ---------------END----------------")

    def alignEvent(self, _power, _zone):
        

        zoneMSTime = constant.zonTime * 10
        self.m_isMode = True

        zoneIndex = [2,3,4,5]
        outSol = [1,6,7]
        count = 0
        
        for power, zone in zip (_zone, zoneIndex):

            self.m_sol.ON(zone, True)
            time.sleep(constant.MeasureDelay)
            volt = self.m_psi.getVoltage()
            logging.info("ZONE INDEX : " + str(zone - 1) + " DST PSI : " + str(power) +" NOW PSI : " + str(volt) + " ZONE TIMEOUT(s) : " + str(constant.zoneTimeout/10))

            count = 0

            while count < constant.zoneTimeout:
                volt = self.m_psi.getVoltage()

                if abs(power - volt) <= constant.ValueInterval:

                    logging.info("result PSI : " + str(volt))
                    self.m_sol.OFF(zone, False) 
                    self.m_sol.multiOFF(outSol)  
                    self.m_pump.pumpOFF(False)
                    break

                else:
                    logging.info("PSI : " + str(volt))
                    #1 > 3.3
                    if (power >= volt):
                        
                        self.m_pump.pumpON(False)
                        self.m_sol.multiOFF(outSol)       
                    else:
                        
                        self.m_pump.pumpOFF(False)
                        self.m_sol.multiON(outSol)

                if(self.m_isMode == False):
                    break;

                time.sleep(0.1)
                count += 1
            
            self.m_sol.OFF(zone, False)

        self.m_sol.multiOFF(zoneIndex)
        self.m_sol.multiOFF(outSol)   
        self.m_pump.pumpOFF(False)
        self.m_isMode = False
        logging.info("alignment : " + _power + " ---------------END----------------")
            
    def lightEvent(self, _power):

        if(_power == "on"):
            logging.info("LED ON")
            self.m_led.ledPWM(constant.ledBright)

        elif(_power == "off"):
            logging.info("LED OFF")
            self.m_led.ledPWM(0)

    def purifierEvent(self, _power):

        if(_power == "on"):

            self.m_purifier.ON(True)

        elif(_power == "off"):
            
            self.m_purifier.OFF(True)
 
