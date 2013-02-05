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
#sys.path.append("C:\Python25\ResTool\Client")
#sys.path.append("/Volumes/10.5-2/Users/tester/Documents/workspace/Client/")
##################This section is mainly for debug -- End #############################

from allTasks.baseTask import Task

from xml.dom import minidom
import os, subprocess, zipfile
import shutil
import re
import tarfile
import globalProperty
            
class childTask(Task):    
    
    def __init__(self, type, priority = 800):        
        super(childTask, self).__init__(type, priority)
        
        self.tmpFolder = os.path.join(os.getcwd(), 'tmp')
        try:
            if (os.path.exists(self.tmpFolder)):
                shutil.rmtree(self.tmpFolder)
            os.mkdir(self.tmpFolder)
        except WindowsError, (errno,strerror):
            self.logger.error("catch WindowsError: error(%s): %s" % (errno,strerror))
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
##################This section is mainly for debug -- End #############################
        self.unzipbuildPath = ''
        self.downloadFolder = os.path.join(os.getcwd(), 'download')
                
        self.uninstallFolder = os.path.join(os.getcwd(), 'uninstall')
        
        if not os.path.exists(self.uninstallFolder):
            os.mkdir(self.uninstallFolder) 
        
        '''
        try:
            if (os.path.exists(self.downloadFolder)):
                shutil.rmtree(self.downloadFolder)
            os.mkdir(self.downloadFolder)
        except WindowsError, (errno,strerror):
            self.logger.error("catch WindowsError: error(%s): %s" % (errno,strerror))
        '''
        self._rmtree(self.downloadFolder)
        if not os.path.exists(self.downloadFolder):
            os.mkdir(self.downloadFolder)
        
        self.dmglist = []
        
        if os.name == 'posix':
            self.platform = "osx10"
        if os.name == 'nt':
            self.platform = "win32"
            
        self.compileTarget = "Release"
        self.buildNum = ""
        
    def initParam(self):
        if 'deploymentFile' in self.parameter and self.parameter['deploymentFile']:
            self.installParam = [self.parameter['deploymentFile']]
            self.uninstallParam = [self.parameter['deploymentFile'], "remove.xml", "\.remove\.xml"]
        else:
            self.installParam = ["\.install\.xml", "deployment\.xml", "install.xml", "setup.xml"]
            self.uninstallParam = ["remove.xml", "\.remove\.xml"]

    def run(self):
        if 'appPlatform' in self.parameter:
            self.platform = self.parameter['appPlatform']
        if not 'appSubProduct' in self.parameter:
            self.parameter['appSubProduct'] = 'Application'
        self.downloadList = self._getAppPackage()
        if self.downloadList==None:
            self.logger.warning("Nothing Downloaded")
            return
        if 'appName' in self.parameter and 'appVer' in self.parameter:
            self.app = self.parameter['appName'] + self.parameter['appVer']
        else:
            if self.parameter['installerType'] == 'RAW':
                self.app = 'Bridge RAW'
            else:
                self.app = 'unknown'
        super(childTask, self).run()
        self._windUp()
        
    def runWin(self):
        self.logger.debug('AppInstall runWin')
        self.installerName = ["Set-up.exe", "RunMeFirst.exe", "Setup.exe", "AdobePatchInstaller.exe"]
        zipfilelist = []
        '''
        for root, dirs, files in os.walk(self.downloadFolder):
            for f in files:
                filepath = os.path.join(root,os.path.basename(f))
                if zipfile.is_zipfile(filepath):
                    zipfilelist.append(filepath)
                    self.unzipbuildPath = root
        '''
        for filepath in self.downloadList:
            if zipfile.is_zipfile(filepath):
                unzipLocation = os.path.dirname(filepath)
                self.unzipbuildPath = unzipLocation
                self._unzipfileBy7zip(filepath,unzipLocation)
                
        self._uninstallWINAPP(self.app)

        if not 'uninstallOnly' in self.parameter or self.parameter['uninstallOnly'].strip()!='true':
            self._installWINAPP(self.app)
            self._backUpUnDeploymentFile()
        else:
            self.note = "" #No build installed
        self._cleanupWIN()

    def runMac(self):
        import plistlib
        self.logger.debug('AppInstall runMac')
        self.installerName = ["Install", "Setup", "AdobePatchInstaller"]
        if self.parameter['installerType'] == 'RAW':
            '''
            for root, dirs, files in os.walk(self.downloadFolder):
                for f in files:                                                    
                    if (zipfile.is_zipfile(os.path.join(root,os.path.basename(f))) ):
                        self.unzipbuildPath = root
                        self._unzipfileBy7zip(os.path.join(root,os.path.basename(f)),root)
                    if '.tar.gz' in os.path.basename(f):
                        self.unzipbuildPath = root                        
                        tar = tarfile.open(os.path.join(root,os.path.basename(f)),"r:gz")
                        for tarinfo in tar:
                            tar.extract(tarinfo.name,root)
                        tar.close()
                    if '.dmg' in os.path.basename(f):
                         self.unzipbuildPath = self._attachDMG(os.path.join(root,os.path.basename(f)))
            '''
            for filepath in self.downloadList:
                if zipfile.is_zipfile(filepath):
                    unzipLocation = os.path.dirname(filepath)
                    self.unzipbuildPath = unzipLocation
                    self._unzipfileBy7zip(filepath, unzipLocation)
                if '.tar.gz' in os.path.basename(filepath):
                    unzipLocation = os.path.dirname(filepath)
                    self.unzipbuildPath = unzipLocation                     
                    tar = tarfile.open(filepath,"r:gz")
                    for tarinfo in tar:
                        tar.extract(tarinfo.name,unzipLocation)
                    tar.close()
                if '.dmg' in os.path.basename(filepath):
                    self.unzipbuildPath = self._attachDMG(filepath)
        else:
            '''
            for root, dirs, files in os.walk(self.downloadFolder):
                for f in files:                                                    
                    if ("dmg" in os.path.basename(f) ):
                        self._attachDMG(os.path.join(root,os.path.basename(f)))
            '''
            for filepath in self.downloadList:                                         
                if ("dmg" in os.path.basename(filepath) ):
                    self._attachDMG(filepath)
                    
        self._uninstallMACAPP(self.app)
        
        if not 'uninstallOnly' in self.parameter or self.parameter['uninstallOnly'].strip()!='true':
            self._installMACAPP(self.app)
            self._backUpUnDeploymentFile()
        else:
            self.note = "" #No build installed
            
        self._cleanupMAC()

    def _getAppPackage(self):
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
            buildNum = "unknown"
            from CodexTask import childTask
            task = childTask('codexTask')
            latestBuild = task.getBuild(
                                   self.parameter["appName"],
                                   self.parameter["appVer"],
                                   self.compileTarget, #CompileTarget
                                   self.platform,
                                   self.parameter["appLang"],
                                   self.parameter['appCertLevel'],
                                   self.parameter['appSubProduct'])
            if latestBuild==None:
                return None
                    
            latestBuildLocation = latestBuild._location['protocol'] + "://" + \
                                  latestBuild._location['server'] + \
                                  latestBuild._location['path']
            buildNum = latestBuild._build
            if not globalProperty.isMachineOutOfChina():
                #Support the machine out of China, will download directly                
                localLatestBuild = self._dbutil.getLatestBuild(
                                   self.parameter['appName'],
                                   self.parameter['appVer'],
                                   self.platform,
                                   self.parameter['appLang'],
                                   self.parameter['appCertLevel'],
                                   self.parameter['appSubProduct'])
                    
                if localLatestBuild==None:
                    return None
                    
                localLatestBuildLocation = localLatestBuild[1]
                localBuildNum = localLatestBuild[0]
                    
                if localBuildNum==buildNum:
                    latestBuildLocation = localLatestBuildLocation
                
            appLocation = re.sub(r'^/*(.*)', r'\1', latestBuildLocation.replace("\\", "/"))
            self.note += self.parameter["appName"] + ":" + self.parameter['appVer'] + "(" + buildNum + ")" 
            self.buildNum = buildNum
                
        #set build folder path
        self.logger.debug('Build Location is %s', appLocation)
        return self._downloadAppPackage(appLocation)

    def _downloadAppPackage(self, appLocation):
        self.logger.debug('get Package')
        self.downloadFolder = os.path.join(self.downloadFolder, self.parameter['appName'].replace(" ", "") + self.parameter['appVer'])
        if re.match('^ftp:', appLocation.lower()):
            from FTPTask import childTask
            task = childTask('task')
            if re.match('.*@.*', appLocation):
                host = re.sub(r'^.*@([^/]*)/.*', r'\1', appLocation)
                task.addPara('Host', host)
                username = re.sub(r'^ftp://(.*):.*@([^/]*)/.*', r'\1', appLocation)
                password = re.sub(r'^.*:(.*)@([^/]*)/.*', r'\1', appLocation)
                task.addPara('User', username)
                task.addPara('Passwd', password)
            else:
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
    
    def _searchFolders(self, parent, folderName):
        folders = []
        for root, dirs, files in os.walk(parent):
            for dirname in dirs:
                if re.search(folderName, dirname)!=None or dirname.lower()==folderName.lower():
                    dirpath = os.path.join(root, dirname)
                    folders.append(dirpath)
        return folders
    
    def _unzipfileBy7zip(self, zipfilename, des):
        try:
            self.logger.debug('UNZIP %s to %s', zipfilename, des)
            
            if (os.path.splitext(zipfilename)[1] != '.zip'):
                self.logger.debug(zipfilename + ' is not a valid zip file')
                return
            
            #first make a folder with the zipfilename
            tmpfolder = os.path.join(des, os.path.splitext(os.path.basename(zipfilename))[0])
            if( not os.path.exists(tmpfolder)):
                os.mkdir(tmpfolder)
            cmd = ''
            if os.name == 'posix':
                cmdGrantAccess = 'sudo chmod +x ' + self.getToolsDir() + '/7zip/7za'
                self.logger.debug('Start to Grant Access for 7zip : ' + cmdGrantAccess)
                os.system(cmdGrantAccess)
                cmd = self.getToolsDir() + '/7zip/7za'
            if os.name == 'nt':
                cmd = self.getToolsDir() + '/7zip/7za.exe'
                
            cmd = cmd + '  x "' + zipfilename + '" -o' + '\"' + tmpfolder + '\" -ry'
            self.logger.debug('Start to extract with 7zip : ' + cmd)
            os.system(cmd)
                
        except Exception, e:
            self.logger.debug('UNZIP %s to %s Failed', zipfilename, des) 

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
        self.logger.info('Uninstall %s ...' % appType)
        unDeploymentFile = self._getUnDeploymentFile()
        
        if os.path.exists(unDeploymentFile) and self.parameter['installerType'] == 'RIBS':
            for installerFileNamePattern in self.installerName:
                installerFile = self._searchFile(self.downloadFolder, installerFileNamePattern)
                if installerFile:
                    break
                
            if not installerFile:
                raise Exception("Installer is not exited in %s" % self.installerName)
                
            cmd = '"%s" --mode=silent --deploymentFile=%s --skipProcessCheck=1' % (installerFile, unDeploymentFile)
            
            rtv = os.system(cmd)
            if rtv != 0:
                self.logger.info("Uninstall code: %d" % rtv)
            else:
                self._cleanUpUnDeploymentFile()
        
    def _installWINAPP(self, appType): 
        self.logger.info('Install %s ...' % appType)
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
                
                for unDeploymentFileNamePattern in self.uninstallParam:
                    unDeploymentFile = self._searchFile(self.downloadFolder, unDeploymentFileNamePattern)
                    if unDeploymentFile:
                        break
                
                if not deploymentFile:
                    raise Exception("Deployment File is not exited in %s" % self.installParam)
                
                self.logger.info("Found the deployment file %s" % deploymentFile)
                
                self.deploymentFile = self._makeUpDeploymentFileOnWin(deploymentFile)
                
                if not unDeploymentFile:
                    self.unDeploymentFile = self.deploymentFile
                else:
                    self.unDeploymentFile = unDeploymentFile
                
                overrideFile = None
                if "serialNumber" in self.parameter:
                    overrideFile = self.getOverrideFileWithSerialNumber(self.parameter["serialNumber"])
                    
                if overrideFile==None:
                    cmd = '"%s" --mode=silent --deploymentFile=%s --skipProcessCheck=1' % (installerFile, self.deploymentFile)
                else:
                    cmd = '"%s" --mode=silent --deploymentFile=%s --overrideFile=%s --skipProcessCheck=1' % (installerFile, self.deploymentFile, overrideFile)
                if 'installDir' in self.parameter and self.parameter['installDir']:
                    self.appendInstallDir(self.deploymentFile, self.parameter['installDir'])
                    
                self.logger.debug(cmd)
                rtv = os.system(cmd)
                if rtv != 0:
                    raise Exception("Installing %s exited abnormally, code: %d" % (appType, rtv))
            elif self.parameter['installerType'] == 'MSI':
                pass
               
        #copy the optional plug-in to %programfiles% and %programfiles(x86)%(64bitOSonly) folder.
        if appType == 'Photoshop11.0':
            programfile = os.getenv("ProgramFiles")
            programfile64 = os.getenv("ProgramFiles(x86)")
            for root, dirs, files in os.walk(self.downloadFolder):
                for _folder in ['Plug-Ins_Release_Win32', 'Optional_Plug-Ins_Release_Win32', 'Plug-Ins_Release_x64', 'Optional_Plug-Ins_Release_x64']:
                    if _folder in root:
                        pf = programfile if _folder.endswith('32') else programfile64
                        if pf:
                            programfilepath = os.path.join(pf, "Adobe", 'Adobe Photoshop CS4','Plug-Ins', os.path.basename(root))
                            self._movefolder(root, programfilepath)
                        
    def _cleanupWIN(self):
        self.logger.info('cleanup the download build folder')
        try:
            if (os.path.exists(self.downloadFolder)):
                shutil.rmtree(self.downloadFolder)
        except WindowsError, (errno,strerror):
            self.logger.error("Cleanup error(%s): %s" % (errno,strerror))
        
    def _movefolder(self, src, des):
        try:
            if(os.path.exists(des)):
                shutil.rmtree(des)
            #else:
                #self.logger.debug('Mkdir: %s' % des)
                #os.mkdir(des)
            #move = 'xcopy /s /e /y "%s" "%s\\"' % (src, des)
            self.logger.debug("Copy File from %s to %s" % (src, des))
            shutil.copytree(src, des, True)
            #os.system(move)
        except WindowsError, (errno,strerror):
            self.logger.error("Move error(%s): %s" % (errno,strerror))


    def _uninstallMACAPP(self, appType):
        self.logger.info('Uninstall %s ...' % appType)
        unDeploymentFile = self._getUnDeploymentFile()
        
        if os.path.exists(unDeploymentFile) and self.parameter['installerType'] == 'RIBS':
            for dmgPath in self.dmglist:
                for installerFileNamePattern in self.installerName:
                    installerFile = self._searchFolder(dmgPath, installerFileNamePattern)
                    if installerFile:
                        installerFile = os.path.join(installerFile, 'Contents/MacOS/' + installerFileNamePattern)
                        break
                
                if not installerFile:
                    raise Exception("Installer is not exited in %s" % self.installerName)
                    
                cmd = 'sudo "%s" --mode=silent --deploymentFile="%s"' % (installerFile, unDeploymentFile)
                
                rtv = os.system(cmd)
                if rtv != 0:
                    self.logger.info("Uninstall code: %d" % rtv)
                else:
                    self._cleanUpUnDeploymentFile()

    def _attachDMG(self, filename):
        import plistlib
        cmd = "hdiutil attach '" + filename + "' -plist > /tmp/attach.plist"
        self.logger.debug(cmd)
        ret = os.system(cmd)
        if ret != 0:
            self.logger.debug("attach error: %d" % ret)
        else: #parse the plist file to get the mount-point value, add this to the dmglist. There maybe multiple dmg, such as plugin for photoshop
            diskname = ''           
            pl = plistlib.readPlist("/tmp/attach.plist")
            for itemx in pl:
                indexy = 0
                for itemy in pl[itemx]:
                    if pl[itemx][indexy].has_key('mount-point'):
                        diskname = pl[itemx][indexy]['mount-point']                       
                        self.dmglist.append(diskname)
                        return diskname
                    indexy = indexy +1 
                    
    def _installMACAPP(self, appType):
        self.logger.info("Install %s ..." % appType)
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
                        installerFile = self._searchFile(dmgPath, installerFileNamePattern)
                        if installerFile:
                            break
                    
                    if not installerFile:
                        raise Exception("Installer is not exited in %s" % self.installerName)
                    
                    for deploymentFileNamePattern in self.installParam:
                        deploymentFile = self._searchFile(dmgPath, deploymentFileNamePattern)
                        if deploymentFile:
                            break
                
                    for unDeploymentFileNamePattern in self.uninstallParam:
                        unDeploymentFile = self._searchFile(self.downloadFolder, unDeploymentFileNamePattern)
                        if unDeploymentFile:
                            break
                    
                    if not deploymentFile:
                        raise Exception("Deployment File is not exited in %s" % self.installParam)
                
                    self.logger.info("Found the deployment file %s" % deploymentFile)
                    
                    self.deploymentFile = self._makeUpDeploymentFileOnMac(deploymentFile)
                
                    if not unDeploymentFile:
                        self.unDeploymentFile = self.deploymentFile
                    else:
                        self.unDeploymentFile = unDeploymentFile
                    
                    overrideFile = None
                    if "serialNumber" in self.parameter:
                        overrideFile = self.getOverrideFileWithSerialNumber(self.parameter["serialNumber"])
                        
                    if overrideFile==None:
                        cmd = 'sudo "%s" --mode=silent --deploymentFile="%s"' % (installerFile, self.deploymentFile)
                    else:
                        cmd = 'sudo "%s" --mode=silent --deploymentFile="%s" --overrideFile="%s"' % (installerFile, self.deploymentFile, overrideFile)
                        
                    if 'installDir' in self.parameter and self.parameter['installDir']:
                        self.appendInstallDir(self.deploymentFile, self.parameter['installDir'])
                        
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
           installPath = r'/Applications/Adobe Bridge CS5'
           if not os.path.exists(installPath):
               self.logger.error("Please first install RIBS bridge build")               
        if os.name == 'nt':
            import _winreg            
            try:
                key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Adobe\Adobe Bridge\CS5\Installer', 0, _winreg.KEY_READ)
            except Exception, e:
                self.logger.info('registy key SOFTWARE\Adobe\Adobe Bridge\CS5\Installer doesn not exist in HKEY_LOCAL_MACHINE, it maybe x64 system')                             
                #windows x64 system
                try: 
                    self.logger.info('try to access x64 adobe install path info in registy')
                    key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Wow6432Node\Adobe\Adobe Bridge\CS5\Installer', 0, _winreg.KEY_READ)            
                except Exception, e:            
                        self.logger.error(' adobe bridge cs5 was not installed in this machine, please check')
                        key = None
                        return
                
            installPath, typeId = _winreg.QueryValueEx(key,'InstallPath')        
            _winreg.CloseKey(key)
        return installPath
    
    #Deprecated
    def getNewDeploymentFileWithSerialNumber(self, deploymentFile, serialNumber):        
        newDeploymentFile = os.path.join(self.tmpFolder, "New_deployment.xml")
        deploymentFileContent = open(deploymentFile).read()
        serialNumberStr = '\n<Property name="serialNumber">%s</Property>' %serialNumber
        deploymentFileContent = re.sub(r'(.*<Properties>)(.*)', r'\1%s\2' %serialNumberStr, deploymentFileContent)    
        self._writeDeploymentXML(newDeploymentFile, deploymentFileContent)
        return newDeploymentFile
    
    def getOverrideFileWithSerialNumber(self, serialNumber):        
        overrideFile = os.path.join(self.tmpFolder, "override.xml")
        fileContent = """<?xml version="1.0" encoding="UTF-8"?>
<Configuration>
    <Payload>
        <Data key="Serial" protected="0">""" + serialNumber +  """</Data>
        <Data key="Registration">Suppress</Data>
        <Data key="EULA">Suppress</Data>
        <Data key="Updates">Suppress</Data>
    </Payload>
</Configuration>
"""    
        self._writeDeploymentXML(overrideFile, fileContent)
        return overrideFile
    
    #This function is for overriden using if needed
    def _makeUpDeploymentFileOnWin(self, deploymentFile):
        return deploymentFile
    def _makeUpDeploymentFileOnMac(self, deploymentFile):
        return deploymentFile
    
    def _writeDeploymentXML(self, deploymentFile, content):
        f = open(deploymentFile, "w")
        f.write(content)
        f.close()
    #This function should be re-implemented by subclass 
    def _windUp(self):        
        if os.name == 'posix':
            self._cleanupMAC()
        else:
            self._cleanupWIN()
            
    def _getUnDeploymentFile(self):
        unDeploymentFileParent = os.path.join(self.uninstallFolder, self.parameter['appName'], self.parameter['appVer'], self.parameter['appSubProduct'])
        
        if not os.path.exists(unDeploymentFileParent):
            os.makedirs(unDeploymentFileParent) 
            
        unDeploymentFile = os.path.join(unDeploymentFileParent, "unDeploymentFile.xml")
        
        return unDeploymentFile
            
    def _getBuildInfoFile(self):
        buildInfoFileParent = os.path.join(self.uninstallFolder, self.parameter['appName'], self.parameter['appVer'], self.parameter['appSubProduct'])
        
        if not os.path.exists(buildInfoFileParent):
            os.makedirs(buildInfoFileParent)
            
        buildInfoFile = os.path.join(buildInfoFileParent, "buildInfo.txt")        
        return buildInfoFile
                
    def _cleanUpUnDeploymentFile(self):
        unDeploymentFile = self._getUnDeploymentFile()
        
        if os.path.exists(unDeploymentFile):
            os.remove(unDeploymentFile)
        
        buildInfoFile = self._getBuildInfoFile()
        if os.path.exists(buildInfoFile):
            os.remove(buildInfoFile)
                
    def _backUpUnDeploymentFile(self):        
        _unDeploymentFileContent = open(self.unDeploymentFile).read()
        
        unDeploymentFileContent = _unDeploymentFileContent.replace("install", "remove")
        
        unDeploymentFile = self._getUnDeploymentFile()
        
        self._writeDeploymentXML(unDeploymentFile, unDeploymentFileContent)
                
        buildInfoFileContent = self.buildNum
        buildInfoFile = self._getBuildInfoFile()        
        self.creatFile(buildInfoFile, buildInfoFileContent)
        
    def _getInstalledBuildNum(self):
        buildInfoFile = self._getBuildInfoFile()
        
        buildNum = None
        if os.path.exists(buildInfoFile):
            buildNum = open(buildInfoFile).read()
            
        return buildNum        
        
##################This section is mainly for debug -- Begin #############################
if __name__ == '__main__':
    o=childTask('AppInstall', 1)
    #filePath = o._searchFile("C:\Program Files\Adobe\Adobe Bridge CS4", "application.xml")
    
    task = childTask('ai', 1)
    #deploymentFile = "D:\\work\\innovation\\ioix_ws\\dev\\qms\\qmsClient\\src\\allTasks\\download\\Bridge4.0\\Installer\\AdobeBridge4-mul\\deployment\\AdobeBridge4-mul.install.xml"
    #task.getNewDeploymentFileWithSerialNumber(deploymentFile, '123412341234123412341234')
    """
    task.addPara('installerType', 'RIBS')
    task.addPara('appName', 'Bridge')
    task.addPara('appVer', '4.0')
    task.addPara('appLang', 'mul')
    task.addPara('appCertLevel', 'Build Failed')    
    task.addPara('serialNumber', '123412341234123412341234')
    task.run()
    """
    task._backUpUnDeploymentFile();
##################This section is mainly for debug -- End #############################
