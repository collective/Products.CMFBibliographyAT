##########################################################################
#                                                                        #
#           copyright (c) 2003 - 2006 ITB, Humboldt-University Berlin    #
#           written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                        #
##########################################################################

"""BaseEntry: base class for bibliographic references;
defines the common schema elements and provides some
basic functionality """

import pyisbn
from zope.interface import implements

from DateTime import DateTime
from ZPublisher.HTTPRequest import FileUpload
from Acquisition import aq_base
from ComputedAttribute import ComputedAttribute
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View, ModifyPortalContent, \
     ManageProperties, AddPortalContent

from Products.CMFCore.utils import getToolByName

from Products.Archetypes.utils import DisplayList
from Products.Archetypes.Renderer import renderer
from Products.Archetypes.utils import shasattr
from Products.ATExtensions.ateapi import getDisplayList
# try ATCT
from Products.ATContentTypes.content.base \
    import ATCTContent as BaseContent


from Products.ATContentTypes.content.base \
    import cleanupFilename

from Products.CMFBibliographyAT.interfaces import IBibliographyExport
from Products.CMFBibliographyAT.interface import IBibliographicItem
from Products.CMFBibliographyAT.interface import IBibAuthorMember

from Products.CMFBibliographyAT.content.schemata \
    import HeaderSchema, AuthorSchema, CoreSchema, TrailingSchema

from Products.CMFBibliographyAT.utils import _getCoinsString

from bibliograph.core.utils import _encode, _decode

BaseEntrySchema = HeaderSchema + \
                  AuthorSchema + \
                  CoreSchema + \
                  TrailingSchema

