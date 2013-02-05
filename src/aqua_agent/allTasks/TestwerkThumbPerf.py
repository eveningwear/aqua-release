"""

    TestwerkThumbPerf.py
    
    This task is just for Testwerk Thumb Perf using
    
    Written by: Jacky Li (yxli@adobe.com)

"""
from allTasks.baseTask import Task
import os
import os.path
import re
import subprocess
import sys
import time
from xml.dom.minidom import Document
import csv
from PSFLog import PSFLog, TestResult
import datetime

class childTask(Task):
    
    def __init__(self, type, priority):
        if sys.platform == "win32":
            self.testwerkRootPath = 'D:\\p4\\releases\\tools\\acidtest\\testwerk\\'
        else:
            self.testwerkRootPath = '/Volumes/Data/testwerk/'   
                        
        super(childTask, self).__init__(type, priority)
        return
    
    def runMac(self):
        return
    
    def runWin(self):
        return
    
    def run(self):
        print '-------------TestwerkThumbPerf run'
        self.isSendToPsluna = True
        self.targetMachine = self.worker.dbutil.getMachineByMacAddress(self.parameter['address'])
        
        if self.targetMachine==None:
            return
         
        self.targetIpAddress = self.targetMachine[0]
        
        self.targetOsType = self.targetMachine[1]
        
        self.testSuitesStr = self.parameter['caseType']      
        
        #write config for testwerk
        self.writeConfig()
        
        self.logger.info('Will kick off testwerk thumb perf test for the machine(%s %s)' % (self.targetIpAddress, self.targetOsType))
        #generate the job file
        self.generateJob(self.parameter['caseType'])
        
        # launch testwerk
        if sys.platform == "win32":
            launch = os.path.join(self.testwerkRootPath, "launchtestwerk.bat")
            launch2 = launch.replace('\\', '\\\\', 500)

            # Run testwerk
            subprocess.Popen(launch2)

        else:
            launch = os.path.join(self.testwerkRootPath, "launchtestwerk.sh")
            cmd = ('open ' + launch)

            # Run testwerk
            os.popen(cmd).close()

        # Look for the job 'done' file to quit Testwerk
#        (path, p) = os.path.split(self._scriptitem.path)
        (base, ext) = os.path.splitext('manualPerformance.job')
        new = "%s.done" % (base)
        new2 = os.path.join(self.testwerkRootPath, 'jobs', new)

        runout = 1    
        timeout = 100000
        while timeout > 0:
            time.sleep(1)
            if os.path.exists(new2):
                runout = 0
                timeout = 0
                pid = self.close()
                self.killByPID(pid)
                self.logger.info('quit testwerk')

            else:
                timeout -= 1

        # If timed out force quit.
        if runout == 1:        
            print 'Test might not have finished, timed out'                
            pid = self.close()
            self.killByPID(pid)
             
        # Clean up jobs
        jobsfolder = os.path.join(self.testwerkRootPath, 'jobs')
        self.cleanup(jobsfolder) 
        self.logger.info('clean jobs and finish perf testing')
        
        # parse result folder
        self.extractToCSV()
        self.logger.info('----finish extracting form result files to result.csv file:')
        # send email report
        self.sendEmail()
        self.logger.info('---finish sending email report')
        # send result to Psluna
        if self.isSendToPsluna:
            self.sendToPsluna()
            self.logger.info('---finish sending result to Psluna')
        
        super(childTask, self).run()
        return
    
    def close(self):

#            osversion = osver.getOSVer()

            procID = None

            pidlist = []

            exefile = 'java'

            

            if sys.platform == "win32":

#                if osversion >= osver.WINXP:

                    cmd = "tasklist /FO CSV /NH /FI \"IMAGENAME eq java.exe\""

                    cmdobj = os.popen(cmd)

                    for line in cmdobj:

                        if line.startswith("INFO"):

                            cmdobj.close()

                            return None

                        elif line.startswith("\""):

                           infolist = line.rstrip().split(",")

                           pidlist.append(int(infolist[1].strip("\"")))

                    cmdobj.close()





            elif sys.platform == "darwin":

                cmd = "ps -cx"

                cmdobj = os.popen(cmd)

                for line in cmdobj:

                    infolist = line.strip().split()

                    if infolist[0].isdigit() and exefile in infolist:

                        # the pid is a number, and "Bridge" is the name

                        # of the command.

                        pidlist.append(int(infolist[0]))



            else:

                  return ()



            if procID:

                # only return the procID or empty list

                if procID in pidlist:

                    return tuple((procID,))

                else:

                    return ()

            else:

                return tuple(pidlist)





    def killByPID(self, pid):



            if sys.platform == "win32":

#                osversion = osver.getOSVer()
#
#                if osversion >= osver.WINXP:

                    cmd = "taskkill /F /PID %s /T" % (pid)

