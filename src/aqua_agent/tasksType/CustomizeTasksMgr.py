"""

    CustomizeTasksMgr.py
    
    Written by: Jacky Li (yxli@adobe.com)

"""

from tasksType.TasksTypeMgr import TasksTypeMgr
import datetime
from timezone import timezone
   
class childTasksMgr(TasksTypeMgr):

    def __init__(self, overdueDir, scheduleDir, tasklist=[]):
        super(childTasksMgr, self).__init__('Customize', overdueDir, scheduleDir, tasklist)#1 means 1 day
        
    '''
    This function is to provide time waiting tactic
    '''  
    def tactic(self, task):        
        startDate = task['startDate']
        startTime = task['startTime']
        dayDuration = int(task['dayDuration'])#This is to implement weekly working time such as from Monday to Friday
        dayGap = int(task['dayGap'])#This means how many days between the task for executing
        eachTimeGap = task['eachTimeGap']#This means how long between same tasks for executing, unit:hour
        duration = task['duration']#This is for counting how many hours for repeating the task, and should less than 24 unit:hour
        timezoneStr = "PST"
        if "timezone" in task:
            timezoneStr = task['timezone']
        
        dateList = startDate.split('-')
        startTimeList = startTime.split(':')
        self._unicodeToInt(dateList)
        self._unicodeToInt(startTimeList)
        
        durationList = duration.split(':')
        eachTimeGapList = eachTimeGap.split(':')
        self._unicodeToInt(durationList)
        self._unicodeToInt(eachTimeGapList)
        
        tz = timezone.getTimeZone(timezoneStr)
        startSchDateTime = datetime.datetime(dateList[0], dateList[1], dateList[2],
                                        startTimeList[0], startTimeList[1], startTimeList[2],
                                        tzinfo=tz)
        endDeltaSeconds = (durationList[0] * 60 + durationList[1]) * 60 + durationList[2]
        endSchDateTime = startSchDateTime + datetime.timedelta(seconds=endDeltaSeconds)
        startDays, startSeconds = self._compareWithCurTime(startSchDateTime, tz)
        endDays, endSencods = self._compareWithCurTime(endSchDateTime, tz)
        
        gap = 0
        if startDays<0:
            startDaysLeft = abs(startDays) % (dayDuration + dayGap)
            endDaysLeft = abs(endDays) % (dayDuration + dayGap)
            
            if startDaysLeft==endDaysLeft:
                if endDaysLeft>=dayDuration:
                    dateList[2] -= (startDays - (dayDuration + dayGap - startDaysLeft) )
                else:
                    dateList[2] -= startDays
                    
                schDateTime = self._makeUpSchDateTime(dateList[0], dateList[1], dateList[2],
                        startTimeList[0], startTimeList[1], startTimeList[2], tz)
                startDays, startSeconds = self._compareWithCurTime(schDateTime, tz)
                gap = startDays * 24 * 60 * 60 + startSeconds
            elif startDaysLeft>endDaysLeft:
                if endDaysLeft>=dayDuration:
                    dateList[2] -= (startDays - (dayDuration + dayGap - startDaysLeft) )
                    schDateTime = self._makeUpSchDateTime(dateList[0], dateList[1], dateList[2],
                        startTimeList[0], startTimeList[1], startTimeList[2], tz)
                    startDays, startSeconds = self._compareWithCurTime(schDateTime, tz)
                    gap = startDays * 24 * 60 * 60 + startSeconds
                else:
                    gap = ( eachTimeGapList[0] * 60 + eachTimeGapList[1] ) * 60 + eachTimeGapList[2]
            else:
                raise "The time must be wrong"
                
        if gap==0:
            gap = startDays * 24 * 60 * 60 + startSeconds
        
        return gap

    def scheduleOneTask(self, task, immediate=False):
        super(childTasksMgr, self).scheduleOneTask(task, immediate)
        