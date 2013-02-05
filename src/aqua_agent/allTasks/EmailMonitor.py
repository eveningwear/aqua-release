"""

    EmailMonitor.py
        
    Written by: Jacky Li (yxli@adobe.com)

"""
import smtplib
import os
import string
import socket
import globalProperty
import re

from allTasks.baseTask import Task
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders

class childTask(Task):
    
    def __init__(self, type, priority):
        super(childTask, self).__init__(type, priority)
        self.tmpFolder = os.path.join(os.getcwd(), 'tmp')
        return

    def run(self):
        self.logger.info('Start email monitor')
            
        send_from = 'QMS@adobe.com'
        if self.parameter.has_key('From'):
            send_from = self.parameter['From']
        
        user = globalProperty.getUser()
        if user==None:
            defaultTo = 'yxli@adobe.com'
        else:
            defaultTo = '%s@adobe.com' % user
            
        """
        if self.parameter.has_key('To'):
            send_to = self.parameter['To'].replace(';', ',').split(',')
        else:
            send_to = defaultTo.split(',')
        """
        send_to = self.parameter['To'] if self.parameter.has_key('To') else defaultTo
        
        if self.exeId==None:
            self.logger.info('No Result could be sent out for monitoring')
            return
        
        reportFile = self.getHtmlReport()
        if reportFile==None or not os.path.exists(reportFile):
            return
        
        #Send Report
        from HtmlEmailUtil import childTask
        htmlEmailUtil = childTask('HtmlEmailUtil', self.priority + 2)
        
        htmlEmailUtil.addPara('From', send_from)
        htmlEmailUtil.addPara('To', send_to)
        
        if globalProperty.isMachineOutOfChina():
            htmlEmailUtil.addPara('SMTPServer', self._dbutil.getAppInfo('email_server_us'))
        else:
            htmlEmailUtil.addPara('SMTPServer', self._dbutil.getAppInfo('email_server_cn'))
        if self.parameter.has_key('Subject'):
            subject = self.parameter['Subject']
        else:
            subject = 'Email Monitor from %s -- %s' % (socket.gethostname(), self._getCurrentTime())
        htmlEmailUtil.addPara('Subject', subject)
        htmlEmailUtil.addPara('ReportFile', reportFile)
        htmlEmailUtil.run()
        """
        result = self._dbutil.getExecutionResult(self.exeId)
        #task_name, start_time, finish_time, status, error_msg
        hostname = socket.gethostname()
        strBody = 'Machine Name: %s' %(hostname) + '\t\t'
        
        ipAddress = globalProperty.getIpAddress()
        strBody += 'Current IP: %s' %(ipAddress)
        strBody += '\nJob ID: %s' %(self.jobId) + '\t\t'
        strBody += 'Execution ID: %s' %(self.exeId)
        
        strBody += '\n\n' + \
            'Task Name'.ljust(25) + \
            'Start Time'.ljust(25) + \
            'Finish Time'.ljust(25) + \
            'Status'.ljust(25) + \
            'Error Message'.ljust(25) + '\n' + '-' * 125 + '\n'        
        
        strSubject = 'Email Monitor from %s -- %s' % (hostname, self._getCurrentTime())
        
        executionSequence = 1
        for task in result:
            strBody += string.join(map(lambda o: o.__str__().ljust(25), task), '') + '\n'
            executionSequence += 1
            
        jobList = self._dbutil.getJobDetail(self.jobId)
        if(jobList!=None):
            for job in jobList:
                if executionSequence==job[1]:
                    strBody +=  job[0].ljust(25)
                    strBody += 'None'.ljust(25)
                    strBody += 'None'.ljust(25)
                    strBody += 'Ready'.ljust(25)
                    strBody += 'None'.ljust(25) + '\n'
                executionSequence += 1
        
        assert type(send_to)==list

        msg = MIMEMultipart()
        msg['From'] = send_from
        msg['To'] = COMMASPACE.join(send_to)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = strSubject

        msg.attach( MIMEText(strBody) )

        smtp = smtplib.SMTP(server)
        smtp.sendmail(send_from, send_to, msg.as_string())
        smtp.close()
        """
        
    def getHtmlReport(self):
        self.formatTableStyle()
        self.formatJavascript()
        self.formatReportHeader()
        self.formatReportFooter()
        self.formatReportBody()
        self.formatReportSummary()
    
        self.formatUniqueReportFileName()
    
        htmlText = self.htmlHeader + self.javascript + self.htmlTableStyle + self.htmlSummary + self.htmlBody + self.htmlFooter
        
        self.htmlReportFilePath = os.path.join(self.tmpFolder, self.htmlReportFile)
        file_obj = open(self.htmlReportFilePath, 'w')
        file_obj.write(htmlText.encode('utf-8'))
        file_obj.close()
        
        return self.htmlReportFilePath
    
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
        self.htmlSummary = '''
    <body>
    <h2>Basic Information</h2>
    <table class="details" border="0" cellpadding="5" cellspacing="2" width="98%">
    <tr>
    <th>Machine Name</th>
    <th>Current IP</th>
    <th>Job ID</th>
    <th>Execution ID</th>
    </tr>
    <tr align="center">
    '''
        self.htmlSummary += "<td><strong>%s<strong></td>" % socket.gethostname()
        self.htmlSummary += "<td><strong>%s<strong></td>" % globalProperty.getIpAddress()
        self.htmlSummary += "<td><strong>%s<strong></td>" % self.jobId
        self.htmlSummary += "<td><strong>%s<strong></td>" % self.exeId
        self.htmlSummary += '''
    </tr>
    </table>
    '''
        return self.htmlSummary

    def formatUniqueReportFileName(self):
        self.htmlReportFile = "job_monitor.html"
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
    <h2>Detailed Tasks</h2>
    <table class="details" border="0" cellpadding="5" cellspacing="2" width="98%">
    <tr>
    <th width="20">Task Name</th>
    <th>Start Time</th>
    <th>Finish Time</th>
    <th>Status</th>
    <th>Error Message</th>
    </tr>
