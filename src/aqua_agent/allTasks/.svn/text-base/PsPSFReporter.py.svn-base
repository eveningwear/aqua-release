"""
object_dict
nkchenz@gmail.com 2007
Provided as-is; use at your own risk; no warranty; no promises; enjoy!
"""

class object_dict(dict):
    """object view of dict, you can 
    >>> a = object_dict()
    >>> a.fish = 'fish'
    >>> a['fish']
    'fish'
    >>> a['water'] = 'water'
    >>> a.water
    'water'
    >>> a.test = {'value': 1}
    >>> a.test2 = object_dict({'name': 'test2', 'value': 2})
    >>> a.test, a.test2.name, a.test2.value
    (1, 'test2', 2)
    """
    def __init__(self, initd=None):
        if initd is None:
            initd = {}
        dict.__init__(self, initd)

    def __getattr__(self, item):
        d = self.__getitem__(item)
        # if value is the only key in object, you can omit it
        if isinstance(d, dict) and 'value' in d and len(d) == 1:
            return d['value']
        else:
            return d

    def __setattr__(self, item, value):
        self.__setitem__(item, value)


"""
Thunder Chen<nkchenz@gmail.com> 2007.9.1
"""
try:
    import xml.etree.ElementTree as ET
except:
    import cElementTree as ET # for 2.4


import re,datetime,shutil,traceback
import globalProperty

class XML2Dict(object):

    def __init__(self):
        pass

    def _parse_node(self, node):
        node_tree = object_dict()
        # Save attrs and text, hope there will not be a child with same name
        if node.text:
            node_tree.value = node.text
        for (k,v) in node.attrib.items():
            k,v = self._namespace_split(k, object_dict({'value':v}))
            node_tree[k] = v
        #Save childrens
        for child in node.getchildren():
            tag, tree = self._namespace_split(child.tag, self._parse_node(child))
            if tag not in node_tree: # the first time, so store it in dict
                node_tree[tag] = tree
                continue
            old = node_tree[tag]
            if not isinstance(old, list):
                node_tree.pop(tag)
                node_tree[tag] = [old] # multi times, so change old dict to a list       
            node_tree[tag].append(tree) # add the new one      

        return  node_tree


    def _namespace_split(self, tag, value):
        """
           Split the tag  '{http://cs.sfsu.edu/csc867/myscheduler}patients'
             ns = http://cs.sfsu.edu/csc867/myscheduler
             name = patients
        """
        result = re.compile("\{(.*)\}(.*)").search(tag)
        if result:
            print tag
            value.namespace, tag = result.groups()    
        return (tag, value)

    def parse(self, file):
        """parse a xml file to a dict"""
        f = open(file, 'r')
        return self.fromstring(f.read()) 

    def fromstring(self, s):
        """parse a string"""
        t = ET.fromstring(s)
        root_tag, root_tree = self._namespace_split(t.tag, self._parse_node(t))
        return object_dict({root_tag: root_tree})


"""
PsfLogsParser.py 
Written by: Baichao Li (lbaichao@adobe.com)
Contributed by Jacky Li (yxli@adobe.com) 
"""

from baseTask import Task
import os, os.path, re, time, sys
from stat import *
from xml.dom import minidom

