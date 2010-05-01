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

class TestReferenceIdCooking(PloneTestCase.PloneTestCase):
    '''Test the id cooking mechanism'''

    # some utility methods

    def getRawBibFolder(self):
        uf = self.folder
        uf.invokeFactory(type_name = "BibliographyFolder",
                         id = 'bib_folder')
        bf = getattr(uf, 'bib_folder')
        return bf

    def getEmptyBibFolder(self,
                          idcooker_id='etal',
                          use_pids_on_import=True,
                          cook_ids_on_bibref_creation=False,
                          cook_ids_after_bibref_edit=False):
        uf = self.folder
        uf.invokeFactory(type_name = "BibliographyFolder",
                         id = 'bib_folder')
        bf = getattr(uf, 'bib_folder')
        bf.setReferenceIdCookingMethod(value=idcooker_id)
        bf.setUseParserIdsOnImport(value=use_pids_on_import)
        bf.setCookIdsOnBibRefCreation(value=cook_ids_on_bibref_creation)
        bf.setCookIdsAfterBibRefEdit(value=cook_ids_after_bibref_edit)
        return bf

    def getPopulatedBibFolder(self,
                              idcooker_id='etal',
                              use_pids_on_import=True,
                              cook_ids_on_bibref_creation=False,
                              cook_ids_after_bibref_edit=False):
        bf = self.getEmptyBibFolder()
        bf.setReferenceIdCookingMethod(value=idcooker_id)
        bf.setUseParserIdsOnImport(value=use_pids_on_import)
        bf.setCookIdsOnBibRefCreation(value=cook_ids_on_bibref_creation)
        bf.setCookIdsAfterBibRefEdit(value=cook_ids_after_bibref_edit)
        idcooking_source = open(setup.IDCOOKING_TEST_BIB, 'r').read()
        bf.processImport(idcooking_source, 'idcooking_test.bib', input_encoding='iso-8859-15')
        return bf

    def processBibRefObject(self, bibfolder=None, bibref_item=None,
                            template_no=None, bibref_id=None, **kwargs):

        content_templates = (
                { 'type_name': 'BookReference',
                  'id': 'bookreference.2006-08-28.8979763101',
                  'authors': ({'lastname': 'Mueller',
                               'firstname': 'Felix',
                               'middlename': ''},
                              {'lastname': 'Leupelt',
                               'firstname': 'Maren',
                               'middlename': ''}, ),
                  'title': 'Eco Targets, Goal Functions, and Orientors',
                  'publication_year': '1997',
                  'publisher': 'Springer-Verlag',
                  'address': 'Berlin, Heidelberg, New York',
                },
                { 'type_name': 'ArticleReference',
                  'id': 'articlereference.2006-08-27.8979763101',
                  'authors': ({'lastname': 'Barkmann',
                               'firstname': 'Jan',
                               'middlename': ''},
                              {'lastname': 'Baumann',
                               'firstname': 'R.',
                               'middlename': ''},
                              {'lastname': 'Meyer',
                               'firstname': 'U.',
                               'middlename': ''},
                              {'lastname': 'Mueller',
                               'firstname': 'Felix',
                               'middlename': ''},
                              {'lastname': 'Windhorst',
                               'firstname': 'Wilhelm',
                               'middlename': ''}, ),
                  'title': 'On the role of Ecosystem Self-Organisation '\
                  'in Landscape Management - A Response',
                  'publication_year': '2001',
                  'journal': 'GAIA',
                  'volume': '10',
                  'number': '4',
                  'pages': '247-248',
                },
                { 'type_name': 'ArticleReference',
                  'id': 'articlereference.2006-08-26.8979763101',
                  'authors': ({'lastname': 'Dolnik',
                               'firstname': 'Christian',
                               'middlename': ''}, ),
                  'title': 'Agonimia allobata und Nachweise anderer seltener Flechten aus Schleswig-Holstein',
                  'publication_year': '2005',
                  'journal': 'Kieler Notizen Pflanzenkd. Schleswig-Holstein Hamb.',
                  'volume': '33',
                  'pages': '90-97',
                },
                { 'type_name': 'BookletReference',
                  'id': 'bookletreference.2006-08-25.8979763101',
                  'title': 'Kleines Plone Handbuch',
                  'publication_year': '2005',
                },
        )
        if bibfolder is not None:

            values = {}
            if template_no is not None:
                values = content_templates[template_no]

            if bibref_id is None and values.has_key('id'):
                bibref_id = values['id']

            # new bibref item in bibfolder
            if bibref_item is None:
                bibfolder.invokeFactory(type_name=values['type_name'],
                                        id=bibref_id )
                bibref_item = getattr(bibfolder, bibref_id)

            if values.has_key('id'):
               del values['id']
            if values.has_key('type_name'):
                del values['type_name']

            # replace **kwargs in values
            for key in kwargs.keys():

                # the authors field behaves weird, comes in as tuple-in-tuple
                if key in [ field.getName() for field in \
                            bibref_item.Schema().fields() ] \
                            and (key == 'authors'):
                    values[key] = kwargs[key][0]
                elif key in [ field.getName() for field in \
                              bibref_item.Schema().fields() ]:
                    values[key] = kwargs[key]

            bibref_item.processForm(values=values)

    # the individual tests

    def test_BibliographyToolIdCookingDefaults(self):
        bib_tool = self.portal.portal_bibliography
        default_idcooker_id = bib_tool.getDefaultIdCooker().getId()
        use_pids_on_import = bib_tool.useParserIdsOnImport()
        cook_ids_on_bibref_creation = bib_tool.cookIdsOnBibRefCreation()
        cook_ids_after_bibref_edit = bib_tool.cookIdsAfterBibRefEdit()

        self.failUnless(default_idcooker_id == 'etal')
        self.failUnless(use_pids_on_import == True)
        self.failUnless(cook_ids_on_bibref_creation == False)
        self.failUnless(cook_ids_after_bibref_edit == False)

    def test_BibliographyToolIdCookingSetup(self):

        self.setRoles(('Manager',))
        bib_tool = self.portal.portal_bibliography
        request = { 'default_idcooker_id': 'abbrev',
                    'use_pids_on_import': False,
                    'cook_ids_on_bibref_creation': True,
                    'cook_ids_after_bibref_edit': True, }
        for key in request.keys():
            self.app.REQUEST.set(key, request[key])
        bib_tool.prefs_bibliography_idcooking()

        default_idcooker_id = bib_tool.getDefaultIdCooker().getId()
        use_pids_on_import = bib_tool.useParserIdsOnImport()
        cook_ids_on_bibref_creation = bib_tool.cookIdsOnBibRefCreation()
        cook_ids_after_bibref_edit = bib_tool.cookIdsAfterBibRefEdit()

        self.failUnless(default_idcooker_id == 'abbrev')
        self.failUnless(use_pids_on_import == False)
        self.failUnless(cook_ids_on_bibref_creation == True)
        self.failUnless(cook_ids_after_bibref_edit == True)

    def test_BibliographyFolderIdCookingWithBibToolDefaults(self):

        bib_tool = self.portal.portal_bibliography
        default_idcooker_id = bib_tool.getDefaultIdCooker().getId()
        use_pids_on_import = bib_tool.useParserIdsOnImport()
        cook_ids_on_bibref_creation = bib_tool.cookIdsOnBibRefCreation()
        cook_ids_after_bibref_edit = bib_tool.cookIdsAfterBibRefEdit()

        bf = self.getRawBibFolder()

        self.failUnless(default_idcooker_id == bf.getReferenceIdCookingMethod())
        self.failUnless(use_pids_on_import == bf.getUseParserIdsOnImport())
        self.failUnless(cook_ids_on_bibref_creation == bf.getCookIdsOnBibRefCreation())
        self.failUnless(cook_ids_after_bibref_edit == bf.getCookIdsAfterBibRefEdit())

    def test_BibliographyFolderIdCookingWithBibToolCustomized(self):

        self.setRoles(('Manager',))
        bib_tool = self.portal.portal_bibliography
        request = { 'default_idcooker_id': 'abbrev',
                    'use_pids_on_import': False,
                    'cook_ids_on_bibref_creation': True,
                    'cook_ids_after_bibref_edit': True, }
        for key in request.keys():
            self.app.REQUEST.set(key, request[key])
        bib_tool.prefs_bibliography_idcooking()

        default_idcooker_id = bib_tool.getDefaultIdCooker().getId()
        use_pids_on_import = bib_tool.useParserIdsOnImport()
        cook_ids_on_bibref_creation = bib_tool.cookIdsOnBibRefCreation()
        cook_ids_after_bibref_edit = bib_tool.cookIdsAfterBibRefEdit()

        bf = self.getRawBibFolder()

        self.failUnless('abbrev' == bf.getReferenceIdCookingMethod())
        self.failUnless(False == bf.getUseParserIdsOnImport())
        self.failUnless(True == bf.getCookIdsOnBibRefCreation())
        self.failUnless(True == bf.getCookIdsAfterBibRefEdit())

    def test_ReferenceIdCookingOnBibRefCreation(self):

        bf = self.getEmptyBibFolder(idcooker_id='abbrev',
                                    cook_ids_on_bibref_creation=True)

        self.processBibRefObject(bibfolder=bf, template_no=0)
        self.processBibRefObject(bibfolder=bf, template_no=1)
        self.processBibRefObject(bibfolder=bf, template_no=2)
        contentIds = bf.objectIds()
        self.failUnless( 'ML1997' in contentIds )
        self.failUnless( 'BBMMW2001' in contentIds )
        self.failUnless( 'Dol2005' in contentIds )

    def test_NoReferenceIdCookingOnBibRefCreation(self):

        bf = self.getEmptyBibFolder(idcooker_id='abbrev',
                                    cook_ids_on_bibref_creation=False)

        self.processBibRefObject(bibfolder=bf, template_no=0)
        self.processBibRefObject(bibfolder=bf, template_no=1)
        self.processBibRefObject(bibfolder=bf, template_no=2)
        ## rr: note added in passing: this doesn't test anything, does it?
        self.failUnless( 'bookreference.2006-08-28.8979763101' in \
                         bf.contentIds() )
        self.failUnless( 'articlereference.2006-08-27.8979763101' in \
                         bf.contentIds() )
        self.failUnless( 'articlereference.2006-08-26.8979763101' in \
                         bf.contentIds() )

    def test_MyIdOnBibRefCreation(self):

        bf = self.getEmptyBibFolder(idcooker_id='abbrev',
                                    cook_ids_on_bibref_creation=False)

        self.processBibRefObject(bibfolder=bf,
                                 template_no=0,
                                 bibref_id='myid0', )
        self.processBibRefObject(bibfolder=bf,
                                 template_no=1,
                                 bibref_id='myid1', )
        self.processBibRefObject(bibfolder=bf,
                                 template_no=2,
                                 bibref_id='myid2', )
        contentIds = bf.objectIds()
        self.failUnless( 'myid0' in contentIds )
        self.failUnless( 'myid1' in contentIds )
        self.failUnless( 'myid2' in contentIds )

    def test_ReferenceIdCookingAfterBibRefEdit(self):

        bf = self.getEmptyBibFolder(idcooker_id='abbrev',
                                    cook_ids_on_bibref_creation=True,
                                    cook_ids_after_bibref_edit=True)

        self.processBibRefObject(bibfolder=bf, template_no=0)
        self.failUnless( 'ML1997' in bf.contentIds() )

        ml1997 = getattr(bf, 'ML1997')
        edit_authors = ({'lastname': 'Fueller',
                         'firstname': 'Melix',
                         'middlename': ''},
                        {'lastname': 'Meupelt',
                         'firstname': 'Laren',
                         'middlename': ''}, ),
        self.processBibRefObject(bibfolder=bf,
                                 bibref_item=ml1997,
                                 authors=edit_authors, )

        self.failUnless( 'FM1997' in bf.contentIds() )

    def test_NoReferenceIdCookingAfterBibRefEdit(self):

        bf = self.getEmptyBibFolder(idcooker_id='abbrev',
                                    cook_ids_on_bibref_creation=True,
                                    cook_ids_after_bibref_edit=False)

        self.processBibRefObject(bibfolder=bf, template_no=0)
        self.failUnless( 'ML1997' in bf.contentIds() )

        ml1997 = getattr(bf, 'ML1997')
        edit_authors = ({'lastname': 'Fueller',
                         'firstname': 'Melix',
                         'middlename': ''},
                        {'lastname': 'Meupelt',
                         'firstname': 'Laren',
                         'middlename': ''}, ),
        self.processBibRefObject(bibfolder=bf,
                                 bibref_item=ml1997,
                                 authors=edit_authors, )

        self.failUnless( 'ML1997' in bf.contentIds() )

    def test_NoAuthorReferenceIdCookerBehaviour(self):

        bf = self.getPopulatedBibFolder(idcooker_id='abbrev',
                                        cook_ids_on_bibref_creation=True)

        self.processBibRefObject(bibfolder=bf, template_no=3)
        self.failUnless( 'nobody2005' in bf.contentIds() )

    def test_NextIdReferenceIdCookerBehaviour(self):

        bf = self.getEmptyBibFolder(idcooker_id='abbrev',
                                    cook_ids_on_bibref_creation=True,
                                    cook_ids_after_bibref_edit=True)

        self.processBibRefObject(bibfolder=bf, template_no=0,)
        item0 = getattr(bf, 'ML1997')
        self.processBibRefObject(bibfolder=bf, template_no=1,)
        item1 = getattr(bf, 'BBMMW2001')
        self.processBibRefObject(bibfolder=bf, template_no=2,)
        item2 = getattr(bf, 'Dol2005')
        self.processBibRefObject(bibfolder=bf, template_no=3,)
        item3 = getattr(bf, 'nobody2005')
        edit_authors = ({'lastname': 'Gabriel',
                         'firstname': 'Mike',
                         'middlename': ''}, ),
        self.processBibRefObject(bibfolder=bf,
                                 bibref_item=item0,
                                 authors=edit_authors,
                                 publication_year='2006' )
        self.processBibRefObject(bibfolder=bf,
                                 bibref_item=item1,
                                 authors=edit_authors,
                                 publication_year='2006' )
        self.processBibRefObject(bibfolder=bf,
                                 bibref_item=item2,
                                 authors=edit_authors,
                                 publication_year='2006' )
        contentIds = bf.objectIds()
        self.failUnless( 'Gab2006' in contentIds )
        self.failUnless( 'Gab2006a' in contentIds )
        self.failUnless( 'Gab2006b' in contentIds )
        self.failUnless( 'nobody2005' in contentIds )

        # remove item 1
        bf.manage_delObjects(['Gab2006a',])

        # editing item 0 should leave id where it is
        # (as opposed to appending it to the chain of nextIDs)
        self.processBibRefObject(bibfolder=bf,
                                 bibref_item=item0,
                                 title='REMOVED' )
        self.failUnless( item0.getId() == 'Gab2006' )

        # same authors for item 3 should result in Gab2006a
        # (as item 1 has been removed from bibfolder)
        self.processBibRefObject(bibfolder=bf,
                                 bibref_item=item3,
                                 template_no=3,
                                 authors=edit_authors,
                                 publication_year='2006' )
        self.failUnless( item3.getId() == 'Gab2006a' )

        # remove item 3, edit item 2: Gab2006b -> Gab2006a
        bf.manage_delObjects(['Gab2006a',])
        self.processBibRefObject(bibfolder=bf,
                                 bibref_item=item2,
                                 template_no=2,
                                 authors=edit_authors,
                                 publication_year='2006' )
        self.failUnless( item2.getId() == 'Gab2006a' )


    def test_ReferenceIdCookerUsePIDsOnImport(self):

        bf = self.getPopulatedBibFolder(use_pids_on_import=True)
        contentIds = bf.objectIds()
        self.failUnless( 'GrootBruinsBreeuwer2003' in contentIds )
        self.failUnless( 'AlibardiThompson2003' in contentIds )
        self.failUnless( 'CokeHunterIsazaKochGoatleyCarpenter2003' in \
                         contentIds )
        self.failUnless( 'TrapeMane2002' in contentIds )
        self.failUnless( 'Dolnik2005' in contentIds )

    def test_EtAlReferenceIdCooker(self):

        bf = self.getPopulatedBibFolder(idcooker_id='etal',
                                        use_pids_on_import=False)
        contentIds = bf.objectIds()
        # This test will fail with all Plone 3.0.x versions using plone.i18n
        # 1.0 and 1.0.1. Plone 3.0.4 is the first 3.0 release which does not
        # lowercase ids for filenames.
        self.failUnless( 'GrootEtAl2003' in contentIds )
        self.failUnless( 'AlibardiThompson2003' in contentIds )
        self.failUnless( 'CokeEtAl2003' in contentIds )
        self.failUnless( 'TrapeMane2002' in contentIds )
        self.failUnless( 'Dolnik2005' in contentIds )

    def test_AbbrevReferenceIdCooker(self):

        bf = self.getPopulatedBibFolder(idcooker_id='abbrev',
                                        use_pids_on_import=False)
        contentIds = bf.objectIds()
        self.failUnless( 'GBB2003' in contentIds )
        self.failUnless( 'AT2003' in contentIds )
        self.failUnless( 'CHIKGC2003' in contentIds )
        self.failUnless( 'TM2002' in contentIds )
        self.failUnless( 'Dol2005' in contentIds )

    def test_PloneReferenceIdCooker(self):

        bf = self.getPopulatedBibFolder(idcooker_id='plone',
                                        use_pids_on_import=False)
        objectIds = bf.objectIds()
        # This test will fail with Plone 3.0.x versions using plone.i18n
        # 1.0 and 1.0.1. Plone 3.0.4 is the first 3.0 release which allows
        # ids over 50 characters. See http://dev.plone.org/plone/changeset/18071
        self.failUnless( 'agonimia-allobata-und-nachweise-anderer-seltener-flechten-aus-schleswig-holstein' in objectIds )
        self.failUnless( 'molecular-genetic-evidence-for-parthenogenesis-in-the-burmese-python-python-molurus-bivittatus' in objectIds )
        self.failUnless( 'epidermal-differentiation-during-ontogeny-and-after-hatching-in-the-snake-liasis-fuscus-pythonidae-serpentes-reptilia-with-emphasis-on-the-formation-of-the-shedding-complex' in objectIds )
        self.failUnless( 'pharmacokinetics-and-tissue-concentrations-of-azithromycin-in-ball-pythons-python-regius' in objectIds )

        # This will require plone.i18n 1.0.2 or Plone 3.0.4.
        # See http://dev.plone.org/plone/changeset/18072
        self.failUnless( 'the-snakes-of-senegal-an-annotated-species-list' in bf.contentIds() )

    def test_UmlautNormalization(self):

        bf = self.getPopulatedBibFolder(idcooker_id='etal',
                                        use_pids_on_import=False)
        self.failUnless( 'OOAAUUoeoeaeaeuu2005' in bf.contentIds() )

    # end of the individual tests

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestReferenceIdCooking))
    return suite

if __name__ == '__main__':
    framework()
