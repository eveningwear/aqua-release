"""

    ImmediateTasksMgr.py
    
    Written by: Jacky Li (yxli@adobe.com)

"""

from tasksType.TasksTypeMgr import TasksTypeMgr
   
class childTasksMgr(TasksTypeMgr):

    def __init__(self, overdueDir, scheduleDir, tasklist=[]):
        super(childTasksMgr, self).__init__('Immediate', overdueDir, scheduleDir, tasklist, repeat=False)
        
    '''
    This faction is to provide time waiting tactic
    '''
    def tactic(self, task): #Immediate Task needs not wait
        return 0
    
    def isOverdue(self, task):
        return False
    
    def needSchedule(self):
        return False  
