"""BibliographyIdCooker main class"""

import re

# Zope stuff
from zope.interface import implements
from zope.interface import Interface
from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
import Products

# PLONE things
from plone.i18n.normalizer import filenamenormalizer
from Products.CMFCore.utils import getToolByName
from Products.CMFBibliographyAT.interface import \
     IBibliographyIdCooker as z3IBibliographyIdCooker
from Products.CMFBibliographyAT.interface import IBibliographyIdCookerFolder

from bibliograph.core.utils import _encode, _decode

class IBibliographyIdCooker(Interface):
    """
    Interface for the bibliography ID cookers
    in the bibliography tool.
    """
    def getId():
        """
        returns the id of the reference id cooker
        """

    def Title():
        """
        returns the title of the reference id cooker
        """

    def Description():
        """
        a short text that explains the basic functionality of the id cooker
        """

    def isEnabled():
        """
        is the renderer enabled by the portal manager (default: yes)?
        """

    def getCookedBibRefId():
        """
        returns a cooked id for a bibliography reference dictionary or object
        """

class BibliographyIdCooker(SimpleItem, PropertyManager):
    """
    Base class for the id cookers of the bibliography tool.
    """

    implements(z3IBibliographyIdCooker)

    meta_type = 'Bibliography IdCooker'
    idcooker_enabled = True

    manage_options = (
        PropertyManager.manage_options +
        SimpleItem.manage_options
    )
    _properties = PropertyManager._properties + (
        {'id': 'idcooker_enabled',
         'type': 'boolean',
         'mode': 'w',
         },
    )

    security = ClassSecurityInfo()

    def __init__(self, id, title=''):
        """
        minimal initialization
        """
        self.id = id
        self.title = title

    def getId(self):
        """ returns the id of the id cooker """
        return self.id

    def Title(self):
        """ returns the title of the id cooker """
        domain='cmfbibliographyat'
        msgid='title_idcooker_%s' % self.getId().lower()
        return self.translate(domain=domain, msgid=msgid, default='%s' % self.title)

    def Description(self):
        """
        a short text that explains the basic functionality of the id cooker
        """
        domain='cmfbibliographyat'
        msgid='help_idcooker_%s' % self.getId()
        return self.translate(domain=domain, msgid=msgid, default='%s' % self.__doc__)

    def isEnabled(self):
        """ if the id cooker is enabled or not can be configured in the PropertyManager
        """
        return self.idcooker_enabled

    def _cleanId(self, text):
        """remove all charcaters not allowed in Zope ids"""
        putils = getToolByName(self, 'plone_utils')
        text = filenamenormalizer.normalize(text)
        return text

    def _object2ref(self, ref):
        """ If the passed on argument 'ref' is a BibRef Item (object), translate the import fields (authors, publication_year, title)
            to a ref dictionary (as in the parsers' code).
        """
        if type(ref) != type({}):
            obj = ref
            bib_tool = getToolByName(self, 'portal_bibliography')
            ref = bib_tool.getEntryDict(obj)
            ref['UID'] = obj.UID()

        return ref

    def _refHasAuthorNames(self, ref):

        return ref.has_key('authors') and (len([ author['lastname'] for author in ref['authors'] if author.get('lastname', None) ]) >= 1)

    def _cookIdCore(self, ref, new_id='', **kwargs):
        """ the core id cooking method that is overridden in the individual id cookers
        """
        return new_id   # needs to be provided by the individual id cookers

    def getCookedBibRefId(self, ref, use_pid_on_import=True, **kwargs):
        """
        cook id for ref dict or object, ref dict / object may be a single reference only
        """
        isReferenceObject = (type(ref) != type({}))
        if isReferenceObject:
            ref = self._object2ref(ref)
        new_id = 'nobody1000'
        if use_pid_on_import and ref.get('pid'):
            new_id = ref['pid']
        else:
            new_id = self._cookIdCore(ref, new_id=new_id)

        return _encode(_decode(self._cleanId(new_id)))


InitializeClass(BibliographyIdCooker)


class IdCookerFolder(Folder):
    """
    A folder that only offers to add objects that implement the
    IBibliographyIdCooker interface.
    """
    implements(IBibliographyIdCookerFolder)
    meta_type = 'IdCooker Folder'

    id = 'IdCookers'
    title = "BibliographyTool's id cooker folder"

    # we don't want 'View'
    manage_options = ( Folder.manage_options[0], ) \
                     + Folder.manage_options[2:]
    index_html = None

    def __init__(self, id, title=''):
        """
        minimal initialization
        """
        self.id = id
        # self.title = title

    def all_meta_types(self):
        product_infos = Products.meta_types
        possibles = []
        for p in product_infos:
            try:
                if IBibliographyIdCooker in p.get('interfaces', []):
                    possibles.append(p)
            except TypeError:
                pass
        definites = map(lambda x: x.meta_type, self.objectValues())
        return filter(lambda x,y=definites: x['name'] not in y, possibles)

InitializeClass(IdCookerFolder)

