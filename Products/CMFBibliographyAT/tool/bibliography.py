##########################################################################
#                                                                        #
#           copyright (c) 2003, 2005 ITB, Humboldt-University Berlin     #
#           written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                        #
##########################################################################

"""BibliographyTool main class"""
# Python stuff
import re
import string
import codecs
import logging

# Zope stuff
from zope.interface import implements
from zope import component
from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo, ModuleSecurityInfo
from OFS.Folder import Folder
from persistent.mapping import PersistentMapping

try:
    import transaction
except ImportError:
    from Products.Archetypes import transaction

# CMF stuff
from Products.CMFCore.permissions import View, ManagePortal
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.atapi import DisplayList

# My stuff ;-)
from Products.CMFBibliographyAT.interface import IBibliographyTool
from Products.CMFBibliographyAT.tool.idcookers.base import IdCookerFolder
from Products.CMFBibliographyAT.DuplicatesCriteria import \
     DuplicatesCriteriaManager
from Products.CMFBibliographyAT.config import REFERENCE_TYPES
from Products.CMFBibliographyAT.config import FOLDER_TYPES as BIBFOLDER_TYPES
from Products.CMFBibliographyAT.config import ZOPE_TEXTINDEXES
from Products.CMFBibliographyAT import permissions

from bibliograph.core.utils import _encode
from bibliograph.core.utils import _decode
from bibliograph.rendering.interfaces import IBibliographyRenderer
from bibliograph.parsing.interfaces import IBibliographyParser



# citation patterns
citations = re.compile(r'\\?cite{([\w, ]*)}')
bibitems = re.compile(r'\\?bibitem{([\w]*)}')

LOG = logging.getLogger('CMFBibliographyAT')


class ImportParseError(Exception):
    """An exception to replace the use of TypeError in
    skins/bibliography/import.py as this masked true TypeErrors and made
    debugging that much more difficult.
    """
    pass

# Need to be able to import this exception so that it can be caught TTW.
module_path = 'Products.CMFBibliographyAT.tool.bibliography'
security = ModuleSecurityInfo(module_path)
security.declarePublic('ImportParseError')

from OFS.PropertySheets import PropertySheets

