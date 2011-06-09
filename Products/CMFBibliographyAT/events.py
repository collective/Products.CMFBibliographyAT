from zope.interface import implements
from zope.component.interfaces import ObjectEvent
from Products.CMFBibliographyAT.interfaces import IBibentryImportedEvent

class BibentryImportedEvent(ObjectEvent):
    """A bibentry was imported successfully or as duplicate.
    """
    implements(IBibentryImportedEvent)
    
    def __init__(self, obj, duplicates):
        ObjectEvent.__init__(self, obj)
        self.duplicates = duplicates