class childTask(Task): 
    def __init__(self, type, priority):
        super(childTask, self).__init__(type, priority)
        
        self.logDicts = {}
        
        #################################
        self.htmlTableStyle = ""
        self.htmlHeader = ""
        self.htmlSummary = ""
        self.htmlFooter = ""
        self.htmlBody = ""
        
        self.caseNum = 0
        self.passCaseNum = 0
        self.passRate = 0
        self.minStartTime = None
        self.maxEndTime = None
    
        self.htmlReportFileRoot = os.path.join(os.getcwd(), 'PSFReport')
        self._cleanReport()
        if(not os.path.exists(self.htmlReportFileRoot)):
            os.mkdir(self.htmlReportFileRoot)
        self.htmlReportFile = ""
        self.htmlEmailReportFile = ""
        #################################
        
        self.logServer = "blazeman.pac.adobe.com";
        self.logServerPath = "http://%s/filterlog/" % self.logServer
        
        #################################
        self.AUT_name = ""
        self.AUT_version = ""
        self.AUT_build = ""
        self.AUT_platform = ""
        self.AUT_locale = ""
        self.TestEnvironment_machineName = ""
        self.TestEnvironment_osVersion = ""
        self.TestEnvironment_systemLanguage = ""
        self.htmlReportFilePath = "Report"
        #################################
        
    def beforeTime(self, firstTime, secondTime):
        delta = firstTime - secondTime
        if delta.days <0:
            return True
        return False
    
    def run(self):
        self.logger.info('Starting PSF log parsing')
        
        self.userHome = globalProperty.getUserHome()
        
        if 'PSFHome' in self.parameter:
            self.psfHome = self.parameter['PSFHome']
        else:
            self.psfHome = os.path.join(self.userHome, 'PSF')
            
        if not os.path.exists(self.psfHome):
            print("There is no PSF installed in [%s]" % self.psfHome)
            raise ("There is no PSF installed in [%s]" % self.psfHome)
        
        self.psfLogHome = os.path.join(self.psfHome, 'logs')
        
        self.walkLogFiles(self.psfLogHome, self.doXmlParsing)
        
        self.prepareFolderHierarchy()
        
        #self.output()
        self.writeHtmlReport()
        
        self.uploadReport()

    def prepareFolderHierarchy(self):        
        for key in self.logDicts.keys():
            logfile = self.logDicts[key]
            if self.AUT_name != "":
                break
            
            self.AUT_name = logfile.Results.TestSession.AUT.name.strip()
            self.AUT_version = logfile.Results.TestSession.AUT.version.strip()
            self.AUT_build = logfile.Results.TestSession.Build.label.strip()
            self.AUT_platform = logfile.Results.TestSession.AUT.platform.strip()
            self.AUT_locale = logfile.Results.TestSession.AUT.locale.strip()
            self.TestEnvironment_machineName = logfile.Results.TestSession.TestEnvironment.machineName.strip()
            self.TestEnvironment_osVersion = logfile.Results.TestSession.TestEnvironment.osVersion.strip()
            self.TestEnvironment_systemLanguage = logfile.Results.TestSession.TestEnvironment.systemLanguage.strip()
        
        self.curReportHierachy = os.path.join(self.AUT_platform, self.AUT_locale, self.AUT_name, self.AUT_version, self.AUT_build, datetime.datetime.now().strftime('%Y_%m_%dT%H_%M_%S'))
        self.curReportPath = os.path.join(self.htmlReportFileRoot, self.curReportHierachy)
        if not os.path.exists(self.curReportPath):
            os.makedirs(self.curReportPath)
        
        self.curDetailReportPath = os.path.join(self.curReportPath, "details")
        if not os.path.exists(self.curDetailReportPath):
            os.makedirs(self.curDetailReportPath)

    def walkLogFiles(self, top, callback):
        '''recursively descend the psf log directory tree,
        calling the callback function for each valid log file '''
    
        for f in os.listdir(top):
            pathname = os.path.join(top, f)
            mode = os.stat(pathname)[ST_MODE]
            
            """
            if(S_ISDIR(mode)):
                if(f=='performanceCSV'):
                    self.walkLogFiles(pathname,callback)
                elif (f=='maddobe'):
                    #self.walkLogFiles(pathname,callback)
                    #print 'Skipping %s' % pathname
                    pass
                else:
                    #print 'Skipping %s' % pathname
                    pass
            """
            #elif(S_ISREG(mode)):
            if(S_ISREG(mode)):
                callback(pathname)
            else:
                print 'Skipping %s' %pathname

    def doXmlParsing(self, lf):
        if(not self.isValidXmlLogFile(lf)):
            return
        print lf
        xml = XML2Dict()
    
        try:
            r = xml.parse(lf)
            key = re.sub(r'(.*)_20\d+_\d+.*', r'\1', os.path.basename(lf))
            self.logDicts[key] = r
        except Exception, e:
            print "XML parsing Error occurs in file [%s]" % lf 
            print e
            print "Skip processing log file [%s]" % lf 
            pass

    # for debug
    def output(self):
        from pprint import pprint
        pprint(self.logDicts)

    def isValidXmlLogFile(self, lf):
        #print os.path.splitext(lf)
        if(os.path.splitext(lf)[1] == ".xml"):
            basename = os.path.basename(lf)
            print basename
            if basename.startswith("BasicFunctionality_") or \
               basename.startswith("AdvancedFunctionality_") or \
               basename.startswith("SmokeTest_") :
                if(lf.find("cxs120") > -1):
                    return False
                if(lf.find("FAILED_DBID") > -1):
                    return False
                return True
            else:
                pass
        return False
    
    def writeHtmlReport(self):
        self.formatTableStyle()
        self.formatJavascript()
        self.formatReportHeader()
        self.formatReportFooter()
        self.formatReportBody()
        self.formatReportSummary()
    
        self.formatUniqueReportFileName()
    
        htmlText = self.htmlHeader + self.javascript + self.htmlTableStyle + self.htmlSummary + self.htmlBody + self.htmlFooter
        #self.htmlReportFile = "/Users/lbaichao/Desktop/psf_report.html"
        self.htmlEmailReportFilePath = os.path.join(self.curReportPath, self.htmlEmailReportFile)
        file_obj = open(self.htmlEmailReportFilePath, 'w')                
        file_obj.write(htmlText.encode('utf-8'))
        file_obj.close()
        
        htmlText = re.sub("(.*)<a[^<]+Click Here for Browsing in Browser</a>\s*(.*)", r"\1\2", htmlText)
        self.htmlReportFilePath = os.path.join(self.curReportPath, self.htmlReportFile)
        file_obj = open(self.htmlReportFilePath, 'w')                
        file_obj.write(htmlText.encode('utf-8'))            
        file_obj.close()
        
    def getHtmlReport(self):
        return self.htmlEmailReportFilePath
        
    def getPassRate(self):
        return str(self.passRate)[0:5] + "%"
    
    def getMachine(self):
        return self.TestEnvironment_machineName
    
    def getOSVersion(self):
        return self.TestEnvironment_osVersion
    
    def getSystemLang(self):
        return self.TestEnvironment_systemLanguage

    def formatTableStyle(self):
        self.htmlTableStyle = '''

<style type="text/css">
      body {
        font:normal 95% helvetica;
        color:#000000;
      }
      table tr td, table tr th {
          font-size: 85%;
      }
      table.details tr th{
        font-weight: bold;
        text-align:center;
        background:#a6caf0;
      vertical-align: middle;
      }
      table.details tr td{
        background:#eeeee0;
      }
    
    A:link {text-decoration: none; color: red;}
    A:visited {text-decoration: none; color: red;}
    A:active {text-decoration: none; color: red;}
    A:hover {text-decoration: underline; color: red;}
      
      p {
        line-height:1.5em;
        margin-top:0.5em; margin-bottom:1.0em;
      }
      h1 {
        margin: 0px 0px 5px; font: 165% verdana,arial,helvetica
      }
      h2 {
        margin-top: 1em; margin-bottom: 0.5em; font: bold 125% verdana,arial,helvetica
      }
      h3 {
        margin-bottom: 0.5em; font: bold 115% verdana,arial,helvetica
      }
      h4 {
        margin-bottom: 0.5em; font: bold 100% verdana,arial,helvetica
      }
      h5 {
        margin-bottom: 0.5em; font: bold 100% verdana,arial,helvetica
      }
      h6 {
        margin-bottom: 0.5em; font: bold 100% verdana,arial,helvetica
      }
      .Error {
        font-weight:bold; color:red;
      }
      .Failure {
        font-weight:bold; color:purple;
      }
      .Success {
        color:green;
      }
      .Properties {
        text-align:right;
      }
      .style1 {color: #FF0000}
      .style2 {color: #009900}
</style>

'''

    def formatJavascript(self):
        self.javascript = '''
<script language="JavaScript" type="text/javascript">
    function openPage(url) {
       window.open(url);
       window.close();
    }
</script>
'''

    def formatReportSummary(self):
        self.totalTestLogs = 0
        getGeneralSummary = False
        self.failedTestLogs = 0
        logFileKeys = self.logDicts.keys()
        logFileKeys.sort()
        for key in logFileKeys:
            logfile = (key, self.logDicts[key])
            #for logfile in self.logDicts.items():
            self.totalTestLogs += 1
            try:
                if(not getGeneralSummary):
                    self.htmlSummary = '''
    <body>
'''
                    expectedReportHtmlPath = self.logServerPath + "/" + self.curReportHierachy.replace("\\", "/") + "/report.html"
