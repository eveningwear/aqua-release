"""

    FTPTask.py
    
    Written by: Jacky Li (yxli@adobe.com)

"""

import re, ftplib, os, stat, time, socket
import smb, nmb

from allTasks.baseTask import Task

class childTask(Task):
    
    def __init__(self, type, priority = 0):
        super(childTask, self).__init__(type, priority)
        self.__downloadedFileList=[]
        return
        
    def runMac(self):
        self.logger.info('FTPTask runMac')
        return
        
    def runWin(self):
        self.logger.info('FTPTask runWin')
        return
    
    def run(self):
        self.logger.info('FTPTask run')
        server = self.parameter['Host']
        user = self.parameter['User']
        passwd = self.parameter['Passwd']
        self.logger.info('Ready to download file')
        if 'Repository' in self.parameter.keys() and self.parameter['Repository'].strip() != '':
            repository = self.parameter['Repository']
        else:
            repository = os.getcwd()
            
        if 'FolderPattern' in self.parameter.keys():
            folderPattern = self.parameter['FolderPattern']
        else:
            folderPattern = ''
            
        if 'FilePath' in self.parameter.keys() and self.parameter['FilePath'].strip() != '':
            filePath = self.parameter['FilePath']
            fileParent = re.sub(r'(.*)/.*', r'\1', filePath)
            filename = re.sub(r'.*/(.*)', r'\1', filePath)
            date = '1979-11-12'
            if 'pattern' in self.parameter.keys() and self.parameter['pattern'].strip() != '':
                pattern = self.parameter['pattern']
            else:
                pattern = filePath + '$' + "|" + filePath + '/.*'
            baseDir = ''
            folderTimeContrain = 'False'
            if 'OneFile' in self.parameter.keys() and self.parameter['OneFile'].strip()=='True':
                self.getOneFileFromFTP(server, user, passwd, filePath, repository)
            else:
                self.getFilesFromFTP(server, user, passwd, fileParent, date, repository, pattern, baseDir, folderPattern, folderTimeContrain)
        if self.parameter.has_key('FolderPath') and self.parameter['FolderPath'].strip() != '':
            filePath = self.parameter['FolderPath']
            date = '1979-11-12'
                    
            if 'pattern' in self.parameter.keys() and self.parameter['pattern'].strip() != '':
                pattern = self.parameter['pattern']
            else:
                pattern = ''
            baseDir = ''
            folderTimeContrain = 'False'
            self.getFilesFromFTP(server, user, passwd, filePath, date, repository, pattern, baseDir, folderPattern, folderTimeContrain)
        return
    
    def getOneFileFromFTP(self, server, user, passwd, filePath, repository):
        self.logger.info('Info:%s, %s, %s, %s', server, user, filePath, repository)
        tryCount = 1
        while tryCount <= 3:
            try:
                ftpCon = ftplib.FTP(server)
            except socket.error, e:
                if tryCount <= 3:
                    self.logger.debug(e)
                    time.sleep(3)
                    tryCount += 1
                    continue
                raise
            else:
                break
        ftpCon.login(user, passwd)
        ftpCon.set_pasv(False)
        fileParent = re.sub(r'(.*)/.*', r'\1', filePath)
        filename = re.sub(r'.*/(.*)', r'\1', filePath)
        if not os.path.exists(repository):
            os.makedirs(repository)
        downloadFile = os.path.join(repository, filename)
        ftpCon.cwd(fileParent)
        filelist = ftpCon.nlst('-l')
        filelist.reverse()
        for line in filelist:
            self.logger.info(line)
        f = open(downloadFile, "wb")
        self.logger.info('downloading file: %s', downloadFile)
        try:
            ftpCon.retrbinary("RETR %s" % (filename), f.write)
        except Exception, e:
            self.logger.error('Exception thrown when downloading the file %s: %s', filename, e)
        self.__downloadedFileList.append(downloadFile)
        f.close()
        ftpCon.close()
        
    def getFilesFromFTP(self, server, user, passwd, filePath, date, repository, pattern, baseDir, folderPattern, folderTimeContrain, recursive=True):
        self.logger.info('Info:%s, %s, %s, %s, %s', server, user, filePath, date, repository)
        tryCount = 1
        while tryCount <= 3:
            try:
                ftpCon = ftplib.FTP(server)
            except socket.error, e:
                if tryCount <= 3:
                    self.logger.debug(e)
                    time.sleep(3)
                    tryCount += 1
                    continue
                raise
            else:
                break
        ftpCon.login(user, passwd)
        ftpCon.set_pasv(False)
        pathArray = filePath.split(";")
        for path in pathArray:
            folderStack = []
            if baseDir.strip()!="":
                folderList = path.split('/')
                appendFlag = 0
                for folder in folderList:
                    if appendFlag == 1:
                        folderStack.append(folder)
                    elif folder.strip() == baseDir:
                        folderStack.append(baseDir)
                        appendFlag = 1
            """
            else:
                repositoryName = re.sub(r'.*/(.*)', r'\1', path)
                localRep = os.path.join(repository, repositoryName)
                folderStack = [repositoryName]
            """
            self.logger.info(folderStack)
            self.getFiles(ftpCon, path, date, repository, folderStack, pattern, folderPattern, folderTimeContrain, recursive)
        ftpCon.quit()
      
    def getFiles(self, ftpCon, path, date, repository, folderStack, pattern, folderPattern, folderTimeContrain, recursive):
        ftpCon.cwd(path)
        self.logger.info("current path is: %s", ftpCon.pwd())
        folderPatternHierarchy = []
        if folderPattern.strip() != '':
            folderPatternHierarchy = folderPattern.split('/')
        filelist = ftpCon.nlst('-l')
        filelist.reverse()
        for line in filelist:
            #self.logger.debug(line)
            print line
            fileInfo = line.split()
            if len(fileInfo)>4 and re.match('^\d*$', fileInfo[4]) != None:
                if re.match('^d.*', fileInfo[0]) != None: #directory
                    dirName = re.sub(r'.*\S{3}\s+\S+\s+\S{4,5}\s+(.*)', r'\1', line)
                  
                    if folderTimeContrain.lower().strip() == 'true': #Compare the created time of folder
                        fileD = re.sub(r'.*\S{3}\s+\S+\s+(\S{4,5})\s+(.*)', r'\1', line)
                        if fileD.find(':')==-1:
                            year = fileD
                        else:
                            year = time.ctime(time.time()).split()[4]
                        month = self.getMonth(fileInfo[5])
                        fileDate = "-".join((year, month, fileInfo[6]))                                             
                        if not self.beforeDate(fileDate, date):
                            continue;
                       
                    folderStack.append(dirName)
                    if len(folderPatternHierarchy)>0 and re.match(folderPatternHierarchy[0], dirName) and recursive:
                        nextFolderPattern = "/".join(folderPatternHierarchy[1:])
                        self.getFiles(ftpCon, dirName, date, repository, folderStack, pattern, nextFolderPattern, folderTimeContrain, recursive)
                    elif len(folderPatternHierarchy)==0 and recursive:
                        self.getFiles(ftpCon, dirName, date, repository, folderStack, pattern, folderPattern, folderTimeContrain, recursive)
                    folderStack.pop()
                    #self.logger.debug("/".join(folderStack))
                    print "/".join(folderStack)
                else: #file
                    if len(folderPatternHierarchy)!=0:
                        continue;
                    fileName = re.sub(r'.*\S{3}\s+\S+\s+\S{4,5}\s+(.*)', r'\1', line)
                    fileD = re.sub(r'.*\S{3}\s+\S+\s+(\S{4,5})\s+(.*)', r'\1', line)
                    if fileD.find(':')==-1:
                        year = fileD
                    else:
                        year = time.ctime(time.time()).split()[4]
                    month = self.getMonth(fileInfo[5])
                    fileDate = "-".join((year, month, fileInfo[6]))
                    fileSize = fileInfo[4] #File Size on FTP Server
                    if self.beforeDate(fileDate, date):#Get File
                        self.getFile(ftpCon, repository, folderStack, fileName, pattern, fileSize)
            #elif re.match('^\d*$', fileInfo[2]) != None:
            elif len(fileInfo)>3: #To avoid some special conditions such as "total 698698" returned whose length is only 2
                if fileInfo[2].strip() == '<DIR>': #directory
                    dirName = re.sub(r'\d{,2}-\d{,2}-\d{,2}\s+\d{,2}:\d{,2}[A|P]M\s+<DIR>\s+(.*)', r'\1', line)
                   
                    if folderTimeContrain.lower().strip() == 'true': #Compare the created time of folder
                        fileDates = fileInfo[0].split('-')
                        year = fileDates[2]
                        if re.match('^20|19\d{2}$', year)==None:
                            year = '20' + fileDates[2]
                        month = fileDates[0]
                        fileDate = "-".join((year, month, fileDates[1]))
                        fileSize = fileInfo[2] #File Size on FTP Server
                        if not self.beforeDate(fileDate, date):
                            continue;
                      
                    folderStack.append(dirName)
                    #newPath = "/".join((path, dirName))
                    #print "/".join(folderStack)
                    #Add Folder Pattern Check Here
                    if len(folderPatternHierarchy)>0 and re.match(folderPatternHierarchy[0], dirName) and recursive:
                        nextFolderPattern = "/".join(folderPatternHierarchy[1:])
                        self.getFiles(ftpCon, dirName, date, repository, folderStack, pattern, nextFolderPattern, folderTimeContrain, recursive)
                    elif len(folderPatternHierarchy)==0 and recursive:
                        self.getFiles(ftpCon, dirName, date, repository, folderStack, pattern, folderPattern, folderTimeContrain, recursive)
                    folderStack.pop()
                    #self.logger.debug("/".join(folderStack))
                    print "/".join(folderStack)
                else: #file
                    if len(folderPatternHierarchy)!=0:
                        continue;
                    fileName = re.sub(r'\d{,2}-\d{,2}-\d{,2}\s+\d{,2}:\d{,2}[A|P]M\s+\d*\s+(.*)', r'\1', line)
                    fileDates = fileInfo[0].split('-')
                    year = fileDates[2]
                    if re.match('^20|19\d{2}$', year)==None:
                        year = '20' + fileDates[2]
                    month = fileDates[0]
                    fileDate = "-".join((year, month, fileDates[1]))
                    fileSize = fileInfo[2] #File Size on FTP Server
                    if self.beforeDate(fileDate, date):#Get File
                        self.getFile(ftpCon, repository, folderStack, fileName, pattern, fileSize)
        ftpCon.cwd('..')

    def getFile(self, ftpCon, repository, folderStack, fileName, pattern, fileSize):
        currentPath = ftpCon.pwd()
        self.logger.info("current path is: %s", currentPath)
        filePath = os.path.normpath(os.path.join(repository, "/".join((folderStack)), fileName))
        patternList = []
        match = False
        if pattern.strip() != "":
            patternList = pattern.split("|")
        else:
            match =True
        for patternElement in patternList:
            if re.match(patternElement, currentPath + "/" + fileName )!=None:
                match = True
                break;
        if not match:
            return
        repository = os.path.normpath(os.path.join(repository, '/'.join(folderStack)))
        if not os.path.exists(repository):
            os.makedirs(repository)
        filePath = os.path.join(repository, fileName)
        if not os.path.exists(filePath):
            #self.logger.debug(ftpCon.pwd())
            f = open(filePath, "wb")
            self.logger.info('downloading file: %s', filePath)
            try:
               ftpCon.retrbinary("RETR %s" % (fileName), f.write)
               self.__downloadedFileList.append(filePath)
            except Exception, e:
                self.logger.error('Exception thrown when downloading the file %s: %s', fileName, e)
            f.close()
        else:#should compare the file size
            fileStates = os.stat(filePath)
            fileInfo = {
               'Size': fileStates[stat.ST_SIZE],
               'LastModified': time.ctime(fileStates[stat.ST_MTIME]),
               'LastAccessed': time.ctime(fileStates[stat.ST_ATIME]),
               'CreationTime': time.ctime(fileStates[stat.ST_CTIME]),
               'Mode': fileStates[stat.ST_MODE]
            }
            self.logger.info(filePath)
            for key in fileInfo.keys():
                self.logger.info("%s\t%s", key, fileInfo[key])
            self.logger.info("%s\t%s", str(fileSize), fileInfo['Size'])
            logStr = str(fileSize) + "\t" + str(fileInfo['Size'])
            self.__downloadedFileList.append(filePath)
            if int(fileSize)!=int(fileInfo['Size']):
                f = open(filePath, "wb")
                self.logger.info('downloading file: %s', filePath)
                try:
                    ftpCon.retrbinary("RETR %s" % (fileName), f.write)
                    #self.__downloadedFileList.append(filePath)
                except Exception, e:
                    self.logger.error('Exception thrown when downloading the file %s: %s', fileName, e)
                f.close()
            return
        return
    
    
    def beforeDate(self, fileDate, date):
        '''
        fileDateList = fileDate.split("-")
        dateList = date.split("-")
        
        regualDateYear = dateList[0]
        regualDateMonth = re.sub(r'0*(.*)', r'\1', dateList[1])
        regualDateDay = re.sub(r'0*(.*)', r'\1', dateList[2])
        
        regualFileDateYear = fileDateList[0]
        regualFileDateMonth = re.sub(r'0*(.*)', r'\1', fileDateList[1])
        regualFileDateDay = re.sub(r'0*(.*)', r'\1', fileDateList[2])
        
        if int(regualFileDateYear)>int(regualDateYear):
            return True
        elif int(regualFileDateYear)==int(regualDateYear) and int(regualFileDateMonth)>int(regualDateMonth):
            return True
        elif int(regualFileDateYear)==int(regualDateYear) and int(regualFileDateMonth)==int(regualDateMonth) and int(regualFileDateDay)>=int(regualDateDay):
            return True
        #Comments here for letting pass
        #retrun False
        '''
        return True
       
    def getMonth(self, monStr):   
        month = {
            "Jan": lambda : "1",
            "Feb": lambda : "2",
            "Mar": lambda : "3",
            "Apr": lambda : "4",
            "May": lambda : "5",
            "Jun": lambda : "6",
            "Jul": lambda : "7",
            "Aug": lambda : "8",
            "Sep": lambda : "9",
            "Oct": lambda : "10",
            "Nov": lambda : "11",
            "Dec": lambda : "12"
            }[monStr]()
        return month
    
    def getDownloadList(self):
        return self.__downloadedFileList

