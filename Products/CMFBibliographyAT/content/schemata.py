from Products.CMFBibliographyAT.config import CMFBAT_USES_LINGUAPLONE
if CMFBAT_USES_LINGUAPLONE:
    from Products.LinguaPlone.public import Schema
    from Products.LinguaPlone.public import StringField, TextField, LinesField
    from Products.LinguaPlone.public import ReferenceField, FileField
    from Products.LinguaPlone.public import ReferenceWidget
    from Products.LinguaPlone.public import TextAreaWidget
    from Products.LinguaPlone.public import FileWidget
    from Products.LinguaPlone.public import RichWidget, StringWidget
    from Products.LinguaPlone.public import KeywordWidget
else:
    from Products.Archetypes.public import Schema
    from Products.Archetypes.public import StringField, TextField, LinesField
    from Products.Archetypes.public import ReferenceField, FileField
    from Products.Archetypes.public import ReferenceWidget
    from Products.Archetypes.public import TextAreaWidget
    from Products.Archetypes.public import FileWidget
    from Products.Archetypes.public import RichWidget, StringWidget
    from Products.Archetypes.public import KeywordWidget

from Products.Archetypes import PloneMessageFactory as _
from Products.ATContentTypes.content.schemata \
     import ATContentTypeSchema as BaseSchema

from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget \
     import ReferenceBrowserWidget

from Products.CMFBibliographyAT.marshall import BibtexMarshaller
from Products.ATExtensions.ateapi import FormattableNamesField
from Products.ATExtensions.ateapi import FormattableNamesWidget
from Products.ATExtensions.ateapi import CommentField, CommentWidget
from Products.ATExtensions.ateapi import RecordsField, RecordsWidget


HeaderSchema = BaseSchema.copy()
HeaderSchema['id'].widget.macro_edit = "widgets/string"
# XXX ugly hack as long as IdWidget subclasses TypesWidget
HeaderSchema['id'].widget.size = 40
HeaderSchema['id'].widget.maxlength = 255
HeaderSchema['id'].widget.condition = 'python: object.visibleIdsEnabled() and not object.getBibFolder().getCookIdsAfterBibRefEdit()'

CookIdWarningField = StringField('shortname_cookid_warning',
                 schemata="default",
                 mode="rw",
                 accessor="getCookIdWarning",
                 widget = StringWidget(
                    label="Short Name",
                    label_msgid="label_shortname_cookid_warning",
                    description="There is ID re-cooking (after every edit / paste action) enabled on this item's parent bibliography folder. You cannot manually edit this item's short name. Modifications in this field will be ignored.",
                    description_msgid="help_shortname_cookid_warning",
                    i18n_domain="cmfbibliographyat",
                    modes=('view', 'edit'),
                    condition = 'python: object.getBibFolder().getCookIdsAfterBibRefEdit() and object.portal_membership.getAuthenticatedMember().getProperty("visible_ids", object.portal_memberdata.getProperty("visible_ids"))',
                 ),
)

HeaderSchema.addField(CookIdWarningField)

tmp_title = HeaderSchema['title']
tmp_title.is_duplicates_criterion=True
del HeaderSchema['title']

AuthorSchema = Schema((
    FormattableNamesField('authors', # was 'publication_authors',
        searchable = 1,
        required = 0,
        minimalSize = 2,
        subfields=('username','firstnames','lastname', 'homepage'),
        subfield_sizes={'firstnames':20, 'lastname':20, 'homepage':15},
        subfield_labels={'username':'Site Members'},
        subfield_vocabularies={'username':'getSiteMembers'},
        subfield_conditions={'username':'python:object.showMemberAuthors()'},
        subfield_maxlength={'homepage': 250,},
        is_duplicates_criterion=True,
        widget=FormattableNamesWidget(label="Authors",
            label_msgid="label_authors",
            macro_edit = "authors_widget",
            helper_js = ('authors_widget.js',),	
            description="If possible, always fill in the complete authors' / editors' names.",
            description_msgid="help_authors",
            i18n_domain="cmfbibliographyat",
        ) ,
    ),
))

