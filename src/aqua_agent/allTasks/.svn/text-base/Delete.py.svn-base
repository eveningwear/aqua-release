from __future__ import division
import os
import re
import datetime,string,time
import xml.dom.minidom 

class File:
    """file object"""
    def __init__(self,path,size,dateTime):
        self.path=path
        self.size=size
        self.dateTime=dateTime
        self.beProtected=0
        
class ProtParam:
    """protect directory"""
    def __init__(self,path,pattern,keyword):
        self.path=path
        self.pattern=pattern
        self.keyword=keyword
        
class DeleteCondition:
    """delete operation """
    def __init__(self,protParam,saveSize,resultPath,logPath):
        self.protParam=protParam
        self.saveSize=saveSize
        self.resultPath=resultPath
        self.logPath=logPath
                    
class DeleteTask:
    def __init__(self,xmlPath=''):
        self.oper=[]  
        self.protectSize=0L
        self.countSize=0L 
        self.rootPath='' 
        self.conditions=self.getCondition(xmlPath) 
        
    def readResultFile(self,resultPath='',oper=[]):
        """used to read log"""
        logStr=str(self.getNowTime())+':'+'Begin reading result file'
        self.writeInLog(logStr)
        try:
            f=open(resultPath,'r')
        except:
            logStr='Open result file occurs exception'
            self.writeInLog(logStr)
            return
        i=0
        path=''
        size=0
        dateTime=datetime
        for each in f.readlines():
            e=each.strip('\n')    
            if i==1:
                self.rootPath=e
            elif i==2:
                self.countSize=self.removeCharacter(e)
            elif i>4:  
                if (i-1)%4==0:
                    path=e
                if (i-1)%4==1:
                    size=self.removeCharacter(e)
                if (i-1)%4==2: 
                    dateTime=time.strptime(e,'%Y-%m-%d %H:%M:%S')
                    try:
                        oper.append(File(path,size,dateTime))
                    except:
                        logStr='Append file occurs exception'
                        self.writeInLog(logStr)
                        pass
            i=i+1
        f.close()
        
    def tagSaveDir(self):
        """specify saved directory"""
        logStr=str(self.getNowTime())+':'+'Tag the file needed to protect'
        self.writeInLog(logStr)
        for file in self.oper:
            if not os.path.exists(file.path):
                return 0
            for param in self.conditions.protParam:
                if param.keyword=='' and param.path=='' and param.pattern=='':
                    break 
                if self.patternCompare(file, param.pattern)and self.pathCompare(file, param.path)and self.keywordCompare(file, param.keyword):
                    file.beProtected=1
                    logStr='protected file:%s'%file.path
                    self.writeInLog(logStr)
                    break
        return 1
            
    def pathCompare(self,file,path):
        """used to compare path"""
        if path=='':
            return True
        dirs1=file.path.split('\\')
        dirs2=path.split('\\')
        i=0
        for dir2 in dirs2:
            if dir2!=dirs1[i]and i!=0:
                return False
            i+=1
        return True
        
    def patternCompare(self,file,pattern):
        if pattern=='':
            return True
        p=re.compile(pattern)
        if p.search(file.path):
            return True
        else:
            return False
        
    def keywordCompare(self,file,keyword):
        if keyword=='':
            return True
        key=keyword.split('|')
        for k in key:
            if re.search(k,file.path):
                return True
        return False        
        
    def sortByTime(self):
        """sort files by create time"""
        logStr=str(self.getNowTime())+':'+'Sort files by create time'
        self.writeInLog(logStr)
        self.oper.sort(key =lambda Obj: Obj.dateTime)   
            
    def run(self):
        """run the delete operation"""
        logStr=str(self.getNowTime())+':'+'Begin running DeleteTask'
        self.writeInLog(logStr)
        for file in self.oper:
            if self.countSize<self.conditions.saveSize:
                logStr='Finish delete cause the size reach to your configuration'
                self.writeInLog(logStr)
                break     
            elif file.beProtected==0:
                try:
                    os.remove(file.path)
                    logStr=str(self.getNowTime())+':'+'delete this file: %s'%file.path
                except:
                    logStr='delete file occurs exception,path=%s'%file.path
                    pass
                self.countSize-=file.size
                d=file.dateTime
                logStr+='\n'+'the file created by %s'%datetime.datetime(d[0],d[1],d[2],d[3],d[4],d[5])
                logStr+='\n'+'current size:%s'%self.addCharacter(self.countSize)
            else:
                self.protectSize+=file.size
                logStr='save this file: %s'%file.path
                logStr+='\n'+'current size:%s'%self.addCharacter(self.countSize)
            self.writeInLog(logStr) 
                
    def delEmptyDir(self,currPath):
        """delete empty directory"""
        if not os.path.isdir(currPath):
            return
        names=os.listdir(currPath)
        if names:
            dirs=[]
            for name in names:
                path=os.path.join(currPath,name)
                if os.path.isdir(path):
                    dirs.append(path)
            for dir in dirs:
                self.delEmptyDir(dir)   
        if os.path.isdir(currPath):
            try:
                os.rmdir(currPath)
                logStr='delete null directory:%s'%currPath
                self.writeInLog(logStr)
            except:
                pass 
                
    def getCondition(self,xmlPath=''):
        """get delete operation from xml file"""
        conditions=DeleteCondition
        conditions.protParam=[]
        dom = xml.dom.minidom.parse(xmlPath)
        paramNodes=dom.getElementsByTagName('protParam')
        protTask=dom.getElementsByTagName('protTask')[0]
        saveSpa=protTask.getAttribute('saveSpa').encode()
        conditions.saveSize=self.realizeSpa(saveSpa)     
        conditions.resultPath=protTask.getAttribute('resultPath').encode()
        logPath=protTask.getAttribute('logPath').encode()
        name='log'+self.getNowDate()+'.txt'
        conditions.logPath=os.path.join(logPath,name) 
        for node in paramNodes:
            path=node.getAttribute('path').encode()
            pattern=node.getAttribute('pattern').encode()
            keyword=node.getAttribute('keyword').encode()
            conditions.protParam.append(ProtParam(path,pattern,keyword))
        return conditions
        
    def realizeSpa(self,saveSpa=''):
        """convert deleteSpa from xml file to digital"""
        pattern=re.compile(r'\d*\.?\d*[G,M,K,T]$')
        match=pattern.match(saveSpa)
        countSize=0L
        if match:
            space=string.atof(filter(lambda ch: ch in '0123456789.',saveSpa))
            char=filter(str.isalpha,saveSpa)
            if char=='K':
                countSize=space*1024
            elif char=='M':
                countSize=space*1024*1024
            elif char=='G':
                countSize=space*1024*1024*1024
            elif char=='T':
                countSize=space*1024*1024*1024*1024
            return countSize
        else:
            return -1 
        
    def removeCharacter(self,saveSpa=''):
        """remove character from result file"""
        space=string.atof(filter(lambda ch: ch in '0123456789.',saveSpa))
        char=filter(str.isalpha,saveSpa)
        if char=='B':
            countSize=space
        elif char=='KB':
            countSize=space*1024
        elif char=='MB':
            countSize=space*1024*1024
        elif char=='GB':
            countSize=space*1024*1024*1024
        elif char=='TB':
            countSize=space*1024*1024*1024*1024
        return countSize
         
    def addCharacter(self,size):
        """add character to log file"""
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
           
           
    def delete(self):
        """delete work flow"""
        if not os.path.exists(self.conditions.logPath):
            print 'Config file has wrong logPath'
            return
        logStr='----------------------------------------------------------'+'\n'+'Start DeleteTask'
        self.writeInLog(logStr)        
        if not os.path.exists(self.conditions.resultPath):
            self.writeInLog('result file does not exisit')
        elif self.conditions.saveSize==-1:
            self.writeInLog('save space is not right format')
        self.readResultFile(self.conditions.resultPath,self.oper) 
        if self.countSize<self.conditions.saveSize:
            self.writeInLog('current size smaller than your configuration')
            self.writeInLog('current size is %s'%str(self.countSize))
            self.writeInLog('save size is %s'%str(self.conditions.saveSize))
        elif len(self.oper)==0:
            logStr='The result file has no files\' information'
            self.writeInLog(logStr)
        else:
            self.sortByTime()
            if not self.tagSaveDir():
                logStr='The result file need to update,find file path does not exist!'
                self.writeInLog(logStr)
                return
            self.run()
            logStr=str(self.getNowTime())+':'+'Begin deleting empty directory'
            self.writeInLog(logStr)
            self.delEmptyDir(self.rootPath)
            logStr='After delete:'
            logStr+='\n'+'current size:%s'%self.addCharacter(self.countSize)
            logStr+='\n'+'protected directory size:%s'%self.addCharacter(self.protectSize)
            logStr+='\n'+'specified save size:%s'%self.addCharacter(self.conditions.saveSize)
            self.writeInLog(logStr)
        logStr='Finish DeleteTask'+'\n'+'----------------------------------------------------------'+'\n'
        self.writeInLog(logStr)
        
    def getNowTime(self):
        """get current time"""
        nowTime=time.localtime()
        d1=datetime.datetime(nowTime[0],nowTime[1],nowTime[2],nowTime[3],nowTime[4],nowTime[5])
        return d1  
    
    def getNowDate(self):
        """get new date"""
        nowTime=time.localtime()
        d1=datetime.date(nowTime[0],nowTime[1],nowTime[2])
        return str(d1)
    
    def writeInLog(self,logString=''):
        """ write string to log file"""
        try:
            f=open(self.conditions.logPath,'a')
        except:
            print 'Open log file occurs exception,path=%s'%self.conditions.logPath
        try:
            f.write('\n'+logString)
        except:
            print 'Write to log occurs exception,path=%s'%self.conditions.logPath
        try:
            f.close()
        except:
            print 'Close log file occurs exception,path=%s'%self.conditions.logPath
        
            
