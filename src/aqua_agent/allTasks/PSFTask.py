"""

    PSFTask.py
    
    Written by: Jacky Li (yxli@adobe.com)
    Contributed by: ChunTang Pan (chtpan@adobe.com)

"""
import os,zipfile,shutil,re,time

from allTasks.baseTask import Task
from allTasks.PSFCaseAreaParser import PSFCaseAreaParser
import globalProperty

class childTask(Task):    
    
    def __init__(self, type, priority):
        super(childTask, self).__init__(type, priority)
        
        if globalProperty.isMachineOutOfChina():
            self.PSFLocation = self._dbutil.getAppInfo("psf_path_us")
            self.testFilesLocation = self._dbutil.getAppInfo("psf_test_file_us")
        else:
            self.PSFLocation = self._dbutil.getAppInfo("psf_path")
            self.testFilesLocation = self._dbutil.getAppInfo("psf_test_file")
        
        self.PSFRepository = os.path.join(os.getcwd(), 'PSFLocal')
        
        cwd = os.getcwd()
        if os.name == 'posix':
            self.PSFLocalHome = cwd.split("QMSClient")[0]
        elif os.name == 'nt':
            self.PSFLocalHome = cwd[0:3]
        
        self.PSFLogBackUpDir = os.path.join(os.getcwd(), 'PSFLogBak')        
        
        self.PSFConfig = "psConfig.js"
        
        self.launcherFileName = "MyPsfLauncher"
        
        self.launcherFilePath = None
        
        self.buildNum = ""
        
        self.localTestFileLocation = ""
        
        self.localConfigFileLocation = ""
        
        self.downloadFileFlag = "1"
        
        self.setupFileFlag = "Yes"
        
        self.userHome = globalProperty.getUserHome()
        
        if os.name == 'posix':
            self.platform = "osx10"
            
            #Need to add this to enable access for assistive devices
            self.runCommand('sudo touch /private/var/db/.AccessibilityAPIEnabled')
        if os.name == 'nt':
            self.platform = "win32" 
        
        return
    
    def run(self):
        self.logger.debug('PSFTask run')
                 
        from PhotoshopInstall import childTask
        psInstall = childTask('psInstall')
        
        if 'ProductVersion' in self.parameter:
            self.productVersion = self.parameter['ProductVersion']
        else:
            self.productVersion = 'Photoshop'
        
        if not psInstall.isInstallPS(self.parameter['ProductVersion']):
            self.logger.warning("Cannot Find Photoshop Installed")
            return
        elif 'checkPlugIn' in self.parameter and self.parameter['checkPlugIn']=='Yes'  and not psInstall.isInstallCRCPlugIn(self.parameter['ProductVersion']):
            #self.logger.warning("Cannot Find CRC Plugin Installed")
            #return
            psInstall.addPara('appVer', self.productVersion)
            psInstall.installSpecialPlugIn()
        
        if 'zstring' in self.parameter and self.parameter['zstring'].strip() == "true":  
            psInstall.addPara('zstring', "true")
        psInstall.makeBackDoorFile(self.parameter['ProductVersion'])
        
        if 'PSFHome' in self.parameter:
            self.psfHome = os.path.join(self.parameter['PSFHome'], 'PSF')
        else:
            self.psfHome = os.path.join(self.PSFLocalHome, 'PSF')
        
        self.psfLogHome = os.path.join(self.psfHome, 'logs')
            
        self.psfScriptsHome = os.path.join(self.psfHome, 'scripts')
            
        if 'LocalConfigFilesLocation' in self.parameter:
            self.localConfigFileLocation = self.parameter['LocalConfigFilesLocation']
        
        if 'LocalTestFilesLocation' in self.parameter:
            self.localTestFileLocation = self.parameter['LocalTestFilesLocation']
            
        if os.path.exists(self.psfHome):
            self.PSFLocation = self._dbutil.getAppInfo("psf_path_us")
        
        if 'downloadFileFlag' in self.parameter:
            self.downloadFileFlag = self.parameter['downloadFileFlag']
        
        if 'SetupFile' in self.parameter:
            self.setupFileFlag = self.parameter['SetupFile']
        
        self.__getPSF()
            
        if 'copyAppPanel' in self.parameter and self.parameter['copyAppPanel']=='Yes' or not 'copyAppPanel' in self.parameter:
            psInstall.prepareAppPanel("%s/testfiles/FlashPanels/AppPanels" % self.psfHome, self.parameter['ProductVersion'])
            
        if os.name == 'nt':
            self._removeFile()
        
        if 'TestStudioControl' in self.parameter and self.parameter['TestStudioControl'] == 'Yes':
            psfController = self.parameter['PSFController']
            try:
                caseXML = self._dbutil.getValidTestCasesFromTS("Photoshop", psfController)
                self.updateCaseByTestStudioResult(caseXML)
            except Exception, e:
                self.logger.debug(e)

        if 'runPSF' in self.parameter and self.parameter['runPSF'] == 'No':
            return
        
        self.__prepareLauncher()
        self.__cleanPSFLog()
        
        if self.launcherFilePath==None:
            raise Exception("Launcher File is created failed")
        
        self.logger.debug("PSF automation test is kicked off")
        self.runSimpleCommand(self.launcherFilePath)
        
        #Back Up Log
        self.__backupPSFLog()
        
        if 'sendReport_ASC' in self.parameter and self.parameter['sendReport_ASC'] == 'Yes':
            self._sendReport()
        elif 'SendReport_ASC' in self.parameter and self.parameter['SendReport_ASC'] == 'Yes':
            self._sendReport()

        
    def __getPSF(self):
        if 'GetLatestPSF' in self.parameter and self.parameter['GetLatestPSF']=='true' or not os.path.exists(self.psfHome):
            #Prepare the core test case file
            self.logger.debug('Start preparing for PSF core file')
            self.PSFFile = self._downloadFile(self.PSFLocation, self.PSFRepository)
            #self._unzipfile(self.PSFFile, self.userHome)
            #psfHomeParent = os.path.dirname(self.psfHome)
            if not os.path.exists(self.psfHome):
                os.makedirs(self.psfHome)
                
            if os.path.exists(self.PSFFile):
                self._unzipfileBy7zip(self.PSFFile, self.psfHome)
                os.remove(self.PSFFile)
        
        #Prepare the test files
        self.logger.debug('Start preparing for PSF test file')
        
        if self.testFilesLocation!="" and self.localTestFileLocation=="" and self.setupFileFlag=="Yes":
            if re.match(".*\.zip$", self.testFilesLocation.lower()):
                self.TestFileList = [self._downloadFile(self.testFilesLocation, self.PSFRepository)]
            else:
                self.TestFileList = self._downloadFolder(self.testFilesLocation, self.PSFRepository)
            for testFile in self.TestFileList:
                #self._unzipfile(TestFile, self.psfHome + "/testfiles/")
                #self._unzipfileBy7zip(testFile, self.psfHome + "/testfiles/" + os.path.basename(testFile).split('.')[0] + "/")
                self._unzipfileBy7zip(testFile, self.psfHome + "/testfiles/")
            
        #Prepare the config file
        self.logger.debug('Start preparing for PSF config file')
        #self._getPSFConfig()
        
    def _getPSFConfig(self):
        psfConfigFile = os.path.join(self.psfHome, self.PSFConfig)
        psfConfigObj = open(psfConfigFile, "w")
        
        inputStr = 'var rootPath = "%s";\n' %self.psfHome
        inputStr += 'var scriptsPath = rootPath + "/scripts"\n'
        
        if self.localConfigFileLocation=="":
            inputStr += 'var datFilesPath = rootPath + "/config"\n'
        else:
            inputStr += 'var datFilesPath = "%s"\n' % self.localConfigFileLocation
        
        if self.localTestFileLocation=="":
            inputStr += 'var testFilesPath = rootPath + "/testfiles"\n'
        else:
            inputStr += 'var testFilesPath = "%s"\n' % self.localTestFileLocation
        inputStr += 'var logsPath = rootPath + "/logs"\n'
        psfConfigObj.write(inputStr)
        
        psfConfigObj.close()
            
            
    def _downloadFile(self, fileLocation, fileRepository):
        fullPath = fileLocation[6:]
        parts = fullPath.split('/', 1)
            
        (host, location) = parts
        from FTPTask import childTask
        task = childTask('task')
            
        task.addPara('Host', host)
        task.addPara('User', self._commonDomain + "\\" +self._commonUser )
        task.addPara('Passwd', self._commonPassword)
            
        if not location.startswith('/'):
            location = '/' + location
        
        task.addPara('Repository', fileRepository) 
        task.addPara('FilePath', location)
        task.run()
        return task.getDownloadList()[0]
    
    def _downloadFolder(self, fileLocation, fileRepository):
        fullPath = fileLocation[6:]
        parts = fullPath.split('/', 1)
            
        (host, location) = parts
        from FTPTask import childTask
        task = childTask('task')
            
        task.addPara('Host', host)
        task.addPara('User', self._commonDomain + "\\" +self._commonUser)
        task.addPara('Passwd', self._commonPassword)
            
        if not location.startswith('/'):
            location = '/' + location
        
        task.addPara('Repository', fileRepository) 
        task.addPara('FolderPath', location)
        task.run()
        return task.getDownloadList()
    
    def _unzipfile(self, zipfilename, des):
        try:
            self.logger.debug('UNZIP %s to %s', zipfilename, des)
            zf = zipfile.ZipFile(zipfilename)
            
            #first make a folder with the zipfilename
            tmpfolder = os.path.join(des, os.path.splitext(os.path.basename(zipfilename))[0])
            if( not os.path.exists(tmpfolder)):
                os.mkdir(tmpfolder)
                
            # extract files to directory structure
            for name in enumerate(zf.namelist()):
                if name[1].endswith('/'):
                    if( not os.path.exists(os.path.join(tmpfolder,name[1]))):
                        os.makedirs(os.path.join(tmpfolder,name[1]))
                else:
                    tmpFile = os.path.normpath(os.path.join(tmpfolder, name[1]))
                    tmpFileFolder = os.path.dirname(tmpFile)
                    if not os.path.exists(tmpFileFolder):
                        os.makedirs(tmpFileFolder)
                    outfile = open(tmpFile, 'wb')
                    outfile.write(zf.read(name[1]))
                    outfile.flush()
                    outfile.close()
        except Exception, e:
            self.logger.debug('UNZIP %s to %s Failed', zipfilename, des)
            
    def _unzipfileBy7zip(self, zipfilename, des):
        try:
            self.logger.debug('UNZIP %s to %s', zipfilename, des)
            
            if (os.path.splitext(zipfilename)[1] != '.zip'):
                self.logger.debug(zipfilename + ' is not a valid zip file')
                return
            
            #first make a folder with the zipfilename
            #tmpfolder = os.path.join(des, os.path.splitext(os.path.basename(zipfilename))[0])
            if( not os.path.exists(des)):
                os.mkdir(des)
            cmd = ''
            if os.name == 'posix':
                cmdGrantAccess = 'sudo chmod +x ' + self.getToolsDir() + '/7zip/7za'
                self.logger.debug('Start to Grant Access for 7zip : ' + cmdGrantAccess)
                os.system(cmdGrantAccess)
                cmd = self.getToolsDir() + '/7zip/7za'
            if os.name == 'nt':
                cmd = self.getToolsDir() + '/7zip/7za.exe'
                
            cmd = cmd + '  x ' + zipfilename + ' -o' + '\"' + des + '\" -ry'
            self.logger.debug('Start to extract with 7zip : ' + cmd)
            os.system(cmd)
                
        except Exception, e:
            self.logger.debug('UNZIP %s to %s Failed', zipfilename, des)
           
    def runSimpleCommand(self, cmd):
        cmdStr = '\"' + cmd + '\"'
        self.logger.debug(cmdStr)
        os.system(cmdStr)
    
    def __prepareLauncher(self):
        if 'buildNum' in self.parameter and self.parameter['buildNum'] != None:
            self.buildNum = self.parameter['buildNum']
        else:
            from AppInstall import childTask
            task = childTask('appInstall')
            task.addPara('appName', 'Photoshop')
            task.addPara('appVer', self.parameter['ProductVersion'])
            task.addPara('appSubProduct', 'Application')
            self.buildNum = task._getInstalledBuildNum()
            
        if self.buildNum!="" and self.buildNum!=None:
            pass
        elif 'molecule' in self.parameter:
            moleculeReStr = "\d{8}\." + self.parameter['molecule'] + "\.\d{1,}"
            from CodexTask import childTask
            task = childTask('codexTask')
            self.buildNum = "unknown"
            builds = task.getBuilds(
                                    'Photoshop',
                                    self.parameter['ProductVersion'],
                                    "Molecule",
                                    "Release", #CompileTarget
                                    self.platform,
                                    globalProperty.getSysInfo().locale,
                                    'Build Failed')
            if builds==None:
                return None
                
            latestBuildLocation = None
            for build in builds:
                if re.match(moleculeReStr, build._build):
                    latestBuildLocation = build._location['protocol'] + "://" + \
                                          build._location['server'] + \
                                          build._location['path']
                
                    self.buildNum = build._build
                    break
        else:
            if globalProperty.isMachineOutOfChina():
                #Support the machine out of China, will download directly
                from CodexTask import childTask
                task = childTask('codexTask')
                latestBuild = task.getBuild(
                                      'Photoshop',
                                      self.parameter['ProductVersion'],
                                      "Release", #CompileTarget
                                      self.platform,
                                      globalProperty.getSysInfo().locale,
                                      'Build Failed')
                if latestBuild==None:
                    return None
                
                self.buildNum = latestBuild._build
            else:
                self.buildNum = globalProperty.getLatestBuildNum('Photoshop',
                                                                 self.parameter['ProductVersion'],
                                                                 self.platform,
                                                                 globalProperty.getSysInfo().locale,
                                                                 'Build Failed',
                                                                 'Application')
        if 'sendReport' in self.parameter and self.parameter['sendReport'] != None:
            self.sendReport = self.parameter['sendReport']
        else:
            self.sendReport = 'No'
        
        user = globalProperty.getUser()
        if user==None:
            defaultTo = 'yxli@adobe.com'
        else:
            defaultTo = '%s@adobe.com' % user
            
        if 'sendReportTo' in self.parameter and self.parameter['sendReportTo'] != None:
            self.sendReportTo = self.parameter['sendReportTo']
        else:
            self.sendReportTo = defaultTo
        
        if 'specifyLocation' in self.parameter and self.parameter['specifyLocation'] != None:
            self.specifyLocation = self.parameter['specifyLocation']
        else:
            self.specifyLocation = ''  
            
        import platform;
        self.hostname_psf = platform.node();
        
        #Due to PSF bug, the version 12.0 must be set as 12.0.0, so add a workaround here
        productVersionTmp = self.parameter['ProductVersion']
        if re.match("^\d{1,2}\.\d{1,3}$", productVersionTmp.lower()):
            productVersionTmp += ".0"
        
        if os.name == 'posix':
            if not (os.path.exists(os.path.join(self.userHome, "Desktop"))):
                os.makedirs(os.path.join(self.userHome, "Desktop"))
            self.launcherFileName += ".sh"
            self.launcherFilePath = os.path.join(self.userHome, "Desktop", self.launcherFileName)
            inputStr = "#!/bin/sh\n"
            inputStr += "chmod +x %s/psf_launcher\n" % self.psfHome
            inputStr += "chmod +x %s/config/utils/TestFilesDownloader\n" % self.psfHome
            inputStr += '%s/psf_launcher "%s" "%s" "%s" "%s" "%s" "%s" "%s" "1" "%s" "1" "" "%s" "" "" "" "" "%s" "%s" "%s" "%s" "%s" "%s"\n' \
                %(self.psfHome, self.parameter['ProductTested'], self.parameter['BuildConfig'], self.buildNum, globalProperty.getSysInfo().locale, globalProperty.getSysInfo().locale, self.parameter['SuiteSelected'], self.parameter['SendResult'], self.hostname_psf, productVersionTmp, self.parameter['PSFController'], self.parameter['LDAPUser'], self.downloadFileFlag, self.specifyLocation, self.sendReport, self.sendReportTo)            
                        
            self.creatFile(self.launcherFilePath, inputStr)
            
            #Add execution
            
            self.runCommand('chmod +x %s' % self.launcherFilePath)
        
        elif os.name == 'nt':
            if not (os.path.exists(os.path.join(self.userHome, "Desktop"))):
                os.makedirs(os.path.join(self.userHome, "Desktop"))
            self.launcherFileName += ".cmd"
            self.launcherFilePath = os.path.join(self.userHome, "Desktop", self.launcherFileName)            
            inputStr = "cd /d %s\n" % self.psfHome
            buildConfig = self.parameter['BuildConfig']
            if re.match('.*_32bt_.*',buildConfig ):
                inputStr += 'Call psf_launcher32.exe '
            else:
                inputStr += 'Call psf_launcher.exe '
            inputStr += '"%s" "%s" "%s" "%s" "%s" "%s" "%s" "1" "%s" "1" "" "%s" "" "" "" "" "%s" "%s" "%s" "%s" "%s" "%s"\n' \
                %(self.parameter['ProductTested'], self.parameter['BuildConfig'], self.buildNum, globalProperty.getSysInfo().locale, globalProperty.getSysInfo().locale, self.parameter['SuiteSelected'], self.parameter['SendResult'], self.hostname_psf, productVersionTmp, self.parameter['PSFController'], self.parameter['LDAPUser'], self.downloadFileFlag, self.specifyLocation, self.sendReport, self.sendReportTo)
            #Following statement should not be called
            #inputStr += "Call cmd"
            self.creatFile(self.launcherFilePath, inputStr)

    def __cleanPSFLog(self):
        try:
            if (os.path.exists(self.psfLogHome)):
                self.logger.info('Clean PSF Log %s' % self.psfLogHome)
                shutil.rmtree(self.psfLogHome)
            os.mkdir(self.psfLogHome)
        except WindowsError, (errno,strerror):
            self.logger.error("catch WindowsError: error(%s): %s" % (errno,strerror))
            
    def __backupPSFLog(self):
        try:
            if not os.path.exists(self.PSFLogBackUpDir):
                os.mkdir(self.PSFLogBackUpDir)
            fileList = os.listdir(self.PSFLogBackUpDir)
            #Only reserve recent 10 records
            if len(fileList)>10:
                fileListD = fileList[0:len(fileList) - 10]
                for fileD in fileListD:
                    curBackUpPath = os.path.join(self.PSFLogBackUpDir, fileD)
                    if os.path.exists(curBackUpPath):
                        shutil.rmtree(curBackUpPath, True)
            if os.path.exists(self.psfLogHome):
                timeFolder = time.strftime("%Y-%m-%d(%H-%M-%S)")
                curBackUpPath = os.path.join(self.PSFLogBackUpDir, timeFolder)
                self.logger.info('Backup PSF Log %s to %s' % (self.psfLogHome, curBackUpPath))
                if os.path.exists(curBackUpPath):
                    shutil.rmtree(curBackUpPath, True)
                shutil.copytree(self.psfLogHome, curBackUpPath, True)          
        except WindowsError, (errno,strerror):
            self.logger.error("catch WindowsError: error(%s): %s" % (errno,strerror))
            
           
    def _sendReport(self):
        #Generate Report
        from PsPSFReporter import childTask
        psfReporter = childTask("PSFReporter", self.priority + 1)
        psfReporter.addPara('PSFHome', self.psfHome)
        if self.parameter.has_key('FeatureOwner'):
            psfReporter.addPara('FeatureOwner', self.parameter['FeatureOwner'])
        else:
            psfReporter.addPara('FeatureOwner', 'Unknown')   
        psfReporter.addPara('ProductVersion', self.productVersion)         
        psfReporter.run()
        reportFile = psfReporter.getHtmlReport()
        
        #Send Report
        from HtmlEmailUtil import childTask
        htmlEmailUtil = childTask('HtmlEmailUtil', self.priority + 2)
        
        if self.parameter.has_key('From'):
            htmlEmailUtil.addPara('From', self.parameter['From'])
        else:
            htmlEmailUtil.addPara('From', 'QMS@adobe.com')
        
        user = globalProperty.getUser()
        if user==None:
            defaultTo = 'yxli@adobe.com'
        else:
            defaultTo = '%s@adobe.com' % user
        
        if self.parameter.has_key('To'):
            htmlEmailUtil.addPara('To', self.parameter['To'])
        else:
            htmlEmailUtil.addPara('To', defaultTo)
        
        if globalProperty.isMachineOutOfChina():
            htmlEmailUtil.addPara('SMTPServer', self._dbutil.getAppInfo('email_server_us'))
        else:
            htmlEmailUtil.addPara('SMTPServer', self._dbutil.getAppInfo('email_server_cn'))
        if self.parameter.has_key('Subject'):
            subject = self.parameter['Subject']
        elif self.parameter.has_key("SuiteSelected"):
            subject = "PSF Report: Photoshop 12.0 Results"
        else:
            subject = "PSF Report: Photoshop 12.0 Results"
        subject = " [%s][%s][%s][%s]%s[%s](%s)" % (self.productVersion, psfReporter.getPassRate(),globalProperty.getSysInfo().locale, globalProperty.getSysInfo().os, subject, self.buildNum, psfReporter.getMachine())
        htmlEmailUtil.addPara('Subject', subject)
        htmlEmailUtil.addPara('ReportFile', reportFile)
        htmlEmailUtil.run()
        
    def updateCaseByTestStudioResult(self, caseData):
        tcTuple = caseData.split("<testcase>")
        for tcStr in tcTuple:
            if not re.search(r'displayid', tcStr):
                continue 
            excutingModeStr = tcStr.split("<globalgeneralattributelist")[1].split("</globalgeneralattributelist>")[0]
            automatedFlag = False
            if re.search(r'Execution Mode', excutingModeStr) and re.search(r'<value>Automated</value>', excutingModeStr):
                automatedFlag = True
            tcIdStr = tcStr.split("<displayid")[1].split("</displayid>")[0]
            tcId = re.sub(r'.*\s*TC_([0-9]+)\s*.*', r'\1', tcIdStr)
            tcStatusStr = tcStr.split("<status")[1].split("</status>")[0]
            tcStatus = re.sub(r'.*<name>([^<]+)</name>.*', r'\1', tcStatusStr)
            automationDataStr = tcStr.split("<automationdata>")[1].split("</automationdata>")[0]
            automationData = re.sub(r'^\s*(.*)\s*$', r'\1', automationDataStr)
            automationData = re.sub(r'^\s*(.*)\s*$', r'\1', automationDataStr)
            lines = automationData.split('||')
            autoDataProperty = {}
            for line in lines:
                if line.find('=') != -1:
                    key, value = line.strip().split("=")
                    autoDataProperty[key] = value
            if 'case_file' in autoDataProperty:
                self.updatePSFCase(tcId, tcStatus, automatedFlag, autoDataProperty['case_file'])
    
    def _searchFile(self, parent, fileName):
        for root, dirs, files in os.walk(parent):
            for filename in files:
                if filename.lower()==fileName.lower():
                    filePath = os.path.join(root, filename)
                    return filePath
        return None
    
    def updatePSFCase(self, tcId, tcStatus, automatedFlag, caseFileName):
        caseFile = self._searchFile(self.psfScriptsHome, caseFileName)
        
        if caseFile==None:
            return
        else:
            try:
                f = open(caseFile, "r")
                caseStr = f.read()
                #print caseStr
                if tcStatus=="Approved" and automatedFlag and re.search(r'\n_,' + tcId + ',' , caseStr):
                    caseStr = re.sub(r'(.*\n)_(,' + tcId + ',.*)', r'\1\2', caseStr)
                    #print caseStr
                    f.close()
                    os.chmod(caseFile, 0666)
                    f = file(caseFile, "w")
                    f.write(caseStr)
                elif (tcStatus!="Approved" or not automatedFlag) and re.search(r'\n,' + tcId + ',' , caseStr):
                    caseStr = re.sub(r'(.*\n)(,' + tcId + ',.*)', r'\1_\2', caseStr)
                    #print caseStr
                    f.close()
                    os.chmod(caseFile, 0666)
                    f = file(caseFile, "w")
                    f.write(caseStr)
            except Exception, e:
                self.logger.error(e)
            finally:
                if f!=None:
                    f.close()
                    os.chmod(caseFile, 0444)
    '''
    This method is to delete screencap.exe, this app file may cause PSF hang  
    '''            
    def _removeFile(self):
        targetFile = os.path.join(self.psfHome, 'config\utils\screencap.exe')
        if os.path.exists(targetFile):
            os.remove(targetFile)
        return None
    
    def prepareLauncher(self):
        self.__prepareLauncher()
        
