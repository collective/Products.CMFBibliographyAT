##########################################################################
#                                                                        #
#           copyright (c) 2003 ITB, Humboldt-University Berlin           #
#           written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                        #
##########################################################################

"""Inbook reference main class"""

from zope.interface import implements
from Products.CMFBibliographyAT.interface import IInBookReference

from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View

from Products.CMFBibliographyAT.config import CMFBAT_USES_LINGUAPLONE
if CMFBAT_USES_LINGUAPLONE:
    from Products.LinguaPlone.public import Schema
else:
    from Products.Archetypes.public import Schema

from Products.ATContentTypes.content.base import registerATCT as registerType
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from Products.CMFBibliographyAT.config import PROJECTNAME
from Products.CMFBibliographyAT.content.base import BaseEntry
from Products.CMFBibliographyAT.content.schemata \
    import HeaderSchema, AuthorSchema, CoreSchema, TrailingSchema
from Products.CMFBibliographyAT.content.fields \
    import booktitleField, editorField, publisherField, addressField, \
           editionField, volumeField, seriesField, chapterField, pagesField, isbnField

SourceSchema = Schema((
    booktitleField,
    editorField,
    publisherField,
    addressField,
    editionField,
    volumeField,
    seriesField,
    chapterField,
    pagesField,
    isbnField,
    ))

InbookSchema = HeaderSchema.copy() + AuthorSchema.copy() + CoreSchema.copy() +  \
               SourceSchema.copy() + TrailingSchema.copy()
InbookSchema.get('authors').required = 1
InbookSchema.get('publication_year').required = 1
InbookSchema.get('chapter').required = 1
InbookSchema.get('booktitle').required = 1
InbookSchema.get('pages').required = 1
InbookSchema.get('publisher').required = 1
InbookSchema.get('editor').required = 1

# the default AT 'description' field shall be invisible, it is kept in sync with the 'abstract' field
InbookSchema.get('description').widget.visible = {'view': 'invisible', 'edit': 'invisible', }

finalizeATCTSchema(InbookSchema)

class InbookReference(BaseEntry):
    """ content type to make reference to a part/chapter within a book.
    """

    implements(IInBookReference)


    security = ClassSecurityInfo()
    archetype_name = "Inbook Reference"
    source_fields = ('booktitle', 'editor', 'publisher', 'address', 'edition', 'volume', 'series', 'chapter', 'pages', 'isbn',)

    schema = InbookSchema

    security.declareProtected(View, 'Source')
    def Source(self):
        """ the default 'inbook' source format
        """
        try:

            return self.InbookSource()

        except AttributeError:

            booktitle = self.getBooktitle()
            editor    = self.getEditor()
            publisher = self.getPublisher()
            address   = self.getAddress()
            volume    = self.getVolume()
            chapter   = self.getChapter()
            pages     = self.getPages()
            series    = self.getSeries()
            isbn      = self.getIsbn()

            source = 'In: %s' % booktitle

            if editor: source += ', ed. by %s' % editor
            if publisher: source += '. ' + publisher
            if address: source += ', ' + address
            if volume: source += ', vol. %s' % volume
            if chapter: source += ', chap. %s' % chapter
            if pages: source += ', pp. %s' % pages
            if source and (source[-1] != '.'):
                source += '.'
            if series: source += ' %s.' % series
            if isbn: source += ' (ISBN: %s).' % isbn

            if source and (source[-1] not in '.!?'):
                source += '.'

            return source

    security.declareProtected(View, 'getCoinsDict')
    def getCoinsDict(self):
        """ Select which values to display in the COinS tag for this item """

        coinsData = BaseEntry.getCoinsDict(self)
        coinsData['rft.atitle'] = self.Title()
        coinsData['rft.btitle'] = self.getBooktitle()
        coinsData['rft.pages'] = self.getPages()
        coinsData['rft.genre'] = "bookitem"
        coinsData['rft.pub'] = self.getPublisher()
        coinsData['rft.place'] = self.getAddress()
        coinsData['rft.series'] = self.getSeries()
        coinsData['rft_val_fmt'] = "info:ofi/fmt:kev:mtx:book"

        # Why do we have fields in the superclass that aren't in the subclasses?
        coinsData['rft.edition'] = hasattr(self, 'edition') and self.getEdition() or ""
        coinsData['rft.chapter'] = hasattr(self, 'chapter') and self.getChapter() or ""

        
        return coinsData
        
registerType(InbookReference, PROJECTNAME)
