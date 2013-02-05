"""

    globalProperty.py
    
    Written by: Jacky Li

"""
from DbUtil import DbUtil
from restWkr import restWkr
from restSchTkMgr import restSchTkMgr
from SynchronizerPool import SyncerPoolManager
from SystemInformation import SystemInformation
from xml.dom import minidom,Node

import os,subprocess,re,uuid,socket,time
import logging
import logging.config

dbutil = None
commonUser = None
commonDomain = None
commonPassword = None
macAddress = None
restAdminInstance = None
restWorkerInstance = None
restSchTkMgrInstance = None
platform = None
syncerPoolManager = None
productTeam = None
configProperty = None
sysInfo = None
scriptDir = None
tmpDir = None
taskListDir = None
overdueTaskDir = None
schedulTaskDir = None
toolsDir = None
cloudServer = None
appInfoDic = {}
ipAddress = None
user = None

def __runCommand(cmd):
    outPutStr= subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()
    return outPutStr

def getDbUtil():
    global dbutil
    if dbutil==None:
        loadConfigProperty()
        dbutil = DbUtil()
    return dbutil

def getCommonDomain():
    global commonDomain    
    if commonDomain==None:
        commonDomain = getDbUtil().getAppInfo("common_domain")
    return commonDomain

def getCommonUser():
    global commonUser    
    if commonUser==None:
        commonUser = getDbUtil().getAppInfo("common_user")
    return commonUser

def getCommonPassword():
    global commonPassword
    if commonPassword==None:
        commonPassword = getDbUtil().getAppInfo("common_password")
    return commonPassword

def getAppInfo(key):
    global appInfoDic
    if not key in appInfoDic:
        loadAppInfo()
    elif 'appInfoUpdateTime' in appInfoDic:
        updateTime = appInfoDic['appInfoUpdateTime']
        currentTime = time.time()
        if currentTime<updateTime or currentTime>updateTime + 60*60: #No necessary to update peer list data
            loadAppInfo()
    if not key in appInfoDic: 
        return ""
    return appInfoDic[key]
    
def loadAppInfo():
    global appInfoDic
    try:
        appInfoXml = getDbUtil().getAppInfoXml()
        if appInfoXml:
            appInfoDoc = minidom.parseString(appInfoXml)
            appInfoes = appInfoDoc.getElementsByTagName("config")[0]
            for node in appInfoes.childNodes:
                if node.nodeType == node.TEXT_NODE:
                    continue
                else:
                    for attr in node.attributes.items():
                        appInfoDic[attr[0]] = attr[1]
            appInfoDic['appInfoUpdateTime'] = time.time()
    except Exception, e:
        logging.getLogger().error(e)
    

def getMacAddress():
    global macAddress
    if macAddress==None:
        macAddressList = None
        try :
            if os.name == 'posix':
                #Current only get en0 MacAddress
                cmd = 'ifconfig en0 | grep ether'
                outstr = __runCommand(cmd)
                macAddressList = re.findall(r'\w{2}:\w{2}:\w{2}:\w{2}:\w{2}:\w{2}', outstr)                
            elif os.name == 'nt':
                cmd = 'getMac'
                outstr = __runCommand(cmd)
                macAddressList = re.findall(r'\w{2}-\w{2}-\w{2}-\w{2}-\w{2}-\w{2}', outstr)
                
            if macAddressList!=None and len(macAddressList) > 0:
                macAddress = macAddressList[0]
                macAddress = macAddress.replace(":", "-")
            else:
                add = uuid.uuid1().hex[-12:]
                macAddress = ''.join(map(lambda (i, v): v + '-' if i > 0 and i < len(add) - 1 and (i - 1) % 2 == 0 else v, [(i, v) for (i, v) in enumerate(add)]))
        except Exception, e:
            add = uuid.uuid1().hex[-12:]
            macAddress = ''.join(map(lambda (i, v): v + '-' if i > 0 and i < len(add) - 1 and (i - 1) % 2 == 0 else v, [(i, v) for (i, v) in enumerate(add)]))
        
    return macAddress

