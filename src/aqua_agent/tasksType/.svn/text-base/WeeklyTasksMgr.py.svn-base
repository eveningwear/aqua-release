"""

    WeeklyTasksMgr.py
    
    Written by: Jacky Li (yxli@adobe.com)

"""

import datetime, time, math
from tasksType.TasksTypeMgr import TasksTypeMgr
from timezone import timezone
   
class childTasksMgr(TasksTypeMgr):

    def __init__(self, overdueDir, scheduleDir, tasklist=[]):
        super(childTasksMgr, self).__init__('Weekly', overdueDir, scheduleDir, tasklist, [0, 0, 7])#1 means 1 day
        
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
        
        t = time.gmtime()
        curtime = datetime.datetime(t[0], t[1], t[2], t[3], t[4], t[5], tzinfo=timezone.GMT())
        
        #Transfer to current timezone
        tz = timezone.getTimeZone(timezoneStr)
        curdate = curtime.astimezone(tz)
        
        curweekday = curdate.weekday()
        expweekday = int(task['weekday']) 
        
        dateList[0] = curdate.year
        dateList[1] = curdate.month
        dateList[2] = curdate.day + (expweekday - curweekday)
        
        schDateTime = self._makeUpSchDateTime(dateList[0], dateList[1], dateList[2],
                                              timeList[0], timeList[1], timeList[2], tz)
        days, seconds = self._compareWithCurTime(schDateTime, tz)
        while days<0 and self.repeat:
            dateList[0] += self.timeTactic[0] #year
            dateList[1] += self.timeTactic[1] #month
            dateList[2] += self.timeTactic[2] * (- math.floor(days/7))
            schDateTime = self._makeUpSchDateTime(dateList[0], dateList[1], dateList[2],
                                                  timeList[0], timeList[1], timeList[2], tz)
            days, seconds = self._compareWithCurTime(schDateTime, tz)
            
        gap = days * 24 * 60 * 60 + seconds
        return gap
        
if __name__ == '__main__':
    class w():
        dbutil=1
    t = childTasksMgr(w(),'Once',2,3);
    
    for i in range(7):
        assert t.tactic({'weekday': i, 'startTime': '11:38:00'}) > 0        
        assert t.tactic({'weekday': i, 'startTime': '16:30:00'}) > 0       