#                elif osversion >= osver.WIN2K:
#
#                    cmd = "kill %s" % (pid)

            elif sys.platform == "darwin":
                for p in pid:
                    cmd = "kill -9 %d" % (p)

            else:

                return None



            os.popen(cmd).close()

            return 0
    ''' generate the build information file'''
    def writeConfig(self):                
        appBuild = self.parameter['appBuild']
        #construct result folder name
#        timeStamp = datetime.datetime.strftime()(datetime.datetime.now(), '%Y%m%d.%H%M')
        timeStamp = datetime.datetime.now().strftime('%Y%m%d.%H%M')
        self.resultFolderName = 'perf-%s-%s-%s' % (appBuild, self.targetOsType, timeStamp)
        self.resultPath = os.path.expanduser(os.path.join('~', self.resultFolderName))
        
        text = 'appVersion = %s' % self.parameter['appVersion']
        text += '\nappBuild = %s' % appBuild
        text += '\ncaseType = %s' % self.parameter['caseType']
        text += '\nplatform = %s' % self.targetOsType
        text += '\ntestType = %s' % self.parameter['testType']
        text += '\nresultFolderName = %s' % self.resultFolderName        
        
        configFile = open( os.path.join(self.testwerkRootPath, 'scripts', 'performance3', 'config.properties'), 'w')
        configFile.write(text)
        configFile.close()
        return

    ''' generate the testwerk job file'''
    def generateJob(self, testSuitesStr):
        pramMap = {'launch': 'performance3.Launch.class',
                    'thum': 'performance3.ThumbnailPerformance.class',
                    'mem': 'performance3.MemoryUsageNew.class'}
        
        filePath = os.path.join(self.testwerkRootPath, 'jobs', 'manualPerformance.job')
        file = open(filePath, 'w')
        
        strs = testSuitesStr.split(',')
        doc = Document()
        root = doc.createElement('job')
        doc.appendChild(root)
        
        for str in strs:            
            self.logger.info('----------add %s to job file' % str)
            script = doc.createElement('script')
            if not pramMap.has_key(str):
                continue
            text = doc.createTextNode(pramMap[str])
            script.appendChild(text)
            root.appendChild(script)
        
        lan = doc.createElement('language')
        lan.appendChild(doc.createTextNode('Default'))
        root.appendChild(lan)
        
        sut = doc.createElement('sut')
        ip = doc.createElement('ip')
        sut.appendChild(ip)
        ip.appendChild(doc.createTextNode(self.targetIpAddress))
        root.appendChild(sut)
        
#        doc.writexml(file, encoding='utf-8')
        
        file.write(root.toprettyxml())
        file.close()
        return
    
    def cleanup(self, jobsfolder):

       """

          Do any cleanup that might be necessary

       """

       # Clean Job folder

       #jobsfolder = os.path.join(cwd, "testwerk\jobs"
       if os.path.exists( jobsfolder ):

                for root, dirs, files in os.walk(jobsfolder, topdown=False):

                    for name in files:

                        fullPath = os.path.join(root, name)

                        try:

                            os.remove(fullPath)

                        except:

                            print sys.exc_type, sys.exc_value

                            print "WARNING error removing: " + fullPath



        

       return 0

   
    def sendToPsluna(self):
        ps = TWResultParser(self.resultPath, self.parameter['appBuild'], self.targetOsType, self.logger)
        if "thum" in self.testSuitesStr:
            ps.extractThumbnails(os.path.join(self.testwerkRootPath, "labels.csv"))
        
        if "launch" in self.testSuitesStr:
            ps.extractLaunch()
            
        ps.sendToPSLuna()
        
#        psflogFilename = os.path.join(self.resultPath, self.resultFolderName + ".xml")
#        self.psfLog.sendToPSLuna("chxyang", psflogFilename)
        return
    
    def extractToCSV(self):
        ps = TWResultParser(self.resultPath, self.parameter['appBuild'], self.targetOsType, self.logger)
        ps.extractToCSV(os.path.join(self.testwerkRootPath, 'labels.csv'))
        return
                      
    def sendEmail(self):
        from email.MIMEMultipart import MIMEMultipart
        from email.MIMEBase import MIMEBase
        from email.MIMEText import MIMEText
        from email.Utils import COMMASPACE, formatdate
        from email import Encoders
        import smtplib
        from smtplib import SMTP
        
        self.logger.info('Start sending email')
        server= 'mailsj-v1.corp.adobe.com'
        files = []
        files.append(os.path.join(self.resultPath, "result.csv"))
        files.append(os.path.join(self.resultPath, 'Launch.txt'))       

