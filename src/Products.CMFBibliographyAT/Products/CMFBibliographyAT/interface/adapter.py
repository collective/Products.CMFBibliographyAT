from zope.interface import Interface

class IBibAuthorMember(Interface):

    """Interface for Adapter that handles authors and member connection
    """

    def getSiteMembers(self, *args, **kw):
        """
        For use when members are authors, return a DisplayList of members
        Alternative to 'getMembers' if 'no reference' must not be empty
        (to work around a bug in the 'Records' packager)
        """

    def showMemberAuthors(self):
        """ return True if referencing of authors / editors to portal members is supported
        """

    def inferAuthorReferences(self, report_mode='v', is_new_object=False):
        """
        If the item has no author references set but the tool supports
        member references or the site uses CMFMember, it tries to find
        a content object corresponding to the author name and makes
        reference there.

        Lookup is done on firstname lastname match.

        A report is returned controlled by the mode:

        - 'v': verbose; the default; for each author it is indicated
               what was done.
        - 'q': quiet; nothing is returned
        - 'c': conflicts only; conflicts occur if several potential
               target members are found
        """