'''
        result = self._dbutil.getExecutionResult(self.exeId)
        executionSequence = 0
        for task in result:
            self.htmlBody += '''
    <tr>
    '''
            self.htmlBody += '<td align="center"><strong>%s<strong></td>' % task[0]
            self.htmlBody += '<td align="center">%s</td>' % task[1]
            self.htmlBody += '<td align="center">%s</td>' % task[2]
            if task[3]=="succeed":
                self.htmlBody += '<td align="center"><font color="green">%s<font></td>' % task[3]
            elif task[3]=="failed":
                self.htmlBody += '<td align="center"><font color="red">%s<font></td>' % task[3]
            else:
                self.htmlBody += '<td align="center">%s</td>' % task[3]
            self.htmlBody += '<td><font color="red">%s<font></td>' % task[4]
            #self.htmlBody += string.join(map(lambda o: """
            #<td>%s</td>""" % o.__str__(), task), '')
            self.htmlBody += '''
    </tr>
    '''
            executionSequence = task[5]
        
        jobList = self._dbutil.getJobDetail(self.jobId)
        if(jobList!=None):
            getJobLeft = False
            for job in jobList:
                if int(job[1])>int(executionSequence) and not getJobLeft:
                    getJobLeft = True
                    
                if getJobLeft:
                    self.htmlBody += '''
    <tr>
    '''
                    self.htmlBody += '<td align="center"><strong>%s<strong></td>' % job[0]
                    self.htmlBody += '<td align="center">wait</td>'
                    self.htmlBody += '<td align="center">wait</td>'
                    self.htmlBody += '<td align="center">wait</td>'
                    self.htmlBody += "<td></td>"
                    self.htmlBody += '''
    </tr>
    '''
                
        self.htmlBody += '''
    </table>
    '''
        return self.htmlBody

if __name__ == '__main__':
    task = childTask('xx', 1)
    task.addPara('From', 'yxli@adobe.com')
    task.addPara('To', 'yxli@adobe.com')
    task.exeId = "29110"
    task.jobId = "d662c28f-faeb-11e0-af94-0024e832d01c"
    task.getHtmlReport()
