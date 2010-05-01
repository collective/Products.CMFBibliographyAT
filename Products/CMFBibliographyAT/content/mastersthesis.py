##########################################################################
#                                                                        #
#           copyright (c) 2003 ITB, Humboldt-University Berlin           #
#           written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                        #
##########################################################################

"""Mastersthesis reference main class"""

from zope.interface import implements
from Products.CMFBibliographyAT.interface import IMastersthesisReference

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
    import schoolField, addressField, typeField


SourceSchema = Schema((
    schoolField,
    typeField,
    addressField,
     ))

MastersthesisSchema = HeaderSchema.copy() + AuthorSchema.copy() + CoreSchema.copy() +  \
                      SourceSchema.copy() + TrailingSchema.copy()
MastersthesisSchema.get('authors').required = 1
MastersthesisSchema.get('publication_year').required = 1
MastersthesisSchema.get('school').required = 1

# the default AT 'description' field shall be invisible, it is kept in sync with the 'abstract' field
MastersthesisSchema.get('description').widget.visible = {'view': 'invisible', 'edit': 'invisible', }

finalizeATCTSchema(MastersthesisSchema)


class MastersthesisReference(BaseEntry):
    """ content type to make reference to a masters thesis.
    """

    implements(IMastersthesisReference)


    security = ClassSecurityInfo()
    archetype_name = "Mastersthesis Reference"
    source_fields = ('school', 'address', 'publication_type',)

    schema = MastersthesisSchema

    security.declareProtected(View, 'Source')
    def Source(self):
        """ the default masters thesis source format
        """
        try:

            return self.MastersthesisSource()

        except AttributeError:

            school              = self.getSchool()
            publication_type    = self.getPublication_type()
            address             = self.getAddress()

            if publication_type:
                source = publication_type
            else:
                source = 'Master thesis'
            if school: source += ', %s' % school
            if address: source += ', %s' % address

            return source + '.'

    security.declareProtected(View, 'getCoinsDict')
    def getCoinsDict(self):
        """ Select which values to display in the COinS tag for this item """
        coinsData = BaseEntry.getCoinsDict(self)
        coinsData['rft.aucorp'] = self.getSchool()
        coinsData['rft.genre'] = "document"
        coinsData['rft.btitle'] = self.Title()
        coinsData['rft_val_fmt'] = "info:ofi/fmt:kev:mtx:book"
        return coinsData

registerType(MastersthesisReference, PROJECTNAME)