if __name__ == '__main__':
    task = childTask('xx', 1)
    task.addPara("Subject", "Filter Test Automation Result of Photoshop by QMS")
    #task.addPara("PSFHome", "D:\\localPSF")
    #task.run();
    #task.psfScriptsHome = "D:\\tmp\\test"
    task.addPara("ProductVersion", "13.0")
    task.addPara("molecule", "plct")
    task.addPara("From", "yxli@adobe.com")
    task.addPara("To", "yxli@adobe.com")
    #task._sendReport()
    #caseXML = task._dbutil.getValidTestCasesFromTS("Photoshop", "psfController_PS_filter.csv")
    #task.updateCaseByTestStudioResult(caseXML)
    task.prepareLauncher()
'''
    task.addPara("BuildConfig", "Ext_32bt_OGLOff")
    task.addPara("SuiteSelected", "1,0,0,0,0,0")
    task.addPara("LDAPUser", "yxli")
    task.addPara("ProductTested", "Adobe Photoshop CS5")
    task.addPara("LDAPUser", "yxli")
    task.addPara("ProductVersion", "12.0.0")
    task.addPara("PSFController", "psfController_PS12.csv")
    task.addPara("PSFHome", "D:\\localPSF")
    task.addPara("SendResult", "No")
    task.addPara("SendReport", "Yes")
    task.addPara("From", "yxli@adobe.com")
    task.addPara("To", "yxli@adobe.com")
    #task.run();
    task.run()
'''
    
        