class BaseEntry(BaseContent):
    """Base content for bibliographical references content types
    """

    implements(IBibliographicItem)

    global_allow = 0
    content_icon = 'bibliography_entry.png'
    immediate_view = 'bibliography_entry_view'
    default_view = 'bibliography_entry_view'
    suppl_views    = ('bibliography_entry_view',
                      'base_view',
                      'table_view',
                      )

    schema = BaseEntrySchema
    _at_rename_after_creation = True

    __implements__ = (BaseContent.__implements__,
                      IBibliographyExport,
                     )
    security = ClassSecurityInfo()

    # the default source
    security.declareProtected(View, 'Source')
    def Source(self):
        """
        the default source format
        """
        try:
            source = self.DefaultSource()
        except AttributeError:   # don't blow if we have no skin context
            source = self.portal_type
        return source

    security.declareProtected(View, 'isTranslatable')
    def isTranslatable(self):

        bib_tool = getToolByName(self, 'portal_bibliography')
        plone_utils = getToolByName(self, 'plone_utils')
        return bib_tool.isBibrefItemTranslatable() and plone_utils.isTranslatable(self)

    security.declareProtected(View, 'getCookIdWarning')
    def getCookIdWarning(self, **kwargs):
        try:
            return self.getId(**kwargs)
        except TypeError:
            return self.getId()

    security.declareProtected(View, 'getReferenceTypes')
    def getReferenceTypes(self):

        bib_tool = getToolByName(self, 'portal_bibliography')
        return bib_tool.getReferenceTypes()


    security.declareProtected(View, 'getAbstract')
    def getAbstract(self, html_format=False, **kw):
        """ get the 'description' and put it in the 'abstract'
        """
        if not html_format:
            return self.Description(**kw)

        # this is for dynamic migration: in v0.8 description and abstract were the same field (description)
        # in > v0.9 'abstract' stores the html abstract, 'description' the plain text abstract.
        if not self.Schema()['abstract'].get(self, **kw) and self.Description(**kw):
            return self.Description(**kw)

        return self.Schema()['abstract'].get(self, **kw)

    security.declareProtected(View, 'editAbstract')
    def editAbstract(self, **kw):
        """ get the 'description' and put it in the 'abstract'
        """
        return self.getAbstract(html_format=True, raw=True, **kw)

    security.declareProtected(ModifyPortalContent, 'setAbstract')
    def setAbstract(self, val, **kw):
        """ synchronize 'abstract' and 'description'
        """
        tr_tool = getToolByName(self, 'portal_transforms')
        plain = tr_tool.convertTo('text/plain', val)
        self.setDescription(plain.getData().replace('\r\n', ' ').replace('\n\r', ' ').replace('\r', ' ').replace('\n', ' ').strip())
        self.Schema().getField('abstract').set(self, value=val, **kw)


    # helper method for direct attribute access
    # !! Should not be called anymore since Archetypes
    # !! builds automatic getFieldName() methods
    # rr: still needed by the bibtex renderer

    def getFieldValue(self, field_name):
        """
        get a field's value
        """
        field = self.getField(field_name)
        value = getattr(self, field.accessor)()
        if value:
            return value
        else:
            try:
                return field.getDefault()
            except TypeError:
                # AT1.3 compliant
                return field.getDefault(self)

    # custom methods for author handling
    security.declareProtected(View, 'getAuthorList')
    def getAuthorList(self):
        """
        returns the list of author dictionaries for editing
        assumes attribute storage for authors

        Deprecated; use default accessor instead
        """
        return self.getAuthors()

    security.declareProtected(View, 'AuthorItems')
    def AuthorItems(self, format="%L %f"):
        """
        returns a list of author strings, e.g.,
        ["Foo J", "Bar B"]
        useful for being indexed with a keyword index
        """
        return [a(format) for a in self.getAuthors()]

    security.declareProtected(View, 'Authors')
    def Authors(self, *args, **kwargs):
        """Alias for the publication author's accessor
        with a custom default format ("%L, %f%m") if not specified"""
        if 'format' not in kwargs.keys():
            kwargs['format'] = "%L, %f%m"
        return self.getAuthors()(*args, **kwargs)

    security.declareProtected(View, 'getURL')
    def getURL(self, defaultURL=None, relative=None, remote=False):
        """
        the publication_url if set, otherwise a link to PubMed
        if pmid is set, the default if not None or the item's
        absolute_url otherwise except if relative equals 1
        in which case the items relative url is obtained from
        the portal_url tool.
        """
        if relative==1:
            # called from folder_contents and friends
            utool = getToolByName(self, 'portal_url')
            return utool.getRelativeContentURL(self)
        url = self.getPublication_url()
        if url:
            return url
        elif not remote:
            return defaultURL or self.absolute_url()
        else:
            return defaultURL

    ## helper methods for dealing with multiple common identifiers

    def _getIdentifier(self, label):
        ids = self.getIdentifiers()
        for id in ids:
            if id.get('label') == label:
                return id.get('value')
        return None
        
    security.declareProtected(View, 'PMID')
    def PMID(self):
        """
        to be available for all types
        overwritten by article
        """
        return self._getIdentifier('PMID')

    security.declareProtected(View, 'ISBN')
    def ISBN(self):
        """
        to be available for all types
        overwritten by books
        """
        return self._getIdentifier('ISBN')

    # original accessor of the ISBN field
    security.declareProtected(View, 'getIsbn')
    getIsbn = ISBN

    security.declareProtected(View, 'publicationIdentifiers')
    def publicationIdentifiers(self, instance=None):
        """
        list of common identifiers for publications
        used as vocabulary for the 'identifiers' field
        """
        return getDisplayList(self, 'publication_identifiers')

    security.declareProtected(View, 'additionalFields')
    def additionalFields(self, instance=None):
        """
        list of additional field keys for publications
        used as vocabulary for the 'additional' field
        Managed as property on the bibliography tool
        """
        bibtool = getToolByName(self, 'portal_bibliography', None)
        if bibtool is not None:
            values = bibtool.getProperty('additional_fields',[])
            select = ('','Select')
            dlist = [(value,value) for value in values]
            return DisplayList([select]+dlist)
        return []

    def allowAdditionalFields(self):
        """
        returns the flag set on the bibliography tool controlling
        the availability of additional fields
        """
        bibtool = getToolByName(self, 'portal_bibliography', None)
        if bibtool is not None:
            return bibtool.getProperty('allow_additional_fields',False)
        return False

    security.declareProtected(View, 'pre_validate')
    def pre_validate(self, REQUEST, errors):

        at_tool = getToolByName(self, 'archetype_tool')

        authors = REQUEST.get('authors',[])
        result = []
        references=[]

        # deduce author names from member reference
        for author in authors:
            reference = author.get('reference', None)
            if reference == 'None':
                author.reference = ''
            elif reference:

                reference_object = at_tool.lookupObject(reference)
                if reference_object.isTranslatable():
                    references.append(reference_object.getCanonical().UID())
                    reference_object = reference_object.getCanonical()
                else:
                    references.append(reference)

                # obtain author data from privileged fields in the reference object
                data = self.getAuthorDataFromMember(reference_object)
                only_requested_data = not not author.get('lastname', None)
                if data:
                    for key in [ key for key in data.keys() if key not in ('middlename',) ]:
                        if not only_requested_data or (author.get(key, None) == '?'):
                            if key == 'firstname':
                                author.firstnames = _decode(data['firstname']) + ' ' + _decode(data['middlename'])
                            else:
                                exec('author.%s = _decode(data[key])' % key)

                # if this doesn't help, we try to derive the author name from the Title of reference... (YUK)
                if not author.get('lastname', None):
                    firstnames, lastname = self._name_from_reference(reference)
                    author.firstnames = firstnames
                    author.lastname = lastname

            if ''.join([_decode(_encode(val)) for val in dict(author).values()]).strip():
                result.append(author)

        REQUEST.form['authors'] = result[:]
        REQUEST.form['member_publication_authors'] = references[:]

    def _name_from_reference(self, uid):
        catalog = getToolByName(self, 'uid_catalog', None)
        if catalog is None:
            return ('','')
        brains = catalog(UID=uid)
        if not brains:
            return ('','')
        parts = brains[0].Title.split()
        first = ''.join(parts[:-1]).strip()
        last = parts[-1]
        return first, last


    security.declareProtected(View, 'getPublicationDate')
    def getPublicationDate(self):
        """
        Returns the publication date as DateTime
        or None if it is not well defined
        """
        year = self.getField('publication_year').get(self)
        try:
            year = int(year)
        except ValueError:
            year = None

        month = self.getField('publication_month').get(self)
        if month:
            try:
                month = int(month)
            except ValueError:
                try:
                    # This is probably a string
                    monthcomp = month.split(' ')
                    month = 1
                    for m in monthcomp:
                        if m.lower() in DateTime._monthmap.keys():
                            month = m
                            continue
                except (ValueError, AttributeError, IndexError):
                    month = 1
        else:
            month = 1

        return year and DateTime('%s/%s/01' % (year, month)) or None

    publication_date = ComputedAttribute(getPublicationDate, 1)

    # PDF support stuff
    security.declareProtected(View, 'widget')
    def widget(self, field_name, mode='view', field=None, **kwargs):
        """ special handling for uploaded_pdfFile widget
        """
        bib_tool = getToolByName(self, 'portal_bibliography')
        pdf_file = self.getPdf_file()
        if (pdf_file and self.isPdfUploadAllowedForThisType() and \
            bib_tool.allowPdfUploadPortalPolicy()) and \
            ((field_name == 'uploaded_pdfFile') or \
             (field == self.Schema().getField('uploaded_pdfFile'))):

            if pdf_file:
                field_name = 'uploaded_pdfFile'
                if field is None:
                    field = pdf_file.Schema()['file']
                widget = field.widget
                return renderer.render(field_name,
                                       mode,
                                       widget,
                                       pdf_file,
                                       field=field,
                                       **kwargs)

        else:

            return BaseContent.widget(self,
                                      field_name=field_name,
                                      mode=mode,
                                      field=field,
                                      **kwargs)

    security.declareProtected(View, 'getPdfFolderPath')
    def getPdfFolderPath(self):
        """path to the pdfs folder in the parent bib-folder"""
        url_tool = getToolByName(self, 'portal_url')
        pdff = self.getBibFolder().getPdfFolder()
        return url_tool.getRelativeContentURL(pdff)

    security.declareProtected(AddPortalContent, 'setUploaded_pdfFile')
    def setUploaded_pdfFile(self, value=None, **kwargs):
        """create PDF file in PDF folder on-the-fly"""
        bib_tool = getToolByName(self, 'portal_bibliography')
        types_tool = getToolByName(self, 'portal_types')
        bibfolder = self.getBibFolder()
        pdf_file = self.getPdf_file()
        if not pdf_file and isinstance(value, FileUpload):

            pdf_folder = bibfolder.getPdfFolder()

            # create PDF file and associate reference with it
            file_field = self.getField('uploaded_pdfFile')

            if bibfolder.getSynchronizePdfFileAttributes():

                pdf_file_id = self.getId() + '.pdf'

            else:
                file_field.getFilename(self, fromBaseUnit=False)
                file_field.getFilename(self, fromBaseUnit=True)
                try:
                    request=getattr(self, 'REQUEST', None)
                    pdf_file_id = cleanupFilename(filename=value.filename,
                                                  request=request,
                                                  )
                except TypeError: # BBB < Plone 3
                    pdf_file_id = cleanupFilename(filename=value.filename,
                                                  context=self,
                                                  encoding=self.getCharset(),
                                                  )

            # temporarily allow PDF File creation in PDF Folder,
            # create PDF File, revoke PDF File creation allowance
            pdf_folder.allowPdfFileCreation()
            new_id = pdf_folder.invokeFactory(id=pdf_file_id,
                                              type_name='PDF File',
                                              )
            pdf_folder.disallowPdfFileCreation()

            # find the PDF File's ID and get the object
            if new_id is None or (new_id == ''):
                new_id = pdf_file_id
            pdf_file = pdf_folder._getOb(id=new_id)

            # set the file value
            pdf_file.setFile(value, **kwargs)
            if pdf_file:
                self.setPdf_file(value=pdf_file.UID())

        elif pdf_file and isinstance(value, FileUpload):
            ## replace file field in PDF file
            pdf_file.setFile(value, **kwargs)

        elif pdf_file and isinstance(value, basestring) and (value == 'DELETE_FILE'):

            pdf_folder = bibfolder.getPdfFolder()
            ## delete PDF file, delete PDF file reference
            pdf_folder.manage_delObjects(ids=[pdf_file.getId()])
            self.setPdf_file(value=None)

    security.declareProtected(View, 'getUploaded_pdfFile')
    def getUploaded_pdfFile(self, **kwargs):
        """ retrieve pdf document from associated pdf file
        """
        bib_tool = getToolByName(self, 'portal_bibliography')
        pdf_file = self.getPdf_file()
        if (pdf_file is not None) and self.isPdfUploadAllowedForThisType() and bib_tool.allowPdfUploadPortalPolicy():
            return pdf_file.Schema()['file'].getBaseUnit(pdf_file, **kwargs)
        else:
            return None

    security.declareProtected(View, 'editUploaded_pdfFile')
    def editUploaded_pdfFile(self, **kwargs):
        """ retrieve pdf document from associated pdf file for editing
        """
        return self.getUploaded_pdfFile(**kwargs)

    security.declarePrivate('manage_beforeDelete')
    def manage_beforeDelete(self, item, container):

        # manage_beforeDelete is deprecated in Zope 2.11+

        ### remove associated PDF file if any
        ###
        ### BEWARE: to debug this code go into 
        ###         portal_skins/plone_scripts/object_delete 
        ###         and comment out the
        ###         fallback exception or use PloneTestCase
        ###

        bibfolder = self.getBibFolder()

        # delete PDF file (if any) only if _delete_associated_pdffile 
        # flag in bibfolder is set
        pdf_file = self.getPdf_file()
        if pdf_file:
            if bibfolder._delete_associated_pdffiles:

                bibfolder = self.getBibFolder()
                pdf_folder = bibfolder.getPdfFolder()
                pdf_file = self.getPdf_file()
                pdf_folder.manage_delObjects(ids=[pdf_file.getId()])
                bibfolder._delete_associated_pdffiles = False

            if bibfolder._move_associated_pdffiles:

                setattr(item, '_temp_pdffile_UID', pdf_file.UID())

        BaseContent.manage_beforeDelete(self, item, container)

    security.declarePrivate('manage_afterAdd')
    def manage_afterAdd(self, item, container):

        # manage_afterAdd is deprecated in Zope 2.11+

        ### copy PDF file if bibreference has been copied

        ###
        ### BEWARE: to debug this code go into 
        ###         portal_skins/plone_scripts/folder_paste 
        ###         and comment out the
        ###         fallback exception or use PloneTestCase
        ###

        at_tool = getToolByName(self, 'archetype_tool')
        bib_tool = getToolByName(self, 'portal_bibliography')
        bibfolder = container

        # grab the PDF file and its back references before the reference is removed by
        # BaseContent.manage_afterAdd
        pdf_file = self.getPdf_file() or None
        pdf_file_uid = ''
        if pdf_file:
            pdf_file_uid = pdf_file.UID()
            pdf_file_brefs = [ bref.UID() for bref in pdf_file.getBRefs('printable_version_of') if bref is not None ]

        if not pdf_file_uid and shasattr(self, '_temp_pdffile_UID') and self._temp_pdffile_UID:
            pdf_file_uid = self._temp_pdffile_UID
            pdf_file_brefs = [ bref.UID() for bref in at_tool.lookupObject(pdf_file_uid).getBRefs('printable_version_of') if bref is not None ]
            delattr(self, '_temp_pdffile_UID')

        # first do all necessary ATCT, Archetypes, etc. things...
        BaseContent.manage_afterAdd(self, item, container)

        # we have to set another transaction savepoint here, 
        # before we can cut or copy the associated PDF file
        bib_tool.transaction_savepoint(optimistic=True)

        # then check PDF file association
        pdf_file = pdf_file_uid and at_tool.lookupObject(pdf_file_uid)
        if pdf_file and pdf_file_brefs and (self.UID() not in pdf_file_brefs):

            # bibref item has been copied and UID of bibref item has changed
            # => copy PDF file
            new_pdf_file = self.relocatePdfFile(pdf_file=pdf_file, op=0)
            self.setPdf_file(value=new_pdf_file.UID())

        elif pdf_file and (pdf_file.aq_inner.aq_parent.aq_inner.aq_parent.getPhysicalPath() != self.aq_inner.aq_parent.getPhysicalPath()):

            # PDF file and bibref item are not in the same bibfolder
            # => move PDF file!!!
            moved_pdf_file = self.relocatePdfFile(pdf_file=at_tool.lookupObject(pdf_file_uid), op=1)

    security.declareProtected(AddPortalContent, 'relocatePdfFile')
    def relocatePdfFile(self, pdf_file=None, bibfolder=None, op=1):
        """ find associated PDF File and move into correct PDF Folder
            --> used for manage_cutObjects -> manage_pasteObjects
            --> used if PDF Folder is inconsistent
            op == 0: copy operation
            op == 1: move operation (default)
        """
        bib_tool = getToolByName(self, 'portal_bibliography')

        bibfolder = bibfolder or self.getBibFolder()
        pdf_file = pdf_file or self.getPdf_file()

        new_pdf_file = None
        if pdf_file:

            pdf_folder = bibfolder.getPdfFolder()
            if (pdf_file not in pdf_folder.contentValues()) or (op==0):

                pdf_file_id = pdf_file.getId()

                # we need to explicitly add 'PDF File' content type 
                # as allowed type to 'PDF Folder' content type
                pdf_folder.allowPdfFileCreation()

                # if the edit action was cut+paste, we will copy the PDF file
                # here anyway. In case of cut+past it
                # will be deleted by self.manage_beforeDelete.
                if op == 0: pdf_objs = pdf_file.aq_inner.aq_parent.manage_copyObjects([pdf_file_id])
                elif op == 1: pdf_objs = pdf_file.aq_inner.aq_parent.manage_cutObjects([pdf_file_id])
                result = pdf_folder.manage_pasteObjects(pdf_objs)

                # restore PDF Folder's allowed content types
                pdf_folder.disallowPdfFileCreation()

                # get the new PDF file
                new_pdf_file_id = [ res['new_id'] for res in result if res['id'] == pdf_file_id ][0]
                new_pdf_file = pdf_folder._getOb(new_pdf_file_id)

                # set field values of the new PDF file
                if bibfolder.getSynchronizePdfFileAttributes():
                    self.bibliography_pdffile_cookId()

        if new_pdf_file:
            # make sure our new PDF file gets seen by the portal's catalog tool
            new_pdf_file.reindexObject()
            return new_pdf_file

    security.declareProtected(View, 'isPdfUploadAllowedForThisType')
    def isPdfUploadAllowedForThisType(self):

        bib_folder = self.getBibFolder()
        return self.portal_type in bib_folder.getAllowPdfUploadForTypes()

    security.declareProtected(View, 'download_pdf')
    def download_pdf(self):
        """
        Returns the URL of the printable (pdf) file.

        Used by the download printable action
        """
        bib_tool = getToolByName(self, 'portal_bibliography')

        # for the case that people have already uploaded files and
        # policy changed later we have to assume that PDF files are
        # already there and shall be hidden after the setup of a more
        # restricted policy.
        if bib_tool.allowPdfUploadPortalPolicy():

            if self.isPdfUploadAllowedForThisType():

                pdf_file = self.getPdf_file()
                if pdf_file:
                    return pdf_file.absolute_url()

        pdf_url = self.getPdf_url()
        if pdf_url:
            return pdf_url
        return None

    security.declareProtected(View, 'has_pdf')
    def has_pdf(self):
        """Used by the download printable action condition"""
        return self.download_pdf() and True or False

    security.declareProtected(View, 'validate_identifiers')
    def validate_identifiers(self, data={}):
        """ Identifier verification: types can only be used once """

        if data['label'] == 'ISBN':
            isbn = data.get('value')
            if not isbn:
                return
            try:
                isbn_ok = pyisbn.validate(isbn)
            except ValueError, e:
                isbn_ok = False

            if not isbn_ok:
                return 'Invalid ISBN %s' % isbn

    security.declareProtected(View, 'post_validate')
    def post_validate(self, REQUEST=None, errors=None):
        """Make sure our dependend gets cataloged as well"""

        pdf_file = self.getPdf_file()
        if pdf_file:
            pdf_file.reindexObject()

    security.declarePrivate('_renameAfterCreation')
    def _renameAfterCreation(self, check_auto_id=False):
        """override Archetype's _renameAfterCreation method with 
           CMFBAT's ID cooker
        """
        pass # A very efficient nop

    security.declarePrivate('at_post_create_script')
    def at_post_create_script(self):
        self.at_post_edit_script()

    security.declarePrivate('at_post_edit_script')
    def at_post_edit_script(self):

        bib_tool = getToolByName(self, 'portal_bibliography')
        plone_utils = getToolByName(self, 'plone_utils')
        bibfolder = self.getBibFolder()

        # id cooking
        if (bibfolder.getCookIdsOnBibRefCreation() and plone_utils.isIDAutoGenerated(self.getId())) or bibfolder.getCookIdsAfterBibRefEdit():
            new_id = bib_tool.cookReferenceId(ref=self, idcooker_id=bibfolder.getReferenceIdCookingMethod())
            if new_id != 'nobody1000':

                # this will implicitly call the PDF File rename code 
                # via self.manage_renameObject
                self.bibliography_entry_cookId()

            else:
                # no author, no publication year, do not know what to do
                BaseContent._renameAfterCreation(self, check_auto_id=True)

        # infer member references after edit
        if bib_tool.inferAuthorReferencesAfterEdit():
            self.inferAuthorReferences()

    security.declareProtected(View, 'getBibFolder')
    def getBibFolder(self):
        """ return the bibref items bibliography folder """
        return self.aq_inner.aq_parent


    # support inline citations
    security.declareProtected(View, 'citationLabel')
    def citationLabel(self, join_two='and', et_al='et al.'):
        """
        a short label for inline citations like
        "Ritz, 1995" or "Ritz and Herz, 2004" or
        "Ritz et al., 2005"
        """
        authors = self.getAuthors()
        nofa = len(authors)
        year = self.getField('publication_year').get(self)

        if nofa == 0:
            return "Anonymous, %s" % year

        if nofa == 1:
            return "%s, %s" % (authors[0].get('lastname', ''),
                               year)
        if nofa == 2:
            return "%s %s %s, %s" % (authors[0].get('lastname', ''),
                                     join_two,
                                     authors[1].get('lastname', ''),
                                     year)
        return "%s %s, %s" % (authors[0].get('lastname', ''),
                              et_al,
                              year)

    security.declareProtected(View, 'getReference_type')
    def getReference_type(self):
        return self.meta_type

    security.declareProtected(View, 'additionalReferenceInfo')
    def additionalReferenceInfo(self):
        """
        'Authors (year): Source'
        to be shown in reference browser widgets
        """
        s = "%s (%s): %s" % (self.Authors(),
                             self.getPublication_year(),
                             self.Source()
                             )
        return s


    ############################################################################
    #                                                                          #
    #     Adapted methods                                                      #
    #                                                                          #
    ############################################################################

    security.declareProtected(ModifyPortalContent, 'inferAuthorReferences')
    def inferAuthorReferences(self, report_mode='v', is_new_object=False):
        """
        Try to set author references, e.g., after uploads
        """
        return IBibAuthorMember(self).inferAuthorReferences(report_mode, is_new_object)

    security.declareProtected(View, 'getSiteMembers')
    def getSiteMembers(self, *args, **kw):
        """
        For use when members are authors, return a DisplayList of members
        Alternative to 'getMembers' if 'no reference' must not be empty
        (to work around a bug in the 'Records' packager)
        """
        return IBibAuthorMember(self).getSiteMembers( *args, **kw)

    security.declareProtected(View, 'showMemberAuthors')
    def showMemberAuthors(self):
        """ return True if referencing of authors / editors to portal members is supported
        """
        return  IBibAuthorMember(self).showMemberAuthors()

    security.declareProtected(View, 'getCoinsString')
    def getCoinsString(self):
        return _getCoinsString(self, self.getCoinsDict())

    security.declareProtected(View, 'getCoinsDict')
    def getCoinsDict(self):
        coinsData = {}
        coinsData['rfr_id'] = hasattr(self,'DOI') and self.DOI or self.absolute_url()
        coinsData['rft.date'] = self.getPublication_year()
        coinsData['rft.isbn'] = self.ISBN()
        authorNames = []
        for author in self.getAuthors():
            # getAuthors returns the blank rows as well, skip over them.
            if 'lastname' in author.keys():
                authorNames.append("%s %s" % (author['firstname'], author['lastname']))
        coinsData['rft.au'] = authorNames

        return coinsData
