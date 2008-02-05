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

class TestContentTypes(PloneTestCase.PloneTestCase):
    '''Test the various content types'''

    layer = testing.medlineBibFolder

    def test_plainTextAbstract(self):
        bf = self.folder.bib_folder
        article = getattr(bf, 'GrootEtAl2003')
        abstract = "\nMy special abstract\n"
        article.setAbstract(abstract, mimetype='text/plain')
        self.assertEqual(str(article.editAbstract()), abstract)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestContentTypes))
    return suite

if __name__ == '__main__':
    framework()
