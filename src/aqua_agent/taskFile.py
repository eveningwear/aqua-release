
class taskFile:
    def __init__(self, type, fileName, startDate, startTime):
        self.__type = type
        self.__fileName = fileName
        self.__startDate = startDate
        self.__startTime = startTime
        
    def getType(self):
        return self.__type
        
    def getFileName(self):
        return self.__fileName
    
    def getStartDate(self):
        return self.__startDate
    
    def getStartTime(self):
        return self.__startTime
    
    def compare(self, tksFile):
        if self.__fileName == tksFile.getFileName() and \
           self.__startDate == tksFile.getStartDate() and \
           self.__startTime == tksFile.getStartTime():
            return True
        return False