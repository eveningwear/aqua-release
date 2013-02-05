"""

    machineAnswer.py
    
    Written by: Alon Ao (alonao@adobe.com)
    Written by: Jacky Li (yxli@adobe.com)

"""

import socket
import logging
import globalProperty
import re

from threading import Thread

class machineAnswer(Thread):
    
    def __init__(self, host='', port=21888, bufsiz=1024):
        Thread.__init__(self)
        self.setName("machineAnswer")
        
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
        self.logger.info('-----Startup machine Answer')
        self.__start_listen()
        return
    
    def __start_listen(self):
        while True:
            try:
                self.logger.debug('machine Answer: waiting for connection...')
                tcpCliSock, addr = self.__tcpSerSock.accept()
                self.logger.debug('...connect from: %s', addr)
                while True:
                    try:
                        data = tcpCliSock.recv(self.__bufsiz)
                        if not data:
                            break;
                        response = 'ok'
                        self.logger.debug('received data is %s ', data)
                        if re.match('.*sendTask', data):
                            self.logger.debug('try recieve data')
                        #send machine information
                        elif re.match('.*machineInfo', data):
                            import machine
                            xml = machine.toXML()
                            self.logger.debug(xml)
                            response = xml
                        elif re.match('.*checkRemoteEnv', data):
                            import checkRemoteEnv
                            xml = checkRemoteEnv.toXML()
                            self.logger.debug(xml)
                            response = xml
                        elif re.match('.*currentTask', data):
                            currentJobId, currentExeId = self.__worker.getCurrentJobIdAndExeId()
                            import execution
                            xml = execution.toXML(currentJobId, currentExeId)
                            response = xml
                        elif re.match(".+:.+", data):
                            operation, jobId = data.split(":")
                            if re.match('.*restart', operation):
                                self.__schMgr.restartTask(jobId)
                            elif re.match('.*stop', operation):
                                self.__schMgr.stopTask(jobId)
                            elif re.match('.*delete', operation):
                                self.__schMgr.deleteTask(jobId)
                        tcpCliSock.sendall(response)
                        tcpCliSock.flush()
                        #time.sleep(3)
                    except socket.timeout:
                        self.logger.debug('time out')
                        break;
                    except Exception, e:
                        break;
            except Exception, e:
                self.logger.error(e)
            finally:
                try:
                    tcpCliSock.close()
                except Exception, e:
                    self.logger.error(e)
