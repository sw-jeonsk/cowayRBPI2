## server.py

import socket
import constant
import logging

class socketServer():

    def __init__(self, _ip, _port):
        self.m_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.m_socket.bind((_ip, _port))
        #self.m_socket.setblocking(0)
        logging.info('SERVER BIND [IP : ' + _ip + ":" + str(_port) +"]")
        
    def listen(self):
        self.m_socket.listen(3)

    def accept(self):
        clientSocket, addr = self.m_socket.accept()    
        return clientSocket

    def close(self):
        self.m_socket.close()


