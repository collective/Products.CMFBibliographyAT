##########################################################################
#                                                                        #
#           copyright (c) 2003 ITB, Humboldt-University Berlin           #
#           written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                        #
##########################################################################

"""Unpublished reference class"""

from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View

from Products.CMFBibliographyAT.interface import IUnpublishedReference

from Products.CMFBibliographyAT.config import CMFBAT_USES_LINGUAPLONE

from Products.ATContentTypes.content.base import registerATCT as registerType
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from Products.CMFBibliographyAT.config import PROJECTNAME
from Products.CMFBibliographyAT.content.base import BaseEntry, BaseEntrySchema

UnpublishedSchema = BaseEntrySchema.copy()
UnpublishedSchema.get('authors').required = 1
# YES!!! note is a required field for UnpublishedReferences!!!
UnpublishedSchema.get('note').required = 1
# normally the publication_year for UnpublishedReferences is optional, but
# in CMFBAT we better force the user to enter something here (better not
# irritate portal_catalog...).
UnpublishedSchema.get('publication_year').required = 1

# the default AT 'description' field shall be invisible, it is kept in sync with the 'abstract' field
UnpublishedSchema.get('description').widget.visible = {'view': 'invisible', 'edit': 'invisible', }

finalizeATCTSchema(UnpublishedSchema)


class UnpublishedReference(BaseEntry):
    """Content type to make reference to a unpublished document.
    """

    implements(IUnpublishedReference)
    __implements__ = (BaseEntry.__implements__,)

    archetype_name = "Unpublished Reference"
    security = ClassSecurityInfo()

    schema = UnpublishedSchema

    security.declareProtected(View, 'getCoinsDict')
    def getCoinsDict(self):
        """ Select which values to display in the COinS tag for this item """
        coinsData = BaseEntry.getCoinsDict(self)
        coinsData['rft.genre'] = "document"
        coinsData['rft.btitle'] = self.Title()
        coinsData['rft_val_fmt'] = "info:ofi/fmt:kev:mtx:book"
        return coinsData

registerType(UnpublishedReference, PROJECTNAME)
