"""

    HtmlEmailUtil.py
    
    Written by: Jacky Li (yxli@adobe.com)

"""

import smtplib
import os

from allTasks.baseTask import Task
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders

class childTask(Task):
    
    def __init__(self, type, priority):
        super(childTask, self).__init__(type, priority)
        self.exeId = None
        return

    def run(self):
        print 'HtmlEmailUtil run'
        self.logger.info('Start email')
        
        fromAddr = self.parameter['From']
        toAddr = self.parameter['To']
        subject = self.parameter['Subject']
        server = self.parameter['SMTPServer']
        reportFile = self.parameter['ReportFile']
        self.sendMail(toAddr, fromAddr, subject, reportFile)
    
    # Sends an email copy of results
    def sendMail(self, toAddr, fromAddr, subject, reportFile):
        endl = "\n"
        
        toList = toAddr.replace(';', ',').split(",") # in case of multiple addresses
        
        from smtplib import SMTP
        server = self._dbutil.getAppInfo('email_server_cn')
        
        '''
        msg = MIMEMultipart()
        msg['From'] = fromAddr
        msg['To'] = COMMASPACE.join(toList)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject        
        '''
        msg = "From: " + fromAddr + endl
        msg += "To: " + COMMASPACE.join(toList) + endl
        msg += "Subject: " + subject + endl
        msg += "Mime-Version: 1.0" + endl
        msg += "Content-Type: text/html; charset=ISO-8859-1" + endl + endl
        reportF = file(reportFile, 'r')
        lines = reportF.readlines()
        #strBody = ''
        for line in lines:
            msg += line
            reportF.close()
        #msg.attach( MIMEText(strBody) )
        smtp = smtplib.SMTP(server)
        self.logger.info('Sending Email to %s' % toAddr)
        smtp.sendmail(fromAddr, toList, msg)
        smtp.close()

if __name__ == '__main__':
    task = childTask('xx', 1)
    task.addPara('From', 'yxli@adobe.com')
    task.addPara('To', 'yxli@adobe.com')
    task.addPara('Subject', 'Just for test')
    task.addPara('SMTPServer', 'mailsj-v1.corp.adobe.com')
    task.addPara('Subject', 'Just for test')
    task.addPara('ReportFile', 'stealthReport.html')
    task.run()