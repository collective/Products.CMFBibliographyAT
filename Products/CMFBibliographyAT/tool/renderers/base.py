##############################################################################
#                                                                            #
#               copyright (c) 2003 ITB, Humboldt-University Berlin           #
#               written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                            #
##############################################################################

"""BibliographyRenderer main class"""

# Zope stuff
from zope.interface import implements
from Interface import Interface
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
import Products

# PLONE things
from Products.CMFCore.utils import getToolByName
from Products.CMFBibliographyAT.encodings import _python_encodings
from Products.CMFBibliographyAT.utils import _decode, _encode
from Products.CMFBibliographyAT.interface import \
     IBibliographyRenderer as z3IBibliographyRenderer
from Products.CMFBibliographyAT.interface import IBibliographyRendererFolder

class IBibliographyRenderer(Interface):
    """Interface for the output/export
    renderers of the bibliography tool.
    """
    def Description():
        """a short text that explains the target format of the renderer
        """

    def isAvailable():
        """are all pre-requisites for this renderer fullfilled?
        """

    def isEnabled():
        """is the renderer enabled by the portal manager (default: yes)?
        """

    def initializeDefaultOutputEncoding():
        """initialize the default output encoding of text format based export
        files
        the default is taken from your portal's default_charset property.
        """

    def getDefaultOutputEncoding():
        """returns the default output encoding of text format based export
        files
        """

    def getFormatName():
        """returns the name of the format
        """

    def getFormatExtension():
        """returns the filename extension of the format
        """

    def render(objects):
        """returns the rendered object(s)
        object may be a bibliography folder, a single, or a list of
        bibliography entries
        """

class BibliographyRenderer(SimpleItem, PropertyManager):
    """Base class for the output renderer of the bibliography tool.
    """
    __implements__ = (IBibliographyRenderer ,)
    implements(z3IBibliographyRenderer)

    meta_type = 'Bibliography Renderer'
    renderer_enabled = True

    default_output_encoding = ''

    format = {'name':'name of the format',
              'extension':'typical filename extension'
              }
    manage_options = (
        PropertyManager.manage_options +
        SimpleItem.manage_options
    )
    _properties = PropertyManager._properties + (
        {'id': 'renderer_enabled',
         'type': 'boolean',
         'mode': 'w',
         },
        {'id': 'default_output_encoding',
         'type': 'selection',
         'select_variable': 'getAvailableEncodings',
         'mode': 'w',
        }
    )

    security = ClassSecurityInfo()

    def __init__(self, id, title='', format=None):
        """minimal initialization
        """
        self.id = id
        self.title = title
        self.format = format

    def initializeDefaultOutputEncoding(self, portal_instance=None):
        """initialize default output encoding
        """
        if portal_instance:
            p_tool = getToolByName(portal_instance, 'plone_utils')
            self.default_output_encoding = p_tool.getSiteEncoding()

    def Description(self):
        """a short text that explains the target format of the renderer
        """
        domain='cmfbibliographyat'
        msgid='help_renderer_%s' % self.getId()
        return self.translate(domain=domain, msgid=msgid, default='%s' % self.__doc__)

    def isAvailable(self):
        """by default renderer is available, override in specific renderer's
        code if there are some hurdles to take before rendering is possible
        """
        return True

    def isEnabled(self):
        """if renderer is enabled or not can be configured in the PropertyManager
        """
        return self.renderer_enabled

    def getDefaultOutputEncoding(self):
        """returns the default output encoding of text format based export files
        """
        return self.default_output_encoding or None

    def _convertToOutputEncoding(self, export_text, output_encoding=None):
        """convert the renderer's result to the output encoding
        """
        p_tool = getToolByName(self, 'plone_utils')
        portal_encoding = p_tool.getSiteEncoding()
        if output_encoding:
            if portal_encoding:
                return _encode(_decode(export_text, portal_encoding), output_encoding)
            return _encode(_decode(export_text), output_encoding)
        default = self.getDefaultOutputEncoding()
        if portal_encoding:
            return _encode(_decode(export_text, portal_encoding), default)
        return _encode(_decode(export_text), default)

    def getAvailableEncodings(self):
        """return a list of available encodings, this list is directly taken from python
        """
        return _python_encodings

    def getFormatName(self):
        """returns the name of the format """
        return self.format.get('name', 'No name specified')

    def getFormatExtension(self):
        """returns the filename extension of the format """
        return self.format.get('extension', 'no extension specified')

    def render(self, objects, output_encoding=None, **kwargs):
        """renders objects
        objects may be a bibliography folder, a single, or a list of
        bibliography items
        """
        pass   #  needs to be provided by the individual renderer

InitializeClass(BibliographyRenderer)


class RendererFolder(Folder):
    """A folder that only offers to add objects that implement the
    IBibliographyRenderer interface.
    """
    implements(IBibliographyRendererFolder)
    meta_type = 'Renderer Folder'

    id = 'Renderers'
    title = "BibliographyTool's renderer folder"

    # we don't want 'View'
    manage_options = ( Folder.manage_options[0], ) \
                     + Folder.manage_options[2:]
    index_html = None

    def __init__(self, id, title=''):
        """minimal initialization
        """
        self.id = id
        # self.title = title

    def all_meta_types(self):
        product_infos = Products.meta_types
        possibles = []
        for p in product_infos:
            try:
                if IBibliographyRenderer in p.get('interfaces', []):
                    possibles.append(p)
            except TypeError:
                pass
        definites = map(lambda x: x.meta_type, self.objectValues())
        return filter(lambda x,y=definites: x['name'] not in y, possibles)

InitializeClass(RendererFolder)

