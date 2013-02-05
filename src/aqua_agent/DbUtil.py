"""

    DBUtil.py
    
    Written by: Tianying Yang
    Written by: Jacky Li
    Web Service Supported by: Jacky Li(yxli@adobe.com)

"""
#import MySQLdb
import xml.parsers.expat
import logging
import logging.config
import os
import os.path
import socket
import globalProperty
from QMSWebService import QMSWebService
from service.TSProxyService import TSProxyService

from tasksType.TasksTypeMgr import TasksTypeMgr
from xml.dom import minidom
from threading import RLock

from SOAPpy import SOAPProxy, WSDL
from xml.dom.minidom import parseString

class DbUtil:
    
    def __init__(self):
        logging.config.fileConfig('log.config')
        
        self.__qmsWS = QMSWebService()
        
        self.__tsProxy = TSProxyService()
        
        self.logger = logging.getLogger()

        self.__lock = RLock()#Thread relative
        
        self.taskDict = {}
        
        try:
            #self.__conn = MySQLdb.connect(host="blazeman.pac.adobe.com", db="qmsu", user="jacky", passwd="goodluck")
            #self.__conn = MySQLdb.connect(host="ps-builds.pac.adobe.com", db="qmsu", user="jacky", passwd="goodluck")
            #self.__conn = MySQLdb.connect(host="ps-bj-qe.pac.adobe.com", db="qmsu", user="jacky", passwd="goodluck")
            #self.__conn = MySQLdb.connect(host="yxli-xp", db="qmsu", user="jacky", passwd="goodluck")
            ''' by nle
            self.__conn = MySQLdb.connect(host=globalProperty.configProperty['dbserver'], 
                                          db=globalProperty.configProperty['dbname'], 
                                          user=globalProperty.configProperty['dbuser'], 
                                          passwd=globalProperty.configProperty['dbpassword'])
            self.__conn.autocommit(1)

            sql = "SELECT task_id, task_name FROM task"
            for (id, name) in self.__query(sql):
                self.taskDict[name] = int(id)   #...god...how come it became long...
            print self.taskDict
            self.getTask()
            '''
        except Exception, e:
            self.logger.error(e)

        self.__macAddress = globalProperty.getMacAddress()
        
    def __connect(self):
        #http://dev.mysql.com/doc/refman/5.0/en/auto-reconnect.html
        self.__conn.ping(True)
        '''
        try:
            self.__conn.ping()
        except:
            self.logger.debug('reconnect to mysql...gosh')
            self.__conn = MySQLdb.connect(host="192.168.0.120", db="qms", user="root", passwd="goodluck")
            self.__conn.autocommit(1)
        '''
    
    def __update(self, sql, param=None):
        self.__lock.acquire()
        try:
            self.__connect()
            c = self.__conn.cursor()
            if type(param) == list:
                for item in param:
                    self.logger.debug(sql % item if item else sql)
                c.executemany(sql, param)
            else:
                c.execute(sql, param)
            return c.lastrowid
        except Exception, e:
            self.logger.error(e)
            print e
        finally:
            self.__lock.release()
    
    def __query(self, sql, param=None):
        self.__lock.acquire()
        try:
            self.__connect()
            c = self.__conn.cursor()
            self.logger.debug(sql % param if param else sql)
            r = c.execute(sql, param)
            return c.fetchall()
        except Exception, e:
            self.logger.error(e)
            print e
        finally:
            self.__lock.release()
    
    '''
    @warning: Should be Deprecated
    '''
    def addNewJob(self, task, jobType):
