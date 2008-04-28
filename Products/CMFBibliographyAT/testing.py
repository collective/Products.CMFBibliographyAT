import transaction

from AccessControl.SecurityManagement import newSecurityManager
from Testing import ZopeTestCase
from Products.PloneTestCase import ptc, layer

from Products.CMFPlone import utils

from tests import setup

class Layer(object):

    def __init__(self, *bases):
        self.__bases__ = bases
        self.__name__ = self.__class__.__name__

    def start(self):
        self.app = ZopeTestCase.app()
        uf = self.app.acl_users
        user = uf.getUserById(ptc.portal_owner)
        if not hasattr(user, 'aq_base'):
            user = user.__of__(uf)
        newSecurityManager(None, user)
        self.portal = getattr(self.app, ptc.portal_name)
        pm = self.portal.portal_membership
        self.folder = pm.getHomeFolder(ptc.default_user)

    def finish(self):
        transaction.commit()
        ZopeTestCase.close(self.app)

class EmptyBibFolder(Layer):

    def setUp(self):
        self.start()
        utils._createObjectByType(
            type_name="BibliographyFolder",
            container=self.folder, id='bib_folder')
        self.finish()

emptyBibFolder = EmptyBibFolder(layer.PloneSite)

class MedlineBibFolder(EmptyBibFolder):

    def setUp(self):
        self.start()
        bf = self.folder.bib_folder
        med_source = open(setup.MEDLINE_TEST_MED, 'r').read()
        bf.processImport(med_source, 'medline_test.med')
        self.finish()

medlineBibFolder = MedlineBibFolder(emptyBibFolder)

class BibtexBibFolder(EmptyBibFolder):

    def setUp(self):
        self.start()
        bf = self.folder.bib_folder
        bib_source = open(setup.BIBTEX_TEST_BIB, 'r').read()
        bf.processImport(bib_source, 'bibtex_test.bib')
        self.finish()

bibtexBibFolder = BibtexBibFolder(emptyBibFolder)
