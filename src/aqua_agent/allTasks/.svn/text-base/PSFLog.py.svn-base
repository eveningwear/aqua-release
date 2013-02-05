from xml.dom import minidom,Node
import ftplib
import os
import sys
import datetime

class PSFLog:
    def __init__(self, logger):
        self.__logger = logger
        
        self.__doc = minidom.Document()
        self.__root = self.__doc.createElement("TestSession")
        self.__root.setAttribute("schemaVersion", "1.2 PS Subset")
        self.__doc.appendChild(self.__root)
        
        self.__ownersNode = self.__doc.createElement("Owners")
        self.__root.appendChild(self.__ownersNode)
        
        self.__testResultsList = []
        return
    
    def setSUT(self, appName, version, platform, locale, config):
        self.__SUTNode = self.__doc.createElement("SUT")
        self.__SUTNode.setAttribute("name", appName)
        self.__SUTNode.setAttribute("version", version)
        self.__SUTNode.setAttribute("platform", platform)
        self.__SUTNode.setAttribute("locale", locale)
        self.__SUTNode.setAttribute("config", config)
        self.__root.appendChild(self.__SUTNode)
        return
    
    def setBuildVersion(self, value):
        self.__buildVersionNode = self.__doc.createElement("Build")
        self.__buildVersionNode.setAttribute("buildVersion", value)
        
        self.__root.appendChild(self.__buildVersionNode)
        return
    
    def setTestEnvironment(self, machineName, osVersion, systemLanguage):
        self.__testEnvironmentNode = self.__doc.createElement("TestEnvironment")
        self.__testEnvironmentNode.setAttribute("machineName", machineName)
        self.__testEnvironmentNode.setAttribute("osVersion", osVersion)
        self.__testEnvironmentNode.setAttribute("systemLanguage", systemLanguage)
        
        self.__root.appendChild(self.__testEnvironmentNode)
        return
            
    def setStatus(self, status):
        self.__statusNode = self.__doc.createElement("Status")
        self.__statusNode.setAttribute("value", status)
        
        self.__root.appendChild(self.__statusNode)
        return
    
    def addTestResult(self, testResult):
        self.__testResultsList.append(testResult)
        return
    
    def addOwner(self, name, role):
        node = self.__doc.createElement("Owner")
        node.setAttribute("name", name)
        node.setAttribute("role", role)
        self.__ownersNode.appendChild(node)
        return

    def toXML(self):
        for tr in self.__testResultsList:
            self.__root.appendChild(tr.getNode())
        
#        return self.__doc.toprettyxml("  ", "\n", "UTF-8")
#        return self.__root.toprettyxml()
        return self.__root.toxml()
        
    def writeResult(self, path):
        self.__logger.info("write file on local sys:" + path)
        file = open(path, 'w')
        file.write(self.toXML())
        file.close()
        return
    
    def addLogtoPsautoDB(self, userName):       
#        wsdlURL = "http://psauto.corp.adobe.com/cs5/service.asmx?WSDL"
#        psautoService = WSDL.Proxy(wsdlURL)
#        
#        psautoService.soapproxy.config.dumpSOAPOut = 1
#        psautoService.soapproxy.config.dumpSOAPIn = 1
#        ret = psautoService.CS5_AddDatabaseFromXmlLog(userName, self.localFilename)
#        print ret
        import httplib
        conn=httplib.HTTPConnection("psauto.corp.adobe.com")
        requestURL = "/cs5/service.asmx/CS5_AddDatabaseFromXmlLog?sUserName=%s&sFileName=%s" % (userName, self.localFilename)
        conn.request("GET", requestURL)
        r=conn.getresponse()
        self.__logger.info('invoke psluna trigger API')
        self.__logger.info(r.read()) 
        return
    
    def uploadLog(self, fullname):        
        self.localFilename = os.path.split(fullname)[1]        
            
        self.__logger.info("Logging in FTP...")
        ftp = ftplib.FTP()
        host = "psauto.corp.adobe.com"
        ftp.connect(host)
        self.__logger.info(ftp.getwelcome())
        
        try:
            ftp.login("anonymous", "")
            ftp.cwd("_upload_log")
            # move to the desired upload directory
            self.__logger.info( "Currently in:" + ftp.pwd())
    
            self.__logger.info( "Uploading...")          
            name = os.path.split(fullname)[1]
            f = open(fullname, "rb")
            ftp.storbinary('STOR ' + name, f)
            f.close()
            self.__logger.info( "OK")
            
#            print "Files:"
    #            print ftp.retrlines('LIST')
        finally:
            self.__logger.info( "Quitting...")
            ftp.quit()

    def sendToPSLuna(self, username, fullFilename):
        self.writeResult(fullFilename)
        self.uploadLog(fullFilename)
        self.addLogtoPsautoDB(username)
        return

