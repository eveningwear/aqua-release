"""

    DailyTasksMgr.py
    
    Written by: Jacky Li (yxli@adobe.com)

"""

from tasksType.TasksTypeMgr import TasksTypeMgr
   
class childTasksMgr(TasksTypeMgr):

    def __init__(self, overdueDir, scheduleDir, tasklist=[]):
        super(childTasksMgr, self).__init__('Daily', overdueDir, scheduleDir, tasklist, [0, 0, 1])#1 means 1 day
