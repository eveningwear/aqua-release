"""

    RestoreOS.py
    
    Written by: Jacky Li (yxli@adobe.com)
    Written by: Alon Ao (alonao@adobe.com)

"""

from allTasks.baseTask import Task
import os, os.path, re, time, machine, sys

import globalProperty

class childTask(Task):
    
    def __init__(self, type, priority):
        super(childTask, self).__init__(type, priority)
        self.imageRepository = os.path.join(os.getcwd(), 'OSImage')
        self.createImageFlag = False
            
        if(not os.path.exists(self.imageRepository)):
            os.mkdir(self.imageRepository)
        return
    
    def run(self):
        self.logger.info('Starting getting OSImage before restoring OS')
        if 'CreateImage' in self.parameter and self.parameter['CreateImage'] == 'Yes' and os.name == 'nt':
            self.createImageFlag = True
        self.__getOSImage()
        self.logger.info('Starting restoring OS')
            
        super(childTask, self).run()
    
    def macGetUniqePartiotionName(self, name):
        import random
        rint = random.randint(1, 999)
        oldPartitions = set(machine.getMacPartitions())
        newName = name + str(rint)
        if newName in oldPartitions:
            return self.macGetUniqePartiotionName(name)
        else:
            return newName
        
    def macRenamePartition(self, oldName):
        os.system("diskutil rename '/Volumes/%s' '%s'" % (oldName, self.macGetUniqePartiotionName(oldName)))
        return
    
    def restoreMacImage(self, target, imagePath):
        '''
        cmd.append(os.path.normpath(os.getcwd() + '/tools/restore.sh ' + volumneName + ' ' +  imagePath))
        oldPartitions = set(machine.getMacPartitions())
        #rename old partition if possible
        newPartitionName = os.path.basename(self.parameter['OSImagelocation'])
        #Since the restored partition's name will be replaced by a new name in the image file, we suppose the new partition name is same with the image file name.
        newPartitionName = os.path.splitext(os.path.split(imagePath)[1])[0]
        if not target == newPartitionName:
            if newPartitionName in oldPartitions:
                self.macRenamePartition(newPartitionName)
                # re-get the new partition info
                oldPartitions = set(machine.getMacPartitions())
        '''
        info = machine.getVolumeInfo(target)
        disk = info['DeviceNode']   #DeviceIdentifier seems ok, too
        
        self.logger.debug('start restore')
        disk = re.sub(r'^/dev/(.*)', r'\1', disk)
        cmd = "sudo asr restore -s '%s' -t /dev/%s -noprompt -noverify -erase" % (imagePath, disk)
        self.logger.debug(cmd)
        outstr = self.runCommand(cmd)
                
        if re.search('timed out', outstr)!=None:
            self.logger.debug("Try to restore again due to time out issue")
            time.sleep(2)
            outstr = self.runCommand(cmd)
            if re.search('timed out', outstr)!=None:
                raise Exception(outstr)
        
        #using os.system puts output on console, while subprocess can assign it to a variable
        #we need to log, so the latter. better solution?
        #os.system(cmd)
        self.logger.debug(outstr)
        
        #rename to original volume name
        self.logger.debug("Try to rename disk %s to '%s'" %(disk, target))
        cmd = "sudo diskutil rename /dev/%s '%s'" % (disk, target)
        self.logger.debug(cmd)
        outstr = self.runCommand(cmd)
        self.logger.debug(outstr)
        if re.search('Error', outstr)!=None:
            self.logger.debug("Try to rename disk again due to Error")
            time.sleep(2)
            outstr = self.runCommand(cmd)
            if re.search('Error', outstr)!=None:
                raise Exception(outstr)
        
        #cmd = "sudo diskutil repairvolume /Volumes/%s" % (target)
        #self.runCommand(cmd)
        
        #cmd = "sudo diskutil repairPermissions /Volumes/%s" % (target)
        #self.runCommand(cmd)

        '''
        newPartitions = set(machine.getMacPartitions())
        
        rebootVolumeName = None
        for p in newPartitions:
            if p not in oldPartitions:
                rebootVolumeName = p
                break
        
        if not rebootVolumeName:
            rebootVolumeName = target
        '''
        
        self.logger.debug('start bless mount')
        time.sleep(2)
        cmd = 'sudo bless --mount "/Volumes/%s" --setBoot' % (target)
        self.logger.debug(cmd)
        outstr = self.runCommand(cmd)
        self.logger.debug(outstr)
        
        self.logger.debug('start reboot')
        cmd = 'sudo reboot'
        self.logger.debug(cmd)
        time.sleep(1)
        outstr = self.runCommand(cmd)
        self.logger.debug(outstr)
        
    def runMac(self):
        self.logger.debug('RestoreOS runMac')
        self.logger.debug(self.__downloadedFileList)
        target1 = self.parameter['targetPartition1']
        target2 = self.parameter['targetPartition2']
        sysVol = machine.getSysVol()
        target = target2 if sysVol == target1 else target1
        
        imagePath = self.__downloadedFileList[0]
        self.logger.debug('The target ' + target + ' will be restored by image ' + imagePath)
        self.restoreMacImage(target, imagePath)
        time.sleep(8888)#bucause the system will restart, just let it halt, so it can't perform following task.
        return
        
    def runWin(self):
        self.logger.debug('RestoreOS runWin')
        if not self.createImageFlag:
            self.logger.debug(self.__downloadedFileList)
        self.__oemPartition = False
        self.__getLabPETool()
        #self.__getDiskInfo()
        self.__generateSwitchFile()
        cmd = []
        if not os.path.exists(self.__LabPEToolPath):
            raise "LabPETool is lost"
        cmd.append(self.__LabPEToolPath)
        #Attention: Following sentence is high dangerous which may cause destructive damning destruction
        
        self.runCommand(cmd)
        #time.sleep(888)#bucause the system will restart, just let it halt, so it can't perform following task.
        sys.exit(0)
        return
    
    def __getLabPETool(self):
        '''
        This Function is for Windows Only
        Hardcode temporarily
        '''
        LabPEToolName = self._dbutil.getAppInfo('labpe_tool_name').strip()
        if LabPEToolName==None:
            LabPEToolName = "LabPE_4.2_Ramdisk.exe"
            
        self.__LabPEToolPath = os.path.join(self.getToolsDir(), LabPEToolName)
        if os.path.exists(self.__LabPEToolPath):
            return
        
        if globalProperty.isMachineOutOfChina():
            labPEToolLocation = self._dbutil.getAppInfo('labpe_us').strip()
        else:
            labPEToolLocation = self._dbutil.getAppInfo('labpe_cn').strip()
        if labPEToolLocation==None or labPEToolLocation=="":
            raise "Donwload LabPE Tool Failed"
        elif labPEToolLocation.startswith('ftp://'):
            labPEToolLocation += '/' + LabPEToolName
            fullPath = labPEToolLocation[6:]
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
        else:
            labPEToolLocation += '/' + LabPEToolName
            from SambaTask import childTask
            task = childTask('task')
            if not 'sambaDomain' in self.parameter or \
                not 'sambaUser' in self.parameter or \
                not 'sambaPsw' in self.parameter:
                task.addPara('sambaDomain', self._commonDomain)
                task.addPara('sambaUser', self._commonUser)
                task.addPara('sambaPsw', self._commonPassword)
            else:
                task.addPara('sambaDomain', self.parameter['sambaDomain'])
                task.addPara('sambaUser', self.parameter['sambaUser'])
                task.addPara('sambaPsw', self.parameter['sambaPsw'])
                
            locationForSamba = re.sub(r'^/*(.*)', r'\1', labPEToolLocation.replace("\\", "/"))
                
            task.addPara('FilePath', locationForSamba)
            task.targetFolder = self.getToolsDir() 
            task.run()
    
    def __generateSwitchFile(self):
        '''
        This Function is for Windows Only
        '''
        cwd = os.getcwd()
        qmsImageCmdName = ":\qmsimage.cmd"
        qmsImageCmdFile = cwd[0]+qmsImageCmdName
        self.logger.debug('generate switch file')
        switchesFile = 'C:\\petask.cmd'
        disk = None
        if self.createImageFlag:
            imageFileFullPath = self.parameter['OSImageLocation'][7:]
        else:
            for imageFileFullPath in self.__downloadedFileList:
                if re.match('.*\.gho$', imageFileFullPath.strip().lower()):
                    disk = imageFileFullPath[:2]
                    self.logger.info('The target partition will be restored by the image ' + imageFileFullPath)
                    break
            if not disk:
                raise 'The image could not be found'