class BibliographyTool(UniqueObject, Folder, ## ActionProviderBase,
                       DuplicatesCriteriaManager):

    """Tool for managing import and export functionality
       as well as some resources of the BibliographyFolders
       and -Entries.
    """

    implements(IBibliographyTool)

    __allow_access_to_unprotected_subobjects__ = 1

    id = 'portal_bibliography'
    meta_type = 'Bibliography Tool'
    show_isbn_link = 0
    allow_folder_intro = 0
    bibfolders_translatable = 1
    bibrefitems_translatable = 1
    support_member_references = False
    default_idcooker_id = 'etal'
    use_pids_on_import = True
    cook_ids_on_bibref_creation = False
    cook_ids_after_bibref_edit = False
    synchronize_pdffile_attributes = False
    enable_duplicates_manager = True
    member_types = []
    sort_members_on = ''
    select_members_attr = ''
    members_search_on_attr = ''
    infer_author_references_after_edit = True
    infer_author_references_after_import = True
    authorof_implies_owner = False
    authorof_implies_creator = False
    allow_pdfupload_portal_policy = True
    allow_pdfupload_for_types = REFERENCE_TYPES
    searchable_bibfolders = True
    preprint_servers = []
    allow_additional_fields = False
    additional_fields = ['howpublished','recommendedby']  # just an example

    security = ClassSecurityInfo()
    security.declareObjectProtected(View)

    manage_options = (
        (Folder.manage_options[0],)
        + DuplicatesCriteriaManager.manage_options
        + Folder.manage_options[2:]
        )

    _properties = Folder._properties + (
        {'id':'default_idcooker_id',
         'type':'selection',
         'select_variable':'listIdCookers',
         'mode':'w',
         },
        {'id':'cook_ids_on_bibref_creation',
         'type':'boolean',
         'mode':'w',
         },
        {'id':'cook_ids_after_bibref_edit',
         'type':'boolean',
         'mode':'w',
         },
        {'id':'use_pids_on_import',
         'type':'boolean',
         'mode':'w',
         },
        {'id':'synchronize_pdffile_attributes',
         'type':'boolean',
         'mode':'w',
         },
        {'id':'enable_duplicates_manager',
         'type':'boolean',
         'mode':'w',
         },
        {'id':'allow_folder_intro',
         'type':'boolean',
         'mode':'w',
         },
        {'id':'allow_pdfupload_portal_policy',
         'type':'boolean',
         'mode':'w',
         },
        {'id':'allow_pdfupload_for_types',
         'type':'multiple selection',
         'select_variable':'getReferenceTypes',
         'mode':'w',
         },
        {'id':'bibfolders_translatable',
         'type':'boolean',
         'mode':'w',
         },
        {'id':'bibrefitems_translatable',
         'type':'boolean',
         'mode':'w',
         },
        {'id':'support_member_references',
         'type':'boolean',
         'mode':'w',
         },
        {'id':'member_types',
         'type':'multiple selection',
         'select_variable':'getPortalTypeNames',
         'mode':'w',
         },
        {'id':'sort_members_on',
         'type':'selection',
         'select_variable':'getFieldIndexes',
         'mode':'w',
         },
        {'id':'select_members_attr',
         'type':'selection',
         'select_variable':'getMetaDataColumns',
         'mode':'w',
         },
        {'id':'members_search_on_attr',
         'type':'selection',
         'select_variable':'getTextIndexes',
         'mode':'w',
         },
        {'id':'infer_author_references_after_edit',
         'type':'boolean',
         'mode':'w',
         },
        {'id':'infer_author_references_after_import',
         'type':'boolean',
         'mode':'w',
         },
        {'id':'authorof_implies_owner',
         'type':'boolean',
         'mode':'w',
         },
        {'id':'authorof_implies_creator',
         'type':'boolean',
         'mode':'w',
         },
        {'id':'show_isbn_link',
         'type':'boolean',
         'mode':'w',
         },
        {'id':'preprint_servers',
         'type':'lines',
         'mode':'w',
         },
        {'id':'searchable_bibfolders',
         'type':'boolean',
         'mode':'w',
         },
        {'id':'allow_additional_fields',
         'type':'boolean',
         'mode':'w',
         },
        {'id':'additional_fields',
         'type':'lines',
         'mode':'w',
         },
        )
    _match_criteria = {}
    _default_criteria = ('bibliography type',)

    def __init__(self):
        self._setObject('IdCookers', IdCookerFolder('IdCookers', ''))
        DuplicatesCriteriaManager.__init__(self)
        # Add the local reference types registry
        self._reference_types = PersistentMapping()
        # Populate it initially with those types declared in config.py
        for ref_type in REFERENCE_TYPES:
            self._reference_types[ref_type] = None

    def isBibFolderTranslatable(self):
        """ return what is in bibfolders_translatable property
            this is only half of the truth!!! (ITranslatable)
        """
        return self.bibfolders_translatable

    def isBibrefItemTranslatable(self):
        """ return what is in bibrefitems_translatable property
            this is only half of the truth!!! (ITranslatable)
        """
        return self.bibrefitems_translatable

    security.declarePublic('getMemberTypes')
    def getMemberTypes(self, default=()):
        member_types = self.getProperty('member_types', default)
        if not isinstance(member_types, (list, tuple)):
            return (member_types,)
        else:
            return member_types

    security.declarePublic('getSortMembersOn')
    def getSortMembersOn(self, default='getId'):
        return self.getProperty('sort_members_on', default)

    security.declarePublic('getSelectMembersAttr')
    def getSelectMembersAttr(self, default='Title'):
        return self.getProperty('select_members_attr', default)

    security.declarePublic('getMembersSearchOnAttr')
    def getMembersSearchOnAttr(self, default='Title'):
        return self.getProperty('members_search_on_attr', default)

    security.declarePublic('getReferenceTypes')
    def getReferenceTypes(self, display=False):
        """
        returns a list with the names (meta types) of the
        currently registered reference types of a BibliographyFolder
        """
        if display:
            return DisplayList(tuple([ (key, key) for key in self.getReferenceTypes() ]))
        else:
            return self._reference_types.keys()

    security.declarePublic('getBibFolderTypes')
    def getBibFolderTypes(self):
        """
        returns a list with the names (meta types) of the
        currently registered bibfolder types
        """
        return BIBFOLDER_TYPES

    security.declareProtected(permissions.ManageReferenceTypes,
                              'registerReferenceType')
    def registerReferenceType(self, portal_type):
        """Add portal_type to the list that should be considered references
        for this plone instance.  Do not fail on duplicates.
        """
        # self._reference_types is a PersistentMapping
        self._reference_types[portal_type] = None

    security.declareProtected(permissions.ManageReferenceTypes,
                              'unregisterReferenceType')
    def unregisterReferenceType(self, portal_type):
        """Remove portal_type from the list that should be considered
        references for this plone instance.  Do not fail if the type is not
        already registered.
        """
        # self._reference_types is a PersistentMapping
        try:
            del self._reference_types[portal_type]
        except KeyError:
            pass

    security.declarePublic('getImportFormatNames')
    def getImportFormatNames(self, with_unavailables=False, with_disabled=False):
        """
        returns a list with the names of the supported import formats
        """
        parsers = component.getAllUtilitiesRegisteredFor(IBibliographyParser)
        return [parser.getFormatName() \
                for parser in parsers if (parser.isAvailable() or with_unavailables) and (parser.isEnabled() or with_disabled) ]

    security.declarePublic('getImportFormatExtensions')
    def getImportFormatExtensions(self, with_unavailables=False, with_disabled=False):
        """
        returns a list with the file name extensions
        of the supported import formats
        """
        parsers = component.getAllUtilitiesRegisteredFor(IBibliographyParser)
        return [parser.getFormatExtension() \
                for parser in parsers if (parser.isAvailable() or with_unavailables) and (self.isParserEnabled(parser.getFormatName()) or with_disabled)]

    def getImportFormatDescriptions(self, with_unavailables=False, with_disabled=False):
        """
        returns a list with the description texts
        of the supported import formats
        """
        parsers = component.getAllUtilitiesRegisteredFor(IBibliographyParser)
        return [parser.Description() \
                for parser in parsers if (parser.isAvailable() or with_unavailables) and (parser.isEnabled() or with_disabled) ]

    security.declarePublic('getExportFormatNames')
    def getExportFormatNames(self, with_unavailables=False, with_disabled=False):
        """
        returns a list with the names of the supported export formats
        """
        utils = component.getAllUtilitiesRegisteredFor(IBibliographyRenderer)
        return [ renderer.__name__ for renderer in utils
                 if (renderer.available or with_unavailables) and
                    (self.isRendererEnabled(renderer.__name__) or with_disabled) ]

    security.declarePublic('getExportFormatExtensions')
    def getExportFormatExtensions(self, with_unavailables=False, with_disabled=False):
        """
        returns a list with the file name extensions
        of the supported export formats
        """
        utils = component.getAllUtilitiesRegisteredFor(IBibliographyRenderer)
        return [ renderer.target_format for renderer in utils
                 if (renderer.available or with_unavailables) and
                    (self.isRendererEnabled(renderer.__name__) or with_disabled) ]

    def getExportFormatDescriptions(self, with_unavailables=False, with_disabled=False):
        """
        returns a list with the description texts
        of the supported export formats
        """
        utils = component.getAllUtilitiesRegisteredFor(IBibliographyRenderer)
        return [ renderer.description for renderer in utils
                 if (renderer.available or with_unavailables) and
                    (self.isRendererEnabled(renderer.__name__) or with_disabled) ]

    security.declarePublic('getExportFormats')
    def getExportFormats(self, with_unavailables=False, with_disabled=False):
        """
        returns a list of (name, extension, description) tuples
        of the supported export formats
        """
        export_formats = zip(
            self.getExportFormatNames(with_unavailables=with_unavailables,
                                      with_disabled=with_disabled),
            self.getExportFormatExtensions(with_unavailables=with_unavailables,
                                           with_disabled=with_disabled),
            self.getExportFormatDescriptions(with_unavailables=with_unavailables,
                                            with_disabled=with_disabled))
        export_formats.sort()
        return export_formats

    security.declarePublic('getImportFormats')
    def getImportFormats(self, with_unavailables=False, with_disabled=False):
        """
        returns a list of (name, extension, description) tuples
        of the supported import formats
        """
        supported_parsers = zip(self.getImportFormatNames(with_unavailables=with_unavailables, with_disabled=with_disabled),
                                self.getImportFormatExtensions(with_unavailables=with_unavailables, with_disabled=with_disabled),
                                self.getImportFormatDescriptions(with_unavailables=with_unavailables, with_disabled=with_disabled))
        supported_parsers.sort()
        return supported_parsers

    security.declareProtected(View, 'render')
    def render(self, entry, format='', output_encoding=None, **kw):
        """
        renders a BibliographyEntry object in the specified format
        """
        renderer = self.getRenderer(format=format, **kw)
        if renderer:
            return renderer.render(entry, output_encoding=output_encoding, **kw)
        else:
            return None

    security.declareProtected(View, 'isParserEnabled')
    def isParserEnabled(self, name):
        """ Check cmfbibat propertysheet """
        return self.getSheetProperty(name, 'parser_enabled')

    security.declareProtected(View, 'isRendererEnabled')
    def isRendererEnabled(self, name):
        """ Check cmfbibat propertysheet """
        return self.getSheetProperty(name, 'renderer_enabled')

    security.declareProtected(View, 'getRenderer')
    def getRenderer(self, format, with_unavailables=False, with_disabled=False, **kw):
        """
        returns the renderer for the specified format
        first looks for a renderer with the 'format' name
        next looks for a renderer with the 'format' extension
        """
        utils = component.getAllUtilitiesRegisteredFor(IBibliographyRenderer)
        for renderer in utils:
            if (renderer.available or with_unavailables) and \
               (renderer.enabled or with_disabled):
                if format.lower() == renderer.__name__.lower():
                    return renderer.__of__(self)
                if format.lower() == renderer.target_format.lower():
                    return renderer.__of__(self)
        return None


    security.declareProtected(View, 'getEntries')
    def getEntries(self, source, format, file_name=None, input_encoding='utf-8'):
        """
        main routine to be called from BibliographyFolders
        returns a list with the parsed entries
        """

        source = self.checkEncoding(source, input_encoding)
        format = self.checkFormat(source, format, file_name)
        parser = self.getParser(format)

        if parser:
            try:
                return parser.getEntries(source)
            except Exception, e:
                LOG.error('Import error while importing file (%s)' % e, exc_info=True)
                raise RuntimeError('An error occured (%s) - please check the log file for details' % e)
        else:
            return "No parser for '%s' available." % format

    security.declareProtected(View, 'getParser')
    def getParser(self, format, with_unavailables=False, with_disabled=False, **kw):
        """
        returns the parser for the specified format
        first looks for a parser with the 'format' name
        next looks for a parser with the 'format' extension
        """
        parsers = component.getAllUtilitiesRegisteredFor(IBibliographyParser)
        for parser in parsers:
            if (parser.isAvailable() or with_unavailables) and (parser.isEnabled() or with_disabled):
                if format.lower() == parser.getFormatName().lower():
                    return parser
                elif format.lower() == parser.getFormatExtension().lower():
                    return parser
        return None ## rr: we probabliy should raise an error here

    security.declareProtected(View, 'getIdCooker')
    def getIdCooker(self, idcooker_id='etal', with_disabled=False, **kwargs):
        """
        returns the id cooker object of the specified cooker_id
        """
        for idcooker in self.IdCookers.objectValues():
            if idcooker.isEnabled() or with_disabled:
                if idcooker_id == idcooker.getId():
                    return idcooker
        return None ## rr: we probabliy should raise an error here

    security.declareProtected(View, 'getDefaultIdCooker')
    def getDefaultIdCooker(self, **kwargs):
        """
        returns the site wide default id cooker (as an object)
        """
        return self.getIdCooker(idcooker_id=self.default_idcooker_id, **kwargs)

    security.declareProtected(View, 'listIdCookers')
    def listIdCookers(self, with_disabled=False):
        """
        returns a list of strings with the ids of available id cookers
        """
        idcooker_ids = [ idcooker.getId() for idcooker in self.IdCookers.objectValues() if idcooker.isEnabled() or with_disabled ]
        idcooker_ids.sort()
        return idcooker_ids

    security.declareProtected(View, 'allowPdfUploadPortalPolicy')
    def allowPdfUploadPortalPolicy(self):

        return self.allow_pdfupload_portal_policy

    security.declareProtected(View, 'allowPdfUploadForTypes')
    def allowPdfUploadForTypes(self):

        return self.allow_pdfupload_for_types

    security.declareProtected(View, 'useParserIdsOnImport')
    def useParserIdsOnImport(self):

        return self.use_pids_on_import

    security.declareProtected(View, 'cookIdsOnBibRefCreation')
    def cookIdsOnBibRefCreation(self):

        return self.cook_ids_on_bibref_creation

    security.declareProtected(View, 'cookIdsAfterBibRefEdit')
    def cookIdsAfterBibRefEdit(self):

        return self.cook_ids_after_bibref_edit

    security.declareProtected(View, 'synchronizePdfFileAttributes')
    def synchronizePdfFileAttributes(self):

        return self.synchronize_pdffile_attributes

    security.declareProtected(View, 'searchableBibFolders')
    def searchableBibFolders(self):

        return self.searchable_bibfolders

    security.declareProtected(View, 'filterOutBibEntriesFromNonSearchableBibFolders')
    def filterOutBibEntriesFromNonSearchableBibFolders(self, search_results, object_getmethod='getObject'):

        result = []
        for b in search_results:
            object = getattr(b, object_getmethod)()
            if object.getParentNode().portal_type in self.getBibFolderTypes() and object.getSearchable():
                result.append(b)
        return result


    security.declareProtected(View, 'filterOutDupesByTitle')
    def filterOutDupesByTitle(self, search_results):

        result = []
        titles_seen = []
        for b in search_results:
            title = b.Title
            if not title in titles_seen:
                result.append(b)
                titles_seen.append(b.Title)
        return result


    security.declareProtected(View, 'enableDuplicatesManager')
    def enableDuplicatesManager(self):

        return self.enable_duplicates_manager

    security.declareProtected(View, 'getEnableDuplicatesManager')
    def getEnableDuplicatesManager(self, instance=None):

        if instance and getattr(instance, 'portal_type', None) and instance.portal_type in ('BibliographyFolder', 'LargeBibliographyFolder',):
            return instance.getEnableDuplicatesManager()
        else:
            return self.enable_duplicates_manager

    security.declareProtected(View, 'inferAuthorReferencesAfterEdit')
    def inferAuthorReferencesAfterEdit(self):

        return self.infer_author_references_after_edit

    security.declareProtected(View, 'inferAuthorReferencesAfterImport')
    def inferAuthorReferencesAfterImport(self):

        return self.infer_author_references_after_import

    security.declareProtected(View, 'authorOfImpliesOwner')
    def authorOfImpliesOwner(self):

        return self.authorof_implies_owner

    security.declareProtected(View, 'authorOfImpliesCreator')
    def authorOfImpliesCreator(self):

        return self.authorof_implies_creator

    security.declareProtected(ManagePortal, 'transaction_savepoint')
    def transaction_savepoint(self, **kw):
        """ needed as a wrapper for bibliography_entry_cookId script
        """
        transaction.savepoint(**kw)

    security.declareProtected(View, 'cookReferenceId')
    def cookReferenceId(self, ref, idcooker_id='etal', **kwargs):
        """
        returns the cooked id for reference object
        """
        idcooker = self.getIdCooker(idcooker_id=idcooker_id, **kwargs)

        if idcooker:
            return idcooker.getCookedBibRefId(ref, **kwargs)

        return 'nobody1000'

    def nextId(self, testid):
        letters = string.letters
        if testid[-1] in letters:
            last = letters[letters.find(testid[-1])+1]
            return testid[:-1] + last
        else:
            # FIXME BAD
            return testid + 'a'

    def checkEncoding(self, source, input_encoding='utf-8'):
        """ Make sure we have utf-8 encoded text """

        encoding = input_encoding
        if source.startswith(codecs.BOM_UTF8):
            source = source[3:] # chop of BOM (might confuse checkFormat())
            encoding = 'utf-8'

        source = unicode(source, encoding)
        return source.encode('utf-8')

    def checkFormat(self, source, format, file_name):
        """
        plausibility test whether 'source' has the 'format' specified
        if not it tries to infer the format from the 'file_name'
        raises an error if both fail
        """

        ok = 0
        if format:
            parser = self.getParser(format)
            ok = parser.checkFormat(source)
        # TODO: This should be changed!  If the user requests a format, and it
        # doesn't match, we should report that error back to the user.  Guessing
        # results in ambiguous results.
        if not ok and file_name:
            format = self.guessFormat(file_name)
        if format:
            return format
        else:
            raise  ImportParseError, "%s Parser's 'checkFormat' and " \
                  "guessing the format from the file name '%s' failed." \
                  % (format, file_name)

    def guessFormat(self, file_name):
        """
        Checks whether the file_name extension is
        among the supported ones.

        returns the respective format name if found
        returns None otherwise
        """
        extension = file_name.split('.')[-1].lower()
        parsers = component.getAllUtilitiesRegisteredFor(IBibliographyParser)
        if extension in [ext.lower()
                         for ext in self.getImportFormatExtensions()]:
            for parser in parsers:
                if extension == parser.getFormatExtension().lower():
                    return parser.getFormatName()
        return None


    # support BibTeX style citations in text
    security.declarePublic('link_citations')
    def link_citations(self, text=""):
        """
        replace all citations with links to their references

        the pattern is 'cite{key}' or 'cite{key1,key2}
        If 'key' matches the id of a reference the pattern
        will be replaced with inline link(s) to this reference(s).
        Otherwise the pattern is replaced with the key.

        Using the pattern 'bibitem{key}' you can include the
        full reference like shown in other bibliographic listings
        (authors (year) title linked to entry, source)
        """
        text = citations.sub(self._inline_links, text)
        return bibitems.sub(self._bibitem_links, text)

    def _inline_links(self, hit):
        keys = [k.strip() for k in hit.group(1).split(',')]
        results = []
        catalog = getToolByName(self, 'portal_catalog')
        encoding = self.getProperty('default_charset') or 'utf-8'
        for key in keys:
            brains = catalog(getId = key,
                             portal_type = self.getReferenceTypes()
                             )
            if brains:
                url = brains[0].getURL()
                label = _encode(brains[0].citationLabel, encoding) \
                        or 'no label'
                link = '<a href="%s">%s</a>' % (url, label)
                results.append(link)
            else:
                results.append(key)
        return '; '.join(results)

    def _bibitem_links(self, hit):
        key = hit.group(1).strip()
        catalog = getToolByName(self, 'portal_catalog')
        brains = catalog(getId = key,
                         portal_type = self.getReferenceTypes()
                         )
        if brains:
            brain = brains[0]
            encoding = self.getProperty('default_charset') or 'utf-8'

            authors = _encode(brain.Authors, encoding)
            year = _encode(brain.publication_year, encoding)
            title = _encode(brain.Title, encoding)
            source = _encode(brain.Source, encoding)
            url = brain.getURL()

            link = '%s (%s) <a href="%s">%s</a>, %s' % \
                   (authors, year, url, title, source)
            return link
        else:
            return key

    ## XXX just to have this in trusted code
    def getSortedMemberIds(self):
        """Return the ids like the membership tool but sorted (by id)"""
        mt = getToolByName(self, 'portal_membership')
        ids = mt.listMemberIds()
        ids.sort()
        return ids

    security.declareProtected(View, 'getFieldIndexes')
    def getFieldIndexes(self, start_with_empty_element=False):
        """returns a list of all field index ids from the catalog"""
        catalog = getToolByName(self, 'portal_catalog')
        indexes = catalog.indexes()
        field_indexes = [i for i in indexes \
                         if catalog.Indexes[i].meta_type == 'FieldIndex']
        field_indexes.sort()
        if start_with_empty_element:
            return [''] + field_indexes
        else:
            return field_indexes

    security.declareProtected(View, 'getSortIndexes')
    def getSortIndexes(self, start_with_empty_element=False):
        """returns a list of all sortable index ids from the catalog"""
        catalog = getToolByName(self, 'portal_catalog')
        indexes = catalog.indexes()
        sort_indexes = [i for i in indexes \
                         if catalog.Indexes[i].meta_type in ('FieldIndex', 'DateIndex', 'DateRangeIndex', 'KeywordIndex') ]
        sort_indexes.sort()
        if start_with_empty_element:
            return [''] + sort_indexes
        else:
            return sort_indexes

    security.declareProtected(View, 'getTextIndexes')
    def getTextIndexes(self, start_with_empty_element=False):
        """returns a list of all text index like ids from the catalog"""
        catalog = getToolByName(self, 'portal_catalog')
        indexes = catalog.indexes()
        text_indexes = [ i for i in indexes \
                          if catalog.Indexes[i].meta_type in ZOPE_TEXTINDEXES ]
        text_indexes.sort()
        if start_with_empty_element:
            return [''] + text_indexes
        else:
            return text_indexes

    security.declareProtected(View, 'getMetaDataColumns')
    def getMetaDataColumns(self, start_with_empty_element=False):
        """returns a list of all field index ids from the catalog"""
        catalog = getToolByName(self, 'portal_catalog')
        columns = catalog.schema()
        if start_with_empty_element:
            return [''] + columns
        else:
            return columns

    security.declareProtected(ManagePortal, 'getBibliographyContentTypes')
    def getBibliographyContentTypes(self):
        """ return a sequence that contains all bibliography types"""
        bibContentTypes = []
        arche_tool = getToolByName(self,'archetype_tool')
        bib_tool = getToolByName(self, 'portal_bibliography')
        for reference_type in bib_tool.getReferenceTypes():
            for reg_type in arche_tool.listRegisteredTypes():
                if reference_type == reg_type['name']:
                    bibContentTypes.append(reg_type)
        return bibContentTypes

    security.declareProtected(ManagePortal, 'getBibliographyContentTypes')
    def getBibrefArchetypeName(self, classname):
        """ return the archetype name of a bibref content type class"""
        arche_tool = getToolByName(self,'archetype_tool')
        bib_tool = getToolByName(self, 'portal_bibliography')
        if classname in bib_tool.getReferenceTypes():
            for reg_type in arche_tool.listRegisteredTypes():
                if classname == reg_type['name']:
                    return reg_type['klass'].archetype_name

    security.declareProtected(View, 'usesCMFMember')
    def usesCMFMember(self):
        quickinstaller = getToolByName(self, 'portal_quickinstaller')
        return quickinstaller.isProductInstalled('CMFMember')

    # The cmfbibat_properties property sheet is used to store render and
    # parser related preferences. The 'prefix' refers to the name of
    # the renderer or parser. Parser/Renderer names are normalized
    # (compare with propertiestool.xml)

    security.declareProtected(ManagePortal, 'updateSheetProperty')
    def updateSheetProperty(self, prefix, property, value):
        """ Update cmfbibat propertysheet """
        ps = getToolByName(self, 'portal_properties').cmfbibat_properties
        prop_name = '%s_%s' % (prefix, property)
        prop_name = ''.join([c for c in prop_name if c.lower() in string.letters + '_'])
        ps.manage_changeProperties(**{prop_name:value})


    security.declareProtected(View, 'getSheetProperty')
    def getSheetProperty(self, prefix, property):
        """ return property from cmfbibat propertysheet """
        ps = getToolByName(self, 'portal_properties').cmfbibat_properties
        prop_name = '%s_%s' % (prefix, property)
        prop_name = ''.join([c for c in prop_name if c.lower() in string.letters + '_'])
        return ps.getProperty(prop_name)


    security.declarePrivate('getEntryDict')
    def getEntryDict(self, bibref_item, instance=None, title_link=False, title_link_only_if_owner=False, ):
        """ transform a BiblioRef Object into python dictionary
        """
        ref_attributes = ('publication_year',
                          'publication_month',
                          'publication_url',
                          'abstract',
                          'note',
                          'publisher',
                          'editor',
                          'editor_flag',
                          'organization',
                          'institution',
                          'school',
                          'address',
                          'booktitle',
                          'chapter',
                          'journal',
                          'volume',
                          'edition',
                          'number',
                          'pages',
                          'series',
                          'type',
                          'howpublished',
                          'preprint_server',
                          'pmid',
                          'isbn',
                          'annote',)
        values = {}
        values['UID'] = bibref_item.UID()
        tmp_title = _decode(bibref_item.Title())
        if tmp_title and (tmp_title[-1] == '.'): tmp_title = tmp_title[:-1]
        values['title'] = tmp_title
        uniauthors=[]
        for author in bibref_item.getAuthors():
            uniauthor={}
            for field in author.keys():
                uniauthor[field] = _decode(author.get(field))
            uniauthors.append(uniauthor)
        values['authors'] = uniauthors
        uniauthors=[]
        uniauthor={}
        for attr in ref_attributes:
            field = bibref_item.getField(attr)
            if field:
                value = getattr(bibref_item, field.accessor)()
                if not value:
                    value = field.getDefault(bibref_item)
                try:
                    for x in range(value.len()):
                        value[x] = _decode(value[x])
                    values[attr] = value
                except:
                    if type(value) == type(''):
                        values[attr] = _decode(value)
                    else:
                        # this is mainly for the editor flag (not a string, no unicode transformation possible
                        values[attr] = value
        values['source'] = _decode(bibref_item.Source())
        values['description'] = _decode(bibref_item.Description())
        values['meta_type'] = bibref_item.meta_type
        values['reference_type'] = bibref_item.getReference_type() # should be same as portal_type
        if title_link:
            mtool = getToolByName(self, 'portal_membership')
            bibref_item_roles = mtool.getAuthenticatedMember().getRolesInContext(bibref_item)
            if not title_link_only_if_owner or [ role for role in ['Owner', 'Manager'] if role in bibref_item_roles ]:
                values['title_link'] = bibref_item.absolute_url()
        wf_tool = getToolByName(self, 'portal_workflow')
        values['review_state'] = wf_tool.getInfoFor(bibref_item, 'review_state', '')
        if instance is not None:
            values['came_from'] = instance.absolute_url()
            values['came_from_title'] = _decode(instance.Title())
            values['came_from_description'] = _decode(instance.Description())
        return values

    def listWfStatesForReferenceTypes(self, filter_similar=1):

        wtool = getToolByName(self, 'portal_workflow')
        bibref_chain = []
        for reftype in self.getReferenceTypes():
            bibref_chain.extend(list(wtool.getChainForPortalType(reftype)))

        uniq_chain = []
        dummy = [ uniq_chain.append(ch) for ch in bibref_chain if ch not in uniq_chain ]

        bibref_states = []
        for statesByWorkflow in [ wtool.getWorkflowById(wf_id).states.objectValues() for wf_id in uniq_chain if wtool.getWorkflowById(wf_id) ]:
            bibref_states.extend(statesByWorkflow)

        # TODO: When using CMFPlacefulWorkflow the retrieved bibref_states might be an empty list.
        #       For this case let us for now just return the standard workflow states
        if not bibref_states:
            return [ ('Private', 'private'), ('Public Draft', 'visible'), ('Pending', 'pending'), ('Published', 'published'), ]

        result = []
        dup_keys = {}
        for state in bibref_states:

            key = '%s:%s' % (state.title, state.getId(), )
            if not filter_similar:
                result.append((state.title, state.getId(), ))
            else:
                if not dup_keys.has_key(key):
                    result.append((state.title, state.getId(), ))
                dup_keys[key] = 1

        return result

    security.declareProtected(View, 'getBibutilsVersion')
    def getBibutilsVersion(self):
        """ Return installed Bibutils version """
        from bibliograph.core.version_check import checkBibutilsVersion
        try:
            return checkBibutilsVersion()
        except RuntimeError, e:
            return 'n/a (%s)' % e

InitializeClass(BibliographyTool)
