"""

    RunSikuli.py
    
    Written by: Jacky Li (yxli@adobe.com) 

"""
import re, os
import globalProperty

from allTasks.baseTask import Task

class childTask(Task):
        
    def __init__(self, type, priority):
        super(childTask, self).__init__(type, priority)
        
        self.launcherFileName = "sikuliLauncher"
        self.sikuliScriptHome = os.path.join(os.getcwd(), "sikuli", "automationsikuli")
        self.launcherFilePath = None
        self.sikuliJar = None
        self.buildNum = ""
        
    def run(self):
        self.logger.info('Run Sikuli Task')
        super(childTask, self).run()
        
        self.__getLatestBuildNumber()
        
        if self.sikuliJar:
            self.__prepareLauncher()
            self.logger.debug("Sikuli automation test is kicked off")
            self.runSimpleCommand(self.launcherFilePath)
        
    def runWin(self):
        programfile = os.getenv("ProgramFiles")
        programfileX86 = os.getenv("ProgramFiles(x86)")
        sikuliHome = None
        if programfileX86:
            sikuliHome = self._straightSearchFile(programfileX86, r'[sS]ikuli.*')
        else:
            sikuliHome = self._straightSearchFile(programfile, r'[sS]ikuli.*')
        if sikuliHome:
            self.sikuliJar = self.__getSikuliJar(sikuliHome)
    
    def runMac(self):
        application = "/Applications"
        sikuliHome = self._straightSearchFile(application, r'[sS]ikuli.*')
        if sikuliHome:
            self.sikuliJar = self.__getSikuliJar(sikuliHome)
           
    def runSimpleCommand(self, cmd):
        cmdStr = '\"' + cmd + '\"'
        self.logger.debug(cmdStr)
        os.system(cmdStr)
    
    def __prepareLauncher(self):
        tmpDir = globalProperty.getTmpDir()
        if not os.path.exists(tmpDir):
            os.makedirs(tmpDir)
            
        sikuliScript = "TestSuiteSmoke.sikuli"
        if 'sikuliScript' in self.parameter and self.parameter['sikuliScript'] != '':
            sikuliScript = "%s.sikuli" % self.parameter['sikuliScript']
            
        if os.name == 'posix':
            self.launcherFileName += ".sh"
            self.launcherFilePath = os.path.join(tmpDir, self.launcherFileName)
            inputStr = "#!/bin/sh\n"
            inputStr += 'cd "%s"\n' % self.sikuliScriptHome
            inputStr += 'java -jar "%s" %s "%s"' % (self.sikuliJar, sikuliScript, self.buildNum)
            self.creatFile(self.launcherFilePath, inputStr)
            #Add execution
            self.runCommand('chmod +x %s' % self.launcherFilePath)
        
        elif os.name == 'nt':
            self.launcherFileName += ".cmd"
            self.launcherFilePath = os.path.join(tmpDir, self.launcherFileName)
            inputStr = 'cd /d "%s"\n' % self.sikuliScriptHome
            inputStr += 'java -jar "%s" %s "%s"' % (self.sikuliJar, sikuliScript, self.buildNum)
            self.creatFile(self.launcherFilePath, inputStr)
    
    def __getSikuliJar(self, sikuliHome):
        sikuliJar = self._searchFile(sikuliHome, "sikuli-script.jar")
        return sikuliJar
    
    def __getLatestBuildNumber(self):
        if 'buildNum' in self.parameter and self.parameter['buildNum'] != None:
            self.buildNum = self.parameter['buildNum']
        else:
            import AppInstall
            task = AppInstall.childTask('appInstall')
            task.addPara('appName', 'Photoshop')
            task.addPara('appVer', self.parameter['ProductVersion'])
            task.addPara('appSubProduct', 'Application')
            self.buildNum = task._getInstalledBuildNum()
            
        if self.buildNum!="" and self.buildNum!=None:
            pass
        elif 'molecule' in self.parameter:
            moleculeReStr = "\d{8}\." + self.parameter['molecule'] + "\.\d{1,}"
            from CodexTask import childTask
            task = childTask('codexTask')
            self.buildNum = "unknown"
            builds = task.getBuilds(
                                    'Photoshop',
                                    self.parameter['ProductVersion'],
                                    "Molecule",
                                    "Release", #CompileTarget
                                    self.platform,
                                    globalProperty.getSysInfo().locale,
                                    'Build Failed')
            if builds==None:
                return None
                
            latestBuildLocation = None
            for build in builds:
                if re.match(moleculeReStr, build._build):
                    latestBuildLocation = build._location['protocol'] + "://" + \
                                          build._location['server'] + \
                                          build._location['path']
                
                    self.buildNum = build._build
                    break
        else:
            if globalProperty.isMachineOutOfChina():
                #Support the machine out of China, will download directly
                import CodexTask
                task = CodexTask.childTask('codexTask')
                latestBuild = task.getBuild(
                                      'Photoshop',
                                      self.parameter['ProductVersion'],
                                      "Release", #CompileTarget
                                      self.platform,
                                      globalProperty.getSysInfo().locale,
                                      'Build Failed')
                if latestBuild==None:
                    return None
                
                self.buildNum = latestBuild._build
            else:
                self.buildNum = globalProperty.getLatestBuildNum('Photoshop',
                                                                 self.parameter['ProductVersion'],
                                                                 self.platform,
                                                                 globalProperty.getSysInfo().locale,
                                                                 'Build Failed',
                                                                 'Application')
                
##################This section is mainly for debug -- Begin #############################
if __name__ == '__main__':
    runSikuli = childTask('RunSikuli', 1)
    runSikuli.run()