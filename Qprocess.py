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
        self.m_isMode = False
        self.m_StartTime = 0
        self.m_EndTime = 0

        self.m_isOperation = False

        self.headMode = False
        self.footMode = False
        self.m_count = 0
        self.m_zoneFlag = {"1":False, "2":False, "3":False, "4":False}

   


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


                #각 Zone을 제어하는 request
                if "zone_" in cmd:

                    zone = unit.ZONE()
                    self.airEvent(power, zone)
                    logging.info("send zone response") #jordan
                    unit.CLIENT()

                #전체 Zone을 제어하는 request
                elif "air" in cmd:

                    zone = unit.ZONE()
                    self.airEvent(power, zone)
                    unit.CLIENT()

                #recliner head 관련 request
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
                #recliner foot 관련 request
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
                #light request             
                elif "light" in cmd:
                    self.lightEvent(power)

                elif "purifier" in cmd:
                    self.purifierEvent(power)

                #bedtime 시나리오 request 
                elif "bedtime" in cmd:

                    if(self.m_isMode):
                        self.m_isMode = False
                         
                        unit.CLIENT() 
                    else:
                        self.m_isMode = True
                        thread = threading.Thread(target=self.bedtimeEvent, args=(power, unit))
                        thread.start()   

                #alignment 시나리오 request 
                elif "alignment" in cmd:
                    
                    if(self.m_isMode):
                        self.m_isMode = False
                        
                        unit.CLIENT() 
                    else:
                        time.sleep(1)
                        zone = unit.ZONE()
                        thread = threading.Thread(target=self.alignEvent, args=(power, zone))
                        thread.start()   

                #wakeup 시나리오 request            
                elif "wakeup" in cmd:
                    if(self.m_isMode):

                        self.m_isMode = False
                        unit.CLIENT()       

                    else:
                        time.sleep(1)
                        thread = threading.Thread(target=self.wakeupEvent, args=(power, unit))
                        thread.start()   

            #일정 주기로, 현재 psi 값 출력
            if(self.m_count >= 100):
                volt = self.m_psi.getVoltage()
                logging.info("NOW PSI : " + str(volt))
                self.m_count = 0
            constant.lock.release()


            self.m_count += 1    
            time.sleep(0.1)
        logging.info('Queue process thread the END')
    
    # 리클라이너 head
    def headEvent(self, _cmd, _power):
        
        self.m_reclinerHead.STOP()

        

        if _power != "stop":

            if _power == "up":

                self.m_reclinerHead.UP()
                logging.info("head up")

                for i in range(0, (constant.HeadDelay) * 10):

                    #stop 또는 down request 받았을때, break로 빠져나감
                    if(self.headMode == False):
                        break

                    
                    time.sleep(0.1)
                self.m_reclinerHead.STOP()
                logging.info("head stop")
                        

            elif _power == "down":

                logging.info("head down")
                self.m_reclinerHead.DOWN()

                for i in range(0, (constant.HeadDelay-constant.HeadInterval) * 10):

                    #stop 또는 up request 받았을때, break로 빠져나감
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


        self.m_reclinerHead.STOP()         
        self.m_reclinerFoot.STOP()  

        self.m_isMode = False                 
        logging.info("WAKEUP : "+ _power + " ---------------END----------------")


    #psi 연속으로 0값 체크
    def psiCheck(self ,_list):
        _value = False
        
        for item in _list:
            if item != 0.0:
                _value = True

        return _value

    #psi 평균값 계산
    def average(self, _list):

        _value = 0

        for item in _list:
            _value += item

        return _value / len(_list)

    def airEvent(self, _power, _zone):
        zoneMSTime = constant.zonTime * 100
        self.m_isMode = True

        zoneIndex = [2,3,4,5]
        outSol = [1]
        count = 0
        isNext = 0
        voltList = [] 
        air = "OUT"

        if _power == "in":
            for power, zone in zip (_zone, zoneIndex):
                
                #request에서 각 zone에 대한 처리를 할 경우, 나머지 zone은 -1 수치 값으로 진행됨
                #dictionary에 zone 수치가 -1은 넘기도록 구현했음
                if power == -1:
                    continue
                    
                self.m_sol.ON(zone, True)
                time.sleep(constant.MeasureDelay)
                voltList =[]
                for i in range(0, 10):
                    volt = self.m_psi.getVoltage()
                    voltList.append(volt)
                    time.sleep(0.01)


                avg_volt = self.average(voltList)
                    
                logging.info("ZONE INDEX : " + str(zone - 1) + " DST PSI : " + str(power) + " NOW PSI : " + str(avg_volt) + " ZONE TIMEOUT(s) : " + str(constant.zoneTimeout/10))

                if (power > avg_volt):

                    logging.info("AIR IN....")
                    self.m_pump.pumpON(False)
                    self.m_sol.OFF(1, False)
                    air = "IN"

                else:

                    air = "OUT"
                    logging.info("AIR OUT....")
                    self.m_pump.pumpOFF(False)
                    self.m_sol.ON(1, False)
                

                #while count < constant.zoneTimeout:
                
                while True:
                    isPsi = True
                    volt = self.m_psi.getVoltage()
                    
                    if(len(voltList) == 10):
                        del voltList[0]
                        voltList.append(volt)
                        
                        avg_volt = self.average(voltList)

                    else:    
                        voltList.append(volt)

                    logging.info("PSI: "+ str(avg_volt))

                    if air == "IN":
                        #일정 변수를 곱하여, 현재 psi 값을 맞춤 
                        if(avg_volt * 0.67  - power) > 0:
                            self.m_sol.OFF(zone, True)
                            self.m_pump.pumpOFF(True)
                            self.m_sol.OFF(1, True)
                            break
                    
                    if air == "OUT":
                        #일정 변수를 곱하여, 현재 psi 값을 맞춤 
                        if(avg_volt * 1.7 - power) < 0 or (avg_volt <= 0.21):
                            self.m_sol.OFF(zone, True)
                            self.m_pump.pumpOFF(True)
                            self.m_sol.OFF(1, True)
                            break

                    if self.m_isMode == False or isPsi == False:
                        self.m_sol.OFF(zone, True)
                        self.m_pump.pumpOFF(True)
                        self.m_sol.OFF(1, True)
                        break        
                   
                
                    time.sleep(0.01)

                self.m_pump.pumpOFF(True) 
                self.m_sol.OFF(1, True)
                self.m_sol.OFF(zone, False)

        elif _power == "out":
            self.m_sol.ON(1, False)
            for power, zone in zip (_zone, zoneIndex):
                self.m_sol.ON(zone, True)
                count = 0
                while count < constant.zoneTimeout:
                    count += 1

                    if(count % 10 == 0):
                        volt = self.m_psi.getVoltage()
                        logging.info("now PSI : " + str(volt))

                    time.sleep(0.01)
                self.m_sol.OFF(zone, True)

        self.m_sol.multiOFF(zoneIndex)
        self.m_sol.multiOFF(outSol)   
        self.m_pump.pumpOFF(False)
        self.m_isMode = False
        logging.info("alignment : " + _power + " ---------------END----------------")

    def alignEvent(self, _power, _zone):
        
        self.m_isMode = True

        zoneIndex = [2,3,4,5]
        outSol = [1]
        count = 0
        isNext = 0
        voltList = [] 
        air = "OUT"
 
        for power, zone in zip (_zone, zoneIndex):

            self.m_sol.ON(zone, True)
            time.sleep(1)
            
            voltList =[]
            for i in range(0, 10):
                volt = self.m_psi.getVoltage()
                voltList.append(volt)
                time.sleep(0.01)


            avg_volt = self.average(voltList)
                
            logging.info("ZONE INDEX : " + str(zone - 1) + " DST PSI : " + str(power) + " NOW PSI : " + str(avg_volt) + " ZONE TIMEOUT(s) : " + str(constant.zoneTimeout/100))

            if (power > avg_volt):

                air = "IN"
                self.m_pump.pumpON(False)
                self.m_sol.OFF(1, False)
                

            else:

                air = "OUT"
                self.m_pump.pumpOFF(False)
                self.m_sol.ON(1, False)

            logging.info("ZONE : " + str(zone - 1) + " DST : " + str(power) + " NOW : " + str(avg_volt) + " TMOUT(s) : " + str(constant.zoneTimeout/100) +" AIR : " + air)

            count = 0

            while count < constant.zoneTimeout:
                # while True:
                count += 1
                volt = self.m_psi.getVoltage()
                    
                if(len(voltList) == 10):
                    del voltList[0]
                    voltList.append(volt)
                    
                    avg_volt = self.average(voltList)

                else:    
                    voltList.append(volt)

                logging.info("PSI: "+ str(avg_volt))

                if air == "IN":
                    if(avg_volt * 0.67  - power) > 0:
                        self.m_sol.OFF(zone, True)
                        self.m_pump.pumpOFF(True)
                        self.m_sol.OFF(1, True)
                        break
                
                if air == "OUT":
                    if(avg_volt * 1.7 - power) < 0 or (avg_volt <= 0.21):
                        self.m_sol.OFF(zone, True)
                        self.m_pump.pumpOFF(True)
                        self.m_sol.OFF(1, True)
                        break

                if self.m_isMode == False:
                    self.m_sol.OFF(zone, True)
                    self.m_pump.pumpOFF(True)
                    self.m_sol.OFF(1, True)
                    break        
                
                
                    time.sleep(0.01)
                
                time.sleep(0.01)

            self.m_pump.pumpOFF(True) 
            self.m_sol.OFF(1, True)
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
 
