########################################################################
#
# File Name:            HTMLLegendElement
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

class HTMLLegendElement(HTMLElement):

    def __init__(self, ownerDocument, nodeName="LEGEND"):
        HTMLElement.__init__(self, ownerDocument, nodeName)

    ### Attribute Methods ###

    def _get_accessKey(self):
        return self.getAttribute("ACCESSKEY")

    def _set_accessKey(self, value):
        self.setAttribute("ACCESSKEY", value)

    def _get_align(self):
        return string.capitalize(self.getAttribute("ALIGN"))

    def _set_align(self, value):
        self.setAttribute("ALIGN", value)

    def _get_form(self):
        parent = self.parentNode
        while parent:
            if parent.nodeName == "FORM":
                return parent
            parent = parent.parentNode
        return None

    ### Attribute Access Mappings ###

    _readComputedAttrs = HTMLElement._readComputedAttrs.copy()
    _readComputedAttrs.update({
        "accessKey" : _get_accessKey,
        "align" : _get_align,
        "form" : _get_form
        })

    _writeComputedAttrs = HTMLElement._writeComputedAttrs.copy()
    _writeComputedAttrs.update({
        "accessKey" : _set_accessKey,
        "align" : _set_align
        })

    _readOnlyAttrs = filter(lambda k,m=_writeComputedAttrs: not m.has_key(k),
                     HTMLElement._readOnlyAttrs + _readComputedAttrs.keys())
