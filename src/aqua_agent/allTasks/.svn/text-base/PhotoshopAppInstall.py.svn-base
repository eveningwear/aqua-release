"""

    AppInstall.py
    
    Written by: Kathy Guo (kguo@adobe.com)
    Written by: Jacky Li (yxli@adobe.com)
    
    FOR WIN - installation
    1. FTP to download package
    2. Unzip the zip files in package
    3. Uninstall previous installation
    4. Install new build
    5. cleanup folder
    6. Send back confirmation signal?
    
    FOR MAC - installation
    1. FTP to data drive
    2. Extract DMG
    3. Uninstall previous installation
    4. Install new build
    5. send back confirmation signal
    

    todo:tell which app to uninstall
    todo:transfer parameters
    todo:WIN 64 install

"""
##################This section is mainly for debug -- Begin #############################        
import sys
sys.path.append("C:\Python25")
sys.path.append("D:\QMSClient")
#sys.path.append("/Volumes/10.5-2/Users/tester/Documents/workspace/Client/")
##################This section is mainly for debug -- End #############################

from allTasks.baseTask import Task

from xml.dom import minidom
import os, subprocess, zipfile, platform
import shutil
import re
import tarfile
            
class childTask(Task):    
    
    def __init__(self, type, priority = 800):        
        super(childTask, self).__init__(type, priority)
        
##################This section is mainly for debug -- Begin #############################   
##      self.parameter['APPPackHost'] = '10.162.120.67' 
##      self.parameter['APPPackUser'] = 'AppFTPAccount' 
##      self.parameter['APPPackPasswd'] = 'G00dluck' 
##      self.parameter['APPPacklocation'] =    '/Projects/Bridge/builds/3.0/Win/mul/20080310.m.251'
        '''
        self.parameter['APPPackHost'] = 'pek-rnd-buildfs'
        self.parameter['APPPackUser'] = 'adobenet/kguo'
        self.parameter['APPPackPasswd'] = ''
#       self.parameter['APPPacklocation'] = '/psqe/Builds/Photoshop/Builds/11.0/KilladmPrivateBuild/20080328' #killadm
        self.parameter['APPPacklocation'] = '/psqe/Builds/Photoshop/Builds/11.0/win32/Americas/20080328.m.319' #bridge
        '''
        
        self.parameter['APPPackHost'] = 'pektools'
#        self.parameter['APPPackUser'] = 'tonyhao'
#        self.parameter['APPPackPasswd'] = 'tonyhao'
#        self.parameter['APPPacklocation'] = '/Volumes/Photoshop Build Store/ps-builds/Photoshop/12.0/Application/win32/Americas/20090723.m.687/Retail'
        self.parameter['APPPackHost'] = 'pektools'
        self.parameter['APPPacklocation'] = '/pektools/Builds/Photoshop/12.0/Application/win32/Americas/20090721.m.687/Release/RibInstaller'
        self.parameter['appName'] = 'Photoshop'
        self.parameter['appVer'] = '12.0'
        self.parameter['installerType'] = 'RIBS'
             
##################This section is mainly for debug -- End #############################
        self.unzipbuildPath = ''
        self.downloadFolder = os.path.join(os.getcwd(), 'download')
        try:
            if (os.path.exists(self.downloadFolder)):
                shutil.rmtree(self.downloadFolder)
            os.mkdir(self.downloadFolder)
        except WindowsError, (errno,strerror):
            self.logger.error("catch WindowsError: error(%s): %s" % (errno,strerror))
        
        self.dmglist = []
        
        if os.name == 'posix':
            self.platform = "osx10"
        if os.name == 'nt':
            windowsversion = sys.getwindowsversion()
            if windowsversion[0]<= 5: #XP
                self.platform = "win32"
            else:#Vista and Win7 value is 6
                self.platform = "win64"

    def run(self):
#        self.__getAppPackage()
        if 'appName' in self.parameter and 'appVer' in self.parameter:
            self.app = self.parameter['appName'] + self.parameter['appVer']
        else:
            if self.parameter['installerType'] == 'RAW':
                self.app = 'Bridge RAW'
            else:
                self.app = 'unknown'
        #self.parameter['installParam'] = "*.install.xml;deployment.xml"
        #self.installParam = ["\.install\.xml", "deployment\.xml", "install.xml"]
        if self.platform == "win32":
            self.installParam = ["en_US_Deployment.xml"]
        elif self.platform == "win64":
            self.installParam = ["en_US_Hybid_Deployment.xml"]
        else:
            self.installParam = ["en_US_Deployment.xml"]
            
        super(childTask, self).run()
        
    def runWin(self):
        self.logger.debug('AppInstall runWin')
