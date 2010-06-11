##########################################################################
#                                                                        #
#           copyright (c) 2005 ITB, Humboldt-University Berlin           #
#           written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                        #
##########################################################################

from zope.interface import implements
from Products.PortalTransforms.interfaces import itransform

class BibawareToHTML:
    """Transforms the mime-type back to text/html"""
    implements(itransform)
    __name__ = "bibaware_to_html"
    inputs = ('text/x-html-bibaware',)
    output = "text/html"

    def __init__(self, name=None):
        if name:
            self.__name__ = name

    def name(self):
        return self.__name__

    def convert(self, data, idata, filename=None, **kwargs):
        """
        simple identity to transform the mimetype only
        """
        idata.setData(data)
        return idata

def register():
    return BibawareToHTML()

def initialize():
    engine = getToolByName(portal, 'portal_transforms', None)
    if engine is not None:
        engine.registerTransform(register())
