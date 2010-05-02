##########################################################################
#                                                                        #
#           copyright (c) 2003 ITB, Humboldt-University Berlin           #
#           written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                        #
##########################################################################

"""Book reference class"""

from types import StringTypes

from zope.interface import implements
from Products.CMFBibliographyAT.interface import IBookReference

from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions \
     import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName

from Products.CMFBibliographyAT.config import CMFBAT_USES_LINGUAPLONE
if CMFBAT_USES_LINGUAPLONE:
    from Products.LinguaPlone.public import Schema
    from Products.LinguaPlone.public import StringField
    from Products.LinguaPlone.public import StringWidget
else:
    from Products.Archetypes.public import Schema
    from Products.Archetypes.public import StringField
    from Products.Archetypes.public import StringWidget

from Products.ATContentTypes.content.base import registerATCT as registerType
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from Products.CMFBibliographyAT.content.base import BaseEntry
from Products.CMFBibliographyAT.config import PROJECTNAME
from Products.CMFBibliographyAT.content.schemata \
    import HeaderSchema, AuthorSchema, CoreSchema, TrailingSchema
from Products.CMFBibliographyAT.content.fields \
    import publisherField, addressField, editionField, volumeField, \
           numberField, seriesField, editor_flagField, isbnField


AuthorTrailingSchema = Schema((
    editor_flagField,
    ))

SourceSchema = Schema((
    publisherField,
    addressField,
    editionField,
    volumeField,
    numberField,
    seriesField,
    isbnField,
))
BookSchema = HeaderSchema.copy() + AuthorSchema.copy() + AuthorTrailingSchema.copy() + \
             CoreSchema.copy() + SourceSchema.copy() + TrailingSchema.copy()
BookSchema.get('authors').required = 1
BookSchema.get('publication_year').required = 1
BookSchema.get('publisher').required = 1

# the default AT 'description' field shall be invisible, it is kept in 
# sync with the 'abstract' field
BookSchema.get('description').widget.visible = {'view': 'invisible',
                                                'edit': 'invisible', }

finalizeATCTSchema(BookSchema)


class BookReference(BaseEntry):
    """ content type to make reference to a book.
    """

    implements(IBookReference)
    __implements__ = (BaseEntry.__implements__,)

    archetype_name = "Book Reference"
    source_fields = ('publisher', 'address', 'edition',
                     'volume', 'number', 'isbn',)

    security = ClassSecurityInfo()

    schema = BookSchema

    security.declareProtected(View, 'pre_validate')
    def pre_validate(self, REQUEST, errors):

        amazon_tool = getToolByName(self, 'amazon_tool', None)
        if (self.ISBN() or (REQUEST.form.has_key('isbn') and REQUEST.form['isbn'])) and ((self.Authors() == 'No names specified') and not self.Title()) and amazon_tool and amazon_tool.hasValidLicenseKey():

            self.Schema()['isbn'].set(self, value=REQUEST.form['isbn'])
            self.setDetailsFromISBN(is_new_object=True)

            # for BaseEntry.pre_validate we need at least authors 
            # in REQUEST.form
            REQUEST.form['authors'] = self.Schema()['authors']._to_dict(self.Schema()['authors'].get(self) )

            # to ship around required schema fields we need these
            # as well (especially on BookReference creation)
            REQUEST.form['publication_year'] = self.getPublication_year()
            REQUEST.form['publication_month'] = self.getPublication_month()
            REQUEST.form['title'] = self.Title()
            REQUEST.form['publisher'] = self.getPublisher()

        BaseEntry.pre_validate(self, REQUEST, errors)

    security.declareProtected(View, 'Source')
    def Source(self):
        """ the default book source format
        """
        try:

            return self.BookSource()

        except AttributeError:

            bs_tool = getToolByName(self, 'portal_bibliostyles', None)

            publisher = self.getPublisher()
            address   = self.getAddress()
            edition   = self.getEdition()
            volume    = self.getVolume()
            number    = self.getNumber()
            series    = self.getSeries()
            isbn      = self.getIsbn()

            source = publisher
            if address: source += ', %s' % address
            if volume:
                source += ', vol. %s' % volume
                if number: source += '(%s)' % number

            if edition:
                if bs_tool:
                    source += ', %s' % bs_tool.formatEdition(edition,
                                                             abbreviate=True)
                else:
                    source += ',  %s ed.' % edition
            if source and (source[-1] != '.'):
                source += '.'
            if series: source += ' %s.' % series
            if isbn: source += ' (ISBN: %s).' % isbn

            if source and (source[-1] not in '.!?'):
                source += '.'

            return source

    security.declareProtected(View, 'ISBN')
    def ISBN(self):
        """ the ISBN number
        """
        return self.getIsbn()

    security.declareProtected(ModifyPortalContent, 'setDetailsFromISBN')
    def setDetailsFromISBN(self, isbn=None, is_new_object=False, REQUEST=None):
        """ Get details from Amazon using the AmazonTool.
            If isbn == None, try to use the asin (isbn) already on the object.
        """
        atool = getToolByName(self, 'amazon_tool')
        if isbn is None:
            isbn = self.getIsbn()
        if not isbn:
            raise Exception('Bad ISBN')
        result = atool.searchByASIN(asin=isbn, locale='us')[0]
        self.setTitle(result.ProductName)
        # result.Authors can look like:
        #   u'Joseph S. Nye' or
        #   [u'Peter A. Hall', u'David W. Soskice']
        authors = []
        if isinstance(result.Authors, StringTypes):
            result.Authors = [result.Authors]
        for each in result.Authors:
            author = {}
            l = each.split(' ')
            author['firstname'] = l[0]
            if len(l) == 3:
                author['middlename'] = l[1]
                author['lastname'] = l[2]
            else:
                author['middlename'] = ''
                author['lastname'] = l[1]
            authors.append(author)
        self.setAuthors(authors)
        # result.ReleaseDate looks like:
        #   u'01 December, 2001' or
        #   u'May, 2004'
        l = result.ReleaseDate.split(', ')
        year = l[1]
        if len(l) >= 2:
            month = l[0].split(' ')[1]
        else:
            month = l[0]
        self.setPublication_year(year)
        self.setPublication_month(month)
        self.setPublisher(result.Manufacturer)
        if not is_new_object:
            self.reindexObject()

        if REQUEST is not None:
            self.REQUEST.RESPONSE.redirect(self.absolute_url())

    security.declareProtected(View, 'getCoinsDict')
    def getCoinsDict(self):
        """ Select which values to display in the COinS tag for this item """
        coinsData = BaseEntry.getCoinsDict(self)
        coinsData['rft.pub'] = self.getPublisher()
        coinsData['rft.place'] = self.getAddress()
        coinsData['rft.edition'] = self.getEdition()
        coinsData['rft.series'] = self.getSeries()
        coinsData['rft.genre'] = "book"
        coinsData['rft.btitle'] = self.Title()
        coinsData['rft_val_fmt'] = "info:ofi/fmt:kev:mtx:book"
        return coinsData

registerType(BookReference, PROJECTNAME)