#        self.installerName = ["Setup.exe", "RunMeFirst.exe"]
        self.installerName = ["RunMeFirst.exe", "Setup.exe"]
        for root, dirs, files in os.walk(self.downloadFolder):
            for f in files:                                                    
                if (zipfile.is_zipfile(os.path.join(root,os.path.basename(f))) ):
                    self.unzipbuildPath = root
                    self._unzipfile(os.path.join(root,os.path.basename(f)),root)
        self._uninstallWINAPP(self.app)
        self._installWINAPP(self.app)
        self._cleanupWIN(self.app)

    def runMac(self):
        import plistlib
        self.logger.debug('AppInstall runMac')
        self.installerName = ["Setup", "Install"]
##        self._uninstallMACAPP('photoshopcs4')
        if self.parameter['installerType'] == 'RAW':
            for root, dirs, files in os.walk(self.downloadFolder):
                for f in files:                                                    
                    if (zipfile.is_zipfile(os.path.join(root,os.path.basename(f))) ):
                        self.unzipbuildPath = root
                        self._unzipfile(os.path.join(root,os.path.basename(f)),root)
                    if '.tar.gz' in os.path.basename(f):
                        self.unzipbuildPath = root                        
                        tar = tarfile.open(os.path.join(root,os.path.basename(f)),"r:gz")
                        for tarinfo in tar:
                            tar.extract(tarinfo.name,root)
                        tar.close()
                    if '.dmg' in os.path.basename(f):
                         self.unzipbuildPath = self._attachDMG(os.path.join(root,os.path.basename(f)))
        else:
            for root, dirs, files in os.walk(self.downloadFolder):
                for f in files:                                                    
                    if ("dmg" in os.path.basename(f) ):
                        self._attachDMG(os.path.join(root,os.path.basename(f)))
                        
        self._installMACAPP(self.app)
        self._cleanupMAC()

    def __getAppPackage(self):
        self.logger.debug('get Package')
        #Attention: For OSImage, here must be FolderPath other than FilePath
        
        #task.addPara('FolderPath', self.parameter['APPPacklocation'])
        #FIXME
        if self.parameter['installerType'] == 'RAW':
            appLocation = self.parameter['APPPacklocation']
            self.downloadFolder = os.path.join(self.downloadFolder, 'BridgeRawBuild')
            self.logger.debug('download raw build from: %s', appLocation)
        elif 'APPPacklocation' in self.parameter:
            appLocation = self.parameter['APPPacklocation']
            self.downloadFolder = os.path.join(self.downloadFolder, 'Build')
            self.logger.debug('download raw build from: %s', appLocation)
        else:
            latestBuild = self._dbutil.getLatestBuild(
                                self.parameter['appName'],
                                self.parameter['appVer'],
                                self.platform,
                                self.parameter['appLang'],
                                self.parameter['appCertLevel'])
            if latestBuild==None:
                return None
            
            latestBuildLocation = latestBuild[1]                        
            
            appLocation = re.sub(r'^/*(.*)', r'\1', latestBuildLocation.replace("\\", "/"))
            self.downloadFolder = os.path.join(self.downloadFolder, self.parameter['appName']+self.parameter['appVer'])
            
        #set build folder path
        self.logger.debug('Build Location is %s', appLocation)
        
        if re.match('^ftp:', appLocation.lower()):
            from FTPTask import childTask
            task = childTask('task')
            host = re.sub(r'^ftp://([^/]*)/.*', r'\1', appLocation)
            task.addPara('Host', host)
            task.addPara('User', self._commonDomain + '\\' + self._commonUser)
            task.addPara('Passwd', self._commonPassword)
            
            appLocation = re.sub(r'^[^/]*(/.*)', r'\1', appLocation[6:])
            if re.match('.*/$', appLocation):
                #Delete ftp://                
                task.addPara('FolderPath', appLocation)
            else:
                task.addPara('FilePath', appLocation)
        else:
            from SambaTask import childTask
            task = childTask('task')
            task.addPara('sambaDomain', self._commonDomain)
            task.addPara('sambaUser', self._commonUser)
            task.addPara('sambaPsw', self._commonPassword)

            if 'appLang' in self.parameter:
                task.addPara('appLang', self.parameter['appLang'])
            task.addPara('FolderPath', appLocation)
        
        #Change downloadFolder to avoid collision with other Product

        task.addPara('Repository', self.downloadFolder)

        task.run()
        return task.getDownloadList()
    
    def _searchFile(self, parent, fileName):
        for root, dirs, files in os.walk(parent):
            for filename in files:
                if re.search(fileName, filename)!=None or filename.lower()==fileName.lower():
                    filePath = os.path.join(root, filename)
                    return filePath
        return None
    
    def _searchFolder(self, parent, folderName):
        for root, dirs, files in os.walk(parent):
            for dirname in dirs:
                if re.search(folderName, dirname)!=None or dirname.lower()==folderName.lower():
                    dirpath = os.path.join(root, dirname)
                    return dirpath
        return None

    def _unzipfile(self, zipfilename, des):
        self.logger.debug('UNZIP %s', zipfilename)
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
        return tmpfolder
       

    def _uninstallWINAPP(self, appType):
        self.logger.info('Uninstall %s? not yet implemented:)' % appType)
        
    def _installWINAPP(self, appType): 
        self.logger.debug('install application:' + appType)
        #we need find out where the setup.exe file exist.                    
        if self.parameter['installerType'] == 'RAW':            
            bridgeExeFile  = self._searchFile(self.unzipbuildPath, 'Bridge.exe')
            tmphead, tmptail = os.path.split(bridgeExeFile)
            bridgeInstallPath = self._getinstallerPath()
            if bridgeInstallPath == None or bridgeInstallPath== '':
                self.logger.error("native Bridge was not installed on this machine, must install RIBS or MSI bridge build before install Raw Build")                
                return
            bridgeBackPath = bridgeInstallPath+'bak'
            self.logger.info('bridge install path:'+bridgeInstallPath)
            #backup current install bridge and override the original bridge
            if os.path.exists(bridgeInstallPath):
                if os.path.exists(bridgeBackPath):
                    shutil.rmtree(bridgeBackPath, True)
                shutil.copytree(bridgeInstallPath, bridgeBackPath, True)
                shutil.rmtree(bridgeInstallPath, True)                
                shutil.copytree(tmphead, bridgeInstallPath, True)
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
                    raise Exception("Deployment File is not exited in %s" % self.installParam)
                    
                cmd = '%s --mode=silent --deploymentFile=%s --skipProcessCheck=1' % (installerFile, deploymentFile)
                #if self.parameter['installDir']:
                #    self.appendInstallDir(deploymentFile, self.parameter['installDir'])
                    
                self.logger.debug(cmd)
                rtv = os.system(cmd)
                if rtv != 0:
                    raise Exception("Installing %s exited abnormally, code: %d" % (appType, rtv))
            elif self.parameter['installerType'] == 'MSI':
                pass
               
        #copy the optional plug-in to %programfiles% and %programfiles(x86)%(64bitOSonly) folder.
        if appType == 'Photoshop12.0':
            programfile = os.getenv("ProgramFiles")
            programfile64 = os.getenv("ProgramFiles(x86)")
            for root, dirs, files in os.walk(self.downloadFolder):
                for _folder in ['Plug-Ins_Release_Win32', 'Optional_Plug-Ins_Release_Win32', 'Plug-Ins_Release_x64', 'Optional_Plug-Ins_Release_x64']:
                    if _folder in root:
                        pf = programfile if _folder.endswith('32') else programfile64
                        if pf:
                            programfilepath = os.path.join(pf, "Adobe", 'Adobe Photoshop CS5','Plug-Ins', os.path.basename(root))
                            self._movefolder(root, programfilepath)
                        
    def _cleanupWIN(self, appType):
        self.logger.debug('cleanup the download build folder')
        try:
            if (os.path.exists(self.downloadFolder)):
                shutil.rmtree(self.downloadFolder)
        except WindowsError, (errno,strerror):
            self.logger.error("Cleanup error(%s): %s" % (errno,strerror))
        
    def _movefolder(self, src, des):
        try:
            if(os.path.exists(des)):
                shutil.rmtree(des)
            else:
                self.logger.debug('Mkdir: %s' % des)
                os.mkdir(des)
            move = 'xcopy /s /e /y "%s" "%s\\"' % (src, des)
            self.logger.debug(move)
            os.system(move)
        except WindowsError, (errno,strerror):
            self.logger.error("Move error(%s): %s" % (errno,strerror))


    def _uninstallMACAPP(self, appType):
        self.logger.info('Uninstall %s? not yet implemented:)' % appType)

    def _attachDMG(self, filename):
        import plistlib
        cmd = "hdiutil attach '" + filename + "' -plist > temp.plist"
        self.logger.debug(cmd)
        ret = os.system(cmd)
        if ret != 0:
            self.logger.debug("attach error: %d" % ret)
        else: #parse the plist file to get the mount-point value, add this to the dmglist. There maybe multiple dmg, such as plugin for photoshop
            diskname = ''           
            pl = plistlib.readPlist("temp.plist")
            for itemx in pl:
                indexy = 0
                for itemy in pl[itemx]:
                    if pl[itemx][indexy].has_key('mount-point'):
                        diskname = pl[itemx][indexy]['mount-point']                       
                        self.dmglist.append(diskname)
                        return diskname
                    indexy = indexy +1 
                    
    def _installMACAPP(self, appType):
        self.logger.debug("install mac application %s" % appType)
        #Let's find the Setup.app first
        found = False
        if self.parameter['installerType'] == 'RAW':            
            bridgeApp  = self._searchFile(self.unzipbuildPath, r'Adobe Bridge CS5.app')
            if bridgeApp == None or bridgeApp == '':
                self.logger.error("this is invalid bridge mac raw build")
            tmphead, tmptail = os.path.split(bridgeApp)
            bridgeInstallPath = self._getinstallerPath()
            if bridgeInstallPath == None or bridgeInstallPath== '':
                self.logger.error("native Bridge was not installed on this machine, must install RIBS or MSI bridge build before install Raw Build")                
                return
            bridgeBackPath = bridgeInstallPath+'bak'
            self.logger.info('bridge install path:'+bridgeInstallPath)
            #backup current install bridge and override the original bridge
            if os.path.exists(bridgeInstallPath):
                if os.path.exists(bridgeBackPath):
                    shutil.rmtree(bridgeBackPath, True)
                shutil.copytree(bridgeInstallPath, bridgeBackPath, True)
                shutil.rmtree(bridgeInstallPath, True)                
                shutil.copytree(tmphead, bridgeInstallPath, True)
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
                        raise Exception("Deployment File is not exited in %s" % self.installParam)
                        
                    cmd = 'sudo %s --mode=silent --deploymentFile=%s' % (installerFile, deploymentFile)
                    if self.parameter['installDir']:
                        self.appendInstallDir(deploymentFile, self.parameter['installDir'])
                        
                    self.logger.debug(cmd)
                    rtv = os.system(cmd)
                    if rtv != 0:
                        raise Exception("Installing %s exited abnormally, code: %d" % (appType, rtv))
                
    def appendInstallDir(self, depFile, installDir):
        try:
            f = open(depFile)
            doc = minidom.parse(f)
            p = doc.getElementsByTagName('Properties')
            if p:
                tag = doc.createElement('Property')
                tag.setAttribute('name', 'INSTALLDIR')
                tag.appendChild(doc.createTextNode(installDir))
                p[0].appendChild(tag)
                doc.writexml(file(depFile, 'w'))
                f.close()
        except IOError:
            pass

    def _cleanupMAC(self):
        self.logger.debug('cleanup the disk')
        for i in self.dmglist:
            self._detachDMG(i)
        
        try:
            if (os.path.exists(self.downloadFolder)):
                shutil.rmtree(self.downloadFolder)
        except WindowsError, (errno,strerror):
            self.logger.error("Cleanup error(%s): %s" % (errno,strerror))
                     
    def _detachDMG(self, filename):
        try:
            cmd = "hdiutil detach '%s'" % filename
            self.logger.debug(cmd)
            ret = os.system(cmd)
            if ret != 0:
                self.logger.debug("detach error %d", ret)
        except WindowsError, (errno,strerror):
            self.logger.error("Detach error(%s): %s" % (errno,strerror))
            
    def _getinstallerPath(self):
        if os.name == 'posix':
           installPath = r'/Applications/Adobe Photoshop CS5'
           if not os.path.exists(installPath):
               self.logger.error("Please first install RIBS Photoshop build")               
        if os.name == 'nt':
            import _winreg            
            try:
                key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Adobe\Photoshop\12.0\ApplicationPath', 0, _winreg.KEY_READ)
            except Exception, e:
                self.logger.info('registy key SOFTWARE\\Adobe\Photoshop\12.0\ApplicationPath does not exist in HKEY_LOCAL_MACHINE, adobe Photoshop cs5 64 bit was not installed in this machine')                             
                #windows x64 system
                try: 
                    self.logger.info('try to access x32 adobe install path info in registy')
                    key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Wow6432Node\Adobe\Photoshop\12.0\ApplicationPath', 0, _winreg.KEY_READ)            
                except Exception, e:            
                        self.logger.error(' adobe photoshop cs5 was not installed in this machine, please check')
                        key = None
                        return
                
            installPath, typeId = _winreg.QueryValueEx(key,'InstallPath')        
            _winreg.CloseKey(key)
        return installPath
        
        
##################This section is mainly for debug -- Begin #############################
if __name__ == '__main__':    
#    o=childTask('PhotoshopAppInstall', 1)
    o=childTask('PhotoshopAppInstall', 800)
    o.run()
#    filePath = o._searchFile("C:\Program Files\Adobe\Adobe Bridge CS4", "application.xml")
    '''
    if 'nt' in os.name:
        o.runWin()        
    elif 'mac' in os.name: 
        o.runMac()
    else:
        print("don't support this os")
   '''


##################This section is mainly for debug -- End #############################
