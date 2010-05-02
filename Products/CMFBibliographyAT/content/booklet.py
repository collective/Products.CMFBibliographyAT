##########################################################################
#                                                                        #
#           copyright (c) 2003 ITB, Humboldt-University Berlin           #
#           written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                        #
##########################################################################

"""Booklet reference class"""

from zope.interface import implements
from Products.CMFBibliographyAT.interface import IBookletReference

from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View

from Products.CMFBibliographyAT.config import CMFBAT_USES_LINGUAPLONE
if CMFBAT_USES_LINGUAPLONE:
    from Products.LinguaPlone.public import Schema
else:
    from Products.Archetypes.public import Schema

from Products.ATContentTypes.content.base import registerATCT as registerType
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from Products.CMFBibliographyAT.content.base import BaseEntry
from Products.CMFBibliographyAT.config import PROJECTNAME
from Products.CMFBibliographyAT.content.schemata \
    import HeaderSchema, AuthorSchema, CoreSchema, TrailingSchema
from Products.CMFBibliographyAT.content.fields import howpublishedField


howpublishedspecificField = howpublishedField.copy()
howpublishedspecificField.default = 'Booklet'
SourceSchema = Schema((
    howpublishedspecificField,
    ))
BookletSchema = HeaderSchema.copy() + AuthorSchema.copy() + CoreSchema.copy() +  \
                SourceSchema.copy() + TrailingSchema.copy()
BookletSchema.get('authors').required = 0
# normally the publication_year for BookletReferences is optional, but
# in CMFBAT we better force the user to enter something here (better not
# irritate portal_catalog...).
BookletSchema.get('publication_year').required = 1

# the default AT 'description' field shall be invisible, it is kept in sync with the 'abstract' field
BookletSchema.get('description').widget.visible = {'view': 'invisible', 'edit': 'invisible', }

finalizeATCTSchema(BookletSchema)

class BookletReference(BaseEntry):
    """ content type to make reference to a booklet (a book without publisher).
    """

    implements(IBookletReference)


    security = ClassSecurityInfo()
    archetype_name = "Booklet Reference"
    source_fields = ('howpublished',)

    schema = BookletSchema

    security.declareProtected(View, 'Source')
    def Source(self):
        """ the default booklet source format
        """
        try:
            return self.BookletSource()

        except AttributeError:
            howpublished = self.getHowpublished()
            source = 'Booklet'
            if howpublished: source += ', %s' % howpublished
            return source + '.'

    security.declareProtected(View, 'getCoinsDict')
    def getCoinsDict(self):
        """ Select which values to display in the COinS tag for this item """
        coinsData = BaseEntry.getCoinsDict(self)
        coinsData['rft.genre'] = "book"
        coinsData['rft.btitle'] = self.Title()
        coinsData['rft_val_fmt'] = "info:ofi/fmt:kev:mtx:book"
        return coinsData
        
registerType(BookletReference, PROJECTNAME)
