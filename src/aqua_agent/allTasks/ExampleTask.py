"""

    ExampleTask.py
    
    This task is just for example using
    
    Written by: Jacky Li (yxli@adobe.com)

"""

from allTasks.baseTask import Task

class childTask(Task):
    
    def __init__(self, type, priority):
        super(childTask, self).__init__(type, priority)
        return
        
    def runMac(self):
        print 'ExampleTask runMac'
        return
        
    def runWin(self):
        print 'ExampleTask runWin'
        return
    
    def run(self):
        print 'ExampleTask run'
        return