#        if self.__diskDic[disk.split(':')[0].upper()][5] != 'Healthy':
##            raise 'The repository disk ' + disk + ' containing image is not healthy which will cause dangerous operations'
#            self.logger.info('The repository disk ' + disk + ' containing image is not healthy which will cause dangerous operations')
##        if self.__diskDic[self.__firstPart][5] != 'Healthy':
##            raise 'The target-restored disk ' + self.__firstPart + ': is not healthy which will cause dangerous operations'
#        if self.__diskDic[disk.split(':')[0].upper()][0] == '1:1':
#            raise 'The target-restored disk should not be the repository one containing disk image'
#        
#        PartIdForDos = self.__getPartIdForDos(self.__getPartNum(disk))
#        srcFilePath = re.sub(r'.:(.*)', PartIdForDos + r':\1', imageFileFullPath)

        srcFilePath = imageFileFullPath[1:]

        (systemDiskId, partitionNum) = self.__getSysPartitionId()
        
        if systemDiskId == None or partitionNum == None:
            raise 'The System Disk could not be found'
        
        switchContent = '''@echo off
set qmsimageFile=:\qmsimage.cmd
for %%i in (C D E F G H I) do (
    if EXIST "%%i%qmsimageFile%" (
        if EXIST "%%i%qmsimageFile%" start %%i%qmsimageFile%
        goto :FINDQMSIMAGEFILE
    )
)
:FINDQMSIMAGEFILE
:END
'''
        self.__generateFile(switchesFile, switchContent)

        qmsImageCmdFileContent = '''@echo off
set petaskFile=:\petask.cmd
for %%i in (C D E F G H I) do (
    if EXIST "%%i%petaskFile%" (
        set petaskFilePath="%%i%petaskFile%"
        goto :FINDPETASKFILE
    )
)
goto :END
:FINDPETASKFILE
set QMSClienHome=:\QMSClient
set imageFile=''' + srcFilePath + '''
set systemDiskId=''' + systemDiskId + '''
set partitionId=''' + str(partitionNum) + '''
for %%i in (C D E F G H I) do ('''
        if self.createImageFlag:
            qmsImageCmdFileContent +=''' 
    if EXIST "%%i%QMSClienHome%" ('''
        else:
            qmsImageCmdFileContent +=''' 
    if EXIST "%%i%imageFile%" ('''
        qmsImageCmdFileContent +='''
        set imageFileFound=%%i%imageFile%
        set diskUsed=%%i
        goto :FINDSYSDISK
    )
)
goto :IMAGENOTFOUND
:FINDSYSDISK
rem I support 4 Disks in Maximum
for %%j in (0,1,2,3) do (
    echo select disk %%j> "%diskUsed%:\\diskInfoGet.bat"
    echo detail disk>>"%diskUsed%:\\diskInfoGet.bat"
    echo list partition>>"%diskUsed%:\\diskInfoGet.bat"
    diskpart /s "%diskUsed%:\\diskInfoGet.bat" > "%diskUsed%:\\result.txt"
    for /F "eol=; tokens=3 delims= " %%k in (%diskUsed%:\\result.txt) do (
        if "%%k"=="%systemDiskId%" (
            set /A diskRestoredOrder=%%j+1
            if EXIST %diskUsed%:\\diskInfoGet.bat del %diskUsed%:\\diskInfoGet.bat
            if EXIST %diskUsed%:\\result.txt del %diskUsed%:\\result.txt
            goto :RESTORE
        )
    )
)
if EXIST %diskUsed%:\\diskInfoGet.bat del %diskUsed%:\\diskInfoGet.bat
if EXIST %diskUsed%:\\result.txt del %diskUsed%:\\result.txt
goto :SYSTEMDISKNOTFOUND
:IMAGENOTFOUND
echo [Error]Image File is not found...
goto :END
:SYSTEMDISKNOTFOUND
echo [Error]System Disk is not found...
goto :END
:RESTORE
echo %imageFileFound% is found and will start restoring'''
        if self.createImageFlag:
            qmsImageCmdFileContent += '''
if EXIST %petaskFilePath% del "%petaskFilePath%"'''
            if 'RestoreToDisk' in self.parameter and self.parameter['RestoreToDisk'] == 'Yes':
                qmsImageCmdFileContent += '''
ghost32.exe -clone,mode=pcreate,src=%diskRestoredOrder%,dst="%imageFileFound%" -fx -sure -rb'''
            else:
                qmsImageCmdFileContent += '''
ghost32.exe -clone,mode=pcreate,src=%diskRestoredOrder%:%partitionId%,dst="%imageFileFound%" -fx -sure -rb'''
            qmsImageCmdFileContent += '''
echo @echo off> "%petaskFilePath%"
echo set qmsimageFile=:\qmsimage.cmd> "%petaskFilePath%"
echo for %%%%i in (C D E F G H I) do (>> "%petaskFilePath%"
echo     if EXIST "%%%%i%%qmsimageFile%%" (>> "%petaskFilePath%"
echo         del "%%%%i%%qmsimageFile%%">> "%petaskFilePath%"
echo         goto :END>> "%petaskFilePath%"
echo     )>> "%petaskFilePath%"
echo )>> "%petaskFilePath%"
echo :END>> "%petaskFilePath%"
echo wpeutil reboot>> "%petaskFilePath%"'''
        else:
            qmsImageCmdFileContent += '''
if EXIST %petaskFilePath% del "%petaskFilePath%"'''
            if 'RestoreToDisk' in self.parameter and self.parameter['RestoreToDisk'] == 'Yes':
                qmsImageCmdFileContent += '''
ghost32.exe -clone,mode=restore,src="%imageFileFound%",dst=%diskRestoredOrder% -fx -sure -rb'''
            else:
                qmsImageCmdFileContent += '''
ghost32.exe -clone,mode=prestore,src="%imageFileFound%":1,dst=%diskRestoredOrder%:%partitionId% -fx -sure -rb'''
            qmsImageCmdFileContent += '''
echo @echo off> "%petaskFilePath%"
echo wpeutil reboot>> "%petaskFilePath%"'''
                
        qmsImageCmdFileContent += '''
goto :END
:END
start %petaskFilePath%
wpeutil reboot'''

        #stream = 'ghost32.exe -clone,mode=prestore,src=' + srcFilePath + ':1,dst=' + self.__getSysPartitionId() + '  -fx -sure -rb'
        #self.logger.info(stream)
        
