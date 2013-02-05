"""

    QMSWebService.py
    
    Written by: Jacky Li(yxli@adobe.com)

"""

from SOAPpy import SOAPProxy, WSDL
from xml.dom.minidom import parseString

import globalProperty, time

class QMSWebService:
    
    #WSQMSURL = "http://blazeman.pac.adobe.com:8080/qmsserver/services/qmsService?WSDL"
    #WSQMSURL = "http://ps-builds.pac.adobe.com:8080/qmsserver/services/qmsService?WSDL"
    #WSQMSURL = "http://%s:8080/qmsserver/services/qmsService?WSDL" % globalProperty.configProperty['wsserver']
    #WSQMSURL = "http://ps-bj-qe.pac.adobe.com:8080/qmsserver/services/qmsService?WSDL"
    #WSQMSURL = "http://yxli-xp:8080/qmsserver/services/qmsService?WSDL"
    #WSQMSBUILDURL = "http://blazeman.pac.adobe.com:8080/qmsserver/services/buildService?WSDL"
    #WSQMSBUILDURL = "http://ps-builds.pac.adobe.com:8080/qmsserver/services/buildService?WSDL"
    #WSQMSBUILDURL = "http://ps-builds.pac.adobe.com:8080/qmsserver/services/buildService?WSDL"
    #WSQMSBUILDURL = "http://%s:8080/qmsserver/services/buildService?WSDL" % globalProperty.configProperty['wsserver']
    #WSQMSBUILDURL = "http://ps-bj-qe.pac.adobe.com:8080/qmsserver/services/buildService?WSDL"
    #WSQMSBUILDURL = "http://yxli-xp:8080/qmsserver/services/buildService?WSDL"
    #WSQMSAUTOURL = "http://blazeman.pac.adobe.com:8080/qmsserver/services/qmsAutoService?wsdl"
    #WSQMSAUTOURL = "http://ps-builds.pac.adobe.com:8080/qmsserver/services/qmsAutoService?wsdl"
    #WSQMSAUTOURL = "http://%s:8080/qmsserver/services/qmsAutoService?wsdl" % globalProperty.configProperty['wsserver']
    #WSQMSAUTOURL = "http://ps-bj-qe.pac.adobe.com:8080/qmsserver/services/qmsAutoService?wsdl"
    #WSQMSAUTOURL = "http://yxli-xp:8080/qmsserver/services/qmsAutoService?wsdl"
                
    def __init__(self):
        try:
            self._WSQMSURL = "http://%s/services/qmsService?WSDL" % globalProperty.configProperty['wsserver']
            self._WSQMSBUILDURL = "http://%s/services/buildService?WSDL" % globalProperty.configProperty['wsserver']
            self._WSQMSAUTOURL = "http://%s/services/qmsAutoService?wsdl" % globalProperty.configProperty['wsserver']
            self.__qmsServer = WSDL.Proxy(self._WSQMSURL)
            self.__buildServer = WSDL.Proxy(self._WSQMSBUILDURL)
            self.__qmsAutoServer = WSDL.Proxy(self._WSQMSAUTOURL)
        except Exception, e:
            self.__qmsServer = None
            self.__buildServer = None
            self.__qmsAutoServer = None
    
    def __getQMSServer(self, refresh=False):
        if 'webservice' in globalProperty.configProperty and globalProperty.configProperty['webservice']=="none":
            self.__qmsServer = None
        elif refresh or self.__qmsServer==None:
            print "Try to get QMS Server"
            while True:
                try: 
                    self.__qmsServer = WSDL.Proxy(self._WSQMSURL)
                except Exception, e:
                    self.__qmsServer = None
                if self.__qmsServer:
                    break
                time.sleep(1)
            
    def __getQMSBuildServer(self, refresh=False):
        if 'webservice' in globalProperty.configProperty and globalProperty.configProperty['webservice']=="none":
            self.__buildServer = None
        elif refresh or self.__buildServer==None:
            print "Try to get QMS Build Server"
            while True:
                try: 
                    self.__buildServer = WSDL.Proxy(self._WSQMSBUILDURL)
                except Exception, e:
                    self.__buildServer = None
                if self.__buildServer:
                    break
                time.sleep(1)
            
    def __getQMSAutoServer(self, refresh=False):
        if 'webservice' in globalProperty.configProperty and globalProperty.configProperty['webservice']=="none":
            self.__qmsAutoServer = None
        elif refresh or self.__qmsAutoServer==None:
            print "Try to get QMS Auto Server"
            while True:
                try: 
                    self.__qmsAutoServer = WSDL.Proxy(self._WSQMSAUTOURL)
                except Exception, e:
                    self.__qmsAutoServer = None
                if self.__qmsAutoServer:
                    break
                time.sleep(1)
            
    def updateMachine(self, macAddress, ip_address, os, hostname, userId="free", managerName='none'):
        #self.__update("INSERT INTO machine (address, ip_address, user_id, os_type, machine_name) VALUES(%s, %s, %s, %s, %s)", (self.__macAddress, _ip_address, "free", _os, _hostname))
        #self.__update("UPDATE machine set user_id = %s, ip_address = %s WHERE address = %s", (userId, _ip_address, self.__macAddress))
        print "Update Machine"
        try:
            self.__getQMSServer()
            if self.__qmsServer != None:
                self.__qmsServer.updateMachine(
                                               macAddress, 
                                               userId, 
                                               ip_address, 
                                               os, 
                                               hostname,
                                               managerName)
        except Exception, e:
            print e
            
    #Deprecated
    def updateMachineIp(self, macAddress, ip_address, os, hostname):
        #self.__update("INSERT INTO machine (address, ip_address, user_id, os_type, machine_name) VALUES(%s, %s, %s, %s, %s)", (self.__macAddress, _ip_address, "free", _os, _hostname))
        #self.__update("UPDATE machine set user_id = %s, ip_address = %s WHERE address = %s", (userId, _ip_address, self.__macAddress))
        print "Update Machine IP"
        try:
            self.__getQMSServer()
            if self.__qmsServer != None:
                self.__qmsServer.updateMachineIp(
                                               macAddress,
                                               ip_address, 
                                               os, 
                                               hostname)
        except Exception, e:
            print e
            
    def updateMachineInfo(self, macAddress, ip_address, os, hostname, osVersion, locale,videoAdapter,owner):
        print "Update Machine Info"
        try:
            self.__getQMSServer()
            if self.__qmsServer != None:
                self.__qmsServer.updateMachineInfo(
                                               macAddress,
                                               ip_address, 
                                               os, 
                                               hostname,
                                               osVersion, 
                                               locale,
                                               videoAdapter,
                                               owner)
        except Exception, e:
            print e
            
    def updateMachineName(self, macAddress, hostname):
        print "Update Machine Name"
        try:
            self.__getQMSServer()
            if self.__qmsServer != None:
                self.__qmsServer.updateMachineName(
                                               macAddress,
                                               hostname)
        except Exception, e:
            print e
            
    def updateLabMachineStatus(self, macAddress, status):
        #self.__update("INSERT INTO machine (address, ip_address, user_id, os_type, machine_name) VALUES(%s, %s, %s, %s, %s)", (self.__macAddress, _ip_address, "free", _os, _hostname))
        #self.__update("UPDATE machine set user_id = %s, ip_address = %s WHERE address = %s", (userId, _ip_address, self.__macAddress))
        print "Update Lab Machine Status"
        try:
            self.__getQMSServer()
            if self.__qmsServer != None:
                self.__qmsServer.updateLabMachineStatus(
                                               macAddress,
                                               status)
        except Exception, e:
            print e
            
    def addNewJob(self, jobId, jobTitle, userId, macAddress, content, comment, fileName, jobType, scheduleTime, timeout=60, lastStatus="scheduled", sortpattern="linear"):
        #self.__update("INSERT INTO job (job_id, user_id, received_time, target_machine, content, comment, timeout, file_name, job_type) VALUES (%s, %s, now(), %s, %s, %s, %s, %s, %s)", 
        #          (jobId, userId, self.__macAddress, content, comment, timeout, fileName, jobType))
        print "Add a new Job"
        try:
            self.__getQMSServer()
            if self.__qmsServer != None:
                self.__qmsServer.addNewJob(
                                           jobId,
                                           jobTitle, 
                                           userId, 
                                           macAddress, 
                                           content, 
                                           comment, 
                                           timeout, 
                                           fileName, 
                                           jobType, 
                                           lastStatus, 
                                           sortpattern,
                                           str(scheduleTime))
                                           #scheduleTime.isoformat())
        except Exception, e:
            print e
            
    def updateJobInfo(self, jobId, status, errorMsg, scheduleTime):
        #self.__update("UPDATE job set last_status = %s, last_error_msg = %s WHERE job_id = %s", (status, errorMsg, jobId))
        print "Update Job Info"
        try:
            self.__getQMSServer()
            if self.__qmsServer != None:
                self.__qmsServer.updateJobInfo(jobId, status, errorMsg, str(scheduleTime))
        except Exception, e:
            print e
            
    def deleteJob(self, jobId):
        #self.__update("UPDATE job set last_status = %s, last_error_msg = %s WHERE job_id = %s", (status, errorMsg, jobId))
        print "Update Job"
        try:
            self.__getQMSServer()
            if self.__qmsServer != None:
                self.__qmsServer.deleteJob(jobId)
        except Exception, e:
            print e

    def addNewJobDetail(self, jobId, taskId, sequence):
        #"INSERT INTO job_detail (job_id, task_id, sequence) VALUES (%s, %s, %s)", params
        print "Add a new Job Detail"
        try:
            self.__getQMSServer()
            if self.__qmsServer != None:
                self.__qmsServer.addNewJobDetail(
                                           jobId, 
                                           taskId, 
                                           sequence)
        except Exception, e:
            print e
            
    def addNewExecution(self, jobId):
        #"INSERT INTO job_detail (job_id, task_id, sequence) VALUES (%s, %s, %s)", params
        print "Add a new Execution"
        try:
            self.__getQMSServer()
            if self.__qmsServer != None:
                executionId = self.__qmsServer.addNewExecution(jobId)
                return executionId
        except Exception, e:
            print e
            
    def updateExecution(self, exectuionId, status, errorMsg):
        #self.__update("UPDATE execution set status = %s, error_msg = %s, finish_time = now() WHERE execution_id = %s", (status, errorMsg, executionId))
        print "Update Execution"
        try:
            self.__getQMSServer()
            if self.__qmsServer != None:
                self.__qmsServer.updateExecution(exectuionId, status, errorMsg)
        except Exception, e:
            print e
    
    #@Deprecated
    def addNewExecutionDetailByTaskId(self, executionId, taskId, taskPriority):
        #self.__update("INSERT INTO execution_detail (execution_id, task_id, start_time, priority) VALUES (%s, %s, now(), %s)", (executionId, taskId, taskPriority))
        print "Add a new Execution Detail"
        try:
            self.__getQMSServer()
            if self.__qmsServer != None:
                self.__qmsServer.addNewExecutionDetailByTaskId(executionId, taskId, taskPriority)
        except Exception, e:
            print e
            
    def addNewExecutionDetailByTaskName(self, executionId, taskName, taskPriority):
        #self.__update("INSERT INTO execution_detail (execution_id, task_id, start_time, priority) VALUES (%s, %s, now(), %s)", (executionId, taskId, taskPriority))
        print "Add a new Execution Detail"
        try:
            self.__getQMSServer()
            if self.__qmsServer != None:
                self.__qmsServer.addNewExecutionDetailByTaskName(executionId, taskName, taskPriority)
        except Exception, e:
            print e
            
    def updateExecutionDetail(self, executionId, taskId, taskPriority, status, errorMsg, note):
        #self.__update("UPDATE execution_detail set finish_time = now(), status = %s, error_msg = %s WHERE execution_id = %s AND task_id = %s", (status, errorMsg, executionId, taskId))
        print "Update Execution Detail"
        try:
            self.__getQMSServer()
            if self.__qmsServer != None:
                self.__qmsServer.updateExecutionDetail(executionId, taskId, taskPriority, status, errorMsg, note)
        except Exception, e:
            print e
            
    def getProductTeam(self, manager):
        print "Get name of product team managed by %s" %manager
        try:
            self.__getQMSServer()
            if self.__qmsServer != None:
                return self.__qmsServer.getProductTeam(manager)
        except Exception, e:
            print e
            
    def updateProductTeam(self, team, manager):
        print "Update a new product team %s managed by %s" %(team, manager)
        try:
            self.__getQMSServer()
            if self.__qmsServer != None:
                return self.__qmsServer.updateProductTeam(team, manager)
        except Exception, e:
            print e
            
    def getTask(self):
        print "Get all tasks"
        try:
            self.__getQMSServer()
            if self.__qmsServer != None:
                return self.__qmsServer.getTask()
        except Exception, e:
            print e
            
    def addNewLatestBuild(self, productName, version, buildNum, platform, language, certLevel, subProduct, latestBuildLocation):
        #self.__update("UPDATE execution_detail set finish_time = now(), status = %s, error_msg = %s WHERE execution_id = %s AND task_id = %s", (status, errorMsg, executionId, taskId))
        print "add New Latest Build"
        try:
            self.__getQMSBuildServer()
            if self.__buildServer != None:
                self.__buildServer.addNewLatestBuild(productName, version, buildNum, platform, language, certLevel, subProduct, latestBuildLocation)
        except Exception, e:
            print e
            
    def addPsfProductFeature(self, productName, featureName):
        print "Add PSF Supported Product Feature"
        try:
            self.__getQMSServer()
            if self.__qmsServer != None:
                self.__qmsServer.addPsfProductFeature(productName, featureName)
        except Exception, e:
            print e
            
    def kickOffAutoTest(self, platform):
        print "Kick off autotest"
        try:
            self.__getQMSAutoServer()
            if self.__qmsAutoServer != None:
                self.__qmsAutoServer.kickOffAutoTest(platform)
        except Exception, e:
            print e
            
    def kickOffTestwerkThumbPerfTest(self, kickOffMachineAddress, targetMachineAddress, caseType, testType, appVersion, sendResult, appBuild):
        print "Kick off testwerk performance test"
        try:
            self.__getQMSAutoServer()
            if self.__qmsAutoServer != None:
                self.__qmsAutoServer.kickOffTestwerkThumbPerfTest(kickOffMachineAddress, targetMachineAddress, caseType, testType, appVersion, sendResult, appBuild)
        except Exception, e:
            print e
            
    def getMachineName(self, macAddress):
        print "get Machine Name by MAC address"
        try:
            self.__getQMSServer()
            if self.__qmsServer != None:
                return self.__qmsServer.getMachineName(macAddress)
        except Exception, e:
            print e
    
    def getMachineByMacAddress(self, macAddress):
        print "get Machine by MAC address"
        try:
            self.__getQMSServer()
            if self.__qmsServer != None:
                return self.__qmsServer.getMachineByMacAddress(macAddress)
        except Exception, e:
            print e

    def getUserIDByJobID(self, jobID):
        print "get User Id by Job Id"
        try:
            self.__getQMSServer()
            if self.__qmsServer != None:
                return self.__qmsServer.getUserIDByJobID(jobID)
        except Exception, e:
            print e
            
    def getExecutionIDByJobID(self, jobID):
        print "get Execution Id by Job Id"
        try:
            self.__getQMSServer()
            if self.__qmsServer != None:
                return self.__qmsServer.getExecutionIDByJobID(jobID)
        except Exception, e:
            print e
            
    def getAppInfo(self, key):
        print "get info by key %s" %key
        try:
            self.__getQMSServer()
            if self.__qmsServer != None:
                return self.__qmsServer.getAppInfo(key)
        except Exception, e:
            print e
            
    def getAppInfoXml(self):
        print "get info xml"
        try:
            self.__getQMSServer()
            if self.__qmsServer != None:
                return self.__qmsServer.getAppInfoXml()
        except Exception, e:
            print e

    def getMachineImage(self, model, osType, edition, osLang):
        print "get getMachineImage by model, osType, edition, osLang"
        try:
            self.__getQMSServer()
            if self.__qmsServer != None:
                return self.__qmsServer.getMachineImage(model, osType, edition, osLang)
        except Exception, e:
            print e
            
    def getLatestBuild(self, productName, version, platform, language, certLevel, subproduct):
        print "get labtest build by model, osType, edition"
        try:
            self.__getQMSServer()
            if self.__qmsServer != None:
                return self.__qmsServer.getLatestBuildNew(productName, version, platform, language, certLevel, subproduct)
        except Exception, e:
            print e
    
    def getJobContent(self, jobId):
        print "get Job Content by Job Id"
        try:
            self.__getQMSServer()
            if self.__qmsServer != None:
                return self.__qmsServer.getJobContent(jobId)
        except Exception, e:
            print e
            
    def getTaskOwnerByExeId(self, executionId):
        print "get Task Owner by Execution Id"
        try:
            self.__getQMSServer()
            if self.__qmsServer != None:
                return self.__qmsServer.getTaskOwnerByExeId(executionId)
        except Exception, e:
            print e
            
    def hasProductWithFeature(self, productName, featureName):
        print "get Product Feature by Execution Id"
        try:
            self.__getQMSServer()
            if self.__qmsServer != None:
                return self.__qmsServer.getTaskOwnerByExeId(productName, featureName)
        except Exception, e:
            print e
            
    def getExecutionResult(self, executionId):
        print "get Execution Result by Execution Id"
        try:
            self.__getQMSServer()
            if self.__qmsServer != None:
                return self.__qmsServer.getExecutionResult(executionId)
        except Exception, e:
            print e
            
    def getJobDetail(self, jobId):
        print "get Job Detail by Job Id"
        try:
            self.__getQMSServer()
            if self.__qmsServer != None:
                return self.__qmsServer.getJobDetail(jobId)
        except Exception, e:
            print e
            
    def getValidTestCasesFromTS(self, productName, controllerFileName):
        print "get Valid Test Cases according to product %s's controller file %s" % (productName, controllerFileName)
        try:
            self.__getQMSAutoServer()
            if self.__qmsAutoServer != None:
                return self.__qmsAutoServer.getValidTestCasesFromTS(productName, controllerFileName)
        except Exception, e:
            print e
            
