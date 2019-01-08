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

        #recliner head
        # if self.m_Data.value("head") == "up":
        #     self.m_reclinerHead.UP()
        # else:    
        #     self.m_reclinerHead.DOWN()

        # if self.m_Data.value("feet") == "up":
        #     self.m_reclinerFeet.UP()
        # else:    
        #     self.m_reclinerFeet.DOWN()

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

                    #THREAD로 구현
                    # seperate = cmd.split("_")
                    # if(self.m_zoneFlag[seperate[1]] == True):

                    #     self.m_zoneFlag[seperate[1]] = False
                    #     time.sleep(1.5)
                    #     thread = threading.Thread(target=self.zoneEvent, args=(cmd, power, seperate[1]))
                    #     thread.start()

                    # else:

                    #     time.sleep(0.5)
                    #     thread = threading.Thread(target=self.zoneEvent, args=(cmd, power, seperate[1]))
                    #     thread.start()     



                    #THREAD가 아닌거 
                    seperate = cmd.split("_")
                    self.zoneEvent2(cmd, power, seperate[1])
                    unit.CLIENT()

                elif "reset" in cmd:
                    self.resetEvent()
                    unit.CLIENT()

                elif "head" in cmd:
                    
                       
                    if(self.headMode == False):

                        #시작 단계일듯...
                        self.m_StartTime = datetime.datetime.now()
                        thread = threading.Thread(target=self.headEvent, args=(cmd, power))
                        thread.start()             
                        pass            
                    else:
                        self.headMode = False

                        time.sleep(2)
                        self.m_EndTime = datetime.datetime.now()

                        thread = threading.Thread(target=self.headEvent, args=(cmd, power))
                        thread.start()       

                elif "foot" in cmd:

                    if(self.footMode == False):

                        #시작 단계일듯...
                        thread = threading.Thread(target=self.footEvent, args=(cmd, power))
                        thread.start()             
                        pass            
                    else:
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
                        time.sleep(6)

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

    #Delay를 줘서 구현(PSI를 읽지 않고, 그냥 delay줘서 )
    def zoneEvent2(self, _cmd, _power, _index):

        if(_power == "soft"):
            self.m_sol.ON(1,True)
            self.m_sol.ON(constant.ZONE[_cmd], True)
            
            time.sleep(constant.zoneSoftDelay)

            self.m_sol.OFF(1,True)
            self.m_sol.OFF(constant.ZONE[_cmd], True) 

        elif(_power == "hard"):
            self.m_sol.ON(constant.ZONE[_cmd], True)
            self.m_pump.pumpON(True)
            

            for i in range (0, constant.zoneHardDelay * 10):
                volt = self.m_psi.getVoltage()

                if(volt >= constant.maxPSI):

                    break
                time.sleep(0.1)
           
            self.m_sol.OFF(constant.ZONE[_cmd], True)
            self.m_pump.pumpOFF(True)        

        else:
            logging.error("parameter error")        

        self.m_Data.change(_cmd, _power)
        self.m_zoneFlag[_index] = False


    def resetEvent(self):
        self.m_sol.multiON([1,2,3,4,5])

        time.sleep(constant.resetDelay)

        self.m_Data.change("zone_1", "soft")
        self.m_Data.change("zone_2", "soft")
        self.m_Data.change("zone_3", "soft")
        self.m_Data.change("zone_4", "soft")

        self.m_sol.multiOFF([1,2,3,4,5])
    def headEvent(self, _cmd, _power):
        
        self.m_reclinerHead.STOP()
        self.headMode = True  

        if _cmd == "head":

            if _power != "stop":

                if _power == "up":
                    self.m_reclinerHead.UP()

                    for i in range(0, constant.maxUpDelay * 10):
                        if(self.headMode == False):
                            break
                        time.sleep(0.1)

                elif _power == "down":
                    self.m_reclinerHead.DOWN()

                    for i in range(0, constant.maxDownDelay * 10):
                        if(self.headMode == False):
                            break
                        time.sleep(0.1)


        self.headMode = False 
        self.m_reclinerHead.STOP()
        logging.info("headevent end---------------------")
 
    def footEvent(self, _cmd, _power):
        
        self.m_reclinerFoot.STOP()
        self.footMode= True  


        if _cmd == "foot":

            if _power != "stop":

                if _power == "up":
                    self.m_reclinerFoot.UP()

                    for i in range(0, constant.maxUpDelay * 10):
                        if(self.footMode == False):
                            break
                        time.sleep(0.1)

                elif _power == "down":
                    self.m_reclinerFoot.DOWN()

                    for i in range(0, constant.maxDownDelay * 10):
                        if(self.footMode == False):
                            break
                        time.sleep(0.1)

        self.footMode = False 
        self.m_reclinerFoot.STOP()
        logging.info("footevent end---------------------")

    def bedtimeEvent(self, _power, _object):
        
        start = constant.bedTimeBrightStart
        end = constant.bedTimeBrightEnd
        self.m_isMode = True
        if(_power == "start"):
            logging.info("------------bed Time Start-------------")
            logging.info("HEAD down Time : " + str(constant.reclinerHeadDownDelay) + " FOOT down Time : " + str(constant.reclinerFootDownDelay))
            logging.info("LED DUTY : " + str(constant.duty) + " LED FREQUENCY : " + str(constant.frequency))

           

            self.m_StartTime = datetime.datetime.now()

            self.m_reclinerHead.DOWN()
            self.m_reclinerFoot.DOWN()


            for i in range(0, constant.reclinerDownDelay * 10):
                if self.m_isMode:
                    if(i%2 == 0 and start >= 0): 
                        logging.info("BRIGHT : " + str(start))  
                        self.m_led.ledPWM(start)
                        start = start - constant.duty     
                    time.sleep(0.1)
                else:
                    break

            self.m_reclinerHead.STOP()         
            self.m_reclinerFoot.STOP()


            
        elif _power == "stop":
            logging.info("------------bed Time Stop-------------")


            self.m_EndTime = datetime.datetime.now()
            self.m_reclinerFoot.UP()
            self.m_reclinerHead.UP()
            
            work_time = self.m_EndTime - self.m_StartTime
            getbackTime = int(work_time.total_seconds())            

            logging.info("[BEDTIME] get back work Time : " + str(getbackTime))
            for i in range(0, getbackTime * 10):
              
                time.sleep(0.1)

            self.m_led.ledPWM(100)

            self.m_reclinerFoot.STOP()
            self.m_reclinerHead.STOP()    
            _object.CLIENT()

            
        self.m_isMode = False                 
        logging.info("bedTime : " + _power + " ---------------END----------------")


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

    #PSI를 사용하지 않고 딜레이로 계산
    def alignEvent2(self, _power, _object):
        

        logging.info("------------Alignment2 Start-------------")
        logging.info("analysis Time : " + str(constant.analysisDelay))
        logging.info("Zone_1 Time : " + str(constant.open_zone_1) + " Zone_2 Time : " + str(constant.open_zone_2) + " Zone_3 Time : " + str(constant.open_zone_3) + " Zone_4 Time : " + str(constant.open_zone_4))

        zoneMSTime = constant.zonTime * 10
        self.m_isMode = True
        if _power == "start":

            # 5초간 몸 분석을 시작한다.
            self.m_pump.pumpOFF(False)


            for i in range(0, constant.analysisDelay * 10):
                self.m_sol.multiON([1,2,3,4,5])
                
                if(self.m_isMode == False):
                    break
                time.sleep(0.1)


            self.m_sol.multiOFF([1,2,3,4,5])
            ######################################################
            self.m_pump.pumpON(True)

            self.m_sol.ON(2, True)
            for i in range(0, zoneMSTime):

                if(self.m_isMode == False):
                    break
                time.sleep(0.1)
                zoneMSTime = zoneMSTime - 1    

            self.m_sol.OFF(2, True)
            self.m_sol.ON(3, True)
            
            for i in range(0, zoneMSTime):

                if(self.m_isMode == False):
                    break
                time.sleep(0.1)    
                zoneMSTime = zoneMSTime - 1    

            self.m_sol.OFF(3, True)
            self.m_sol.ON(4, True)
            for i in range(0, zoneMSTime):

                if(self.m_isMode == False):
                    break
                time.sleep(0.1)    
                zoneMSTime = zoneMSTime - 1 

            self.m_sol.OFF(4, True)
            self.m_sol.ON(5,True)
            for i in range(0, zoneMSTime):

                if(self.m_isMode == False):
                    break
                time.sleep(0.1)        

        else: # _power stop

            self.m_pump.pumpOFF(True)
            self.m_sol.multiON([1,2,3,4,5])

            for i in range(0, zoneMSTime):
                
                volt = self.m_psi.getVoltage()

                if(constant.minPSI >= volt):
                    time.sleep(constant.modeStopDelay)
                    break
                if(self.m_isMode == False):
                    break
                time.sleep(0.1)

            _object.CLIENT() 


        self.m_sol.multiOFF([1,2,3,4,5])
        self.m_pump.pumpOFF(True)
        self.m_isMode = False
        logging.info("---------------END----------------")

    def wakeupEvent(self, _power, _object):

        start = constant.wakeUpBrightStart
        end = constant.wakeUpBrightEnd
        self.m_isMode = True
        self.m_reclinerHead.STOP()
        self.m_reclinerFoot.STOP()

        if(_power == "start"):

            logging.info("------------wake Up Start-------------")
            logging.info("HEAD down Time : " + str(constant.reclinerHeadUpDelay) + " FOOT down Time : " + str(constant.reclinerFootUpDelay))
            logging.info("LED DUTY : " + str(constant.duty) + " LED FREQUENCY : " + str(constant.frequency))

            self.m_StartTime = datetime.datetime.now()

            self.m_reclinerHead.UP()
            self.m_reclinerFoot.UP()

            for i in range(0, constant.reclinerUpDelay * 10):
                if self.m_isMode:
                    
                    if(i%2 == 0 and  start  <= 100 ): 
                        logging.info("BRIGHT : " + str(start)) 
                        self.m_led.ledPWM(start)
                        start = start + constant.duty        
                    time.sleep(0.1)
                else:
                    break

            self.m_reclinerHead.STOP()         
            self.m_reclinerFoot.STOP()


        elif _power == "stop":

            logging.info("------------wake Up Stop-------------")


            self.m_EndTime = datetime.datetime.now()

            self.m_reclinerHead.DOWN()
            self.m_reclinerFoot.DOWN()


            work_time = self.m_EndTime - self.m_StartTime
            getbackTime = int(work_time.total_seconds())            

            logging.info("[WAKEUP] get back work Time : " + str(getbackTime))


            for i in range(0, getbackTime * 10):
                if self.m_isMode:
                    
                    # if(i%2 == 0 and  start < constant.wakeUpBrightEnd/2 ): 
                    #     self.m_led.ledPWM(start)
                    #     start = start + constant.duty        
                    time.sleep(0.1)
                else:
                    break
            self.m_led.ledPWM(0)
            self.m_reclinerHead.STOP()         
            self.m_reclinerFoot.STOP()    
               
            _object.CLIENT()

        self.m_isMode = False                 
        logging.info("WAKEUP : "+ _power + " ---------------END----------------") 

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
 
