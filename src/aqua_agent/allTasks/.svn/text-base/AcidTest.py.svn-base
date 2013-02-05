"""

    AcidTest.py
    
    This task is just for example using
    
    Written by: Jacky Li (yxli@adobe.com)

"""
import os.path
from allTasks.baseTask import Task

class childTask(Task):
    
    def __init__(self, type, priority):
        super(childTask, self).__init__(type, priority)
        return
        
    def runMac(self):
        return
        
    def runWin(self):
        cmd = os.path.normpath(str(self.parameter['KickOffPath']))
        if os.path.exists(cmd):
            os.system(cmd)
        return
    
    def run(self):
        super(childTask, self).run()
        return