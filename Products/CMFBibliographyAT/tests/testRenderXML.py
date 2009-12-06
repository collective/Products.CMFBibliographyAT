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
from Products.CMFCore.utils import getToolByName

from bibliograph.core.bibutils import _getCommand

from Products.CMFBibliographyAT.tests import setup
from Products.CMFBibliographyAT import testing

class TestRenderXML(PloneTestCase.PloneTestCase):
    """Test rendering to XML.
    """

    layer = testing.emptyBibFolder

    # some utility methods

    def getPopulatedBibFolder(self, source_file=setup.MEDLINE_TEST_MED, format="med"):
        bf = self.folder.bib_folder
        source = open(source_file, 'r').read()
        bf.processImport(source, 'source.%s' % format)
        return bf

    # the individual tests

    def testRenderXML(self):
        bf = self.getPopulatedBibFolder()
        xml_source = bf.restrictedTraverse('@@export').export(format='xml').strip()
        # chop of BOM
        pos = xml_source.find('<?xml')
        xml_source = xml_source[pos:] 
        # Need to remove Windows carriage returns for when tests run on Windows.
        xml_source = xml_source.replace('\r', '')
        expected_source = open(setup.MEDLINE_TEST_XML, 'r').read().strip()
        # just in case we need to debug that again
        #l1 = bib_source.splitlines(1)
        #l2 = expected_source.splitlines(1)
        #from difflib import Differ
        #from pprint import pprint
        #d = Differ()
        #pprint(list(d.compare(l1,l2)))
        self.assertEqual(xml_source, expected_source)

    # end of the individual tests


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    if _getCommand('bib', 'xml', False):
        suite.addTest(makeSuite(TestRenderXML))
    return suite

if __name__ == '__main__':
    framework()
