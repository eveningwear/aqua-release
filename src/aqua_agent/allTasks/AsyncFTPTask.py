"""

    AsyncFTPTask.py
    
    Written by: Jacky Li (yxli@adobe.com)

"""

from allTasks.baseTask import Task
import globalProperty

class childTask(Task):
    
    def __init__(self, type, priority = 0):
        super(childTask, self).__init__(type, priority)
        return
        
    def runMac(self):
        self.logger.debug('FTPTask runMac')
        return
        
    def runWin(self):
        self.logger.debug('FTPTask runWin')
        return
    
    def run(self):
        self.logger.debug('AsyncFTPTask run')
        globalProperty.getSyncerPoolManager().runSyncer(self.parameter)
        return