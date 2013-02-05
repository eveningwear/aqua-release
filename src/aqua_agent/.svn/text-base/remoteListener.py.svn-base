"""

    remoteListener.py
    
    Written by: Lei Nie(nlei@adobe.com)

"""

import logging
import time,os
import globalProperty
import re
from QMSWebService import QMSWebService
from threading import Thread, RLock, Condition

class remoteListener(Thread):
    
    def __init__(self):
        Thread.__init__(self)
        self.__qmsWS = QMSWebService()
        self.__macAddress = globalProperty.getMacAddress()
        self.setName("remoteListener")
        self.__status=self.getConnectStatus()
        self.updateStatus(self.__status)
        self.__statusChange=False
        self.__worker = globalProperty.getRestWorkerInstance()
        
    def run(self):
        logging.config.fileConfig('log.config')
        self.logger = logging.getLogger()
        self.logger.info('-----Startup remote listener')
        self.__start_listen()
        return
    
    def __start_listen(self):
        '''
        if(self.__status):
            self.logger.debug('There is a remote connection now')
        else:
            self.logger.debug('No remote connection')
        '''
        while True:            
            #print 'Remote Listener: check remote connection...'
            try:
                time.sleep(5)
                status = self.getConnectStatus()
                if(self.__status!=status):
                    #print 'Machine Status Changed ... '
                    self.__status=status
                    self.updateStatus(status)
            except Exception, e:
                self.logger.error(e)
                
    def getConnectStatus(self):
        if os.name=='nt':
            cmd = 'qwinsta.exe'
            output=os.popen(cmd).read()
            if(output==''):
                cmd = os.path.join(os.getcwd(),'tools\\qwinsta.exe')
            output=os.popen(cmd).read()
            n=output[output.find('rdp-tcp')+7:].find('rdp-tcp')
            if n==-1:
                return self.getConnectStatusByNetstat()
            else:
                return True
        else:
            '''
            logFile=os.path.expanduser('~/Library/logs/vineserver.log')
            if(os.path.isfile(logFile)):
                file=open(logFile,'r')
                nlines=file.readlines()
                lines=str(nlines[-3:])
                import string
                lines=string.join(nlines[-3:])
                if((lines.find('Hextile for client')>0) or (lines.find('Client Connected')>0)):
                    return True
                else:
                    return False   
            '''
            return self.getConnectStatusByNetstat()
            
    def getConnectStatusByNetstat(self):
        cmd = 'netstat -n'
        if os.name=='nt':
            reString = '\d+\.\d+\.\d+\.\d+:5900.+\d+\.\d+\.\d+\.\d+:.+ESTABLISHED'
        else:
            reString = '\d+\.\d+\.\d+\.\d+\.5900.+\d+\.\d+\.\d+\.\d+\..+ESTABLISHED'
        m=re.search(reString, os.popen(cmd).read())
        if m==None:
            return False
        else:
            return True
        
    def updateStatus(self,status):
        #self.logger.debug('Update Status')
        if(status):
            self.__qmsWS.updateLabMachineStatus(self.__macAddress,2)
        else:
            self.__qmsWS.updateLabMachineStatus(self.__macAddress,1)
            
if __name__ == '__main__':
    rml = remoteListener()
    print rml.getConnectStatus()