#                    self.htmlSummary += '<input type="submit" value="Click Here for Browsing in Browser" onClick="openPage(\'' + expectedReportHtmlPath + '\')">'
                    self.htmlSummary += '''
<a href='''
                    self.htmlSummary += "\"" + expectedReportHtmlPath + "\" target=\"_blank\">Click Here for Browsing in Browser</a>"
                    self.htmlSummary += '''
    <h2>Basic Information</h2>
    <table class="details" border="0" cellpadding="5" cellspacing="2" width="98%">
    <tr>
    <th>Application</th>
    <th>Version</th>
    <th>Build</th>
    <th>Platform</th>
    <th>Locale</th>
    <th>Machine</th>
    <th>OSVersion</th>
    <th>System Lang</th>
    </tr>
    '''
                    self.htmlSummary += '''
    <tr>
    '''
                    self.htmlSummary += "<td>" + logfile[1].Results.TestSession.AUT.name + "</td>"
                    if self.parameter.has_key('ProductVersion'):
                        self.htmlSummary += "<td>" + self.parameter['ProductVersion'] + "</td>"
                    else:
                        self.htmlSummary += "<td>" + logfile[1].Results.TestSession.AUT.version + "</td>"
                    self.htmlSummary += "<td>" + logfile[1].Results.TestSession.Build.label + "</td>"
                    self.htmlSummary += "<td>" + logfile[1].Results.TestSession.AUT.platform + "</td>"
                    self.htmlSummary += "<td>" + logfile[1].Results.TestSession.AUT.locale + "</td>"
                    self.htmlSummary += "<td>" + logfile[1].Results.TestSession.TestEnvironment.machineName + "</td>"
                    self.htmlSummary += "<td>" + logfile[1].Results.TestSession.TestEnvironment.osVersion + "</td>"
                    self.htmlSummary += "<td>" + logfile[1].Results.TestSession.TestEnvironment.systemLanguage + "</td>"
                    self.htmlSummary += '''
    </tr>
    </table>
    '''
                    self.AUT_name = logfile[1].Results.TestSession.AUT.name
                    self.AUT_version = logfile[1].Results.TestSession.AUT.version
                    self.AUT_build = logfile[1].Results.TestSession.Build.label
                    self.AUT_platform = logfile[1].Results.TestSession.AUT.platform
                    self.AUT_locale = logfile[1].Results.TestSession.AUT.locale
        
                    self.TestEnvironment_machineName = logfile[1].Results.TestSession.TestEnvironment.machineName
                    self.TestEnvironment_osVersion = logfile[1].Results.TestSession.TestEnvironment.osVersion
                    self.TestEnvironment_systemLanguage = logfile[1].Results.TestSession.TestEnvironment.systemLanguage
            
                    self.htmlSummary += '''
    <hr size="1">
    <h2>Summary</h2>
    <table class="details" border="0" cellpadding="5" cellspacing="2" width="98%">
    <tr>
    <th>TESTS</th>
    <th>FAILURES</th>
    <th>SUCCESS RATE</th>
    <th>SUM TIME</th>
    </tr>
    '''
                    self.htmlSummary += '''
    <tr align="center">
    '''
                    self.htmlSummary += "<td><strong>" + str(self.caseNum) + "</strong></td>"
                    self.htmlSummary += "<td><strong>" + str(self.caseNum - self.passCaseNum) + "</strong></td>"
                    self.passRate = float(self.passCaseNum) * 100/float(self.caseNum) if self.caseNum!=0 else 0                
                    self.htmlSummary += "<td><strong>" + str(self.passRate)[0:5] + "%</strong></td>"
                    maxDelta = self.maxEndTime - self.minStartTime
                    self.htmlSummary += "<td><strong>%s</strong></td>" %maxDelta
                    self.htmlSummary += '''
    </tr>
    </table>
    '''
                    getGeneralSummary = True
            
                if isinstance(logfile[1].Results.TestSession.Test, list):
                    for item in logfile[1].Results.TestSession.Test:
                        if not item.TestResult.passed == "True":
                            self.failedTestLogs +=1
                            break
                else:
                    if(logfile[1].Results.TestSession.Test.TestResult.passed == "True"):
                        pass
                    else:
                        self.failedTestLogs += 1
                
            except Exception, Err:
                self.failedTestLogs += 1
        
        return self.htmlSummary

    def formatUniqueReportFileName(self):
        self.htmlReportFile = "report.html"
        self.htmlEmailReportFile = "report_email.html"
        return self.htmlReportFile
    

    def formatReportHeader(self):
        self.htmlHeader = '''
<html>
    <meta http-equiv="content-type" content="text/html;charset=utf-8">
''' 
        return self.htmlHeader

    def formatReportFooter(self):
        self.htmlFooter = '''
    </body>
</html>
'''
        return self.htmlFooter


    def formatReportBody(self):
        self.htmlBody = '''
    <hr size="1">
    <h2>Detailed Report of PSF Results</h2>
    <table class="details" border="0" cellpadding="5" cellspacing="2" width="98%">
    <tr>
    <th width="20">TEST LOG NAME</th>
    <th>TEST CASE NAME</th>
    <th>PASSED</th>
    <th>OWNER</th>
    <th>EXECUTION TIME</th>
    </tr>
'''

        logFileKeys = self.logDicts.keys()
        logFileKeys.sort()
        strTmpBody = ""
        for key in logFileKeys:
            logfile = (key, self.logDicts[key])
                #for logfile in self.logDicts.items():    
                    #print logfile
            strTmpTR = ""
            isPassedAllSubTestCases = True
            try:
                if isinstance(logfile[1].Results.TestSession.Test, list):
                    hasWrittenLogName = False 
                    localMinStartTime = None
                    localMaxEndTime = None
