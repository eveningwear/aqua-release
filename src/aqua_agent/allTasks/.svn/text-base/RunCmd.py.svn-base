"""

    RunCmd.py
    
    Written by: Jacky Li (yxli@adobe.com) 

"""
import os

from allTasks.baseTask import Task

class childTask(Task):
    
    def run(self):
        print 'Command task run'
        cmdText = self.parameter['CmdText']
        if cmdText == "cmd":
            raise Exception('Unsupported Command: %s' % cmdText)
        r = os.system(cmdText)
        if r != 0:
            raise Exception('Command returned abnormally, code: %d' % r)
