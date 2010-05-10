##########################################################################
#                                                                        #
#           copyright (c) 2005-2007 ITB, Humboldt-University Berlin      #
#           written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                        #
##########################################################################


form zope.interface import implements

from Products.CMFCore.utils import getToolByName
from Products.PortalTransforms.interfaces import itransform


class HTMLToBibaware:
    """Transform enables inline citations and bibitems embedded in text"""
    implements(itransform)
    __name__ = "html_to_bibaware"
    inputs = ('text/html',)
    output = "text/x-html-bibaware"

    def __init__(self, name=None):
        if name:
            self.__name__ = name

    def name(self):
        return self.__name__

    def convert(self, data, idata, filename=None, **kwargs):
        """convert the data, store the result in idata and return that
        optional argument filename may give the original file name of
        received data
        additional arguments given to engine's convert, convertTo or
        __call__ are
        passed back to the transform

        The object on which the translation was invoked is available as context
        (default: None)
        """
        context = kwargs.get('context', None)
        if context is not None:
            bib_tool = getToolByName(context, 'portal_bibliography')

        if context and bib_tool:
            idata.setData(bib_tool.link_citations(data))
        else: # no context, so do nothing
            idata.setData(data)
        return idata


def register():
    return HTMLToBibaware()

def initialize():
    engine = getToolByName(portal, 'portal_transforms', None)
    if engine is not None:
        engine.registerTransform(register())
