############################################################################
#                                                                          #
#             copyright (c) 2004 ITB, Humboldt-University Berlin           #
#             written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                          #
############################################################################

"""RISRenderer (Research Information Systems/Reference Manager) class"""

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

class RISRenderer(BibliographyRenderer):
    """
    A specific renderer that exports bibliographical references in RIS (Research Information Systems/Reference Manager) format.
    """
    # depends on the BibTeX renderer

    __implements__ = (IBibliographyRenderer ,)

    meta_type = "RIS Renderer"

    format = {'name':'RIS',
              'extension':'ris'}

    def __init__(self,
                 id = 'ris',
                 title = "transforms bibtex renderer output"):
        """
        initializes id and title
        """
        self.id = id
        self.title = title

    def isAvailable(self):
        """ test if it is possible to transforming from BibTex to RIS
        format is possible...
        """
        bib_tool = getToolByName(self, 'portal_bibliography')
        return bib_tool.isTransformable('bib', 'ris')

    def render(self, objects, output_encoding=None, msdos_eol_style=False, **kwargs):
        """
        renders a bibliography object in RIS format
        (Research Information Systems/Reference Manager)
        """
        if not isinstance(objects, (list, tuple)):
            objects = [objects]
        bib_tool = getToolByName(objects[0], 'portal_bibliography')
        bibtex_source = bib_tool.render(objects, 'bib', output_encoding=_default_encoding, msdos_eol_style=msdos_eol_style)

        # open a pipe
        (fi, fo, fe) = os.popen3('bib2xml | xml2ris', 't')
        # provide the input
        fi.write(bibtex_source)
        fi.close()
        # get the output
        ris = fo.read()
        fo.close()
        # get the staus/error message
        # (this isn't used but we don't want it in the output)
        error = fe.read()
        fe.close()
        # done
        return self._convertToOutputEncoding(\
            ris, output_encoding=output_encoding)

InitializeClass(RISRenderer)


def manage_addRISRenderer(self, REQUEST=None):
    """ """
    try:
        self._setObject('ris', RISRenderer())
    except:
        return MessageDialog(
            title='Bibliography tool warning message',
            message='The renderer you attempted to add already exists.',
            action='manage_main')
    return self.manage_main(self, REQUEST)
