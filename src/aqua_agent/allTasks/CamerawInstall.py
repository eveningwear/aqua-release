"""

    CamerawInstall.py
    
    Written by: Jacky Li (yxli@adobe.com)

"""
from allTasks.AppInstall import childTask
import os, subprocess, zipfile, sys, re
import shutil
            
class childTask(childTask):
    
    def __init__(self, type, priority = 810):
        super(childTask, self).__init__(type, priority)
        self.__camerawPath = None
        return        

    def run(self):
        super(childTask, self).run()
        return
        
    def runWin(self):
        print 'CamerawInstall runWin'
        self._getAppPackage()
           
        for root, dirs, files in os.walk(self.downloadFolder):
            for f in files:
                if (zipfile.is_zipfile(os.path.join(root,os.path.basename(f)))):
                    foldername = self._unzipfile(os.path.join(root,os.path.basename(f)),root)
                    if (str(os.path.basename(f)).lower().startswith("adobecameraraw")):
                        self.__camerawPath = foldername        
        self.__install()
        return

    def runMac(self):
        print 'CamerawInstall runMac'           
        return   
            
    def _generateDeployFile(self):
        outf = os.path.basename(self.__camerawPath)
        stiXml =  outf + ".proxy.xml"
        log = os.path.join(self.__camerawPath, "payloads", outf, stiXml)
    
        try:
            resFile = open(log, 'r', 1024)
        except IOError:
            print 'IOError', sys.exc_value
        for line in resFile:
            if re.search("\"AdobeCode\">{", line):
                    (f1,f2) = line.split('{')
                    (f3,f4) = f2.split('}')
        resFile.close()
    
        deployfile = os.path.join(self.__camerawPath, "deploy.xml")
        file = open(deployfile, 'w') 
        file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
        file.write("<Deployment><Payloads><Payload adobeCode=\"{%s}\"><Action>install</Action></Payload></Payloads></Deployment>" % (f3))
        file.close()
    
        uninstallf = os.path.join(self.__camerawPath, "uninstall.xml")
        file2 = open(uninstallf, 'w')
        file2.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
        file2.write("<Deployment><Payloads><Payload adobeCode=\"{%s}\"><Action>remove</Action></Payload></Payloads></Deployment>" % (f3))
        file2.close()
    
        setup = os.path.join(self.__camerawPath, "Setup.exe")
    
        return (setup, deployfile, uninstallf, outf)
    
    def __install(self):
        (setup, deployfile, uninstallf, outf) = self._generateDeployFile()
        cmd = setup + ' --mode=silent --deploymentFile=' + deployfile
        print cmd
        os.system(cmd)
    
