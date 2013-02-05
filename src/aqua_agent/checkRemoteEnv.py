"""

    checkRemoteEnv.py
    
    Written by: Lei Nie (nlei@adobe.com)

"""

import subprocess, os, os.path, re, time, logging

#logging.config.fileConfig('log.config')
#logger = logging.getLogger()
       
def toXML():
    xmlStr = ''
    xmlStr = enVtoXML(getRemoteEnv())
    
    return xmlStr
     
def getRemoteEnv():
    remoteEnv = {}
    if os.name == 'posix':
        remoteEnv['win'] = checkApp('RDC.app')
        remoteEnv['mac'] = 'true'
    if os.name == 'nt':
        remoteEnv['win'] = 'true'
        remoteEnv['mac'] = checkApp('vncviewer.exe')
    return remoteEnv

    
def checkApp(appName):
    appPath = os.path.join(os.getcwd(), 'tools')+'/'+appName
    print appPath
    if os.name == 'nt':
        if os.path.isfile(appPath): 
            return 'true'; 
        else:
            return 'false';
    if os.name == 'posix':
        if os.path.exists(appPath): 
            return 'true'; 
        else:
            return 'false';
      
def enVtoXML(remoteEnv):
    from xml.dom import minidom,Node
    doc = minidom.Document()
    content = doc.createElement("RemoteEnv")
    doc.appendChild(content)
    
    win = doc.createElement("param")
    win.setAttribute("name", 'win')
    win.setAttribute("value", remoteEnv['win'])
    content.appendChild(win)

    mac = doc.createElement("param")
    mac.setAttribute("name", 'mac')
    mac.setAttribute("value", remoteEnv['mac'])
    content.appendChild(mac)
    
    return doc.toprettyxml()
    
if __name__ == '__main__':
    xmlStr = ''
    xmlStr = enVtoXML(getRemoteEnv())
    
    print xmlStr

