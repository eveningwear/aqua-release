"""

    KillTask.py
    
    Written by: Jacky Li (yxli@adobe.com)

"""

import os, sys
from allTasks.baseTask import Task
    
class childTask(Task):
    
    def __init__(self, type, priority = 0):
        super(childTask, self).__init__(type, priority)
        return
    
    def run(self):
        if 'exefileName' in self.parameter:
            pids = self.__getProcID(self.parameter["exefileName"])
            for pid in pids:
                self.__killByPID(pid)
        return
   
    def __getProcID(self, exefileName, procID = None):
       """
          Try to get the Proc Id's of any running processes
          If passed procID, then filter the list of running processes
          to only return that one.  This means that if the procID
          is running, it will return it, and if not, it will return
          an empty list.
       """
       osversion = osver.getOSVer()
    
       pidlist = []
    
       if sys.platform == "win32":
          if osversion >= osver.WINXP:
             #cmd = "tasklist /FO CSV /NH /FI \"IMAGENAME eq %s\"" % (exefileName)
             cmd = "tasklist /FO CSV | find \"%s\"" % (exefileName)
             cmdobj = os.popen(cmd)
             for line in cmdobj:
                if line.startswith("INFO"):
                   cmdobj.close()
                   return None
                elif line.startswith("\""):
                   infolist = line.rstrip().split(",")
                   pidlist.append(int(infolist[1].strip("\"")))
             cmdobj.close()
          else:
             cmd = "tlist | find \"%s\"" % (exefileName)
             cmdobj = os.popen(cmd)
             p = cmdobj.read().strip()
             cmdobj.close()
             if p != "":
                thePid = p.split( " %s" % (exefileName) )
                pidlist.append(int(thePid[0]))
             else:
                return None
    
       elif sys.platform == "darwin":
          cmd = "ps -cx | grep %s" % exefileName
          cmdobj = os.popen(cmd)
          for line in cmdobj:
             infolist = line.strip().split()
             if infolist[0].isdigit() and exefileName in infolist:
                # the pid is a number, and "Bridge" is the name
                # of the command.
                pidlist.append(int(infolist[0]))
       else:
          return ()
    
       if procID:
          # only return the procID or empty list
          if procID in pidlist:
             return tuple((procID,))
          else:
             return ()
       else:
          return tuple(pidlist)
            
    def __killByPID(self, pid):
       """
       Kill a process with the given PID.
       """
       
       if sys.platform == "win32":
          osversion = osver.getOSVer()
          if osversion >= osver.WINXP:
             cmd = "taskkill /F /PID %s /T" % (pid)
          elif osversion >= osver.WIN2K:
             cmd = "kill %s" % (pid)
       elif sys.platform == "darwin":
          cmd = "kill -9 %d" % (pid)
       else:
          return None
       
       os.popen(cmd).close()
       return 0
   
class osver:
    WINNT = 400000
    WIN2k = 500000
    WINXP = 510000
    WIN2003 = 520000
    TIGER = 10400
    PANTHER = 10300
    JAGUAR = 10200
    
    @staticmethod
    def getOSVer():
       """
       Retrieve the OS version and convert it to an integer.
       The version may have more numbers, but the first two
       or three are what's really important.
       """
       if sys.platform == "win32":
          (major, minor, build, platform, text) = sys.getwindowsversion()
          version = (major * 100000) + (minor * 10000) + build
       elif sys.platform == "darwin":
          # This command will return a string with the version number in
          # 10.x.x format.
          cmd = "sw_vers -productVersion"
          cmdobj = os.popen(cmd)
          verstring = cmdobj.read().rstrip()
          cmdobj.close()
          verstuple = verstring.split(".")
          # Convert the string to an integer by multiplying the individual
          # numbers by powers of 10.
          multiplier = 1000
          version = 0
          for number in verstuple:
             version += int(number) * multiplier
             multiplier /= 10
       return version
   
##################This section is mainly for debug -- Begin #############################
if __name__ == '__main__':    
    
    task = childTask('KillTask', 1)
    task.addPara('exefileName', 'notepad')
    task.run()