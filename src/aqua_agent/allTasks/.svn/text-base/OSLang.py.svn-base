"""

    OSLang.py
    
    Written by: Jacky Li (yxli@adobe.com) 

"""
import os,time

from allTasks.baseTask import Task

class childTask(Task):
    
    macLangDic = {
               "en_US": "en",
               "ja_JP": "ja",
               "de_DE": "de",
               "fr_FR": "fr",
               "zh_CN": "zh-Hans",
               "ru_RU": "ru"
               }
    
    def __init__(self, type, priority):
        super(childTask, self).__init__(type, priority)
        return
        
    def runMac(self):
        self.logger.info('Start Changing the OS Language to: ' + self.parameter['osLang'])
        cmd = 'defaults write ~/Library/Preferences/.GlobalPreferences AppleLanguages \'(%s)\'' % self.macLangDic[self.parameter['osLang']]
        self.logger.info(cmd)
        self.logger.info(self.runCommand(cmd))
        cmd = 'defaults write ~/Library/Preferences/.GlobalPreferences AppleLocale \'%s\'' % self.parameter['osLang']
        self.logger.info(cmd)
        self.logger.info(self.runCommand(cmd))        
        self.logger.debug('Reboot machine for activating the OS Language after 10 seconds')
        time.sleep(10)
        self.runCommand('sudo reboot')
        time.sleep(888)
        return
        
    def runWin(self):
        self.logger.info('Not Support on Windows')
        return
    
    def run(self):
        super(childTask, self).run()
        return
    
if __name__ == '__main__':
    task=childTask('OSLang', 1)
    task.addPara('osLang', 'zh_CN')
    task.run()
