from xhpy.pylib import *


class :footer(:xhpy:html-element):
    category %flow
    children (pcdata | %flow)*
    def __init__(self, attributes={}, children=[]):
        super(:xhpy:html-element, self).__init__(attributes, children)
        self.tagName = 'footer'
