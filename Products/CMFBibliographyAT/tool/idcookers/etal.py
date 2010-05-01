"""EtAl Bibliography IdCooker class"""

# Zope stuff
from App.class_init import InitializeClass
from App.Dialogs import MessageDialog

# CMF stuff
from Products.CMFCore.utils import getToolByName

# Bibliography stuff
from Products.CMFBibliographyAT.tool.idcookers.base \
     import IBibliographyIdCooker, BibliographyIdCooker


class EtalIdCooker(BibliographyIdCooker):
    """
    If a bibliographical reference item has one or two authors, it uses the authorname(s) + publication year to cook a reference's ID.
    If an item has more than two authors, it uses the first author's name plus 'EtAl' plus the publication year.
    """



    meta_type = "EtAl Bibliography ID Cooker"

    def __init__(self,
                 id = 'etal',
                 title = "EtAl Bibliography ID Cooker"):
        """
        initializes id and title
        """
        self.id = id
        self.title = title

    def _cookIdCore(self, ref, new_id='', **kwargs):
        """
        cooks a bibref id for one reference entry dict
        """

        # AUTHORS
        namepart = 'nobody'
        if self._refHasAuthorNames(ref):
            lastnames = []
            for each in ref['authors']:
                if each.get('lastname', None):
                    lastnames.append(each['lastname'])

            if len(lastnames) > 2:
                namepart = '%sEtAl' % lastnames[0]
            elif len(lastnames) <= 2:
                namepart = ''.join(lastnames)
            else:
                pass

        # PUBLICATION YEAR
        if ref.get('publication_year', None):
            yearpart = str(ref['publication_year'])
        else:
            yearpart = "1000"

        return  namepart + yearpart

InitializeClass(EtalIdCooker)


def manage_addEtalIdCooker(self, REQUEST=None):
    """ """
    try:
        self._setObject('etal', EtalIdCooker())
    except:
        return MessageDialog(
            title='Bibliography tool warning message',
            message='The id cooker you attempted to add already exists.',
            action='manage_main')
    return self.manage_main(self, REQUEST)
