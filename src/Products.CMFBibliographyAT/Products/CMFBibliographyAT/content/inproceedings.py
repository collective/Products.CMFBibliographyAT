##########################################################################
#                                                                        #
#           copyright (c) 2003 ITB, Humboldt-University Berlin           #
#           written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                        #
##########################################################################

"""Inproceedings reference main class"""

from zope.interface import implements
from Products.CMFBibliographyAT.interface import IInProceedingsReference

from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName

from Products.CMFBibliographyAT.config import CMFBAT_USES_LINGUAPLONE
if CMFBAT_USES_LINGUAPLONE:
    from Products.LinguaPlone.public import Schema
else:
    from Products.Archetypes.public import Schema

from Products.ATContentTypes.content.base import registerATCT as registerType
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from Products.CMFBibliographyAT.config import PROJECTNAME
from Products.CMFBibliographyAT.content.inbook import InbookReference
from Products.CMFBibliographyAT.content.schemata \
    import HeaderSchema, AuthorSchema, CoreSchema, TrailingSchema
from Products.CMFBibliographyAT.content.fields \
    import booktitleField, editorField, volumeField, numberField, \
           publisherField, organizationField, addressField, \
           editionField, seriesField, chapterField, pagesField, isbnField

SourceSchema = Schema((
   booktitleField,
   editorField,
   volumeField,
   numberField,
   chapterField,
   pagesField,
   publisherField,
   organizationField,
   addressField,
   editionField,
   seriesField,
   isbnField,
))

InproceedingsSchema = HeaderSchema.copy() + AuthorSchema.copy() + CoreSchema.copy() +  \
               SourceSchema.copy() + TrailingSchema.copy()
InproceedingsSchema.get('authors').required = 1
InproceedingsSchema.get('booktitle').required = 1

# the default AT 'description' field shall be invisible, it is kept in sync with the 'abstract' field
InproceedingsSchema.get('description').widget.visible = {'view': 'invisible', 'edit': 'invisible', }

finalizeATCTSchema(InproceedingsSchema)

class InproceedingsReference(InbookReference):
    """ content type to make reference to a chapter within a proceedings volume.
    """

    implements(IInProceedingsReference)
    __implements__ = (InbookReference.__implements__,)

    security = ClassSecurityInfo()
    source_fields = ('booktitle', 'editor', 'volume', 
                     'number',  'chapter', 'pages', 
                     'publisher', 'organization', 'address', 
                     'edition', 'series', 'isbn',)

    archetype_name = "Inproceedings Reference"
    schema = InproceedingsSchema

    security.declareProtected(View, 'Source')
    def Source(self):
        """ the default 'inproceedings' source format
        """
        try:

            return self.InproceedingsSource()

        except AttributeError:

            booktitle        = self.getBooktitle()
            editor           = self.getEditor()
            volume           = self.getVolume()
            number           = self.getNumber()
            chapter          = self.getChapter()
            pages            = self.getPages()
            publisher        = self.getPublisher()
            organization     = self.getOrganization()
            address          = self.getAddress()
            edition          = self.getEdition()
            series           = self.getSeries()
            isbn             = self.getIsbn()

            bs_tool = getToolByName(self, 'portal_bibliostyles', None)

            source = 'In: %s' % booktitle
            if editor: source += ', ed. by %s' % editor
            if volume:
                source += ', vol. %s' % volume
                if number: source += '(%s)' % number
            if chapter: source += ', chap. %s' % chapter
            if pages: source += ', pp. %s' % pages
            if organization: source += ', %s' % organization
            if address: source += ', %s' % address
            if publisher: source += ', %s' % publisher
            if edition:
                if bs_tool:
                    source += ', %s' % bs_tool.formatEdition(edition, abbreviate=True)
                else:
                    source += ',  %s ed.' % edition

            if series: source += '. %s' % series
            if isbn: source += ' (ISBN: %s).' % isbn

            if source and (source[-1] not in '.!?'):
                source += '.'

            return source

    security.declareProtected(View, 'getCoinsDict')
    def getCoinsDict(self):
        """ Select which values to display in the COinS tag for this item """
        coinsData = InbookReference.getCoinsDict(self)
        coinsData['rft.genre'] = "proceeding"
        coinsData['rft.aucorp'] = self.getOrganization()
        return coinsData

registerType(InproceedingsReference, PROJECTNAME)
