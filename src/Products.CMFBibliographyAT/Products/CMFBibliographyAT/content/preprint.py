##########################################################################
#                                                                        #
#           copyright (c) 2003 ITB, Humboldt-University Berlin           #
#           written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                        #
##########################################################################

"""Preprint reference main class"""

from zope.interface import implements
from Products.CMFBibliographyAT.interface import IPreprintReference

from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName

from Products.CMFBibliographyAT.config import CMFBAT_USES_LINGUAPLONE
if CMFBAT_USES_LINGUAPLONE:
    from Products.LinguaPlone.public import Schema
    from Products.LinguaPlone.public import StringField, SelectionWidget
    from Products.LinguaPlone.public import DisplayList
else:
    from Products.Archetypes.public import Schema
    from Products.Archetypes.public import StringField, SelectionWidget
    from Products.Archetypes.public import DisplayList

from Products.ATContentTypes.content.base import registerATCT as registerType
from Products.ATContentTypes.content.schemata import finalizeATCTSchema


from Products.CMFBibliographyAT.config import PROJECTNAME
from Products.CMFBibliographyAT.content.base import BaseEntry
from Products.CMFBibliographyAT.content.schemata \
    import HeaderSchema, AuthorSchema, CoreSchema, TrailingSchema


SourceSchema = Schema((
    StringField('preprint_server',
        searchable=1,
        required=0,
        vocabulary="PreprintServers",
        widget=SelectionWidget(label="Preprint server",
                label_msgid="label_preprint_server",
                description="If the preprint is available from one of the following preprint servers, you can indicate that here. Contact the site's admin if you want a server to be added to the list.",
                description_msgid="help_preprint_server",
                i18n_domain="cmfbibliographyat",),
                ),
    ))

PreprintSchema = HeaderSchema.copy() + AuthorSchema.copy() + CoreSchema.copy() +  \
                 SourceSchema.copy() + TrailingSchema.copy()

# the default AT 'description' field shall be invisible, it is kept in sync with the 'abstract' field
PreprintSchema.get('description').widget.visible = {'view': 'invisible', 'edit': 'invisible', }

finalizeATCTSchema(PreprintSchema)

class PreprintReference(BaseEntry):
    """ content type to make reference to a preprint
    """

    implements(IPreprintReference)
    __implements__ = (BaseEntry.__implements__,)

    security = ClassSecurityInfo()
    archetype_name = "Preprint Reference"
    source_fields = ('preprint_server', )

    schema = PreprintSchema

    security.declareProtected(View, 'PreprintServers')
    def PreprintServers(self):
        """ return a display list of the preprint servers as
            defined in the tool properties.
        """
        bib_tool = getToolByName(self, 'portal_bibliography')
        servers = bib_tool.getProperty('preprint_servers', [])
        values = []
        for server in servers:
            if ':' in server:
                text = server.split(':')[0]
            else:
                text = server
            values.append([server, text])
        return DisplayList(tuple(values))

    security.declareProtected(View, 'Source')
    def Source(self):
        """ the default preprint server source format
        """
        try:
            return self.PreprintSource()
        except AttributeError:
            source = "Preprint"
            preprint_server = self.getPreprint_server()
            if preprint_server:
                if ':' in preprint_server:
                    text, link = preprint_server.split(':', 1)
                    if text != 'None':
                        source += ' at <a href="%s">%s</a>' % (link, text)
                else:
                    source += " at %s" % preprint_server
            return source + "."

    security.declareProtected(View, 'getCoinsDict')
    def getCoinsDict(self):
        """ Select which values to display in the COinS tag for this item """
        coinsData = BaseEntry.getCoinsDict(self)
        coinsData['rft.genre'] = "document"
        coinsData['rft.btitle'] = self.Title()
        coinsData['rft_val_fmt'] = "info:ofi/fmt:kev:mtx:book"
        return coinsData

registerType(PreprintReference, PROJECTNAME)