def getIpAddress():
    global ipAddress
    if 'ipAddressUpdateTime' in appInfoDic:
        updateTime = appInfoDic['ipAddressUpdateTime']
        currentTime = time.time()
        if currentTime<updateTime or currentTime>updateTime + 10*60: #No necessary to update peer list data
            ipAddress = None
    
    if ipAddress==None:
        print "Try to get IP Address of current machine"        
        appInfoDic['ipAddressUpdateTime'] = time.time()
        ipAddressList = None
        while True:
            try:
                if os.name == 'posix':
                    #Current only get en0 on Mac
                    cmd = 'ifconfig en0 | grep inet'
                    outstr = __runCommand(cmd)
                    #Only support IPV4
                    ipAddressList = re.findall(r'\d{1,3}\.\d{1,3}.\d{1,3}.\d{1,3}', outstr)
                    if ipAddressList!=None and len(ipAddressList) > 0:
                        ipAddress = ipAddressList[0]
                    else:
                        try:
                            ipAddress = socket.gethostbyname(socket.gethostname())
                        except Exception, e:
                            #cmd = 'ifconfig en1 | grep inet'
                            cmd = 'ifconfig en1 | grep inet'
                            outstr = __runCommand(cmd)
                            #Only support IPV4
                            ipAddressList = re.findall(r'\d{1,3}\.\d{1,3}.\d{1,3}.\d{1,3}', outstr)
                            if ipAddressList!=None and len(ipAddressList) > 0:
                                ipAddress = ipAddressList[0]
                            else:
                                logging.getLogger().error("Failed to get IP Address")
                elif os.name == 'nt':
                    ipAddress = socket.gethostbyname(socket.gethostname())
            except Exception, e:
                ipAddress = None
            if ipAddress == "127.0.0.1":
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("gmail.com",80))
                ipAddress = s.getsockname()[0]
                s.close
            if ipAddress and len(str(ipAddress)) >= 7: # e.g. 1.1.1.1
                break;
            time.sleep(1)
        
    return ipAddress

def getRestAdminInstance():
    global restAdminInstance
    return restAdminInstance

def getRestWorkerInstance():
    global restWorkerInstance
    if restWorkerInstance==None:
        restWorkerInstance = restWkr() 
    return restWorkerInstance

def getRestSchTkMgrInstance():
    global restSchTkMgrInstance
    if restSchTkMgrInstance==None:
        restSchTkMgrInstance = restSchTkMgr() 
    return restSchTkMgrInstance

def getPlatform():
    global platform
    if platform==None:
        if os.name == 'posix':
            platform="osx10" 
        if os.name == 'nt':
            platform = "win32"
    return platform

def getLatestBuild(productName, version, platform, language, certLevel, subProduct):
    latestBuild = getDbUtil().getLatestBuild(productName, version, platform, language, certLevel, subProduct)
    return latestBuild

def getLatestBuildNum(productName, version, platform, language, certLevel, subProduct):
    latestBuild = getLatestBuild(productName, version, platform, language, certLevel, subProduct)
    if latestBuild==None:
        return None
             
    latestBuildNum = latestBuild[0]
            
    buildLocation = latestBuild[1]
            
    if buildLocation!=None and re.match(r'.*(\d{8}\.\w{1,4}\.\d{1,4}).*', buildLocation):
        latestBuildNum = re.sub(r'.*(\d{8}\.\w{1,4}\.\d{1,4}).*', r'\1', buildLocation)
            
    return latestBuildNum

def getUserHome():
    userHome = os.path.expanduser("~")
    if userHome=="~":
        userHome = os.getenv("HOME") if os.name == 'posix' else os.getenv("USERPROFILE")
    return userHome

def getSyncerPoolManager():
    global syncerPoolManager
    if syncerPoolManager==None:
        syncerPoolManager = SyncerPoolManager(1, 4)
        syncerPoolManager._initIdleSyncer()
    return syncerPoolManager

def isMachineOutOfChina():
    #Maybe Buggy, hope better solution
    ipAddress = getIpAddress()
    if not re.match('^10\.162\..*', ipAddress):
        return True
    return False

def getLatestVersion():
    latest = getDbUtil().getAppInfo('latest_version')
    if latest==None:
        return None
    latest = latest.strip()
    latestVersion = latest.split(".")
    if latestVersion==None:
        return None
    elif len(latestVersion)==1:
        latestVersion.insert(0, "0")
    return latestVersion

def getCurrentVersion():
    versionFile = os.path.join(os.getcwd(), 'version.txt').strip()
    if not os.path.exists(versionFile):
        return None
    else:
        try:
            f = open(versionFile, "r")
            versionStr = f.read()
            currentVersion = versionStr.split(".")
            if currentVersion==None:
                #Means will update if there has a file named version.txt even it's empty
                currentVersion=['0']
            elif len(currentVersion)==1:
                currentVersion.insert(0, "0")
        except:
            return False
        finally:
            if f!=None:
                f.close()
        return currentVersion
    
def shouldUpdate():
    latestVersion = getLatestVersion()
    curVersion = getCurrentVersion()
    if latestVersion==None or curVersion==None:
        return False
    else:
        for i in range(3):
            try:
                if latestVersion[i]==None or curVersion[i]!=None and int(latestVersion[i])<int(curVersion[i]):
                    break
                elif curVersion[i]==None or latestVersion[i]!=None and int(latestVersion[i])>int(curVersion[i]):
                    return True
            except:
                return False
    return False

def updateVersion():
    versionFile = os.path.join(os.getcwd(), 'version.txt')
    latestVersion = getLatestVersion()
    try:
        f = open(versionFile, "w")
        versionStr = f.write('.'.join(latestVersion))
    except:
        pass
    finally:
        if f!=None:
            f.close()
            
