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

from zope.interface import verify
from zope.interface.common.mapping import IIterableMapping

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFCore.utils import getToolByName

from bibliograph.core.interfaces import IBibliography

from Products.CMFBibliographyAT.tests import setup
from Products.CMFBibliographyAT import testing

class TestBibliographyFolder(PloneTestCase.PloneTestCase):
    '''Test the BibliographyFolder'''

    layer = testing.emptyBibFolder

    # some utility methods

    def getPopulatedBibFolder(self,
                              source_file=setup.MEDLINE_TEST_MED,
                              format="med"):
        bf = self.folder.bib_folder
        source = open(source_file, 'r').read()
        bf.processImport(source, 'source.%s' % format)
        return bf

    # the individual tests

    def test_FolderCreation(self):
        uf = self.folder
        uf.invokeFactory(type_name = "BibliographyFolder",
                         id = 'test_folder')
        self.failUnless('test_folder' in uf.contentIds())

    def test_MedlineImport(self):
        bf = self.folder.bib_folder
        med_source = open(setup.MEDLINE_TEST_MED, 'r').read()
        bf.processImport(med_source, 'medline_test.med')
        expected_ids = ['GrootEtAl2003',
                        'AlibardiThompson2003',
                        'CokeEtAl2003',
                        'TrapeMane2002']
        for id in expected_ids:
            self.failUnless(id in bf.contentIds(),
                            'Importing %s failed.' % id)

    def test_BibtexImport(self):
        bf = self.folder.bib_folder
        bib_source = open(setup.BIBTEX_TEST_BIB, 'r').read()
        bf.processImport(bib_source, 'bibtex_test.bib')
        expected_ids = ['Lutz2001',
                        'Lattier2001',
                        'McKay2003']
        for id in expected_ids:
            self.failUnless(id in bf.contentIds(),
                            'Importing %s failed.' % id)
        # Test the annote handling
        self.failUnless(bf['McKay2003'].getAnnote() == 'I really like it.')

    def test_BibtexExport(self):
        bf = self.getPopulatedBibFolder()
        bib_source = bf.restrictedTraverse('@@export').export(format='BibTeX').strip()
        expected_source = open(setup.MEDLINE_TEST_BIB, 'r').read().strip()
        # split bibtex files by-line and compare them as lists (ignoring empty lines)
        l1 = bib_source.splitlines(1)
        l1 = [l.strip() for l in l1 if l.strip()]
        l2 = expected_source.splitlines(1)
        l2 = [l.strip() for l in l2 if l.strip()]
        self.assertEqual(l1, l2)
        return
    def test_BibtexExportCiteKeys(self):
        bf = self.getPopulatedBibFolder(setup.BIBTEX_TEST_CITE_KEY, 'bib')
        #bib_source = bf.bibliography_export(format='BibTeX').strip()
        bib_source = bf.restrictedTraverse('@@export').export(format='BibTeX').strip()
        #expected_source = open(setup.BIBTEX_TEST_CITE_KEY, 'r').read().strip()
        self.failUnless(bib_source.startswith('@Book{Esping-Andersen1985'))

    # for the folder defaults
    def test_AuthorURLs(self):
        bf = self.folder.bib_folder
        link_list = [{'key':'foo',
                      'value':'foos_home'},
                     {'key':'bar',
                      'value':'bars_home'}]
        bf.processAuthorUrlList(link_list)
        self.assertEqual(bf.AuthorURLs()['foo'], 'foos_home')
        self.assertEqual(bf.AuthorURLs()['bar'], 'bars_home')

    def test_processImportReturnsObjects(self):
        bf = self.folder.bib_folder
        med_source = open(setup.MEDLINE_TEST_MED, 'r').read()
        result = bf.processImport(med_source,
                                  'medline_test.med',
                                  return_obs=True,
                                  )
        self.assertEqual(len(result), 4)

    def test_cookId(self):
        bf = self.folder.bib_folder
        ref_dict1 = {'authors' : [ {'lastname'  : 'Hicks',
                                    'firstname' : 'Tim',
                                    'middlename': 'M.',
                                    },
                                   {'lastname'  : 'Smith',
                                    'firstname' : 'Tom',
                                    'middlename': 'W.',
                                    },
                                 ],
                     'publication_year' : '2006'
                     }
        id1 = bf.cookId(ref_dict1)
        self.assertEqual(id1, 'HicksSmith2006')
        ref_dict2 = {'authors' : [ {'lastname'  : 'Hicks',
                                    'firstname' : 'Tim',
                                    'middlename': 'M.',
                                    },
                                   {'lastname'  : 'Smith',
                                    'firstname' : 'Tom',
                                    'middlename': 'W.',
                                    },
                                   {'lastname'  : 'Parsons',
                                    'firstname' : 'Tammy',
                                    'middlename': 'T.',
                                    },
                                 ],
                     'publication_year' : '2006'
                     }
        id2 = bf.cookId(ref_dict2)
        self.assertEqual(id2, 'HicksEtAl2006')

    def test_interfaces(self):
        assert verify.verifyObject(IBibliography, self.folder.bib_folder)
        assert IIterableMapping.providedBy(self.folder.bib_folder)
    # end of the individual tests



