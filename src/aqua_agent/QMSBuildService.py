"""

    QMSBuildService.py
    
    Written by: Jacky Li(yxli@adobe.com)

"""

from SOAPpy import SOAPProxy, WSDL

import globalProperty

class QMSBuildService:
    
    #WSQMSBUILDURL = "http://blazeman.pac.adobe.com:8080/qmsserver/services/buildService?WSDL"
    #WSQMSBUILDURL = "http://ps-bj-qe.pac.adobe.com:8080/qmsserver/services/buildService?WSDL"
    #WSQMSBUILDURL = "http://ps-builds.pac.adobe.com:8080/qmsserver/services/buildService?WSDL"

    def __init__(self):
        try: 
            self._WSQMSBUILDURL = "http://%s/services/qmsAutoService?wsdl" % globalProperty.configProperty['wsserver']
            self.__buildServer = WSDL.Proxy(self._WSQMSBUILDURL)
        except Exception, e:
            self.__qmsServer = None
            print e 
            
    def __getQMSBuildServer(self):
        try: 
            if self.__buildServer==None:
                self.__buildServer = WSDL.Proxy(self._WSQMSBUILDURL)
        except Exception, e:
            self.__buildServer = None
            print e 
            
    def addNewBuild(self, 
                    productName, 
                    mainVersion, 
                    minorMersion, 
                    platform, 
                    language, 
                    latestBuildLocation):
        #self.__update("UPDATE execution_detail set finish_time = now(), status = %s, error_msg = %s WHERE execution_id = %s AND task_id = %s", (status, errorMsg, exeId, taskId))
        print "Add New Build"
        try:
            self.__getQMSBuildServer()
            if self.__buildServer != None:
                self.__buildServer.addNewBuild(
                                               productName, 
                                               mainVersion, 
                                               minorMersion, 
                                               platform, 
                                               language, 
                                               latestBuildLocation);
        except Exception, e:
            print e
            
if __name__ == "__main__":
    qbService = QMSBuildService()
    qbService.addNewBuild(
                          'Bridge', 
                          '4.0', 
                          '70', 
                          'Win', 
                          'mul', 
                          '\\\\pektools\\Builds\\PSQE\\Bridge\\4.0\\Win\\mul\\20090305.m.70')
