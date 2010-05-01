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

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFBibliographyAT.tests import setup
from ZODB.PersistentList import PersistentList
from Persistence import PersistentMapping

from Products.CMFBibliographyAT.tests import dummy

#ZopeTestCase.installProduct('DeadlockDebugger')
#import Products.DeadlockDebugger

class TestBibliographyFolder(PloneTestCase.PloneTestCase):
    '''Test the BibliographyFolder Import and duplication handling'''

    def afterSetUp(self):
        self._refreshSkinData()


    def getEmptyBibFolder(self, id='bibfolder'):

        uf = self.folder
        if not hasattr(uf, id):
            uf.invokeFactory(type_name = "BibliographyFolder", id=id )
        bf = getattr(uf, id)
        return bf

    def getPopulatedBibFolder(self, id='bibfolder'):
        bf = self.getEmptyBibFolder(id=id)
        bib_source = open(setup.BIBTEX_TEST_BIB, 'r').read()
        bf.processImport(bib_source, 'bibtex_test.bib')
        return bf

    def getTwoPopulatedBibFolders(self, id1='bibfolder1', id2='bibfolder2'):
        bf1 = self.getPopulatedBibFolder(id=id1)
        bf2 = self.getPopulatedBibFolder(id=id2)
        return bf1, bf2

    def testSiteWideEnableDuplicatesManager(self):

        bf = self.getEmptyBibFolder(id='dup_tool_test')
        self.failUnless(bf.getEnableDuplicatesManager())

    def testDuplicatesFolder(self):
        bf = self.getEmptyBibFolder(id='dup_bf')
        bf.getDuplicatesFolder()
        self.failUnless('duplicates' in bf.contentIds())
        self.failUnless(bf.duplicates.portal_type == 'DuplicatesBibliographyFolder')
        self.failUnless(bf.duplicates.getReferenceIdCookingMethod() == 'uid')
        self.failUnless(bf.duplicates.getCookIdsAfterBibRefEdit())

        try:
            bf.duplicates.invokeFactory(type_name='ArticleReference', id='test1')
        except:
            pass

        # bib ref item creation should not be possible!!!
        self.failUnless('test1' not in bf.duplicates.contentIds())

    def testDuplicatesIdCooking(self):
        bf = self.getEmptyBibFolder(id='dup_bf')
        df = bf.getDuplicatesFolder()
        bib_tool = bf.portal_bibliography

        tt = bf.portal_types
        fti = tt[bf.duplicates.portal_type]
        fti.allowed_content_types = tuple(bib_tool.getReferenceTypes())

        bf.duplicates.invokeFactory(type_name='ArticleReference', id='test1')
        bf.duplicates.invokeFactory(type_name='ArticleReference', id='test2')

        fti.allowed_content_types = ()

        test1 = bf.duplicates.test1
        test1.edit(title='Test1', publication_year='2001', journal='journal1')
        self.failUnless(test1.Title() == 'Test1')
        self.failUnless(test1.getPublication_year() == '2001')
        self.failUnless(test1.getJournal() == 'journal1')
        test1.bibliography_entry_cookId()

        test2 = bf.duplicates.test2
        test2.edit(title='Test2', publication_year='2002', journal='journal2')
        self.failUnless(test2.Title() == 'Test2')
        self.failUnless(test2.getPublication_year() == '2002')
        self.failUnless(test2.getJournal() == 'journal2')
        test2.bibliography_entry_cookId()

        for dup_id in bf.duplicates.contentIds():
            self.failUnless(dup_id == bf.duplicates[dup_id].UID())

    def testDuplicatesFolderIdCooking(self):
        bf = self.getEmptyBibFolder(id='dup_bf')
        df = bf.getDuplicatesFolder()
        tt = bf.portal_types
        fti = tt[bf.duplicates.portal_type]

    def testObjectsMovedToAnotherBibFolderBecomeLocalDuplicatesOfTargetBibFolder(self):

        bf1, bf2 = self.getTwoPopulatedBibFolders(id1='move_bf1', id2='move_bf2')
        objs = bf1.manage_cutObjects(['Lutz2001'])
        bf2.manage_pasteObjects(objs)
        self.failUnless(len(bf1.contentIds()) == 2)
        self.failUnless(len(bf2.contentIds()) == 4)
        self.failUnless('duplicates' in bf2.contentIds())

        objs = bf1.manage_cutObjects(['McKay2003'])
        bf2.manage_pasteObjects(objs)
        self.failUnless(len(bf1.contentIds()) == 1)
        self.failUnless(len(bf2.contentIds()) == 4)
        self.failUnless('duplicates' in bf2.contentIds())

        for dup_id in bf2.duplicates.contentIds():
            self.failUnless(dup_id == bf2.duplicates[dup_id].UID())

    def testObjectsCopiedToAnotherBibFolderBecomeLocalDuplicatesOfTargetBibFolder(self):

        bf1, bf2 = self.getTwoPopulatedBibFolders(id1='copy_bf1', id2='copy_bf2')
        objs = bf1.manage_copyObjects(['Lutz2001'])
        bf2.manage_pasteObjects(objs)
        self.failUnless(len(bf1.contentIds()) == 3)
        self.failUnless(len(bf2.contentIds()) == 4)
        self.failUnless('duplicates' in bf2.contentIds())

        objs = bf1.manage_copyObjects(['McKay2003'])
        bf2.manage_pasteObjects(objs)
        self.failUnless(len(bf1.contentIds()) == 3)
        self.failUnless(len(bf2.contentIds()) == 4)
        self.failUnless('duplicates' in bf2.contentIds())

        for dup_id in bf2.duplicates.contentIds():
            self.failUnless(dup_id == bf2.duplicates[dup_id].UID())

    def testObjectsWithAssocPdfFilesMovedToAnotherBibFolderBecomeLocalDuplicatesOfTargetBibFolder(self):

        bf1, bf2 = self.getTwoPopulatedBibFolders(id1='move_bf1_pdf', id2='move_bf2_pdf')
        bf1.setSynchronizePdfFileAttributes(True)
        bf2.setSynchronizePdfFileAttributes(True)
        bf1.setCookIdsAfterBibRefEdit(True)
        bf2.setCookIdsAfterBibRefEdit(True)
        bib_tool = self.portal.portal_bibliography

        # upload some PDF files...
        pdffile_source = [
            dummy.File(filename='cmfbat-pdffile1.pdf', data=open(setup.CMFBAT_TEST_PDF_1, 'r').read(),),
            dummy.File(filename='cmfbat-pdffile2.pdf', data=open(setup.CMFBAT_TEST_PDF_2, 'r').read(),),
            dummy.File(filename='cmfbat-pdffile3.pdf', data=open(setup.CMFBAT_TEST_PDF_3, 'r').read(),),
        ]
        idx1 = idx2 = 0
        for item1, item2  in zip(bf1.contentValues(), bf2.contentValues()):
            if item1.portal_type in bib_tool.getReferenceTypes():
                item1.setUploaded_pdfFile(pdffile_source[idx1])
                idx1 += 1
            if item2.portal_type in bib_tool.getReferenceTypes():
                item2.setUploaded_pdfFile(pdffile_source[idx2])
                idx2 += 1

        # now do the cut+paste stuff again, but also check for the occurrence of the PDF file
        objs = bf1.manage_cutObjects(['Lutz2001'])
        bf2.manage_pasteObjects(objs)
        # expecting McKay2003, Lattier2001 and "pdfs" in bf1
        self.failUnless(len(bf1.contentIds()) == 3)
        self.failUnless('pdfs' in bf1.contentIds())
        # expecting McKay2003.pdf, Lattier2001.pdf in bf1.pdfs
        self.failUnless(len(bf1.pdfs.contentIds()) == 2)
        # expecting Lutz2001, McKay2003, Lattier2001, "pdfs" and "duplicates" in bf2
        self.failUnless(len(bf2.contentIds()) == 5)
        self.failUnless('pdfs' in bf2.contentIds())
        self.failUnless('duplicates' in bf2.contentIds())
        # expecting duplicate-Lutz2001 in bf2.duplicates
        self.failUnless(len(bf2.duplicates.contentIds()) == 1)
        # expecting Lutz2001.pdf, McKay2003.pdf, Lattier2001.pdf and <UID>.pdf for duplicate-Lutz2001 in bf2.pdfs
        self.failUnless(len(bf2.pdfs.contentIds()) == 4)

        objs = bf1.manage_cutObjects(['McKay2003'])
        bf2.manage_pasteObjects(objs)
        # expecting things dito
        self.failUnless(len(bf1.contentIds()) == 2)
        self.failUnless(len(bf2.contentIds()) == 5)
        self.failUnless(len(bf1.pdfs.contentIds()) == 1)
        self.failUnless(len(bf2.pdfs.contentIds()) == 5)
        self.failUnless(len(bf2.duplicates.contentIds()) == 2)

        for dup_id in bf2.duplicates.contentIds():
            self.failUnless(dup_id == bf2.duplicates[dup_id].UID())
            # uid cooker for duplicates' PDF files (so they do not interfere with other bibref items' ID cookers...)
            self.failUnless('%s.pdf' % dup_id in bf2.pdfs.contentIds())

    def testObjectsWithAssocPdfFilesCopiedToAnotherBibFolderBecomeLocalDuplicatesOfTargetBibFolder(self):

        bf1, bf2 = self.getTwoPopulatedBibFolders(id1='copy_bf1_pdf', id2='copy_bf2_pdf')
        bf1.setSynchronizePdfFileAttributes(True)
        bf2.setSynchronizePdfFileAttributes(True)
        bf1.setCookIdsAfterBibRefEdit(True)
        bf2.setCookIdsAfterBibRefEdit(True)
        bib_tool = self.portal.portal_bibliography

        # upload some PDF files...
        pdffile_source = [
            dummy.File(filename='cmfbat-pdffile1.pdf', data=open(setup.CMFBAT_TEST_PDF_1, 'r').read(),),
            dummy.File(filename='cmfbat-pdffile2.pdf', data=open(setup.CMFBAT_TEST_PDF_2, 'r').read(),),
            dummy.File(filename='cmfbat-pdffile3.pdf', data=open(setup.CMFBAT_TEST_PDF_3, 'r').read(),),
        ]
        idx1 = idx2 = 0
        for item1, item2  in zip(bf1.contentValues(), bf2.contentValues()):
            if item1.portal_type in bib_tool.getReferenceTypes():
                item1.setUploaded_pdfFile(pdffile_source[idx1])
                idx1 += 1
            if item2.portal_type in bib_tool.getReferenceTypes():
                item2.setUploaded_pdfFile(pdffile_source[idx2])
                idx2 += 1

        # now do the cut+paste stuff again, but also check for the occurrence of the PDF file
        objs = bf1.manage_copyObjects(['Lutz2001'])
        bf2.manage_pasteObjects(objs)
        # expecting Lutz2001, McKay2003, Lattier2001 and "pdfs" in bf1
        self.failUnless(len(bf1.contentIds()) == 4)
        self.failUnless('pdfs' in bf1.contentIds())
        # expecting Lutz2001.pdf, McKay2003.pdf, Lattier2001.pdf in bf1.pdfs
        self.failUnless(len(bf1.pdfs.contentIds()) == 3)
        # expecting Lutz2001, McKay2003, Lattier2001, "pdfs" and "duplicates" in bf2
        self.failUnless(len(bf2.contentIds()) == 5)
        self.failUnless('pdfs' in bf2.contentIds())
        self.failUnless('duplicates' in bf2.contentIds())
        # expecting duplicate-Lutz2001 in bf2.duplicates
        self.failUnless(len(bf2.duplicates.contentIds()) == 1)
        # expecting Lutz2001.pdf, McKay2003.pdf, Lattier2001.pdf and <UID>.pdf for duplicate-Lutz2001 in bf2.pdfs
        self.failUnless(len(bf2.pdfs.contentIds()) == 4)

        objs = bf1.manage_copyObjects(['McKay2003'])
        bf2.manage_pasteObjects(objs)
        # expecting things dito
        self.failUnless(len(bf1.contentIds()) == 4)
        self.failUnless(len(bf2.contentIds()) == 5)
        self.failUnless(len(bf1.pdfs.contentIds()) == 3)
        self.failUnless(len(bf2.pdfs.contentIds()) == 5)
        self.failUnless(len(bf2.duplicates.contentIds()) == 2)

        for dup_id in bf2.duplicates.contentIds():
            self.failUnless(dup_id == bf2.duplicates[dup_id].UID())
            # uid cooker for duplicates' PDF files (so they do not interfere with other bibref items' ID cookers...)
            self.failUnless('%s.pdf' % dup_id in bf2.pdfs.contentIds())

    def testObjectsWithAssocPdfFilesManuallyDeletedFromDuplicatesFolder(self):

        bf = self.getPopulatedBibFolder(id='del_bf_pdf')
        bf.setSynchronizePdfFileAttributes(True)
        bf.setCookIdsAfterBibRefEdit(True)
        bib_tool = self.portal.portal_bibliography

        # upload some PDF files...
        pdffile_source = [
            dummy.File(filename='cmfbat-pdffile1.pdf', data=open(setup.CMFBAT_TEST_PDF_1, 'r').read(),),
            dummy.File(filename='cmfbat-pdffile2.pdf', data=open(setup.CMFBAT_TEST_PDF_2, 'r').read(),),
            dummy.File(filename='cmfbat-pdffile3.pdf', data=open(setup.CMFBAT_TEST_PDF_3, 'r').read(),),
        ]
        idx = 0
        for item in bf.contentValues():
            if item.portal_type in bib_tool.getReferenceTypes():
                item.setUploaded_pdfFile(pdffile_source[idx])
                idx += 1

        # now do some copy+paste and then delete
        objs = bf.manage_copyObjects(['Lutz2001'])
        bf.manage_pasteObjects(objs)
        # expecting Lutz2001, McKay2003, Lattier2001, "pdfs" and "duplicates" in bf
        self.failUnless(len(bf.contentIds()) == 5)
        self.failUnless('pdfs' in bf.contentIds())
        self.failUnless('duplicates' in bf.contentIds())
        # expecting Lutz2001.pdf, McKay2003.pdf, Lattier2001.pdf and <UID of duplicate-Lutz2001.pdf> in bf.pdfs
        self.failUnless(len(bf.pdfs.contentIds()) == 4)
        # expecting duplicate-Lutz2001 in bf.duplicates
        self.failUnless(len(bf.duplicates.contentIds()) == 1)

        dup_bref_item = bf.duplicates.contentValues()[0]
        self.failUnless('%s.pdf' % dup_bref_item.UID() in bf.pdfs.contentIds())

        bf.duplicates.manage_delObjects([dup_bref_item.UID()])
        self.failUnless(len(bf.contentIds()) == 5)
        self.failUnless(len(bf.pdfs.contentIds()) == 3)
        self.failUnless(len(bf.duplicates.contentIds()) == 0)
        pdf_ids = bf.pdfs.contentIds()
        pdf_ids.sort()
        self.failUnless(tuple(pdf_ids) == ('Lattier2001.pdf', 'Lutz2001.pdf', 'McKay2003.pdf'))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestBibliographyFolder))
    return suite

if __name__ == '__main__':
    framework()