class TestLargeBibliographyFolder(TestBibliographyFolder):
    """Test the LargeBibliographyFolder.
    We subclass the TestBibliographyFolder test case so that all of those tests
    are applied to LargeBibliographyFolders as well.
    """

    def afterSetUp(self):
        self._refreshSkinData()
        # Make sure that 'LargeBibliographyFolder' is an addable type...
        ttool = getToolByName(self.folder, 'portal_types')
        ftype = getattr(ttool, 'Folder')
        ftype_allowed = list(ftype.getProperty('allowed_content_types'))
        ftype_allowed.append('LargeBibliographyFolder')
        ftype.manage_changeProperties(allowed_content_types=ftype_allowed)

    # some utility methods

    def getEmptyBibFolder(self):
        uf = self.folder
        uf.invokeFactory(type_name='LargeBibliographyFolder',
                         id='bib_folder')
        return getattr(uf, 'bib_folder')

    def getPopulatedBibFolder(self,
                              source_file=setup.MEDLINE_TEST_MED,
                              format='med'):
        bf = self.folder.bib_folder
        source = open(source_file, 'r').read()
        bf.processImport(source, 'source.%s' % format)
        return bf

    # the individual tests

    def test_BibtexExport(self):
        # Overridden from the standard version: since this is an unordered
        # folder we can not rely on the order, which means we can not compare
        # against fixed output. So we test for the ids directly.
        bf = self.getPopulatedBibFolder()
        #bib_source = bf.bibliography_export(format='BibTeX').strip()
        bib_source = bf.restrictedTraverse('@@export').export(format='BibTeX').strip()
        self.failUnless("AlibardiThompson2003" in bib_source)
        self.failUnless("CokeEtAl2003" in bib_source)
        self.failUnless("GrootEtAl2003" in bib_source)
        self.failUnless("TrapeMane2002" in bib_source)

    # end individual tests

class TestMedlineBibliographyFolder(PloneTestCase.PloneTestCase):
    '''Test the BibliographyFolder'''

    layer = testing.medlineBibFolder

    def test_BibtexExportIgnoresNonBibrefItems(self):
        bf = self.folder.bib_folder
        bf.getPdfFolder() # non-bibref item
        #bib_source = bf.bibliography_export(format='BibTeX').strip()
        bib_source = bf.restrictedTraverse('@@export').export(format='BibTeX').strip()
        self.failIf("pdfs" in bib_source.lower())

    def test_getPublicationsByAuthors(self):
        bf = self.folder.bib_folder
        # one author
        refs  = bf.getPublicationsByAuthors('J Trape')
        self.assertEqual(len(refs), 1)
        self.assertEqual(refs[0].getId(), 'TrapeMane2002')
        # joint authors (and_flag false)
        refs  = bf.getPublicationsByAuthors(['J Trape',
                                             'Y Mane'])
        self.assertEqual(len(refs), 1)
        self.assertEqual(refs[0].getId(), 'TrapeMane2002')
        # joint authors (and_flag true)
        refs  = bf.getPublicationsByAuthors(['J Trape',
                                             'Y Mane'],
                                            1)
        self.assertEqual(len(refs), 1)
        self.assertEqual(refs[0].getId(), 'TrapeMane2002')
        # disjoint authors (and_flag false)
        refs  = bf.getPublicationsByAuthors(['J Trape',
                                             'T Groot'])
        ref_ids = [ref.getId() for ref in refs]
        self.assertEqual(len(refs), 2)
        self.failUnless('TrapeMane2002' in ref_ids)
        self.failUnless('GrootEtAl2003' in ref_ids)
        # disjoint authors (and_flag true)
        refs  = bf.getPublicationsByAuthors(['J Trape',
                                             'T Groot'],
                                            1)
        self.assertEqual(len(refs), 0)

    def test_Top(self):
        bf = self.folder.bib_folder
        bf.setTop(['TrapeMane2002', 'GrootEtAl2003', 'CokeEtAl2003'])
        top_2 = [ref.getId() for ref in bf.Top(2)]
        self.assertEqual(top_2, ['TrapeMane2002', 'GrootEtAl2003'])

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestBibliographyFolder))
    suite.addTest(makeSuite(TestLargeBibliographyFolder))
    suite.addTest(makeSuite(TestMedlineBibliographyFolder))
    return suite

if __name__ == '__main__':
    framework()

