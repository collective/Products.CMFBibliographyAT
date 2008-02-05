############################################################################
#                                                                          #
#             copyright (c) 2004 ITB, Humboldt-University Berlin           #
#             written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                          #
############################################################################

"""XMLRenderer (MODS) class"""

# Python stuff
import os

# Zope stuff
from Globals import InitializeClass
from App.Dialogs import MessageDialog

# Bibliography stuff
from Products.CMFCore.utils import getToolByName
from Products.CMFBibliographyAT.tool.renderers.base \
     import IBibliographyRenderer, BibliographyRenderer

from Products.CMFBibliographyAT.utils import _default_encoding

class XMLRenderer(BibliographyRenderer):
    """
    A specific XML (MODS) intermediate renderer. The XML intermediate format is conform to
    the Library of Congress's Metadata Object Description Schema (MODS). This is a very flexible standard
    that should prove quite useful as the number of tools that directly interact with it increase.
    """
    # depends on the BibTeX renderer

    __implements__ = (IBibliographyRenderer ,)

    meta_type = "XML Renderer"

    format = {'name':'XML (MODS)',
              'extension':'xml'}

    def __init__(self,
                 id = 'xml_mods',
                 title = "XML (MODS) - transforms " \
                 "bibtex renderer output"):
        """
        initializes id and title
        """
        self.id = id
        self.title = title

    def isAvailable(self):
        """ test if transforming from BibTex to XML is possible...
        """
        bib_tool = getToolByName(self, 'portal_bibliography')
        return bib_tool.isTransformable('bib', 'xml')

    def render(self, objects, output_encoding=None, msdos_eol_style=False, **kwargs):
        """
        renders a bibliography object in XML (MODS) format
        """
        if not isinstance(objects, (list, tuple)):
            objects = [objects]
        bib_tool = getToolByName(objects[0], 'portal_bibliography')
        bibtex_source = bib_tool.render(objects, 'bib', output_encoding=_default_encoding, msdos_eol_style=msdos_eol_style)

        # open a pipe
        (fi, fo, fe) = os.popen3('bib2xml ', 't')
        # provide the input
        fi.write(bibtex_source)
        fi.close()
        # get the output
        xml = fo.read()
        fo.close()
        # get the staus/error message
        # (this isn't used but we don't want it in the output)
        error = fe.read()
        fe.close()
        # done
        return self._convertToOutputEncoding(xml, output_encoding=output_encoding)

InitializeClass(XMLRenderer)


def manage_addXMLRenderer(self, REQUEST=None):
    """ """
    try:
        self._setObject('xml_mods', XMLRenderer())
    except:
        return MessageDialog(
            title='Bibliography tool warning message',
            message='The renderer you attempted to add already exists.',
            action='manage_main')
    return self.manage_main(self, REQUEST)
