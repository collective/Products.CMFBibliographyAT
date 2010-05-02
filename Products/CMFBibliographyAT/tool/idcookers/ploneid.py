"""PLONE Default Bibliography IdCooker class"""

# Zope stuff
from zope.component import getUtility
from App.class_init import InitializeClass
from App.Dialogs import MessageDialog

# Bibliography stuff
from Products.CMFCore.utils import getToolByName
from Products.CMFBibliographyAT.tool.idcookers.base \
     import IBibliographyIdCooker, BibliographyIdCooker

from plone.i18n.normalizer.interfaces import IFileNameNormalizer

class PloneIdCooker(BibliographyIdCooker):
    """
    The ID is cooked from the bibliographical reference's title as a normalized string. That is the way Plone normally cooks object IDs.
    """



    meta_type = "PLONE Default Bibliography ID Cooker"

    def __init__(self,
                 id = 'plone_cooker',
                 title = "PLONE Default Bibliography ID Cooker"):
        """
        initializes id and title
        """
        self.id = id
        self.title = title

    def _cookIdCore(self, ref, **kwargs):
        """
        cooks a bibref id for one reference entry dict
        """
        normalizer = getUtility(IFileNameNormalizer)
        id=ref['title'].lower().lstrip()
        id=id.rstrip()
        id=id.replace(" ", "-")
        return normalizer.normalize(id)

InitializeClass(PloneIdCooker)


def manage_addPloneIdCooker(self, REQUEST=None):
    """ """
    try:
        self._setObject('plone_cooker', PloneIdCooker())
    except:
        return MessageDialog(
            title='Bibliography tool warning message',
            message='The id cooker you attempted to add already exists.',
            action='manage_main')
    return self.manage_main(self, REQUEST)
