"""PLONE Default Bibliography IdCooker class"""

# Zope stuff
from App.class_init import InitializeClass
from App.Dialogs import MessageDialog

# CMF stuff
from Products.CMFCore.utils import getToolByName

# Bibliography stuff
from Products.CMFBibliographyAT.tool.idcookers.base \
     import IBibliographyIdCooker, BibliographyIdCooker


class UidIdCooker(BibliographyIdCooker):
    """
    The ID is cooked from the bibliographical reference's UID (Archetypes' unique object identifier).
    """



    meta_type = "UID Bibliography ID Cooker"

    def __init__(self,
                 id = 'uid',
                 title = "UID Bibliography ID Cooker"):
        """
        initializes id and title
        """
        self.id = id
        self.title = title

    def _cookIdCore(self, ref, **kwargs):
        """
        cooks a bibref id for one reference entry dict
        """
        return ref['UID']

InitializeClass(UidIdCooker)


def manage_addUidIdCooker(self, REQUEST=None):
    """ """
    try:
        self._setObject('uid', UidIdCooker())
    except:
        return MessageDialog(
            title='Bibliography tool warning message',
            message='The id cooker you attempted to add already exists.',
            action='manage_main')
    return self.manage_main(self, REQUEST)
