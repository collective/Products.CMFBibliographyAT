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

class TestBibliographyTool(PloneTestCase.PloneTestCase):
    '''Test the reference types'''

    # the individual tests

    def testGetReferenceTypes(self):
        bibtool = self.portal.portal_bibliography
        ref_types = list(bibtool.getReferenceTypes())
        ref_types.sort()
        # the expected types
        from Products.CMFBibliographyAT.config import REFERENCE_TYPES
        expected_types = list(REFERENCE_TYPES)
        expected_types.sort()
        self.assertEqual(ref_types, expected_types)

    def testImportFormats(self):
        bibtool = self.portal.portal_bibliography
        expected_names = ['BibTeX', 'Medline']
        names = bibtool.getImportFormatNames()
        # This makes sure we only check for the required types
        # IBSS, ISBN, PyBl might be present aswell
        names = [name for name in expected_names if name in names]
        names.sort()
        self.assertEqual(names, expected_names)
        expected_extensions = ['bib', 'med']
        extensions = bibtool.getImportFormatExtensions()
        # Filter, same as for names
        extensions = [ext for ext in expected_extensions if ext in extensions]
        extensions.sort()
        self.assertEqual(extensions, expected_extensions)

    def testExportFormats(self):
        bibtool = self.portal.portal_bibliography

        # bibtex is always available, all others are optional
        assert 'BibTeX' in bibtool.getExportFormatNames()
        assert 'bib' in bibtool.getExportFormatExtensions()


    # end of the individual tests

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestBibliographyTool))
    return suite

if __name__ == '__main__':
    framework()
