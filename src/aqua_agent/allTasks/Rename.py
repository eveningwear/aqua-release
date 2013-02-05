"""

    Rename.py
    
    Written by: Jacky Li (yxli@adobe.com)

"""

from allTasks.baseTask import Task
import os,time

class childTask(Task):
    
    def __init__(self, type, priority):
        super(childTask, self).__init__(type, priority)
        return
        
    def runMac(self):
        cmd = 'sudo scutil --set ComputerName ' + self.parameter['hostname']
        self.runCommand(cmd)
        cmd = 'sudo scutil --set LocalHostName ' + self.parameter['hostname']
        self.runCommand(cmd)
        self.modifyHostConfig()
        return
    
    def modifyHostConfig(self):
        inputStr = '#!/bin/bash\n'
        inputStr += 'myhostconfig=/etc/hostconfig\n'
        inputStr += 'cat ${myhostconfig} | grep HOSTNAME\n'
        inputStr += 'res=$?\n'
        inputStr += 'if [ $res = 0  ]; then\n'
        inputStr += '    sudo sed -ie \'/^\HOSTNAME=/s/=.*/=%s/\' ${myhostconfig}\n' %(self.parameter['hostname'])
        inputStr += 'else\n' 
        inputStr += '    sudo sed -ie \'/AFPSERVER=.*/a\\\n'
        inputStr += 'HOSTNAME=%s\n' %(self.parameter['hostname'])
        inputStr += '\' ${myhostconfig}\n'
        inputStr += 'fi\n'
        modifyHostConfig = os.path.join(os.getcwd(), 'modifyHostConfig.sh')
        self.creatFile(modifyHostConfig, inputStr)
        self.runCommand('chmod +x %s' % modifyHostConfig)
        self.runSimpleCommand(modifyHostConfig)
        
        #Reboot machine for activating the hostname
        self.logger.debug('Reboot machine for activating the Hostname')
        
        self.runCommand('sudo reboot')
        time.sleep(888)
        
    def runWin(self):
        cmd = 'reg.exe ADD HKLM\SYSTEM\CurrentControlSet\Control\ComputerName\ComputerName /v ComputerName /d ' + self.parameter['hostname'] + ' /f'
        self.runCommand(cmd)
        cmd = 'reg.exe ADD HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters /v "NV Hostname" /d ' + self.parameter['hostname'] + ' /f'
        self.runCommand(cmd)
        cmd = 'reg.exe ADD HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters /v Hostname  /d ' + self.parameter['hostname'] + ' /f'
        self.runCommand(cmd)
        return
    
    def run(self):
        self.logger.info('Start naming that machine:' + self.parameter['hostname'])
        super(childTask, self).run()
        return
    
if __name__ == '__main__':
    task=childTask('Rename', 1)
    task.addPara('hostname', 'jacky-imac')
    task.modifyHostConfig()