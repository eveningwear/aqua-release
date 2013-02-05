"""

    cloudNode.py
    
    Spaceholder firstly
    
    Written by: Jacky Li (yxli@adobe.com)

"""

import socket
import logging
import globalProperty
import Queue
import time
from xml.dom import minidom,Node

from threading import Thread, RLock, Condition


class cloudNode(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.setName("cloudNode")
        
    def run(self):
        return