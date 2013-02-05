"""

    TasksTypeMgr.py
    
    Written by: Jacky Li (yxli@adobe.com)

"""

import os.path, sys, os, re, math, time, socket, stat, subprocess, datetime
import xml.parsers.expat, ftplib
import logging
import globalProperty
from threading import Timer
from timezone import timezone

class TasksTypeMgr(object):

    #timeTactic = [year, month, day]
    def __init__(self, type, overdueDir, scheduleDir, tasklist=[], timeTactic=[0, 0, 0], repeat=True):
        self.logger = logging.getLogger()
        self.logger.info('-----Generete a new Type Manager:' + type)
        self._worker = globalProperty.getRestWorkerInstance()
        self._dbutil = globalProperty.getDbUtil()
        
        self.type = type
        self.overdueDir = overdueDir
        self.scheduleDir = scheduleDir
        self.tasklist = tasklist
        self.timeSpaceHolder = ['0', '0', '0'] * 3
        self.timeTactic = timeTactic
        self.repeat = repeat
        
        self.__timerDic = {}
        
    def _unicodeToInt(self, l):
        for i in range(len(l)):
            l[i] = int(l[i])
            
    #Determine whether it's overdue, default is False
    def isOverdue(self, task):
        return False
    
    '''
    This faction is to provide time waiting tactic
    '''  
    def tactic(self, task):        
        startDate = task['startDate']
        startTime = task['startTime']
        timezoneStr = "PST"
        if "timezone" in task:
            timezoneStr = task['timezone']
            
        dateList = startDate.split('-')
        timeList = startTime.split(':')
        self._unicodeToInt(dateList)
        self._unicodeToInt(timeList)
        
        tz = timezone.getTimeZone(timezoneStr)
        schDateTime = datetime.datetime(dateList[0], dateList[1], dateList[2],
                                        timeList[0], timeList[1], timeList[2],
                                        tzinfo=tz)
        days, seconds = self._compareWithCurTime(schDateTime, tz)
        while days<0 and self.repeat:
            if self.timeTactic[0:2]==[0, 0]:
                dateList[2] -= days
            else:
                dateList[0] += self.timeTactic[0] #year
                dateList[1] += self.timeTactic[1] #month
                dateList[2] += self.timeTactic[2] #day
                
            schDateTime = self._makeUpSchDateTime(dateList[0], dateList[1], dateList[2],
                                         timeList[0], timeList[1], timeList[2], tz)
            #schDateTime = datetime.datetime(dateList[0], dateList[1], dateList[2],
            #                                timeList[0], timeList[1], timeList[2],
            #                                tzinfo=tz)
            days, seconds = self._compareWithCurTime(schDateTime, tz)
            
        gap = days * 24 * 60 * 60 + seconds
        return gap
        """
        dateList = startDate.split('-')
        timeList = startTime.split(':') + self.timeSpaceHolder
        dateList.extend(timeList)
        self._unicodeToInt(dateList)
        stdDateTuple = tuple(dateList[0:9])
        schDateTime = time.mktime(stdDateTuple)
        gap = self._returnGap(schDateTime)
        while(gap < 0 and self.repeat):
            dateList[0] += self.timeTactic[0] #year
            dateList[1] += self.timeTactic[1] #month
            dateList[2] += self.timeTactic[2] #day
            stdDateTuple = tuple(dateList[0:9])
            newSchDateTime = time.mktime(stdDateTuple)
            gap = self._returnGap(newSchDateTime)

        nextStartDate = '-'.join((str(dateList[0]), str(dateList[1]), str(dateList[2])))
        nextStartTime = ':'.join((str(dateList[3]), str(dateList[4]), str(dateList[5])))
#        self.logger.info('Task ' + str(task['fileName']) + ' will be kicked off on ' + nextStartDate + ' ' + nextStartTime)
        return gap
        """
        
    def _makeUpSchDateTime(self, year, month, day, hour, minute, second, tzinfo):
        newSchDate = time.localtime(time.mktime([int(year), int(month), int(day),
                                    int(hour), int(minute), int(second),
                                    0, 0, 0]))
        schDateTime = datetime.datetime(newSchDate[0], newSchDate[1], newSchDate[2],
                                        hour, minute, second,
                                        tzinfo=tzinfo)
        return schDateTime
    
    def _returnGap(self, scheduleTime):
        currentTime = time.time()
        gap = scheduleTime - currentTime
        return gap
    
    def _compareWithCurTime(self, scheduleDateTime, tzinfo):
        #t = time.gmtime()
        #curtime = datetime.datetime(t[0], t[1], t[2], t[3], t[4], t[5], tzinfo=timezone.GMT())
        curtime = datetime.datetime.now(tzinfo)
        delta = scheduleDateTime - curtime
        return delta.days, delta.seconds
    
    def setTimeTactic(self, timeTactic):
        self.timeTactic = timeTactic
    
    def schedule(self):
        overdueTaskList = []
        for task in self.tasklist:
            taskOperation = 'start'
            if task.has_key('operation'):
                taskOperation = task['operation']
            tksFilePath = os.path.join(self.scheduleDir, task['fileName'])
            if not os.path.exists(tksFilePath):
                overdueTaskList.append(task)
            elif self.isOverdue(task):#Only affected to OnceTask now
                overdueTaskList.append(task)
            elif taskOperation == 'overdue':
                overdueTaskList.append(task)
            elif self._worker.getPendingTaskFileName()==task['fileName']:#Avoid schedule task repeatedly
                continue
            elif taskOperation == 'stop':#Stop task but not removed
                continue
            else:
                self.logger.info('Schedule a new ' + self.type + ' task' + str(task))
                self.scheduleOneTask(task)
        return overdueTaskList

    def scheduleOneTask(self, task, immediate=False):
        if immediate:
            waitTime = 0
        else:
            waitTime = self.tactic(task) + 1
        t = time.gmtime()
        curtime = datetime.datetime(t[0], t[1], t[2], t[3], t[4], t[5], tzinfo=timezone.GMT())
        dt = curtime + datetime.timedelta(seconds=waitTime)
        
        dateFormat = dt.astimezone(timezone.getTimeZone(globalProperty.getTimeZone())).strftime("%Y-%m-%d %H:%M:%S %A (%Z)")
            
        #content = globalProperty.getRestSchTkMgrInstance().getContentOfJob(task['fileName'])
        self._dbutil.addNewScheduleJob(task, self.type, dateFormat)
        self.logger.info('Task %s will be kicked off on %s' % (str(task['fileName']), dateFormat))
            
        fileName = task['fileName']
        funcArgs = [str(fileName)]
        funcKwargs = task
        t = Timer(waitTime, self.popUpTaskHandle, funcArgs, funcKwargs)
        timerName = 'timer_%s' %fileName
        t.setName(timerName)
        t.start()
        
        #Record timer
        self.__timerDic[fileName] = t
        
    
    def removeTaskByName(self, taskFileName):
        try:
            for task in self.tasklist:
                if task['fileName']==taskFileName:
                    self.tasklist.remove(task)
                    if self.__timerDic.has_key(taskFileName):
                        timer = self.__timerDic[taskFileName]
                        timer.cancel()
                        break
        except:
            print self.type + 'TasksMgr failed to remove task:' + taskFileName
        
    
    def removeTask(self, task):
        try:
            for tk in self.tasklist:
                if tk['fileName'] == task['fileName']:
                    self.tasklist.remove(tk)
                    taskFileName = tk['fileName']
                    if self.__timerDic.has_key(taskFileName):
                        timer = self.__timerDic[taskFileName]
                        timer.cancel()
                        break
        except:
            print self.type + 'TasksMgr failed to remove task:' + str(task['fileName'])

    def appendTask(self, task):
        self.tasklist.append(task)

    def findTaskByName(self, taskFileName):
        for task in self.tasklist:
            if task['fileName']==taskFileName:
                return task
        return None
    
    def needSchedule(self):
        return True
    
    """
    args: [fileName]
    """
    def popUpTaskHandle(self, *args, **kwargs):
        taskFile = os.path.join(self.scheduleDir, args[0])
        if os.path.exists(taskFile):
            self._worker.addTaskFile(args[0], kwargs)
        else:
            print 'should remove the taskFile'