CoreSchema = Schema((
    tmp_title,
    StringField('publication_year',
        searchable=1,
        required=1,
        languageIndependent=1,
        is_duplicates_criterion=True,
        widget=StringWidget(
            label="Publication Year",
            label_msgid="label_publication_year",
            description_msgid="help_publication_year",
            description="The year of publication. For unpublished works, please specify the year of composure. This field should contain a year number like '1984', but it can also process notes like 'in print' etc.",
            i18n_domain="cmfbibliographyat",
            ),
        ),
    TextField('abstract',
        searchable=1,
        required=0,
        default_content_type='text/html',
        default_output_type='text/x-html-safe',
        allowable_content_types=('text/structured',
                                 'text/restructured',
                                 'text/html',
                                 'text/plain',),
        accessor="getAbstract",
        edit_accessor="editAbstract",
        mutator="setAbstract",
        widget=RichWidget(
            label="Abstract",
            label_msgid="label_abstract",
            description="An abstract of the referenced publication. Please contact your portal's reviewers if unsure about the site's default language for abstracts in bibliographical references.",
            description_msgid="help_abstract",
            i18n_domain="cmfbibliographyat",
            rows=5,
            ),
        ),
    # full text and printable versions
    CommentField('explain_links',
                 schemata="full text",
                 comment = """\
                 There are several ways to make reference to
                 the original paper:

                   - A link to an online version

                   - A link to a printable (pdf) version

                   - Upload a printable (pdf) file""",
                 comment_msgid="comment_explain_links",
                 comment_type = "text/structured",
                 widget = CommentWidget(
                    i18n_domain="cmfbibliographyat",
                 ),
    ),
    StringField('publication_url',
        schemata="full text",
        required=0,
        searchable=0,
        ## validators=('isURL',),    # re-enable if it doesn't fail
                                     # for empty values any more
        widget=StringWidget(
            label="Online URL",
            label_msgid="label_url",
            description="The (external) URL to get to an online version of the referenced resource.",
            description_msgid="help_url",
            i18n_domain="cmfbibliographyat",
            size=60,
            ),
        ),
    StringField('pdf_url',
        schemata="full text",
        required=0,
        searchable=0,
        ## validators=('isURL',),    # re-enable if it doesn't fail
                                     # for empty values any more
        widget=StringWidget(
            label="PDF URL",
            label_msgid="label_pdfref_url",
            description="The (external) URL to retrieve a printable version (PDF file) of the referenced resource from.",
            description_msgid="help_pdfref_url",
            i18n_domain="cmfbibliographyat",
            size=60,
            ),
        ),
    ReferenceField('pdf_file',
                    schemata="full text",
                    relationship="printable_version_of",
                    multiValued=0,
                    required=0,
                    allowed_types=("PDF File",),
                    # allowed_types=("PDF File", "File"),
                    widget=ReferenceBrowserWidget(
                        label="AT Reference to Printable File (PDF Format)",
                        label_msgid="label_pdf_file",
                        description="This is AT field is hidden to anyone but portal managers. It refers to the associated PDF document on this site (if any). Use it for repair if the PDF file association of this bibliographical entry is broken.",
                        description_msgid="help_pdf_file",
                        addable=0,
                        force_close_on_insert=True,
                        destination='getPdfFolderPath',
                        startup_directory_method='getPdfFolderPath',
                        i18n_domain = "cmfbibliographyat",
                        visible={'edit': 'visible', 'view': 'invisible',},
                        condition="python: object.portal_membership.checkPermission('ManagePortal', object)",
                    ),
    ),
    FileField('uploaded_pdfFile',
                    schemata="full text",
                    languageIndependent=True,
                    default_content_type = "application/pdf",
                    mutator='setUploaded_pdfFile',
                    edit_accessor='editUploaded_pdfFile',
                    accessor='getUploaded_pdfFile',
                    #validators = (('isNonEmptyFile', V_REQUIRED),),
                    widget = FileWidget(
                                label= "Printable PDF File",
                                label_msgid = "label_upload_pdffile_from_bibrefitem",
                                description = "If not in conflict with any copyright issues, use this field to upload a printable version (PDF file) of the referenced resource.",
                                description_msgid = "help_upload_pdffile_from_bibrefitem",
                                i18n_domain = "cmfbibliographyat",
                                show_content_type = True,
                                condition="python:object.portal_bibliography.allowPdfUploadPortalPolicy() and object.isPdfUploadAllowedForThisType()",
                    ),
    ),
    ReferenceField('is_duplicate_of',
                    relationship="hasDuplicates",
                    multiValued=1,
                    required=0,
                    allowed_types='getBibReferenceTypes',
                    widget=ReferenceWidget(
                        visible={'edit': 'invisible', 'view': 'invisible',},
                    ),
    ),
))

TrailingSchema = Schema((
    RecordsField('identifiers',
        searchable=0,
        required=0,
        languageIndependent=1,
        is_duplicates_criterion=False,
        subfields = ('label', 'value'),
        subfield_labels ={'label':'Identifier'},
        subfield_vocabularies = {'label':'publicationIdentifiers',},      
        widget=RecordsWidget(
                i18n_domain = "cmfbibliographyat",
                label = u"Identifiers",
                ),
        ),
    LinesField('keywords',
        searchable=1,
        required=0,
        languageIndependent=1,
        is_duplicates_criterion=False,
        multiValued=1,
        widget=KeywordWidget(
                label=_(u'label_keywords', default=u'Keywords'),
                description=_(u'help_keywords',
                              default=u'Categorization of the publications content.'),
                i18n_domain = "cmfbibliographyat",
                ),
        ),
    StringField('publication_month',
        searchable=1,
        required=0,
        languageIndependent=1,
        is_duplicates_criterion=True,
        widget=StringWidget(
            label="Publication Month",
            label_msgid="label_publication_month",
            description_msgid="help_publication_month",
            description="Month of publication (or writing, if not published).",
            i18n_domain="cmfbibliographyat",
            ),
        ),
    TextField('note',
        searchable=1,
        required=0,
        is_duplicates_criterion=True,
        widget=TextAreaWidget(label="Note",
            label_msgid="label_note",
            description_msgid="help_note",
            description="Any additional information that can help the reader. The first word should be capitalized.",
            i18n_domain="cmfbibliographyat",
            ),
        ),
    TextField('annote',
        searchable=1,
        required=0,
        is_duplicates_criterion=True,
        widget=TextAreaWidget(label="Annote",
            label_msgid="label_annote",
            description_msgid="help_annote",
            description="Any annotation that you do not wish to appear in rendered (bibtex) bibliographies.",
            i18n_domain="cmfbibliographyat",
            ),
        ),
    RecordsField('additional',
        searchable=0,
        required=0,
        languageIndependent=0,
        is_duplicates_criterion=False,
        subfields = ('key', 'value'),
        subfield_vocabularies = {'key':'additionalFields',},  
        innerJoin = ': ',
        outerJoin = '<br />',
        widget=RecordsWidget(
                i18n_domain = "cmfbibliographyat",
                label = u"Additional Fields",
                condition="object/allowAdditionalFields",
                ),
        ),
    ), marshall = BibtexMarshaller())

