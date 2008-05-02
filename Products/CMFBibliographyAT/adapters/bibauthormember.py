from zope.interface import implements

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.utils import DisplayList
from Products.Archetypes.utils import shasattr

from Products.CMFBibliographyAT.interface import IBibAuthorMember
from bibliograph.core.utils import _encode, _decode

class BibAuthorMember:

    """Adapter that handles authors and member connection
    """
    implements(IBibAuthorMember)

    def __init__(self, context, view=None):
        self.context = context
        self.view = view

    def getSiteMembers(self, *args, **kw):
        """
        For use when members are authors, return a DisplayList of members
        Alternative to 'getMembers' if 'no reference' must not be empty
        (to work around a bug in the 'Records' packager)
        """
        pas=getToolByName(self.context, "acl_users")
        results=pas.searchUsers(**(True and dict(sort_by='userid') ))
        results = dict([(result["userid"], result) for result in results]).values()
        dl = DisplayList()
        #zzz todo: Make this translateable, how?
        dl.add('',"Select a site member")
        for r in results:
            title = r['title']
            if title=="":
                title=r['userid']
            dl.add(r['userid'],title)
        return dl

    def showMemberAuthors(self):
        """ return True if referencing of authors / editors to portal members is supported
        """
        bib_tool = getToolByName(self.context, 'portal_bibliography')
        return bib_tool.getProperty('support_member_references')


    #zzz todo: fix inferAuthorReferences so it works with usernames and not references for members
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
        bib_tool = getToolByName(self.context, 'portal_bibliography')
        if not self.showMemberAuthors():
            return "No inference attempted"
        report = []
        authors = []
        a_modified = False
        pas=getToolByName(self.context, "acl_users")
        first_inferred_author = True
        for author in self.context.getAuthors():
            authors.append(author)
            lastname = author.get('lastname', None)
            firstnames = author.get('firstnames', None)
            if lastname is None:
                continue
            raw_candidates = pas.searchUsers(fullname=lastname)
            candidates = []
            for cand in raw_candidates:
                    candidate_name = cand['title']
                    candidate_lastname = candidate_name.split(' ')[-1]
                    candidate_firstnames = ' '.join(candidate_name.split(' ')[:-1])
                    if (lastname == candidate_lastname) and (firstnames == candidate_firstnames):
                        candidates.append(cand)

                    if candidates: break

            if not candidates:
                msg = "%s: no corresponding member found." % author()
                if report_mode == 'v':
                    report.append(msg)
            elif len(candidates) > 1:
                msg = "%s: several corresponding members found:" % author()
                for c in candidates:
                    msg += " %s at %s," % (c.Title, c.getURL(relative=1))
                report.append(msg)
            else:
                target = candidates[0]
                memberId = target['id']
                name = target['title']
                author['username'] = memberId
                
                if bib_tool.authorOfImpliesOwner:
                    # assign the member ids as owner
                    self.context.bibliography_entry_addOwnerToLocalRoles(memberId=memberId)
                    if self.context.getBibFolder().getSynchronizePdfFileAttributes():
                        self.bibliography_pdffile_addOwnerToLocalRoles(memberId=memberId)

                if bib_tool.authorOfImpliesCreator():

                    # also write the member ids to the creator metadata field.
                    #try:
                        if first_inferred_author:
                            creators = []
                            first_inferred_author = False
                        else:
                            creators = list(self.context.listCreators())

                        if memberId not in creators:
                            creators.append(memberId)

                        self.context.setCreators(value=tuple(creators))
                        pdf_file = self.context.getPdf_file()
                        if pdf_file and self.context.getBibFolder().getSynchronizePdfFileAttributes():

                            pdf_file.setCreators(value=tuple(creators))

                    #except AttributeError:
                    #    pass

                a_modified = True
                msg = "%s: referring to %s at %s." \
                      % (author(),
                         name,
                         target['id'],
                         )
                if report_mode == 'v':
                    report.append(msg)

        if a_modified and not is_new_object:
            self.context.setAuthors(authors)
            self.context.reindexObject()
        if report_mode != 'q' and report:
            ## report.insert(0, "%s:\n" % self.absolute_url(relative=1))
            return ' '.join(report)
        return None