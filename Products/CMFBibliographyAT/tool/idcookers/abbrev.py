"""Abbreviation Bibliography IdCooker class"""

# Zope stuff
from Globals import InitializeClass
from App.Dialogs import MessageDialog

# CMF stuff
from Products.CMFCore.utils import getToolByName

# Bibliography stuff
from Products.CMFBibliographyAT.tool.idcookers.base \
     import IBibliographyIdCooker, BibliographyIdCooker


class AbbrevIdCooker(BibliographyIdCooker):
    """
    If a bibliographical reference item has one author, it takes the first three letters of the author's lastname
    plus publication year to cook the reference's ID. For more than one author, it uses the initials of all authors' lastnames plus publication
    year.
    """

    __implements__ = (IBibliographyIdCooker ,)

    meta_type = "Abbreviation Bibliography ID Cooker"

    def __init__(self,
                 id = 'abbrev',
                 title = "Abbreviation Bibliography ID Cooker"):
        """
        initializes id and title
        """
        self.id = id
        self.title = title

    def _cookIdCore(self, ref, **kwargs):
        """
        cooks a bibref id for one reference entry dict
        """

        # AUTHORS
        namepart='nobody'
        if self._refHasAuthorNames(ref):
            lastnames = []
            for each in ref['authors']:
                if each.get('lastname', None):
                    lastnames.append(each['lastname'])

            if len(lastnames) > 1:
                namepart = '%s' % ''.join([ lastname[0] for lastname in lastnames ])
            elif len(lastnames) == 1:
                namepart = lastnames[0][:3]
            else:
                pass

        # PUBLICATION YEAR
        if ref.get('publication_year', None):
            yearpart = str(ref['publication_year'])
        else:
            yearpart = "1000"

        return  namepart + yearpart


InitializeClass(AbbrevIdCooker)


def manage_addAbbrevIdCooker(self, REQUEST=None):
    """ """
    try:
        self._setObject('abbrev', AbbrevIdCooker())
    except:
        return MessageDialog(
            title='Bibliography tool warning message',
            message='The id cooker you attempted to add already exists.',
            action='manage_main')
    return self.manage_main(self, REQUEST)
