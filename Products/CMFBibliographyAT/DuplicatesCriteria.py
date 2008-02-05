##########################################################################
#                                                                        #
#          copyright (c) 2005  LOGILAB S.A. (Paris, FRANCE)              #
#          http://www.logilab.fr/ -- mailto:contact@logilab.fr           #
#                                                                        #
##########################################################################

# Zope stuff
import os.path, copy
from Globals import InitializeClass, MessageDialog, PersistentMapping
from Acquisition import Implicit
from ZODB.PersistentList import PersistentList
from AccessControl import ClassSecurityInfo

# CMF stuff
from Products.CMFCore.permissions import View, ManagePortal
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.Archetypes.ArchetypeTool import ArchetypeTool
from Products.Archetypes.utils import shasattr
from Products.CMFCore.utils import getToolByName

class DuplicatesCriteriaManager(Implicit):
    """ An object that contains :
    _criteria {bib_type : [criteria_name]}:
              contains all possible criteria (meta-data) for each bibliography type

    duplicates_criteria {bib_type : [criteria] } :
          contains criteria to be checked
          for duplication while importing for each bibliography type

    _nonmeta_criteria = ( 'reference_type', ) : contains criteria not
         comprised in meta_data

    _criteria_names = {'publication_authors' : 'authors'} : contains
         mappings for meta_data that need a special treatement like 'authors'

    _ignored_criteria = (critrias) : contains the names of  same meta_data
         like 'id' or 'allowDiscussion' to be filtered

    IMPORTANT : only 'authors','reference_type', 'publication_year',
      'title' are fully functional for now
    """

    _nonmeta_criteria = ( 'reference_type', )

    _default_duplicates_criteria  = (
        #FIXME - we may need a default value for these
                          'authors',
                          'reference_type',
                          'publication_year',
                          'title',)

    _criteria_names = {'publication_authors' : 'authors'}

    _ignored_criteria = ('allowDiscussion','id', )

    _www = os.path.join(os.path.dirname(__file__), 'www')

    security = ClassSecurityInfo()

    manage_options = (
        { 'label'  : 'Criteria',
          'action' : 'manageImportCriteria',
          },
        )

    security.declareProtected(ManagePortal,
                              'manageImportCriteria')
    manageImportCriteria = PageTemplateFile('manage_criteria', _www)

    def __init__(self):
        self._criteria = PersistentMapping()
        self.duplicates_criteria = PersistentMapping()
        self.criteriaUpdated = False

    def allCriteria(self, bib_type=None):

        # migrate CMFBAT v0.8 duplicates engine, mending a linguistic fault-pas
        if shasattr(self, '_criterias'):
            print 'CMFBibliographyAT: performing duplicates engine property update - v0.8 -> v0.9 (allCriteria of %s)' % '/'.join(self.getId())
            self._criteria = PersistentMapping()
            self.initCriteria()
            try: delattr(self, '_criterias')
            except: pass

        # this should have been performed by __init__ but after some product migrations we might want to check it here again
        if not shasattr(self, '_criteria'):
            self._criteria = PersistentMapping()
        if not shasattr(self, 'duplicates_criteria'):
            self.duplicates_criteria = PersistentMapping()

        # first call? initialize self._criteria (available duplicates criteria per reference type)
        if not self._criteria:
            self.initCriteria()

        # always init criteria, during development, schema changes, etc.
        self.initCriteria()
        if bib_type:
            try:
                self._criteria[bib_type]
            except KeyError:
                return False

            return self._criteria[bib_type]
        else:
            critKeys = self._criteria.keys()
            critKeys.sort()
            return [(key, self._criteria[key]) for key in critKeys]

    # fixing a linguistic fault-pas
    allcriterias = allCriteria

    def sortCriteriaByTitles(self, criteria, i18n_domain='cmfbibliographyat'):
        """ take a list of criteria tuples (as returned by allCriteria)
            and sort it according to their i18n names. used for nice display on screen
        """
        # sorting reference types by their i18n titles
        ref_types_i18n = [ (self.translate(domain='plone', msgid=criterion[0], default=criterion[0]), criterion[0]) for criterion in criteria ]
        ref_types_i18n.sort()
        ref_types = [ t[1] for t in ref_types_i18n ]

        # turning criteria into a dictionary
        criteria_dict = {}
        for ref_type in ref_types:
            criteria_dict[ref_type] = [ t[1] for t in criteria if t[0] == ref_type ][0]

        # sorting fields for each ref_type, standard fields always preceed non-standard fields
        standard_fields = ['authors', 'publication_year', 'title', 'reference_type',]
        for ref_type in ref_types:
            nonstandard_fields_i18n = [ (self.translate(domain=i18n_domain, msgid='label_%s' % field, default=field), field) for field in criteria_dict[ref_type] if field not in standard_fields ]
            nonstandard_fields_i18n.sort()
            nonstandard_fields = [ f[1] for f in nonstandard_fields_i18n ]
            criteria_dict[ref_type] = standard_fields + nonstandard_fields

        return [ (t, tuple(criteria_dict[t])) for t in ref_types ]

    def initCriteria(self):
        """ initialize the dictionary of import criteria
        for each bibliography type
        """
        # this is a migration 0.8 -> 0.9 fix:
        if not shasattr(self, '_criteria'):
            self._criteria = PersistentMapping()
        bib_tool = getToolByName(self, 'portal_bibliography')
        has = self._criteria_names.has_key
        for bib_type in bib_tool.getBibliographyContentTypes():
            bibname = bib_type['name']
            self._criteria[bibname] = [criteria for criteria in self._nonmeta_criteria]
            #adds all meta_data as criteria for each bibliography type
            for field in bib_type['schema'].fields():
                field_name = field.getName()
                if field_name in self._ignored_criteria:
                    continue
                if not shasattr(field, 'is_duplicates_criterion'):
                    continue
                if not field.is_duplicates_criterion:
                    continue
                if has(field_name):
                    self._criteria[bibname].append(self._criteria_names[field_name])
                else :
                    self._criteria[bibname].append(field_name)
            self._criteria[bibname].sort()
            self._criteria[bibname] = tuple(self._criteria[bibname])

    # fixing a linguistic fault-pas
    initCriterias = initCriteria

    def manage_changeCriteria(self, REQUEST):
        """Changes all criteria for a bibliography type given,
           called by management screen
         """
        reference_type = REQUEST.get('bibtype')
        has = REQUEST.has_key
        if reference_type != 'all':
            reference_types = [reference_type]
        else:
            bib_tool = getToolByName(self, 'portal_bibliography')
            reference_types = bib_tool.getReferenceTypes()

        for reference_type in reference_types:
            criteria = []
            for criterion in self._criteria[reference_type]:
                # the form bibtype_criterion is not useful for now, but it was set up
                # in case we want to use one submit input for all the bibliography types
                if has("%s_%s" % (reference_type, criterion)):
                    criteria.append(criterion)
            try: self.setCriteriaForType(reference_type, criteria)
            except:
                return MessageDialog(
                    title  ='Warning!',
                    message='Your changes have not been saved',
                    action ='manageImportCriteria')

        return MessageDialog(
                title  ='Success!',
                message='Your changes have been saved',
                action ='manageImportCriteria'
                )

    # fixing a linguistic fault-pas
    manage_changeCriterias = manage_changeCriteria

    def setCriteriaForType(self, bib_type, criteria):
        """update criteria for a bibliography type given"""
        self.duplicates_criteria[bib_type] = PersistentList(criteria)
        #FIXME may need to check if any change has been done
        self.criteriaUpdated = True
        return True

    # fixing a linguistic fault-pas
    setCriteriasForType = setCriteriaForType

    def setCriteria(self, duplicates_criteria):
        """update criteria for all bibliography types"""
        if not duplicates_criteria:
            duplicates_criteria = {}
            bib_tool = getToolByName(self, 'portal_bibliography')
            for key in bib_tool.getReferenceTypes():
                duplicates_criteria[key] = []
        self.duplicates_criteria = PersistentMapping(duplicates_criteria)
        self.criteriaUpdated = True

    # fixing a linguistic fault-pas
    setCriterias = setCriteria

    def isCriterionSelected(self, bib_type, criterion):
        return (criterion in self.getSelectedCriteria(bib_type)) and True or False

    def isNonMetaCriterion(self, criterion):
        return criterion in self._nonmeta_criteria

    # fixing a linguistic fault-pas
    isCriteriaSelected = isCriterionSelected

    def getSelectedCriteria(self, bib_type = None):

        # migrate CMFBAT v0.8 duplicates engine, mending a linguistic fault-pas
        if shasattr(self, 'imp_criterias'):
            print 'CMFBibliographyAT: performing duplicates engine property update - v0.8 -> v0.9 (getSelectedCriteria of %s)' % '/'.join(self.getId())
            self.duplicates_criteria = PersistentMapping()
            self.duplicates_criteria = copy.deepcopy(self.imp_criterias)
            self.criteriaUpdated = self.criteriasUpdated
            try: delattr(self, 'imp_criterias')
            except: pass
            try: delattr(self, 'criteriasUpdated')
            except: pass

        # first call? initialize self.duplicates_criteria
        bib_tool = getToolByName(self, 'portal_bibliography')
        if not shasattr(self, 'duplicates_criteria') or not self.duplicates_criteria:

            if self.getId() == bib_tool.getId():
                for reference_type in bib_tool.getReferenceTypes():
                    self.duplicates_criteria[reference_type] = PersistentList(self._default_duplicates_criteria)
                self.criteriaUpdated = True
            else:
                self.duplicates_criteria = bib_tool.getSelectedCriteria()
                self.criteriaUpdated = True

        if not shasattr(self, '_criteria') or not self._criteria:
            self.initCriteria()

        # make sure, our selected criteria are in sync with available criteria
        duplicates_criteria = {}
        for key in self._criteria.keys():
            duplicates_criteria[key] = [ criterion for criterion in self._criteria[key] if self.duplicates_criteria.has_key(key) and (criterion in self.duplicates_criteria[key]) ]

        if bib_type:
            try:
                duplicates_criteria[bib_type]
            except KeyError:
                return False
            return duplicates_criteria[bib_type]
        else:
            return duplicates_criteria

    # fixing a linguistic fault-pas
    getSelectedCriterias = getSelectedCriteria

InitializeClass(DuplicatesCriteriaManager)