#        assert type(send_to)==list
#        assert type(files)==list

        send_from = 'chxyang@adobe.com'
        send_to = ["chxyang@adobe.com","alonao@adobe.com"]       
        msg = MIMEMultipart()
        msg['From'] = send_from
        msg['To'] = COMMASPACE.join(send_to)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = 'Bridge Perf Test Results: ' + self.resultFolderName

        strBody = 'Ran following test cases:\n' + self.parameter['caseType']
        msg.attach( MIMEText(strBody) )

        for f in files:
            if not os.path.exists(f):
                continue
            part = MIMEBase('application', "octet-stream")
            part.set_payload( open(f,"rb").read() )
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
            msg.attach(part)
        smtp = smtplib.SMTP(server)
        smtp.sendmail(send_from, send_to, msg.as_string())
        smtp.close()
        return


class TWResultParser:
    def __init__(self, TWResultPath, buildnumber, platform, logger):
        self.__twResultPath = TWResultPath
        self.__logger = logger
        # init PSF log
        self.__psfLog = PSFLog(logger)
        self.__psfLog.addOwner("chxyang", "NotifyErrorOnly")
        self.__psfLog.addOwner("chxyang", "NotifyWhenDone")
        self.__psfLog.setBuildVersion(buildnumber)
        self.__psfLog.setStatus("AUTOMATION_COMPLETE")
        if platform.lower() == "win":            
            self.__psfLog.setSUT("Adobe Bridge", "4.0.0", "Windows", "en_US", "Release")
            self.__psfLog.setTestEnvironment("br-perf-win", "Windows XP 5.1 Service Pack 3", "en_US")
        else:
            self.__psfLog.setSUT("Adobe Bridge", "4.0.0", "Macintosh", "en_US", "Release")
            self.__psfLog.setTestEnvironment("br-perf-mac", "Macintosh OS 10.5.6", "en_US")
            
        return
    
    def extractThumbnails(self, labelsFilePath):
        import csv         
        resultFiles = os.listdir(self.__twResultPath)
        
        self.nameMap = {}
        for file in resultFiles:
            if os.path.isfile(os.path.join(self.__twResultPath, file)):
                name = file
                self.nameMap[name.replace('_', '').lower().replace('.txt', '')] = name
        
        
        labsFile = open(labelsFilePath, 'rb')
        reader = csv.reader(labsFile)        
        labs = reader.next()        
        
        for l in labs:
            av = str(self.__getValue(l))
            fst = str(self.__getFirstValue(l))                        
            # Test case name should be "draft_model_first"
            # add result to PSF log 
            self.__addResulttoPSFLog(self.__createThubnailTestName(l), int(float(av)*1000), av != "0")
            self.__addResulttoPSFLog(self.__createThubnailTestName(l) + "_first", int(float(fst)*1000), fst != "0")
       
             
        labsFile.close()        
        return
    
    def extractLaunch(self):
        launchResultPath = os.path.join(self.__twResultPath, "Launch.txt")
        coldlaunch = self.__getTimeFromTWResult(launchResultPath, "Average Cold Launch Time")
        warmlaunch = self.__getTimeFromTWResult(launchResultPath, "Average Warm Launch Time")
        self.__addResulttoPSFLog("Performance.Standalone Cold Launch.Standalone Cold Launch", int(coldlaunch *1000), 0 != coldlaunch)
        self.__addResulttoPSFLog("Performance.Standalone Warm Launch.Standalone Warm Launch", int(warmlaunch * 1000), 0 != warmlaunch)
        return
    
    def sendToPSLuna(self):
        xmlName = os.path.basename(self.__twResultPath)
        fullFilename = os.path.join(self.__twResultPath, xmlName + ".xml")
        self.__psfLog.sendToPSLuna("chxyang", fullFilename)
        return
    
    def WriteToXML(self):
        xmlName = os.path.basename(self.__twResultPath)
        self.__psfLog.writeResult(os.path.join(self.__twResultPath, xmlName + ".xml"))
        return
    
    def __getFirstValue(self, lab):
        name = '%s200first' % lab.replace('_', '').lower()
        name = name.replace(" ", "")
        if self.nameMap.has_key(name):
            fileName = self.nameMap[name];
        else:
            self.__logger.info("Did not find thumbnail result for: " + name)
            return 0        
        rf = os.path.join(self.__twResultPath, fileName)
        return self.__getResult(rf)
        
    def __getValue(self, lab):
        name = '%s200' % lab.replace('_', '').lower()
        name = name.replace(' ', '')
        if self.nameMap.has_key(name):
            filename = self.nameMap[name.replace('_', '')]
        else:
            self.__logger.info("Did not find thumbnail result for: " + name)
            return 0
        rf = os.path.join(self.__twResultPath, filename)
        return self.__getResult(rf)
    
    def __getResult(self, filePath):
        time = self.__getTimeFromTWResult(filePath, 'time')
        return time
    
    def __getTimeFromTWResult(self, filePath, id):
        time = 0
        try:
            file = open(filePath, 'r')
            for line in file.readlines():
                if id in line:
                    strs = line.split('\t')
                    timestr = strs[3]
                    timestr = timestr.strip().replace('\n', '')
                    time = float(timestr)
                    break
                
            file.close()             
        except Exception, e:
            # do nothing, just return 0
            self.__logger.error("Parse with error for:" + filePath)
            self.__logger.error(e)
            
        return time
    
    def __addResulttoPSFLog(self, caseName, time, isPassed):
        # there is a space in "Thumbnails (UI)", this is consistent with psluna and test id need to set to 0
        tr = TestResult(caseName, "1", "0")
        tr.setDetails("UI test result")
        tr.setExecutionTime(time)
        timeStamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        tr.setStartandEndTime(timeStamp, timeStamp)
        if isPassed:
            tr.setPassed("true")
            tr.setState("PASS")
        else:
            tr.setPassed("False")
            tr.setState("FAILURE")
            
        tr.setTestOutputMetadata("ScriptDate", timeStamp)
        tr.setTestOutputMetadata("MemoryIncreased", "0")
        tr.setTestOutputMetadata("DiskSpaceUsed", "0")
        tr.setTestOutputMetadata("GenericOutputInteger", "0")
        tr.setTestOutputMetadata("GenericOutputFloat", "0.0")
        
        self.__psfLog.addTestResult(tr)
        return
    
    def __createThubnailTestName(self, label):
        if "HQ" in label:
            tname = "proof_" + label.replace("HQ", "").replace(" ", "") 
        else:
            tname = "draft_" + label.replace(" ", "")
        
        return "Performance.Thumbnails (UI)." + tname
    
    def extractToCSV(self, labelsFilePath):
        import csv         
        resultFiles = os.listdir(self.__twResultPath)
        
        self.nameMap = {}
        for file in resultFiles:
            if os.path.isfile(os.path.join(self.__twResultPath, file)):
                name = file
                self.nameMap[name.replace('_', '').lower().replace('.txt', '')] = name
        
        
        labsFile = open(labelsFilePath, 'rb')
        reader = csv.reader(labsFile)        
        labs = reader.next()
        
        average = []
        first = []
        for l in labs:
            av = str(self.__getValue(l))
            fst = str(self.__getFirstValue(l))
            average.append(av)
            first.append(fst)        
        
        resultCSV = os.path.join(self.__twResultPath, 'result.csv')
        dest = open(resultCSV, 'w')
        dr = csv.writer(dest)
        dr.writerow(labs)
        average.append('average')
        dr.writerow(average)
        first.append('first')
        dr.writerow(first)
        
        labsFile.close()
        dest.close()
        return

          
