# Zope imports
from persistent.mapping import PersistentMapping

# Archetypes import
from Products.Archetypes.public import listTypes
from Products.Archetypes.utils import shasattr

# Product imports
from Products.CMFCore.utils import getToolByName
from Products.CMFBibliographyAT.config import REFERENCE_TYPES
from Products.CMFBibliographyAT.config import FOLDER_TYPES as BIBFOLDER_TYPES

from bibliograph.core.utils import _encode, _decode

import copy

# test the following bibref item schema attributes to find out if the schema needs a migration
CMFBAT_SCHEMA_UPGRADE_INDICATORS = [

    'annote',

]

class Migration(object):
    """Migrate from 0.8 to 0.9

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
        print >> self.out, u"Migrating CMFBibliographyAT 0.8 -> 0.9"
        bibtool = getToolByName(self.site, 'portal_bibliography')
        self.migrateTool(bibtool)
        if self.needsCriteriasManagerUpgrade():
            self.migrateCriteriasManagerReferenceType()
        if self.needsTypeFieldSchemaUpgrade():
            self.migrateTypeFieldSchema()
        if self.needsGeneralSchemaUpgrade():
            self.generalSchemaUpgrade()
        if self.needsDuplicationEngineUpgrade():
            self.migrateDuplicationEngine()

    def migrateTool(self, bibtool):
        """Migrate the bibtool.
        """
        # Check for and add a persistent dictionary to keep track of
        # registered reference types on the tool.
        print >> self.out, u'BibliographyTool migration:'
        print >> self.out, u'---------------------------'
        rt = getattr(bibtool, '_reference_types', None)
        if rt is None:
            msg = u"    Adding the tool's _reference_types attribute."
            print >> self.out, msg
            bibtool._reference_types = PersistentMapping()
            # By default, we just use the standard CMFBib ref types
            for ref_type in REFERENCE_TYPES:
                bibtool._reference_types[ref_type] = None
        else:
            print >> self.out, u'    Tool is up-to-date'
        print >> self.out

    def needsCriteriasManagerUpgrade(self):

        """Check for old publication_type (alias for meta_type) Criterias in BibFolders' CriteriasManager
           -> should be renamed to "reference_type"
        """
        print >> self.out, u'ImportCriteriasManager schema migration:'
        print >> self.out, u'----------------------------------------'
        ct = getToolByName(self.site, 'portal_catalog')
        bibtool = getToolByName(self.site, 'portal_bibliography')

        # only check ref_types without typeField (id: publication_type)
        # if other ref_types have publication_type in ImportCriteriasManager
        # then we definitely need to upgrade!!!
        ReferenceClasses_without_typeField = [ t['klass'] for t in listTypes() if (t['meta_type'] in bibtool.getReferenceTypes()) and ('publication_type' not in [ field.getName() for field in t['schema'].fields() ]) ]
        ReferenceTypes_without_typeField = tuple([ klass.meta_type for klass in ReferenceClasses_without_typeField ])

        count = 0
        brains = ct(portal_type=BIBFOLDER_TYPES, Language='all')
        for brain in brains[:5]:
            bibfolder = brain.getObject()

            # if we come from a non-ImportCriteriasManager version of CMFBAT, we have to be carefull here.
            if shasattr(bibfolder, 'imp_criterias'):
                sel_crits = bibfolder.getSelectedCriterias()
                for ref_type in sel_crits.keys():
                    if (ref_type in ReferenceTypes_without_typeField) and ('publication_type' in sel_crits[ref_type]):
                        count += 1

        if count:
            print >> self.out, u'    Upgrade of ImportCriteriasManager required.'
            return True

        print >> self.out, u'    No ImportCriteriasManager upgrade needed.'
        print >> self.out
        return False

    def migrateCriteriasManagerReferenceType(self):

        ct = getToolByName(self.site, 'portal_catalog')
        bibtool = getToolByName(self.site, 'portal_bibliography')
        brains = ct(portal_type=BIBFOLDER_TYPES, Language='all')

        ReferenceClasses_without_typeField = [ t['klass'] for t in listTypes() if (t['meta_type'] in bibtool.getReferenceTypes()) and ('publication_type' not in [ field.getName() for field in t['schema'].fields() ]) ]
        ReferenceTypes_without_typeField = tuple([ klass.meta_type for klass in ReferenceClasses_without_typeField ])

        for brain in brains:
            bibfolder = brain.getObject()

            # reinitialize a bibfolder's possible import criterias for each reference type
            bibfolder.initCriterias()
            print >> self.out, u'    Migrating import criteria for BibliographyFolder: %s' % (bibfolder.getId())
            sel_crits = copy.deepcopy(bibfolder.getSelectedCriterias())

            all_crits = {}
            for ref_type, crits in copy.deepcopy(bibfolder.allCriterias()):
                all_crits[ref_type] = crits

            for ref_type in sel_crits.keys():

                # publication_type always migrate for classes with no typeField
                # and if there is only one publication_type in the list
                if ref_type in ReferenceTypes_without_typeField:
                    if 'publication_type' in sel_crits[ref_type]:
                        del sel_crits[ref_type][sel_crits[ref_type].index('publication_type')]
                        if ('reference_type' not in sel_crits[ref_type]) and ('reference_type' in all_crits[ref_type]):
                            sel_crits[ref_type].append('reference_type')

                # classes with typeField: migrate only if old type value still in dict
                # or if publication_type appears twice in the list.
                if ref_type not in ReferenceTypes_without_typeField:

                    # if the refitem schema is already migrated (who knows why...) we have to seek
                    # for criteria lists that have two publication_type entries
                    more_than_one_publication_type = ( 1 < len([ field for field in bibfolder.allCriterias() if field == 'publication_type' ]) )

                    if ('type' in sel_crits[ref_type]) or more_than_one_publication_type:

                        if 'publication_type' in sel_crits[ref_type]:

                            # this will delete only one publiation_type entry
                            del sel_crits[ref_type][sel_crits[ref_type].index('publication_type')]
                            if ('reference_type' not in sel_crits[ref_type]) and ('reference_type' in all_crits[ref_type]):
                                sel_crits[ref_type].append('reference_type')

                        if 'type' in sel_crits[ref_type]:
                            del sel_crits[ref_type][sel_crits[ref_type].index('type')]
                            if ('publication_type' not in sel_crits[ref_type]) and ('publication_type' in all_crits[ref_type]):
                                sel_crits[ref_type].append('publication_type')

                    else:

                        if 'publication_type' in sel_crits[ref_type]:
                            del sel_crits[ref_type][sel_crits[ref_type].index('publication_type')]
                            if ('reference_type' not in sel_crits[ref_type]) and ('publication_type' in all_crits[ref_type]):
                                sel_crits[ref_type].append('reference_type')

            #print 'Migrating criterias of BibFolder: %s' % bibfolder.getId()
            #print sel_crits
            bibfolder.setCriterias(sel_crits)
        print >> self.out

    def needsTypeFieldSchemaUpgrade(self):
        """Check for old straying type field remnants, they indicate a typeField migration need
        """
        print >> self.out, u'typeField schema migration:'
        print >> self.out, u'---------------------------'
        ct = getToolByName(self.site, 'portal_catalog')
        bibtool = getToolByName(self.site, 'portal_bibliography')

        # detect reference_types that contain the typeField
        ReferenceClasses_with_typeField = [ t['klass'] for t in listTypes() if (t['meta_type'] in bibtool.getReferenceTypes()) and ('publication_type' in [ field.getName() for field in t['schema'].fields() ]) ]
        ReferenceTypes_with_typeField = tuple([ klass.meta_type for klass in ReferenceClasses_with_typeField ])

        brains = ct(portal_type=ReferenceTypes_with_typeField, Language='all')
        # check ALL(!) brains if we really need schema upgrade for old typeField: 'type' -> 'publication_type'
        for brain in brains:
            old_typeField_value = getattr(brain.getObject(), 'type', False)

            # to avoid mismatch with the BaseObject's type definition (alias for schema) check
            # for a unicode value in typeField
            if old_typeField_value and (type(old_typeField_value) == type(u'')):
                print >> self.out, u'    Upgrade of typeField required.'
                return True

        print >> self.out, u'    No typeField schema upgrade needed.'
        print >> self.out
        return False

    def migrateTypeFieldSchema(self):
        """Migrate typeField id 'type' to new (less overloaded) id 'publication_type'
        """
        ct = getToolByName(self.site, 'portal_catalog')
        bibtool = getToolByName(self.site, 'portal_bibliography')

        # detect reference_types that contain the typeField
        ReferenceClasses_with_typeField = [ t['klass'] for t in listTypes() if (t['meta_type'] in bibtool.getReferenceTypes()) and ('publication_type' in [ field.getName() for field in t['schema'].fields() ]) ]
        ReferenceTypes_with_typeField = tuple([ klass.meta_type for klass in ReferenceClasses_with_typeField ])

        brains = ct(meta_type=ReferenceTypes_with_typeField, Language='all')
        for brain in brains:

            bibref_item = brain.getObject()
            # this one is the old typeField value
            old_typeField_value = copy.deepcopy(getattr(bibref_item, 'type', False))
            # this one the new typeField with id 'publication_type'
            new_typeField = bibref_item.Schema().get('publication_type', None)

            # if there is no formerly set typeField value, just do the schema update
            if new_typeField and (type(old_typeField_value) == type(bibref_item.schema)):
                bibref_item._updateSchema()
                try:
                    print >> self.out, u'    Only simple schema update needed for ObjectId %s: typeField value=\'%s\'' % (brain.getId, bibref_item.getPublication_type())
                except UnicodeDecodeError:
                    print >> self.out, u'    Only simple schema update needed for ObjectId %s: typeField value=\'%s\'' % (brain.getId, '<HIDDEN: value contains non-ASCII characters>')

            # but if there is an old 'type' attribute in the bibref_item object, update the new typeField with its value
            # to avoid mismatch with the BaseObject's type definition (alias for schema) check for a unicode value in typeField
            elif new_typeField and (type(old_typeField_value) == type(u'')):
                delattr(bibref_item, 'type')
                bibref_item._updateSchema()
                bibref_item.edit(publication_type=old_typeField_value)
                try:
                    print >> self.out, u'    Migrating typeField of ObjectId %s: value=\'%s\'' % (brain.getId, bibref_item.getPublication_type())
                except UnicodeDecodeError:
                    print >> self.out, u'    Migrating typeField of ObjectId %s: value=\'%s\'' % (brain.getId, '&lt;HIDDEN: value contains non-ASCII characters&gt;')

            else:

                print >> self.out, u'    typeField schema update for ObjectId: %s failed.' % bibref_item.getId()

        print >> self.out

    def needsGeneralSchemaUpgrade(self):
        """Returns True if one of the first 5 bibitems found
           has missing schema fields (compared to v0.8); called
           by the installer to figure out whether a schema update
           is needed."""
        print >> self.out, u"general schema upgrade of bibliographical reference items"
        print >> self.out, u"---------------------------------------------------------"
        ct = getToolByName(self.site, 'portal_catalog')
        bib_tool = getToolByName(self.site, 'portal_bibliography')
        brains = ct(portal_type=bib_tool.getReferenceTypes(), Language='all')

        # needs schema upgrade for authors field
        if brains:
            for attribute in CMFBAT_SCHEMA_UPGRADE_INDICATORS:
                for brain in brains[:10]:
                    if not shasattr(brain.getObject(), attribute, False):
                        return True
        print >> self.out, u"    No general schema upgrade needed."
        print >> self.out
        return False

    # migrate data from old to new schema
    def generalSchemaUpgrade(self):
        """perform a general AT schema upgrade"""
        ct = getToolByName(self.site, 'portal_catalog')
        bib_tool = getToolByName(self.site, 'portal_bibliography')

        # logging to ZLog and to quick installer's report
        print >> self.out, u'    Bibliographical references need general schema upgrade!!! This might take a while...'
        print u'***'
        print u'*** CMFBibliogaphyAT migration: Bibliographical references need general schema upgrade!!! This might take a while...'
        print u'***'
        brains = ct(portal_type=bib_tool.getReferenceTypes(), Language='all')
        for brain in brains:
            obj = brain.getObject()
            obj._updateSchema()

        print u'CMFBibliographyAT migration: Upgraded schemata of %s bibliographical references' % len(brains)
        print
        print >> self.out, u'    Upgraded schemata of %s bibliographical references' % len(brains)
        print >> self.out

    def needsDuplicationEngineUpgrade(self):
        """Returns True if any existing bibfolder shows signs of bibfolder._duplicates """
        print >> self.out, u"upgrade of bibliography folders' duplicate bibliographical reference engine"
        print >> self.out, u"---------------------------------------------------------------------------"
        ct = getToolByName(self.site, 'portal_catalog')
        bib_tool = getToolByName(self.site, 'portal_bibliography')
        brains = ct(portal_type=BIBFOLDER_TYPES, Language='all')

        # needs schema upgrade for authors field
        if brains:
            for brain in brains:
                if shasattr(brain.getObject(), '_duplicates'):
                        return True
        print >> self.out, u"    No duplication engine migration needed."
        print >> self.out
        return False

    # migrate duplication engine
    def migrateDuplicationEngine(self):
        """ migrate bibfolder._duplicates -> bibfolder.duplicates.<items> """
        ct = getToolByName(self.site, 'portal_catalog')
        bib_tool = getToolByName(self.site, 'portal_bibliography')
        reference_catalog = getToolByName(self.site, 'reference_catalog')

        print >> self.out, u'    Bibliography Folder needs duplication engine upgrade ...'
        brains = ct(portal_type=BIBFOLDER_TYPES, Language='all')
        for brain in brains:
            bibfolder = brain.getObject()
            if shasattr(bibfolder, '_duplicates'):
                duplicates = bibfolder._duplicates
                for key in duplicates.keys():
                    entry = duplicates[key]
                    if entry.has_key('publication_type') and entry['publication_type'] in bib_tool.getReferenceTypes():
                        # very old instance...
                        entry['reference_type'] = entry['publication_type']
                        del entry['publication_type']
                        if entry.has_key('type'):
                            entry['publication_type'] = entry['type']

                    matched_uuids = entry['matched_uuids']
                    del entry['matched_uuids']
                    (report_line, import_status, bibref_item) = bibfolder.processSingleImport(entry, force_to_duplicates=True)
                    print >> self.out, '    Transferred _duplicates item %s to object %s in %s/duplicates' % (key, bibref_item.getId(), bibfolder.absolute_url())
                    bibref_item.setIs_duplicate_of([ matched_uuid for matched_uuid in matched_uuids if reference_catalog.lookupObject(matched_uuid) ])
                delattr(bibfolder, '_duplicates')

        print >> self.out, u'    Upgraded of bibliography folders\' duplication engine completed. %s bibliography folders migrated.' % len(brains)
        print >> self.out
