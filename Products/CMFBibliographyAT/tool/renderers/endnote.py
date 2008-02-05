############################################################################
#                                                                          #
#             copyright (c) 2004, 2006 ITB, Humboldt-University Berlin     #
#             written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                          #
############################################################################

"""EndRenderer (EndNotes) class"""

# Zope stuff
from Globals import InitializeClass
from App.Dialogs import MessageDialog

# Bibliography stuff
from Products.CMFCore.utils import getToolByName
from Products.CMFBibliographyAT.tool.renderers.base \
     import IBibliographyRenderer, BibliographyRenderer

from Products.CMFBibliographyAT.utils import _default_encoding

class EndRenderer(BibliographyRenderer):
    """
    A specific EndNote renderer that exports bibliographical references
    in the EndNote text format.
    """
    # depends on the BibTeX renderer

    __implements__ = (IBibliographyRenderer ,)

    meta_type = "EndNote Renderer"

    format = {'name':'EndNote',
              'extension':'end'}

    def __init__(self,
                 id = 'endnote',
                 title = "transforms bibtex renderer output"):
        """
        initializes id and title
        """
        self.id = id
        self.title = title

    def isAvailable(self):
        """ test if transforming, from 'BibTex' to 'Endnote' is possible...
        """
        bib_tool = getToolByName(self, 'portal_bibliography')
        bibtex_renderer = bib_tool.Renderers.bibtex
        return bib_tool.isTransformable('bib', 'end') and \
               bibtex_renderer.isAvailable()

    def render(self, objects, output_encoding=None, msdos_eol_style=False, **kwargs):
        """
        renders a bibliography object in EndNote's text format
        """
        if not isinstance(objects, (list, tuple)):
            objects = [objects]
        bib_tool = getToolByName(objects[0], 'portal_bibliography')
        source = bib_tool.render(objects, 'bib', output_encoding=_default_encoding, msdos_eol_style=msdos_eol_style)
        return self._convertToOutputEncoding(\
            bib_tool.transform(source, 'bib', 'end'),
            output_encoding=output_encoding)

InitializeClass(EndRenderer)


def manage_addEndRenderer(self, REQUEST=None):
    """ """
    try:
        self._setObject('endnote', EndRenderer())
    except:
        return MessageDialog(
            title='Bibliography tool warning message',
            message='The renderer you attempted to add already exists.',
            action='manage_main')
    return self.manage_main(self, REQUEST)