#                    for item in logfile[1].Results.TestSession.Test:
#                        if not item.TestResult.passed == "True":
#                            isPassedAllSubTestCases = False;
#                            break
                  
                    for item in logfile[1].Results.TestSession.Test:
                        strTmpSubTR = ""
                        isPassedSubTestCases = True
                    
                        strTmpSubTR += '''
                            <tr>
                            <td/>'''
                        strTmpSubTR += '''
                            <td>'''
                        strTmpSubTR += item.name
                        strTmpSubTR += "</td>"
                            
                        self.caseNum += 1
                        if not item.TestResult.passed == "True":
                            isPassedAllSubTestCases = False
                            isPassedSubTestCases = False
                            strTmpSubTR += '''
                            <td align="center" class="Error"> ''' 
#                            strTmpTR += '<input class="Error" type="submit" value="' + item.TestResult.passed + '" onClick="openPage(' + self.generateDetailReport(item) + ')">'
                            strTmpSubTR += '<a href="' + self.generateDetailReport(item) + '" target="_blank">'
                            strTmpSubTR += item.TestResult.passed
                            strTmpSubTR += "</a>"
                        else:
                            self.passCaseNum += 1
                            strTmpSubTR += '''
                            <td align="center" class="Success"> ''' 
                            strTmpSubTR += item.TestResult.passed
