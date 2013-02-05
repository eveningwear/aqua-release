########################################################################
#
# File Name:            HTMLQuoteElement
#
#

### This file is automatically generated by GenerateHtml.py.
### DO NOT EDIT!

"""
WWW: http://4suite.com/4DOM         e-mail: support@4suite.com

Copyright (c) 2000 Fourthought Inc, USA.   All Rights Reserved.
See  http://4suite.com/COPYRIGHT  for license and copyright information
"""

import string
from xml.dom import Node
from xml.dom.html.HTMLElement import HTMLElement

class HTMLQuoteElement(HTMLElement):

    def __init__(self, ownerDocument, nodeName):
        HTMLElement.__init__(self, ownerDocument, nodeName)

    ### Attribute Methods ###

    def _get_cite(self):
        return self.getAttribute("CITE")

    def _set_cite(self, value):
        self.setAttribute("CITE", value)

    ### Attribute Access Mappings ###

    _readComputedAttrs = HTMLElement._readComputedAttrs.copy()
    _readComputedAttrs.update({
        "cite" : _get_cite
        })

    _writeComputedAttrs = HTMLElement._writeComputedAttrs.copy()
    _writeComputedAttrs.update({
        "cite" : _set_cite
        })

    _readOnlyAttrs = filter(lambda k,m=_writeComputedAttrs: not m.has_key(k),
                     HTMLElement._readOnlyAttrs + _readComputedAttrs.keys())
