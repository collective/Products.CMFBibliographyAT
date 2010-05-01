##########################################################################
#                                                                        #
#           copyright (c) 2003 ITB, Humboldt-University Berlin           #
#           written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                        #
##########################################################################

"""Phdthesis reference main class"""

from zope.interface import implements
from Products.CMFBibliographyAT.interface import IPhdthesisReference

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
    import schoolField, addressField, typeField, isbnField


SourceSchema = Schema((
    typeField,
    schoolField,
    addressField,
    isbnField,
     ))

PhdthesisSchema = HeaderSchema.copy() + AuthorSchema.copy() + CoreSchema.copy() +  \
                  SourceSchema.copy() + TrailingSchema.copy()
PhdthesisSchema.get('authors').required = 1
PhdthesisSchema.get('school').required = 1

# the default AT 'description' field shall be invisible, it is kept in sync with the 'abstract' field
PhdthesisSchema.get('description').widget.visible = {'view': 'invisible', 'edit': 'invisible', }

finalizeATCTSchema(PhdthesisSchema)

class PhdthesisReference(BaseEntry):
    """ content type to make reference to a PhD thesis.
    """

    implements(IPhdthesisReference)


    security = ClassSecurityInfo()
    archetype_name = "Phdthesis Reference"
    source_fields = ('school', 'address', 'publication_type', 'isbn',)

    schema = PhdthesisSchema

    security.declareProtected(View, 'Source')
    def Source(self):
        """ the default source renderer
        """
        try:
            return self.PhdthesisSource()
        except AttributeError:
            publication_type    = self.getPublication_type()
            school              = self.getSchool()
            address             = self.getAddress()
            isbn                = self.getIsbn()

            if publication_type:
                source = publication_type
            else:
                source = 'PhD thesis'
            if school: source += ', %s' % school
            if address: source += ', %s' % address
            if source and (source[-1] != '.'):
                source += '.'
            if isbn: source += ' (ISBN: %s).' % isbn

            if source and (source[-1] not in '.!?'):
                source += '.'

            return source

    security.declareProtected(View, 'getCoinsDict')
    def getCoinsDict(self):
        """ Select which values to display in the COinS tag for this item """
        coinsData = BaseEntry.getCoinsDict(self)
        coinsData['rft.aucorp'] = self.getSchool()
        coinsData['rft.genre'] = "document"
        coinsData['rft.btitle'] = self.Title()
        coinsData['rft_val_fmt'] = "info:ofi/fmt:kev:mtx:book"
        return coinsData

registerType(PhdthesisReference, PROJECTNAME)
