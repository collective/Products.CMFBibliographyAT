from zope.interface import implements

from Products.Archetypes.utils import shasattr

from bibliograph.core.interfaces import IBibrenderable

class BiliographicExportAdapter(object):
    
    implements(IBibrenderable)
    
    def __init__(self, context):
        self.context = context
        
        self.__name__ = self.context.getId()
        self.title = self.context.Title()
        self.publication_year = self.context.publication_year
        self.abstract = self.context.getAbstract()
        self.subject = self.context.subject
        self.note = self.context.note
        self.annote = self.context.annote
        self.url = self.context.aq_base.getURL()
        
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

    @property
    def source_fields(self):
        if shasattr(self.context, 'source_fields') and \
           self.context.source_fields:
            return list(self.context.source_fields)
        return []
                      
    @property
    def field_values(self):
        context = self.context
        field_values = []
        if shasattr(context, 'source_fields') and context.source_fields:
            for key in context.source_fields:
                if key == 'publication_type':
                    field_values.append('type')
                elif key in context.Schema():
                    field_values.append(context.getFieldValue(key))
                elif callable(context[key]):
                    field_values.append(context[key]())
                else:
                    field_values.append(getattr(context, key, None))
        return field_values     
        
    @property    
    def publication_type(self):
        return unicode(self.context.meta_type[:-9])
        