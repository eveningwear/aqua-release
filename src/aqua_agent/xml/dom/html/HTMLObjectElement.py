########################################################################
#
# File Name:            HTMLObjectElement
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

class HTMLObjectElement(HTMLElement):

    def __init__(self, ownerDocument, nodeName="OBJECT"):
        HTMLElement.__init__(self, ownerDocument, nodeName)

    ### Attribute Methods ###

    def _get_align(self):
        return string.capitalize(self.getAttribute("ALIGN"))

    def _set_align(self, value):
        self.setAttribute("ALIGN", value)

    def _get_archive(self):
        return self.getAttribute("ARCHIVE")

    def _set_archive(self, value):
        self.setAttribute("ARCHIVE", value)

    def _get_border(self):
        return self.getAttribute("BORDER")

    def _set_border(self, value):
        self.setAttribute("BORDER", value)

    def _get_code(self):
        return self.getAttribute("CODE")

    def _set_code(self, value):
        self.setAttribute("CODE", value)

    def _get_codeBase(self):
        return self.getAttribute("CODEBASE")

    def _set_codeBase(self, value):
        self.setAttribute("CODEBASE", value)

    def _get_codeType(self):
        return self.getAttribute("CODETYPE")

    def _set_codeType(self, value):
        self.setAttribute("CODETYPE", value)

    def _get_contentDocument(self):
        return "None"

    def _get_data(self):
        return self.getAttribute("DATA")

    def _set_data(self, value):
        self.setAttribute("DATA", value)

    def _get_declare(self):
        return self.hasAttribute("DECLARE")

    def _set_declare(self, value):
        if value:
            self.setAttribute("DECLARE", "DECLARE")
        else:
            self.removeAttribute("DECLARE")

    def _get_form(self):
        parent = self.parentNode
        while parent:
            if parent.nodeName == "FORM":
                return parent
            parent = parent.parentNode
        return None

    def _get_height(self):
        return self.getAttribute("HEIGHT")

    def _set_height(self, value):
        self.setAttribute("HEIGHT", value)

    def _get_hspace(self):
        return self.getAttribute("HSPACE")

    def _set_hspace(self, value):
        self.setAttribute("HSPACE", value)

    def _get_name(self):
        return self.getAttribute("NAME")

    def _set_name(self, value):
        self.setAttribute("NAME", value)

    def _get_standby(self):
        return self.getAttribute("STANDBY")

    def _set_standby(self, value):
        self.setAttribute("STANDBY", value)

    def _get_tabIndex(self):
        value = self.getAttribute("TABINDEX")
        if value:
            return int(value)
        return 0

    def _set_tabIndex(self, value):
        self.setAttribute("TABINDEX", str(value))

    def _get_type(self):
        return self.getAttribute("TYPE")

    def _set_type(self, value):
        self.setAttribute("TYPE", value)

    def _get_useMap(self):
        return self.getAttribute("USEMAP")

    def _set_useMap(self, value):
        self.setAttribute("USEMAP", value)

    def _get_vspace(self):
        return self.getAttribute("VSPACE")

    def _set_vspace(self, value):
        self.setAttribute("VSPACE", value)

    def _get_width(self):
        return self.getAttribute("WIDTH")

    def _set_width(self, value):
        self.setAttribute("WIDTH", value)

    ### Attribute Access Mappings ###

    _readComputedAttrs = HTMLElement._readComputedAttrs.copy()
    _readComputedAttrs.update({
        "align" : _get_align,
        "archive" : _get_archive,
        "border" : _get_border,
        "code" : _get_code,
        "codeBase" : _get_codeBase,
        "codeType" : _get_codeType,
        "contentDocument" : _get_contentDocument,
        "data" : _get_data,
        "declare" : _get_declare,
        "form" : _get_form,
        "height" : _get_height,
        "hspace" : _get_hspace,
        "name" : _get_name,
        "standby" : _get_standby,
        "tabIndex" : _get_tabIndex,
        "type" : _get_type,
        "useMap" : _get_useMap,
        "vspace" : _get_vspace,
        "width" : _get_width
        })

    _writeComputedAttrs = HTMLElement._writeComputedAttrs.copy()
    _writeComputedAttrs.update({
        "align" : _set_align,
        "archive" : _set_archive,
        "border" : _set_border,
        "code" : _set_code,
        "codeBase" : _set_codeBase,
        "codeType" : _set_codeType,
        "data" : _set_data,
        "declare" : _set_declare,
        "height" : _set_height,
        "hspace" : _set_hspace,
        "name" : _set_name,
        "standby" : _set_standby,
        "tabIndex" : _set_tabIndex,
        "type" : _set_type,
        "useMap" : _set_useMap,
        "vspace" : _set_vspace,
        "width" : _set_width
        })

    _readOnlyAttrs = filter(lambda k,m=_writeComputedAttrs: not m.has_key(k),
                     HTMLElement._readOnlyAttrs + _readComputedAttrs.keys())
