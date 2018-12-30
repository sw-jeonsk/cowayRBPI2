import socket
import threading
import time
import constant
import json
import logging
import select
class socketClient(threading.Thread):

    def __init__(self, _socket):

        threading.Thread.__init__(self)
        self.m_clientSocket = _socket
        logging.info("socket client connect...")
        self.m_read = [self.m_clientSocket]
        self.m_write = []
    def run(self):

        while(True):
            readable, writeable, expend = select.select(self.m_read, self.m_write, self.m_read)

            for socket in readable:
                data = self.m_clientSocket.recv(1024)
                
                if(data == ""):
                    logging.info("SOCKET CLOSE")
                    return
                else:
                    try:
                        jsonData = json.loads(data)

                        constant.lock.acquire()

                        unit = constant.joB(jsonData, self.m_clientSocket, 200)
                        constant.jobQ.append(unit)
                        #debug..
                        logging.info(data)
                        constant.lock.release()

                        # jsonData['res'] = 200

                        # sendData = json.dumps(jsonData) + "\n"
                        # self.m_clientSocket.sendall(sendData)

                    except ValueError, e:
                        logging.error(data)

            time.sleep(0.5)
        logging.info("SOCKET EXIT")     
