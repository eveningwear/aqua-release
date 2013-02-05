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


import re

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
        userHome = os.path.expanduser("~")
        psfHome = os.path.join(userHome, 'PSF')
        self.psfPath = psfHome
        self.logDicts = {}
        
    	#################################
        self.htmlTableStyle = ""
        self.htmlHeader = ""
        self.htmlSummary = ""
        self.htmlFooter = ""
        self.htmlBody = ""
    
        self.htmlReportFileRoot = os.path.join(os.getcwd(), 'PSFReport')
        if(not os.path.exists(self.htmlReportFileRoot)):
            os.mkdir(self.htmlReportFileRoot)
        self.htmlReportFile = ""
    	#################################
        
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
        
        if(not os.path.exists(self.psfPath)):
    	    print("There is no PSF installed in [%s]" % self.psfPath)
    	    raise ("There is no PSF installed in [%s]" % self.psfPath)

    def run(self):
    	self.logger.info('Starting PSF log parsing')
    	self.psfLogPath = os.path.join(self.psfPath , 'logs')
    	self.walkLogFiles(self.psfLogPath, self.doXmlParsing)
        
        #self.output()
        self.writeHtmlReport()
        self.formatUniqueReportFileName()

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
    	    self.logDicts[lf] = r
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
    	self.formatReportHeader()
    	self.formatReportFooter()
    	self.formatReportBody()
    	self.formatReportSummary()
    
    	self.formatUniqueReportFileName()
    
    	htmlText = self.htmlHeader + self.htmlTableStyle + self.htmlSummary + self.htmlBody + self.htmlFooter
    	#self.htmlReportFile = "/Users/lbaichao/Desktop/psf_report.html"
        self.htmlReportFilePath = os.path.join(self.htmlReportFileRoot, self.htmlReportFile)
    	file_obj = open(self.htmlReportFilePath, 'w')
    	file_obj.write(htmlText)
    	file_obj.close()
        
    def getHtmlReport(self):
        return self.htmlReportFilePath

    def formatTableStyle(self):
        self.htmlTableStyle = ""
        self.htmlTableStyle = '''

<style type="text/css">
CAPTION.MYTABLE
{
	font-family:arial;
	font-size:12pt;
	background-color:#8080ff;
	color:white;
	border-style:solid;
	border-width:2px;
	border-color:black;
}

TABLE.MYTABLE
{ 
	font-family:arial;
	font-size:10pt;
	background-color:#808080;
	width:800px;
	border-style:solid;
	border-color:black;
	border-width:2px;
}

TH.MYTABLE
{
	font-size:10pt;
	color:white;
      border-style:solid;
      border-width:1px;
      border-color:black;
}


TR.MYTABLE
{ 
}

TD.MYTABLE
{  
	font-size:10pt;
	background-color:#409040;
	color:white;
	border-style:solid;
	border-width:1px;
	border-color:black;
	text-align:left;
}
</style>

'''

    def formatReportSummary(self):
    	self.htmlSummary= ""
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
			    self.htmlSummary += "<B>Application Under Test:</B>"
			    self.htmlSummary += logfile[1].Results.TestSession.AUT.name
			    self.AUT_name = logfile[1].Results.TestSession.AUT.name
			    self.htmlSummary += "\t<B>Version:</B>"
			    self.htmlSummary += logfile[1].Results.TestSession.AUT.version
			    self.AUT_version = logfile[1].Results.TestSession.AUT.version
			    self.htmlSummary += "\t<B>Build:</B>"
			    self.htmlSummary += logfile[1].Results.TestSession.Build.label
			    self.AUT_build = logfile[1].Results.TestSession.Build.label
			    self.htmlSummary += "\t<B>Platform:</B>" 
			    self.htmlSummary += logfile[1].Results.TestSession.AUT.platform
			    self.AUT_platform = logfile[1].Results.TestSession.AUT.platform
			    self.htmlSummary += "\t<B>Locale:</B>" 
			    self.htmlSummary += logfile[1].Results.TestSession.AUT.locale
			    self.AUT_locale = logfile[1].Results.TestSession.AUT.locale
		
			    self.htmlSummary += "\n<p><B>Machine:</B>"
			    self.htmlSummary += logfile[1].Results.TestSession.TestEnvironment.machineName
			    self.TestEnvironment_machineName = logfile[1].Results.TestSession.TestEnvironment.machineName
			    self.htmlSummary += "\t<B>OsVersion:</B>" 
			    self.htmlSummary += logfile[1].Results.TestSession.TestEnvironment.osVersion 
			    self.TestEnvironment_osVersion = logfile[1].Results.TestSession.TestEnvironment.osVersion
			    self.htmlSummary += "\t<B>SystemLanguage:</B>" 
			    self.htmlSummary += logfile[1].Results.TestSession.TestEnvironment.systemLanguage
			    self.TestEnvironment_systemLanguage = logfile[1].Results.TestSession.TestEnvironment.systemLanguage
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
		
        
        
    	self.htmlSummary += "\n<p><B>TestResults:</B>"
    	self.htmlSummary += "\t" 
    	self.htmlSummary += str(self.failedTestLogs) 
    	self.htmlSummary += " failed in total\t"
    	self.htmlSummary += str(self.totalTestLogs)
    	self.htmlSummary += "<p>"
    	return self.htmlSummary

    def formatUniqueReportFileName(self):
    	from datetime import datetime
    	n = datetime.now()
    	strTimeName = ""
    	#for item in n.timetuple():
    	for item in n.timetuple():
    	    strTimeName += "_"
    	    if( item < 0):
        		item = -1 * item
        		strTimeName += "_"
            strTimeName += str(item)
    	    #print strTimeName
    	self.htmlReportFile = "Report"
    	self.htmlReportFile += "_"
    	self.htmlReportFile += self.AUT_name
    	self.htmlReportFile += "_"
    	self.htmlReportFile += self.AUT_version
    	self.htmlReportFile += "."
    	self.htmlReportFile += self.AUT_build
    	self.htmlReportFile += "_"
    	self.htmlReportFile += self.AUT_platform
    	self.htmlReportFile += "_"
    	self.htmlReportFile += self.AUT_locale
    	self.htmlReportFile += "_"
    	self.htmlReportFile += self.TestEnvironment_machineName
    	self.htmlReportFile += "_"
    	self.htmlReportFile += self.TestEnvironment_osVersion
    	self.htmlReportFile += "_"
    	self.htmlReportFile += self.TestEnvironment_systemLanguage
    
    	self.htmlReportFile += strTimeName
	self.htmlReportFile = re.sub("[/\\:*?\"<>|]", "_", self.htmlReportFile) 
    	self.htmlReportFile += ".html"
    	return self.htmlReportFile
    

    def formatReportHeader(self):
    	self.htmlHeader = ""
        self.htmlHeader += '''
<html>
    <body>
''' 
        return self.htmlHeader

    def formatReportFooter(self):
    	self.htmlFooter = ""
    	self.htmlFooter += '''
    </body>
</html>
'''
        return self.htmlFooter


    def formatReportBody(self):
        self.htmlBody = ""
        self.htmlBody += '''
    <TABLE class="MYTABLE">
    <CAPTION class="MYTABLE">Detailed Report of PSF Results</CAPTION>
    <THEAD>
    <TR class="MYTABLE">
    <TH class="MYTABLE" width="20">TEST LOG NAME</TH>
    <TH class="MYTABLE">TEST CASE NAME</TH>
    <TH class="MYTABLE">PASSED</TH>
    <TH class="MYTABLE">EXECUTION TIME</TH>
    </TR>
    </THEAD>
    '''

	logFileKeys = self.logDicts.keys()
	logFileKeys.sort()
	for key in logFileKeys:
	    logfile = (key, self.logDicts[key])
    	#for logfile in self.logDicts.items():	
            #print logfile
	    strTmpTR = ""
	    try:
		if isinstance(logfile[1].Results.TestSession.Test, list):
		    hasWrittenLogName = False 
		    isPassedAllSubTestCases = True
		    for item in logfile[1].Results.TestSession.Test:
			if not item.TestResult.passed == "True":
			    isPassedAllSubTestCases = False;
			    break
	      
		    for item in logfile[1].Results.TestSession.Test:
			if not hasWrittenLogName:
			    strTmpTR += '''
				<TR class="MYTABLE">
				<TD class="MYTABLE">'''
			    strTmpTR += logfile[0]
			    hasWrittenLogName = True
			    strTmpTR += '</TD><TD class="MYTABLE"/><TD class="MYTABLE">'
			    if not isPassedAllSubTestCases:
				strTmpTR += "<font color='red'>"
				strTmpTR += str(isPassedAllSubTestCases)
				strTmpTR += "</font>"
			    else:
				strTmpTR += str(isPassedAllSubTestCases)
			    strTmpTR += '</TD><TD class="MYTABLE"/>'
	    
			strTmpTR += '''
				<TR class="MYTABLE">
				<TD class="MYTABLE"/>'''
			strTmpTR += '''
				<TD class="MYTABLE">'''
			strTmpTR += item.name
			strTmpTR += "</TD>"
				
			strTmpTR += '''
				<TD class="MYTABLE"> ''' 
			if not item.TestResult.passed == "True":
			    strTmpTR += "<font color='red'>"
			    strTmpTR += item.TestResult.passed
			    strTmpTR += "</font>"
			else:
			    strTmpTR += item.TestResult.passed
			strTmpTR += "</TD>"
    
			strTmpTR += '''
				<TD class="MYTABLE">'''
			strTmpTR += item.TestResult.executionTime
			strTmpTR += ' (ms)'
			strTmpTR += "</TD>"
			
			strTmpTR += "</TR>"
		else:
		    strTmpTR += '''
			<TR class="MYTABLE">
			    <TD class="MYTABLE" width="20">'''
		    strTmpTR += logfile[0]
		    strTmpTR += "</TD>"
		    strTmpTR += '''
			<TD class="MYTABLE">'''
		    strTmpTR += logfile[1].Results.TestSession.Test.name
		    strTmpTR += "</TD>"
		    strTmpTR += '''
			<TD class="MYTABLE">'''
		    if not logfile[1].Results.TestSession.Test.TestResult.passed == 'True':
			strTmpTR += "<font color='red'>"
			strTmpTR += str(logfile[1].Results.TestSession.Test.TestResult.passed)
			strTmpTR += "</font>"
		    else:
			strTmpTR += logfile[1].Results.TestSession.Test.TestResult.passed
		    strTmpTR += "</TD>"
		    strTmpTR += '''
			<TD class="MYTABLE">'''
		    strTmpTR += logfile[1].Results.TestSession.Test.TestResult.executionTime
		    strTmpTR += ' (ms)'
		    strTmpTR += "</TD>"
		    strTmpTR += "</TR>"
		    
	    except Exception, Err:
		    self.htmlBody += '''
			<TR class="MYTABLE">
			    <TD class="MYTABLE" width="20">'''
		    self.htmlBody += logfile[0]
		    self.htmlBody += "</TD>"
		    self.htmlBody += '''
			<TD class="MYTABLE">'''
		    self.htmlBody += "Unknown Error Occurs"
		    self.htmlBody += "</TD>"
		    self.htmlBody += '''
			<TD class="MYTABLE">'''
		    self.htmlBody += '<font color="red">'
		    self.htmlBody += 'False'
		    self.htmlBody += '</font>'
		    self.htmlBody += "</TD>"
		    self.htmlBody += '''
			<TD class="MYTABLE">'''
		    self.htmlBody += '???'
		    self.htmlBody += ' (ms)'
		    self.htmlBody += "</TD>"
		    self.htmlBody += "</TR>"	
		    
		    #print Err
		

	    self.htmlBody += strTmpTR
        self.htmlBody += '''
    </TABLE>
    '''
        return self.htmlBody



##################This section is mainly for debug -- Begin #############################
if __name__ == '__main__':
    ro=childTask('PSFReporter', 1)
    ro.run()

##################This section is mainly for debug -- End #############################
