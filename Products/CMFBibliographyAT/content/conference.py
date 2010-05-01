
##########################################################################
#                                                                        #
#           copyright (c) 2003 ITB, Humboldt-University Berlin           #
#           written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                        #
##########################################################################

"""Conference (proceedings) reference class"""

from zope.interface import implements
from Products.CMFBibliographyAT.interface import IConferenceReference

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
from Products.CMFBibliographyAT.content.inbook import InbookReference
from Products.CMFBibliographyAT.content.schemata \
    import HeaderSchema, AuthorSchema, CoreSchema, TrailingSchema
from Products.CMFBibliographyAT.content.fields \
    import booktitleField, volumeField, numberField, \
           publisherField, organizationField, addressField, \
           seriesField, pagesField

SourceSchema = Schema((
   booktitleField,
   volumeField,
   numberField,
   seriesField,
   pagesField,
   addressField,
   organizationField,
   publisherField,
))

ConferenceSchema = HeaderSchema.copy() + AuthorSchema.copy() + CoreSchema.copy() +  \
               SourceSchema.copy() + TrailingSchema.copy()
ConferenceSchema.get('authors').required = 1
ConferenceSchema.get('booktitle').required = 1

# the default AT 'description' field shall be invisible, it is kept in sync with the 'abstract' field
ConferenceSchema.get('description').widget.visible = {'view': 'invisible', 'edit': 'invisible', }

finalizeATCTSchema(ConferenceSchema)

class ConferenceReference(InbookReference):
    """ content type to make reference to a conference volume.
    """

    implements(IConferenceReference)
    __implements__ = (InbookReference.__implements__,)

    security = ClassSecurityInfo()
    source_fields = ('booktitle', 'volume', 'number',  'series', 'pages', 'address', 'organization', 'publisher',  )

    archetype_name = "Conference Reference"
    schema = ConferenceSchema

    security.declareProtected(View, 'Source')
    def Source(self):
        """ the default 'conference' source format
        """
        try:

            return self.ConferenceSource()

        except AttributeError:

            booktitle        = self.getBooktitle()
            volume           = self.getVolume()
            number           = self.getNumber()
            series           = self.getSeries()
            pages            = self.getPages()
            address          = self.getAddress()
            organization     = self.getOrganization()
            publisher        = self.getPublisher()

            source = 'In: %s' % booktitle
            if volume:
                source += ', vol. %s' % volume
                if number: source += '(%s)' % number
            if pages: source += ', pp. %s' % pages
            if address: source += ', ' + address
            if organization: source += ', %s' % organization
            if publisher: source += ', %s' % publisher
            if series: source += '. %s' % series

            return source + '.'

    security.declareProtected(View, 'getCoinsDict')
    def getCoinsDict(self):
        """ Select which values to display in the COinS tag for this item """
        coinsData = InbookReference.getCoinsDict(self)
        coinsData['rft.aucorp'] = self.getOrganization()
        coinsData['rft.genre'] = "conference"
        return coinsData
        
registerType(ConferenceReference, PROJECTNAME)
