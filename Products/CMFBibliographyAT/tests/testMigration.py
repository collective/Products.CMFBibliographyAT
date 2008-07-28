# Python imports
from cStringIO import StringIO

# Plone imports
from Products.Archetypes.tests.utils import makeContent
from Products.PloneTestCase import PloneTestCase as ptc

# Own factory imports
from Products.CMFBibliographyAT.migrations.cmfbib09to10 import Migration

class TestMigration09to10(ptc.PloneTestCase):

    def test_toolmigration(self):
        out = StringIO()
        makeContent(self.folder, portal_type='Folder', id='Renderers')
        makeContent(self.folder, portal_type='Folder', id='Parsers')

        assert 'Renderers' in self.folder.objectIds()
        assert 'Parsers' in self.folder.objectIds()

        migration = Migration(self.portal, out)
        migration.migrateTool(self.folder)

        self.failIf('Renderers' in self.folder.objectIds())
        self.failIf('Parsers' in self.folder.objectIds())

        # run again to make sure, it's safe.
        migration.migrateTool(self.folder)

        self.failIf('Renderers' in self.folder.objectIds())
        self.failIf('Parsers' in self.folder.objectIds())

        # run again with only Parsers in place
        makeContent(self.folder, portal_type='Folder', id='Parsers')

        assert 'Parsers' in self.folder.objectIds()

        migration.migrateTool(self.folder)

        self.failIf('Parsers' in self.folder.objectIds())

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMigration09to10))
    return suite

