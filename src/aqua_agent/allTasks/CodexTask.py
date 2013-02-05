"""

    CodexTask.py
    
    Written by: Jacky Li (yxli@adobe.com)

"""

from allTasks.baseTask import Task
from codex import CodexService
import globalProperty

class childTask(Task):
    
    def __init__(self, type, priority = 0):
        super(childTask, self).__init__(type, priority)
        return
    
    def run(self):
        self.logger.debug('CodexTask run')
        build = None
        if not self.parameter.has_key("CertLevel"):
            self.parameter["CertLevel"] = "Not Tested"
        if not self.parameter.has_key("SubProduct"):
            self.parameter["SubProduct"] = "Application"
        if not self.parameter.has_key("CompileTarget"):
            self.parameter["CompileTarget"] = "Release"
        if not self.parameter.has_key("Format"):
            format = "RIBS Installer"
        else:
            format = self.parameter["Format"]
        
        platforms = self.parameter["Platform"].split(";")
        certLevels = self.parameter["CertLevel"].split(";")
        langs = self.parameter["Language"].split(";")
        for platform in platforms:
            for certLevel in certLevels:
                for lang in langs:
                    build = self.getBuild(
                        self.parameter["Product"],
                        self.parameter["Version"],
                        self.parameter["CompileTarget"],
                        platform,
                        lang,
                        certLevel,
                        self.parameter["SubProduct"],
                        format
                    )
                    latestBuildInDB = self.getBuildFromDB(
                        self.parameter["Product"],
                        self.parameter["Version"],
                        platform,
                        lang,
                        certLevel,
                        self.parameter["SubProduct"]
                    )
                    #if build != None and (latestBuildInDB==None or latestBuildInDB[0] != build._build):
                    if build != None:
                        parameter = self.copyParameter()
                        parameter["Platform"] = platform
                        parameter["CertLevel"] = certLevel
                        parameter["Language"] = lang
                        self.syncBuild(build._location, build._build, parameter)
    
    def getBuild(self, product, version, compiletarget, platform, language='en_US', certlevel='Not Tested', subproduct='Application', format='RIBS Installer'):
        try:
            codex = CodexService()
            self.logger.info("Trying to get build information from Codex")
            builds = codex.getBuilds(product, version, subproduct, compiletarget=compiletarget, platform=platform, language=language, certlevel=certlevel, format=format, status='Available')
        except Exception, e:
            self.logger.warn(e)
            self.logger.info("Restart QMS Due to Error")
            from Restart import childTask
            task = childTask('restart')
            task.run()
            
        '''
        certLevels = codex.getCertLevels()
        for certLevel in certLevels:
            print certLevel._name
        '''
        #builds = codex.getBuilds(product, version, platform, language=language)
        if len(builds)>0:
            return builds[0]
        else:
            return None
    
    def getBuildFromDB(self, product, version, platform, language='en_US', certlevel='Not Tested', subproduct='Application'):
        latestBuild = self._dbutil.getLatestBuild(
                    product,
                    version,
                    platform,
                    language,
                    certlevel,
                    subproduct)
        if latestBuild==None:
            return None
        return latestBuild
    
    def syncBuild(self, location, buildNum, parameter):
        if location['protocol']=='ftp':
            parameter['Host'] = location['server']
            parameter['FilePath'] = location['path']
            parameter['BuildNum'] = buildNum
            if not self.parameter.has_key("BaseDir"):
                parameter['BaseDir'] = self.parameter["Product"]
            
            globalProperty.getSyncerPoolManager().runSyncer(parameter)
            return
        
    def copyParameter(self):
        parameter = {}
        for key in self.parameter.keys():
            parameter[key] = self.parameter[key]
        return parameter
    
    def getBuilds(self, product, version, subproduct, compiletarget, platform, language='en_US', certlevel='Not Tested', format='RIBS Installer'):
        try:
            codex = CodexService()
            self.logger.info("Trying to get build information from Codex")
            builds = codex.getBuilds(product, version, subproduct, compiletarget=compiletarget, platform=platform, language=language, certlevel=certlevel, format=format, status='Available')
        except Exception, e:
            self.logger.warn(e)
            self.logger.info("Restart QMS Due to Error")
            from Restart import childTask
            task = childTask('restart')
            task.run()
            
        return builds

#For testing
if __name__ == "__main__":
    ct = childTask("CodexTask")
    ct.addPara("Product", "Photoshop")
    ct.addPara("Version", "13.0")
    ct.addPara("Platform", "win32")
    ct.addPara("CertLevel", "Build Failed;Not Tested")
    #ct.addPara("CompileTarget", "None")
    ct.addPara("Language", "en_US")
    #ct.addPara("Format", "Installer")
    ct.addPara("Repository", "\\\\ps-builds\\Builds\\")
    ct.addPara("FTPRepository", "ftp://ps-bj-fs/Builds/")
    ct.run()
    