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

        self.HeadCount = 0
        self.FootCount = 0

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
                        time.sleep(3)

                        thread = threading.Thread(target=self.bedtimeEvent, args=(power, unit))
                        thread.start()             
                    else:
                        self.m_isMode = True
                        thread = threading.Thread(target=self.bedtimeEvent, args=(power, unit))
                        thread.start()             

                elif "alignment" in cmd:

                    if(self.m_isMode):
                        self.m_isMode = False
                        time.sleep(3)

                        thread = threading.Thread(target=self.alignEvent, args=(power, unit))
                        thread.start()   
                    else:
                        time.sleep(1)

                        thread = threading.Thread(target=self.alignEvent, args=(power, unit))
                        thread.start()   
                        
                elif "wakeup" in cmd:
                    if(self.m_isMode):
                        self.m_isMode = False
                        time.sleep(3)

                        thread = threading.Thread(target=self.wakeupEvent, args=(power, unit))
                        thread.start()             
                    else:
                        time.sleep(1)
                        thread = threading.Thread(target=self.wakeupEvent, args=(power, unit))
                        thread.start()             

            if(self.m_count >= 300):
                volt = self.m_psi.getVoltage()
                logging.info("NOW VOLT : " + str(volt))
                self.m_count = 0
            constant.lock.release()


            self.m_count += 1    
            time.sleep(0.1)
        logging.info('Queue process thread the END')
    
    #zone_1 -> sol_2
    #zone_2 -> sol_3
    #zone_3 -> sol_4
    #zone_4 -> sol_5
    #thread로 동작하도록 구현 (PSI 값을 비교하여 break)
    def zoneEvent(self, _cmd, _power, _index):
        log = True
        self.m_zoneFlag[_index] = True

        #SOFT 명령일때
        if _power == "soft":
            volt = self.m_psi.getVoltage()

            logging.info("open before volt : " + str(volt))
            self.m_sol.ON(constant.ZONE[_cmd], True)
            time.sleep(constant.MeasureDelay)

            volt = self.m_psi.getVoltage()
            logging.info("open after volt : " + str(volt))

            if volt < constant.minPSI:
                # 에어 집어 넣어야 할 경우....
                logging.info("NOW Volt(" + str(volt) + ") < minPSI(" + str(constant.minPSI) + ")")

                while  self.m_zoneFlag[_index]:
                    volt = self.m_psi.getVoltage()

                    if constant.minPSI <= volt:
                        logging.info("minPSI(" + str(constant.minPSI) + ") < NOW(" + str(volt) + ")")
                        break;

                    else:
                        self.m_pump.pumpON(log)
                        log = False

            else:    
                #에어 빼야 할 경우,,,
                logging.info("NOW Volt(" + str(volt) + ") > minPSI(" + str(constant.minPSI) + ")")

                while self.m_zoneFlag[_index]:
                    volt = self.m_psi.getVoltage()

                    if constant.minPSI >= volt:
                        logging.info("minPSI(" + str(constant.minPSI) + ") > NOW(" + str(volt) + ")")
                        break;

                    else:
                        self.m_sol.ON(1, log)
                        log = False
                        # for i in range(0, constant.pumpDELAY * 10):
                        #     #플레그 변경되면 break...
                        #     if self.m_zoneFlag[_index] == False:
                        #         break
                        #     time.sleep(0.1)
                        # log = False
                time.sleep(constant.zoneSoftDelay)

        elif _power == "hard": 

            self.m_pump.pumpON(True)
            self.m_sol.ON(constant.ZONE[_cmd], True)
            time.sleep(constant.MeasureDelay)

            while self.m_zoneFlag[_index]:
                volt = self.m_psi.getVoltage()

                if constant.maxPSI <= volt:

                    logging.info("HARD " + str(volt))
                    self.m_sol.OFF(constant.ZONE[_cmd], True)
                    break;

                else:
                    self.m_pump.pumpON(log)
                    log = False


        self.m_sol.OFF(1, True)
        self.m_sol.OFF(constant.ZONE[_cmd], True)
        self.m_pump.pumpOFF(True)            
        self.m_zoneFlag[_index] = False
        logging.info(_cmd + " Thread END")


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

                    if(self.HeadCount < constant.HeadDelay):
                        logging.info("BEFORE COUNT : " + str(self.HeadCount))
                        self.m_reclinerHead.UP()
                        logging.info("head up")

                        for i in range(0, (constant.HeadDelay - self.HeadCount) * 10):
                            if(self.headMode == False):
                                break

                            if (i % 10 == 0):
                                self.HeadCount += 1

                            if (self.HeadCount == constant.HeadDelay):
                                logging.info("head stop")
                                self.m_reclinerHead.STOP() 
                                break
                            time.sleep(0.1)
                    else:
                        logging.error("i'try head up,,, But HeadCount > max HeadUp...")   
                        logging.error("max head up count : " + str(constant.HeadDelay) + " head count : " + str(self.HeadCount))

                        

                elif _power == "down":

                    if self.HeadCount > 0:
                        logging.info("BEFORE COUNT : " + str(self.HeadCount))
                        logging.info("head down")
                        self.m_reclinerHead.DOWN()

                        for i in range(0, (constant.HeadDelay-constant.HeadInterval) * 10):
                            if(self.headMode == False):
                                break

                            if (i%10 == 0):
                                self.HeadCount -= 1

                            time.sleep(0.1)
                        self.m_reclinerHead.STOP()   
                    
                    logging.info("head stop")
        logging.info("AFTER HEAD COUNT :" + str(self.HeadCount))

        self.headMode = False 
        self.m_isOperation = False
        self.m_reclinerHead.STOP()
        logging.info("headevent end " + _cmd)
 
    def footEvent(self, _cmd, _power):
        
        self.m_reclinerFoot.STOP()
        self.footMode= True  
        stopEvent = True

        if _cmd == "foot":

            if _power != "stop":

                if _power == "up":

                    if(self.FootCount < constant.FootDelay):
                        logging.info("BEFORE FOOT COUNT :" + str(self.FootCount))

                        logging.info("[foot] Foot recliner up" )

                        self.m_reclinerFoot.UP()

                        for i in range(0, constant.FootDelay * 10):
                            if(self.footMode == False):
                                break

                            if(i%10 == 0):
                                self.FootCount += 1

                            if(self.FootCount == constant.FootDelay):
                                logging.info("[foot] Foot recliner stop")
                                self.m_reclinerFoot.STOP() 
                                break
                            time.sleep(0.1)
                    
                elif _power == "down":

                    if (self.FootCount > 0):
                        logging.info("[FOOT] FOOT COUNT : " + str(self.FootCount))
                        self.m_reclinerFoot.DOWN()

                        for i in range(0, (constant.FootDelay - constant.FootInterval) * 10):

                            if(self.footMode == False):
                                break
                            if(i%10 == 0):
                                self.FootCount -= 1

                            time.sleep(0.1)

                        self.m_reclinerFoot.STOP() 

        logging.info("[FOOT] AFTER FOOT COUNT :" + str(self.FootCount))
            

        self.footMode = False 
        self.m_isOperation = False
        self.m_reclinerFoot.STOP()

    def bedtimeEvent(self, _power, _object):
        
        start = constant.bedTimeBrightStart
        end = constant.bedTimeBrightEnd
        stopEvent = True

        self.m_isMode = True
        if(_power == "start" and self.HeadCount > 0 and self.FootCount > 0):
            logging.info("------------bed Time Start-------------")
            logging.info("now headCount : " + str(self.HeadCount) + " now footCount : " + str(self.FootCount))

            self.m_reclinerFoot.DOWN()
            logging.info("[bedtime] recliner foot down")
            stopEvent = True

            for i in range(0, (constant.FootDelay-constant.FootInterval) * 10):
                if self.m_isMode:

                    if(i%2 == 0 and start >= 0): 
                        # logging.info("BRIGHT : " + str(start))  
                        self.m_led.ledPWM(start)
                        start = start - constant.duty 

                    if(i%10 == 0):
                        self.FootCount -= 1

                    if(self.FootCount == constant.FootInterval):
                        self.m_reclinerFoot.STOP()
                        self.FootCount = 0
                        break


                    time.sleep(0.1)
                else:
                    break
            logging.info("[bedtime] recliner foot stop")
            self.m_reclinerFoot.STOP()
            
            for i in range(0, constant.WaitTime * 10):
                if self.m_isMode == False:
                    break
                time.sleep(0.1)

            logging.info("[bedtime] recliner head down")

            self.m_reclinerHead.DOWN()

            for i in range(0, (constant.HeadDelay-constant.HeadInterval) * 10):
                if self.m_isMode:
                    if(i%2 == 0 and start >= 0): 
                        # logging.info("BRIGHT : " + str(start))  
                        self.m_led.ledPWM(start)
                        start = start - constant.duty   

                    if(i%10 == 0):
                        self.HeadCount -= 1   

                    if(self.HeadCount == constant.HeadInterval):

                        logging.info("[bedtime] head now down")
                        self.m_reclinerHead.STOP()
                        self.HeadCount = 0
                        break

                    time.sleep(0.1)
                else:
                    break

            logging.info("recliner head stop")

            self.m_reclinerHead.STOP() 

            for i in range(0, constant.WaitTime * 10): 
                if self.m_isMode == False:
                    break
                time.sleep(0.1)


            logging.info("HEAD COUNT : "+ str(self.HeadCount) + " FOOT COUNT : " + str(self.FootCount))

        elif _power == "stop":
            logging.info("------------bed Time Stop-------------")

            logging.info("[STOP] HEAD COUNT : "+ str(self.HeadCount) + " FOOT COUNT : " + str(self.FootCount))

            self.m_reclinerFoot.STOP()
            self.m_reclinerHead.STOP()    
            #   
            self.m_led.ledPWM(100)
            _object.CLIENT()
        
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
        if(_power == "start" and self.HeadCount < constant.HeadDelay and self.FootCount <  constant.FootDelay):

            logging.info("------------wake Up Start-------------")
            logging.info("now headCount : " + str(self.HeadCount) + " now footCount : " + str(self.FootCount))
            
            self.m_StartTime = datetime.datetime.now()
            logging.info("head recliner up")
            self.m_reclinerHead.UP()

            for i in range(0, constant.HeadDelay * 10):
                if self.m_isMode:
                    
                    if(i%2 == 0 and  start  <= 100 ): 
                        # logging.info("BRIGHT : " + str(start)) 
                        self.m_led.ledPWM(start)
                        start = start + constant.duty   

                    if(i%10 == 0):
                        self.HeadCount += 1
                    if(self.HeadCount == constant.HeadDelay):

                        if stopEvent == True:
                            self.m_reclinerHead.STOP()              
                            stopEvent = False
                            break

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
                        # logging.info("BRIGHT : " + str(start)) 
                        self.m_led.ledPWM(start)
                        start = start + constant.duty  

                    if(i%10 ==0):
                        self.FootCount += 1
                    if(self.FootCount == constant.FootDelay):

                        if(stopEvent == True):
                            self.m_reclinerFoot.STOP()
                            stopEvent = False
                            break

                    time.sleep(0.1)
                else:
                    break
            logging.info("foot recliner stop")
            self.m_reclinerFoot.STOP()

            logging.info("HEAD COUNT : "+ str(self.HeadCount) + " FOOT COUNT : " + str(self.FootCount))


            self.m_reclinerHead.STOP()         
            self.m_reclinerFoot.STOP()

            for i in range(0, constant.WaitTime * 10):
                if self.m_isMode == False:
                    break
                time.sleep(0.1)


        elif _power == "stop":

            logging.info("------------wake Up Stop-------------")

            self.m_reclinerHead.STOP()         
            self.m_reclinerFoot.STOP()  
            logging.info("[STOP] HEAD COUNT : "+ str(self.HeadCount) + " FOOT COUNT : " + str(self.FootCount))


            
            self.m_led.ledPWM(0)
            _object.CLIENT()

        self.m_isMode = False                 
        logging.info("WAKEUP : "+ _power + " ---------------END----------------") 
    

    #리클라이너 하나씩 동작시킴
    # def headEvent2(self, _cmd, _power):
        
    #     self.m_reclinerHead.STOP()

    #     if _cmd == "head":

    #         if _power != "stop":

    #             if _power == "up":
    #                 self.m_reclinerHead.UP()

    #                 for i in range(0, constant.HeadUp * 10):
    #                     if(self.headMode == False):
    #                         break
    #                     time.sleep(0.1)

    #             elif _power == "down":
    #                 self.m_reclinerHead.DOWN()

    #                 for i in range(0, constant.HeadDown * 10):
    #                     if(self.headMode == False):
    #                         break
    #                     time.sleep(0.1)


    #     self.headMode = False 
    #     self.m_isOperation = False
    #     self.m_reclinerHead.STOP()
    #     logging.info("headevent end---------------------")
 
    # def footEvent2(self, _cmd, _power):
        
    #     self.m_reclinerFoot.STOP()
    #     self.footMode= True  

    #     if _cmd == "foot":

    #         if _power != "stop":

    #             if _power == "up":
    #                 self.m_reclinerFoot.UP()

    #                 for i in range(0, constant.FootUp * 10):
    #                     if(self.footMode == False):
    #                         break
    #                     time.sleep(0.1)

    #             elif _power == "down":
    #                 self.m_reclinerFoot.DOWN()

    #                 for i in range(0, constant.FootDown * 10):
    #                     if(self.footMode == False):
    #                         break
    #                     time.sleep(0.1)

    #     self.footMode = False 
    #     self.m_isOperation = False
    #     self.m_reclinerFoot.STOP()
    #     logging.info("footevent end---------------------")

    # def bedtimeEvent2(self, _power, _object):
        
    #     start = constant.bedTimeBrightStart
    #     end = constant.bedTimeBrightEnd
    #     self.m_isMode = True
    #     if(_power == "start"):
    #         logging.info("------------bed Time Start-------------")
    #         logging.info("HEAD Up Time : " + str(constant.HeadUp) + " FOOT Up Time : " + str(constant.FootUp))
    #         logging.info("HEAD down Time : " + str(constant.HeadDown) + " FOOT down Time : " + str(constant.FootDown))
    #         logging.info("LED DUTY : " + str(constant.duty) + " LED FREQUENCY : " + str(constant.frequency))

           

    #         self.m_StartTime = datetime.datetime.now()

    #         self.m_reclinerHead.DOWN()

    #         for i in range(0, constant.HeadDown * 10):
    #             if self.m_isMode:
    #                 if(i%2 == 0 and start >= 0): 
    #                     logging.info("BRIGHT : " + str(start))  
    #                     self.m_led.ledPWM(start)
    #                     start = start - constant.duty     
    #                 time.sleep(0.1)
    #             else:
    #                 break

    #         self.m_reclinerHead.STOP() 
    #         for i in range(0, constant.WaitTime * 10):
    #             if self.m_isMode == False:
    #                 break
    #             time.sleep(0.1)
    #         self.m_reclinerFoot.DOWN()


    #         for i in range(0, constant.FootDown * 10):
    #             if self.m_isMode:
    #                 if(i%2 == 0 and start >= 0): 
    #                     logging.info("BRIGHT : " + str(start))  
    #                     self.m_led.ledPWM(start)
    #                     start = start - constant.duty     
    #                 time.sleep(0.1)
    #             else:
    #                 break

    #         self.m_reclinerHead.STOP()         
    #         self.m_reclinerFoot.STOP()

    #         for i in range(0, constant.WaitTime * 10):
    #             if self.m_isMode == False:
    #                 break
    #             time.sleep(0.1)
            
    #     elif _power == "stop":
    #         logging.info("------------bed Time Stop-------------")

            
    #         self.m_reclinerFoot.STOP()
    #         self.m_reclinerHead.STOP()    

    #         #   
    #         self.m_led.ledPWM(100)
    #         _object.CLIENT()

            
    #     self.m_isMode = False                 
    #     logging.info("bedTime : " + _power + " ---------------END----------------")


    # def wakeupEvent2(self, _power, _object):

    #     start = constant.wakeUpBrightStart
    #     end = constant.wakeUpBrightEnd
    #     self.m_isMode = True
    #     self.m_reclinerHead.STOP()
    #     self.m_reclinerFoot.STOP()

    #     if(_power == "start"):

    #         logging.info("------------wake Up Start-------------")
    #         logging.info("HEAD Up Time : " + str(constant.HeadUp) + " FOOT Up Time : " + str(constant.FootUp))
    #         logging.info("HEAD down Time : " + str(constant.HeadDown) + " FOOT down Time : " + str(constant.FootDown))
    #         logging.info("LED DUTY : " + str(constant.duty) + " LED FREQUENCY : " + str(constant.frequency))

    #         self.m_StartTime = datetime.datetime.now()

    #         self.m_reclinerHead.UP()

    #         for i in range(0, constant.HeadUp * 10):
    #             if self.m_isMode:
                    
    #                 if(i%2 == 0 and  start  <= 100 ): 
    #                     logging.info("BRIGHT : " + str(start)) 
    #                     self.m_led.ledPWM(start)
    #                     start = start + constant.duty        
    #                 time.sleep(0.1)
    #             else:
    #                 break


    #         self.m_reclinerHead.STOP()

    #         for i in range(0, constant.WaitTime * 10):
    #             if self.m_isMode == False:
    #                 break
    #             time.sleep(0.1)

    #         self.m_reclinerFoot.UP()


    #         for i in range(0, constant.FootUp * 10):
    #             if self.m_isMode:
                    
    #                 if(i%2 == 0 and  start  <= 100 ): 
    #                     logging.info("BRIGHT : " + str(start)) 
    #                     self.m_led.ledPWM(start)
    #                     start = start + constant.duty        
    #                 time.sleep(0.1)
    #             else:
    #                 break


    #         self.m_reclinerHead.STOP()         
    #         self.m_reclinerFoot.STOP()

    #         for i in range(0, constant.WaitTime * 10):
    #             if self.m_isMode == False:
    #                 break
    #             time.sleep(0.1)


    #     elif _power == "stop":

    #         logging.info("------------wake Up Stop-------------")

    #         self.m_reclinerHead.STOP()         
    #         self.m_reclinerFoot.STOP()  

    #         self.m_led.ledPWM(0)
    #         _object.CLIENT()

    #     self.m_isMode = False                 
    #     logging.info("WAKEUP : "+ _power + " ---------------END----------------") 

   
    # def headEvent3(self, _cmd, _power):
        
    #     self.m_reclinerHead.STOP()

    #     if _cmd == "head":

    #         if _power != "stop":

    #             if _power == "up":
    #                 self.m_reclinerHead.UP()

    #                 for i in range(0, constant.HeadUp * 10):
    #                     if(self.headMode == False):
    #                         break
    #                     time.sleep(0.1)

    #             elif _power == "down":
    #                 self.m_reclinerHead.DOWN()

    #                 for i in range(0, constant.HeadDown * 10):
    #                     if(self.headMode == False):
    #                         break
    #                     time.sleep(0.1)


    #     self.headMode = False 
    #     self.m_isOperation = False
    #     self.m_reclinerHead.STOP()
    #     logging.info("headevent end---------------------")
 
    # def footEvent3(self, _cmd, _power):
        
    #     self.m_reclinerFoot.STOP()
    #     self.footMode= True  


    #     if _cmd == "foot":

    #         if _power != "stop":

    #             if _power == "up":
    #                 self.m_reclinerFoot.UP()

    #                 for i in range(0, constant.FootUp * 10):
    #                     if(self.footMode == False):
    #                         break
    #                     time.sleep(0.1)

    #             elif _power == "down":
    #                 self.m_reclinerFoot.DOWN()

    #                 for i in range(0, constant.FootDown * 10):
    #                     if(self.footMode == False):
    #                         break
    #                     time.sleep(0.1)

    #     self.footMode = False 
    #     self.m_isOperation = False
    #     self.m_reclinerFoot.STOP()
    #     logging.info("footevent end---------------------")


    #리클라이너 두개 동시 동작
    # def bedtimeEvent3(self, _power, _object):
        
    #     start = constant.bedTimeBrightStart
    #     end = constant.bedTimeBrightEnd
    #     self.m_isMode = True
    #     if(_power == "start"):
    #         logging.info("------------bed Time Start-------------")
    #         logging.info("HEAD Up Time : " + str(constant.HeadUp) + " FOOT Up Time : " + str(constant.FootUp))
    #         logging.info("HEAD down Time : " + str(constant.HeadDown) + " FOOT down Time : " + str(constant.FootDown))
    #         logging.info("LED DUTY : " + str(constant.duty) + " LED FREQUENCY : " + str(constant.frequency))

           

    #         self.m_StartTime = datetime.datetime.now()

    #         self.m_reclinerHead.DOWN()
    #         self.m_reclinerFoot.DOWN()

    #         for i in range(0, constant.HeadDown * 10):
    #             if self.m_isMode:
    #                 if(i%2 == 0 and start >= 0): 
    #                     logging.info("BRIGHT : " + str(start))  
    #                     self.m_led.ledPWM(start)
    #                     start = start - constant.duty     
                    
    #                 if(i == constant.FootDown * 10):
    #                     self.m_reclinerFoot.STOP()
    #                 time.sleep(0.1)
    #             else:
    #                 break

    #         self.m_reclinerHead.STOP()         
    #         self.m_reclinerFoot.STOP()

    #         for i in range(0, constant.WaitTime * 10):
    #             if self.m_isMode == False:
    #                 break
    #             time.sleep(0.1)
            
    #     elif _power == "stop":
    #         logging.info("------------bed Time Stop-------------")

            
    #         self.m_reclinerFoot.STOP()
    #         self.m_reclinerHead.STOP()    

    #         #   
    #         self.m_led.ledPWM(100)
    #         _object.CLIENT()

            
    #     self.m_isMode = False                 
    #     logging.info("bedTime : " + _power + " ---------------END----------------")


    # def wakeupEvent3(self, _power, _object):

    #     start = constant.wakeUpBrightStart
    #     end = constant.wakeUpBrightEnd
    #     self.m_isMode = True
    #     self.m_reclinerHead.STOP()
    #     self.m_reclinerFoot.STOP()

    #     if(_power == "start"):

    #         logging.info("------------wake Up Start-------------")
    #         logging.info("HEAD Up Time : " + str(constant.HeadUp) + " FOOT Up Time : " + str(constant.FootUp))
    #         logging.info("HEAD down Time : " + str(constant.HeadDown) + " FOOT down Time : " + str(constant.FootDown))
    #         logging.info("LED DUTY : " + str(constant.duty) + " LED FREQUENCY : " + str(constant.frequency))

    #         self.m_StartTime = datetime.datetime.now()

    #         self.m_reclinerHead.UP()
    #         self.m_reclinerFoot.UP()

    #         for i in range(0, constant.HeadUp * 10):
    #             if self.m_isMode:
                    
    #                 if(i%2 == 0 and  start  <= 100 ): 
    #                     logging.info("BRIGHT : " + str(start)) 
    #                     self.m_led.ledPWM(start)
    #                     start = start + constant.duty        
    #                 time.sleep(0.1)

    #                 if( i == constant.FootUp * 10):
    #                     self.m_reclinerFoot.STOP()
    #             else:
    #                 break

    #         self.m_reclinerHead.STOP()         
    #         self.m_reclinerFoot.STOP()

    #         for i in range(0, constant.WaitTime * 10):
    #             if self.m_isMode == False:
    #                 break
    #             time.sleep(0.1)


    #     elif _power == "stop":

    #         logging.info("------------wake Up Stop-------------")

    #         self.m_reclinerHead.STOP()         
    #         self.m_reclinerFoot.STOP()  

    #         self.m_led.ledPWM(0)
    #         _object.CLIENT()

    #     self.m_isMode = False                 
    #     logging.info("WAKEUP : "+ _power + " ---------------END----------------") 


    def alignEvent(self, _power, _object):
        

        zoneMSTime = constant.zonTime * 10
        self.m_isMode = True
        if _power == "start":

            logging.info("------------Alignment Start-------------")
            logging.info("analysis Time : " + str(constant.analysisDelay) + " AIR INPUT TOTAL TIME(MS) : " + str(zoneMSTime))
            #logging.info("Zone_1 Time : " + str(constant.open_zone_1) + " Zone_2 Time : " + str(constant.open_zone_2) + " Zone_3 Time : " + str(constant.open_zone_3) + " Zone_4 Time : " + str(constant.open_zone_4))

            self.m_StartTime = datetime.datetime.now()
            # 5초간 몸 분석을 시작한다.
            self.m_pump.pumpOFF(False)


            for i in range(0, constant.analysisDelay * 10):
                self.m_sol.multiON([1,2,3,4,5])
                
                if(self.m_isMode == False):
                    break
                time.sleep(0.1)


            self.m_sol.multiOFF([1,2,3,4,5])
            ######################################################


            #2번 열고, 2초 측정시간 갖은 다음, Pump 주입 시작
            self.m_pump.pumpON(False)
            self.m_sol.ON(2, True)

            if(self.m_isMode):
                time.sleep(constant.MeasureDelay)

            zoneMSTime = zoneMSTime - constant.MeasureDelay * 10 
            volt = self.m_psi.getVoltage()
            logging.info("INDEX 2 OPEN Measure Volt : " + str(volt))
 

            for i in range(0, zoneMSTime):
                volt = self.m_psi.getVoltage()

                if constant.maxPSI <= volt:
                    self.m_pump.pumpOFF(False)
                    break;

                if(self.m_isMode == False):
                    break
                time.sleep(0.1)
                self.m_pump.pumpON(False)
                zoneMSTime = zoneMSTime - 1    

            self.m_pump.pumpOFF(False)
            self.m_sol.OFF(2, True)


            ########################################################

            self.m_sol.ON(3, True)
            
            if(self.m_isMode):
                time.sleep(constant.MeasureDelay)

            zoneMSTime = zoneMSTime - constant.MeasureDelay * 10 

            volt = self.m_psi.getVoltage()
            logging.info("INDEX 3 OPEN Measure Volt : " + str(volt))

            for i in range(0, zoneMSTime):
                volt = self.m_psi.getVoltage()

                if constant.maxPSI <= volt:
                    self.m_pump.pumpOFF(False)
                    break;
                if(self.m_isMode == False):
                    break
                time.sleep(0.1)    
                self.m_pump.pumpON(False)
                zoneMSTime = zoneMSTime - 1    

            self.m_pump.pumpOFF(False)
            self.m_sol.OFF(3, True)

            ##########################################################
            self.m_sol.ON(4, True)

            if(self.m_isMode):
                time.sleep(constant.MeasureDelay)

            zoneMSTime = zoneMSTime - constant.MeasureDelay * 10 
            volt = self.m_psi.getVoltage()
            logging.info("INDEX 4 OPEN Measure Volt : " + str(volt))

            for i in range(0, zoneMSTime):
                volt = self.m_psi.getVoltage()

                if constant.maxPSI <= volt:
                    self.m_pump.pumpOFF(False) 
                    logging.info("INDEX 4 HARD : " + str(volt))
                    break;

                if(self.m_isMode == False):
                    break
                self.m_pump.pumpON(False)    
                time.sleep(0.1)    
                zoneMSTime = zoneMSTime - 1 


            self.m_pump.pumpOFF(False)
            self.m_sol.OFF(4, True)

            ##########################################################

            self.m_sol.ON(5,True)

            if(self.m_isMode):
                time.sleep(constant.MeasureDelay)

            zoneMSTime = zoneMSTime - constant.MeasureDelay * 10 
            volt = self.m_psi.getVoltage()
            logging.info("INDEX 5 OPEN Measure Volt : " + str(volt))

            for i in range(0, zoneMSTime):
                volt = self.m_psi.getVoltage()

                if constant.maxPSI <= volt:
                    self.m_pump.pumpOFF(False) 
                    logging.info("INDEX 5 HARD : " + str(volt))
                    break;

                if(self.m_isMode == False):
                    break

                self.m_pump.pumpON(False)    
                time.sleep(0.1)        

            self.m_pump.pumpOFF(False)
            self.m_sol.OFF(5, True)

        else: # _power stop
            logging.info("------------Alignment Stop-------------")


            self.m_EndTime = datetime.datetime.now()

            work_time = self.m_EndTime - self.m_StartTime
            getbackTime = int(work_time.total_seconds())            

            logging.info("[ALIGNMENT] get back work Time : " + str(getbackTime))

            self.m_pump.pumpOFF(True)

            self.m_sol.multiON([1,2,3,4,5])

            for i in range(0, getbackTime * 10):
                time.sleep(0.1)
                # if(volt <= constant.minPSI):
                #     break
            _object.CLIENT() 

        self.m_sol.multiOFF([1,2,3,4,5])
        self.m_pump.pumpOFF(True)
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
 
