from Acquisition import aq_inner

from zope.interface import implements

from Products.Archetypes.utils import shasattr

from bibliograph.core.interfaces import IBibliographicReference
from bibliograph.core.interfaces import IAuthor
from bibliograph.core.utils import _decode


class Author(object):
    """
    """

    implements(IAuthor)

    def __init__(self, title, firstname, middlename, lastname):
        self.title = title
        self.firstname = firstname
        self.middlename = middlename
        self.lastname = lastname


class BiliographicExportAdapter(object):

    implements(IBibliographicReference)

    def __init__(self, context):
        self.context = context

        self.__name__ = self.context.getId()
        self.title = _decode(self.context.Title())
        self.publication_year = self.context.publication_year
        self.publication_month = self.context.getPublication_month()
        self.abstract = _decode(self.context.getAbstract())
        self.subject = _decode(self.context.getKeywords())
        self.note = _decode(self.context.note)
        self.annote = _decode(self.context.annote)
        self.url = self.context.aq_base.getURL()

        # identifiers
        identifiers = dict()
        for d in self.context.getIdentifiers():
            if d.get('value'):
                identifiers[d['label']] = d['value']
        self.identifiers = identifiers

        # Authors as a FormattableNames structure
        self.getAuthors = self.context.getAuthors

    @property
    def editor_flag(self):
        return shasattr(self.context, 'editor_flag') and \
               self.context.getFieldValue('editor_flag')
    @property
    def authors(self):
        """ Authors as a string """
        authors = self.context.Authors(sep=' and ',
                                    lastsep=' and ',
                                    format="%L, %F %M",
                                    abbrev=0,
                                    lastnamefirst=0)
        if not isinstance(authors, unicode):
            authors = unicode(authors, 'utf-8')
        return authors

    def getAuthors(self):
        """A sequence of IAuthor objects.
        """
        authors = []
        for each in self.context.getAuthors():
            title = each['title']
            firstname = each['firstname']
            middlename = each['middlename']
            lastname = each['lastname']
            author = Author(title, firstname, middlename, lastname)
            authors.append(author)
        return authors

    @property
    def source_fields(self):
        context = self.context
        source_fields = []
        if shasattr(context, 'source_fields') and context.source_fields:
            for key in context.source_fields:
                if key == 'publication_type':
                    value = 'type'
                elif key in context.Schema():
                    value = context.getFieldValue(key)
                elif callable(context[key]):
                    value = context[key]()
                else:
                    value = getattr(context, key, None)
                source_fields.append((key, value))

        return source_fields

    @property
    def publication_type(self):
        return unicode(self.context.meta_type[:-9])