#                            strTmpTR += "<font color='green'>"
#                            strTmpTR += item.TestResult.passed
#                            strTmpTR += "</font>"
                        
                        strTmpSubTR += "</td><td/>"
                        
                        strTmpSubTR += '''
                            <td>'''
                        strTmpSubTR += item.TestResult.executionTime
                        strTmpSubTR += ' (ms)'
                        strTmpSubTR += "</td>"
                        
                        strTmpSubTR += "</tr>"
                        
                        startTime = datetime.datetime.strptime(item.TestResult.startTime, '%Y-%m-%dT%H:%M:%S')
                        if self.minStartTime==None or self.beforeTime(startTime, self.minStartTime):
                            self.minStartTime = startTime
                        if localMinStartTime==None or self.beforeTime(startTime, localMinStartTime):
                            localMinStartTime = startTime
                            
                        endTime = datetime.datetime.strptime(item.TestResult.endTime, '%Y-%m-%dT%H:%M:%S')
                        if self.maxEndTime==None or self.beforeTime(self.maxEndTime, endTime):
                            self.maxEndTime = endTime
                        if localMaxEndTime==None or self.beforeTime(localMaxEndTime, endTime):
                            localMaxEndTime = endTime
                            
                        if isPassedSubTestCases:
                            strTmpTR += strTmpSubTR                            
                        else:
                            strTmpTR = strTmpSubTR + strTmpTR
                    
                    if not hasWrittenLogName:
                        hasWrittenLogName = True
                        
                        strLogNameTmpTR = '''
                        <tr>
                        <td><strong>'''
                        strLogNameTmpTR += logfile[0]
                        strLogNameTmpTR += '</strong></td><td/><td/>'
                        
                        #FIXME: Hardcode here
                        strLogNameTmpTR += '''
                        <td><strong>''' + self.parameter['FeatureOwner'] + '''</strong></td>'''
                        
