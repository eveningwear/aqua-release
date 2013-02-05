from __future__ import division
import os
from os.path import join, getsize
import datetime,time
import xml.dom.minidom 

class File:
    def __init__(self,path,size):
        self.path=path
        self.size=size
        self.dateTime=self.getCreateTime(path)
             
    def getCreateTime(self,path):
        statinfo=os.stat(path)
        dirs=time.localtime(statinfo.st_ctime)
        d1=datetime.datetime(dirs[0],dirs[1],dirs[2],dirs[3],dirs[4],dirs[5])
        return d1
            
 
        
class ReadTask:
    def __init__(self,xmlPath=''):
        self.rootPath=self.getRootPath(xmlPath)
        self.resultPath=self.getResultPath(xmlPath)
        self.logPath=self.getLogPath(xmlPath)

            
    def run(self):
        countSize=0L
        oper=[]
        try:
            oper.append(File(self.rootPath,countSize))
        except:
            logStr='Append root directory occurs exception, path=%s'%self.rootPath
            self.writeInLog(logStr)
            return
        for root, dirs, files in os.walk(self.rootPath):
            for file in files:
                path=join(root,file)
                size=0L
                try:
                    size=getsize(path)
                except:
                    logStr='Get size occurs exception, path=%s'%path
                    self.writeInLog(logStr)
                    continue
                countSize+=size
                try:
                    oper.append(File(path,size))
                except:
                    logStr='Append file occurs exception, path=%s'%path
                    self.writeInLog(logStr)
                    return
        oper[0].size=countSize
        return oper        
        
    def getNowTime(self):
        """get current time"""
        nowTime=time.localtime()
        d1=datetime.datetime(nowTime[0],nowTime[1],nowTime[2],nowTime[3],nowTime[4],nowTime[5])
        return d1   
    
    def writeInResult(self):
        """write in Result file"""
        if self.oper==None:
            return
        logStr=str(self.getNowTime())+':'+'Begin writing in result file'
        self.writeInLog(logStr)
        try:
            f=open(self.resultPath,'w')
        except:
            logStr='Open result file occurs exception,path=%'%self.resultPath
            self.writeInLog(logStr)
            return
        s='The result file was created on %s'%str(self.getNowTime())+'\n'
        for file in self.oper:
            s+=file.path+'\n'+self.addCharacter(file.size)+'\n'+str(file.dateTime)+'\n'+'\n'
        try:
            f.write(s)
        except:
            logStr='Write to result file occurs exception,path=%'&self.resultPath
            self.writeInLog(logStr)
            return
        try:
            f.close()
        except:
            logStr='Close result file occurs exception,path=%'&self.resultPath
            self.writeInLog(logStr)
        
    def addCharacter(self,size):
        """add character to result file"""
        if size<1024:
            return str(size)+'B'
        size=size/1024
        if size<1024:
            return str(size)+'KB'
        size=size/1024
        if size<1024:
            return str(size)+'MB'
        size=size/1024
        if size<1024:
            return str(size)+'GB'
        size=size/1024
        if size<1024:
            return str(size)+'TB'
        size=size/1024
        return None    
    
    def getRootPath(self,xmlPath=''):
        dom = xml.dom.minidom.parse(xmlPath)
        protTask=dom.getElementsByTagName('protTask')[0]
        return protTask.getAttribute('rootPath').encode()   

    def getLogPath(self,xmlPath=''):
        dom = xml.dom.minidom.parse(xmlPath)
        protTask=dom.getElementsByTagName('protTask')[0]
        logPath=protTask.getAttribute('logPath').encode()
        name='log'+self.getNowDate()+'.txt'
        return os.path.join(logPath,name) 
        
    def getResultPath(self,xmlPath=''):
        dom = xml.dom.minidom.parse(xmlPath)
        protTask=dom.getElementsByTagName('protTask')[0]
        return protTask.getAttribute('resultPath').encode()
    
    def getNowDate(self):
        """get new date"""
        nowTime=time.localtime()
        d1=datetime.date(nowTime[0],nowTime[1],nowTime[2])
        return str(d1) 
    
    def writeInLog(self,logString=''):
        """write string in log file"""
        try:
            f=open(self.logPath,'a')
        except:
            print 'Open log file occurs exception,path=%'%self.logPath
        try:
            f.write('\n'+logString)
        except:
            print 'Write to log occurs exception,path=%'%self.logPath
        try:
            f.close()
        except:
            print 'Close log file occurs exception,path=%'%self.logPath
            
    def read(self):
        """read directories and files"""
        if not self.logPath:
            print 'Config file has wrong logPath'
            return
        logStr='----------------------------------------------------------'+'\n'+'Start ReadTask'+'\n'
        logStr+=str(self.getNowTime())+':'+'Begin running Read operation'
        self.writeInLog(logStr)
        if not self.rootPath:
            logStr='Config file has wrong rootPath'
            self.writeInLog(logStr)
        elif not self.resultPath:
            logStr='Config file has wrong resultPath'
            self.writeInLog(logStr)
        else:
            self.oper=self.run() 
            self.writeInResult()
        logStr='Finish ReadTask'+'\n'+'----------------------------------------------------------'+'\n'
        self.writeInLog(logStr)         
        
