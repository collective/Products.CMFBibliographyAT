from Acquisition import aq_inner

from zope.interface import implements

from Products.Archetypes.utils import shasattr

from bibliograph.core.interfaces import IBibliographicReference
from bibliograph.core.utils import _decode

from bibliograph.rendering.adapter import Zope2FolderAdapter

###############################################################################

class CMFFolderAdapter(Zope2FolderAdapter):
    
    def __iter__(self):
        return iter(self.context.contentValues())
        
class BTreeFolderAdapter(Zope2FolderAdapter):

    def __iter__(self):
        return self.context._tree.itervalues()
    
    def prehook(self, entry):
         # _tree.itervalues() returns unwrapped objects,
         # but the renderer needs
         # context-aware objects, so we wrap it.
         # Check to see if the object has been changed (elsewhere in the
         # current transaction/request.
        changed = getattr(entry, '_p_changed', False)
        self.deactivate = not changed
        return entry.__of__(aq_inner(self.context))
    
    def posthook(self, entry):
        # We now 'unload' the entry from the ZODB object cache to
        # reclaim its memory.
        # See http://wiki.zope.org/ZODB/UnloadingObjects for details.
        if self.deactivate:
            entry._p_deactivate()   

###############################################################################

class BiliographicExportAdapter(object):
    
    implements(IBibliographicReference)
    
    def __init__(self, context):
        self.context = context
        
        self.__name__ = self.context.getId()
        self.title = _decode(self.context.Title())
        self.publication_year = self.context.publication_year
        self.abstract = _decode(self.context.getAbstract())
        self.subject = _decode(self.context.subject)
        self.note = _decode(self.context.note)
        self.annote = _decode(self.context.annote)
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
        
