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

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

from Products.CMFBibliographyAT.tests import setup
from Products.CMFBibliographyAT import testing

class TestReferenceTypesCreation(PloneTestCase.PloneTestCase):
    '''Test the reference types'''

    layer = testing.emptyBibFolder

    def test_ArticleCreation(self):
        bf = self.folder.bib_folder
        bf.invokeFactory(type_name = 'ArticleReference',
                         id = 'test_article')
        self.failUnless('test_article' in bf.contentIds())

class TestReferenceTypes(PloneTestCase.PloneTestCase):
    '''Test the reference types'''

    layer = testing.medlineBibFolder

    def test_ArticleSource(self):
        bf = self.folder.bib_folder
        source = bf.CokeEtAl2003.Source()
        expected_source = 'Am J Vet Res, 64(2):225-8.'
        self.assertEqual(source, expected_source)

    def test_getPdfFolder(self):
        bf = self.folder.bib_folder
        entry = bf.CokeEtAl2003
        o1 = bf.getPdfFolder()
        o2 = entry.getPdfFolder()
        self.assertEqual(o1, o2)
        self.failUnless('pdfs' in bf.contentIds())
        folder_type = o1.portal_type
        self.assertEqual(folder_type, 'PDF Folder')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(
        makeSuite(TestReferenceTypesCreation))
    suite.addTest(
        makeSuite(TestReferenceTypes))
    return suite

if __name__ == '__main__':
    framework()
