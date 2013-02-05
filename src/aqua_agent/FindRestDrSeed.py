"""

    FindResTool.py
    
    Written by: Alon Ao (alonao@adobe.com)
    Written by: Jacky Li (yxli@adobe.com);

"""

import os.path, sys, os, re, math, time, socket, stat, subprocess, machine

RestDrName = 'RestDr'
def generateLinkFileinMac():
    ResToolFind = False
    startFileName = 'startup.sh'

    #ResToolFile = 'taskManager.py'
    for disk in machine.getMacPartitions():
        resToolRealFolder = '/Volumes/' + disk + '/' + RestDrName
        ResToolRelPath = resToolRealFolder + '/' + startFileName
        
    #    ResToolFullPath = os.path.normpath(os.path.join(disk, '/', ResToolFolder, ResToolFile))
        if os.path.exists(ResToolRelPath):
            ResToolFind = True
            break
        
    if ResToolFind:
    #    stream += disk + '\n'
        stream = 'cd ' + resToolRealFolder + '\n'
        stream += './' + startFileName + '\n'
        linkFilePath = 'linkResClient.sh'
        startF = file(linkFilePath, 'wb')
        startF.write(stream)
        startF.close()
        
        time.sleep(1)
        # change to executable file
        os.system('chmod +x ' + linkFilePath)
        os.system('./' + linkFilePath)
#        cmd = []
#        cmd.append('chmod +x ' + linkFilePath)
#        cmd.append('./' + linkFilePath)
#        subprocess.Popen(cmd).pid
    else:
        #do nothing
        return
    
def generateLinkFileinWin():
    ResToolFind = False
    startFileName = 'startup.cmd'
    #ResToolFile = 'taskManager.py'
    for disk in machine.getWinPartitions():
        resToolRealFolder = disk + ':\\' + RestDrName
        ResToolRelPath = resToolRealFolder + '\\' + startFileName
        
    #    ResToolFullPath = os.path.normpath(os.path.join(disk, '/', ResToolFolder, ResToolFile))
        if os.path.exists(ResToolRelPath):
            ResToolFind = True
            break
    print  ResToolRelPath
    print ResToolFind
    if ResToolFind:
        stream = []
        stream.append(disk + ': \n')
        stream.append('cd ' + resToolRealFolder + ' \n')
        stream.append(startFileName)
        linkFilePath = 'link.cmd'
        startF = open(linkFilePath, 'wb')
        startF.writelines(stream)
        startF.close()
        print stream
        time.sleep(1)
        cmd = []
        cmd.append(linkFilePath)
        subprocess.Popen(cmd).pid
    else:
        #do nothing or show error message here
        return
    
if os.name == 'posix':
    generateLinkFileinMac()
if os.name == 'nt':
    generateLinkFileinWin()