#                        strLogNameTmpTR += '</strong></td><td/><td><strong><font color="red">'
#                        if not isPassedAllSubTestCases:
#                            strLogNameTmpTR += str(isPassedAllSubTestCases)
#                            strLogNameTmpTR += "</font>"
#                            strLogNameTmpTR += '</strong></td>'
#                        else:
#                            strLogNameTmpTR += str(isPassedAllSubTestCases)
#                            strLogNameTmpTR += '</td>'

                        localMaxDelta = localMaxEndTime - localMinStartTime
                        strLogNameTmpTR += '<td><strong>%s</strong></td>' %(localMaxDelta)
                        
                        strTmpTR = strLogNameTmpTR + strTmpTR
                else:
                    strTmpTR += '''
                    
                    <tr>
                        <td width="20"><strong>'''
                    strTmpTR += logfile[0]
                    strTmpTR += "</strong></td>"
                    strTmpTR += '''
                    <td>'''
                    strTmpTR += logfile[1].Results.TestSession.Test.name
                    strTmpTR += "</td>"
                    
                    self.caseNum += 1                    
                    if not logfile[1].Results.TestSession.Test.TestResult.passed == 'True':
                        isPassedAllSubTestCases = False
                        strTmpTR += '''
                            <td align="center" class="Error"> ''' 
#                        strTmpTR += '<input class="Error" type="submit" value="' + logfile[1].Results.TestSession.Test.TestResult.passed + '" onClick="openPage(\'' + self.generateDetailReport(item) + '\')">'
                        strTmpTR += '<a href="' + self.generateDetailReport(logfile[1].Results.TestSession.Test) + '" target="_blank">'
                        strTmpTR += str(logfile[1].Results.TestSession.Test.TestResult.passed)
                        strTmpTR += "</a>"
                    else:
                        self.passCaseNum += 1
                        strTmpTR += '''
                            <td align="center" class="Success"> '''
                        strTmpTR += logfile[1].Results.TestSession.Test.TestResult.passed
