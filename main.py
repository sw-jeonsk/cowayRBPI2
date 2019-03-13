# -*- coding: utf-8 -*- 

import server
import time
import client
import Qprocess
import logging
logging.basicConfig(filename='/home/pi/Desktop/github/cowayRBPI2/log/cowayRBPI.log', 
filemode='a', level=logging.DEBUG, format='[%(asctime)s][%(levelname)s] %(message)s')

#todo client socket select로 처리하여,, recv데이터 send데이터 각자 놀도록 
def main():
    #현재 코웨이에 설치되어 있는 침대 2대 (110, 210)    
    ip = "192.168.0.110"
    #ip = "192.168.0.210"
    port = 1114
    socketServer = server.socketServer(ip, port) 
    #TEST  
    process =Qprocess.Qprocess()

    #todo gpio control thread ..

    process.start()

    try:
        logging.info("--------------MAIN LOOP---------------")
        while(True):
            
            socketServer.listen()
            clientSocket = socketServer.accept()
            logging.info("CLIENT ACCEPT.....")
            newConn = client.socketClient(clientSocket)
            newConn.daemon = True
            newConn.start()

            time.sleep(1)
    except KeyboardInterrupt:
        socketServer.close()
        


main()
