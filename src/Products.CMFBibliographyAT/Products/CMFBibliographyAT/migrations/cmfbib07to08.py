# Zope imports
from persistent.mapping import PersistentMapping

# Product imports
from Products.ATExtensions.ateapi import FormattableNamesField

from Products.CMFCore.utils import getToolByName

def replaceAuthorsField(obj):
    """
    change from the old custom 'publication_authors' field
    to the 'authors' FormattableNamesField from ATExtensions
    """
    try:
        obj.schema.replaceField('publication_authors',
                                FormattableNamesField('authors')
                                )
    except ValueError:
        pass

def migrateAuthorsValue(obj):
    """rename the attribute holding the value

    assumes attribute storage
    FormattableNamesField is clever enough to deal with the type change
    """
    authors = getattr(obj, 'publication_authors', None)
    if authors is not None:
        obj.authors = authors
        del obj.publication_authors
        obj._p_changed = 1

def migrateAuthors(obj):
    """
    deal with the renaming of the authors field:
    change the schema abd migrate the value
    """
    replaceAuthorsField(obj)
    migrateAuthorsValue(obj)

class Migration(object):
    """Migrating from 0.7 to 0.8

    It *must* be safe to use this multiple times as it is run automatically
    upon (re)install in the portal_quickinstaller.
    """

    def __init__(self, site, out):
        self.site = site
        self.out = out

    def migrate(self):
        """Run migration on site object passed to __init__.
        """
        print >> self.out
        print >> self.out, u"Migrating CMFBibliographyAT 0.7 -> 0.8"
        if self.needsAuthorSchemaUpgrade():
            self.migrateAuthorSchema()

    def needsAuthorSchemaUpgrade(self):
        """Returns True if one of the first 5 bibitems found
        has the old 'publication_authors' attribute; called
        by the installer to figure out whether a schema update
        is needed."""
        print >> self.out, u"authorSchema migration to FormattableNames field"
        print >> self.out, u"-----------------------------------------------"
        ct = getToolByName(self.site, 'portal_catalog')
        bib_tool = getToolByName(self.site, 'portal_bibliography')
        brains = ct(portal_type=bib_tool.getReferenceTypes(), Language='all')

        # needs schema upgrade for authors field
        if brains:
            for brain in brains[:5]:
                if getattr(brain.getObject(), 'publication_authors', False):
                    return True

        print >> self.out, u"    No authorSchema migration needed."
        print >> self.out
        return False

    # migrate data from old to new schema
    def migrateAuthorSchema(self):
        """restore the old author data to be available to the
        new author schema"""
        ct = getToolByName(self.site, 'portal_catalog')
        bib_tool = getToolByName(self.site, 'portal_bibliography')
        brains = ct(portal_type=bib_tool.getReferenceTypes(), Language='all')
        for brain in brains:
            obj = brain.getObject()
            authors = getattr(obj, 'publication_authors', None)
            if authors is not None:
                print >> self.out, u"    migrating authors of objectId: %s" % obj.getId()
                migrateAuthors(obj)
        print >> self.out
