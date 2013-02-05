"""

    Update.py
    
    Written by: Jacky Li (yxli@adobe.com)
    Written by: Tian Ying

"""
import os, os.path, sys, datetime, string, time, re

from traceback import print_exc, format_exception

from allTasks.baseTask import Task

from allTasks import SambaTask

from allTasks import FTPTask


import globalProperty

class childTask(Task):
    
    def __init__(self, type, priority):
        super(childTask, self).__init__(type, priority)
    
    def runMac(self):
        self.logger.debug('Update runMac')
        self.download()
        
        os.system('crontab -l > ct && echo \'%d\t%d\t*\t*\t* open %s\' >> ct && crontab < ct && rm ct' % (self.when.minute, self.when.hour, self.QMSGateLocation))
        #os.abort()
        self.logger.info('restAdm will be restared after 120 seconds')
        time.sleep(10)
        os._exit(0)
                
    def runWin(self):
        self.logger.debug('Update runWin')
        self.download()
        
        sysInfo = globalProperty.getSysInfo()
        if re.match('.*windows.*\s+vista\s+.*', sysInfo.os.lower()) or re.match('.*windows.*\s+7\s+.*', sysInfo.os.lower()):
            self.logger.info('Windows Vista and Windows 7 do not support AT command, so to activate QMS need reboot your machine')
            from RebootOS import childTask
            rebootOS = childTask('rebootOS', self.priority+1)
            rebootOS.addPara("timeLength", 60)
            rebootOS.run()
        else:
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
        
        if re.match('^ftp:', seedLocation.lower()):
            task = FTPTask.childTask('task')
            if re.match('.*@.*', seedLocation):
                host = re.sub(r'^.*@([^/]*)/.*', r'\1', seedLocation)
                task.addPara('Host', host)
                username = re.sub(r'^ftp://(.*):.*@([^/]*)/.*', r'\1', seedLocation)
                password = re.sub(r'^.*:(.*)@([^/]*)/.*', r'\1', seedLocation)
                task.addPara('User', username)
                task.addPara('Passwd', password)
            else:
                host = re.sub(r'^ftp://([^/]*)/.*', r'\1', seedLocation)
                task.addPara('Host', host)
                task.addPara('User', self._commonDomain + '\\' + self._commonUser)
                task.addPara('Passwd', self._commonPassword)
            
            seedLocation = re.sub(r'^[^/]*(/.*)', r'\1', seedLocation[6:])
            if re.match('.*/$', seedLocation):
                #Delete ftp://                
                task.addPara('FilePath', seedLocation + self.QMSGateName)
            else:
                task.addPara('FilePath', seedLocation + "/" + self.QMSGateName)
        else:
            task = SambaTask.childTask('getQMSGate', 1)
            task.addPara('sambaDomain', unicode(self._commonDomain, 'utf-8'))
            task.addPara('sambaUser', unicode(self._commonUser, 'utf-8'))
            task.addPara('sambaPsw', unicode(self._commonPassword, 'utf-8'))
            #task.targetFolder = dest
        
            task.addPara('FolderPath', unicode(seedLocation + "/" + self.QMSGateName, 'utf-8'))
            
        task.addPara('Repository', self.QMSGateParent) 
        task.run()
        
        if not os.path.exists(self.QMSGateLocation):
            raise "Get QMSGate File fail"
        
        if os.name == 'posix':
            cmd = "sudo chmod +x %s" %self.QMSGateLocation;
            self.logger.debug(cmd)
            os.system(cmd)        
    
    def run(self):
        if not globalProperty.shouldUpdate():
            self.logger.warning("There should be some error happened to cause this update failed in request but I cannot")
            return
        if not self.isQMSGateExist():
            QMSGateLocation = self.getQMSGate()
        super(childTask, self).run()
        return
    
    def download(self):
        self.logger.info('Start update')
        path = None
        if globalProperty.isMachineOutOfChina():
            path = self._dbutil.getAppInfo('pkg_path_us_staging')
        else:
            path = self._dbutil.getAppInfo('pkg_path_cn_staging')
        dest = os.path.join(os.getcwd(), '..')
        if re.match('^ftp:', path.lower()):
            task = FTPTask.childTask('task')
            if re.match('.*@.*', path):
                host = re.sub(r'^.*@([^/]*)/.*', r'\1', path)
                task.addPara('Host', host)
                username = re.sub(r'^ftp://(.*):.*@([^/]*)/.*', r'\1', path)
                password = re.sub(r'^.*:(.*)@([^/]*)/.*', r'\1', path)
                task.addPara('User', username)
                task.addPara('Passwd', password)
            else:
                host = re.sub(r'^ftp://([^/]*)/.*', r'\1', path)
                task.addPara('Host', host)
                task.addPara('User', self._commonDomain + '\\' + self._commonUser)
                task.addPara('Passwd', self._commonPassword)
            
            path = re.sub(r'^[^/]*(/.*)', r'\1', path[6:])
            if re.match('.*/$', path):
                #Delete ftp://                
                task.addPara('FolderPath', path)
            else:
                task.addPara('FilePath', path)
                task.addPara('pattern', '.*%s.*' % os.path.basename(path))
                task.addPara('FolderPattern', re.sub(r'.*/(.*)', r'\1', path))
        else:
            task = SambaTask.childTask('getUpdate', 1)
            task.addPara('sambaDomain', unicode(self._commonDomain, 'utf-8'))
            task.addPara('sambaUser', unicode(self._commonUser, 'utf-8'))
            task.addPara('sambaPsw', unicode(self._commonPassword, 'utf-8'))
            #task.targetFolder = dest
        
            task.addPara('FolderPath', unicode(path, 'utf-8'))
            
        task.addPara('Repository', dest) 
        task.run()
        self.when = datetime.datetime.now()
        self.when += datetime.timedelta(seconds=120)
        
        globalProperty.updateVersion()
        self._dbutil.finishTask(self.exeId, self, "succeed", "", self.getTaskNote())
        self.reload()
               
    def reload(self):
        #allModuleArray = sys.modules.iteritems()
        allModuleArray = sys.modules.values()
        for module in allModuleArray:
            #self.logger.debug('added module %s' % m)
            filename = getattr(module, "__file__", None)
            if filename and filename != __file__ and filename.find('restAdm') == -1:
                if not os.path.exists(filename):
                    continue
                if filename.endswith(".pyc") or filename.endswith(".pyo"):
                    filename = filename[:-1]
                if filename.startswith(os.getcwd()) and os.path.exists(filename):
                    try:
                        self.logger.debug('reloaded module %s' % filename)
                        reload(module)
                    except Exception, e:
                        self.logger.warning(e)

##################This section is mainly for debug -- Begin #############################
if __name__ == '__main__':
    u = childTask('TestUpdates', 1)
    u.runWin()
'''
    if not u.isQMSGateExist():
        u.getQMSGate()
    u.when = datetime.datetime.now()
    u.when += datetime.timedelta(seconds=120)
    os.system('at %d:%d /interactive %s' % (u.when.hour, u.when.minute, u.QMSGateLocation))
'''