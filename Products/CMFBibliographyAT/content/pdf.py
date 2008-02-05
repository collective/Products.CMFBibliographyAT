from zope.interface import implements
from Products.CMFBibliographyAT.interface import IPdfFolder
from Products.CMFBibliographyAT.interface import IPdfFile

from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import ManagePortal, ManageProperties

from Products.CMFCore.utils import getToolByName
from Products.CMFBibliographyAT.config import CMFBAT_USES_LINGUAPLONE
if CMFBAT_USES_LINGUAPLONE:
    from Products.LinguaPlone.public import Schema, \
         PrimaryFieldMarshaller, FileField, FileWidget
else:
    from Products.Archetypes.public import Schema, \
         PrimaryFieldMarshaller, FileField, FileWidget
from Products.Archetypes.public import registerType

from Products.ATContentTypes.content.folder import ATBTreeFolder
from Products.ATContentTypes.content.folder import ATBTreeFolderSchema
from Products.ATContentTypes.content.file import ATFile
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from Products.CMFBibliographyAT.config \
     import PROJECTNAME, USE_EXTERNAL_STORAGE
from folder import associateToBibliographyFolder

if USE_EXTERNAL_STORAGE:
    from Products.ExternalStorage.ExternalStorage import ExternalStorage as Storage
else:
    from Products.Archetypes.Storage import AttributeStorage as Storage

finalizeATCTSchema(ATBTreeFolderSchema, folderish=True, moveDiscussion=False)

PdfFolderSchema = ATBTreeFolderSchema.copy()
PdfFolderSchema['id'].widget.visible['edit'] = 'invisible'

PdfBaseSchema = ATContentTypeSchema.copy()
PdfBaseSchema['id'].widget.condition = 'python: not object.getBibFolder().getSynchronizePdfFileAttributes()'
PdfBaseSchema['title'].required = False
PdfBaseSchema['title'].widget.visible['edit'] = 'invisible'
PdfBaseSchema['description'].widget.visible['edit'] = 'invisible'
PdfBaseSchema['relatedItems'].widget.visible['edit'] = 'invisible'
PdfBaseSchema['allowDiscussion'].widget.visible['edit'] = 'invisible'

PdfFileSchema = PdfBaseSchema + Schema((
    FileField('file',
              #required=True,
              primary=True,
              languageIndependent=True,
              default_content_type = "application/pdf",
              storage = Storage(),
              # validators = (('isNonEmptyFile', V_REQUIRED),),
              widget = FileWidget(
                        label= "Printable File",
                        label_msgid = "label_upload_pdffile_from_bibrefitem",
                        description = "If not in conflict with any copyright issues, use this field to upload a printable version (PDF file) of the referenced resource.",
                        description_msgid = "help_upload_pdffile_from_bibrefitem",
                        i18n_domain = "cmfbibliographyat",
                        show_content_type = False,)),
    ) , marshall=PrimaryFieldMarshaller()
    )

finalizeATCTSchema(PdfFileSchema)

class PdfFolder(ATBTreeFolder):
    """CMFBib's specialized folder for holding printable (pdf) files"""

    implements(IPdfFolder)

    schema = PdfFolderSchema

    content_icon   = 'bibliography_pdffolder.png'
    portal_type    = 'PDF Folder'
    archetype_name = 'PDF Folder'

    allowed_content_types = ()
    filter_content_types = True

    _assoc_bibliography_folder = None

    typeDescription= "A specialized folder for holding printable (pdf) files"

    security       = ClassSecurityInfo()

    # play nice with the bibfolders custom listing
    publication_year = "0001" # should suffice to be always last

    # this method is provided as a function in CMFBAT's folder module
    associateToBibliographyFolder = associateToBibliographyFolder

    def Authors(self, *args, **kw):
        """ compatibility method """
        return "Printable files"

    def Title(self):
        """ the Title"""
        return "PDFs"

    def getPublication_year(self):
        """ compatibility method """
        return "as available"

    def Source(self):
        """ compatibility method """
        return ""

    def nextId(self, testid):
        bib_tool = getToolByName(self, 'portal_bibliography')
        return bib_tool.nextId(testid)

    security.declareProtected(ManagePortal, 'allowPdfFileCreation')
    def allowPdfFileCreation(self):
        """ allow PDF file creation
        """
        return self.manage_pdfFileCreationPolicy(enable=True)

    security.declareProtected(ManagePortal, 'disallowPdfFileCreation')
    def disallowPdfFileCreation(self):
        """ disallow PDF file creation
        """
        return self.manage_pdfFileCreationPolicy(enable=False)

    security.declareProtected(ManagePortal, 'manage_pdfFileCreationPolicy')
    def manage_pdfFileCreationPolicy(self, enable=False):
        """ allow/disallow PDF File creation in PDF Folders...
        """
        disable = not enable
        types_tool = getToolByName(self, 'portal_types')

        if enable:
            pdf_folder_fti = types_tool[self.portal_type]
            if 'PDF File' not in pdf_folder_fti.allowed_content_types:
                pdf_folder_fti.allowed_content_types += ('PDF File',)

        if disable:
            pdf_folder_fti = types_tool[self.portal_type]
            pdf_folder_allowed_types = list(pdf_folder_fti.allowed_content_types)
            for ct_idx in range(len(pdf_folder_allowed_types)-1, -1, -1):
                if pdf_folder_allowed_types[ct_idx] == 'PDF File':
                    del pdf_folder_allowed_types[ct_idx]
            pdf_folder_fti.allowed_content_types = tuple(pdf_folder_allowed_types)

    def getBibFolder(self):

        return self.aq_inner.aq_parent

    def manage_beforeDelete(self, item, container):
        """ do some cleaning up before we leave the world """

        # manage_beforeDelete will be deprecated in Zope 2.11+
        bibfolder = self.getBibFolder()
        bibfolder._assoc_pdf_folder = None
        ATBTreeFolder.manage_beforeDelete(self, item, container)

registerType(PdfFolder, PROJECTNAME)

class PdfFile(ATFile):
    """
    A restricted file type to hold printable (pdf) files only
    Get's its title and description from the associated reference
    """

    implements(IPdfFile)

    schema = PdfFileSchema

    content_icon   = 'bibliography_pdffile.png'
    portal_type    = 'PDF File'
    archetype_name = 'PDF File'
    global_allow = False
    assocMimetypes = ('application/pdf', )

    security       = ClassSecurityInfo()

    def Title(self):
        """Override with the title from the associated reference"""
        refs = self.getBRefs('printable_version_of')
        if not (refs and refs[0]):
            return self.getId()
        else:
            return refs[0].Title()

    def Description(self):
        """Override with authors and source from the associated reference"""
        refs = self.getBRefs('printable_version_of')
        if not refs:
            return "No associated reference"
        ref = refs[0]
        return "PDF of %s (%s): %s Located at portal path: %s" % (ref.Authors(),
                                       ref.getPublication_year(),
                                       ref.Source(),
                                       ref.absolute_url(),
                                       )

    def getBibFolder(self):

        return self.aq_inner.aq_parent.aq_inner.aq_parent

    def getPdfFolder(self):

        return self.aq_inner.aq_parent

registerType(PdfFile, PROJECTNAME)
