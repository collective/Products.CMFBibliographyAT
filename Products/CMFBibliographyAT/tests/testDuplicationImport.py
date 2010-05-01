#######################################################
#                                                     #
#    Copyright (C), 2004, Raphael Ritz                #
#    <r.ritz@biologie.hu-berlin.de>                   #
#                                                     #
#    Humboldt University Berlin                       #
#                                                     #
# Copyright (C), 2005, Logilab S.A. (Paris, FRANCE)   #
# http://www.logilab.fr/ -- mailto:contact@logilab.fr #
#                                                     #
#######################################################

__revision__ = '$Id:  $'


import os, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.CMFPlone.tests import PloneTestCase
from Products.CMFBibliographyAT.tests import setup
from ZODB.PersistentList import PersistentList
from Globals import PersistentMapping

from Products.CMFBibliographyAT import testing

class TestBibliographyFolder(PloneTestCase.PloneTestCase):
    '''Test the BibliographyFolder Import and duplication handling'''

    layer = testing.bibtexBibFolder

    def afterSetUp(self):
        self._refreshSkinData()
        self.bf = self.folder.bib_folder

    #FIXME duplicate from testBibliographyFolder - REFACTOR
    def getEmptyBibFolder(self, ident):
        uf = self.folder
        uf.invokeFactory(type_name = "BibliographyFolder",
                         id = ident )
        return getattr(uf, ident)

    def testBibtexImportDuplicate(self):
        bibtool = self.portal.portal_bibliography
        filter = {'portal_type': bibtool.getReferenceTypes(), }

        self.insertDuplicates()
        self.assertEquals(len(self.bf.contentIds(filter=filter)), 3 ,
                          'Duplicate Entry was introduced, expected 3 unique entries')

    def insertDuplicates(self):
        bib_source = open(setup.BIBTEX_TEST_BIB_DUP, 'r').read()
        self.bf.processImport(bib_source, 'bibtex_test_duplicates.bib')

    def insertSameImportFile(self):
        bib_source = open(setup.BIBTEX_TEST_BIB, 'r').read()
        self.bf.processImport(bib_source, 'bibtex_test.bib')


    def testBibtexImportDuplicate_Access(self):
        self.insertDuplicates()

        self.assertNotEqual(self.bf.getDuplicatesFolder().contentValues(), [])

        dup_entry = self.bf.getDuplicatesFolder().contentValues()[0]
        self.assertEquals(dup_entry.Title(), 'Programming Python.')
        self.assertEquals(len(dup_entry.getIs_duplicate_of()), 1)

    def testNewFolderCriterias(self):
        """
        testes that the import_criterias for a fold changed after
        being modifieded (folder bg)
        """
        duplicates_criteria = {'BookReference' : PersistentList(('authors', 'title')) }

        self.second_bf = self.getEmptyBibFolder('second_bib_folder')

        old_criterias = self.bf.getCriterias()
        sec_old_criterias = self.second_bf.getCriterias()

        for bib_type in duplicates_criteria.keys():
            self.bf.setCriteriasForType(bib_type, duplicates_criteria[bib_type])

        new_criterias = self.bf.getCriterias()
        sec_new_criterias = self.second_bf.getCriterias()

        self.assertNotEquals(old_criterias, new_criterias,
                              'Criterias have not been changed')

        self.assertEquals(sec_old_criterias, sec_new_criterias,
                              'Criterias have been changed')

    def testLocalGlobalDistinction(self):
        bibtool = self.portal.portal_bibliography
        filter = {'portal_type': bibtool.getReferenceTypes(), }

        # insert 3 entries in second_bib_folder
        second_bf = self.getEmptyBibFolder('second_bib_folder')
        bib_source = open(setup.BIBTEX_TEST_BIB, 'r').read()
        second_bf.processImport(bib_source, 'bibtex_test.bib')

        folder_contents = [ c for c in self.folder.contentIds() if c != '.personal' ]
        self.assertEquals(folder_contents, ['bib_folder', 'second_bib_folder'])
        self.assertEquals(len(folder_contents), 2)

        # do a global import of bib_folder
        bibtool = self.portal.portal_bibliography
        bib_source = open(setup.BIBTEX_TEST_BIB_DUP, 'r').read()
        entries = bibtool.getEntries(bib_source, None, 'bibtex_test_duplicates.bib')
        for entry in entries:
            if entry.get('title'):
                upload = self.bf.processSingleImport(entry, span_of_search='global')

        # check matches 2
        dup_entry = self.bf.getDuplicatesFolder().contentValues()[0]
        self.assertEquals(len(dup_entry.getIs_duplicate_of()), 2)


    def testCriteriasScope(self):
        """
        testes
        set 1 :
           Changing criterias for a folder (self.bg) doesn't imply changing
           those of another folder (self.second_bg)
        set 2 :
           If criterias for a folder had been changed, changing
           portal criterias has no influence on them (self.bg),
           otherwise, a folder gets new portal criterias (self.second_bg)


        """
        bibtool = self.portal.portal_bibliography
        port_old_criterias = bibtool.getSelectedCriteria()

        folder_criterias = {'BookReference' : ('authors', 'title') }
        portal_criterias = {'ArticleReference' :
                                   ('publication_year', 'title')}
        self.second_bf = self.getEmptyBibFolder('second_bib_folder')

        #port_old_criterias = PersistentMapping()
        for key, value in bibtool.getSelectedCriteria().items():
            port_old_criterias[key] = value

        ### set 1

        old_criterias = self.bf.getCriterias()
        sec_old_criterias = self.second_bf.getCriterias()
        #changes criterias on first folder
        for bib_type in folder_criterias.keys():
            self.bf.setCriteriasForType(bib_type, \
                                        folder_criterias[bib_type])
        new_criterias = self.bf.getCriterias()
        sec_new_criterias = self.second_bf.getCriterias()

        #Criterias on Folder1 should got changed
        self.assertNotEquals(old_criterias, new_criterias,
                              'Folder1 criterias have not been changed')

        #Criterias for Folder2 should stay unchanged
        self.assertEquals(sec_old_criterias, sec_new_criterias,
                              'Folder2 criterias have been changed')

        #Criterias for Folder2 should be equal to those of Portal
        self.assertEquals(sec_new_criterias, port_old_criterias,
                              'Folder2 criterias are not equal to those of Portal')

        #Criterias for Folder1 should not be equal to those of Portal
        self.assertNotEquals(new_criterias, port_old_criterias,
                              'Folder1 criterias are equal to those of Portal')

        ### set 2

        #changes criterias on bibliography tool
        for bib_type in portal_criterias.keys():
            bibtool.setCriteriasForType(bib_type,\
                                        portal_criterias[bib_type])
        port_new_criterias = bibtool.getSelectedCriteria()

        new2_criterias = self.bf.getCriterias()

        self.second_bf = self.getEmptyBibFolder('another_second_bib_folder')
        sec_new2_criterias = self.second_bf.getCriterias()

        #portal criterias should got changed
        self.assertNotEquals(port_old_criterias, port_new_criterias,
                             'Portal criterias have not been changed')


        #Criterias for Folder1 should stay unchanged
        self.assertEquals(new_criterias, new2_criterias,
                              'Folder 1 criterias have been changed')
        #Criterias for Folder2 should be those of Portal
        self.assertEquals(port_new_criterias, sec_new2_criterias,
                              'Criterias For Folder 2 are not those of Portal')

    def testZeroCriterias(self):
        """
        testes an import without criterais specified
        """
        bibtool = self.portal.portal_bibliography
        filter = {'portal_type': bibtool.getReferenceTypes(), }

        self.bf.setCriterias({})
        self.insertDuplicates()
        # 4 bibref items, no duplicate folder
        self.assertEquals(len(self.bf.contentIds(filter=filter)), 4,
                          'Import failed, expected 4 entries')

    def testDuplicateImportFolderWideCriterias(self):
        """
        bibtex_test.bib contains 2 entries of BookReference type and
        1 entry of WebpublishedReference type
        """
        folder_criterias = {'BookReference' : () }
        bibtool = self.portal.portal_bibliography
        filter = {'portal_type': bibtool.getReferenceTypes(), }

        self.insertSameImportFile()
        self.assertEquals(len(self.bf.contentIds(filter=filter)), 3 ,
                          'Import failed, expected 3 entries')

        #set criterais for BookReference type to ()
        for bib_type in folder_criterias.keys():
            self.bf.setCriteriasForType(bib_type, \
                                        folder_criterias[bib_type])
        self.insertSameImportFile()
        self.assertEquals(len(self.bf.contentIds(filter=filter)), 5,
                          'Import failed, expected 5 entries')

    def testDuplicateImportCriterias(self):
        """
        bibtex_test.bib contains 2 entries of BookReference type and
        1 entry of WebpublishedReference type
        """
        portal_criterias = {'BookReference' : () }
        bibtool = self.portal.portal_bibliography
        filter = {'portal_type': bibtool.getReferenceTypes(), }

        # tests : portal wide criterias
        # set portal criterias for BookReference type to ()
        for bib_type in portal_criterias.keys():
            bibtool.setCriteriasForType(bib_type, \
                                        portal_criterias[bib_type])

        self.insertSameImportFile()
        self.assertEquals(len(self.bf.contentIds(filter=filter)), 3 ,
                          'Import failed, expected 3 entries')

        ###
        ### the next test is deprecated as the behaviour of the duplicates
        ### engine has slightly changed: bib_tool duplicates criteria are
        ### only adopted on bibfolder creation, afterwards there will be
        ### no further influence on bibfolder criteria by the bib_tool.
        ### mg, 20061121

        ## tests : portal wide criterias
        ## set portal criterias for BookReference type to ()
        #for bib_type in portal_criterias.keys():
        #    bibtool.setCriteriasForType(bib_type, \
        #                                portal_criterias[bib_type])
        #
        #self.insertSameImportFile()
        #print len(self.bf.contentIds(filter=filter))
        #self.assertEquals(len(self.bf.contentIds(filter=filter)), 5,
        #                  'Import failed, expected 5 entries')

        # tests : folder wide criterias
        #set folder criterias for BookReference to ()

        folder_criterias = {'BookReference' : () }
        for bib_type in folder_criterias.keys():
            self.bf.setCriteriasForType(bib_type, \
                                        folder_criterias[bib_type])
        self.insertSameImportFile()
        self.assertEquals(len(self.bf.contentIds(filter=filter)), 5,
                          'Import failed, expected 5 entries')



    def testBibtexImportDuplicate_2matches(self):
        """ test that the references in the duplicated entry is multiple"""
        bibtool = self.portal.portal_bibliography
        filter = {'portal_type': bibtool.getReferenceTypes(), }

        bib_source = open(setup.BIBTEX_TEST_BIB_DUP, 'r').read()
        self.bf.processImport(bib_source, 'bibtex_test_duplicates.bib')
        self.assertEquals(len(self.bf.contentIds(filter=filter)), 3 ,
                          'Duplicate Entry was introduced, expected 3 unique entries')

    def testDelay(self):
        func_name = 'delayDuplicated'
        nb_end = 1
        expected_logs = []
        self.action_test(func_name, expected_logs, nb_end)

    def testSkip(self):
        func_name = 'skipDuplicated'
        nb_end = 0
        expected_logs = []
        self.action_test(func_name, expected_logs, nb_end)

    # FIXME - freeze - from previous (force)?
    def testReplace(self):
        func_name = 'replaceDuplicated'
        nb_end = 0
        expected_logs = ['replace begin implemented']
        self.action_test(func_name, expected_logs, nb_end)
        # check UID hasn't changed
        # check edition has changed to 3rd
        #self.bf. check

    def testForce(self):
        bibtool = self.portal.portal_bibliography
        filter = {'portal_type': bibtool.getReferenceTypes(), }

        func_name = 'forceDuplicated'
        nb_end = 0
        expected_logs = None
        self.action_test(func_name, expected_logs, nb_end)
        self.assertEquals(len(self.bf.contentIds(filter=filter)), 4,
                          'Duplicate Entry was not forcefully introduced, expected 4 entries')

    def action_test(self, func_name, expected_logs, nb_end):
        """
        if expected_logs is None - don't test logs
        """
        logs = []
        self.insertDuplicates()
        duplicates = self.bf.getDuplicates()
        self.assertEquals(len(duplicates), 1, 'beginning count is not right')

        for key, each_duplicated_entry in duplicates.items():
            action_func = getattr(self.bf, func_name)
            msg = action_func(key)
            if msg:
                logs.append(msg)
        if not expected_logs is None:
            self.assertEquals(logs, expected_logs)

        duplicates = self.bf.getDuplicates()
        #self.assertEquals(len(self.bf._duplicates), nb_end)
        self.assertEquals(len(duplicates), nb_end, 'end count is not right')


    # test logs
    def testBibtexImportLogs(self):
        # do a global import of bib_folder
        bibtool = self.portal.portal_bibliography
        bib_source = open(setup.BIBTEX_TEST_BIB_DUP, 'r').read()
        entries = bibtool.getEntries(bib_source, None, 'bibtex_test_duplicates.bib')
        logs = []
        for entry in entries:
            if entry.get('title'):
                upload = self.bf.processSingleImport(entry, span_of_search='global')
                obj = upload[2]
                if upload:
                    logs.append(upload)
        self.assertEquals(logs, [('Skipped: Programming Python.\n', 'SKIPPED', obj, )])




def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestBibliographyFolder))
    return suite

if __name__ == '__main__':
    framework()
