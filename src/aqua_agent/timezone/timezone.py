"""

    timezone.py
    
    Written by: Jacky Li (yxli@adobe.com)

"""
import logging
import time
from datetime import timedelta, datetime, tzinfo

class basetime(tzinfo):

    def __init__(self, type, dstType=None, hourdelta=0, supportDST=False):
        self.logger = logging.getLogger()
        #self.logger.info('-----Generete a timezone:' + type)
        
        self.type = type
        self.dstType = dstType
        self.supportDST = supportDST
        self.hourdelta = hourdelta
        
    def utcoffset(self, dt):
        return timedelta(hours=self.hourdelta) + self.dst(dt)
    
    def dst(self, dt):
        if self.supportDST:
            d = datetime(dt.year, 4, 1)
            self.dston = d - timedelta(days=d.weekday() + 1)
            d = datetime(dt.year, 11, 1)
            self.dstoff = d - timedelta(days=d.weekday() + 1)
            if self.dston <=  dt.replace(tzinfo=None) < self.dstoff:
                self.type = self.dstType
                return timedelta(hours=1)
        return timedelta(0)
    
    def tzname(self, dt):
        return self.type
    
class GMT(basetime):
    def __init__(self):
        super(GMT, self).__init__("Greenwich Mean Time", None, 0)

class CST(basetime):
    def __init__(self):
        super(CST, self).__init__("China Standard Time", None, 8)
        
class PST(basetime):
    def __init__(self):
        super(PST, self).__init__("Pacific Standard Time", "Pacific Daylight Time", -8, True)
        
class PDT(basetime):
    def __init__(self):
        super(PDT, self).__init__("Pacific Standard Time", "Pacific Daylight Time", -8, True)
        
class MST(basetime):
    def __init__(self):
        super(MST, self).__init__("Mountain Standard Time", "Mountain Daylight Time", -7, True)
        
class MDT(basetime):
    def __init__(self):
        super(MDT, self).__init__("Mountain Standard Time", "Mountain Daylight Time", -7, True)
        
class CDT(basetime):
    def __init__(self):
        super(CDT, self).__init__("Central Standard Time", "Central Daylight Time", -6, True)
        
class EST(basetime):
    def __init__(self):
        super(EST, self).__init__("Eastern Standard Time", "Eastern Daylight Time", -5, True)
        
class EDT(basetime):
    def __init__(self):
        super(EDT, self).__init__("Eastern Standard Time", "Eastern Daylight Time", -5, True)
        
tzdictionary = {
                "CST":["China Standard Time", "China Daylight Time", "CST"],
                "PST":["Pacific Standard Time", "Pacific Daylight Time", "PST", "PDT"],
                "MST":["Mountain Standard Time", "Mountain Daylight Time", "MST", "MDT"],
                "CDT":["Central Standard Time", "Central Daylight Time", "CDT"],
                "EST":["Eastern Standard Time", "Eastern Daylight Time", "EST", "EDT"]
                }
        
def getTimeZone(tzname):
    tzClassName = "GMT"
    tzclass = None
    
    for key in tzdictionary:
        if tzname in tzdictionary[key]:
            tzClassName = key
            break;
        
    tzClassStr = "tzclass = %s()" % tzClassName
    exec tzClassStr
    return tzclass


####################For Test#########################3
if __name__ == '__main__':
    t = time.gmtime()
    curtime = datetime(t[0], 3, t[2], t[3], t[4], t[5], tzinfo=GMT())
    bjt = CST()
    #curdate = datetime(2009, 8, 9, 13, 52, tzinfo=bjt)
    curdate = curtime.astimezone(bjt)
    print curdate.strftime("%Y-%m-%d %H:%M:%S %Z")
    pt = PDT()
    newdate = curdate.astimezone(pt)
    print newdate.strftime("%Y-%m-%d %H:%M:%S %Z")
    testdate = datetime(2009, 8, 12, 10, 40, tzinfo=bjt)
    print curtime-testdate
    print curdate-testdate
    dt = curtime-testdate
    print dt.seconds
#    print "%s %s:%s:%s" %(dt.days, dt.hours, dt.minutes, dt.seconds)
    test = curdate + timedelta(seconds=3000)
    #newdate = test.astimezone(bjt)
    test1 = test.astimezone(pt)
    print test1.strftime("%Y-%m-%d %H:%M:%S %Z")
    