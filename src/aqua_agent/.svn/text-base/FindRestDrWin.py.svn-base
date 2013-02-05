"""

    FindRestDrWin.py
    
    Written by: Jacky Li (yxli@adobe.com)

"""

import os.path, sys, os, re, math, time, socket, stat, subprocess

diskList = ['d', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n']

RestDrFind = False
startFileName = 'startRestDr.bat'
RestDrFolder = 'RestDr'
RestDrFile = 'restAdm.py'
for disk in diskList:
    RestDrRelPath = os.path.join(RestDrFolder, RestDrFile)
    disk += ':'
    RestDrFullPath = os.path.normpath(os.path.join(disk, '//', RestDrRelPath))
    print RestDrFullPath
    if os.path.exists(RestDrFullPath):
        RestDrFind = True
        break

if RestDrFind:
    stream = ''
    stream += disk + '\n'
    stream += 'cd ' + RestDrFolder + '\n'
    stream += 'python ' + RestDrFile + '\n'
    startFileFullPath = os.path.normpath(os.path.expanduser('~\Start Menu\Programs\Startup' + '/' + startFileName))
    print startFileFullPath
    startF = open(startFileFullPath, 'w')
    startF.write(stream)
    startF.close()
    
    cmd = []
    cmd.append(startFileFullPath)
    subprocess.Popen(cmd).pid
