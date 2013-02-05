"""

    AutoDelete.py
    
    Written by: Lei Nie (nlei@adobe.com)

"""

from baseTask import Task
import os, os.path, re, time, sys
from xml.dom import minidom,Node
import Read,Delete
#sys.path.append("..")
import globalProperty

class childTask(Task):
    
    def __init__(self, type, priority):
        super(childTask, self).__init__(type, priority)
    
    def run(self):
        self.logger.info('Starting Auto Delete task')
        self.logger.info('Starting ReadTask')
        r=Read.ReadTask(r'D:\newdata.xml')
        r.read()
        self.logger.info('Starting DeleteTask')
        d=Delete.DeleteTask(r'D:\newdata.xml')
        d.delete()
        self.logger.info('Finish Auto Delete task')

##################This section is mainly for debug -- Begin #############################
if __name__ == '__main__':    
    crt=childTask('crt', 1)
    crt.addPara('OSImageLocation', 'test1')
    crt.addPara('InstalledSoftware', 'test2')
    crt.run()
##################This section is mainly for debug -- End #############################
