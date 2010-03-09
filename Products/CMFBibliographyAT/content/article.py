##########################################################################
#                                                                        #
#           copyright (c) 2003, 2005 ITB, Humboldt-University Berlin     #
#           written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                        #
##########################################################################

"""Article reference class"""

from zope.interface import implements
from Products.CMFBibliographyAT.interface import IArticleReference

from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View, ModifyPortalContent

from Products.CMFBibliographyAT.config import CMFBAT_USES_LINGUAPLONE
if CMFBAT_USES_LINGUAPLONE:
    from Products.LinguaPlone.public import Schema
    from Products.LinguaPlone.public import StringField, StringWidget
else:
    from Products.Archetypes.public import Schema
    from Products.Archetypes.public import StringField, StringWidget

from Products.ATContentTypes.content.base import registerATCT as registerType
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from Products.CMFBibliographyAT.config import PROJECTNAME
from Products.CMFBibliographyAT.content.base import BaseEntry
from Products.CMFBibliographyAT.content.schemata \
    import HeaderSchema, AuthorSchema, CoreSchema, TrailingSchema
from Products.CMFBibliographyAT.content.fields \
    import journalField, volumeField, numberField, pagesField


SourceSchema = Schema((
    journalField,
    volumeField,
    numberField,
    pagesField,
    StringField('pmid',
        is_duplicates_criterion=True,
        widget=StringWidget(label="PubMed ID",
            label_msgid="label_pmid",
            description="The reference's number in the PubMed database.",
            description_msgid="help_pmid",
            i18n_domain="cmfbibliographyat",
            visible = {'view': 'invisible',
                       'edit': 'invisible', }
        ),
    ),
    StringField('DOI',
        is_duplicates_criterion=True,
        widget=StringWidget(label="DOI",
            label_msgid="label_doi",
            description="The reference's digital object identifier.",
            description_msgid="help_doi",
            i18n_domain="cmfbibliographyat",
            visible = {'view': 'invisible',
                       'edit': 'invisible', }
        ),
    ),
))

ArticleSchema = HeaderSchema.copy() + \
                AuthorSchema.copy() + CoreSchema.copy() +  \
                SourceSchema.copy() + TrailingSchema.copy()

ArticleSchema.get('authors').required = 1
ArticleSchema.get('publication_year').required = 1
ArticleSchema.get('journal').required = 1

# the default AT 'description' field shall be invisible, 
# it is kept in sync with the 'abstract' field
ArticleSchema.get('description').widget.visible = {'view': 'invisible',
                                                   'edit': 'invisible', }

finalizeATCTSchema(ArticleSchema)

class ArticleReference(BaseEntry):
    """ content type to make reference to a (scientific) article.
    """

    implements(IArticleReference)
    __implements__ = (BaseEntry.__implements__,)

    security = ClassSecurityInfo()
    archetype_name = "Article Reference"
    source_fields = ('journal', 'volume', 'number', 'pages', 'PMID',)

    schema = ArticleSchema

    security.declareProtected(View, 'PMID')
    def PMID(self):
        """ returns the pmid if set
        """
        value = None
        ids = self.getIdentifiers()
        for id in ids:
            if id.get('label') == 'PMID':
                value = id['value']
        return value or self.getPmid() ## BBB


    security.declareProtected(View, 'getPubMedLink')
    def getPubMedLink(self, defaultURL=None):
        """ a link to PubMed
            if pmid is set or the default otherwise
        """
        pmid = self.PMID()
        if pmid:
            url = "http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve"
            return url + "&db=PubMed&list_uids=%s" % pmid
        else:
            return defaultURL

    security.declareProtected(ModifyPortalContent, 'setPmid')
    def setPmid(self, value, **kw):
        """Set the PMID in such a way that the new and the old way
           of handling PMIDs are supported.
        """
        self._setIdentifier('PMID', value, **kw)

    security.declareProtected(ModifyPortalContent, 'setDOI')
    def setDOI(self, value, **kw):
        """Set the DOI in such a way that the new and the old way
           of handling DOIs are supported.
        """
        self._setIdentifier('DOI', value, **kw)

    security.declarePrivate('_setIdentifier')
    def _setIdentifier(self, label, value, **kw):
        ## this is needed for the imports
        ids = self.getIdentifiers()
        updated = False
        for id in ids:
            if id.get('label') == label:
                id['value'] = value
                updated = True
        if not updated:
            ids.append(dict(label=label, value=value))
        self.setIdentifiers(ids, **kw)

    security.declareProtected(View, 'Source')
    def Source(self):
        """ the default article source format
        """
        try:
            return self.ArticleSource()
        except AttributeError:
            journal = self.getJournal()
            volume  = self.getVolume()
            number  = self.getNumber()
            pages   = self.getPages()
            source = ''
            if journal:
                source += journal
            if volume:
                source += ', %s' % volume
            if number:
                source += '(%s)' % number
            if pages:
                source += ':%s' % pages
            return source + '.'


    security.declareProtected(View, 'getCoinsDict')
    def getCoinsDict(self):
        """ Select which values to display in the COinS tag for this item """
        coinsData = BaseEntry.getCoinsDict(self)
        coinsData['rft.part'] = self.getNumber()
        coinsData['rft.volume'] = self.getVolume()
        coinsData['rft.pages'] = self.getPages()
        coinsData['rft.genre'] = "article"
        coinsData['rft.atitle'] = self.Title()
        coinsData['rft.title'] = self.getJournal()
        coinsData['rft.jtitle'] = self.getJournal()

        coinsData['rft_val_fmt'] = "info:ofi/fmt:kev:mtx:journal"
        return coinsData

registerType(ArticleReference, PROJECTNAME)
