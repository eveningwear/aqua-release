########################################################################
#
# File Name:            HTMLScriptElement
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

class HTMLScriptElement(HTMLElement):

    def __init__(self, ownerDocument, nodeName="SCRIPT"):
        HTMLElement.__init__(self, ownerDocument, nodeName)

    ### Attribute Methods ###

    def _get_charset(self):
        return self.getAttribute("CHARSET")

    def _set_charset(self, value):
        self.setAttribute("CHARSET", value)

    def _get_defer(self):
        return self.hasAttribute("DEFER")

    def _set_defer(self, value):
        if value:
            self.setAttribute("DEFER", "DEFER")
        else:
            self.removeAttribute("DEFER")

    def _get_event(self):
        return self.getAttribute("EVENT")

    def _set_event(self, value):
        self.setAttribute("EVENT", value)

    def _get_htmlFor(self):
        return self.getAttribute("FOR")

    def _set_htmlFor(self, value):
        self.setAttribute("FOR", value)

    def _get_src(self):
        return self.getAttribute("SRC")

    def _set_src(self, value):
        self.setAttribute("SRC", value)

    def _get_text(self):
        if not self.firstChild:
            return
        if self.firstChild == self.lastChild:
            return self.firstChild.data
        self.normalize()
        text = filter(lambda x: x.nodeType == Node.TEXT_NODE, self.childNodes)
        return text[0].data

    def _set_text(self, value):
        text = None
        for node in self.childNodes:
            if not text and node.nodeType == Node.TEXT_NODE:
                text = node
            else:
                self.removeChild(node)
        if text:
            text.data = value
        else:
            text = self.ownerDocument.createTextNode(value)
            self.appendChild(text)

    def _get_type(self):
        return self.getAttribute("TYPE")

    def _set_type(self, value):
        self.setAttribute("TYPE", value)

    ### Attribute Access Mappings ###

    _readComputedAttrs = HTMLElement._readComputedAttrs.copy()
    _readComputedAttrs.update({
        "charset" : _get_charset,
        "defer" : _get_defer,
        "event" : _get_event,
        "htmlFor" : _get_htmlFor,
        "src" : _get_src,
        "text" : _get_text,
        "type" : _get_type
        })

    _writeComputedAttrs = HTMLElement._writeComputedAttrs.copy()
    _writeComputedAttrs.update({
        "charset" : _set_charset,
        "defer" : _set_defer,
        "event" : _set_event,
        "htmlFor" : _set_htmlFor,
        "src" : _set_src,
        "text" : _set_text,
        "type" : _set_type
        })

    _readOnlyAttrs = filter(lambda k,m=_writeComputedAttrs: not m.has_key(k),
                     HTMLElement._readOnlyAttrs + _readComputedAttrs.keys())
