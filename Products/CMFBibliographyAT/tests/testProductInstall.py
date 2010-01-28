##################################################
#                                                #
#    Copyright (C), 2004, Raphael Ritz           #
#    <r.ritz@biologie.hu-berlin.de>              #
#                                                #
#    Humboldt University Berlin                  #
#                                                #
##################################################

import os, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from zope.component import getUtility

from Testing import ZopeTestCase

from Products.CMFPlone.tests import PloneTestCase

from bibliograph.rendering.interfaces import IBibliographyRenderer
from bibliograph.rendering.utility import BibtexRenderer
from bibliograph.parsing.interfaces import IBibliographyParser
from bibliograph.parsing.parsers.bibtex import BibtexParser
from bibliograph.parsing.parsers.medline import MedlineParser

from Products.CMFBibliographyAT.tests import setup


class TestCMFBibliographyATInstall(PloneTestCase.PloneTestCase):
    '''Test the CMFBibliographyAT installation'''

    def afterSetUp(self):
        pass

    # the individual tests

    def testSkinInstallation(self):
        st = self.portal.portal_skins
        self.failUnless('bibliography' in st.objectIds())

    def testToolInstalltion(self):
        root = self.portal
        self.failUnless('portal_bibliography' in root.objectIds())

    def testBibtexParserInstallation(self):
        parser = getUtility(IBibliographyParser, name='bibtex')
        self.failUnless(isinstance(parser, BibtexParser))

    def testMedlineParserInstallation(self):
        parser = getUtility(IBibliographyParser, name='medline')
        self.failUnless(isinstance(parser, MedlineParser))

    def testBibtexRendererInstallation(self):
        util = getUtility(IBibliographyRenderer, name='bibtex')
        self.failUnless(isinstance(util, BibtexRenderer))


    def testBibFolderInstallation(self):
        ttool = self.portal.portal_types
        self.failUnless('BibliographyFolder' in ttool.objectIds())

    def testReferenceTypesInstallation(self):
        ttool = self.portal.portal_types
        # first check all listed in config
        from Products.CMFBibliographyAT.config import REFERENCE_TYPES
        for reftype in REFERENCE_TYPES:
            self.failUnless(reftype in ttool.objectIds(),
                            '%s not installed' % reftype)
        # to double check do also explicit tests
        reftypes = ['ArticleReference',
                    'BookReference',
                    'BookletReference',
                    'InbookReference',
                    'IncollectionReference',
                    'InproceedingsReference',
                    'ManualReference',
                    'MastersthesisReference',
                    'MiscReference',
                    'PhdthesisReference',
                    'PreprintReference',
                    'ProceedingsReference',
                    'TechreportReference',
                    'UnpublishedReference',
                    'WebpublishedReference',
                    ]
        for reftype in reftypes:
            self.failUnless(reftype in ttool.objectIds(),
                            '%s not installed' % reftype)


    def testCatalogExtensions(self):
        ctool = self.portal.portal_catalog

        newFieldIndexes = ['Authors', 'publication_year']
        newSchemaEntries = ['Authors', 'publication_year', 'Source']

        for idx in newFieldIndexes:
            self.failUnless(idx in ctool.indexes())

        for entry in newSchemaEntries:
            self.failUnless(entry in ctool.schema())

## rr: obsolte in CMF-2.0; custom tools must not be action providers
##     def testActionProvider(self):
##         atool = self.portal.portal_actions
##         self.failUnless('portal_bibliography' \
##                         in atool.listActionProviders())

    def testBibliographyViewAction(self):
        acttool = self.portal.portal_actions
        action_ids = [a.id for a in acttool.listActions()]
        self.failUnless('bibliography_search' in action_ids)

    def testExistencePropertySheet(self):
        pp = self.portal.portal_properties
        self.assertEqual('cmfbibat_properties' in pp.objectIds(), True)

    def testDefaultValuesInPropertySheet(self):
        bib_tool = self.portal.portal_bibliography
        self.assertEqual(bib_tool.getSheetProperty('BibTeX', 'parser_enabled'), True)
        self.assertEqual(bib_tool.getSheetProperty('BibTeX', 'renderer_enabled'), True)

    # end of the individual tests

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCMFBibliographyATInstall))
    return suite

if __name__ == '__main__':
    framework()
