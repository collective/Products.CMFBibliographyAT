##########################################################################
#                                                                        #
#           copyright (c) 2003 ITB, Humboldt-University Berlin           #
#           written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                        #
##########################################################################

"""Webpublished reference main class"""

from zope.interface import implements
from Products.CMFBibliographyAT.interface import IWebpublishedReference

from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View

from Products.CMFBibliographyAT.config import CMFBAT_USES_LINGUAPLONE

from Products.ATContentTypes.content.base import registerATCT as registerType
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from Products.CMFBibliographyAT.config import PROJECTNAME
from Products.CMFBibliographyAT.content.base import BaseEntry, BaseEntrySchema

WebpublishedSchema = BaseEntrySchema.copy()
WebpublishedSchema.get('authors').required = 0

# the default AT 'description' field shall be invisible, 
# it is kept in sync with the 'abstract' field
WebpublishedSchema.get('description').widget.visible = {'view': 'invisible',
                                                        'edit': 'invisible', }

finalizeATCTSchema(WebpublishedSchema)

class WebpublishedReference(BaseEntry):
    """Content type to make reference to a webpublished (only) document.
    """


    implements(IWebpublishedReference)

    archetype_name = "Webpublished Reference"
    schema = WebpublishedSchema
    security = ClassSecurityInfo()

    security.declareProtected(View, 'Source')
    def Source(self):
        """ the default webpublished source format
        """
        try:

            return self.BookSource()

        except AttributeError:

            url = self.getPublication_url()

            source = 'Webpublished'
            if url: source += ', %s' % url
            if source and (source[-1] not in  '.!?'):
                source += '.'

            return source

    security.declareProtected(View, 'getCoinsDict')
    def getCoinsDict(self):
        """ Select which values to display in the COinS tag for this item """
        coinsData = BaseEntry.getCoinsDict(self)
        coinsData['rft.genre'] = "document"
        coinsData['rft.btitle'] = self.Title()
        coinsData['rft_val_fmt'] = "info:ofi/fmt:kev:mtx:book"
        return coinsData

registerType(WebpublishedReference, PROJECTNAME)
