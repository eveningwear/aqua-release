"""

    SuiteInstall.py
    
    Written by: Jacky Li (yxli@adobe.com)

"""
##################This section is mainly for debug -- Begin #############################        
import sys
import globalProperty
#sys.path.append("C:\Python25\ResTool\Client")
#sys.path.append("/Volumes/10.5-2/Users/tester/Documents/workspace/Client/")
##################This section is mainly for debug -- End #############################

from allTasks.AppInstall import childTask

from xml.dom import minidom
import os, subprocess, zipfile
import shutil
import re
import tarfile
import time
            
class childTask(childTask):
    
    def __init__(self, type, priority = 800):
        super(childTask, self).__init__(type, priority)

        self.exInstallComponents = ["AdobePhotoshop"]
        self.componentProxyFiles = ["\.proxy\.xml"]
        self.installParam = ["install"]
        
        self.compileTarget = ""

    def _installWINAPP(self, appType): 
        self.logger.debug('install application:' + appType)
        #we need find out where the setup.exe file exist.  
        self.installParam = ["install"]
        if self.parameter['installerType'] == 'RAW':
            pass
        else:
            if self.parameter['installerType'] == 'RIBS':
                for installerFileNamePattern in self.installerName:
                    installerFile = self._searchFile(self.downloadFolder, installerFileNamePattern)
                    if installerFile:
                        break
                
                if not installerFile:
                    raise Exception("Installer is not exited in %s" % self.installerName)
                
                for deploymentFileNamePattern in self.installParam:
                    deploymentFileName = "%s-%s.xml" %(deploymentFileNamePattern, self.parameter['appLang'])
                    deploymentFile = self._searchFile(self.downloadFolder, deploymentFileName)
                    if deploymentFile:
                        break
                
                if not deploymentFile:
                    raise Exception("Deployment File is not exited in %s" % self.installParam)
                
                self.logger.info("Found the deployment file %s" % deploymentFile)
                
                deploymentFile = self.__generateDeploymentFile(deploymentFile)
                                
                if not deploymentFile:
                    raise Exception("Deployment File is not exited in %s" % self.installParam)
                    
                cmd = '"%s" --mode=silent --deploymentFile=%s --skipProcessCheck=1' % (installerFile, deploymentFile)
                if 'installDir' in self.parameter and self.parameter['installDir']:
                    self.appendInstallDir(deploymentFile, self.parameter['installDir'])
                    
                self.logger.info(cmd)
                rtv = os.system(cmd)
                if rtv != 0:
                    raise Exception("Installing %s exited abnormally, code: %d" % (appType, rtv))
                
                time.sleep(10)
            elif self.parameter['installerType'] == 'MSI':
                pass
                    
    def _installMACAPP(self, appType):
        self.logger.debug("install mac application %s" % appType)
        self.installParam = ["install"]
        if self.parameter['installerType'] == 'RAW':
            pass
        else:
            if self.parameter['installerType'] == 'RIBS':                
                for dmgPath in self.dmglist:
                    for installerFileNamePattern in self.installerName:
                        installerFile = self._searchFolder(dmgPath, installerFileNamePattern)
                        if installerFile:
                            installerFile = os.path.join(installerFile, 'Contents/MacOS/' + installerFileNamePattern)
                            break
                    
                    if not installerFile:
                        raise Exception("Installer is not exited in %s" % self.installerName)
                    
                    for deploymentFileNamePattern in self.installParam:
                        deploymentFileName = "%s-%s.xml" %(deploymentFileNamePattern, self.parameter['appLang'])
                        deploymentFile = self._searchFile(dmgPath, deploymentFileName)
                        if deploymentFile:
                            break
                        
                    if not deploymentFile:
                        raise Exception("Deployment File is not exited in %s" % self.installParam)
                    
                    deploymentFile = self.__generateDeploymentFile(deploymentFile)
                                    
                    if not deploymentFile:
                        raise Exception("Deployment File is not exited in %s" % self.installParam)
                        
                    cmd = 'sudo "%s" --mode=silent --deploymentFile="%s"' % (installerFile, deploymentFile)
                    if 'installDir' in self.parameter and self.parameter['installDir']:
                        self.appendInstallDir(deploymentFile, self.parameter['installDir'])
                        
                    self.logger.info(cmd)
                    rtv = os.system(cmd)
                    if rtv != 0:
                        raise Exception("Installing %s exited abnormally, code: %d" % (appType, rtv))
                    
        
    def __generateDeploymentFile(self, deploymentFile):        
        newDeploymentFile = os.path.join(self.tmpFolder, "Suite_deployment.xml")
        componentProxyFiles = []
        
        payloadsFolder = None
        for componentFolderPattern in self.exInstallComponents:
            if os.name=="nt":
                if not payloadsFolder:
                    payloadsFolder = self._searchFolder(self.downloadFolder, "payloads")
                if not payloadsFolder:
                    raise "Payloads Folder is not existing"
                
                componentFolders = self._searchFolders(payloadsFolder, componentFolderPattern)
                                
                for componentFolder in componentFolders:
                    for componentProxyFilePattern in self.componentProxyFiles:
                        componentProxyFile = self._searchFile(componentFolder, componentProxyFilePattern)
                        if componentProxyFile:
                            componentProxyFiles.append(componentProxyFile)
            else:
                for dmgPath in self.dmglist:
                    payloadsFolder = self._searchFolder(dmgPath, "payloads")
                    if not payloadsFolder:
                        raise "Payloads Folder is not existing"
                    
                    componentFolders = self._searchFolders(payloadsFolder, componentFolderPattern)

                    for componentFolder in componentFolders:
                        for componentProxyFilePattern in self.componentProxyFiles:
                            componentProxyFile = self._searchFile(componentFolder, componentProxyFilePattern)
                            if not componentProxyFile:
                                continue
                            else:
                                componentProxyFiles.append(componentProxyFile)
                                
        if len(componentProxyFiles)==0:
            return deploymentFile
        else:
            deploymentFileContent = open(deploymentFile).read()
            
            for componentProxyFile in componentProxyFiles:
                try:
                    resFile = open(componentProxyFile, 'r', 1024)
                except IOError:
                    print 'IOError', sys.exc_value
                adobeCode = None
                for line in resFile:
                    if re.search("\"AdobeCode\">{", line):
                        #(f1,f2) = line.split('{')
                        #(adobeCode,f4) = f2.split('}')
                        adobeCode = re.sub(r'.*\"AdobeCode\">\s*\{([\w+|-]+)}.*', r'\1', line).rstrip()
                        break;
                if not adobeCode:
                    continue
                
                deploymentFileContent = re.sub(r'(.*)<Payload adobeCode=\"{' + adobeCode + '}\">\s*<Action>install</Action>\s*</Payload>(.*)', r'\1\2', deploymentFileContent)
                
            self._writeDeploymentXML(newDeploymentFile, deploymentFileContent)
            return newDeploymentFile
        
    def _windUp(self):
        #Install PS Plug-In        
        super(childTask, self)._windUp()

##################This section is mainly for debug -- Begin #############################
if __name__ == '__main__':
    task = childTask('SuiteInstall', 1)
    task.addPara('installerType', 'RIBS')
    task.addPara('appName', 'Master Collection')
    task.addPara('appVer', 'CS6')
    task.addPara('appLang', 'en_US')
    task.addPara('appCertLevel', 'Not Tested')
    task.run()

##################This section is mainly for debug -- End #############################
