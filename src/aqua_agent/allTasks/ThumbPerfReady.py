"""

    ThumbPerfReady.py
    
    This task is just for Testwerk Thumb Perf using
    
    Written by: Jacky Li (yxli@adobe.com)

"""

from allTasks.baseTask import Task
import globalProperty

class childTask(Task):
    
    def __init__(self, type, priority):
        super(childTask, self).__init__(type, priority)
        return
    
    def run(self):
        print 'ThumbPerfReady run'
        
        from QMSWebService import QMSWebService
        qmsWS = QMSWebService()
        self.logger.info('The machine is get ready for Thumb Performance Testing')
        
        if 'appBuild' in self.parameter.keys() and self.parameter['appBuild'].strip() != '':
            appBuild = self.parameter['appBuild']
        else:
            appBuild = globalProperty.getLatestBuildNum('Bridge',
                                                        '4.0',
                                                        globalProperty.getPlatform(),
                                                        'mul',
                                                        'Build Failed')
            
        qmsWS.kickOffTestwerkThumbPerfTest(
                                           self.parameter['kickOffMachineAddress'], 
                                           self.macAddress, 
                                           self.parameter['caseType'], 
                                           self.parameter['testType'], 
                                           self.parameter['appVersion'], 
                                           self.parameter['sendResult'], 
                                           appBuild)
        return

if __name__ == '__main__':
    task = childTask('xx', 1)
    task.addPara("kickOffMachineAddress", "00-50-56-c0-00-08")
    task.addPara("caseType", "launch")
    task.addPara("testType", "1")
    task.addPara("appBuild", "APIP226")
    task.addPara("appVersion", "CS5")
    task.addPara("sendResult", "No")
    task.run()