#        fat32PartCForDos = self.__getFirstFat32PartId()
#        switchesFileFullPath = os.path.normpath(os.path.join(fat32PartCForDos + '://', switchesFile))
        self.__generateFile(qmsImageCmdFile, qmsImageCmdFileContent)
    
    def __getOSImage(self):
        if self.createImageFlag:
            return
        self.logger.debug("getOSImage")
        if self.parameter.has_key("CleanOSImage") and self.parameter['CleanOSImage'] == 'Yes':
            try:
                if (os.path.exists(self.imageRepository)):
                    shutil.rmtree(self.imageRepository)
                    os.mkdir(self.imageRepository)
            except WindowsError, (errno,strerror):
                self.logger.error("Cleanup error(%s): %s" % (errno,strerror))
        if self.parameter.has_key('OSImageLocation'):
            osImageLocation = self.parameter['OSImageLocation']
            self.__getOSImageByLocation(osImageLocation)
        else:
            model = self.parameter['OSModel']
            osType = self.parameter['OSType']
            osEdition = self.parameter['OSEdition']
            osLang = self.parameter['OSLang']
            osImageLocation = self._dbutil.getMachineImage(model, osType, osEdition, osLang)
            self.__getOSImageByLocation(osImageLocation)
        '''
        self.logger.debug("getOSImage")
        if self.parameter.has_key('sambaDomain'):
            if self.parameter['OSImagelocation'].startswith('file://'):
                fullPath = self.parameter['OSImagelocation'][7:]
                if self.parameter['sourceOS'] != 'Windows' and not fullPath.startswith('/'):
                    fullPath = '/' + fullPath
                self.__downloadedFileList = [fullPath]    #remove file://
                return
            #elif not self.parameter['OSImagelocation'] is None:
            #    raise Exception('Please check your OS Image Location')
            elif not self.parameter['OSImagelocation'] is None:
                from SambaTask import childTask
                task = childTask('task')
                task.addPara('sambaDomain', self.parameter['sambaDomain'])
                task.addPara('sambaUser', self.parameter['sambaUser'])
                task.addPara('sambaPsw', self.parameter['sambaPsw'])
                
                OSImagelocationForSamba = re.sub(r'^/*(.*)', r'\1', self.parameter['OSImagelocation'].replace("\\", "/"))
                
                task.addPara('FolderPath', OSImagelocationForSamba)
                task.targetFolder = self.imageRepository 
                task.run()
                self.__downloadedFileList = task.getDownloadList()
                return
            else:
                raise Exception('Please check your OS Image Location')
        else:
            from FTPTask import childTask
            task = childTask('task')
            
            #FIXME: Modified by Jacky
            task.addPara('Host', self.parameter['OSImageHost'])
            task.addPara('User', self.parameter['OSImageUser'])
            task.addPara('Passwd', self.parameter['OSImagePasswd'])
        
            #Attention: For OSImage, here must be FolderPath other than FilePath
            task.addPara('Repository', self.imageRepository) 
            task.addPara('FolderPath', self.parameter['OSImagelocation'])
            task.run()
            self.__downloadedFileList = task.getDownloadList()
            return
        '''
    
    def __getOSImageByLocation(self, imageLocation):
        self.logger.debug("Get image from " + imageLocation)
        if imageLocation==None or imageLocation=="":
            return
        elif imageLocation.startswith('ftp://'):
            from FTPTask import childTask
            task = childTask('task')
            if re.match('.*@.*', imageLocation):
                host = re.sub(r'^.*@([^/]*)/.*', r'\1', imageLocation)
                task.addPara('Host', host)
                username = re.sub(r'^ftp://(.*):.*@([^/]*)/.*', r'\1', imageLocation)
                password = re.sub(r'^.*:(.*)@([^/]*)/.*', r'\1', imageLocation)
                task.addPara('User', username)
                task.addPara('Passwd', password)
            else:
                host = re.sub(r'^ftp://([^/]*)/.*', r'\1', imageLocation)
                task.addPara('Host', host)
                task.addPara('User', self._commonDomain + '\\' + self._commonUser)
                task.addPara('Passwd', self._commonPassword)
            
            imageLocation = re.sub(r'^[^/]*(/.*)', r'\1', imageLocation[6:])
            if re.match('.*/$', imageLocation):
                #Delete ftp://                
                task.addPara('FolderPath', imageLocation)
            else:
                task.addPara('FilePath', imageLocation)
                
            task.addPara('Repository', self.imageRepository) 
            task.run()
            self.__downloadedFileList = task.getDownloadList()
        elif imageLocation.startswith('file://') or imageLocation.startswith('file:\\'):            
            fullPath = imageLocation[7:]
            if os.path.exists(fullPath) and os.path.isdir(fullPath):
                self.__downloadedFileList = self._getFileList(fullPath)
            elif os.path.exists(fullPath) and os.path.isfile(fullPath):
                self.__downloadedFileList = [fullPath]
            else:
                self.__getOSImageByLocation(fullPath)
        else:
            from SambaTask import childTask
            task = childTask('task')
            if not 'sambaDomain' in self.parameter or \
                not 'sambaUser' in self.parameter or \
                not 'sambaPsw' in self.parameter:
                task.addPara('sambaDomain', self._commonDomain)
                task.addPara('sambaUser', self._commonUser)
                task.addPara('sambaPsw', self._commonPassword)
            else:
                task.addPara('sambaDomain', self.parameter['sambaDomain'])
                task.addPara('sambaUser', self.parameter['sambaUser'])
                task.addPara('sambaPsw', self.parameter['sambaPsw'])
                
            OSImagelocationForSamba = re.sub(r'^/*(.*)', r'\1', imageLocation.replace("\\", "/"))
                
            task.addPara('FolderPath', OSImagelocationForSamba)
            task.targetFolder = self.imageRepository 
            task.run()
            self.__downloadedFileList = task.getDownloadList()
            return
        
    def _getFileList(self, parent):
        fileList = []
        for root, dirs, files in os.walk(parent):
            for filename in files:
                filePath = os.path.join(root, filename)
                fileList.append(filePath)
            for dirname in dirs:
                filePath = os.path.join(root, dirname)
                fileList.append(self._getFileList(dirname))
        return fileList
        
    def __generateFile(self, filePath, content):             
        f = open(filePath, 'w')
        f.write(content)
        f.close()
        
    def transformValue(self, str):#Transform to MB
        value, unit = str.split()
        value = int(value)
        if unit=="GB":
            value *= 1024
        elif unit=="KB":
            value /= 1024
        
        return value
                
    def isOEMPartition(self, sizeStr):
        size = self.transformValue(sizeStr)
        
        if size < 6500: #6500MB
            return True
        
        return False
        
    def __getDiskInfo(self):
        '''
        This Function is for Windows Only
        '''
        self.__diskDic = {}
        breakFind = False
        for i in range(10):
            stream = 'select disk '+str(i)+'\ndetail disk\nlist partition'
            diskInfoGet = os.path.normpath(os.path.join(os.getcwd() + '/diskInfoGet.bat'))
            self.__generateFile(diskInfoGet, stream)
            cmd = 'diskpart /s ' + "\"" + diskInfoGet + "\""
            outPutStr = self.runCommand(cmd)
            resultList = outPutStr.split('\n')
            partNum = 1
            for line in resultList:
                if re.match('.*no disk.*', line.strip().lower()):
                    breakFind = True
                    break
                if re.match('^Volume\s+\d+.*', line.strip()):
                    diskWithPartition = str(i+1) + ':' + str(partNum)
                    if re.match('.*FAT32.*', line.strip()):
                        line = re.sub(r'(^Volume\s+\d+\s+\S\s+).*(FAT32\s+.*)', r'\1\2', line.strip())
                    elif re.match('.*NTFS.*', line.strip()):
                        line = re.sub(r'(^Volume\s+\d+\s+\S\s+).*(NTFS\s+.*)', r'\1\2', line.strip())
                    infoList = line.strip().split()
                    newInforList = infoList[3:]
                    newInforList.insert(0, diskWithPartition)
                    self.__diskDic[infoList[2].lower()] = newInforList
                    if partNum==1 and i==1:
                        self.__firstPart = infoList[2]
                    partNum+=1
                    self.logger.debug(line)
                if re.match(r'.*\s+\d+\s+\w{1}B\s+\d+\s+\w{1}B.*', line.strip()):
                    size = re.sub(r'.*\s+(\d+\s+\w{1}B)\s+\d+\s+\w{1}B.*', r'\1', line.strip())
                    if re.match(r'.*\s+oem\s+.*', line.strip().lower()) or self.isOEMPartition(size):
                        self.__oemPartition = True
                        self.oemPartitionSize =  re.sub(r'.*\s+(\d+\s+\w{1}B)\s+\d+\s+\w{1}B.*', r'\1', line.strip())
                        self.oemPartitionOffset = re.sub(r'.*\s+\d+\s+\w{1}B\s+(\d+\s+\w{1}B).*', r'\1', line.strip())
            if breakFind:
                break
            time.sleep(2)
        
        for (k, v) in self.__diskDic.iteritems():
            self.logger.debug('%s = %s' % (k, v))
        
    
    def __getPartIdForDos(self, number): 
        '''
        This Function is for Windows Only
        '''  
        diskIdInDos = {
            "1": lambda : "c",
            "2": lambda : "d",
            "3": lambda : "e",
            "4": lambda : "f",
            "5": lambda : "g",
            "6": lambda : "h",
            "7": lambda : "i",
            "8": lambda : "j",
            "9": lambda : "k",
            "10": lambda : "l",
            "11": lambda : "m",
            "12": lambda : "n"
            }[str(number)]()
        return diskIdInDos
    
    
    def __getFat32PartIdForDos(self, number): 
        '''
        This Function is for Windows Only (Deprecated)
        '''  
        diskIdInDos = {
            "1": lambda : "c",
            "2": lambda : "d",
            "3": lambda : "e",
            "4": lambda : "f",
            "5": lambda : "g",
            "6": lambda : "h",
            "7": lambda : "i",
            "8": lambda : "j",
            "9": lambda : "k",
            "10": lambda : "l",
            "11": lambda : "m",
            "12": lambda : "n"
            }[str(number)]()
        return diskIdInDos
    
    def __getPartNum(self, diskIdInWin):
        '''
        This Function is for Windows Only
        It's for getting the sorted number of diskIdInWin in Dos Env (Deprecated)        
        '''
        diskSimpleId = diskIdInWin.split(':')[0].upper()
        RealPartNum = 1
        diskWithPart = self.__diskDic[diskSimpleId][0]
        (diskNum, partNum) = diskWithPart.split(':')
        for key in self.__diskDic.keys():
            if key == diskSimpleId:
                continue
            infoList = self.__diskDic[key]
            (diskNumTmp, partNumTmp) = infoList[0].split(':')
            if int(diskNum) > int(diskNumTmp):
                RealPartNum+=1
            elif int(diskNum)==int(diskNumTmp) and int(partNum)>int(partNumTmp):
                RealPartNum+=1
        if self.__oemPartition:
            pass
