"""

    FTPUploadTask.py
    
    Written by: Jacky Li (yxli@adobe.com)

"""

import re, ftplib, os, stat, time, socket
import smb, nmb

from allTasks.baseTask import Task

class childTask(Task):
    
    def __init__(self, type, priority = 0):
        super(childTask, self).__init__(type, priority)
        self.__uploadedFileList=[]
        return
        
    def runMac(self):
        self.logger.debug('FTPUploadTask runMac')
        return
        
    def runWin(self):
        self.logger.debug('FTPUploadTask runWin')
        return
    
    def run(self):
        self.logger.debug('FTPUploadTask run')
        server = self.parameter['Host']
        user = self.parameter['User']
        passwd = self.parameter['Passwd']
        self.logger.debug('Ready to upload file')
        if 'Repository' in self.parameter.keys() and self.parameter['Repository'].strip() != '':
            repository = self.parameter['Repository']
        else:
            repository = os.getcwd()
        
        if 'baseDir' in self.parameter.keys() and self.parameter['baseDir'].strip() != '':
            baseDir = self.parameter['baseDir']
        else:
            baseDir = ''
        
        if 'pattern' in self.parameter.keys() and self.parameter['pattern'].strip() != '':
            pattern = self.parameter['pattern']
        else:
            pattern = ''
            
            
        folderStack = []
        
        if 'FilePath' in self.parameter.keys() and self.parameter['FilePath'].strip() != '':
            filePath = self.parameter['FilePath']
            self.putOneFileToFTP(server, user, passwd, filePath, repository)
        if self.parameter.has_key('FolderPath') and self.parameter['FolderPath'].strip() != '':
            filePath = self.parameter['FolderPath']
            if baseDir != "":
                folderStackRe = ".*(" + baseDir + ".*)"
                folderStack = re.sub(folderStackRe, r"\1", filePath.replace("\\", "/")).rstrip("/").split("/")
                folderStack.reverse()
                filePathRe = "(.*)" + baseDir + ".*"
                filePath = re.sub(filePathRe, r"\1", filePath.replace("\\", "/"))
            self.putFilesToFTP(server, user, passwd, filePath, repository, folderStack, pattern, baseDir)
        return
    
    def putFilesToFTP(self, server, user, passwd, filePath, repository, folderStack, pattern, baseDir):
        self.logger.debug('Info:%s, %s, %s, %s, %s', server, user, passwd, filePath, repository)
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
        ftpCon.cwd(repository)
        for root, dirs, files in os.walk(filePath):
            folderName = ""
            if len(folderStack)>0:
                folderName = folderStack.pop()
            rootName = os.path.basename(root)
            try:
                if folderName=="" or folderName != "" and folderName == rootName:
                    ftpCon.mkd(rootName)
                else:
                    folderStack.append(folderName)
                    continue
            except:
                pass
            ftpCon.cwd(rootName)
            if len(folderStack)>0:
                continue
            for filename in files:
                fp = os.path.join(root, filename)
                f = open(fp, "rb")
                self.logger.debug('uploading file: %s', fp)
                try:
                    ftpCon.storbinary('STOR %s' % filename, f, 1024)
                except Exception, e:
                    self.logger.error('Exception thrown when uploading the file %s: %s', filename, e)
        ftpCon.close()
        
    
    def putOneFileToFTP(self, server, user, passwd, filePath, repository):
        self.logger.debug('Info:%s, %s, %s, %s', server, user, filePath, repository)
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
        ftpCon.cwd(repository)
        filename = os.path.basename(filePath)
        f = open(filePath, "rb")
        self.logger.debug('uploading file: %s', filePath, 1024)
        try:
            ftpCon.storbinary(filename, f)
        except Exception, e:
            self.logger.error('Exception thrown when uploading the file %s: %s', filename, e)
        self.__uploadedFileList.append(filePath)
        f.close()
        ftpCon.close()
        
    
    def getUploadList(self):
        return self.__uploadedFileList

if __name__ == '__main__':
    task = childTask('xx', 1)
    task.addPara('Host', "blazeman.pac.adobe.com")
    task.addPara('User', "adobenet\\cndtpqe")
    task.addPara('Passwd', "CN-qe002")
    task.addPara('Repository', "/filtertestResults")
    task.addPara('FolderPath', "D:\\work\\innovation\\ioix_ws\\dev\\qms\\qmsClient\\src\\allTasks\\PSFReport\\Windows\\en_US\\Adobe Photoshop\\12.0.0\\20090904.m.832\\2009_09_24T16_58_08")
    task.addPara('baseDir', "Windows")
    task.run()
    