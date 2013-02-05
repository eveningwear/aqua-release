########################################################################
#
# File Name:            HTMLLinkElement
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

class HTMLLinkElement(HTMLElement):

    def __init__(self, ownerDocument, nodeName="LINK"):
        HTMLElement.__init__(self, ownerDocument, nodeName)

    ### Attribute Methods ###

    def _get_disabled(self):
        return self.hasAttribute("DISABLED")

    def _set_disabled(self, value):
        if value:
            self.setAttribute("DISABLED", "DISABLED")
        else:
            self.removeAttribute("DISABLED")

    def _get_charset(self):
        return self.getAttribute("CHARSET")

    def _set_charset(self, value):
        self.setAttribute("CHARSET", value)

    def _get_href(self):
        return self.getAttribute("HREF")

    def _set_href(self, value):
        self.setAttribute("HREF", value)

    def _get_hreflang(self):
        return self.getAttribute("HREFLANG")

    def _set_hreflang(self, value):
        self.setAttribute("HREFLANG", value)

    def _get_media(self):
        return self.getAttribute("MEDIA")

    def _set_media(self, value):
        self.setAttribute("MEDIA", value)

    def _get_rel(self):
        return self.getAttribute("REL")

    def _set_rel(self, value):
        self.setAttribute("REL", value)

    def _get_rev(self):
        return self.getAttribute("REV")

    def _set_rev(self, value):
        self.setAttribute("REV", value)

    def _get_target(self):
        return self.getAttribute("TARGET")

    def _set_target(self, value):
        self.setAttribute("TARGET", value)

    def _get_type(self):
        return self.getAttribute("TYPE")

    def _set_type(self, value):
        self.setAttribute("TYPE", value)

    ### Attribute Access Mappings ###

    _readComputedAttrs = HTMLElement._readComputedAttrs.copy()
    _readComputedAttrs.update({
        "disabled" : _get_disabled,
        "charset" : _get_charset,
        "href" : _get_href,
        "hreflang" : _get_hreflang,
        "media" : _get_media,
        "rel" : _get_rel,
        "rev" : _get_rev,
        "target" : _get_target,
        "type" : _get_type
        })

    _writeComputedAttrs = HTMLElement._writeComputedAttrs.copy()
    _writeComputedAttrs.update({
        "disabled" : _set_disabled,
        "charset" : _set_charset,
        "href" : _set_href,
        "hreflang" : _set_hreflang,
        "media" : _set_media,
        "rel" : _set_rel,
        "rev" : _set_rev,
        "target" : _set_target,
        "type" : _set_type
        })

    _readOnlyAttrs = filter(lambda k,m=_writeComputedAttrs: not m.has_key(k),
                     HTMLElement._readOnlyAttrs + _readComputedAttrs.keys())
