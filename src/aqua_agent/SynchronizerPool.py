"""

    SynchronizerPool.py
    
    This program is used for downloading builds some kind thing asynchronously with a customized size 
    Thread Pool to manage and allocate the feasible thread resource to the Downloaded Target, since I
    have used CodexTask and AysncFTPTask for downloading works, the multi-threads connecting to server
    especially to one Same Server will cause server exhausted accompany with count of thread increases
    too much as bad as my downloading job failed and other unpredictable issue coming up, so I create 
    this program to allocate the idle thread in the pool to the Downloaded Target, any request exceeds 
    the Maximum Thread Customized for the Pool will be blocked till some busy thread exchanged to IDLE. 
    
    Written by: Jacky Li (yxli@adobe.com)

"""

import os.path, sys, os, re, math, time, stat, subprocess, socket, time, threading, traceback

import xml.parsers.expat, ftplib
from threading import Thread, RLock, Condition, Timer
import logging
import logging.config
import QMSWebService
import globalProperty
import Queue
import random
import ctypes
#import FtpWalker

class FileOperator(object):
    def __init__(self):
        self.__lock = RLock()#Thread relative
        self.__dbutil = globalProperty.getDbUtil()
    
    def updateLatestFile(self, 
                         unFinishedDic, 
                         productName, 
                         version,
                         buildNum,
                         platform,
                         language,
                         certLevel,
                         subProduct,
                         latestBuildLocation):
        for filePath in unFinishedDic.keys():
            fileInfo = self.getFileInfo(filePath)
            tmpFileSize = int(fileInfo['Size'])
            if tmpFileSize != unFinishedDic[filePath]:
                return
        self.__lock.acquire()
        self.__dbutil.addNewLatestBuild(
            productName,
            version,
            buildNum,
            platform,
            language,
            certLevel,
            subProduct,
            latestBuildLocation)
        self.__lock.release()
    
    def getFileInfo(self, filePath):
        fileStates = os.stat(filePath)
        fileInfo = {
            'Size': fileStates[stat.ST_SIZE],
            'LastModified': time.ctime(fileStates[stat.ST_MTIME]),
            'LastAccessed': time.ctime(fileStates[stat.ST_ATIME]),
            'CreationTime': time.ctime(fileStates[stat.ST_CTIME]),
            'Mode': fileStates[stat.ST_MODE]
        }
        return fileInfo

def _async_raise(tid, excobj):
    #res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(excobj))
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), ctypes.py_object(excobj))
    if res == 0:
        raise ValueError("nonexistent thread id")
    elif res > 1:
        # """if it returns a number greater than one, you're in trouble, 
        # and you should call it again with exc=NULL to revert the effect"""
        #ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, 0)
        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), 0)
        raise SystemError("PyThreadState_SetAsyncExc failed")


