'''
PSFTCParser.py
Created on Apr 10, 2009
@author: chtpan
'''
import os.path, sys, os, re, math, time, stat, subprocess, socket

import xml.parsers.expat, ftplib
from threading import Thread, RLock, Condition
import logging
import logging.config
from QMSWebService import QMSWebService 


class PSFCaseAreaParser(object):
    '''
    classdocs
    '''

    def __init__(self, path="."):
        # init some member
        logging.config.fileConfig('log.config')
        self.logger = logging.getLogger()
        self._psfRootPath      = path #psf lib root folder path
        self._psfScriptsPath   = os.path.join(self._psfRootPath,'scripts')
        self._psfConfigPath    = os.path.join(self._psfRootPath,'config')
        self._psfBRConfigPath  = os.path.join(self._psfConfigPath,'psfController_BR4.csv')
        self._psfPSConfigPath  = os.path.join(self._psfConfigPath,'psfController_PS12.csv')
        self._psfTestFilesPath = os.path.join(self._psfRootPath,'testfiles')      
        self._case2AreaMap = {}
        self._area2CasesMap = {}
        self._ProdcutAreasDict = {}
        self._areaList = []
        self._case2AreaFilePath = os.path.join(self._psfRootPath,'case2area.dat')
        self._area2CaseFilePath = os.path.join(self._psfRootPath,'area2case.dat')
        
   
        #logger config
        logging.config.fileConfig('log.config')
        self.logger = logging.getLogger()
    
    def getTestAreaMetaData(self):
        
        if not (os.path.isdir(self._psfRootPath)):
            self.logger.error('invalid psf path:' + self._psfRootPath)
            return
        
        for root, dirs, files in os.walk(self._psfScriptsPath, True, None):
            for testcaseFileName in files:                
                if(os.path.splitext(testcaseFileName)[1] == '.csv'):
                    casepath = os.path.split(root)[1]
                    casename = casepath + '/' + os.path.splitext(testcaseFileName)[0]                    
                    testAreaName = self.__dumpTestCaseFileInfo(os.path.join(root,testcaseFileName))
                    if(testAreaName == None or testAreaName == ''):
                        testAreaName = 'other'
                    self._case2AreaMap[casename] = testAreaName                   
                    if(testAreaName not in self._areaList):
                        self._areaList.append(testAreaName)
                        self._area2CasesMap[testAreaName] = []
                    self._area2CasesMap[testAreaName].append(casename)
        
        #reset areasbyProduct
        self.__ResetAreasByProduct('Bridge 4.0 CS5')
        if(os.path.isfile(self._area2CaseFilePath)):
            os.remove(self._area2CaseFilePath)
        fobj = open(self._area2CaseFilePath,'w')
        for eacharea in self._area2CasesMap:            
            fobj.write(eacharea)
            fobj.write(':')
            fobj.write(','.join(self._area2CasesMap[eacharea]))
            fobj.write('\n')
        fobj.close()
        
        fobj = open(self._case2AreaFilePath,'w')
        for eachcase in self._case2AreaMap:
            fobj.write(eachcase)
            fobj.write(':')
            fobj.write(self._case2AreaMap[eachcase])
            fobj.write('\n')
        fobj.close()
        
        
        
    def __dumpTestCaseFileInfo(self, testcasePath):
        aCaseInfoList = []
        fobj = open(testcasePath,'rU')
        for eachLine in fobj:
            if(eachLine[:2] != '_,'):
                aCaseInfoList.append(eachLine)
        fobj.close()
        
        if(len(aCaseInfoList) < 2):
            self.logger.error('invalid testcase data file:' + testcasePath)
            return
            
        aParamLabellist = aCaseInfoList[0].strip().split(',')
        aParamValuelist = aCaseInfoList[1].strip().split(',')
        if('testAreaName' in aParamLabellist):
            return aParamValuelist[aParamLabellist.index('testAreaName')]
        

    def MakeNewPsfController(self, featureAreas, mypsfBRConfig):    
        fread = open(self._psfBRConfigPath, 'rU')
        mypsfBRConfig = os.path.join(self._psfConfigPath, mypsfBRConfig)
        fwrite = open(mypsfBRConfig, 'w')
        self.logger.info('make new cotroller file from ' + self._psfBRConfigPath + ' to ' + mypsfBRConfig)
        for eachline in fread:
            caseinfo = eachline.split(',')
            if(caseinfo[0] == '_' or
               eachline[0] != ',' or   
               eachline[0] == ',' and caseinfo[1] in self._case2AreaMap and self._case2AreaMap[caseinfo[1]] in featureAreas):
                fwrite.write(eachline)                                
            else:
                fwrite.write('_' + eachline)                                    
        fread.close()
        fwrite.close()     
                   
        
    def __ResetAreasByProduct(self, productName='Bridge 4.0 CS5'):
        self.logger.info('reset ' + productName + 'area info to server')
        if(productName in 'Bridge 3.0 CS4, Bridge 4.0 CS5' ):
            configPath = self._psfBRConfigPath
        elif (productName in 'Photoshop 12.0'):
            configPath = self._psfPSConfigPath
        
        self._ProdcutAreasDict[productName] = []
        #
        fread = open(configPath, 'rU')
        for eachline in fread:
            casedata = eachline.split(',')
            if(eachline[0] != ',' or
               casedata[0] == '_' or               
               casedata[1] not in self._case2AreaMap
               ):                
                continue                                                        
            else:
                if(self._case2AreaMap[casedata[1]] not in self._ProdcutAreasDict[productName]):                    
                    self._ProdcutAreasDict[productName].append(self._case2AreaMap[casedata[1]])                                                
        fread.close()
        
        #update new area info to database by webservice 
        self.__UpdateNewAreaInfo(productName)                 
        
         
    def __UpdateNewAreaInfo(self, productName = 'Bridge 4.0 CS5'):
        self.logger.info('updating ' + productName + ' area info by qmswebservice...')         
        if(productName not in self._ProdcutAreasDict):        
            return        
        areas = self._ProdcutAreasDict[productName]        
        #update each area info
        qmsService = QMSWebService()
        for area in areas:            
            qmsService.addPsfProductFeature(productName,area)
                            

#parser = PSFCaseAreaParser(r'F:\downloads\psfauto\psf','mypsfController_BR4.csv')
#parser.getTestAreaMetaData()
                      