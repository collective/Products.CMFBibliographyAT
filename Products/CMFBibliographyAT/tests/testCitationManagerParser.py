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

from Products.CMFBibliographyAT.tool.parsers.citationmanager import \
     CitationManagerParser

class TestCitationManagerParser(PloneTestCase.PloneTestCase):
    '''Test the CitationManagerParser'''

    # the individual tests

    def test_Parser(self):
        source = open(setup.CITATION_MANAGER_SOURCE, 'r').read()
        p = CitationManagerParser()
        entries = p.getEntries(source)
        self.failUnless( len(entries) == 3 )
        self.failUnless( entries[0]['title'] == 'Transfers in Kind: Why They Can be Efficient and Nonpaternalistic' )
        self.failUnless( entries[0]['pages'] == '1345-1351' )
        self.failUnless( len( entries[0]['authors'] ) == 2 )
        self.failUnless( entries[1]['authors'][0]['lastname'] == 'Murphy' )
        self.failUnless( entries[1]['authors'][0]['firstname'] == 'Kevin' )
        self.failUnless( entries[1]['authors'][0]['middlename'] == 'M.' )
        self.failUnless( entries[1]['authors'][1]['lastname'] == 'Shleifer' )
        self.failUnless( entries[1]['authors'][1]['firstname'] == 'Andrei' )
        self.failUnless( entries[1]['authors'][1]['middlename'] == '' )
        self.failUnless( entries[1]['authors'][2]['lastname'] == 'Vishny' )
        self.failUnless( entries[1]['authors'][2]['firstname'] == 'Robert' )
        self.failUnless( entries[1]['authors'][2]['middlename'] == 'W.' )
        self.failUnless( entries[2]['volume'] == '57' )
        self.failUnless( entries[2]['number'] == '1' )
        self.failUnless( entries[2]['publication_year'] == '1967' )
        # XXX This test could be adjusted if the parser got smarter about
        #     about converting 'Mar.' into 'March'
        self.failUnless( entries[2]['publication_month'] == 'Mar.' )

    # end of the individual tests

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCitationManagerParser))
    return suite

if __name__ == '__main__':
    framework()
