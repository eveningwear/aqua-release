"""

    MiniBrInstall.py

    Written by: Jacky Li (yxli@adobe.com)

"""
##################This section is mainly for debug -- Begin #############################        
import sys
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
        self.tmpFolder = os.path.join(os.getcwd(), 'tmp')
        try:
            if (os.path.exists(self.tmpFolder)):
                shutil.rmtree(self.tmpFolder)
            os.mkdir(self.tmpFolder)
        except WindowsError, (errno,strerror):
            self.logger.error("catch WindowsError: error(%s): %s" % (errno,strerror))
            
        self.installComponents = ["Microsoft_VC80", "Microsoft_VC90", "AdobeCSXSInfrastructure", "SwitchBoard", "AdobeMiniBridge"]
        self.componentProxyFiles = ["\.proxy\.xml"]
        self.deploymentRawFileHeader = '''<?xml version="1.0" encoding="UTF-8"?>
<Deployment>
<Properties>
    <Property name="installLanguage">en_US</Property>
</Properties>
<Payloads>'''

        self.deploymentRawFilePayloadContent = '''
    <Payload adobeCode="{$ADOBECODE$}">
        <Action>install</Action>
    </Payload>'''
    
        self.deploymentRawFooter = '''
</Payloads>
</Deployment>
'''
        
    def _installWINAPP(self, appType): 
        self.logger.debug('install application:' + appType)
        #we need find out where the setup.exe file exist.                    
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
                    deploymentFile = self._searchFile(self.downloadFolder, deploymentFileNamePattern)
                    if deploymentFile:
                        break                
                
                if not deploymentFile:
                    deploymentFile = self.__generateDeploymentFile()
                                
                if not deploymentFile:
                    raise Exception("Deployment File is not exited in %s" % self.installParam)
                    
                cmd = '"%s" --mode=silent --deploymentFile=%s' % (installerFile, deploymentFile)
                if self.parameter['installDir']:
                    self.appendInstallDir(deploymentFile, self.parameter['installDir'])
                    
                self.logger.debug(cmd)
                rtv = os.system(cmd)
                if rtv != 0:
                    raise Exception("Installing %s exited abnormally, code: %d" % (appType, rtv))
                
                time.sleep(10)
                
                if not self._verifyInstallation():
                    self.logger.info("Installation is not successful, will be kicked of installation again for second try")
                    rtv = os.system(cmd)
                    if rtv != 0:
                        raise Exception("Installing %s exited abnormally, code: %d" % (appType, rtv))
                    if not self._verifyInstallation():
                        raise Exception("Installing %s failed" % appType)
            elif self.parameter['installerType'] == 'MSI':
                pass
                    
    def _installMACAPP(self, appType):
        self.logger.debug("install mac application %s" % appType)
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
                        deploymentFile = self._searchFile(dmgPath, deploymentFileNamePattern)
                        if deploymentFile:
                            break
                        
                    if not deploymentFile:
                        deploymentFile = self.__generateDeploymentFile()
                                    
                    if not deploymentFile:
                        raise Exception("Deployment File is not exited in %s" % self.installParam)
                        
                    cmd = 'sudo %s --mode=silent --deploymentFile=%s' % (installerFile, deploymentFile)
                    if self.parameter['installDir']:
                        self.appendInstallDir(deploymentFile, self.parameter['installDir'])
                        
                    self.logger.debug(cmd)
                    rtv = os.system(cmd)
                    if rtv != 0:
                        raise Exception("Installing %s exited abnormally, code: %d" % (appType, rtv))
        
        
    def __generateDeploymentFile(self):        
        deploymentFile = os.path.join(self.tmpFolder, "MiniBr_deployment.xml")
        componentProxyFiles = []
        
        payloadsFolder = None
        for componentFolderPattern in self.installComponents:
            if os.name=="nt":
                if not payloadsFolder:
                    payloadsFolder = self._searchFolder(self.downloadFolder, "payloads")
                if not payloadsFolder:
                    raise "Payloads Folder is not existing"
                componentFolder = self._searchFolder(payloadsFolder, componentFolderPattern)
                if not componentFolder:
                    continue
                for componentProxyFilePattern in self.componentProxyFiles:
                    componentProxyFile = self._searchFile(componentFolder, componentProxyFilePattern)
                    if not componentProxyFile:
                        continue
                    else:
                        componentProxyFiles.append(componentProxyFile)
            else:
                for dmgPath in self.dmglist:
                    payloadsFolder = self._searchFolder(dmgPath, "payloads")
                    if not payloadsFolder:
                        raise "Payloads Folder is not existing"
                    componentFolder = self._searchFolder(payloadsFolder, componentFolderPattern)
                    if not componentFolder:
                        continue
                    for componentProxyFilePattern in self.componentProxyFiles:
                        componentProxyFile = self._searchFile(componentFolder, componentProxyFilePattern)
                        if not componentProxyFile:
                            continue
                        else:
                            componentProxyFiles.append(componentProxyFile)
        if len(componentProxyFiles)==0:
            return None
        else:
            payLoadsContent = ''
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
                
                payLoadsContent += self.deploymentRawFilePayloadContent.replace("$ADOBECODE$", adobeCode)
                
            self.__writeDeploymentXML(deploymentFile, payLoadsContent)
            return deploymentFile    
    
    def __writeDeploymentXML(self, deploymentFile, payLoadsContent):
        f = open(deploymentFile, "w")
        f.write(self.deploymentRawFileHeader)
        f.write(payLoadsContent)
        f.write(self.deploymentRawFooter)
        f.close()
        
    def _verifyInstallation(self):
        if os.name=="nt":
            commonProgramFilesPath = os.getenv("CommonProgramFiles")
            miniFPFile = os.path.abspath(os.path.join(commonProgramFilesPath, "Adobe/CS5ServiceManager\extensions\AdobeMiniBridge\MiniFP.swf"))
            if os.path.exists(miniFPFile):
                return True
            else:
                return False
        else:
            miniFPFile = "TBD"
            return True
        
    def _windUp(self):
        self.qeTestModule = self._dbutil.getAppInfo('miniBrQEModule')
        
        from SambaTask import childTask
        task = childTask('addMiniBrQETestModule', 1)
        
        if os.name=="nt":
            commonProgramFilesPath = os.getenv("CommonProgramFiles")
            dest = os.path.abspath(os.path.join(commonProgramFilesPath, "Adobe/CS5ServiceManager\extensions\AdobeMiniBridge\modules"))
        else:
            dest = "TBD"
        if not os.path.exists(dest):
            #raise "The path %s is not existed" % dest
            os.makedirs(dest)
        
        task.addPara('sambaDomain', unicode(self._commonDomain, 'utf-8'))
        task.addPara('sambaUser', unicode(self._commonUser, 'utf-8'))
        task.addPara('sambaPsw', unicode(self._commonPassword, 'utf-8'))
        #task.targetFolder = dest
        task.addPara('Repository', dest) 
    
        task.addPara('FolderPath', unicode(self.qeTestModule, 'utf-8'))
        task.run()
        
if __name__ == '__main__':
    o=childTask('MiniBrInstall', 1)
    o._windUp()
        