fo = None
class Synchronizer(Thread):
    
    def __init__(self, syncManager, timeout=10):
        Thread.__init__(self)
        name = time.strftime('%H_%M_%S') + str(time.clock())
        self.setName("synchronizer_%s" % name)
        logging.config.fileConfig('log.config')
        self.logger = logging.getLogger()
        self.syncManager = syncManager
        self.timeout = timeout
        self.parameterQueue = Queue.Queue()
        self.idle = False
        self.timeout = 120 * 60
        global fo
        if fo==None:
            fo = FileOperator()
    
    def __initParameter(self, parameter):
        self.parameter = parameter
        self.__dbutil = globalProperty.getDbUtil()
        self.__downloadedFileList=[]
        self.__toBeDownloadedFileList=[]
        
        # Init value for parameters used in this task
        self._Host = ''
        self._User = self.__dbutil.getAppInfo('common_domain') + "\\" + self.__dbutil.getAppInfo('common_user')
        self._Password = self.__dbutil.getAppInfo('common_password')
        self._FilePath = ''
        self._Pattern = ''#This pattern is for full path of the target file in the FTP Server
        self._FolderPattern = ''#This is for locate the folder containing target file quickly
        self._BaseDir = ''#This is the name of base folder align with the FTP Server
        self._Repository = ''#This is the path for storing the downloaded File
        self._FolderTimeConstrain = 'False'#This is the flag that the folder checked should match the time constrain
        self._KickAutoTest = 'False'
        self._Latest = '60'#This value means the default time constrain for downloading file is latest 3 days according to current time
        self._FTPRepository = ''
        self._UpdateLatest = 'True'
                
        self._Product = ''
        self._Version = ''
        self._Platform = ''
        self._BuildNum = ''
        self._Language = ''
        self._CertLevel = 'Not Tested'
        self._SubProduct = 'Application'
        self._LatestBuildLocation = ''
        self._LatestFolderPattern = ''
        
        self.__initializeParameter()
        self.__unFinishedDic = {}#The dictionary for recording unfinished item      
        self.__emailFrom = 'yxli@adobe.com'
        self.__emailTo = 'yxli@adobe.com'
    
    def __initializeParameter(self):
        self._test = 'test'
        for key in self.parameter.keys():
            if self.parameter[key].strip() != '':
                transferValueStr = "self._%s = self.parameter['%s']" %(str(key), str(key))
                print transferValueStr
                exec transferValueStr
        #self.__printSelfPara()
        
    def __printSelfPara(self):
        for key in self.parameter.keys():
            printStr = 'print self._%s' %(str(key))
            exec printStr
    
    def addParameter(self, parameter):
        self.parameterQueue.put(parameter)
        
    def isParameterEmpty(self):
        empty = self.parameterQueue.empty()
        return empty
    
    def raise_exc(self, excobj):
        assert self.isAlive(), "thread must be started"
        for tid, tobj in threading._active.items():
            if tobj is self:
                _async_raise(tid, excobj)
                return
        
        # the thread was alive when we entered the loop, but was not found 
        # in the dict, hence it must have been already terminated. should we raise
        # an exception here? silently ignore?
    
    def terminate(self):
        # must raise the SystemExit type, instead of a SystemExit() instance
        # due to a bug in PyThreadState_SetAsyncExc
        self.raise_exc(SystemExit)

            
    def run(self):
        self.tid = ctypes.windll.kernel32.GetCurrentThreadId()
        while True:
            self.idle = True
            try:
                parameter = self.parameterQueue.get(timeout=self.timeout)
            except Queue.Empty:
                #Try to put the thread into idle status, otherwise will quit
                if self.syncManager.isIdlableSyncer(self):
                    parameter = self.parameterQueue.get()
                else:
                    break
                
            self.syncManager.setTimer(self)
            
            self.__initParameter(parameter)
            self.logger.info('-----Startup Asyn FTP Task')
            self.__printSelfPara()
            self.__getFilesFromFTP(self._Host, self._User, self._Password, self._FilePath, self._Latest,
                            self._Repository, self._Pattern, self._BaseDir, self._FolderPattern,
                            self._FolderTimeConstrain)
            
            self.syncManager.cleanTimer(self)

    #Following functions are extracted from build synchronizer
    def __getFilesFromFTP(self, server, user, passwd, filePath, latest, repository, pattern, baseDir, folderPattern, folderTimeContrain):
       global fo
       print 'Info:', server, user, passwd, filePath, repository
       ftpsrv = None
       try:
           ftpsrv = ftplib.FTP(server)
           ftpsrv.login(user, passwd)
           ftpsrv.set_pasv(False)
           pathArray = filePath.split(";")
           for path in pathArray:
              folderStack = []
              if baseDir.strip()!="":
                 folderList = path.split('/')
                 appendFlag = 0
                 for folder in folderList:
                    if appendFlag == 1:
                       folderStack.append(folder)
                    elif folder.strip().lower() == baseDir.lower():
                       folderStack.append(baseDir)
                       appendFlag = 1
                 if self._FTPRepository.strip() != "":
                     self._LatestBuildLocation = self._FTPRepository + "/".join(folderStack)
                 else:
                     self._LatestBuildLocation =  repository + "/".join(folderStack)
              else:
                 repositoryName = re.sub(r'.*/(.*)', r'\1', path)
                 localRep = os.path.join(repository, repositoryName)
                 folderStack = [repositoryName]
                 '''
                 if self._FTPRepository.strip() != "":
                     self._LatestBuildLocation = self._FTPRepository + "/" + repositoryName.replace("\\", "/")
                 else:
                     self._LatestBuildLocation =  repository + "\\" + repositoryName
                 '''                     
              print folderStack
              self.__getFiles(ftpsrv, path, latest, repository, folderStack, pattern, folderPattern, folderTimeContrain)
           if len(self.__toBeDownloadedFileList)>0 and self.__dbutil!=None and self._Product!='' and self._Version!='' and self._Platform!='' and self._Language!='' and self._LatestBuildLocation!='':
              latestBuild = self.__dbutil.getLatestBuild(
                                               self._Product, 
                                               self._Version,
                                               self._Platform,
                                               self._Language,
                                               self._CertLevel,
                                               self._SubProduct)
              if self._UpdateLatest=="True" and (latestBuild==None or latestBuild[0]!=self._BuildNum or latestBuild[1]!=self._LatestBuildLocation):
                  fo.updateLatestFile( 
                                                   self.__unFinishedDic,
                                                   self._Product, 
                                                   self._Version,
                                                   self._BuildNum,
                                                   self._Platform,
                                                   self._Language,
                                                   self._CertLevel,
                                                   self._SubProduct,
                                                   self._LatestBuildLocation)
                  if self._KickAutoTest=="True":
                      from QMSWebService import QMSWebService
                      qmsWS = QMSWebService()
                      qmsWS.kickOffAutoTest(self._Platform)
       except Exception, e:
           self.logger.error(e)
       finally:
           if ftpsrv!=None:
               ftpsrv.close()
          
    def __getFiles(self, ftpCon, path, latest, repository, folderStack, pattern, folderPattern, folderTimeContrain):
       ftpCon.cwd(path)
       self.logger.info(path)
       print "current path is: ", ftpCon.pwd()
       folderPatternHierarchy = []
       if folderPattern.strip() != '':
          folderPatternHierarchy = folderPattern.split('/')
       #Need to set pasv to True for running following code
       #self.ls(ftpCon, path)
       filelist = ftpCon.nlst('-l')
       filelist.reverse()
       for line in filelist:
          print line
          fileInfo = line.split()
          if len(fileInfo)>4 and re.match('^\d*$', fileInfo[4]) != None:
             if re.match('^d.*', fileInfo[0]) != None: #directory
                dirName = re.sub(r'.*\S{3}\s+\d{1,2}\s+[0-9:]{4,5}\s+(.*)', r'\1', line)
                if folderTimeContrain!=None and folderTimeContrain.lower().strip() == 'true': #Compare the created time of folder
                   fileD = re.sub(r'.*\S{3}\s+\d{1,2}\s+([0-9:]{4,5})\s+(.*)', r'\1', line)
                   if fileD.find(':')==-1:
                      year = fileD
                   else:
                      year = time.ctime(time.time()).split()[4]
                   month = self.__getMonth(fileInfo[5])
                   fileDate = "-".join((year, month, fileInfo[6]))
                   if not self.__beforeLatest(fileDate, latest):
                      continue;
                   
                folderStack.append(dirName)
                #newPath = "/".join((path, dirName))
                #print "/".join(folderStack)
                #Add Folder Pattern Check Here
                if len(folderPatternHierarchy)>0 and re.match(folderPatternHierarchy[0], dirName):
                   nextFolderPattern = "/".join(folderPatternHierarchy[1:])
                   self.__getFiles(ftpCon, dirName, latest, repository, folderStack, pattern, nextFolderPattern, folderTimeContrain)
                elif len(folderPatternHierarchy)==0:
                   self.__getFiles(ftpCon, dirName, latest, repository, folderStack, pattern, folderPattern, folderTimeContrain)
                   
                if int(latest)<=2 and re.match(self._LatestFolderPattern, dirName) and self._FTPRepository.strip() != "":
                    self._BuildNum = dirName
                    self._LatestBuildLocation = self._FTPRepository + "/".join(folderStack) + "/Release/RibsInstaller"
                    
                folderStack.pop()
                print "/".join(folderStack)
             else: #file
                if len(folderPatternHierarchy)!=0:
                   continue;
                fileName = re.sub(r'.*\S{3}\s+\d{1,2}\s+[0-9:]{4,5}\s+(.*)', r'\1', line)
                fileD = re.sub(r'.*\S{3}\s+\d{1,2}\s+([0-9:]{4,5})\s+(.*)', r'\1', line)
                if fileD.find(':')==-1:
                   year = fileD
                else:
                   year = time.ctime(time.time()).split()[4]
                month = self.__getMonth(fileInfo[5])
                fileDate = "-".join((year, month, fileInfo[6]))
                fileSize = fileInfo[4] #File Size on FTP Server
                if self.__beforeLatest(fileDate, latest):#Get File
                    self.__getFile(ftpCon, repository, folderStack, fileName, pattern, fileSize)
          #elif re.match('^\d*$', fileInfo[2]) != None:
          elif len(fileInfo)>3: #To avoid some special conditions such as "total 698698" returned whose length is only 2
             if fileInfo[2].strip() == '<DIR>': #directory
                dirName = re.sub(r'\d{,2}-\d{,2}-\d{,2}\s+\d{,2}:\d{,2}[A|P]M\s+<DIR>\s+(.*)', r'\1', line)
                if folderTimeContrain!=None and folderTimeContrain.lower().strip() == 'true': #Compare the created time of folder
                   fileDates = fileInfo[0].split('-')
                   year = fileDates[2]
                   if re.match('^20|19\d{2}$', year)==None:
                      year = '20' + fileDates[2]
                   month = fileDates[0]
                   fileDate = "-".join((year, month, fileDates[1]))
                   fileSize = fileInfo[2] #File Size on FTP Server
                   if not self.__beforeLatest(fileDate, latest):
                      continue;
                folderStack.append(dirName)
                #newPath = "/".join((path, dirName))
                #print "/".join(folderStack)
                #Add Folder Pattern Check Here
                if len(folderPatternHierarchy)>0 and re.match(folderPatternHierarchy[0], dirName):
                   nextFolderPattern = "/".join(folderPatternHierarchy[1:])
                   self.__getFiles(ftpCon, dirName, latest, repository, folderStack, pattern, nextFolderPattern, folderTimeContrain)
                elif len(folderPatternHierarchy)==0:
                   self.__getFiles(ftpCon, dirName, latest, repository, folderStack, pattern, folderPattern, folderTimeContrain)
                
                if int(latest)<=2 and re.match(self._LatestFolderPattern, dirName) and self._FTPRepository.strip() != "":
                    self._BuildNum = dirName
                    self._LatestBuildLocation = self._FTPRepository + "/".join(folderStack) + "/Release/RibsInstaller"
                    
                folderStack.pop()
                print "/".join(folderStack)
             else: #file
                if len(folderPatternHierarchy)!=0:
                   continue;
                fileName = re.sub(r'\d{,2}-\d{,2}-\d{,2}\s+\d{,2}:\d{,2}[A|P]M\s+\d*\s+(.*)', r'\1', line)
                fileDates = fileInfo[0].split('-')
                year = fileDates[2]
                if re.match('^20|19\d{2}$', year)==None:
                   year = '20' + fileDates[2]
                month = fileDates[0]
                fileDate = "-".join((year, month, fileDates[1]))
                fileSize = fileInfo[2] #File Size on FTP Server
                if self.__beforeLatest(fileDate, latest):#Get File
                    self.__getFile(ftpCon, repository, folderStack, fileName, pattern, fileSize)
       ftpCon.cwd('..')
    
    def __getFile(self, ftpCon, repository, folderStack, fileName, pattern, fileSize):
       global fo
       print "current path is: ", ftpCon.pwd()
       self.logger.info(ftpCon.pwd())
       filePath = os.path.normpath(os.path.join(repository, "/".join((folderStack)), fileName))
       patternList = []
       match = False
       if pattern.strip() != "":
          patternList = pattern.split("|")
       else:
          match =True
       for patternElement in patternList:
          if re.match(patternElement, filePath)!=None:
             match = True
             break;
       if not match:
          return
       for folder in folderStack:
          repository = os.path.normpath(os.path.join(repository, folder))
          if not os.path.exists(repository):
             try:
                 os.makedirs(repository)
             except Exception, e:
                 self.logger.error(e)
                 from allTasks.Restart import childTask
                 task = childTask('restart')
                 task.run()
    #   filePath = os.path.join(repository, fileName)
       self.__toBeDownloadedFileList.append(filePath)
       if not os.path.exists(filePath):
          print ftpCon.pwd()
          f = None
          try:
             f = file(filePath, "wb")
             self.logger.info(filePath)
             ftpCon.retrbinary("RETR %s" % (fileName), f.write)
             self.__downloadedFileList.append(filePath)
          except Exception, e:
             print 'Exception thrown when downloading the file ', fileName
             logStr = 'Exception thrown when downloading the file ' + fileName
             self.logger.info(logStr)
          finally:
              if f!=None:
                  f.close()
       else:#should compare the file size
          print filePath
          fileInfo = fo.getFileInfo(filePath)
          for key in fileInfo.keys():
             print key, "\t", fileInfo[key]
          print str(fileSize), "\t", fileInfo['Size']
          logStr = str(fileSize) + "\t" + str(fileInfo['Size'])
          self.logger.info(logStr)
          tmpFileSize = int(fileInfo['Size'])
          if int(fileSize) != tmpFileSize:
             for i in range(3):
                 time.sleep(10)#Sleep 10 seconds for checking if the file size is increased
                 fileInfo = fo.getFileInfo(filePath)
                 if int(fileInfo['Size']) != tmpFileSize:
                     self.__unFinishedDic[filePath] = int(fileSize)#Record the unfinished file for checking after a while
                     return#Will return if there has any changes upon the file size that means there has another process is downloading that file
             f = None
             try:
                f = file(filePath, "ab")
                self.logger.info(filePath)
                size = os.path.getsize( filePath )
                ftpCon.retrbinary("RETR %s" % (fileName), f.write, rest=size)
                self.__downloadedFileList.append(filePath)
             except Exception, e:
                print 'Exception thrown when downloading the file ', fileName
                logStr = 'Exception thrown when downloading the file '+ fileName
                self.logger.info(logStr)
             finally:
                if f!=None:
                    f.close()
       return
    
    def __unicodeToInt(self, l):
       for i in range(len(l)):
          l[i] = int(l[i])
          
    def __beforeLatest(self, fileDate, latest):
       timeSpaceHolder = ['0', '0', '0'] * 3
       
       fileDateList = fileDate.split("-")
       fileDateList.extend(timeSpaceHolder)
       self.__unicodeToInt(fileDateList)
       fileDateTuple = tuple(fileDateList[0:9])
       fileDateTime = time.mktime(fileDateTuple)
       
       currentTime = time.time()
       
       validTime = currentTime - int(latest)*24*60*60
       
       if fileDateTime >= validTime and fileDateTime < currentTime:
          return True
       return False
    
       
    def __getMonth(self, monStr):   
       month = {
          "Jan": lambda : "1",
          "Feb": lambda : "2",
          "Mar": lambda : "3",
          "Apr": lambda : "4",
          "May": lambda : "5",
          "Jun": lambda : "6",
          "Jul": lambda : "7",
          "Aug": lambda : "8",
          "Sep": lambda : "9",
          "Oct": lambda : "10",
          "Nov": lambda : "11",
          "Dec": lambda : "12"
          }[monStr]()
       return month
   
