"""

    TSProxyService.py
    
    Written by: Jacky Li(yxli@adobe.com)

"""

import httplib,urllib
import globalProperty

class TSProxyService:
    
    GET_VALID_TEST_CASES = "/tsproxy/GetValidTestCasesServlet"
    
    def __init__(self):
        try:
            self.__qmsHttpClient = httplib.HTTPConnection("%s:8080" % globalProperty.configProperty['wsserver'])
        except Exception, e:
            self.__qmsHttpClient = None
            print e 
    
    def __getQMSHttpClient(self):
        try: 
            if self.__qmsHttpClient==None:
                self.__qmsHttpClient = httplib.HTTPConnection("%s:8080" % globalProperty.configProperty['wsserver'])
        except Exception, e:
            self.__qmsHttpClient = None
            print e 
            
    def getValidTestCasesFromTS(self, productName, controllerFileName):
        print "get Valid Test Cases according to product %s's controller file %s" % (productName, controllerFileName)
        try:
            self.__getQMSHttpClient()
            if self.__qmsHttpClient != None:
                params = urllib.urlencode({'productName': productName, 'controllerFileName': controllerFileName})
                headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
                self.__qmsHttpClient.request("POST", TSProxyService.GET_VALID_TEST_CASES, params, headers)
                response = self.__qmsHttpClient.getresponse()
                data = response.read()
                return data
        except Exception, e:
            print e
        finally:
            if self.__qmsHttpClient != None:
                self.__qmsHttpClient.close()
                self.__qmsHttpClient = None
        
            