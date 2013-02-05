"""

    RemoteConnect.py
    
    Written by: Lei Nie (nlei@adobe.com) 

"""
import os,subprocess

from allTasks.baseTask import Task

class childTask(Task):
    
    def run(self):
        print 'Remote Connect Task run'
        osType=self.parameter['OsType']
        ipAddress = self.parameter['IpAddress']
        toolsDir = os.path.join(os.getcwd(), 'tools')
        
        if osType == 'win':
            if os.name == 'nt':
                cmd = 'mstsc /v:'+ ipAddress
            else:
                cmd = 'open ' + toolsDir+'/RDC.app '
            outPutStr= subprocess.Popen("qwinsta /server:localhost", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()
            
            r = os.system(cmd)
            if r != 0:
                raise Exception('Remote Connect returned abnormally, code: %d' % r)
        elif osType == 'mac':
            if os.name == 'nt':
                cmd = toolsDir+'/vncviewer '+ ipAddress
            else:
                cmd = 'open /System/Library/CoreServices/Screen\ Sharing.app'
                #cmd = 'open ' + toolsDir+'/VNCViewer.app'
            
            r = os.system(cmd)
            if r != 0:
                raise Exception('Remote Connect returned abnormally, code: %d' % r)
