"""

    baseTask.py
    
    Written by: Jacky Li (yxli@adobe.com)

"""

import os.path, sys, os, re, math, time, socket, stat, subprocess
import xml.parsers.expat, ftplib
import logging, shutil
import logging.config
import globalProperty

class Task(object):

    def __init__(self, type, priority):
        logging.config.fileConfig('log.config')
        self.logger = logging.getLogger()
        self.logger.info('Create a new ' + type + ' task with priority ' + str(priority))
        self.type = type
        self.runFlag = False
        self.finishFlag = False
        self.parameter = {}
        self.priority = priority
        self.note = ''
        self._schTkMgr = globalProperty.getRestSchTkMgrInstance()
        self._commonDomain = globalProperty.getCommonDomain()
        self._commonUser = globalProperty.getCommonUser()
        self._commonPassword = globalProperty.getCommonPassword()
        self._dbutil = globalProperty.getDbUtil()
        self.__toolsDir = os.path.join(os.getcwd(), 'tools')
        
        self.macAddress = globalProperty.getMacAddress()
        
        #Following 2 initialization occur in restWkr
        self.jobId = None
        self.exeId = None
        
        if os.name == 'posix':
            self.platform = "osx10"
        elif os.name == 'nt':
            self.platform = "win32"
    
    def addPara(self, name, value):
        self.parameter[name] = value
        
    def printPara(self):
        text = ''
        for key in self.parameter.keys():
            self.logger.info("%s:%s" % (key, self.parameter[key]))
            text = text + "%s:%s" % (key, self.parameter[key]) + '\n'
        return text
    
    def initParam(self):
        pass
    
    def setPriority(self, priority):
        self.priority = priority
        
    def getPriority(self):
        return self.priority
    
    def getType(self):
        return self.type
    
    def getTaskNote(self):
        return self.note
    
    def getToolsDir(self):
        return self.__toolsDir
    
    def run(self):
        if os.name == 'posix':
            self.runMac()
        if os.name == 'nt':
            self.runWin()
     
    def runMac(self):
        self.logger.debug('BaseTask runMac')
        return
        
    def runWin(self):
        self.logger.debug('BaseTask runWin')
        return
    
    def runCommand(self, cmd):
        outPutStr= subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()
        return outPutStr
    
    def runSimpleCommand(self, cmd):
        outPutStr= subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()
        return outPutStr
    
    def runCommandWithoutWait(self, cmd):
        subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        
    def runCommandInFileWithoutWait(self, targetFile, cmd):
        self.creatFile(targetFile, cmd)
        if os.name == 'posix':
            cmdGrantAccess = 'sudo chmod +x %s' % targetFile
            os.system(cmdGrantAccess)
        self.runCommand(targetFile)
    
    def creatFile(self, targetFile, iostream):
        if os.path.exists( targetFile ):
            os.remove(targetFile)
        f = file(targetFile, 'w')
        f.write(iostream)
        f.close()
        
    def _getCurrentTime(self):
        dateList = time.localtime()
        curDate = '-'.join((str(dateList[0]), str(dateList[1]), str(dateList[2])))
        curTime = ':'.join((str(dateList[3]), str(dateList[4]), str(dateList[5])))
        return '%s %s' %(curDate, curTime)
    
    def _rmtree(self, dirpath):
        try:
            if (os.path.exists(dirpath)):
                shutil.rmtree(dirpath)
        except WindowsError, (errno,strerror):
            for root, dirs, files in os.walk(dirpath):
                for f in files:
                    filepath = os.path.join(root,os.path.basename(f))
                    fileAtt = os.stat(filepath)[0]
                    if not fileAtt & stat.S_IWRITE:
                        os.chmod(filepath, stat.S_IWRITE)                        
                    os.remove(filepath)
            shutil.rmtree(dirpath)
    
    def _straightSearchFile(self, parent, fileName):
        files = os.listdir(parent)
        for filename in files:
            if re.search(fileName, filename)!=None or filename.lower()==fileName.lower():
                filePath = os.path.join(parent, filename)
                return filePath
        return None
    
    def _searchFile(self, parent, fileName):
        for root, dirs, files in os.walk(parent):
            for filename in files:
                if filename.lower()==fileName.lower():
                    filePath = os.path.join(root, filename)
                    return filePath
        return None
