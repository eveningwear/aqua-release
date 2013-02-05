"""

    restWkr.py
    
    Written by: Jacky Li (yxli@adobe.com)

"""

import os.path, sys, os, re, math, time, socket, stat, subprocess

import xml.parsers.expat, ftplib

from taskPriorityDef import *

from threading import Thread, RLock, Condition
from Queue import Queue

import logging
import logging.config
import globalProperty
import traceback
from xml.dom import minidom

from DbUtil import DbUtil

class restWkr(Thread):
    
    def __init__(self):
        Thread.__init__(self)
        self.setName('restWkr')
        self.dbutil = globalProperty.getDbUtil()
        #Update machine here once worker started up
        self.dbutil.updateMachineInfo()
        self.dbutil.getTask()
        logging.config.fileConfig('log.config')
        self.logger = logging.getLogger()
        self.logger.info('-----Startup restTask worker')
        self.__taskListSorted = [] 
        self.__taskDic = {}
        self.__currentExeId = None
        self.__currentFile = None
        self.__currentTask = None
        self.__pendingJob = None
        self.__pendingJogPri = None
        self.__pendingJogNote = None
        self.__currentTaskPriority = 0
        self.__sortlinear = False
        #global field so that when all task is done executing, job status can be reflected
        self.__lastStatus = None
        self.__lastErrorMsg = None
        self.__taskMonitorFile = os.path.join(os.getcwd(), 'taskMonitor.txt')
        self.__versionFile = os.path.join(os.getcwd(), 'version.txt')
        self.__readPendingJobs()
        self.__working = False
        
        #Create a synchronized queue
        self.taskFileQueue = Queue()
            
    def run(self):
        while(True):
            if self.__pendingJob:
                self.__working = True
                self.__currentExeId = self.dbutil.getLatestExecutionId(self.__currentFile)
                self.__callTask(self.__currentFile)
                self.dbutil.finishExecution(self.__currentFile, self.__currentExeId, self.__lastStatus, self.__lastErrorMsg)
                self.logger.debug('restTask Worker:finished rest tasks %s', self.__currentFile)
                #Finish Task
                
                tempFile = self.__currentFile
                self.__currentFile = None
                globalProperty.getRestSchTkMgrInstance().finishTaskByPath(tempFile)
            self.logger.debug('restTask Worker: waiting for new task...')            
            
            self.dbutil.updateMachine()#Update machine here once previous task finished
            self.dbutil.updateMachineInfo()#Update machine here once previous task finished
            
            self.__working = False
            self.__currentFile = self.getTaskFile()
            self.__working = True
            self.logger.info('Worker gets new task:' + self.__currentFile)
            
            self.__currentExeId = self.dbutil.startExecution(self.__currentFile)
            self.__callTask(self.__currentFile)
            self.dbutil.finishExecution(self.__currentFile, self.__currentExeId, self.__lastStatus, self.__lastErrorMsg)
            self.logger.info('Worker finishes task:' + str(self.__currentFile))
            
            #Finish Task
            globalProperty.getRestSchTkMgrInstance().finishTaskByPath(self.__currentFile)
            self.__currentFile = None
            self.__currentExeId = None
            
            #Clean Leak Tasks such as Immediate Task
            #self.__schTkMgr.cleanLeakTasks()
            
    def addTaskFile(self, fileName, jobAttrs):
        taskFilePath = os.path.join(globalProperty.getSchedulTaskDir(), fileName)
        jobId = fileName[5:-3]
        cloudName = None
        deliverToCloud = False
        if not self.isIdle() and 'cloudName' in jobAttrs and 'cloudType' in jobAttrs:
            cloudName = jobAttrs['cloudName']
            cloudType = jobAttrs['cloudType']
            try:
                f = open(taskFilePath, "r")
                jobContent = f.read()
            except:
                self.logger.debug("Deliver job to cloud failed")
            finally:
                if f!=None:
                    f.close()
            if globalProperty.getCloudNodeInstance().deliverJobToCloud(jobId, jobContent, cloudName, cloudType):
                deliverToCloud = True
                    
        if not deliverToCloud:
            self.taskFileQueue.put(fileName)
        else:
            globalProperty.getRestSchTkMgrInstance().stopTask(jobId)
        
    def getTaskFile(self):
        self.__currentFileName = self.taskFileQueue.get()
        return os.path.join(globalProperty.getSchedulTaskDir(), self.__currentFileName)

    def notifyByAdm(self):
        self.lock.acquire()
        self.con.notify()
        self.lock.release()
    
    def notifyByMgr(self):
        self.lock.acquire()
        self.con.notify()
        self.lock.release()
        
    def __start_element(self, name, attrs):
        if name.strip().lower() == 'tasks':
            if attrs.has_key('sortpattern'):
                self.__setLinearSort(attrs['sortpattern'])
            if attrs.has_key('username'):
                globalProperty.setUser(attrs['username'])
            if self.__shouldUpdate():
                task = self.__getTask('Update', 0)
                self.__taskDic[task.getPriority()] = task
            if self.__shouldRename():
                task = self.__getTask('Rename', 1)
                task.addPara('hostname', self.dbutil.getMachineName())
                self.__taskDic[task.getPriority()] = task
        try:
            if name.strip().lower() == 'task':
                type = attrs['type']
                #The reboot operation will be started before restoring on Mac
                if type=='RestoreOS' and os.name == 'posix':
                    '''
                    The reason why add RebootOS before restoring OS on Mac is because we
                    must guarantee OS Restore successfully with a refresh Env.
                    '''
                    task = self.__getTask('RebootOS')
                    self.__taskDic[task.getPriority()] = task
                    
                task = self.__getTask(type)
                if not self.__isLinearSort() and attrs.has_key('priority'):
                    task.setPriority(int(attrs['priority']))
                self.__taskDic[task.getPriority()] = task
                self.__currentTask = task#Update currentTask to new one
                
                if type=='RestoreOS' or type=='CircleRestore':
                    '''
                    Add a new task following for renaming the machine after restore os
                    '''
                    task = self.__getTask('Rename')
                    expectedHostname = self.dbutil.getMachineName()
                    self.logger.info("The expected hostname is %s" %expectedHostname)
                    task.addPara('hostname', expectedHostname)
                    self.__taskDic[task.getPriority()] = task
                    
                    #The reboot operation will be started after restoring on Win
                    if os.name == 'nt':
                        '''
                        The reason why add RebootOS after restoring OS on Win is because we
                        must guarantee OS Partitions recognized by OS.
                        '''
                        task = self.__getTask('RebootOS')
                        self.__taskDic[task.getPriority()] = task
                        task.addPara('timeLength', '120')
            if name.strip() == 'param':
                name = attrs['name']
                value = attrs['value']
                self.__currentTask.addPara(name, value)
        except Exception, e:
            task = self.__getTask('Update', 0)
            self.__taskDic[task.getPriority()] = task
        return
    
    def __end_element(self, name):
        if name.strip().lower() == 'tasks':
            self.__sortTask()
            self.__runTasks()
    
    def __setLinearSort(self, linearSort):
        if linearSort.lower() == 'linear':
            self.__sortlinear = True
            
    def __isLinearSort(self):
        return self.__sortlinear
            
    def __sortTask(self):
        self.__taskListSorted = sorted(self.__taskDic.items(), key=lambda d: d[0])
        self.logger.debug(self.__taskListSorted)
        if self.__pendingJob != None and self.__pendingJogPri != None:
            count = 0
            for task in self.__taskListSorted:
                count+=1
                if task[1].getType() == self.__pendingJob and task[1].getPriority() == int(self.__pendingJogPri):
                    self.__taskListSorted = self.__taskListSorted[count:]
                    self.dbutil.finishTask(self.__currentExeId, task[1], 'succeed', self.__lastErrorMsg, self.__pendingJogNote)
                    self.logger.debug(self.__taskListSorted)
                    break
            
    def __runTasks(self):
        self.logger.debug('-----')
        self.logger.debug(self.__taskListSorted)

        self.__lastStatus = 'succeed'
        self.__lastErrorMsg = ''

        for task in self.__taskListSorted:
            self.logger.debug('-----task')
            self.logger.debug(task)
            self.logger.debug(task[1])
            self.logger.info('Task Type is ' + task[1].getType() + ' with Priority ' + str(task[1].getPriority()))
            self.logger.debug('following is the parameter for this task')
            self.logger.debug(task[1].printPara())
            self.__monitorTask(task[1])
            self.dbutil.startTask(self.__currentExeId, task[1])
            
            try:
                task[1].worker = self
                task[1].exeId = self.__currentExeId
                task[1].jobId = self.__currentFile[self.__currentFile.rfind('_') + 1:-3]
                task[1].initParam()
                task[1].run()
                status = 'succeed'
                errorMsg = ''
            except SystemExit:
                raise
            except Exception, e:
                self.logger.error(e)
                status = self.__lastStatus = 'failed'
                errorMsg = self.__lastErrorMsg = str(e)
                exstr = traceback.format_exc()
                self.logger.error(exstr)
            self.dbutil.finishTask(self.__currentExeId, task[1], status, errorMsg, task[1].getTaskNote())
            self.logger.info('Finished performing task')
        
    def __cleanTask(self):
        self.logger.debug('Clean Task')
        self.logger.debug(self.__taskListSorted)
        
        self.__taskListSorted = []        
        self.__taskDic = {}
        self.__currentTask = None
        self.__pendingJob = None
        self.__pendingJogPri = None
        self.__currentTaskPriority = 0
        self.__sortlinear = False
        
        if os.path.exists(self.__taskMonitorFile):
            os.remove(self.__taskMonitorFile)
        self.__pendingJob = None
        self.__pendingJogPri = None
        
            
    def __monitorTask(self, task):
        f = open(self.__taskMonitorFile, "w")
        content = self.__currentFileName
        content += '|'
        content += task.getType()
        content += '|'
        content += str(task.getPriority())
        content += '|'
        content += str(task.getTaskNote())
        f.write(content)
        f.flush()
        f.close()
    
    def __callTask(self, taskFile):
        p = xml.parsers.expat.ParserCreate()
        p.StartElementHandler = self.__start_element
        p.EndElementHandler = self.__end_element
        if os.path.exists(taskFile):
            taskXMLF = file(taskFile, 'r')
            p.Parse(taskXMLF.read())
            taskXMLF.close()
        self.__cleanTask()
        return

    def __getTask(self, type, priorityExp=-1):
        '''
        if type.strip().lower() == 'rename':
            from allTasks.Rename import childTask
            task = childTask(str(type), PRIORITY_ReName)
            return task
        if type.strip().lower() == 'restoreos':
            from allTasks.RestoreOS import childTask
            task = childTask(str(type), PRIORITY_RestoreOS)
            return task
        if type.strip().lower() == 'appinstall':
            from allTasks.AppInstall import childTask
            task = childTask(str(type), PRIORITY_AppInstall)
            return task
        '''
        try:
            importStr = 'from allTasks.%s import childTask' %(type.strip())
            self.logger.debug(importStr)
            exec importStr
            if self.__isLinearSort() and priorityExp==-1:
                self.__currentTaskPriority += 100
                priority = self.__currentTaskPriority
            elif self.__isLinearSort():
                priority = priorityExp
            else:#Set priority by default order
                priorityStr = 'priority = PRIORITY_%s' %(type.strip())
                self.logger.debug(priorityStr)
                exec priorityStr
            task = childTask(str(type), priority)
            return task
        except Exception, e:
            self.logger.error('getTask for %s, %s', type, e)
    
    def __readPendingJobs(self):
        if os.path.exists(self.__taskMonitorFile):
            f = open(self.__taskMonitorFile, "r")
            lines = f.readlines()
            
            (self.__currentFileName, self.__pendingJob, self.__pendingJogPri, self.__pendingJogNote) = lines[0].strip().split('|')
            if os.path.exists(self.__currentFileName):
                self.__currentFile = self.__currentFileName
                self.__currentFileName = self.getPendingTaskFileName()
            else:
                self.__currentFile = os.path.join(globalProperty.getSchedulTaskDir(), self.__currentFileName)
            f.close()
            
    def getPendingTaskFileName(self):
        if self.__currentFile:
            return os.path.basename(self.__currentFile)
        return None

    def __shouldUpdate(self):
        return globalProperty.shouldUpdate()    
    
    def __shouldRename(self):
        expectedName = self.dbutil.getMachineName()
        currentName = socket.gethostname()
        #Would rather leave name without modification than modify it if it's None or Null
        if expectedName==None or expectedName=="":
            return False
        if currentName!= expectedName:
            return True
        return False
    
    
    def getCurrentExecutionId(self):
        return self.__currentExeId
    
    def getCurrentJobIdAndExeId(self):
        if self.__currentFile !=  None:
            jobId = self.__currentFile[self.__currentFile.rfind('_') + 1:-3]
            if self.__currentExeId != None:
                return jobId, self.__currentExeId
        return None, None
    
    def isIdle(self):
        return self.taskFileQueue.empty() and not self.__working
    
if __name__ == "__main__":
    startFileName = 'FindResTool.py'
    startFileFullPath = os.path.normpath(os.path.expanduser('~\Start Menu\Programs\Startup' + '/' + startFileName))
    if os.path.exists(startFileFullPath):
        os.remove(startFileFullPath)
    host = socket.gethostbyname(socket.gethostname())
    taskManager = TaskManager(host)
