"""

    MiniBrPerfTestTask.py
    
    Written by: Jacky Li (yxli@adobe.com)

"""
import os,zipfile,shutil,re

from allTasks.baseTask import Task
from allTasks.PSFCaseAreaParser import PSFCaseAreaParser
from xml.dom import minidom,Node
import globalProperty

class childTask(Task):
    
    def __init__(self, type, priority):
        super(childTask, self).__init__(type, priority)
        return
        
    def runMac(self):
        self.logger.debug('MiniBRPerfTestTask runMac')
        return
        
    def runWin(self):
        self.logger.debug('MiniBRPerfTestTask runWin')
        return
    
    def run(self):
        self.logger.debug('MiniBRPerfTestTask run')
        from ScarfTask import childTask
        task = childTask('ScarfTask')
        task.addPara("product", "Mini Bridge")
        testSuiteFile = ''.join(self.parameter['testSuite'].split()) + '.xml'
        task.addPara("tcSuiteFiles", testSuiteFile)
        task.run();
        return
        
    def __getScarfScript(self):
        pass
    
    def __launchScarf(self):
        pass
    
    def parseSuiteController(self):
        pass
        
if __name__ == '__main__':
    task = childTask('xx', 1)
    task.run();
    
        
