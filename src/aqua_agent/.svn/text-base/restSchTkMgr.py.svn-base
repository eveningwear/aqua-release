"""

    restSchTkMgr.py
    
    Written by: Jacky Li (yxli@adobe.com)

"""

import os.path, sys, os, re, math, time, socket, stat, subprocess

import xml.parsers.expat, ftplib

from taskPriorityDef import *
from xml.dom import minidom,Node
from restWkr import restWkr

import logging
import logging.config

import uuid
import globalProperty

class restSchTkMgr:
    
    def __init__(self):
        self.logger = logging.getLogger()
        self.logger.info('-----Startup restTask schedule Manager')
        
        self.__onceTasksFileList = []
        self.__dailyTasksFileList = []
        self.__weeklyTasksFileList = []
        self.__montylyTasksFileList = []
        self.doc = None
        
    def getNewScheduleTaskFileName(self, jobId=None):
        if jobId:
            name = 'task_%s.tk' % jobId
        else:
            name = 'task_%s.tk' % uuid.uuid1()
        filePath = os.path.join(self.__schedulTaskDir, name)
        return (filePath, name)
    
    def __createDir(self, *dirpath):
        for path in dirpath:
            if not os.path.isdir(path):
                os.mkdir(path)        
    
    def __initDirectory(self):
        self.__taskListDir = globalProperty.getTaskListDir()
        self.__overdueTaskDir = globalProperty.getOverdueDir()
        self.__schedulTaskDir = globalProperty.getSchedulTaskDir()
        self.__createDir(self.__taskListDir, self.__overdueTaskDir, self.__schedulTaskDir)
    
    def initScheduleTask(self):
        self.__initDirectory()
        self.__scheduleTasksFile = os.path.join(self.__taskListDir, 'scheduleTasks.xml')
        if not os.path.exists(self.__scheduleTasksFile):
            #create a new scheduleTasksFile
            self.doc = minidom.Document()
            
            scheduleTasks = self.doc.createElement("ScheduleTasks")
            self.doc.appendChild(scheduleTasks)
            
            onceTasks = self.doc.createElement("ImmediateTasks")
            scheduleTasks.appendChild(onceTasks)
            
            onceTasks = self.doc.createElement("OnceTasks")
            scheduleTasks.appendChild(onceTasks)
            
            dailyTasks = self.doc.createElement("DailyTasks")
            scheduleTasks.appendChild(dailyTasks)
            
            weeklyTasks = self.doc.createElement("WeeklyTasks")
            scheduleTasks.appendChild(weeklyTasks)
            
            monthlyTasks = self.doc.createElement("MonthlyTasks")
            scheduleTasks.appendChild(monthlyTasks)
            
            customizeTasks = self.doc.createElement("CustomizeTasks")
            scheduleTasks.appendChild(customizeTasks)
            
            myTestXML = self.doc.toprettyxml()
            
            self.__writeScheduleXML()
        self.__loadScheduleTask()
        return            
        
    def __removeTextChildNodeRecursion(self, parent):
        textNodeList = []
        for node in parent.childNodes:
            if node.nodeType == node.ELEMENT_NODE:
                self.__removeTextChildNodeRecursion(node)
            elif node.nodeType == node.TEXT_NODE:
                textNodeList.append(node)
                #print parent.nodeName + ':Remove Child ' + node.nodeName
                #parent.removeChild(node)
        for node in textNodeList:
            #print parent.nodeName + ':Remove Child ' + node.nodeName
            parent.removeChild(node)
        
    def __writeScheduleXML(self):        
        scheduleTasks = self.doc.getElementsByTagName("ScheduleTasks")[0]
        self.__removeTextChildNodeRecursion(scheduleTasks)
        f = open(self.__scheduleTasksFile, "w")
        myTestXML = self.doc.toprettyxml()
        f.write(myTestXML)
        f.close()
        
    def __updateScheduleTask(self, tkfile, overdue=False):
        doc = minidom.parse(tkfile)
        tkFileName = os.path.basename(tkfile)
        Tasks = doc.getElementsByTagName("Tasks")[0]
        attrs = {}
        for attr in Tasks.attributes.items():
            attrs[str(attr[0])] = str(attr[1])
        self.updateScheduleTask(tkFileName, attrs, overdue)
        
    def restartTask(self, jobId):
        tkfilename = "task_" + jobId + ".tk"
        overdueJobFile = os.path.join(self.__overdueTaskDir, tkfilename)
        tkfile = os.path.join(self.__schedulTaskDir, tkfilename)
        if os.path.exists(overdueJobFile):
            self.__moveToScheduleDir(tkfilename)
        elif not os.path.exists(tkfile):
            return
        tkfile = os.path.join(self.__schedulTaskDir, tkfilename)
        if os.path.exists(tkfile):
            self.__updateScheduleTask(tkfile)
        
    def stopTask(self, jobId):
        tkfilename = "task_" + jobId + ".tk"
        scheduleJobFile = os.path.join(self.__schedulTaskDir, tkfilename)
        if os.path.exists(scheduleJobFile):
            self.__updateScheduleTask(scheduleJobFile, True)
            self.__moveToOverdueDir(tkfilename)
        else:
            return
        
    def deleteTask(self, jobId):
        tkfilename = "task_" + jobId + ".tk"
        scheduleJobFile = os.path.join(self.__schedulTaskDir, tkfilename)
        overdueJobFile = os.path.join(self.__overdueTaskDir, tkfilename)
        deleteFlag = True
        if os.path.exists(scheduleJobFile):
            try:
                self.__updateScheduleTask(scheduleJobFile, True)
            except Exception, e:
                deleteFlag = False
                self.logger.warning(e)
        
        if os.path.exists(overdueJobFile):
            try:
                self.__updateScheduleTask(overdueJobFile, True)
                os.remove(overdueJobFile)
            except Exception, e:
                deleteFlag = False
                self.logger.warning(e)
        
        if deleteFlag:
            globalProperty.getDbUtil().deleteTask(jobId)
            
    def updateScheduleTask(self, tkfilename, attrs, overdue=False, immediate=False):
        self.logger.debug('Task file ' + tkfilename + '\'s Type:' + str(attrs['type']))
        tks = self.doc.getElementsByTagName(attrs['type'])[0]
        newTask = self.doc.createElement("Task")
        newTask.setAttribute('fileName', tkfilename)
        for key in attrs.keys():
            if key=='type':
                continue
            newTask.setAttribute(key, attrs[key])
        tksMgr = None
        commandStr = 'tksMgr = self.%sMgr' %(attrs['type'])
        exec commandStr
        attrs['fileName'] = tkfilename
        attrs.pop('type')
        #If overdue, the task should be removed
        if overdue or tksMgr.isOverdue(attrs) and tksMgr.needSchedule():
            '''
            tksMgr.removeTask(attrs)
            tasks = self.doc.getElementsByTagName(attrs['type'])[0]
            self.__DeleteTasksFileNode(tasks, attrs)
            self.__moveToOverdueDir(tkfilePath)
            '''
            self.__deleteOverdueTask(tksMgr, attrs)
        else:# Task not overdue, or do not need schedule such as immediate task
            #Write into XML
            if not tksMgr.findTaskByName(tkfilename):
                tks.appendChild(newTask)
                self.__writeScheduleXML()
            
            #Schedule Task
            tksMgr.appendTask(attrs)
            tksMgr.scheduleOneTask(attrs, immediate)
    
    '''
    To update task operation for directing how to schedule task
    
    operation: overdue, stop, start
    @deprecated
    '''
    def updateScheduleTaskOperation(self, tkfilename, operation):
        self.logger.debug('Task file ' + tkfilename + '\'s Operation:' + operation)
        taskNode, type = self.__findTaskNodeAndType(tkfilename)
        if type != None:
            commandStr = 'tksMgr = self.%sMgr' %(type)
            exec commandStr
            # Remove task
            tksMgr.removeTaskByName(tkfilename)
        if taskNode != None:
            taskNode.setAttribute('operation', operation)
            self.__writeScheduleXML()
            
    
    '''
    Find Task and task Type according to task file name
    '''
    def __findTaskAndType(self, tkfilename):
        scheduleTasks = self.doc.getElementsByTagName("ScheduleTasks")[0]
        for node in scheduleTasks.childNodes:
            if node.nodeType == node.TEXT_NODE:
                continue
            self.logger.debug(node.nodeName)
            try:
                commandStr = 'tksMgr = self.%sMgr' %(node.nodeName)
                exec commandStr
                task = tksMgr.findTaskByName(tkfilename)
                if task!=None:
                    return task, node.nodeName
            except:
                self.logger.warning("Find %sMgr occurs some unpredictable issue" %(node.nodeName) )
        return None, None
    
    '''
    Find Task Node and task Type according to task file name
    ''' 
    def __findTaskNodeAndType(self, tkfilename):
        scheduleTasks = self.doc.getElementsByTagName("ScheduleTasks")[0]
        for node in scheduleTasks.childNodes:
            if node.nodeType == node.TEXT_NODE:
                continue
            self.logger.debug(node.nodeName)
            for taskNode in node.childNodes:
                tksFileAttr = self.__getTasksFileAttrs(taskNode)
                if tksFileAttr['fileName'] == tkfilename:
                    return taskNode, node.nodeName
        return None, None
        
    def finishTaskByPath(self, tkfilePath):
        #print tkfilePath
        tkfilename = os.path.basename(tkfilePath)
        #print tkfilename
        task, type = self.__findTaskAndType(tkfilename)
        
        if task==None or type==None:
            self.logger.warning("Job File %s cannot be found" % tkfilename)
            return
        
        commandStr = 'tksMgr = self.%sMgr' %(type)
        exec commandStr
        if tksMgr.isOverdue(task) or not tksMgr.needSchedule():
            #ImmediateTask need not schedule but never overdue
            #OnceTask need schedule but may be overdue
            '''
            tksMgr.removeTask(task)
            tasks = self.doc.getElementsByTagName(type)[0]
            self.__DeleteTasksFileNode(tasks, task)
            self.logger.info('Move finished overdue taskfile ' + tkfilePath + ' to Overdue directory')
            self.__moveToOverdueDir(tkfilePath)
            '''
            if not 'startup' in task or task['startup']!="true":
                self.__deleteOverdueTask(tksMgr, task)
        else:
            '''
            If the task finished is not overdue, the next step is to make it run again
            '''
            tksMgr.scheduleOneTask(task)
            
    
    def __deleteOverdueTask(self, tksMgr, task):
        self.logger.debug('Task ' + str(task['fileName']) + ' is overdue')
        tksMgr.removeTask(task)
        tksTypeNodeName = tksMgr.type + 'Tasks'
        tasks = self.doc.getElementsByTagName(tksTypeNodeName)[0]
        self.__DeleteTasksFileNode(tasks, task)
        self.logger.info('Move finished overdue taskfile ' + task['fileName'] + ' to Overdue directory')
        self.__moveToOverdueDir(task['fileName'])

    def __moveToOverdueDir(self, tkfileName):
        tkfilePath = os.path.join(self.__schedulTaskDir, tkfileName)
        if os.path.exists(tkfilePath):
            self.__moveFileToFolder(tkfilePath, self.__overdueTaskDir)

    def __moveToScheduleDir(self, tkfileName):
        tkfilePath = os.path.join(self.__overdueTaskDir, tkfileName)
        if os.path.exists(tkfilePath):
            self.__moveFileToFolder(tkfilePath, self.__schedulTaskDir)
            
    def __copyFileToFolder(self, file, folder):
        self.logger.debug('Copying file ' + file + ' to the folder ' + folder)
        if sys.platform == 'darwin':
           cmd = 'cp "%s" "%s"' % (file, folder)
           os.popen(cmd).close()
        else:
           cmd = 'copy "%s" "%s"' % (file, folder )
           os.popen(cmd).close()
    
    def __moveFileToFolder(self, file, folder):
        self.__copyFileToFolder(file, folder)
        time.sleep(1)
        targetFile = os.path.join(folder, file)
        if os.path.exists(targetFile):
            self.logger.debug('Removing file ' + file)
            try:
                os.remove(file)
            except Exception, e:
                self.logger.warning(e)
        else:
            self.logger.debug('Failed: Copying file ' + file + ' to the folder ' + folder)
            try:
                os.remove(file)
            except Exception, e:
                self.logger.warning(e)

    def __scheduleTask(self):
        scheduleTasks = self.doc.getElementsByTagName("ScheduleTasks")[0]
        for node in scheduleTasks.childNodes:
            if node.nodeType == node.TEXT_NODE:
                continue
            tasks = self.doc.getElementsByTagName(node.nodeName)[0]
            tasksList = self.__getTasksFileList(tasks)
            importStr = 'from tasksType.%sMgr import childTasksMgr' %(node.nodeName)
            #print importStr
            exec importStr
            tksMgr = childTasksMgr(self.__overdueTaskDir, self.__schedulTaskDir, tasksList)
            commandStr = 'self.%sMgr=tksMgr' %(node.nodeName)
            exec commandStr
            
