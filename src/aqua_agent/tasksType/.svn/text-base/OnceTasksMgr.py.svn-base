"""

    OnceTasksMgr.py
    
    Written by: Jacky Li (yxli@adobe.com)

"""

import datetime, time
from tasksType.TasksTypeMgr import TasksTypeMgr

import globalProperty
   
class childTasksMgr(TasksTypeMgr):

    def __init__(self, overdueDir, scheduleDir, tasklist=[]):
        super(childTasksMgr, self).__init__('Once', overdueDir, scheduleDir, tasklist, repeat=False)#1 means 1 day
        
    '''
    This faction is to provide time waiting tactic    
    def tactic(self, task):
        startDate = task['startDate']
        startTime = task['startTime']
        dt = datetime.datetime.strptime('%s %s' % (startDate, startTime), '%Y-%m-%d %H:%M:%S')
        return time.mktime(dt.timetuple()) - time.time()
    '''
        
    def isOverdue(self, task):
        if self.isDoing(task):
            return False
        waitTime = self.tactic(task)
        if waitTime<0:
            return True
        return False
                    
    def scheduleOneTask(self, task, immediate=False):
        if self.isDoing(task):
            return
        # For task only run once, if overdue, we should not launch it
        super(childTasksMgr, self).scheduleOneTask(task, immediate)
        
    def isDoing(self, task):
        return globalProperty.getRestWorkerInstance().getPendingTaskFileName() == task['fileName']

if __name__ == '__main__':
    class w():
        dbutil=1
    t = childTasksMgr(w(),'Once',2,3);
    assert t.tactic({'startDate': '2008-08-29', 'startTime': '10:38:00'}) < 0
    assert t.tactic({'startDate': '2008-09-29', 'startTime': '10:38:00'}) > 0