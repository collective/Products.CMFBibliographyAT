##########################################################################
#                                                                        #
#           copyright (c) 2003 ITB, Humboldt-University Berlin           #
#           written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                        #
##########################################################################

"""Manual reference class"""

from zope.interface import implements
from Products.CMFBibliographyAT.interface import IManualReference

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
from Products.CMFBibliographyAT.content.base import BaseEntry
from Products.CMFBibliographyAT.content.schemata \
    import HeaderSchema, AuthorSchema, CoreSchema, TrailingSchema
from Products.CMFBibliographyAT.content.fields \
    import organizationField, addressField, editionField, isbnField


SourceSchema = Schema((
    organizationField,
    addressField,
    editionField,
    isbnField,
     ))

ManualSchema = HeaderSchema.copy() + AuthorSchema.copy() + CoreSchema.copy() +  \
               SourceSchema.copy() + TrailingSchema.copy()
ManualSchema.get('authors').required = 0
# normally the publication_year for ManualReferences is optional, but
# in CMFBAT we better force the user to enter something here (better not
# irritate portal_catalog...).
ManualSchema.get('publication_year').required = 1

# the default AT 'description' field shall be invisible, it is kept in sync with the 'abstract' field
ManualSchema.get('description').widget.visible = {'view': 'invisible', 'edit': 'invisible', }

finalizeATCTSchema(ManualSchema)

class ManualReference(BaseEntry):
    """ content type to make reference to a manual.
    """

    implements(IManualReference)


    archetype_name = "Manual Reference"
    source_fields = ('organization', 'address', 'edition', 'isbn',)
    security = ClassSecurityInfo()
    schema = ManualSchema

    security.declareProtected(View, 'Source')
    def Source(self):
        """ the default manual source format
        """
        try:

            return self.ManualSource()

        except AttributeError:

            bs_tool = getToolByName(self, 'portal_bibliostyles', None)
            address = self.getAddress()
            edition = self.getEdition()
            isbn    = self.getIsbn()

            source = ''
            if address:
                source += '%s' % address
                if edition: source += ', '
            if edition:
                if bs_tool: source += '%s' % bs_tool.formatEdition(edition, abbreviate=True)
                else: source += '%s ed.' % edition
            if source and (source[-1] != '.'):
                source += '.'
            if isbn: source += ' (ISBN: %s).' % isbn

            if source and (source[-1] not in '.!?'): source += '.'

            return source

    security.declareProtected(View, 'getCoinsDict')
    def getCoinsDict(self):
        """ Select which values to display in the COinS tag for this item """
        coinsData = BaseEntry.getCoinsDict(self)
        coinsData['rft.edition'] = self.getEdition()
        coinsData['rft.aucorp'] = self.getOrganization()
        coinsData['rft.genre'] = "document"
        coinsData['rft.btitle'] = self.Title()
        coinsData['rft_val_fmt'] = "info:ofi/fmt:kev:mtx:book"
        return coinsData
        
registerType(ManualReference, PROJECTNAME)
