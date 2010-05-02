

from zope.component import adapts

from Products.GenericSetup.interfaces import ISetupEnviron
from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects
from Products.GenericSetup.utils import ObjectManagerHelpers
from Products.GenericSetup.utils import PropertyManagerHelpers
from Products.GenericSetup.utils import XMLAdapterBase
from Products.GenericSetup.utils import NodeAdapterBase

from Products.CMFCore.utils import getToolByName

from Products.CMFBibliographyAT.interface import IBibliographyTool
from Products.CMFBibliographyAT.interface import IBibliographyToolFolder
from Products.CMFBibliographyAT.interface import IBibliographyToolComponent


class BibliographyToolComponentNodeAdapter(NodeAdapterBase,
                                           PropertyManagerHelpers):

    """Node im- and exporter for Bibliographic tool components
       (like parsers, renderers).
    """

    adapts(IBibliographyToolComponent, ISetupEnviron)

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        purge = self.environ.shouldPurge()
        if node.getAttribute('purge'):
            purge = self._convertToBoolean(node.getAttribute('purge'))
        if purge:
            self._purgeProperties()

        self._initProperties(node)

    node = property(_exportNode, _importNode)
        

class BibliographyToolFolderNodeAdapter(NodeAdapterBase,
                                        ObjectManagerHelpers,
                                        PropertyManagerHelpers):

    """Node im- and exporter for the Bibliographic tool folders.
    """

    adapts(IBibliographyToolFolder, ISetupEnviron)

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())
        node.appendChild(self._extractObjects())
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        purge = self.environ.shouldPurge()
        if node.getAttribute('purge'):
            purge = self._convertToBoolean(node.getAttribute('purge'))
        if purge:
            self._purgeProperties()
            self._purgeObjects()

        self._initProperties(node)
        self._initObjects(node)

    node = property(_exportNode, _importNode)
        

class BibliographyToolXMLAdapter(XMLAdapterBase, ObjectManagerHelpers,
                                 PropertyManagerHelpers):

    """XML im- and exporter for the BibliographyTool.
    """

    adapts(IBibliographyTool, ISetupEnviron)

    _LOGGER_ID = 'bibliography'

    name = 'bibliography'

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())
        node.appendChild(self._extractObjects())

        self._logger.info('Bibliography tool exported.')
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeProperties()
            self._purgeObjects()

        self._initProperties(node)
        self._initObjects(node)

        self._logger.info('Bibliography tool imported.')



def importBibliographyTool(context):
    """Import bibliography tool and contained parser, renderer and id-cooker
    definitions from XML files.
    """
    # Only run step if a flag file is present
    if context.readDataFile('cmfbib-tool.txt') is None:
        return

    site = context.getSite()
    tool = getToolByName(site, "portal_bibliography", None)
    if tool is not None:
        importObjects(tool, '', context)

def exportBibliographyTool(context):
    """Export bibliography tool and contained parser, renderer and id-cooker
    definitions from XML files.
    """
    site = context.getSite()
    tool = getToolByName(site, "portal_bibliography")
    if tool is None:
        logger = context.getLogger('bibliography')
        logger.info('Nothing to export.')
        return
    exportObjects(tool, '', context)
