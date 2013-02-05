"""

    Restart.py
    
    Written by: Jacky Li (yxli@adobe.com)

"""
import os, os.path, sys, datetime, string, time

from allTasks.baseTask import Task
from allTasks import SambaTask

import globalProperty

class childTask(Task):
    
    def __init__(self, type, priority = 0):
        super(childTask, self).__init__(type, priority)
    
    def runMac(self):            
        os.system('crontab -l > ct && echo \'%d\t%d\t*\t*\t* open %s\' >> ct && crontab < ct && rm ct' % (self.when.minute, self.when.hour, self.QMSGateLocation))
        #os.abort()
        self.logger.info('restAdm will be restared after 120 seconds')
        time.sleep(10)
        os._exit(0)
                
    def runWin(self):            
        os.system('at %d:%d /interactive %s' % (self.when.hour, self.when.minute, self.QMSGateLocation))
        #sys.exit doesn't work?
        #os.abort()
        self.logger.info('restAdm will be restared after 120 seconds')
        time.sleep(10)
        os._exit(0)
        
    def isQMSGateExist(self):
        QMSGateParent = None
        if os.name == 'posix':
            QMSGateName = self._dbutil.getAppInfo("QMSGate_mac")
            if QMSGateName==None:
                QMSGateName = "QMSGate.command"
            cwd = os.getcwd()
            QMSGateParent = cwd.split("QMSClient")[0]
        elif os.name == 'nt':
            QMSGateName = self._dbutil.getAppInfo("QMSGate_win")
            if QMSGateName==None:
                QMSGateName = "QMSGate.cmd"
            cwd = os.getcwd()
            QMSGateParent = cwd[0:3]
            
        if QMSGateParent==None:
            raise "QMSGate File could not be found"
        self.QMSGateLocation = QMSGateParent + QMSGateName
        if os.path.exists(self.QMSGateLocation):
            return True
        self.QMSGateName = QMSGateName
        self.QMSGateParent = QMSGateParent
        return False
    
    def getQMSGate(self):
        seedLocation = None
        if globalProperty.isMachineOutOfChina():
            seedLocation = self._dbutil.getAppInfo('seed_us')
        else:
            seedLocation = self._dbutil.getAppInfo('seed_cn')
        if seedLocation==None:
            raise "Get Seed Location failure"
        task = SambaTask.childTask('getQMSGate', 1)
        task.addPara('sambaDomain', unicode(self._commonDomain, 'utf-8'))
        task.addPara('sambaUser', unicode(self._commonUser, 'utf-8'))
        task.addPara('sambaPsw', unicode(self._commonPassword, 'utf-8'))
        #task.targetFolder = dest
        task.addPara('Repository', self.QMSGateParent) 
    
        task.addPara('FolderPath', unicode(seedLocation + "/" + self.QMSGateName, 'utf-8'))
        task.run()
        
        if not os.path.exists(self.QMSGateLocation):
            raise "Get QMSGate File fail"
        
        if os.name == 'posix':
            cmd = "sudo chmod +x %s" %self.QMSGateLocation;
            self.logger.debug(cmd)
            os.system(cmd)        
    
    def run(self):
        self.logger.debug('Restart QMS')
        if not self.isQMSGateExist():
            QMSGateLocation = self.getQMSGate()
        self.when = datetime.datetime.now()
        waitTime = 120
        if 'WaitTimeLength' in self.parameter.keys():
            waitTime = int(self.parameter['WaitTimeLength'])
        self.when += datetime.timedelta(seconds=waitTime)
        super(childTask, self).run()
        return

##################This section is mainly for debug -- Begin #############################
if __name__ == '__main__':
    u = childTask('TestRestart', 1)
    if not u.isQMSGateExist():
        u.getQMSGate()