#            if not tksMgr.needSchedule():
#                continue
            overdueTksList = tksMgr.schedule()
            for task in overdueTksList:
                self.__deleteOverdueTask(tksMgr, task)

    def __loadScheduleTask(self):
        if self.doc==None:
            print self.__scheduleTasksFile
            self.doc = minidom.parse(self.__scheduleTasksFile)
        self.__scheduleTask()
            
    def __getTasksFile_old(self, tasksParent):
        fileName = tasksParent.attributes["fileName"].nodeValue
        startDate = tasksParent.attributes["startDate"].nodeValue
        startTime = tasksParent.attributes["startTime"].nodeValue
        tksFile = tasksFile(fileName, startDate, startTime)
        return tksFile
    
    def __getTasksFileAttrs(self, tasksParent):
        '''
        fileName = tasksParent.attributes["fileName"].nodeValue
        startDate = tasksParent.attributes["startDate"].nodeValue
        startTime = tasksParent.attributes["startTime"].nodeValue
        tksFile = tasksFile(fileName, startDate, startTime)
        return tksFile
        '''
        attrs = {}
        for attr in tasksParent.attributes.items():
            attrs[str(attr[0])] = str(attr[1])        
        return attrs
    
    def __checkReproduceTask(self, tasksFileList, tksFile):
        for tasksFile in tasksFileList:
            if tasksFile.compare(tksFile):
                return True
            
    def __DeleteTasksFileNode(self, tasksParent, task):
        for node in tasksParent.childNodes:
            if node.nodeType == node.TEXT_NODE:
                continue
            else:
                tksFileAttr = self.__getTasksFileAttrs(node)
                if tksFileAttr['fileName'] == task['fileName']:
                    tasksParent.removeChild(node)
        self.__writeScheduleXML()
                
        
    def __getTasksFileList(self, tasksParent):
        tasksFileAttrsList = []
        for node in tasksParent.childNodes:
            if node.nodeType == node.TEXT_NODE:
                continue
            else:
                tksFileAttr = self.__getTasksFileAttrs(node)
                tasksFileAttrsList.append(tksFileAttr)
        return tasksFileAttrsList
    
    def cleanLeakTasks(self):
        scheduleTasks = self.doc.getElementsByTagName("ScheduleTasks")[0]
        for node in scheduleTasks.childNodes:
            if node.nodeType == node.TEXT_NODE:
                continue            
            commandStr = 'tksMgr = self.%sMgr' %(node.nodeName)
            exec commandStr
            '''
                FIXME: sometimes not all the task managers are assigned, as appeared in log:
                
                -----Generete a new Type Manager:Immediate
                -----Generete a new Type Manager:Once
                 Move finished overdue taskfile task_eba9f28f-5dff-11dd-9c09-001aa008bf35.tk to Overdue directory
                -----Generete a new Type Manager:Monthly
                
                'Daily' type is logged, but the task file ...35.tk did contain a daily job
            '''
            if tksMgr and not tksMgr.needSchedule():
                overdueTksList = tksMgr.schedule()
                for task in overdueTksList:
                    self.__deleteOverdueTask(tksMgr, task)

    def getSchedulTaskDir(self):
        return self.__schedulTaskDir

