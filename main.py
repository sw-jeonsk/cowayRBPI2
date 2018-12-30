# -*- coding: utf-8 -*- 

import server
import time
import client
import Qprocess
import logging
logging.basicConfig(filename='/home/pi/Desktop/github/cowayRBPI/log/cowayRBPI.log', 
filemode='a', level=logging.DEBUG, format='[%(asctime)s][%(levelname)s] %(message)s')

logging.info("Server Start..")
#todo client socket select로 처리하여,, recv데이터 send데이터 각자 놀도록 
def main():
    ip = "192.168.0.124"
    port = 1113
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
            newConn = client.socketClient(clientSocket)
            newConn.daemon = True
            newConn.start()

            time.sleep(1)
    except KeyboardInterrupt:
        socketServer.close()
        


main()