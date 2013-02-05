"""

    MSIInstallerTask.py
    
    This task is just for insatlling msi installer on Windows only
    
    Written by: Jacky Li (yxli@adobe.com)

"""

from allTasks.baseTask import Task

class childTask(Task):
    
    def __init__(self, type, priority):
        super(childTask, self).__init__(type, priority)
        return
        
    def runWin(self):
        self.logger.info('Run MSIInstaller Task')
        if not 'installerPath' in self.parameter or self.parameter['installerPath'] == '':
            self.logger.warning("No installer parameter")
        
        self.installerCmd = 'msiexec /quiet /i "%s"' % self.parameter['installerPath']
        
        if 'targetDir' in self.parameter and self.parameter['targetDir'] != '':
            self.installerCmd += ' TARGETDIR="%s"' % self.parameter['targetDir']
            
        self.runCommand(self.installerCmd)