#    task object:
#        dict: {u'sortpattern': u'linear', 'fileName': 'task_375f6b30-5d50-11dd-9e0a-001aa008bf35.tk', u'startTime': u'17:24:59', u'startDate': u'2008-07-29'}
        comment = task['comment']
        fileName = task['fileName']
        jobId = fileName[5:-3]
        userId = str(task['username'])
        jobTitle = str(task['jobTitle'])
        if task['timeout']:
            timeout = int(task['timeout'])
        else:
            timeout = None
        
        #Comment it out because I think it's not necessary to update machine if just adding job not executing job 
        #self.updateMachine(userId)
        
        '''
        r = self.__query("SELECT * FROM machine WHERE address = %s", self.__macAddress)
        if r != None and not len(r):
            _os = 'win' if os.name == 'nt' else 'mac'
            _hostname = socket.gethostname()
            self.__update("INSERT INTO machine (address, user_id, os_type) VALUES(%s, %s, %s)", (self.__macAddress, userId, _os))
        '''
        
        #for repeated jobs, scheduleOneTask would be called after each execution
        #since there's no such logic to determine if it is the first call, we have to check the database
        #FIXME: got to have a better solution 
        ''' by nlei
        r = self.__query("SELECT * FROM job WHERE job_id = %s", jobId)
        '''
        r = self.__qmsWS.getJobContent(jobId);
        if r != None and not len(r):
            f = open(os.path.join(globalProperty.getRestSchTkMgrInstance().getSchedulTaskDir(), fileName))
            content = f.read()
            if timeout:
                self.__qmsWS.addNewJob(jobId, jobTitle, userId, self.__macAddress, content, comment, fileName, jobType, timeout);
                #self.__update("INSERT INTO job (job_id, user_id, received_time, target_machine, content, comment, timeout, file_name, job_type) VALUES (%s, %s, now(), %s, %s, %s, %s, %s, %s)", 
                #          (jobId, userId, self.__macAddress, content, comment, timeout, fileName, jobType))
            else:
                self.__qmsWS.addNewJob(jobId, jobTitle, userId, self.__macAddress, content, comment, fileName, jobType);
                #self.__update("INSERT INTO job (job_id, user_id, received_time, target_machine, content, comment, file_name, job_type) VALUES (%s, %s, now(), %s, %s, %s, %s, %s)", 
                #          (jobId, userId, self.__macAddress, content, comment, fileName, jobType))
    
            f.seek(0)
            doc = minidom.parse(f)
            params = []
            sequence = 0
            for task in doc.getElementsByTagName("Task"):
                type = task.getAttribute('type')
                if not type in self.taskDict.keys(): break
                taskId = self.taskDict[type]
                sequence += 1
                params.append((jobId, taskId, sequence))
                self.__qmsWS.addNewJobDetail(jobId, taskId, sequence);
            #self.__update("INSERT INTO job_detail (job_id, task_id, sequence) VALUES (%s, %s, %s)", params)
            f.close()
    
    
    def addNewScheduleJob(self, task, jobType, scheduleTime):
