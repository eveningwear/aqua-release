"""

    SambaUploadTask.py
    
    Written by: Jacky Li (yxli@adobe.com)

"""

import re, ftplib, os, stat, time, StringIO
import smb, nmb, socket

import sys
from allTasks.baseTask import Task

class childTask(Task):
    
    def __init__(self, type, priority = 0):
        super(childTask, self).__init__(type, priority)
        self.__downloadedFileList=[]
        
    def run(self):
        self.logger.debug('Samba upload task run')
        if 'Repository' in self.parameter.keys() and self.parameter['Repository'].strip() != '':
            self.repository = self.parameter['Repository']
        else:
            self.repository = os.getcwd()
            
        self.logger.debug('Ready to download file')
        #a user-provided path, so we use samba
        (filePath, sambaUser, sambaPsw, sambaDomain) = map(lambda s: s.encode('ascii'), (self.parameter['FolderPath'], self.parameter['sambaUser'], self.parameter['sambaPsw'], self.parameter['sambaDomain']))
        #self.getSambaFile('ps-bj-qe/Transfer/tyyang/tool.mpp', 'cndtpqe', 'CN-qe001', 'ADOBENET')
        self.putSambaFiles(filePath, sambaUser, sambaPsw, sambaDomain)
    
    def getDownloadList(self):
        return self.__downloadedFileList
    
    def puttSingleFile(self, dev, remotePath, ioObj=None):
        if 'filterStr' in self.parameter.keys() and not re.match(self.parameter['filterStr'], remotePath):
            return
        if ioObj:
            self.logger.info('Uploading: ' + remotePath)
            self.srv.retr_file(dev, remotePath, ioObj.write)
        else:
            remotePath = remotePath.replace('\\', '/')
            filePath = self.joinPath(self.repository, remotePath.split(self.remotePathBase, 1)[1])
            if os.path.exists(filePath):
                stat =os.stat(filePath) 
                s = stat.st_size
                try:
                    rs = self.srv.list_path(dev, remotePath)[0]
                except smb.SessionError, e:
                    raise Exception('path %s error: %s' % (remotePath, str(e)))
                self.logger.debug('Current File size is:' + str(s) +' while remote File size is ' + str(rs.get_filesize()))
                #mt = stat.st_mtime
                #print mt, rs.get_mtime_epoch()
                # a little risky here...
                if s == rs.get_filesize() and not remotePath.lower().endswith(('txt', 'xml')):   #always download .txt file
                    self.logger.info('Ignored: ' + remotePath)
                    #FIXME: added by Jacky, must add to the list to avoid possible error to miss return downloaded file list
                    #for installation using
                    self.__downloadedFileList.append(filePath)
                    return
            theDir = os.path.dirname(filePath)
            if not os.path.exists(theDir):
                os.makedirs(theDir)
            callBackObj = open(filePath, 'wb')
            self.logger.info('Downloading: ' + remotePath)
            self.srv.retr_file(dev, remotePath, callBackObj.write)
            self.__downloadedFileList.append(filePath)
        
    def getFolder(self, dev, remotePath):
        try:
            fl = self.srv.list_path(dev, self.joinPath(remotePath, '*'))
        except smb.SessionError, e:
            raise Exception('path %s error: %s' % (remotePath, str(e)))
        for f in fl:
            if f.is_hidden():
                continue
            name = f.get_longname()
            if not f.is_directory():
                self.getSingleFile(dev, self.joinPath(remotePath, name))
            elif name not in ('.', '..'):    #better solution?
                self.getFolder(dev, self.joinPath(remotePath, name))
                
    def isDir(self, dev, path):
        #let exceptions raise!
        try:
            result = self.srv.list_path(dev, path)
        except smb.SessionError, e:
            raise Exception('path %s error: %s' % (path, str(e)))
        return result[0].is_directory()
                
    def getFileContent(self, dev, path):
        try:
            strIO = StringIO.StringIO()
            self.getSingleFile(dev, path, strIO)
            text = strIO.getvalue()
            strIO.close()
            return text
        except smb.SessionError:
            return False
    
    #Deprecated
    def latestBuildSpecified(self, dev, remotePath):
        if 'appLang' in self.parameter:
            f = self.getFileContent(dev, self.joinPath(remotePath, 'latest.txt'))
            data = f.split('\r\n')[:-1]
            if len(data) > 0:
                #don't fail me Michael, it's our one-shot chance
                return self.parameter['appLang'].encode('ascii') + '/' + dict(map(lambda p: (p.split(':')), data))[self.parameter['appLang']]
            return f
        return False

    def joinPath(self, *args):
        return os.path.normpath(os.path.join(*args))
    
    def connect(self, url, username, psw, domain):
        parts = url.split('/', 2)
        assert(len(parts) == 3)
        
        (server, dev, remotePath) = parts
        nb = nmb.NetBIOS()
        #nb.set_nameserver(server)
        #ip = nb.gethostbyname(server)[0].get_ip()
        ip = socket.gethostbyname(server)
        server = server.split(".")[0]
        self.srv = smb.SMB(server, ip)
        self.srv.login(username, psw, domain)
        
    
    def putSambaFiles(self, url, username, psw, domain):
        self.logger.info('Start uploading from samba location: ' + url)
        self.connect(url, username, psw, domain)
        
        parts = url.split('/', 2)
        (server, dev, remotePath) = parts
        self.remotePathBase = re.sub(r'^(.*/)[^/].*', r'\1', remotePath)
        if self.isDir(dev, remotePath):  #folder download
            self.putFolder(dev, remotePath)
            '''
            latestBuildDir = self.latestBuildSpecified(dev, remotePath)
            if latestBuildDir:
                self.getFolder(dev, remotePath + latestBuildDir + '/')
            else:
                self.getFolder(dev, remotePath)
            '''
        else:
            self.putSingleFile(dev, remotePath)

if __name__ == '__main__':
    task = childTask('xx', 1)
    task.addPara('sambaDomain', unicode('ADOBENET', 'utf-8'))
    task.addPara('sambaUser', unicode('cndtpqe', 'utf-8'))
    task.addPara('sambaPsw', unicode('CN-qe001', 'utf-8'))
    task.repository = r"c:\temp" 

    task.addPara('FolderPath', unicode(r'pektools/Transfer/yxli/test', 'utf-8'))
    task.run()
    print task.getDownloadList()
#
#    task.addPara('FolderPath', unicode(r'ps-bj-qe/transfer/tyyang/qmsclient/', 'utf-8'))
#    task.run()
#
#    task.addPara('FolderPath', unicode(r'ps-bj-qe/transfer/tyyang/tool.mpp', 'utf-8'))
#    task.run()
#    task.connect('ps-bj-qe/Transfer/tyyang/diskinfo.txt', 'cndtpqe', 'CN-qe001', 'ADOBENET')
#    print task.getFileContent('Transfer', '/tyyang/diskinfo.txt')
    #taskkill /f /fi "imagename eq python.exe"


