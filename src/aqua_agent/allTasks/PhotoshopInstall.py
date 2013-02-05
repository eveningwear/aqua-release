"""

    PhotoshopInstall.py
    
    Written by: Xi Sheng Shang (xsshang@adobe.com)
    Written by: Jacky Li (yxli@adobe.com)

"""
##################This section is mainly for debug -- Begin #############################        
import sys
#sys.path.append ("..")
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
import CodexTask, FTPTask
            
class childTask(childTask):  
    
    def __init__(self, type, priority = 800):
        super(childTask, self).__init__(type, priority)
        self.tmpFolder = os.path.join(os.getcwd(), 'tmp')
        self.latestBuildLocation = None
        self.provisioningToolLocation = os.path.join(os.getcwd(), 'tools/adobe_provisioning_tool')
        self.samplesLocation = os.path.join(os.getcwd(), 'tools/Samples')
        try:
            if (os.path.exists(self.tmpFolder)):
                shutil.rmtree(self.tmpFolder)
            os.mkdir(self.tmpFolder)
        except WindowsError, (errno,strerror):
            self.logger.error("catch WindowsError: error(%s): %s" % (errno,strerror)) 
        if os.name == 'posix':
            self.platform = "osx10"
        elif os.name == 'nt':
            self.platform = "win32"
            import _winreg            
            try:
                key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 0, _winreg.KEY_READ)
            except Exception, e:
                self.logger.info('registy key SYSTEM\CurrentControlSet\Control\Session Manager\Environment does not exist in HKEY_LOCAL_MACHINE')                             
                         
            Processor_Architecture, typeId = _winreg.QueryValueEx(key,'PROCESSOR_ARCHITECTURE')
            self.processorArc = Processor_Architecture
            _winreg.CloseKey(key)
                
    def run(self):
        if not 'appSubProduct' in self.parameter:
            self.parameter['appSubProduct'] = 'Application'
        if os.name == 'posix':
            self.installParam = [self.parameter['appLang'] + "_Deployment.xml", "setup.xml"]
        elif os.name == 'nt':
            if self.processorArc == "x86":
                self.installParam = [self.parameter['appLang'] + "_Deployment.xml", "setup.xml"]
            elif self.processorArc == "AMD64" or self.processorArc == "EM64T":
                self.installParam = [self.parameter['appLang'] + "_Hybrid_Deployment.xml", "setup.xml"]
            else:
                self.installParam = [self.parameter['appLang'] + "_Deployment.xml", "setup.xml"]
        self.compileTarget = "Release"
        if 'debugBuild' in self.parameter and self.parameter['debugBuild'].strip() == "true":
            self.compileTarget = "Debug"
        self.killRelativeProcess()
        super(childTask, self).run()
        
    def __getLatestBuildLocation(self):
        self.logger.debug('get Photoshop Latest Build')
        if self.latestBuildLocation:
            return self.latestBuildLocation, self.buildNum
        
        latestBuildLocation = None
        buildNum = "unknown"
        
        task = CodexTask.childTask('codexTask')
        if not 'molecule' in self.parameter:
            latestBuild = task.getBuild(
                                    self.parameter["appName"],
                                    self.parameter["appVer"],
                                    self.compileTarget, #"Release", #CompileTarget
                                    self.platform,
                                    self.parameter["appLang"],
                                    self.parameter['appCertLevel'],
                                    self.parameter['appSubProduct'])
            if latestBuild==None:
                return None, None
                
            latestBuildLocation = latestBuild._location['protocol'] + "://" + \
                                          latestBuild._location['server'] + \
                                          latestBuild._location['path']
            self.codexLatestBuildLocation = latestBuildLocation
                
            buildNum = latestBuild._build
            if not globalProperty.isMachineOutOfChina() and self.compileTarget=="Release":
                localLatestBuild = self._dbutil.getLatestBuild(
                                    self.parameter['appName'],
                                    self.parameter['appVer'],
                                    self.platform,
                                    self.parameter['appLang'],
                                    self.parameter['appCertLevel'],
                                    self.parameter['appSubProduct'])
                if localLatestBuild==None:
                    return None, None
                
                localLatestBuildLocation = localLatestBuild[1]
                localBuildNum = localLatestBuild[0]
                
                if buildNum==localBuildNum:
                    latestBuildLocation = localLatestBuildLocation
        else:
            moleculeReStr = "\d{8}\." + self.parameter['molecule'] + "\.\d{1,}"
            builds = task.getBuilds(
                                    self.parameter["appName"],
                                    self.parameter["appVer"],
                                    "Molecule",
                                    self.compileTarget, #"Release", #CompileTarget
                                    self.platform,
                                    self.parameter["appLang"],
                                    self.parameter['appCertLevel'])
            if builds==None:
                    return None, None
                
            latestBuildLocation = None
            for build in builds:
                if re.match(moleculeReStr, build._build):
                    latestBuildLocation = build._location['protocol'] + "://" + \
                                          build._location['server'] + \
                                          build._location['path']
                
                    buildNum = build._build
                    break
            self.codexLatestBuildLocation = latestBuildLocation
            
        self.latestBuildLocation = latestBuildLocation
        self.buildNum = buildNum
            
        return latestBuildLocation, buildNum
        
    def _getAppPackage(self):
        if not 'molecule' in self.parameter:
            self.logger.debug('get Package')
            #Attention: For OSImage, here must be FolderPath other than FilePath
            
            #task.addPara('FolderPath', self.parameter['APPPacklocation'])
            #FIXME
            if 'APPPacklocation' in self.parameter:
                appLocation = self.parameter['APPPacklocation']
                self.downloadFolder = os.path.join(self.downloadFolder, 'Build')
                self.logger.debug('Downloading build from: %s', appLocation)
            else:
                latestBuildLocation, buildNum = self.__getLatestBuildLocation()
                
                if latestBuildLocation==None:
                    return None
                
                appLocation = re.sub(r'^/*(.*)', r'\1', latestBuildLocation.replace("\\", "/"))
                if self.compileTarget=="Debug":
                    self.note += self.parameter["appName"] + ":" + self.parameter['appVer'] + "(" + buildNum + ", debug)" 
                else:
                    self.note += self.parameter["appName"] + ":" + self.parameter['appVer'] + "(" + buildNum + ")" 
                
            #set build folder path
            self.logger.debug('Build Location is %s', appLocation)
            return self._downloadAppPackage(appLocation)
            #return super(childTask, self)._getAppPackage()
        else:
            if 'APPPacklocation' in self.parameter:
                appLocation = self.parameter['APPPacklocation']
                self.downloadFolder = os.path.join(self.downloadFolder, 'Build')
                self.logger.debug('Downloading build from: %s', appLocation)
            else:
                latestBuildLocation, buildNum = self.__getLatestBuildLocation()
                
                if latestBuildLocation==None:
                    return None
                
                appLocation = re.sub(r'^/*(.*)', r'\1', latestBuildLocation.replace("\\", "/"))
                if self.compileTarget=="Debug":
                    self.note += self.parameter["appName"] + ":" + self.parameter['appVer'] + "(" + buildNum + ", debug)"
                else:
                    self.note += self.parameter["appName"] + ":" + self.parameter['appVer'] + "(" + buildNum + ")"
            
            return self._downloadAppPackage(appLocation)
        
    def getPlugIn(self):
        self.logger.debug('get Photoshop PlugIn')
                        
        latestBuildLocation, buildNum = self.__getLatestBuildLocation()
        
        folderPattern = ""
        
        if not 'molecule' in self.parameter:
            plugInLocation = re.sub(r'^(.*/)Application.*', r'\1Plugins/', latestBuildLocation.replace("\\", "/"))        
        else:
            plugInLocation = re.sub(r'^(.*/)Molecule.*', r'\1Plugins/', latestBuildLocation.replace("\\", "/"))
            
        #plugInLocation = self._dbutil.getAppInfo('PS-Plug-Ins-Location')
        if self.platform == 'osx10':
            folderPattern = "osx10/(mul|%s)/%s" % (self.parameter['appLang'], buildNum)
        else:
            if self.processorArc == "x86":
                folderPattern = "win32/(mul|%s)/%s" % (self.parameter['appLang'], buildNum)
            else:
                folderPattern = "(win32|win64)/(mul|%s)/%s" % (self.parameter['appLang'], buildNum)
        
        self.downloadFolder = os.path.join(self.downloadFolder, self.parameter['appName']+self.parameter['appVer']+"-Plug-In")
            
        #set build folder path
        self.logger.debug('Photoshop Plug-In Location is %s', plugInLocation)
        
        if re.match('^ftp:', plugInLocation.lower()):
            task = FTPTask.childTask('task')
            task.addPara('FolderPattern', folderPattern)
            if re.match('.*@.*', plugInLocation):
                host = re.sub(r'^.*@([^/]*)/.*', r'\1', plugInLocation)
                task.addPara('Host', host)
                username = re.sub(r'^ftp://(.*):.*@([^/]*)/.*', r'\1', plugInLocation)
                password = re.sub(r'^.*:(.*)@([^/]*)/.*', r'\1', plugInLocation)
                task.addPara('User', username)
                task.addPara('Passwd', password)
            else:
                host = re.sub(r'^ftp://([^/]*)/.*', r'\1', plugInLocation)
                task.addPara('Host', host)
                task.addPara('User', self._commonDomain + '\\' + self._commonUser)
                task.addPara('Passwd', self._commonPassword)
            
            plugInLocation = re.sub(r'^[^/]*(/.*)', r'\1', plugInLocation[6:])
            if re.match('.*/$', plugInLocation):
                #Delete ftp://                
                task.addPara('FolderPath', plugInLocation)
            else:
                task.addPara('FilePath', plugInLocation)
            task.addPara('pattern', '.*Internal.*Plug-Ins.*')
        else:
            from SambaTask import childTask
            task = childTask('task')
            task.addPara('sambaDomain', self._commonDomain)
            task.addPara('sambaUser', self._commonUser)
            task.addPara('sambaPsw', self._commonPassword)
            if 'appLang' in self.parameter:
                task.addPara('appLang', self.parameter['appLang'])
            task.addPara('FolderPath', plugInLocation)
            task.addPara('filterStr', '.*Plug-Ins.*')
        
        #Change downloadFolder to avoid collision with other Product

        task.addPara('Repository', self.downloadFolder)

        task.run()
        return task.getDownloadList()
    
    def installPlugIn(self):
        if os.name == 'posix':
            self.installMacPlugIn()
        else:
            self.installWinPlugIn()
    
    def installMacPlugIn(self):
        for root, dirs, files in os.walk(self.downloadFolder):
            for f in files:                                                    
                if re.match('.*plug-ins.*%s.*' % self.compileTarget.lower(), f.lower()) and "dmg" in os.path.basename(f):
                    self._attachDMG(os.path.join(root,os.path.basename(f)))
        
        for dmgPath in self.dmglist:
            for root, dirs, files in os.walk(dmgPath):
                if re.match('.*Plug-Ins\s*_*%s.*' % self.compileTarget, root):
                    if not os.path.isdir(root):
                        continue
                    _folder = os.path.basename(root)
                    if re.match('^13.\d+.*', self.parameter["appVer"]):
                        destPath = os.path.join("/Applications", 'Adobe Photoshop CS6','Plug-Ins', os.path.basename(root))
                    elif re.match('^12.1.*', self.parameter["appVer"]):
                        destPath = os.path.join("/Applications", 'Adobe Photoshop CS5.1','Plug-Ins', os.path.basename(root))
                    elif re.match('^12.\d+.*', self.parameter["appVer"]):
                        destPath = os.path.join("/Applications", 'Adobe Photoshop CS5','Plug-Ins', os.path.basename(root))
                    elif re.match('^11.\d+.*', self.parameter["appVer"]):
                        destPath = os.path.join("/Applications", 'Adobe Photoshop CS4','Plug-Ins', os.path.basename(root))
                    else:
                        raise "This version of Photoshop is not supported by current task"
                    self._movefolder(root, destPath)
                    break
                        
    def installWinPlugIn(self):
        for root, dirs, files in os.walk(self.downloadFolder):
            for f in files:
                if re.match('.*plug-ins.*%s.*' % self.compileTarget.lower(), f.lower()) and zipfile.is_zipfile(os.path.join(root,os.path.basename(f))):
                    self.unzipbuildPath = root
                    self._unzipfile(os.path.join(root,os.path.basename(f)),root)
        
        programfile = os.getenv("ProgramFiles")
        programfileX86 = os.getenv("ProgramFiles(x86)")
        if programfileX86:
            programfile = re.sub("(.*)\s+\(x86\)", r"\1", programfile)
        for root, dirs, files in os.walk(self.downloadFolder):
            if re.match('.*Plug-Ins_%s.*' % self.compileTarget, root):
                _folder = os.path.basename(root)
                folderAppendix = ""
                if _folder.endswith('64') and not programfileX86:
                    continue
                elif _folder.endswith('64') and programfileX86:
                    folderAppendix = " (64 Bit)"
                
                pf = programfileX86 if _folder.endswith('32') and programfileX86 else programfile
                
                if pf:
                    if re.match('^13.\d+.*', self.parameter["appVer"]):
                        destPath = os.path.join(pf, "Adobe", 'Adobe Photoshop CS6' + folderAppendix, 'Plug-Ins', os.path.basename(root))
                    elif re.match('^12.1.*', self.parameter["appVer"]):
                        destPath = os.path.join(pf, "Adobe", 'Adobe Photoshop CS5.1' + folderAppendix, 'Plug-Ins', os.path.basename(root))
                    elif re.match('^12.\d+.*', self.parameter["appVer"]):
                        destPath = os.path.join(pf, "Adobe", 'Adobe Photoshop CS5' + folderAppendix, 'Plug-Ins', os.path.basename(root))
                    elif re.match('^11.\d+.*', self.parameter["appVer"]):
                        destPath = os.path.join(pf, "Adobe", 'Adobe Photoshop CS4' + folderAppendix, 'Plug-Ins', os.path.basename(root))
                    else:
                        raise "This version of Photoshop is not supported by current task"
                    self._movefolder(root, destPath)
                    
    def isInstallPS(self, version):
        destPath = None
        if os.name == 'posix':
            if re.match('^13.\d+.*', version):
                destPath = os.path.join("/Applications", 'Adobe Photoshop CS6')
            elif re.match('^12.1.*', version):
                destPath = os.path.join("/Applications", 'Adobe Photoshop CS5.1')
            elif re.match('^12.\d+.*', version):
                destPath = os.path.join("/Applications", 'Adobe Photoshop CS5')
            elif re.match('^11.\d+.*', version):
                destPath = os.path.join("/Applications", 'Adobe Photoshop CS4')
        elif os.name == 'nt':
            programfile = os.getenv("ProgramFiles")
            if re.match('^13.\d+.*', version):
                destPath = os.path.join(programfile, "Adobe", 'Adobe Photoshop CS6')
            elif re.match('^12.1.*', version):
                destPath = os.path.join(programfile, "Adobe", 'Adobe Photoshop CS5.1')
            elif re.match('^12.\d+.*', version):
                destPath = os.path.join(programfile, "Adobe", 'Adobe Photoshop CS5')
            elif re.match('^11.\d+.*', version):
                destPath = os.path.join(programfile, "Adobe", 'Adobe Photoshop CS4')
        if destPath and os.path.exists(destPath):
            return True
        return False
    
    def isInstallCRCPlugIn(self, version):
        destPath = None
        if os.name == 'posix':
            if re.match('^13.\d+.*', version):
                destPath = os.path.join("/Applications", 'Adobe Photoshop CS6', 'Plug-Ins')
            elif re.match('^12.1.*', version):
                destPath = os.path.join("/Applications", 'Adobe Photoshop CS5.1', 'Plug-Ins')
            elif re.match('^12.\d+.*', version):
                destPath = os.path.join("/Applications", 'Adobe Photoshop CS5', 'Plug-Ins')
            elif re.match('^11.\d+.*', version):
                destPath = os.path.join("/Applications", 'Adobe Photoshop CS4', 'Plug-Ins')
        elif os.name == 'nt':
            folderAppendix = ""            
            programfile = os.getenv("ProgramFiles")
            programfileX86 = os.getenv("ProgramFiles(x86)")            
            if programfileX86:
                folderAppendix = " (64 Bit)"
                programfile = re.sub("(.*)\s+\(x86\)", r"\1", programfile)
            
            if re.match('^13.\d+.*', version):
                destPath = os.path.join(programfile, "Adobe", 'Adobe Photoshop CS6' + folderAppendix, 'Plug-Ins')
            elif re.match('^12.1.*', version):
                destPath = os.path.join(programfile, "Adobe", 'Adobe Photoshop CS5.1' + folderAppendix, 'Plug-Ins')
            elif re.match('^12.\d+.*', version):
                destPath = os.path.join(programfile, "Adobe", 'Adobe Photoshop CS5' + folderAppendix, 'Plug-Ins')
            elif re.match('^11.\d+.*', version):
                destPath = os.path.join(programfile, "Adobe", 'Adobe Photoshop CS4' + folderAppendix, 'Plug-Ins')
        if destPath and os.path.exists(destPath):
            for root, dirs, files in os.walk(destPath):
                for f in files:                                                    
                    if re.match('.*exportcrc.*', f.lower()):
                        return True
        return False
    
    def _installDebugger(self):
        if os.name == 'nt':
            debugToolName32bit = self._dbutil.getAppInfo('debug_tool_name_32bit').strip()
            if debugToolName32bit==None:
                debugToolName32bit = "DebugCS6Setup_32.msi"
            
            debugTools = [debugToolName32bit]
            
            programfileX86 = os.getenv("ProgramFiles(x86)")
            if programfileX86:
                debugToolName64bit = self._dbutil.getAppInfo('debug_tool_name_64bit').strip()
                if debugToolName64bit==None:
                    debugToolName64bit = "DebugCS6Setup_64.msi"
                debugTools.append(debugToolName64bit)
            
            for debugToolName in debugTools:
                debugToolPath = os.path.join(self.getToolsDir(), debugToolName)
                if not os.path.exists(debugToolPath):
                    if globalProperty.isMachineOutOfChina():
                        debugToolLocation = self._dbutil.getAppInfo('debug_tool_us').strip()
                    else:
                        debugToolLocation = self._dbutil.getAppInfo('debug_tool_cn').strip()
                    if debugToolLocation==None or debugToolLocation=="":
                        raise "Donwload Debug Tool Failed"
                    else:
                        debugToolLocation += '/' + debugToolName
                        fullPath = debugToolLocation[6:]
                        parts = fullPath.split('/', 1)
                        
                        (host, location) = parts
                        from FTPTask import childTask
                        task = childTask('task')
                        
                        #FIXME: Modified by Jacky
                        task.addPara('Host', host)
                        task.addPara('User', self._commonDomain + "\\" + self._commonUser)
                        task.addPara('Passwd', self._commonPassword)
                        
                        if not location.startswith('/'):
                            location = '/' + location
                    
                        #Attention: For OSImage, here must be FolderPath other than FilePath
                        task.addPara('Repository', self.getToolsDir()) 
                        task.addPara('FilePath', location)
                        task.addPara('OneFile', 'True')
                        task.run()
                    if not os.path.exists(debugToolPath):
                        raise "No Debug Tool Downloaded"
                
                import MSIInstallerTask
                task = MSIInstallerTask.childTask('MSIInstallerTask', 0)
                task.addPara('installerPath', debugToolPath)
                task.run()
        
    def getSymbol(self):
        self.logger.debug('get Photoshop Symbol')
        
        latestBuildLocation, buildNum = self.__getLatestBuildLocation()
        
        latestBuildLocation = self.codexLatestBuildLocation
        
        folderPattern = ""
        
        if not 'molecule' in self.parameter:
            symbolLocation = re.sub(r'^(.*/Application/).*', r'\1', latestBuildLocation.replace("\\", "/"))        
        else:
            symbolLocation = re.sub(r'^(.*)Molecule/).*', r'\1', latestBuildLocation.replace("\\", "/"))
            
        if self.platform == 'osx10':
            folderPattern = "osx10/mul/%s/%s/RawBuild" % (buildNum, self.compileTarget)
        else:
            if self.processorArc == "x86":
                folderPattern = "win32/mul/%s/%s/RawBuild" % (buildNum, self.compileTarget)
            else:
                folderPattern = "(win32|win64)/mul/%s/%s/RawBuild" % (buildNum, self.compileTarget)
        
        self.downloadFolder = os.path.join(self.downloadFolder, self.parameter['appName']+self.parameter['appVer']+"-Symbol")
            
        #set build folder path
        self.logger.debug('Photoshop Symbol Location is %s', symbolLocation)
        
        if re.match('^ftp:', symbolLocation.lower()):
            task = FTPTask.childTask('task')
            task.addPara('FolderPattern', folderPattern)
            if re.match('.*@.*', symbolLocation):
                host = re.sub(r'^.*@([^/]*)/.*', r'\1', symbolLocation)
                task.addPara('Host', host)
                username = re.sub(r'^ftp://(.*):.*@([^/]*)/.*', r'\1', symbolLocation)
                password = re.sub(r'^.*:(.*)@([^/]*)/.*', r'\1', symbolLocation)
                task.addPara('User', username)
                task.addPara('Passwd', password)
            else:
                host = re.sub(r'^ftp://([^/]*)/.*', r'\1', symbolLocation)
                task.addPara('Host', host)
                task.addPara('User', self._commonDomain + '\\' + self._commonUser)
                task.addPara('Passwd', self._commonPassword)
            
            symbolLocation = re.sub(r'^[^/]*(/.*)', r'\1', symbolLocation[6:])
            if re.match('.*/$', symbolLocation):
                #Delete ftp://                
                task.addPara('FolderPath', symbolLocation)
            else:
                task.addPara('FilePath', symbolLocation)
            task.addPara('pattern', '.*Map_%s.*|.*PDB_%s.*|.*Symbol_Files.*' % (self.compileTarget, self.compileTarget))
        else:
            from SambaTask import childTask
            task = childTask('task')
            task.addPara('sambaDomain', self._commonDomain)
            task.addPara('sambaUser', self._commonUser)
            task.addPara('sambaPsw', self._commonPassword)
            if 'appLang' in self.parameter:
                task.addPara('appLang', self.parameter['appLang'])
            task.addPara('FolderPath', symbolLocation)
            task.addPara('filterStr', '.*Release.*')
        
        #Change downloadFolder to avoid collision with other Product

        task.addPara('Repository', self.downloadFolder)

        task.run()
        return task.getDownloadList()
    
    def installSymbol(self):
        if os.name == 'posix':
            self.installMacSymbol()
        else:
            self.installWinSymbol()
    
    def installMacSymbol(self):
        if re.match('^13.\d+.*', self.parameter["appVer"]):
            destPath = os.path.join("/Applications", 'Adobe Photoshop CS6')
        elif re.match('^12.1.*', self.parameter["appVer"]):
            destPath = os.path.join("/Applications", 'Adobe Photoshop CS5.1')
        elif re.match('^12.\d+.*', self.parameter["appVer"]):
            destPath = os.path.join("/Applications", 'Adobe Photoshop CS5')
        elif re.match('^11.\d+.*', self.parameter["appVer"]):
            destPath = os.path.join("/Applications", 'Adobe Photoshop CS4')
        else:
            raise "This version of Photoshop is not supported by current task"
            
        for root, dirs, files in os.walk(self.downloadFolder):
            for f in files:                                                    
                if "dmg" in os.path.basename(f):
                    self._attachDMG(os.path.join(root,os.path.basename(f)))
        
        for dmgPath in self.dmglist:
            for root, dirs, files in os.walk(dmgPath):
                if re.match('.*plugins.*Release_x86_64/[^/]+$', root): # No matter self.compileTarget is Release or Debug, this judgement is stable
                    if not os.path.isdir(root):
                        continue
                    _folder = os.path.basename(root)
                    plugInDestpath = os.path.join(destPath, "Plug-Ins", _folder)
                    for dir in dirs:
                        dirPath = os.path.join(plugInDestpath, dir)
                        if os.path.exists(dirPath):
                            shutil.rmtree(dirPath, True)
                        shutil.copytree(os.path.join(root, dir), dirPath)
                    for file in files:
                        filePath = os.path.join(plugInDestpath, dir)
                        shutil.copy(os.path.join(root, file), filePath)
                """
                elif re.match('.*photoshop.*Release_x86_64/[^/]+$', root): # No matter self.compileTarget is Release or Debug, this judgement is stable
                    if not os.path.isdir(root):
                        continue
                    _folder = os.path.basename(root)
                    psDestpath = os.path.join(destPath, _folder)
                    if os.path.exists(psDestpath) and os.path.isdir(psDestpath):
                        shutil.copytree(root, psDestpath)
                """
                        
    def installWinSymbol(self):
        programfile = os.getenv("ProgramFiles")
        programfileX86 = os.getenv("ProgramFiles(x86)")
        if programfileX86:
            programfile = re.sub("(.*)\s+\(x86\)", r"\1", programfile)
            
        for root, dirs, files in os.walk(self.downloadFolder):
            for f in files:
                if zipfile.is_zipfile(os.path.join(root,os.path.basename(f))):
                    self.unzipbuildPath = root
                    self._unzipfile(os.path.join(root,os.path.basename(f)), root)
                    for subroot, subdirs, subfiles in os.walk(root):
                        for file in subfiles:
                            if re.match('.*Photoshop.pdb$', file) or re.match('.*Photoshop.map$', file):
                                folderAppendix = ""
                                if re.match('.*win64.*', root) and not programfileX86:
                                    continue
                                elif re.match('.*win64.*', root) and programfileX86:
                                    folderAppendix = " (64 Bit)"
                                
                                pf = programfileX86 if re.match('.*win32.*', root) and programfileX86 else programfile
                                
                                if pf:
                                    if re.match('^13.\d+.*', self.parameter["appVer"]):
                                        destPath = os.path.join(pf, "Adobe", 'Adobe Photoshop CS6' + folderAppendix)
                                    elif re.match('^12.1.*', self.parameter["appVer"]):
                                        destPath = os.path.join(pf, "Adobe", 'Adobe Photoshop CS5.1' + folderAppendix)
                                    elif re.match('^12.\d+.*', self.parameter["appVer"]):
                                        destPath = os.path.join(pf, "Adobe", 'Adobe Photoshop CS5' + folderAppendix)
                                    elif re.match('^11.\d+.*', self.parameter["appVer"]):
                                        destPath = os.path.join(pf, "Adobe", 'Adobe Photoshop CS4' + folderAppendix)
                                    else:
                                        raise "This version of Photoshop is not supported by current task"
                                    
                                    if os.path.exists(destPath) and os.path.isdir(destPath):
                                        shutil.copy(os.path.join(subroot, file), destPath)

    def _windUp(self):
        try:
            #do silent activation 
            self.silentActivation()
        except Exception, e:
            self.logger.warning(e)
        
        try:
            #Intall Symbol
            if (not 'uninstallOnly' in self.parameter or self.parameter['uninstallOnly'].strip()!='true') and 'symbol' in self.parameter and  self.parameter['symbol'].strip()=='true':
                self.getSymbol()
                self.installSymbol()
        except Exception, e:
            self.logger.warning(e)
            
        try:
            if self.compileTarget=="Debug":
                self._installDebugger()
        except Exception, e:
            self.logger.warning(e)
        
        try:
            #install Samples
            self.installSampleFile(self.parameter["appVer"])
        except Exception, e:
            self.logger.warning(e)
        
        try:
            #Install Backdoor file
            if 'zstring' in self.parameter and self.parameter['zstring'].strip() == "true":
                self.makeBackDoorFile(self.parameter["appVer"])
        except Exception, e:
            self.logger.warning(e)
        
        try:
            #Install PS Plug-In
            if (not 'uninstallOnly' in self.parameter or self.parameter['uninstallOnly'].strip()!='true') and (not 'installPlugIn' in self.parameter or self.parameter['installPlugIn'].strip()=='true'):
                self.getPlugIn()
                self.installPlugIn()
        except Exception, e:
            self.logger.warning(e)
            
        super(childTask, self)._windUp()
        
    def _makeUpDeploymentFileOnWin(self, deploymentFile):
        newDeploymentFile = os.path.join(self.tmpFolder, "new_deployment.xml")

        deploymentFileContent = open(deploymentFile).read()
            
        adobeHome = os.path.normpath(os.path.join(os.getenv("ProgramFiles") + "/Adobe"))

        newDeploymentFileContent = re.sub(r'(.*INSTALLDIR">)[^<.]*(</Property>.*)', r'\1%s\2' % adobeHome, deploymentFileContent)
                
        self._writeDeploymentXML(newDeploymentFile, newDeploymentFileContent)
        
        return newDeploymentFile
    
    def silentActivation (self):
        if os.path.exists(self.provisioningToolLocation):
            self._rmtree(self.provisioningToolLocation)
        if os.name == 'posix':
            self.silentActivationMac()
        elif os.name == 'nt':
            self.silentActivationWin()
        if os.path.exists(self.provisioningToolLocation):
            self._rmtree(self.provisioningToolLocation)
    
    def silentActivationMac (self):   
        if  globalProperty.isMachineOutOfChina():
            toolLocation = self._dbutil.getAppInfo('provisioning_tool_mac_us').strip()
        else:
            toolLocation = self._dbutil.getAppInfo('provisioning_tool_mac_cn').strip()
            
        if toolLocation==None or toolLocation=="":
            raise "Silent Activationg Tool Failed"
        else:
            self.getSilentActivationTool(toolLocation)
            
        toolPath = os.path.join(self.provisioningToolLocation, 'adobe_provisioning_tool.app/Contents/MacOS/adobe_provisioning_tool')
        sn = self._dbutil.getAppInfo('SN_mac').strip()
        self.logger.debug('SN_mac: ' + sn)
        cmd = 'chmod +x ' + toolPath  
        self.logger.info('Cmd: '+cmd) 
        r = os.system(cmd)
        if r != 0:
            raise Exception('chmod returned abnormally, code: %d' % r)
            
        cmd = toolPath + ' -s "'+sn+'" -C -a /Library/Application\ Support/Adobe/Adobe\ Photoshop\ CS6/AMT_Driver'  
        r = os.system(cmd)
        if r != 0:
            raise Exception('Do silent activation returned abnormally, code: %d' % r)
        
    def silentActivationWin (self):      
        if  globalProperty.isMachineOutOfChina():
            toolLocation = self._dbutil.getAppInfo('provisioning_tool_win_us').strip()
        else:
            toolLocation = self._dbutil.getAppInfo('provisioning_tool_win_cn').strip()
            
        if toolLocation==None or toolLocation=="":
            raise "Silent Activationg Tool Failed"
        else:
            self.getSilentActivationTool(toolLocation)
            
        toolPath = os.path.join(self.provisioningToolLocation, 'adobe_provisioning_tool.exe')
        sn = self._dbutil.getAppInfo('SN_win').strip()
        self.logger.debug('SN_win: ' + sn)
        programfileX86 = os.getenv("ProgramFiles(x86)")
        if programfileX86:
            cmd = toolPath + ' -s "'+sn+'" -C -a "%CommonProgramFiles(x86)%\Adobe\Adobe Photoshop CS6\AMT_Driver"'
            r = os.system(cmd)
            if r != 0:
                raise Exception('Do silent activation returned abnormally, code: %d' % r)
        cmd = toolPath + ' -s "'+sn+'" -C -a "%CommonProgramFiles%\Adobe\Adobe Photoshop CS6\AMT_Driver"'  
        r = os.system(cmd)
        if r != 0:
            raise Exception('Do silent activation returned abnormally, code: %d' % r)
        
    def getSilentActivationTool (self,toolLocation):
        fullPath = toolLocation[6:]
        parts = fullPath.split('/', 1)
                        
        (host, location) = parts
        from FTPTask import childTask
        task = childTask('task')
                        
         #FIXME: Modified by Jacky
        task.addPara('Host', host)
        task.addPara('User', self._commonDomain + "\\" + self._commonUser)
        task.addPara('Passwd', self._commonPassword)
                        
        if not location.startswith('/'):
            location = '/' + location
                    
        #Attention: For OSImage, here must be FolderPath other than FilePath
        if not os.path.exists(self.provisioningToolLocation):
            os.makedirs(self.provisioningToolLocation)
        task.addPara('Repository', self.provisioningToolLocation) 
        task.addPara('FolderPath', location)
        task.run()                            
                                 
    def makeBackDoorFile(self, version):
        destPath = None
        destPath2 = None 
        destPath3 = None
        destPath4 = None
        if os.name == 'posix':
            if re.match('^13.\d+.*', version):
                destPath = os.path.join("/Applications", 'Adobe Photoshop CS6/Adobe Photoshop CS6.app/Contents/MacOS')
                destPath3 = os.path.join("/Applications", 'Adobe Photoshop CS6/Locales')
            elif re.match('^12.1.*', version):
                destPath = os.path.join("/Applications", 'Adobe Photoshop CS5.1/Adobe Photoshop CS5.1.app/Contents/MacOS')
            elif re.match('^12.\d+.*', version):
                destPath = os.path.join("/Applications", 'Adobe Photoshop CS5/Adobe Photoshop CS5.app/Contents/MacOS')
            elif re.match('^11.\d+.*', version):
                destPath = os.path.join("/Applications", 'Adobe Photoshop CS4/Adobe Photoshop CS4.app/Contents/MacOS')
        elif os.name == 'nt':
            programfile = os.getenv("ProgramFiles")
            programfileX86 = os.getenv("ProgramFiles(x86)")
            if programfileX86:
                programfile = re.sub("(.*)\s+\(x86\)", r"\1", programfile)
            psRelativePath = None
            if re.match('^13.\d+.*', version):
                psRelativePath = "Adobe/Adobe Photoshop CS6"
            elif re.match('^12.1.*', version):
                psRelativePath = "Adobe/Adobe Photoshop CS5.1"
            elif re.match('^12.\d+.*', version):
                psRelativePath = "Adobe/Adobe Photoshop CS5"
            elif re.match('^11.\d+.*', version):
                psRelativePath = "Adobe/Adobe Photoshop CS4"
            
            if psRelativePath==None:
                return
            
            folderAppendix = ""
            zSringPath = "Locales/"
            if programfileX86:#Must be 64 bit os
                destPath = os.path.join(programfile, psRelativePath + " (64 Bit)")
                destPath2 = os.path.join(programfileX86, psRelativePath)
                destPath3 = os.path.join(destPath, zSringPath)
                destPath4 = os.path.join(destPath2, zSringPath)
            else: #for Windows XP
                destPath = os.path.join(programfile, psRelativePath)
                destPath3 = os.path.join(destPath, zSringPath)
              
        if destPath!=None and os.path.exists(destPath):
            backDoorFile1 = os.path.join(destPath, "APIPDisableAutoDialog.YES")
            if not os.path.exists(backDoorFile1):
                self.creatFile(backDoorFile1, "place holder..")
        if destPath2!=None and os.path.exists(destPath2):
            backDoorFile2 = os.path.join(destPath2, "APIPDisableAutoDialog.YES")
            if not os.path.exists(backDoorFile2):
                self.creatFile(backDoorFile2, "place holder..")
                
        #for zstring in tw10428.dat 
        if 'zstring' in self.parameter and self.parameter['zstring'].strip() == "true":       
            if destPath3!=None and os.path.exists(destPath3):
                self.installZStringFile(destPath3)
            if destPath4!=None and os.path.exists(destPath4):
                self.installZStringFile(destPath4)
           
    def installZStringFile(self, destPath):
        dirs = os.listdir(destPath)
        for dir in dirs:
            targetPath = os.path.join(destPath, dir+"/Support Files/")
            if(os.path.exists(targetPath)):
                backDoorFile = os.path.join(targetPath, "tw10428.dat")
                bdfExist = os.path.exists(backDoorFile)
                f = open(backDoorFile, "ab")
                if bdfExist:
                    f.write("\"$$$/private/onlineservices/title=whatever\"\r\n".encode("UTF-16-LE"))
                else:
                    f.write("\"$$$/private/onlineservices/title=whatever\"\r\n".encode("UTF-16"))
                f.close()
    
    def installSampleFile(self, version):
        self.logger.debug('Install Photoshop Sample Files')   
        destPath = None
        destPath2 = None 
        if os.name == 'posix':
            if re.match('^13.\d+.*', version):
                destPath = os.path.join("/Applications", 'Adobe Photoshop CS6')
            elif re.match('^12.1.*', version):
                destPath = os.path.join("/Applications", 'Adobe Photoshop CS5.1')
            elif re.match('^12.\d+.*', version):
                destPath = os.path.join("/Applications", 'Adobe Photoshop CS5')
        elif os.name == 'nt':
            programfile = os.getenv("ProgramFiles")
            programfileX86 = os.getenv("ProgramFiles(x86)")
            if programfileX86:
                programfile = re.sub("(.*)\s+\(x86\)", r"\1", programfile)
            psRelativePath = None
            if re.match('^13.\d+.*', version):
                psRelativePath = "Adobe/Adobe Photoshop CS6"
            elif re.match('^12.1.*', version):
                psRelativePath = "Adobe/Adobe Photoshop CS5.1"
            elif re.match('^12.\d+.*', version):
                psRelativePath = "Adobe/Adobe Photoshop CS5"
            
            if psRelativePath==None:
                return
            
            folderAppendix = ""
            if programfileX86:#Must be 64 bit os
                destPath = os.path.join(programfile, psRelativePath + " (64 Bit)")
                destPath2 = os.path.join(programfileX86, psRelativePath)
            else: #for Windows XP
                destPath = os.path.join(programfile, psRelativePath)
           
        if 'appLang' in self.parameter:
            locale = self.parameter['appLang'].strip()
        else:
            locale = 'en_US'                
        self.getSamples(locale)        
        filepath = os.path.join( self.samplesLocation,locale+'.zip')
        self._unzipfileBy7zip(filepath,self.samplesLocation)
        fileFolder = os.path.join(self.samplesLocation, locale)
        
        if(os.path.exists(filepath)):
            if destPath!=None and os.path.exists(destPath):
                self.copySamples(fileFolder,destPath) 
            if destPath2!=None and os.path.exists(destPath2):
                self.copySamples(fileFolder,destPath2) 
        self._rmtree(self.samplesLocation)

    def getSamples (self,locale):
        samplesLocation = self._dbutil.getAppInfo('samples').strip()
        if samplesLocation==None or samplesLocation=="":
            raise "Samples Failed"
        fileLocation = samplesLocation + '/' + locale+'.zip'           
        fullPath = fileLocation[6:]
        parts = fullPath.split('/', 1)
                        
        (host, location) = parts
        if not location.startswith('/'):
            location = '/' + location
            
        from FTPTask import childTask
        task = childTask('task')
        task.addPara('Host', host)
        task.addPara('User', self._commonDomain + "\\" + self._commonUser)
        task.addPara('Passwd', self._commonPassword)          
        if not os.path.exists(self.samplesLocation):
            os.makedirs(self.samplesLocation)            
        task.addPara('Repository', self.samplesLocation) 
        task.addPara('FilePath', location)
        task.addPara('OneFile', 'True')
        task.run()    
    
    def copySamples (self,src,dst):
        self.logger.debug('Copy samples %s to %s', src, dst)
        names = os.listdir(src)
        for name in names:
            src1=os.path.join(src,name)
            dst1=os.path.join(dst,name)
            if not os.path.exists(dst1):
                shutil.copytree(src1,dst1)
                
    #Added by nlei
    #This is for install last good known CRC plugin
    def installSpecialPlugIn(self):        
        self.logger.debug('Install Special Photoshop PlugIn')
        plugInLocation = self._dbutil.getAppInfo("Plugin_path")
        if os.name == 'posix':
            folderPattern = "osx10"
        elif os.name == 'nt':
            windowsversion = sys.getwindowsversion()
            if self.processorArc == "x86":
                folderPattern = "win32"
            else:
                folderPattern = "(win32|win64)" 
        self.logger.debug('Special Photoshop PlugIn Path is %s', plugInLocation)
        
        if re.match('^ftp:', plugInLocation.lower()):         
            task = FTPTask.childTask('task')
            task.addPara('FolderPattern', folderPattern)
            if re.match('.*@.*', plugInLocation):
                host = re.sub(r'^.*@([^/]*)/.*', r'\1', plugInLocation)
                task.addPara('Host', host)
                username = re.sub(r'^ftp://(.*):.*@([^/]*)/.*', r'\1', plugInLocation)
                password = re.sub(r'^.*:(.*)@([^/]*)/.*', r'\1', plugInLocation)
                task.addPara('User', username)
                task.addPara('Passwd', password)
            else:
                host = re.sub(r'^ftp://([^/]*)/.*', r'\1', plugInLocation)
                task.addPara('Host', host)
                task.addPara('User', self._commonDomain + '\\' + self._commonUser)
                task.addPara('Passwd', self._commonPassword)
            
            plugInLocation = re.sub(r'^[^/]*(/.*)', r'\1', plugInLocation[6:])
            task.addPara('FolderPath', plugInLocation)
            
            task.addPara('pattern', '.*Plug-Ins.*')
            #task.addPara('OneFile', 'True')
        else:
            from SambaTask import childTask
            task = childTask('task')
            task.addPara('sambaDomain', self._commonDomain)
            task.addPara('sambaUser', self._commonUser)
            task.addPara('sambaPsw', self._commonPassword)
            if 'appLang' in self.parameter:
                task.addPara('appLang', self.parameter['appLang'])
            task.addPara('FolderPath', plugInLocation)
            task.addPara('filterStr', '.*Plug-Ins.*')
        
        #Change downloadFolder to avoid collision with other Product

        task.addPara('Repository', self.downloadFolder)

        task.run()
        
        if os.name == 'posix':
            self.installMacPlugIn()
        else:
            self.installWinPlugIn()
            
    def killRelativeProcess(self):
        self.__killProcess("Photoshop")
        self.__killProcess("Bridge")
        self.__killProcess("ExtendScript")
    
    def __killProcess(self, exefileName):
        try:
            from KillTask import childTask
            task = childTask('killTask')
            task.addPara("exefileName", exefileName)
            task.run()
        except Exception, e:
            pass
    
    #Overriden this function due to debug build affection
    def _backUpUnDeploymentFile(self):        
        _unDeploymentFileContent = open(self.unDeploymentFile).read()
        
        unDeploymentFileContent = _unDeploymentFileContent.replace("install", "remove")
        
        unDeploymentFile = self._getUnDeploymentFile()
        
        self._writeDeploymentXML(unDeploymentFile, unDeploymentFileContent)
        
        buildInfoFileContent = self.buildNum
        
        if self.compileTarget=="Debug":
            buildInfoFileContent += "db"
        
        buildInfoFile = self._getBuildInfoFile()
        self.creatFile(buildInfoFile, buildInfoFileContent)
        
    def prepareAppPanel(self, appPanelFolder, version):
        destFolder = []
        if os.name == 'nt':
            programfile = os.getenv("ProgramFiles")
            programfileX86 = os.getenv("ProgramFiles(x86)")
            if programfileX86:
                programfile = re.sub("(.*)\s+\(x86\)", r"\1", programfile)
                if re.match('^13.\d+.*', version):
                    destPath32 = os.path.join(programfileX86, "Adobe", 'Adobe Photoshop CS6', 'Plug-ins', 'Panels')
                    destPath64 = os.path.join(programfile, "Adobe", 'Adobe Photoshop CS6 (64 Bit)', 'Plug-ins', 'Panels')
                elif re.match('^12.1.*', version):
                    destPath32 = os.path.join(programfileX86, "Adobe", 'Adobe Photoshop CS5.1', 'Plug-ins', 'Panels')
                    destPath64 = os.path.join(programfile, "Adobe", 'Adobe Photoshop CS5.1 (64 Bit)', 'Plug-ins', 'Panels')
                elif re.match('^12.\d+.*', version):
                    destPath32 = os.path.join(programfileX86, "Adobe", 'Adobe Photoshop CS5', 'Plug-ins', 'Panels')
                    destPath64 = os.path.join(programfile, "Adobe", 'Adobe Photoshop CS5 (64 Bit)', 'Plug-ins', 'Panels')
                elif re.match('^11.\d+.*', version):
                    destPath32 = os.path.join(programfileX86, "Adobe", 'Adobe Photoshop CS4', 'Plug-ins', 'Panels')
                    destPath64 = os.path.join(programfile, "Adobe", 'Adobe Photoshop CS4 (64 Bit)', 'Plug-ins', 'Panels')
                else:
                    raise "This version of Photoshop is not supported by current task"
                destFolder.append(destPath32)
                destFolder.append(destPath64)
            else:
                if re.match('^13.\d+.*', version):
                    destPath = os.path.join(programfile, "Adobe", 'Adobe Photoshop CS6', 'Plug-ins', 'Panels')
                elif re.match('^12.1.*', version):
                    destPath = os.path.join(programfile, "Adobe", 'Adobe Photoshop CS5.1', 'Plug-ins', 'Panels')
                elif re.match('^12.\d+.*', version):
                    destPath = os.path.join(programfile, "Adobe", 'Adobe Photoshop CS5', 'Plug-ins', 'Panels')
                elif re.match('^11.\d+.*', version):
                    destPath = os.path.join(programfile, "Adobe", 'Adobe Photoshop CS5', 'Plug-ins', 'Panels')
                else:
                    raise "This version of Photoshop is not supported by current task"
                destFolder.append(destPath)
        elif os.name == 'posix':
            if re.match('^13.\d+.*', version):
                destPath = os.path.join("/Applications", 'Adobe Photoshop CS6', 'Plug-ins', 'Panels')
            elif re.match('^12.1.*', version):
                destPath = os.path.join("/Applications", 'Adobe Photoshop CS5.1', 'Plug-ins', 'Panels')
            elif re.match('^12.\d+.*', version):
                destPath = os.path.join("/Applications", 'Adobe Photoshop CS5', 'Plug-ins', 'Panels')
            else:
                raise "This version of Photoshop is not supported by current task"
            destFolder.append(destPath)
        
        for destPath in destFolder:
            for appPanel in os.listdir(appPanelFolder):
                srcAppPanelPath = os.path.join(appPanelFolder, appPanel)
                destAppPanelPath = os.path.join(destPath, appPanel)
                if not os.path.exists(destAppPanelPath):
                    shutil.copytree(srcAppPanelPath, destAppPanelPath)

##################This section is mainly for debug -- Begin #############################
if __name__ == '__main__':    
    
    task = childTask('PhotoshopInstall', 1)
    task.addPara('installerType', 'RIBS')
    task.addPara('appName', 'Photoshop')
    task.addPara('appVer', '13.0')
    task.addPara('appLang', 'en_US')
    task.addPara('appCertLevel', 'Build Failed')
    task.addPara('appPlatform', 'win32')
    task.addPara('appSubProduct', 'Application')
    
    task.compileTarget = "Release"
    #task.addPara('molecule', 'psl2')
    #task.installSpecialPlugIn()
    #task.getSymbol()
    #task.installSymbol()
    #task.makeBackDoorFile("13.0")
    #task.installSampleFile('13.0');
    task.installZStringFile("D:\\qmsTest")
    #task.run()
    #deploymentFile = "D:\\test\\deployment.xml"
    #task._generateDeploymentFile(deploymentFile)

##################This section is mainly for debug -- End #############################