if __name__ == "__main__":
#    print float('123.45')
#    print int(123.45)
    import logging
    import logging.config
    logging.config.fileConfig('C:\\Users\\tester\\Desktop\\!!perf-183-mac-20090610.0305!\\log.config')
    logger = logging.getLogger()
#    task = childTask('TestThumbPerf', 100)
#    task.resultPath = 'C:\\Users\\tester\\Desktop\\!!perf-183-mac-20090610.0305!'
##    task.testwerkRootPath = "D:\\p4\\releases\\tools\\acidtest\\testwerk"
#    task.resultCSV = 'C:\\Documents and Settings\\tester\\BridgeQETestResults-AIM2-win\\latest_Canon-5DMarkII-21-HQ_First.csv'
#    task.resultFolderName = 'psflog'
#    task.psfLog = PSFLog(logger)
#    task.psfLog.addOwner("chxyang", "NotifyErrorOnly")
#    task.psfLog.addOwner("chxyang", "NotifyWhenDone")
#    task.psfLog.setBuildVersion('2008.m.88')
#    task.psfLog.setStatus("AUTOMATION_COMPLETE")
#    task.psfLog.setSUT("Adobe Bridge", "4.0.0", "Windows", "en_US", "Release")
#    task.psfLog.setTestEnvironment("br-perf-win", "Windows XP 5.1 Service Pack 3", "en_US")
#        
#    task.extractToCSV()
#    task.extractLaunchResult()
#    task.sendToPsluna()
    
    t2p = TWResultParser('C:\\Users\\tester\\Desktop\\!!perf-183-mac-20090610.0305!', '2008.m.88', 'win', logger)
    t2p.extractToCSV('D:\\p4\\releases\\tools\\acidtest\\testwerk\\labels.csv')
    t2p.extractThumbnails('D:\\p4\\releases\\tools\\acidtest\\testwerk\\labels.csv')
    t2p.extractLaunch()
    t2p.WriteToXML()
#    t2p.sendToPSLuna()
#    task.sendEmail()
#    task.extractToCSV()
