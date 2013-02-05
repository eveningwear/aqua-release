"""

    EmailUtil.py
    
    Written by: Tony Wu (wxin@adobe.com)    
    Written by: Jacky Li (yxli@adobe.com)

"""
import smtplib
import os
import string

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
        print 'EmailUtil run'
        self.logger.info('Start email')
        
        send_from = self.parameter['From']
        send_to = self.parameter['To'].split(';')
        strSubject = self.parameter['Subject']
        server = self.parameter['SMTPServer']
        
        result = self._dbutil.getExecutionResult(self.exeId)
        #task_name, start_time, finish_time, status, error_msg
        strBody = 'Execution Result\nTask Name\tStart Time\tFinish Time\tStatus\tError Message\n' + '-' * 200 + '\n'
        for task in result:
            strBody += string.join(map(lambda o: o.__str__(), task), "\t") + '\n'
        
        print 'AttachLog is ', self.parameter['AttachLog']
        files=['restoretool.log']
        
        assert type(send_to)==list
        assert type(files)==list

        msg = MIMEMultipart()
        msg['From'] = send_from
        msg['To'] = COMMASPACE.join(send_to)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = strSubject

        msg.attach( MIMEText(strBody) )

        for f in files:
            part = MIMEBase('application', "octet-stream")
            part.set_payload( open(f,"rb").read() )
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
            msg.attach(part)
        smtp = smtplib.SMTP(server)
        smtp.sendmail(send_from, send_to, msg.as_string())
        smtp.close()
        return
