"""

    policyServer.py
    
    Written by: Jacky Li (yxli@adobe.com)

"""

import socket
import logging
import globalProperty
import re

from threading import Thread

class policyServer(Thread):
    
    def __init__(self, host='', port=21889, bufsiz=1024):
        Thread.__init__(self)
        self.setName("policyAnswer")
        
        self.__worker = globalProperty.getRestWorkerInstance()
        self.__schMgr = globalProperty.getRestSchTkMgrInstance()
        self.__host = host
        self.__port = port
        self.__bufsiz = bufsiz
        self.__tcpSerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__tcpSerSock.bind((host, port))
        self.__tcpSerSock.listen(5)
        
    def run(self):
        logging.config.fileConfig('log.config')
        self.logger = logging.getLogger()
        self.logger.info('-----Startup Policy Server')
        self.__start_listen()
        return
    
    def __start_listen(self):
        while True:
            self.logger.debug('policy Server: waiting for connection...')
            try:
                tcpCliSock, addr = self.__tcpSerSock.accept()
                self.logger.debug('...connect from: %s', addr)
                
                data = tcpCliSock.recv(self.__bufsiz)
                self.logger.debug('received data is %s ',data)
                
                replyPolicy = '<cross-domain-policy><allow-access-from domain="*" to-ports="*" /></cross-domain-policy>'
                tcpCliSock.sendall(replyPolicy)
                tcpCliSock.close()
            except socket.timeout:   
                self.logger.debug('time out')
            except Exception, e:
                self.logger.error(e)
            
