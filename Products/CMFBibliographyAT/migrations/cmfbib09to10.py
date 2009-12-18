# Zope imports

# Archetypes import

# Product imports
from Products.CMFCore.utils import getToolByName

class Migration(object):
    """Migrate from 0.9 to 1.0

    It *must* be safe to use this multiple times as it is run automatically
    upon (re)install in the portal_quickinstaller.
    """

    def __init__(self, site, out):
        self.site = site
        self.out = out
        #self.catalog = getToolByName(self.site, 'portal_catalog')

    def migrate(self):
        """Run migration on site object passed to __init__.
        """
        print >> self.out
        print >> self.out, u"Migrating CMFBibliographyAT 0.9 -> 1.0"
        bibtool = getToolByName(self.site, 'portal_bibliography')
        self.migrateTool(bibtool)
        self.migrateIdentifiers()

    def migrateTool(self, bibtool):
        """Migrate the bibtool.
        """
        # Check for and add a persistent dictionary to keep track of
        # registered reference types on the tool.
        print >> self.out, u'BibliographyTool migration:'
        print >> self.out, u'---------------------------'
        persistent_components = ['Renderers', 'Parsers']
        REMOVED_COMPONENT = False
        for pcid in persistent_components:
            if pcid in bibtool.objectIds():
                msg = u"    Remove the persistent '%s' object." % pcid
                print >> self.out, msg
                bibtool._delObject(pcid)
                REMOVED_COMPONENT = True
        if not REMOVED_COMPONENT:
            print >> self.out, u'    Tool is up-to-date'
        print >> self.out

    def migrateIdentifiers(self):
        """ Migrate numbers to identifiers """

        from Products.CMFBibliographyAT.config import REFERENCE_TYPES

        for brain in self.site.portal_catalog(portal_type=REFERENCE_TYPES):
            ref = brain.getObject()
            if 'isbn' in ref.Schema().keys():

                old_isbn = ref.getIsbnOld()
                new_isbn = ref.ISBN()

                # check for old ISBN and see if the object has already been migrated
                if old_isbn and not getattr(ref, '_migrated_isbn', None):
                    print >>self.out, u'Migrating ISBN number of ', ref.absolute_url(1)

                    # replace ISBN
                    ids = [d for d in ref.getIdentifiers() if d['label'] != 'ISBN']
                    ids.append({'label' : 'ISBN', 'value' : new_isbn})
                    ref.setIdentifiers(ids)
                    ref._migrated_isbn = True

            if 'pmid' in ref.Schema().keys():

                old_pmid = ref.pmid
                new_pmid = ref.PMID()

                # check for old PMID and see if the object has already been migrated
                if old_pmid and not getattr(ref, '_migrated_pmid', None):
                    print >>self.out, u'Migrating PMID number of ', ref.absolute_url(1)

                    # replace PMID
                    ids = [d for d in ref.getIdentifiers() if d['label'] != 'PMID']
                    ids.append({'label' : 'PMID', 'value' : new_pmid})
                    ref.setIdentifiers(ids)
                    ref._migrated_pmid = True

        print >>self.out