"""   
    def ls( self, ftpCon, cwd ):
        lines = []
        ftpCon.retrlines( "LIST", lines.append )
        return map( lambda x: FtpWalker.extract_info( cwd, x ), lines )
"""

class SyncerPoolManager:  
    def __init__( self, num_of_syncers=2, maxnum_of_syncers=8, timeout=1):
        self.__lock = RLock()#Thread relative
        self.timeout = timeout
        logging.config.fileConfig('log.config')
        self.logger = logging.getLogger()
        
        self.num_of_syncers = num_of_syncers
        self.maxnum_of_syncers = maxnum_of_syncers
        self.busySyncerQueue = []
        self.idleSyncerQueue = Queue.Queue(num_of_syncers)
        self.timerDic = {}
        self.syncerDic = {}

    def _initIdleSyncer(self):
        for i in range(self.num_of_syncers):  
            syncer = Synchronizer(self)
            syncer.start()
            self.idleSyncerQueue.put(syncer)
            
    def removeBusySyncer(self, syncer):
        self.__lock.acquire()
        if syncer in self.busySyncerQueue:
            self.busySyncerQueue.remove(syncer)
        self.__lock.release()
        
    def addBusySyncer(self, syncer):
        self.__lock.acquire()
        if not syncer in self.busySyncerQueue:
            self.busySyncerQueue.append(syncer)
        self.__lock.release()

    def runSyncer(self, parameter):
        self.__lock.acquire()
        syncer = None
        try:
            appendSyncer = True
            if len(self.busySyncerQueue)<self.maxnum_of_syncers and self.idleSyncerQueue.empty():
                syncer = Synchronizer(self)
                syncer.addParameter(parameter)
                syncer.start()
            else:
                try:
                    syncer = self.idleSyncerQueue.get(timeout=self.timeout)
                    syncer.addParameter(parameter)
                except:                    
                    if len(self.busySyncerQueue)<self.maxnum_of_syncers and self.idleSyncerQueue.empty():
                        syncer = Synchronizer(self)
                        syncer.addParameter(parameter)
                        syncer.start()
                    else:
                        #Leverage existed busy Syncer
                        appendSyncer = False
                        syncer = self.busySyncerQueue[random.randint(0, self.maxnum_of_syncers-1)]
                        syncer.addParameter(parameter)
            if appendSyncer:
                self.busySyncerQueue.append(syncer)
        except:
            self.logger.error("Generate a usable Synchronizer failure")
        self.__lock.release()
        
    
    def isIdlableSyncer(self, syncer):
        self.__lock.acquire()
        putSuccess = False
        try:
            if not syncer.isParameterEmpty():
                raise "The parameter queue is not empty"
            
            self.busySyncerQueue.remove(syncer)
            
            if not self.idleSyncerQueue.full():
                self.idleSyncerQueue.put(syncer, timeout=self.timeout)
                putSuccess = True
        except Queue.Full:
            putSuccess = False
        except Exception, e:
            putSuccess = False
        self.__lock.release()
        return putSuccess
    
    def setTimer(self, syncer):
        self.__lock.acquire()
        self.idle = False
        syncerName = syncer.getName() 
        timerName = "%s_timer" % syncerName
        funcArgs = [syncerName]
        funcKwargs = {}
        timer = Timer(self.timeout, self.__timesUp, funcArgs, funcKwargs)
        timer.setName(timerName)
        self.timerDic[timerName] = timer
        self.syncerDic[syncerName] = syncer
        timer.start()
        self.__lock.release()
    
    def cleanTimer(self, syncer):
        self.__lock.acquire()
        self.idle = True
        syncerName = syncer.getName() 
        timerName = "%s_timer" % syncerName
        timer = self.timerDic[timerName]
        if timer:
            timer.cancel()
        self.__lock.release()
        
    def __timesUp(self, args=[], kwargs={}):
        self.__lock.acquire()
        syncerName = args
        syncer = self.syncerDic[syncerName]
        if syncer and not syncer.idle:
            self.killSyncer(syncer)
        self.__lock.release()
        
    def killSyncer(self, syncer):
        self.__lock.acquire()
        try:
            if syncer in self.busySyncerQueue:
                self.busySyncerQueue.remove(syncer)
                
            """
            w32 = ctypes.windll.kernel32
            THREAD_TERMINATE = 1 # Privilege level for termination
            handle = w32.OpenThread(THREAD_TERMINATE, False, syncer.tid)
            result = w32.TerminateThread(handle, 0)
            w32.CloseHandle(handle)
            """
            
            from allTasks.Restart import childTask
            restart = childTask("Restart")
            self.logger.info('Restart QMS due to synchronizer hung')
            restart.run()
            
            syncer.terminate()
        except Exception, e:
            exstr = traceback.format_exc()
            print exstr
        self.__lock.release()
