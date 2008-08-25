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

from bibliograph.core.utils import bin_search
from bibliograph.parsing.parsers.ris import \
     RISParser

class TestRISParser(PloneTestCase.PloneTestCase):
    '''Test the RIS parser'''

    # the individual tests

    def test_Parser(self):
        source = open(setup.RIS_SOURCE, 'r').read()
        p = RISParser()
        entries = p.getEntries(source)
        self.failUnless( len(entries) == 1 )
        self.failUnless( entries[0]['title'] == 'Markets and Municipalities: A Study of the Behavior of the Danish Municipalities' )
        self.failUnless( entries[0]['pages'] == '79--102' )
        self.failUnless( len( entries[0]['authors'] ) == 2 )
        self.failUnless( entries[0]['authors'][0]['lastname'] == 'Christoffersen' )
        self.failUnless( entries[0]['authors'][0]['firstname'] == 'Henrik' )
        self.failUnless( entries[0]['authors'][0]['middlename'] == '' )
        self.failUnless( entries[0]['authors'][1]['lastname'] == 'Paldam' )
        self.failUnless( entries[0]['authors'][1]['firstname'] == 'Martin' )
        self.failUnless( entries[0]['authors'][1]['middlename'] == '' )
        self.failUnless( entries[0]['volume'] == '114' )
        self.failUnless( entries[0]['number'] == '1 - 2' )
        self.failUnless( entries[0]['publication_year'] == '2003' )
        self.failUnless( entries[0]['journal'] == 'Public Choice' )
        # XXX This test could be adjusted if the parser got smarter about
        #     about converting 'Mar.' into 'March'
        ## rr: which it did inbetween it seems because I had to add
        ## the fully spelled out month names to the 'month_mapper' dict.
        self.failUnless( entries[0]['publication_month'] == '01' )

    # end of the individual tests

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    if bin_search('ris2xml', False) is False:
        print 'ris2xml not found!'
        print 'please make sure bibutils is installed to run all tests.'
        print '-' * 20
    else:
        suite.addTest(makeSuite(TestRISParser))
    return suite

if __name__ == '__main__':
    framework()
