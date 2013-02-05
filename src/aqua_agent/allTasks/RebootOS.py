"""

    RebootOS.py
    
    Written by: Jacky Li (yxli@adobe.com)

"""

from allTasks.baseTask import Task
import os, os.path, re, time, sys

class childTask(Task):
    
    def __init__(self, type, priority):
        super(childTask, self).__init__(type, priority)
        return
        
    def runMac(self):
        cmd = 'sudo /sbin/reboot'
        self.runCommand(cmd)
        self.logger.debug('rebooting')
        time.sleep(888)
        sys.exit(0)
        return
        
    def runWin(self):
        cmd = 'SHUTDOWN -r -t 01'
        self.runCommand(cmd)
        self.logger.debug('rebooting')
        time.sleep(888)
        sys.exit(0)
        return
    
    def run(self):
        self.logger.info('Start rebooting OS')
        if 'timeLength' in self.parameter:
            self.logger.info('This machine will be rebooted in %s seconds' % self.parameter['timeLength'])
            time.sleep(int(self.parameter['timeLength']))
        self.logger.info('This machine is rebooting')
        super(childTask, self).run()
        return