#    task object:
#        dict: {u'sortpattern': u'linear', 'fileName': 'task_375f6b30-5d50-11dd-9e0a-001aa008bf35.tk', u'startTime': u'17:24:59', u'startDate': u'2008-07-29'}
        comment = task['comment']
        fileName = task['fileName']
        jobId = fileName[5:-3]
        userId = str(task['username'])
        if task['timeout']:
            timeout = int(task['timeout'])
        else:
            timeout = None
        if task['title']:
            jobTitle = task['title']
        else:
            jobTitle = "unknown"
        
        #self.updateMachine(userId)
        
        '''
        r = self.__query("SELECT * FROM machine WHERE address = %s", self.__macAddress)
        if r != None and not len(r):
            _os = 'win' if os.name == 'nt' else 'mac'
            _hostname = socket.gethostname()
            self.__update("INSERT INTO machine (address, user_id, os_type) VALUES(%s, %s, %s)", (self.__macAddress, userId, _os))
        '''
        
        #for repeated jobs, scheduleOneTask would be called after each execution
        #since there's no such logic to determine if it is the first call, we have to check the database
        #FIXME: got to have a better solution 
        ''' by nlei
        r = self.__query("SELECT * FROM job WHERE job_id = %s", jobId)
        '''
        r = self.__qmsWS.getJobContent(jobId);
        if r != None and not len(r):
            f = None
            try:
                f = open(os.path.join(globalProperty.getRestSchTkMgrInstance().getSchedulTaskDir(), fileName))
                content = f.read()
                if timeout:
                    self.__qmsWS.addNewJob(jobId, jobTitle, userId, self.__macAddress, content, comment, fileName, jobType, scheduleTime, timeout)
                    #self.__update("INSERT INTO job (job_id, user_id, received_time, target_machine, content, comment, timeout, file_name, job_type) VALUES (%s, %s, now(), %s, %s, %s, %s, %s, %s)", 
                    #          (jobId, userId, self.__macAddress, content, comment, timeout, fileName, jobType))
                else:
                    self.__qmsWS.addNewJob(jobId, jobTitle, userId, self.__macAddress, content, comment, fileName, jobType, scheduleTime)
                    #self.__update("INSERT INTO job (job_id, user_id, received_time, target_machine, content, comment, file_name, job_type) VALUES (%s, %s, now(), %s, %s, %s, %s, %s)", 
                    #          (jobId, userId, self.__macAddress, content, comment, fileName, jobType))
        
                f.seek(0)
                doc = minidom.parse(f)
                params = []
                sequence = 0
                for task in doc.getElementsByTagName("Task"):
                    type = task.getAttribute('type')
                    if not type in self.taskDict.keys(): break
                    taskId = self.taskDict[type]
                    sequence += 1
                    params.append((jobId, taskId, sequence))
                    self.__qmsWS.addNewJobDetail(jobId, taskId, sequence)
                #self.__update("INSERT INTO job_detail (job_id, task_id, sequence) VALUES (%s, %s, %s)", params)
            except Exception, e:
                self.logger.error(e)
            finally:
                try:
                    f.close()
                except Exception, e:
                    pass
        else:
            self.__qmsWS.updateJobInfo(jobId, "scheduled", None, scheduleTime)
            
    def updateMachine(self, userId="free"):
        #r = self.__query("SELECT * FROM machine WHERE address = %s", self.__macAddress)
        
        _hostname = socket.gethostname()
        try:
            _ip_address = globalProperty.getIpAddress()
        except Exception, e:
            self.logger.error(e)
            return
        _os = 'win' if os.name == 'nt' else 'mac'
        '''
        if r!=None and len(r)>0:
            ipAddress = r[0][1]
            userName = r[0][2]
            teamname = r[0][5]
            if ipAddress==_ip_address and userName==userId and teamname==globalProperty.getProductTeam():
                return
            elif userName=="private" or userName=="server" or userName=="build" or userName=="performance" or userName=="kickoff":
                #Some machine's owner could not be free
                userId = userName
        '''    
        self.__qmsWS.updateMachine(self.__macAddress, _ip_address, _os, _hostname, userId, globalProperty.getManagerName())
        '''
                self.__qmsWS.updateMachineIp(self.__macAddress, _ip_address, _os, _hostname)
                return
            elif userName==userId:
                return
        
        self.__qmsWS.updateMachine(self.__macAddress, _ip_address, _os, _hostname, userId)
        '''
        '''
        if r != None and not len(r):
            _os = 'win' if os.name == 'nt' else 'mac'            
            #self.__update("INSERT INTO machine (address, ip_address, user_id, os_type, machine_name) VALUES(%s, %s, %s, %s, %s)", (self.__macAddress, _ip_address, "free", _os, _hostname))
        elif userId!=None and userId!="":
            #self.__update("UPDATE machine set user_id = %s, ip_address = %s WHERE address = %s", (userId, _ip_address, self.__macAddress))
        ''' 
        
    def updateMachineIp(self):
        #r = self.__query("SELECT * FROM machine WHERE address = %s", self.__macAddress)
        
        _hostname = socket.gethostname()
        try:
            _ip_address = globalProperty.getIpAddress()
        except Exception, e:
            print e
            self.logger.error(e)
            return
        _os = 'win' if os.name == 'nt' else 'mac'
        ''' by nlei
        if r!=None and len(r)>0:
            ipAddress = r[0][1]
            userName = r[0][2]
            if ipAddress==_ip_address:
                return
        '''    
        self.__qmsWS.updateMachineIp(self.__macAddress, _ip_address, _os, _hostname)
        
    def updateMachineInfo(self):
        _hostnameConfig = globalProperty.getMachineName()
        _hostname = socket.gethostname()
        try:
            _ip_address = globalProperty.getIpAddress()
        except Exception, e:
            print e
            self.logger.error(e)
            return
        _os = 'win' if os.name == 'nt' else 'mac'
        sysInfo = globalProperty.getSysInfo()
        _osVersion = sysInfo.os
        _locale = sysInfo.locale  
        _videoAdapter = sysInfo.videoAdapter
        _owner=globalProperty.getOwner()
        self.__qmsWS.updateMachineInfo(self.__macAddress, _ip_address, _os, _hostname, _osVersion ,_locale,_videoAdapter,_owner)
        if _hostnameConfig:
            self.__qmsWS.updateMachineName(self.__macAddress, _hostnameConfig)
      
    def startExecution(self, filePath):
        jobId = filePath[filePath.rfind('_') + 1:-3]
        ''' by nlei
        r = self.__query("SELECT user_id FROM job WHERE job_id = %s", jobId)
        if r != None and len(r)!=0:
            userId = r[0][0]
            #Need to notify I am occupied
            self.updateMachine(userId)
        '''
        userId = self.__qmsWS.getUserIDByJobID(jobId)
        if userId != None:
            self.updateMachine(userId)
        return self.__qmsWS.addNewExecution(jobId)
        #return self.__update("INSERT INTO execution (job_id, start_time) VALUES (%s, now())", jobId)
    
    def getLatestExecutionId(self, filePath):
        try:
            jobId = filePath[filePath.rfind('_') + 1:-3]
            ''' by nlei
            sql = "SELECT execution_id FROM execution WHERE job_id = %s ORDER BY execution_id desc"
            exeId = self.__query(sql, jobId)[0][0]
            '''
            exeId = self.__qmsWS.getExecutionIDByJobID(jobId)
        except Exception, e:
            print e
            return None
        if(exeId==None):
            return None
        else:
            return int(exeId)
    
    def finishExecution(self, filePath, exeId, status, errorMsg):
        if exeId==None:
            return
        jobId = filePath[filePath.rfind('_') + 1:-3]
        self.__qmsWS.updateExecution(exeId, status, errorMsg)
        #self.__update("UPDATE execution set status = %s, error_msg = %s, finish_time = now() WHERE execution_id = %s", (status, errorMsg, exeId))
        
        self.__qmsWS.updateJobInfo(jobId, status, errorMsg, None)
        
        #Need to update machine to notify I am free
        self.updateMachine()
        
        #self.__update("UPDATE job set last_status = %s, last_error_msg = %s WHERE job_id = %s", (status, errorMsg, jobId))
        
    def deleteTask(self, jobId):
        self.__qmsWS.deleteJob(jobId)
    
    def startTask(self, exeId, task):
        try:
            #taskId = self.taskDict[task.type]
            taskPriority = str(task.getPriority())
            #self.__qmsWS.addNewExecutionDetailByTaskId(exeId, taskId, taskPriority)
            self.__qmsWS.addNewExecutionDetailByTaskName(exeId, task.type, taskPriority)
        except Exception, e:
            print e
            self.logger.debug(self.taskDict)
            self.logger.error(e)
        #self.__update("INSERT INTO execution_detail (execution_id, task_id, start_time, priority) VALUES (%s, %s, now(), %s)", (exeId, taskId, taskPriority))

    def finishTask(self, exeId, task, status, errorMsg='', noteMsg=''):
        if not task.type in self.taskDict.keys():return
        taskId = self.taskDict[task.type]
        taskPriority = str(task.getPriority())
        self.__qmsWS.updateExecutionDetail(exeId, taskId, taskPriority, status, errorMsg, noteMsg)
        #self.__update("UPDATE execution_detail set finish_time = now(), status = %s, error_msg = %s WHERE execution_id = %s AND task_id = %s", (status, errorMsg, exeId, taskId))
        
    #for email util
    def getExecutionResult(self, exeId):
        ''' by nlei
        sql = "SELECT task_name, start_time, finish_time, status, error_msg FROM execution_detail NATURAL JOIN task WHERE execution_id = %s AND task_name <> %s  AND task_name <> %s"
        return self.__query(sql, (exeId, 'EmailUtil', 'EmailMonitor'))
        '''
        #return self.__qmsWS.getExecutionResult(exeId)
        results = self.__qmsWS.getExecutionResult(exeId).split('$')
        R=[]
        for result in results:
            details = result.split('%')
            L=[]
            for detail in details:
                L.append(detail)
            #print L
            R.append(L)
        return R
    
    def getJobDetail(self, jobId):   
        ''' by nlei     
        sql = "SELECT task_name, sequence FROM job_detail NATURAL JOIN task WHERE job_id = %s AND task_name <> %s  AND task_name <> %s  ORDER BY sequence asc"
        return self.__query(sql, (jobId, 'EmailUtil', 'EmailMonitor'))
        '''
        #return self.__qmsWS.getJobDetail(jobId)
        results = self.__qmsWS.getJobDetail(jobId)
        if(results!=None):
            results=results.split('$')
            R=[]
            for result in results:
                details = result.split('%')
                R.append(details)
                """
                L=[]
                for detail in details:
                    L.append(detail)
                    #print L
                    R.append(L)
                """
            return R
        else:
            return None
    
    #for email util
    def getTaskOwnerResultByExeId(self, exeId):
        ''' by nlei
        sql = "select user_id from job inner join execution using (job_id) where execution_id=%s"
        return self.__query(sql, (exeId))
        '''
        return self.__qmsWS.getTaskOwnerByExeId(exeId)
    
    def getAppInfo(self, key):
        ''' by nlei
        sql = "SELECT value FROM info WHERE value_key = %s"
        result = self.__query(sql, key)
        if not result: return None
        return result[0][0]
        '''
        #return self.__qmsWS.getAppInfo(key)
        return globalProperty.getAppInfo(key)
    
    def getAppInfoXml(self):
        return self.__qmsWS.getAppInfoXml()
    
    def getProductTeam(self, manager):
        if manager==None or manager.strip()=="":
            return None
        
        ''' by nlei
        sql = "SELECT team_name FROM product_team WHERE manager_name = %s"
        result = self.__query(sql, manager)
        if not result:
            team = manager + "_team"
            team = team.upper()
            self.__qmsWS.updateProductTeam(team, manager)
            return team
        '''
        return self.__qmsWS.getProductTeam(manager)
    
    def getMachineName(self):
        ''' by nlei
        sql = "SELECT machine_name from machine WHERE address=%s"
        result = self.__query(sql, (self.__macAddress))
        if not result: return None
        '''
        return self.__qmsWS.getMachineName(self.__macAddress)
    
    def getMachineByMacAddress(self, macAddress):
        ''' by nlei
        sql = "SELECT ip_address, os_type from machine WHERE address=%s"
        result = self.__query(sql, (macAddress))
        if not result: return None
        return result[0]
        '''
        results = self.__qmsWS.getMachineByMacAddress(macAddress).split('$')
        L=[]
        for result in results:
            L.append(result)
        return L
    
    def addNewLatestBuild(self, productName, version, buildNum, platform, language, certLevel, subProduct, latestBuildLocation):
        self.__qmsWS.addNewLatestBuild(productName, version, buildNum, platform, language, certLevel, subProduct, latestBuildLocation)
        
    def getLatestBuild(self, productName, version, platform, language, certLevel, subproduct='Application'):
        ''' by nlei
        sql = "SELECT build_num, latest_build_location from product inner join latest_build using(product_id) WHERE product_name=%s AND version=%s AND platform=%s AND language=%s AND cert_level=%s"
        result = self.__query(sql, (productName, version, platform, language, certLevel))
        if not result: return None
        return result[0]
        '''
        result = self.__qmsWS.getLatestBuild(productName, version, platform, language, certLevel, subproduct)
        if not result: return None
        return result.split('$')
    
    def getMachineImage(self, model, osType, edition, osLang):
        ''' by nlei
        sql = "select image_location from auto_machine_image inner join auto_machine_os using (os_id) inner join auto_machine_model using (model_id) where model=%s and os_type=%s and edition=%s"
        result = self.__query(sql, (model, osType, edition))
        if not result: return None
        return result[0][0]
        '''
        return self.__qmsWS.getMachineImage(model, osType, edition, osLang)
    
    def hasProductWithFeature(self, productName, featureName):
        ''' by nlei
        sql = "select * from psf_product_feature inner join psf_product using (psf_product_id) where product_name=%s and feature_name=%s"
        result = self.__query(sql, (productName, featureName))
        if not result: return False
        return True
        '''
        return self.__qmsWS.hasProductWithFeature(productName, featureName)
    
    def getMacAddress(self):
        return self.__macAddress
    
    def getTask(self):
        tasksXml = self.__qmsWS.getTask()
        #self.logger.debug(tasksXml)
        if tasksXml:
            p = xml.parsers.expat.ParserCreate()
            p.StartElementHandler = self.__start_element
            #p.EndElementHandler = self.__end_element
            p.Parse(tasksXml)
        
    def __start_element(self, name, attrs):
        if name.strip().lower() == 'task':
            self.taskDict[attrs['taskName']] = int(attrs['taskId'])
    
    def getValidTestCasesFromTS(self, productName, controllerFileName):
        #caseXML = self.__qmsWS.getValidTestCasesFromTS(productName, controllerFileName)
        caseXML = self.__tsProxy.getValidTestCasesFromTS(productName, controllerFileName)
        return caseXML

if __name__ == '__main__':
    #d = DbUtil()
    try:
        '''
        db = MySQLdb.connect(host="10.162.122.151", db="qms", user="root", passwd="goodluck")
        db.autocommit(1)
        c = db.cursor()
        for table in ['job', 'job_detail', 'execution', 'execution_detail']:
            print table, c.execute("delete FROM " + table)
        '''
        #dbutil = globalProperty.getDbUtil()
        #print dbutil.getExecutionResult(1)
        '''
        data = dbutil.getExecutionResult(1).split('$')
        p=[]
        for task in data:
            details = task.split('%')
            L=[]
            for detail in details:
                L.append(detail)
            print L
            p.append(L)
        print p
        '''
        
    except Exception, e:
        print e