class TestResult:
    def __init__(self, name, nTestPlanned, id):
        self.__doc = minidom.Document()
        self.__testNode = self.__doc.createElement("Test")
        self.__testNode.setAttribute("name", name)
        self.__testNode.setAttribute("nTestPlanned", nTestPlanned)
        self.__testNode.setAttribute("id", id)
        
        self.__TestResultNode = self.__doc.createElement("TestResult")
        self.__testNode.appendChild(self.__TestResultNode)
        
        self.__TestOutPutNode = self.__doc.createElement("TestOutput")
        self.__TestResultNode.appendChild(self.__TestOutPutNode)
        
        self.__DetailsNode = self.__doc.createElement("Details")
        self.__TestResultNode.appendChild(self.__DetailsNode)
        return
    
    def setPassed(self, value):
        passNode = self.__doc.createElement("Passed")
        passNode.setAttribute("value", value)
        self.__TestResultNode.appendChild(passNode)
        return
    
    def setState(self, value):
        Node = self.__doc.createElement("State")
        Node.setAttribute("value", value)
        self.__TestResultNode.appendChild(Node)
        return
    
    def setExecutionTime(self, value):
        node = self.__doc.createElement("ExecutionTime")
        node.appendChild(self.__doc.createTextNode(str(value)))
        self.__TestResultNode.appendChild(node)
        return
    
    def setTestOutputMetadata(self, name, value):
        node = self.__doc.createElement("Metadata")
        node.setAttribute("name", name)
        node.setAttribute("value", value)
        self.__TestOutPutNode.appendChild(node)        
        return
    
    def setDetails(self, value):
        node = self.__doc.createTextNode(value)
        self.__DetailsNode.appendChild(node)
        return
    
    def setStartandEndTime(self, start, end):
        startNode = self.__doc.createElement("StartTime")
        startNode.appendChild(self.__doc.createTextNode(start))
        self.__TestResultNode.appendChild(startNode)
        
        endNode = self.__doc.createElement("EndTime")
        endNode.appendChild(self.__doc.createTextNode(end))
        self.__TestResultNode.appendChild(endNode)
        return
    
    def toXML(self):        
        return self.__testNode.toprettyxml()
    
    def getNode(self):
        return self.__testNode



if __name__ == "__main__":
    log = PSFLog()
    log.addOwner("alonao", "NotifyErrorOnly")
    log.addOwner("alonao", "NotifyWhenDone")
    log.setBuildVersion("20090608.m.100")
    log.setStatus("AUTOMATION_COMPLETE")
    log.setSUT("Adobe Bridge", "4.0.0", "Windows", "en_US", "Release")
    log.setTestEnvironment("br-perf-win", "Windows XP 5.1 Service Pack 3", "en_US")
    
    tr = TestResult("Performance.Thumbnails(UI).PSD", "1", "1234")
    tr.setDetails("details")
    tr.setExecutionTime(8000)
    tr.setStartandEndTime("2009-06-08T11:27:20", "2009-06-08T11:27:20")
    tr.setPassed("true")
    tr.setState("PASS")
    tr.setTestOutputMetadata("ScriptDate", "2009-06-08T02:12:28")
    tr.setTestOutputMetadata("MemoryIncreased", "0")
    tr.setTestOutputMetadata("DiskSpaceUsed", "0")
    tr.setTestOutputMetadata("GenericOutputInteger", "0")
    tr.setTestOutputMetadata("GenericOutputFloat", "0.0")
    
    log.addTestResult(tr)
    
    tr1 = TestResult("Performance.Thumbnails(UI).DNG", "1", "1234")
    tr1.setDetails("details")
    tr1.setExecutionTime(8000)
    tr1.setStartandEndTime("2009-06-08T11:27:20", "2009-06-08T11:27:20")
    tr1.setPassed("true")
    tr1.setState("PASS")
    tr1.setTestOutputMetadata("ScriptDate", "2009-06-08T02:12:28")
    tr1.setTestOutputMetadata("MemoryIncreased", "0")
    tr1.setTestOutputMetadata("DiskSpaceUsed", "0")
    tr1.setTestOutputMetadata("GenericOutputInteger", "0")
    tr1.setTestOutputMetadata("GenericOutputFloat", "0.0")
    log.addTestResult(tr1)
    
    print log.toXML()
    timeStamp = datetime.datetime.now().strftime('%Y%m%d_%H%M')
    fullname = os.path.expanduser('~\\QA\\br-perf-win' + timeStamp + '.xml')
    log.sendToPSLuna("alonao", fullname)
#    log.localFilename = "br-perf-win20090608_2045.xml"
#    log.addLogtoPsautoDB("alonao")
    