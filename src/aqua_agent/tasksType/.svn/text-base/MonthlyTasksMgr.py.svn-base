"""

    MonthlyTasksMgr.py
    
    Written by: Jacky Li (yxli@adobe.com)

"""
import datetime, time, calendar
from tasksType.TasksTypeMgr import TasksTypeMgr
from timezone import timezone
   
class childTasksMgr(TasksTypeMgr):

    def __init__(self, overdueDir, scheduleDir, tasklist=[]):
        super(childTasksMgr, self).__init__('Monthly', overdueDir, scheduleDir, tasklist, [0, 1, 0])#1 means 1 month
    

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
        
        dateList[0] = curdate.year
        dateList[1] = curdate.month
        dateList[2] = curdate.day
        
        if task.has_key('nthday'):
            nthday = int(task['nthday'])
            schDateTime = datetime.datetime(dateList[0], dateList[1], nthday,
                                            timeList[0], timeList[1], timeList[2],
                                            tzinfo=tz)
            days, seconds = self._compareWithCurTime(schDateTime, tz)
            while days<0 and self.repeat:
                dateList[0] += self.timeTactic[0] #year
                dateList[1] += self.timeTactic[1] #month
                dateList[2] += self.timeTactic[2] #day
                schDateTime = self._makeUpSchDateTime(dateList[0], dateList[1], nthday,
                                              timeList[0], timeList[1], timeList[2], tz)
                days, seconds = self._compareWithCurTime(schDateTime, tz)
        else:
            which = int(task['whichWeekday'])
            weekday = int(task['weekday'])
            
            day = self.weekdayToDay(dateList[0], dateList[1], which, weekday)
            schDateTime = datetime.datetime(dateList[0], dateList[1], day,
                                            timeList[0], timeList[1], timeList[2],
                                            tzinfo=tz)
            days, seconds = self._compareWithCurTime(schDateTime, tz)
            while days<0 and self.repeat:
                dateList[0] += self.timeTactic[0] #year
                dateList[1] += self.timeTactic[1] #month
                dateList[2] += self.timeTactic[2] #day
                day = self.weekdayToDay(dateList[0], dateList[1], which, weekday)
                schDateTime = self._makeUpSchDateTime(dateList[0], dateList[1], day,
                                                      timeList[0], timeList[1], timeList[2], tz)
                days, seconds = self._compareWithCurTime(schDateTime, tz)
                
        gap = days * 24 * 60 * 60 + seconds
        return gap

    """
    def tactic(self, task):
        startTime = task['startTime']
        now = datetime.datetime.now()
        dt = datetime.datetime.strptime('%d-%d-%d %s' % (now.year, now.month, now.day, startTime), '%Y-%m-%d %H:%M:%S')

        if task.has_key('nthday'):
            nthday = int(task['nthday'])
            if now.day == nthday:
                diff = time.mktime(dt.timetuple()) - time.time()
                if diff > 0:
                    return diff
            dt = dt.replace(day=nthday)
            if dt.day <= now.day:
                m = dt.month
                m = (m + 1) % 12
                tryNext = True
                while tryNext:
                    try:
                        dt = dt.replace(month=m)
                        tryNext = False
                    except ValueError:
                        m += 1      # m won't be 13
                        continue
                    
            print dt.isoformat()
            return time.mktime(dt.timetuple()) - time.time()
        else:
            which = int(task['whichWeekday'])
            weekday = int(task['weekday'])
            
            day = self.weekdayToDay(now.year, now.month, which, weekday)
            if day == now.day:
                diff = time.mktime(dt.timetuple()) - time.time()
                if diff > 0:
                    return diff
            if day > now.day:
                dt = dt.replace(day=day)
            else:
                m = (now.month + 1) % 12
                day = self.weekdayToDay(now.year, m, which, weekday)
                dt = dt.replace(month=m, day=day)

            print dt.isoformat()
            return time.mktime(dt.timetuple()) - time.time()
    """
    
    def weekdayToDay(self, year, month, which, weekday):
        if month>12:
            year = year + month/12
            month = month%12
            if month==0:
                year = year - 1
        c = calendar.Calendar(weekday)
        monthday = c.monthdayscalendar(year, month)
        _array = [0, 1, 2, 3, 4]
        if not monthday[0][0]:
            _array = _array[1:]
        if len(monthday) == 4 or not monthday[4][0]:
            _array = _array[:-1]
        return monthday[_array[which]][0]
        
if __name__ == '__main__':
    class w():
        dbutil=1
    t = childTasksMgr(w(), 'Once', 2, 3);
    for i in range(1, 32):
        assert t.tactic({'nthday': i, 'startTime': '10:38:00'}) > 0
        assert t.tactic({'nthday': i, 'startTime': '15:38:00'}) > 0
    
    for i in range(-1, 4):
        for j in range(0, 7):
            assert t.tactic({'whichWeekday': i, 'weekday': j, 'startTime': '11:38:00'}) > 0
            assert t.tactic({'whichWeekday': i, 'weekday': j, 'startTime': '15:38:00'}) > 0