#            RealPartNum += 1
        return RealPartNum
    
    def __getFat32PartNum(self, diskIdInWin):
        '''
        This Function is for Windows Only (Deprecated)
        '''
        diskSimpleId = diskIdInWin.split(':')[0].upper()
        fat32PartNum = 1
        diskWithPart = self.__diskDic[diskSimpleId][0]
        (diskNum, partNum) = diskWithPart.split(':')
        for key in self.__diskDic.keys():
            if key == diskSimpleId:
                continue
            infoList = self.__diskDic[key]
            if infoList[1].strip().lower()=='fat32':
                (diskNumTmp, partNumTmp) = infoList[0].split(':')
                if int(diskNum) > int(diskNumTmp):
                    fat32PartNum+=1
                elif int(diskNum)==int(diskNumTmp) and int(partNum)>int(partNumTmp):
                    fat32PartNum+=1
        return fat32PartNum
    
    def __getFirstFat32PartId(self):
        '''
        This Function is for Windows Only (Deprecated)
        '''
        diskNum = 8
        partNum = 8
        firstFat32Id= None
        for key in self.__diskDic.keys():
            infoList = self.__diskDic[key]
            if infoList[1].strip().lower()=='fat32':
                (diskNumTmp, partNumTmp) = infoList[0].split(':')
                if int(diskNum) > int(diskNumTmp):
                    diskNum = diskNumTmp
                    partNum = partNumTmp
                    firstFat32Id = key
                elif int(diskNum)==int(diskNumTmp) and int(partNum)>int(partNumTmp):
                    partNum = partNumTmp
                    firstFat32Id = key
        return firstFat32Id
    
    def __getSysPartitionId(self):
        systemDrive = os.getenv("SystemDrive")[0].lower()
        self.logger.info("The system disk is %s" %systemDrive)
        for i in range(5):      #FIXME: five disks tops, should get exact number from "list disk"
            query = 'select disk '+str(i)+'\ndetail disk\nlist partition'
            diskInfoGet = os.path.normpath(os.path.join(os.getcwd() + '/diskInfoGet.bat'))
            self.__generateFile(diskInfoGet, query)
            cmd = 'diskpart /s ' + "\"" + diskInfoGet + "\""
            outPutStr = self.runCommand(cmd)
            resultList = outPutStr.split('\n')
            
            diskTmpId = None
            findBoot = False # Only support for English version OS
            findSystem = False
            
            diskId = None
            partitionNum = 0
            
            oemPartition = False
            oemPartitionSize = None
            oemPartitionOffset = None
            
            colonFlag = 0
            
            for line in resultList:
                '''
                m = re.match(r'^.*\s*id\s*.*:\s*((\d|\w){4,})\s*', line.strip().lower())
                if m:
                    diskTmpId = re.sub(r'^.*:\s*((\d|\w){4,})\s*', r'\1', line)
                '''
                
                if colonFlag<2 and re.match(r'^.*:\s*.*', line.strip().lower()):
                    if colonFlag == 1:
                        diskTmpId = re.sub(r'^.*:\s*"*((\w){6,})"*\s*', r'\1', line)
                    colonFlag += 1
                    
                #if re.match('^.*volume\s+\d+.*', line.strip().lower()) and not findSystem:
                if re.match('^.*\s+[1-9]{1,2}\s+[a-zA-Z]{1}\s+.*', line.strip().lower()) and not findSystem:
                    partitionNum += 1
                                                  
                #if re.match(r'.*volume\s+\d+\s+.*boot.*', line.strip().lower()):
                if re.match(r'.*\s+\d+\s+.*boot.*', line.strip().lower()):
                    findBoot = True
                
                if re.match(r'.*\s+\d+\s+\w{1}B\s+\d+\s+\w{1}B.*', line.strip()):
                    size = re.sub(r'.*\s+(\d+\s+\w{1}B)\s+\d+\s+\w{1}B.*', r'\1', line.strip())
                    if re.match(r'.*\s+oem\s+.*', line.strip().lower()) or self.isOEMPartition(size):
                        oemPartition = True
                        oemPartitionSize =  re.sub(r'.*\s+(\d+\s+\w{1}B)\s+\d+\s+\w{1}B.*', r'\1', line.strip())
                        oemPartitionOffset = re.sub(r'.*\s+\d+\s+\w{1}B\s+(\d+\s+\w{1}B).*', r'\1', line.strip())
                
                #systemVolumeRe = '^volume\s+\d+\s+%s\s+.*' % systemDrive
                #findSystemVolume = re.match(r'^volume\s+\d+\s+%s\s+.*' % systemDrive, line.strip().lower())
                #m = re.match(r'^Volume\s+(\d+)\s+(\w).*Boot$', line.strip())
                #if re.match(r'.*volume\s+\d+\s+%s\s+.*' % systemDrive, line.strip().lower()):   #system partition found
                if re.match(r'.*\s+\d+\s+%s\s+.*' % systemDrive, line.strip().lower()):   #system partition found
                    if not findSystem: #Support for Other version OS such as Chinese, Japanese
                        findSystem = True
                    if diskTmpId != None:
                        diskId = diskTmpId
                
                if 'RestoreToDisk' in self.parameter and self.parameter['RestoreToDisk'] == 'Yes':
                    self.logger.info('Disk level restoration needs not System and Boot check')
                elif findSystem and findBoot:
                    raise "Please check your disk not supported because System partition is not Boot partition which will cause boot issue if restore os"
                
            if findSystem:
                if not oemPartition:
                    return (diskId, partitionNum)
                for j in range(16): #Support 16 partition in one disk as maximum
                    query = 'select disk ' + str(i) + '\nselect partition ' + str(j+1) + '\ndetail disk\ndetail partition\nlist partition'
                    partInfoGet = os.path.normpath(os.path.join(os.getcwd() + '/partInfoGet.bat'))
                    self.__generateFile(partInfoGet, query)
                    cmd = 'diskpart /s ' + "\"" + partInfoGet + "\""
                    outPutStr = self.runCommand(cmd)
                    resultList = outPutStr.split('\n')
                    findSystemPart = False
                    for line in resultList:
                        #if re.match(r'^\*.*volume\s+\d+\s+%s\s+.*' % systemDrive, line.strip().lower()):   #system partition found
                        if re.match(r'.*\s+\d+\s+%s\s+.*' % systemDrive, line.strip().lower()):   #system partition found
                            systemPartitionSize = re.sub(r'.*\s+(\d+\s+\w{1}B)\s+.*', r'\1', line.strip())
                            self.logger.info('System Partition Size is %s' % systemPartitionSize)
                            findSystemPart = True
                        #if findSystemPart and re.match(r'^\*.*\s+%s\s+\d+\s+\w{1}B.*' % systemPartitionSize, line.strip()):
                        if findSystemPart and re.match(r'.*\s+%s\s+\d+\s+\w{1}B.*' % systemPartitionSize, line.strip()):
                            sysParOffset = re.sub(r'.*\s+\d+\s+\w{1}B\s+(\d+\s+\w{1}B).*', r'\1', line.strip())
                            self.logger.info('System Partition Offset is %s' % sysParOffset)
                            self.logger.info('OEM Partition Offset is %s' % oemPartitionOffset)
                            if self.transformValue(sysParOffset) > self.transformValue(oemPartitionOffset):
                                self.logger.info('OEM Partition is located beyond System Partition')
                                partitionNum += 1
                            return (diskId, partitionNum)

        return (None, None)
        
    def __getSysPartitionIdOld(self):
        '''
        This Function is for Windows Only (Deprecated)
        '''
        for i in range(5):      #FIXME: five disks tops, should get exact number from "list disk"
            query = 'select disk '+str(i)+'\ndetail disk\nlist partition'
            diskInfoGet = os.path.normpath(os.path.join(os.getcwd() + '/diskInfoGet.bat'))
            self.__generateFile(diskInfoGet, query)
            cmd = 'diskpart /s ' + "\"" + diskInfoGet + "\""
            outPutStr = self.runCommand(cmd)
            resultList = outPutStr.split('\n')
            dev = 0
            diskId = None
            
            diskTmpId = None
            for line in resultList:
                if re.match('.*no disk selected.*', line.strip().lower()):
                    #a o....so fail-safe approach...
                    raise Exception('Error occured while finding system partition')
                m = re.match(r'^.*\s+id:\s+{*\w+}*\s*', line.strip().lower())
                if m:
                    diskTmpId = re.sub(r'.*:\s+({*\w+}*)\s*', r'\1', line)
                m = re.match(r'^Volume\s+(\d+)\s+(\w).*Boot$', line.strip())
                if m:   #system partition found
                    dev = i + 1
                    partition = self.__getPartNum(m.group(2))
                    if self.__oemPartition:
                        partition += 1
                    if diskTmpId != None:
                        diskId = diskTmpId
                    continue
                
                m = re.match(r'^Volume\s+(\d+)\s+(\w).*System$', line.strip())
                if m and not dev:   #if System and Boot both exists, it seems we should fall for Boot...correct me
                    dev = i + 1
                    partition = self.__getPartNum(m.group(2))
                    if self.__oemPartition:
                        partition += 1
                    if diskTmpId != None:
                        diskId = diskTmpId
                    continue

            if dev:
                return (diskId, partition)
            time.sleep(2)
            
    def getTaskNote(self): 
        if "OSType" in self.parameter:
            self.note = "OS:" + self.parameter['OSType']
        if "OSEdition" in self.parameter:
            self.note += ",OSEdition:" + self.parameter['OSEdition']
        if "InstalledSoftware" in self.parameter:
            self.note += ",InstalledSoftware:" + self.parameter['InstalledSoftware']
        return self.note

##################This section is mainly for debug -- Begin #############################
if __name__ == '__main__':    
#    ro=childTask('RestoreOS', 1)
#    ro.addPara("OSType", "Leopard")
#    ro.addPara("OSEdition", "10.5.6_Fre")
#    ro.addPara("targetPartition1", "Main")
#    ro.addPara("targetPartition2", "Daily")
#    ro.addPara("OSModel", "imac")
#    ro.run()
    ro=childTask('RestoreOS', 1)
    ro.addPara("OSEdition", "")
    ro.addPara("OSImagelocation", "file:\\\\d:\\test.gho")
    ro.addPara("OSType", "")
    ro.addPara("sourceOS", "windows")
    ro.run()
    #ro.getLabPETool()
##################This section is mainly for debug -- End #############################