def getManagerName():
    if 'manager' in configProperty:
        return configProperty['manager']
    else:
        return 'none'

def getOwner():
    if 'owner' in configProperty:
        return configProperty['owner']
    else:
        return None
    
def getMachineName():
    if 'machine_name' in configProperty:
        return configProperty['machine_name']
    else:
        return None

def getProductTeam():
    global productTeam
    if productTeam==None:
        if 'manager' in configProperty:
            productTeam = getDbUtil().getProductTeam(configProperty['manager'])
        if productTeam==None:
            productTeam = ""
    return productTeam

def loadConfigProperty():
    global configProperty
    if configProperty==None:
        configProperty = {}
        __loadConfigProperty()
    return configProperty
    
def __loadConfigProperty():
    configFile = os.path.join(os.getcwd(), 'config.property').strip()
    if os.path.exists(configFile):
        try:
            f = file(configFile, "r")
            lines = f.readlines()
            for line in lines:
                if line.find('=') != -1:
                    key, value = line.strip().split("=")
                    configProperty[key] = value
            f.close()
        except:
            return
        finally:
            if f!=None:
                f.close()
    __updateConfigProperty()

def __updateConfigProperty():
    configFile = os.path.join(os.getcwd(), 'config_update.property').strip()
    if not os.path.exists(configFile):
        return
    else:
        try:
            f = file(configFile, "r")
            lines = f.readlines()
            for line in lines:
                if line.find('=') != -1:
                    key, value = line.strip().split("=")
                    configProperty[key] = value
            f.close()
            f = None
        except:
            return
        finally:
            if f!=None:
                f.close()
    os.remove(configFile)
    __writeConfigProperty()

def __writeConfigProperty():
    text = ''
    configFile = os.path.join(os.getcwd(), 'config.property').strip()
    for key in configProperty.keys():
        text = text + key + '=' + configProperty[key] + '\n'
    if os.path.exists( configFile ):
        os.remove(configFile)
    f = file(configFile, 'w')
    f.write(text)
    f.close()
                
def getSysInfo():
    global sysInfo
    if sysInfo==None:
        sysInfo = SystemInformation()
    return sysInfo

def getScriptDir():
    global scriptDir
    if scriptDir==None:
        scriptDir = os.path.join(os.getcwd(), 'scripts')
    return scriptDir

def getTmpDir():
    global tmpDir
    if tmpDir==None:
        tmpDir = os.path.join(os.getcwd(), 'tmp')
    return tmpDir

def getTaskListDir():
    global taskListDir
    if taskListDir==None:
        taskListDir = os.path.join(os.getcwd(), 'tasklist')
    return taskListDir

def getOverdueDir():
    global overdueTaskDir
    if overdueTaskDir==None:
        overdueTaskDir = os.path.join(getTaskListDir(), 'overdue')
    return overdueTaskDir

def getSchedulTaskDir():
    global schedulTaskDir
    if schedulTaskDir==None:
        schedulTaskDir = os.path.join(getTaskListDir(), 'schedule')
    return schedulTaskDir

def getToolsDir():
    global toolsDir
    if toolsDir==None:
        toolsDir = os.path.join(os.getcwd(), 'tools')
    return toolsDir

def getPrivateCloud():
    if 'private_cloud' in configProperty:
        return configProperty['private_cloud'].split(";")
    else:
        return []

def getPublicCloud():
    if 'public_cloud' in configProperty:
        return configProperty['public_cloud'].split(";")
    else:
        return []

def getCloudServerName():
    if 'cloud_server' in configProperty:
        return configProperty['cloud_server']
    #elif 'wsserver' in configProperty:
    #    return configProperty['wsserver']
    else:
        return None

def getCloudServerPort():
    if 'cloud_server_port' in configProperty:
        return int(configProperty['cloud_server_port'])
    else:
        return 21959
    
def getCloudServer():
    global cloudServer
    if cloudServer==None:
        cloudServerName = getCloudServerName()
        cloudPort = getCloudServerPort()
        cloudServer = None
        if cloudServerName and cloudPort:
            try:
                cloudServerAddress = socket.gethostbyname(cloudServerName)
                cloudServer = (cloudServerAddress, cloudPort)
            except:
                cloudServer = None
    return cloudServer

def getTimeZone():
    if 'timezone' in configProperty:
        return configProperty['timezone']
    else:
        return time.tzname[1]
    
def setUser(userAlias):
    global user
    if not userAlias in ['', 'test', 'tester', 'build', 'ps', 'free', 'private', 'performace', 'server', 'kickoff']:
        user = userAlias
    else:
        user = None
    
def getUser():
    global user
    return user
    
if __name__ == "__main__":
    logging.config.fileConfig('log.config')
    macAddress = getMacAddress()
    print macAddress
    ipAddress = getIpAddress()
    print ipAddress

    
    
