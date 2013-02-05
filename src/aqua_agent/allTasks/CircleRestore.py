"""

    CircleRestore.py
    
    Written by: Jacky Li (yxli@adobe.com)

"""

from allTasks.baseTask import Task
import os, os.path, re, time, machine, sys
from xml.dom import minidom,Node

import globalProperty

class childTask(Task):
    
    def __init__(self, type, priority):
        super(childTask, self).__init__(type, priority)
        self.imagesList = []
        self.doc = None
    
    def run(self):
        self.logger.info('Starting circle restoring OS')
        
        """
        self.initCircleImageFile()
        if len(self.imagesList)==0:
            self.logger.warning("No image found")
            return
        """
        
        self.imageMonitorFile = os.path.join(os.getcwd(), 'imageMonitor.txt')
        self.imagePos = self.getLastImagePos()
        self.imagePos += 1
                
        """
        if imagePos >= len(self.imagesList):
            imagePos = 0
        """
        
        if not "OSImageLocation%s" % self.imagePos in self.parameter:
            self.imagePos = 1
        
        #self.selectedImageAttr = self.imagesList[imagePos]
        self.monitorImage(self.imagePos)
        #self.runRestoreOS(self.selectedImageAttr)
        self.__runRestoreOS()
        
    def runRestoreOS(self, imageAttrs):
        from RestoreOS import childTask
        task = childTask('ResotreOS', 1)
        for key in imageAttrs.keys():
            if key=='type':
                continue
            task.addPara(key, imageAttrs[key])
        task.run()
        
    def __runRestoreOS(self):
        from RestoreOS import childTask
        task = childTask('ResotreOS', 1)
        for key in self.parameter.keys():
            if key=='type' or re.match("OSImageLocation.", key):
                continue
            task.addPara(key, self.parameter[key])
        task.addPara("OSImageLocation", self.parameter["OSImageLocation%s" % self.imagePos])
        task.run()
        
    def getLastImagePos(self):
        imagePos = 0
        if os.path.exists(self.imageMonitorFile):
            f = open(self.imageMonitorFile, "r")
            content = f.read()
            if content!=None and content.strip()!="":
                imagePos = int(content)
        return imagePos
            
        
    def monitorImage(self, imageNum):
        f = open(self.imageMonitorFile, "w")
        f.write(str(imageNum))
        f.flush()
        f.close()
    
    def initDirectory(self):
        self.circleImageListDir = os.path.join(os.getcwd(), 'circleImages')
        if not os.path.exists(self.circleImageListDir):
            os.makedirs(self.circleImageListDir)
        
    #Deprecated
    def initCircleImageFile(self):
        self.initDirectory()
        self.imagesRepositoryFile = os.path.join(self.circleImageListDir, 'imagesRepository.xml')
        self.imageMonitorFile = os.path.join(self.circleImageListDir, 'imageMonitor.txt')
        if not os.path.exists(self.imagesRepositoryFile):
            #create a new scheduleTasksFile
            self.doc = minidom.Document()
            
            scheduleTasks = self.doc.createElement("images")
            self.doc.appendChild(scheduleTasks)
            
            myTestXML = self.doc.toprettyxml()
            
            self.writeXML()
        self.loadImages()
    
    def writeXML(self):        
        images = self.doc.getElementsByTagName("images")[0]
        self.__removeTextChildNodeRecursion(images)
        f = open(self.imagesRepositoryFile, "w")
        myTestXML = self.doc.toprettyxml()
        f.write(myTestXML)
        f.close()
    
    def __removeTextChildNodeRecursion(self, parent):
        textNodeList = []
        for node in parent.childNodes:
            if node.nodeType == node.ELEMENT_NODE:
                self.__removeTextChildNodeRecursion(node)
            elif node.nodeType == node.TEXT_NODE:
                textNodeList.append(node)
                #print parent.nodeName + ':Remove Child ' + node.nodeName
                #parent.removeChild(node)
        for node in textNodeList:
            #print parent.nodeName + ':Remove Child ' + node.nodeName
            parent.removeChild(node)
    
    #Deprecated
    def loadImages(self):
        if self.doc==None:
            self.doc = minidom.parse(self.imagesRepositoryFile)
        
        images = self.doc.getElementsByTagName("images")[0]
        
        for node in images.childNodes:
            if node.nodeType == node.TEXT_NODE:
                continue
            else:
                imageAttr = self.__getImageAttrs(node)
                self.imagesList.append(imageAttr)

    #Deprecated 
    def __getImageAttrs(self, tasksParent):
        attrs = {}
        for attr in tasksParent.attributes.items():
            attrs[attr[0]] = attr[1]
        return attrs
        

##################This section is mainly for debug -- Begin #############################
if __name__ == '__main__':    
    crt=childTask('crt', 1)
    crt.addPara('OSImageLocation1', 'test1')
    crt.addPara('OSImageLocation2', 'test2')
    crt.run()
    #ro.getLabPETool()
##################This section is mainly for debug -- End #############################