#                        strTmpTR += "<font color='green'>"
#                        strTmpTR += logfile[1].Results.TestSession.Test.TestResult.passed
#                        strTmpTR += "</font>"
                    strTmpTR += "</td>"
                        
                        #TODO: Extend the case owner
                    strTmpTR += "<td/>"
                        
                    strTmpTR += '''
                        <td>'''
                    strTmpTR += logfile[1].Results.TestSession.Test.TestResult.executionTime
                    strTmpTR += ' (ms)'
                    strTmpTR += "</td>"
                    strTmpTR += "</tr>"
                    
                    startTime = datetime.datetime.strptime(logfile[1].Results.TestSession.Test.TestResult.startTime, '%Y-%m-%dT%H:%M:%S')
                    if self.minStartTime==None or self.beforeTime(startTime, self.minStartTime):
                        self.minStartTime = startTime
                            
                    endTime = datetime.datetime.strptime(logfile[1].Results.TestSession.Test.TestResult.endTime, '%Y-%m-%dT%H:%M:%S')
                    if self.maxEndTime==None or self.beforeTime(self.maxEndTime, endTime):
                        self.maxEndTime = endTime

            except Exception, Err:
                self.logger.error("Please check the file %s" %key)
                exstr = traceback.format_exc()
                self.logger.warning(exstr)
                isPassedAllSubTestCases = False
                strTmpTR = '''
                <tr>
                    <td width="20">'''
                strTmpTR += logfile[0]
                strTmpTR += "</td>"
                strTmpTR += '''
                <td>'''
                strTmpTR += "Unknown Error Occurs"
                strTmpTR += "</td>"
                strTmpTR += '''
                <td>'''
                strTmpTR += '<font color="red">'
                strTmpTR += 'False'
                strTmpTR += '</font>'
                strTmpTR += "</td>"
                #TODO: Extend the case owner
                strTmpTR += "<td/>"
                strTmpTR += '''
                <td>'''
                strTmpTR += '???'
                strTmpTR += ' (ms)'
                strTmpTR += "</td>"
                strTmpTR += "</tr>"    
                
                #print Err
            
            if isPassedAllSubTestCases:
                strTmpBody += strTmpTR
            else:
                strTmpBody = strTmpTR + strTmpBody
            
        self.htmlBody += strTmpBody
        self.htmlBody += '''
        </table>
        '''
        return self.htmlBody
    
    def generateDetailReport(self, item):
        detailReportPath, detailReportHierarchy = self.getUniqueDetailReportPath(item)
        detailContent = item.TestResult.Details
        sublines = detailContent.split('\n')
        
        findError = False
        i = 0
        count = 0
        length = len(sublines)
        for subline in sublines:
            if findError:
                if count<2:
                    count = count+1
                else:
                    count = 0
                    findError = False
                    sublines[i] = subline + "</B>"
            elif re.match(r'.*ERROR:.*', subline):
                findError = True
                sublines[i] = "<B style='color:black;background-color:#ff9999'>" + subline
            elif re.match(r'.*(Warn).*', subline):
                sublines[i] = "<B style='color:black;background-color:#ffff66'>" + subline + "</B>"
            elif re.match(r'.*(Pass).*', subline):
                sublines[i] = "<B style='color:black;background-color:#99ff99'>" + subline + "</B>"
            i = i+1
            
        
        htmlText = '''<html>
    <meta http-equiv="content-type" content="text/html;charset=utf-8">
    <body>
'''
        htmlText += '\n<br>'.join(sublines)
        htmlText += '''
    </body>
</html>
'''
        file_obj = open(detailReportPath, 'w')
                
        file_obj.write(htmlText.encode('utf-8'))
            
        file_obj.close()
        
        detailReportHtmlPath = self.logServerPath + re.sub(".*(/" + self.AUT_platform + "/.*)", r"\1", detailReportHierarchy.replace("\\", "/"))
        
        return detailReportHtmlPath
        
    def getUniqueDetailReportPath(self, item):
        detailReportHierarchy = os.path.join(self.curReportHierachy, "details", item.name + ".html")
        detailReportPath = os.path.join(self.curReportPath, "details", item.name + ".html")
        step = 1
        while os.path.exists(detailReportPath):
            detailReportPath = os.path.join(self.curReportPath, "details", item.name + "_" + str(step) + ".html")
            step += 1
            
        return detailReportPath, detailReportHierarchy
    
    def uploadReport(self):
        from FTPUploadTask import childTask
        task = childTask('task')
        task.addPara('Host', self.logServer)
        task.addPara('User', self._commonDomain + '\\' + self._commonUser)
        task.addPara('Passwd', self._commonPassword)
        task.addPara('Repository', "/filtertestResults")
        task.addPara('FolderPath', self.curReportPath)
        task.addPara('baseDir', self.AUT_platform)
        task.run()
        
    def _cleanReport(self):
        try:
            if (os.path.exists(self.htmlReportFileRoot)):
                self.logger.info('Clean Html Report %s' % self.htmlReportFileRoot)
                shutil.rmtree(self.htmlReportFileRoot)
        except WindowsError, (errno,strerror):
            self.logger.error("catch WindowsError: error(%s): %s" % (errno,strerror))


##################This section is mainly for debug -- Begin #############################
if __name__ == '__main__':
    ro=childTask('PSFReporter', 1)
    ro.addPara('FeatureOwner', 'jacky')
    ro.run()

##################This section is mainly for debug -- End #############################
