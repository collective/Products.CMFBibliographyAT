from zope.interface import implements

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.utils import DisplayList
from Products.Archetypes.utils import shasattr

from Products.CMFBibliographyAT.interface import IBibAuthorMember
from Products.CMFBibliographyAT.utils import _encode, _decode

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
        md = getToolByName(self.context,     'portal_memberdata')
        m_tool = getToolByName(self.context, 'portal_membership')
        membertypes = bib_tool.getMemberTypes() or \
                      md.getAllowedMemberTypes()
        catalog = getToolByName(self.context, 'portal_catalog')
        first_inferred_author = True
        for author in self.context.getAuthors():
            authors.append(author)
            lastname = author.get('lastname', None)
            firstnames = author.get('firstnames', None)
            if lastname is None:
                continue

            raw_candidates = ()
            search_order = (bib_tool.getMembersSearchOnAttr(), 'Title',)
            for search_on in search_order:
                if search_on:
                    raw_candidates = catalog({'portal_type': membertypes,
                                              '%(search_on)s': lastname})
                    candidates = []
                    for cand in raw_candidates:
                        try:
                            candidate_accessor = eval('cand.getObject().%s' % search_on)
                            if callable(candidate_accessor):
                                candidate_name = candidate_accessor()
                            else:
                                candidate_name = str(candidate_accessor)
                            if candidate_name.find(', ') != -1:
                                candidate_lastname = candidate_name.split(', ')[0]
                                candidate_firstnames = ' '.join(candidate_name.split(', ')[1:])
                            else:
                                candidate_lastname = candidate_name.split(' ')[-1]
                                candidate_firstnames = ' '.join(candidate_name.split(' ')[:-1])
                            if (lastname == candidate_lastname) and (firstnames == candidate_firstnames):
                                candidates.append(cand)
                                break

                        except AttributeError:
                            # cand.getObject does not have the attribute requested in bib_tool.getSelectMembersAttr()
                            # skip this candidate
                            pass

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
                select_attr = bib_tool.getSelectMembersAttr()
                target = candidates[0].getObject()

                # we will prefer the canonical if we have to deal with a translated object
                if target.isTranslatable():
                    target = target.getCanonical()

                author['reference'] = target.UID()
                self.context.addReference(target, 'authorOf')

                # obtain author data from privileged fields in the target object
                data = self.context.getAuthorDataFromMember(target)
                target_givenName = _encode(_decode(data['firstname']) + ' ' + _decode(data['middlename']))
                target_lastName = _encode(_decode(data['lastname']))

                # also prepare for a failure of getAuthorDataFromMember
                select_attr_name = bib_tool.getSelectMembersAttr()
                if select_attr_name:
                    select_attr = getattr(target, select_attr_name, None)
                else:
                    select_attr = None
                if callable(select_attr):
                    name = select_attr() or target.Title()
                else:
                    name = select_attr or target.Title()

                # this is for member name information stored in explicit fields in
                # the member target object
                if \
                   \
                   (author['lastname'] == target_lastName) and \
                   (target_givenName.startswith(author['firstname'])):

                        # we have found a target / author match
                        pass

                # this for name pattern "FIRSTNAMES LASTNAME" \
                elif \
                     \
                   (len(name.split(', ')) == 1) and \
                   name.startswith(author.get('firstname')) and \
                   name.endswith(author.get('lastname')):

                        # we have found a target / author match
                        pass

                # this for name pattern "LASTNAME, FIRSTNAMES" \
                elif \
                     \
                   (len(name.split(', ')) == 2) and \
                   name.startswith(author.get('lastname')) and \
                   ( name.endswith(author.get('firstname')) or \
                     name.endswith(author.get('firstname') + ' ' + author.get('middlename'))):

                        # we have found a target / author match
                        pass

                else:

                    # bad luck, author / member_type data mismatch
                    msg = "%s: no corresponding member found." % author()
                    continue

                if shasattr(target, 'getMemberId'): memberId = target.getMemberId()
                else: memberId = target.getId()
                if m_tool.getMemberInfo(memberId):

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
                         target.absolute_url(relative=1),
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