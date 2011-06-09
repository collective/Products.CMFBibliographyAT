from zope.interface import Interface
from zope.interface import Attribute
from zope.component.interfaces import IObjectEvent

class IBibliographyExport(Interface):
    """Marker interface for exportable bibliography elements
    """

class IBibentryImportedEvent(IObjectEvent):
    """A bibentry was imported successfully or as duplicate.
    """
    
    duplicates = Attribute("Indicates if import was duplicate or not. False "
                           "if not duplicate or a list of matched objects if "
                           "it is a duplicate.")