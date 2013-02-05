"""

    TaskOperation.py
    
    Written by: Jacky Li (yxli@adobe.com)   

"""
import os

from allTasks.baseTask import Task

class childTask(Task):

    def run(self):
        print 'Remove task'
        jobId = self.parameter['JobId']
        operation = self.parameter['TaskOperation']
        fileName = 'task_%s.tk' % jobId
        if self._schTkMgr != None:
            schTkMgr.updateScheduleTaskOperation(fileName, operation)
