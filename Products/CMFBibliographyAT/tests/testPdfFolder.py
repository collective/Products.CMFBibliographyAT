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
from Products.CMFBibliographyAT.tests import setup, dummy

class TestPdfFolder(PloneTestCase.PloneTestCase):
    '''Test the PDF File support in CMFBibliographyAT'''

    def afterSetUp(self):
        self._refreshSkinData()
        self.portal.portal_bibliography.enable_duplicates_manager = False

    # some utility methods

    def getEmptyBibFolder(self, id='bib_folder'):
        uf = self.folder
        uf.invokeFactory(type_name = "BibliographyFolder",
                         id = id)
        bf = getattr(uf, id)
        return bf

    def getPopulatedBibFolderWithEmptyPdfFolder(self, bf=None, id='bib_folder'):
        if bf is None:
            bf = self.getEmptyBibFolder(id=id)
        bref_source = open(setup.PDFFOLDER_TEST_BIB, 'r').read()
        bf.processImport(bref_source, 'pdffolder_test.bib')
        pf = bf.getPdfFolder()
        return bf, pf

    def getPopulatedBibFolderWithPopulatedPdfFolder(self, bf=None, id='bib_folder'):
        bf, pf = self.getPopulatedBibFolderWithEmptyPdfFolder(bf=bf, id=id)
        pdffile_source = [
                dummy.File(filename='cmfbat-pdffile1.pdf', data=open(setup.CMFBAT_TEST_PDF_1, 'r').read(),),
                dummy.File(filename='cmfbat-pdffile2.pdf', data=open(setup.CMFBAT_TEST_PDF_2, 'r').read(),),
                dummy.File(filename='cmfbat-pdffile3.pdf', data=open(setup.CMFBAT_TEST_PDF_3, 'r').read(),),
        ]
        idx=0
        for bref_id in bf.contentIds():
            if bref_id != 'pdfs':
                bref = getattr(bf, bref_id)
                bref.setUploaded_pdfFile(pdffile_source[idx])
                idx += 1

        return bf, pf

    def purgeBibFolders(self):

        for obj in self.folder.contentValues():

            if obj.portal_type in ('BibliographyFolder', 'LargeBibliographyFolder'):
                obj.aq_inner.aq_parent.manage_delObjects([obj.getId()])

    # the individual tests

    def test_PdfFolderCreation(self):
        uf = self.folder
        bf = self.getEmptyBibFolder()
        pdf_folder = bf.getPdfFolder()
        self.failUnless('pdfs' in bf.contentIds())
        self.failUnless(pdf_folder.portal_type == 'PDF Folder')

        self.purgeBibFolders()

    def test_PdfFileCreation(self):

        bf, pf = self.getPopulatedBibFolderWithEmptyPdfFolder()
        # PDF File creation should not work without changing PDF Folder fti
        try:
            pdf = pf.invokeFactory(type_name='PDF File', id='test_pdf1')
        except ValueError:
            pass
        self.failUnless('test_pdf1' not in pf.contentIds())

        pf.allowPdfFileCreation()
        # PDF File creation should now work
        try:
            pdf = pf.invokeFactory(type_name='PDF File', id='test_pdf2')
        except ValueError:
            pass
        self.failUnless('test_pdf2' in pf.contentIds())

        pf.disallowPdfFileCreation()
        # PDF File creation should not work any more
        try:
            pdf = pf.invokeFactory(type_name='PDF File', id='test_pdf3')
        except ValueError:
            pass
        self.failUnless('test_pdf3' not in pf.contentIds())

        self.purgeBibFolders()

    def test_pdfFileUpload(self):
        bf, pf = self.getPopulatedBibFolderWithPopulatedPdfFolder()

        # PDFs are there?
        self.failUnless('cmfbat-pdffile1.pdf' in pf.contentIds())
        self.failUnless('cmfbat-pdffile2.pdf' in pf.contentIds())
        self.failUnless('cmfbat-pdffile3.pdf' in pf.contentIds())

        # test references from bibref items to pdf files
        idx = 0
        for pdf_file in pf.contentValues():
            idx += 1
            bibref = getattr(bf, 'bibref%s' % idx)
            self.failUnless(pdf_file == bibref.getPdf_file() )

        # test back references from pdf files to bibref items
        idx = 0
        for pdf_file in pf.contentValues():
            idx += 1
            brefs = pdf_file.getBRefs('printable_version_of')
            self.failUnless(len(brefs) == 1)
            bref = brefs[0].getId()
            self.failUnless('bibref%s' % idx in bref) and ('pdffile%s' % idx in pdf_file.getId())

        self.purgeBibFolders()

    def test_pdfFileDeletion(self):
        bf, pf = self.getPopulatedBibFolderWithPopulatedPdfFolder()

        # PDFs are there?
        self.failUnless('cmfbat-pdffile1.pdf' in pf.contentIds())

        # test pdf file deletion via bibref entry field mutator
        bibref1 = getattr(bf, 'bibref1')
        bibref1.setUploaded_pdfFile(value='DELETE_FILE')
        self.failUnless('cmfbat-pdffile1.pdf' not in pf.contentIds())

        self.purgeBibFolders()

    def test_pdfFileReplacement(self):
        bf, pf = self.getPopulatedBibFolderWithPopulatedPdfFolder()

        # PDFs are there?
        self.failUnless('cmfbat-pdffile1.pdf' in pf.contentIds())

        # test pdf file replacement via bibref entry field mutator
        bibref1 = getattr(bf, 'bibref1')
        subst = dummy.File(filename='cmfbat-pdffile2.pdf', data=open(setup.CMFBAT_TEST_PDF_2, 'r').read(),),
        bibref1.setUploaded_pdfFile(value=subst)

        self.failUnless('cmfbat-pdffile2.pdf' in pf.contentIds())

        self.purgeBibFolders()

    def test_synchronizePdfFileIdsOnCreation(self):
        bf = self.getEmptyBibFolder()
        bf.setSynchronizePdfFileAttributes(value=True)
        bf, pf = self.getPopulatedBibFolderWithPopulatedPdfFolder(bf=bf)

        # PDFs are there? and have ID derived from bibref item?
        self.failUnless('bibref1.pdf' in pf.contentIds())
        self.failUnless('bibref2.pdf' in pf.contentIds())
        self.failUnless('bibref3.pdf' in pf.contentIds())

        self.purgeBibFolders()

    def test_synchronizePdfFileIdsAfterEdit(self):
        bf = self.getEmptyBibFolder()
        bf.setCookIdsAfterBibRefEdit(value=True)
        bf.setSynchronizePdfFileAttributes(value=True)
        bf, pf = self.getPopulatedBibFolderWithPopulatedPdfFolder(bf=bf)

        # PDFs are there?
        self.failUnless('bibref1.pdf' in pf.contentIds())


        bibref1 = getattr(bf, 'bibref1')
        pdffile1 = bibref1.getPdf_file()

        # edit authors and publication_year
        edit_authors = ({'lastname': 'Gabriel', 'firstname': 'Mike', 'middlename': ''}, )
        edit_publication_year = '2000'
        bibref1.processForm(values={'authors': edit_authors, 'publication_year': edit_publication_year,})

        # test IDs again:
        self.failUnless(bibref1.getId() == 'Gabriel2000')
        self.failUnless(pdffile1.getId() == 'Gabriel2000.pdf')

        self.purgeBibFolders()

    def test_deleteBibRefItemPlusPdfFile(self):
        bf = self.getEmptyBibFolder()
        bf.setSynchronizePdfFileAttributes(value=True)
        bf, pf = self.getPopulatedBibFolderWithPopulatedPdfFolder(bf=bf)

        # PDFs are there?
        self.failUnless('bibref1.pdf' in pf.contentIds())

        bibref1 = getattr(bf, 'bibref1')
        pdffile1 = bibref1.getPdf_file()

        bf.manage_delObjects([bibref1.getId(),])

        self.failUnless(bibref1 not in bf.contentValues())
        self.failUnless(pdffile1 not in pf.contentValues())

        self.purgeBibFolders()

    def test_noPdfFilesMeansNoPdfFolder(self):

        bf1, pf1 = self.getPopulatedBibFolderWithEmptyPdfFolder(id='bib_folder1')
        bf2 = self.getEmptyBibFolder(id='bib_folder2')
        bf3 = self.getEmptyBibFolder(id='bib_folder3')

        self.failUnless(len(pf1.contentIds()) == 0)
        self.failUnless('pdfs' not in bf2.contentIds())
        self.failUnless('pdfs' not in bf3.contentIds())

        # testing manage_pasteObjects
        copied_objs = bf1.manage_copyObjects(['bibref1', 'bibref2', 'bibref3',])
        bf2.manage_pasteObjects(copied_objs)
        cut_objs = bf1.manage_cutObjects(['bibref1', 'bibref2', 'bibref3',])
        bf3.manage_pasteObjects(cut_objs)

        self.failUnless('pdfs' not in bf2.contentIds())
        self.failUnless('pdfs' not in bf3.contentIds())

        # testing atct_edit with id cooking enabled
        bibref1 = getattr(bf3, 'bibref1')
        bf3.setCookIdsAfterBibRefEdit(value=True)
        edit_authors = ({'lastname': 'Gabriel', 'firstname': 'Mike', 'middlename': ''}, )
        edit_publication_year = '2000'
        bibref1.processForm(values={'authors': edit_authors, 'publication_year': edit_publication_year,})

        self.failUnless('Gabriel2000' in bf3.contentIds())
        self.failUnless('pdfs' not in bf3.contentIds())

        self.purgeBibFolders()

    def test_copyMultipleBibRefItemsPlusPdfFiles(self):
        bf1 = self.getEmptyBibFolder(id='bib_folder1')
        bf1.setSynchronizePdfFileAttributes(value=True)
        bf1, pf1 = self.getPopulatedBibFolderWithPopulatedPdfFolder(bf=bf1)
        bf2 = self.getEmptyBibFolder(id='bib_folder2')
        pf2 = bf2.getPdfFolder()

        # PDFs are there?
        self.failUnless('bibref1' in bf1.contentIds())
        self.failUnless('bibref2' in bf1.contentIds())
        self.failUnless('bibref3' in bf1.contentIds())
        self.failUnless('bibref1.pdf' in pf1.contentIds())
        self.failUnless('bibref2.pdf' in pf1.contentIds())
        self.failUnless('bibref3.pdf' in pf1.contentIds())

        bibref1 = getattr(bf1, 'bibref1')
        pdffile1 = bibref1.getPdf_file()
        bibref2 = getattr(bf1, 'bibref2')
        pdffile2 = bibref2.getPdf_file()
        bibref3 = getattr(bf1, 'bibref3')
        pdffile3 = bibref3.getPdf_file()

        # create copy in same bibfolder
        bf1._disable_duplicate_engine = True
        bf2._disable_duplicate_engine = True
        objs1 = bf1.manage_copyObjects([bibref1.getId(), bibref2.getId(), bibref3.getId(), ])
        bf1._disable_duplicate_engine = True
        bf1.manage_pasteObjects(objs1)
        bf2.manage_pasteObjects(objs1)
        objs2 = bf1.manage_cutObjects([bibref1.getId(), bibref2.getId(), bibref3.getId(), ])
        bf2.manage_pasteObjects(objs2)

        # bibref1 - bibref3 should be vanished from bf1
        self.failUnless(bibref1 not in bf1.contentValues())
        self.failUnless(pdffile1 not in pf1.contentValues())
        self.failUnless(bibref2 not in bf1.contentValues())
        self.failUnless(pdffile2 not in pf1.contentValues())
        self.failUnless(bibref3 not in bf1.contentValues())
        self.failUnless(pdffile3 not in pf1.contentValues())

        # bibref1 - bibref3 should now be in bf2
        self.failUnless(bibref1 in bf2.contentValues())
        self.failUnless(pdffile1 in pf2.contentValues())
        self.failUnless(bibref2 in bf2.contentValues())
        self.failUnless(pdffile2 in pf2.contentValues())
        self.failUnless(bibref3 in bf2.contentValues())
        self.failUnless(pdffile3 in pf2.contentValues())

        # ids of bibref1-bibref3 have changed to copy_of_...
        self.failUnless(bibref1.getId() == 'copy_of_bibref1')
        self.failUnless(bibref2.getId() == 'copy_of_bibref2')
        self.failUnless(bibref3.getId() == 'copy_of_bibref3')

        # all bibref items should be associated with the correct PDF files
        bf1_copy_of_bibref1 = getattr(bf1, 'copy_of_bibref1')
        pf1_copy_of_pdffile1 = bf1_copy_of_bibref1.getPdf_file()
        self.failUnless(bf1_copy_of_bibref1.getPdf_file() == pf1_copy_of_pdffile1)
        bf1_copy_of_bibref2 = getattr(bf1, 'copy_of_bibref2')
        pf1_copy_of_pdffile2 = bf1_copy_of_bibref2.getPdf_file()
        self.failUnless(bf1_copy_of_bibref2.getPdf_file() == pf1_copy_of_pdffile2)
        bf1_copy_of_bibref3 = getattr(bf1, 'copy_of_bibref3')
        pf1_copy_of_pdffile3 = bf1_copy_of_bibref3.getPdf_file()
        self.failUnless(bf1_copy_of_bibref3.getPdf_file() == pf1_copy_of_pdffile3)

        bf2_bibref1 = getattr(bf2, 'bibref1')
        pf2_pdffile1 = bf2_bibref1.getPdf_file()
        self.failUnless(bf2_bibref1.getPdf_file() == pf2_pdffile1)
        bf2_bibref2 = getattr(bf2, 'bibref2')
        pf2_pdffile2 = bf2_bibref2.getPdf_file()
        self.failUnless(bf2_bibref2.getPdf_file() == pf2_pdffile2)
        bf2_bibref3 = getattr(bf2, 'bibref3')
        pf2_pdffile3 = bf2_bibref3.getPdf_file()
        self.failUnless(bf2_bibref3.getPdf_file() == pf2_pdffile3)

        bf2_copy_of_bibref1 = getattr(bf2, 'copy_of_bibref1')
        pf2_copy_of_pdffile1 = bf2_copy_of_bibref1.getPdf_file()
        self.failUnless(bf2_copy_of_bibref1.getPdf_file() == pf2_copy_of_pdffile1)
        bf2_copy_of_bibref2 = getattr(bf2, 'copy_of_bibref2')
        pf2_copy_of_pdffile2 = bf2_copy_of_bibref2.getPdf_file()
        self.failUnless(bf2_copy_of_bibref2.getPdf_file() == pf2_copy_of_pdffile2)
        bf2_copy_of_bibref3 = getattr(bf2, 'copy_of_bibref3')
        pf2_copy_of_pdffile3 = bf2_copy_of_bibref3.getPdf_file()
        self.failUnless(bf2_copy_of_bibref3.getPdf_file() == pf2_copy_of_pdffile3)

        self.purgeBibFolders()

    def test_pasteBibRefItemPlusPdfFileSameBibFolder(self):
        bf = self.getEmptyBibFolder()
        bf.setSynchronizePdfFileAttributes(value=True)
        bf, pf = self.getPopulatedBibFolderWithPopulatedPdfFolder(bf=bf)

        # PDFs are there?
        self.failUnless('bibref1.pdf' in pf.contentIds())
        self.failUnless('bibref2.pdf' in pf.contentIds())

        bibref1 = getattr(bf, 'bibref1')
        pdffile1 = bibref1.getPdf_file()

        objs = bf.manage_copyObjects([bibref1.getId(),])
        bf.manage_pasteObjects(objs)

        # test IDs again:
        self.failUnless('copy_of_bibref1' in bf.contentIds())
        self.failUnless('copy_of_bibref1.pdf' in pf.contentIds())

        self.purgeBibFolders()

    def test_pasteBibRefItemPlusPdfFileDifferentBibFolders(self):
        bf1 = self.getEmptyBibFolder(id='bib_folder1')
        bf1.setSynchronizePdfFileAttributes(value=True)
        bf1, pf1 = self.getPopulatedBibFolderWithPopulatedPdfFolder(bf=bf1)
        bf2 = self.getEmptyBibFolder(id='bib_folder2')
        pf2 = bf2.getPdfFolder()

        # PDFs are there?
        self.failUnless('bibref1.pdf' in pf1.contentIds())
        self.failUnless('bibref2.pdf' in pf1.contentIds())

        bibref1 = getattr(bf1, 'bibref1')
        pdffile1 = bibref1.getPdf_file()
        bibref2 = getattr(bf1, 'bibref2')
        pdffile2 = bibref2.getPdf_file()

        # do copy+paste between two bibfolders
        objs = bf1.manage_copyObjects([bibref1.getId(),])
        bf2.manage_pasteObjects(objs)

        # check result of copy action
        self.failUnless(bibref1 in bf1.contentValues())
        self.failUnless(pdffile1 in pf1.contentValues())
        self.failUnless(bibref1.getPdf_file() == pdffile1)
        self.failUnless('bibref1' in bf2.contentIds())
        self.failUnless('bibref1.pdf' in pf2.contentIds())
        copy0_of_bibref1 = getattr(bf2, 'bibref1')
        copy0_of_pdffile1 = getattr(pf2, 'bibref1.pdf')
        self.failUnless(copy0_of_bibref1.getPdf_file() == copy0_of_pdffile1)

        bibref1 = getattr(bf1, 'bibref1')
        pdffile1 = bibref1.getPdf_file()

        # do cut+paste between 2 bibfolders
        objs = bf1.manage_cutObjects([bibref1.getId(),])
        bf2.manage_pasteObjects(objs)

        self.failUnless(bibref1 not in bf1.contentValues())
        self.failUnless(pdffile1 not in pf1.contentValues())
        self.failUnless('copy_of_bibref1' in bf2.contentIds())
        self.failUnless('copy_of_bibref1.pdf' in pf2.contentIds())
        self.failUnless(bibref1.getPdf_file() == pdffile1)
        copy1_of_bibref1 = getattr(bf2, 'copy_of_bibref1')
        copy1_of_pdffile1 = getattr(pf2, 'copy_of_bibref1.pdf')
        self.failUnless(copy1_of_bibref1.getPdf_file() == copy1_of_pdffile1)

        # do cut+paste between 2 bibfolders
        objs = bf1.manage_cutObjects([bibref2.getId(),])
        bf2.manage_pasteObjects(objs)

        self.failUnless(bibref2 not in bf1.contentValues())
        self.failUnless(pdffile2 not in pf1.contentValues())
        self.failUnless('bibref2' in bf2.contentIds())
        self.failUnless('bibref2.pdf' in pf2.contentIds())
        self.failUnless(bibref2.getPdf_file() == pdffile2)
        copy0_of_bibref2 = getattr(bf2, 'bibref2')
        copy0_of_pdffile2 = getattr(pf2, 'bibref2.pdf')
        self.failUnless(copy0_of_bibref2.getPdf_file() == copy0_of_pdffile2)

        self.purgeBibFolders()

    def test_pasteBibRefItemPlusPdfFileDifferentBibFoldersWithIdCooking(self):
        bf1 = self.getEmptyBibFolder(id='bib_folder1')
        bf1.setSynchronizePdfFileAttributes(value=True)
        bf1.setCookIdsOnBibRefCreation(value=True)
        bf1.setCookIdsAfterBibRefEdit(value=True)
        bf1.setUseParserIdsOnImport(value=False)
        bf1.setReferenceIdCookingMethod(value='etal')
        bf1, pf1 = self.getPopulatedBibFolderWithPopulatedPdfFolder(bf=bf1)
        bf2 = self.getEmptyBibFolder(id='bib_folder2')
        bf2.setSynchronizePdfFileAttributes(value=True)
        bf2.setCookIdsOnBibRefCreation(value=True)
        bf2.setCookIdsAfterBibRefEdit(value=True)
        bf2.setUseParserIdsOnImport(value=False)
        bf2.setReferenceIdCookingMethod(value='etal')
        pf2 = bf2.getPdfFolder()

        # PDFs are there?
        self.failUnless('Dolnik2005.pdf' in pf1.contentIds())
        self.failUnless('CokeEtAl2003.pdf' in pf1.contentIds())

        bibref1 = getattr(bf1, 'Dolnik2005')
        pdffile1 = bibref1.getPdf_file()
        bibref2 = getattr(bf1, 'CokeEtAl2003')
        pdffile2 = bibref2.getPdf_file()

        # do copy+paste between two bibfolders
        objs = bf1.manage_copyObjects([bibref1.getId(),])
        bf2.manage_pasteObjects(objs)

        # check result of copy action
        self.failUnless(bibref1 in bf1.contentValues())
        self.failUnless(pdffile1 in pf1.contentValues())
        self.failUnless(bibref1.getPdf_file() == pdffile1)
        self.failUnless('Dolnik2005' in bf2.contentIds())
        self.failUnless('Dolnik2005.pdf' in pf2.contentIds())
        copy0_of_bibref1 = getattr(bf2, 'Dolnik2005')
        copy0_of_pdffile1 = getattr(pf2, 'Dolnik2005.pdf')
        self.failUnless(copy0_of_bibref1.getPdf_file() == copy0_of_pdffile1)

        bibref1 = getattr(bf1, 'Dolnik2005')
        pdffile1 = bibref1.getPdf_file()

        # do cut+paste between 2 bibfolders, target ids already exist
        objs = bf1.manage_cutObjects([bibref1.getId(),])
        bf2.manage_pasteObjects(objs)

        self.failUnless(bibref1 not in bf1.contentValues())
        self.failUnless(pdffile1 not in pf1.contentValues())
        self.failUnless('Dolnik2005a' in bf2.contentIds())
        self.failUnless('Dolnik2005a.pdf' in pf2.contentIds())
        self.failUnless(bibref1.getPdf_file() == pdffile1)
        copy1_of_bibref1 = getattr(bf2, 'Dolnik2005a')
        copy1_of_pdffile1 = getattr(pf2, 'Dolnik2005a.pdf')
        self.failUnless(copy1_of_bibref1.getPdf_file() == copy1_of_pdffile1)

        # do cut+paste between 2 bibfolders, target ids unique
        objs = bf1.manage_cutObjects([bibref2.getId(),])
        bf2.manage_pasteObjects(objs)

        self.failUnless(bibref2 not in bf1.contentValues())
        self.failUnless(pdffile2 not in pf1.contentValues())
        self.failUnless('CokeEtAl2003' in bf2.contentIds())
        self.failUnless('CokeEtAl2003.pdf' in pf2.contentIds())
        self.failUnless(bibref2.getPdf_file() == pdffile2)
        copy0_of_bibref2 = getattr(bf2, 'CokeEtAl2003')
        copy0_of_pdffile2 = getattr(pf2, 'CokeEtAl2003.pdf')
        self.failUnless(copy0_of_bibref2.getPdf_file() == copy0_of_pdffile2)

        self.purgeBibFolders()

    # end of the individual tests

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPdfFolder))
    return suite

if __name__ == '__main__':
    framework()

