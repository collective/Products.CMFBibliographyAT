from zope.interface import Interface

class IBibliographyTool(Interface):
    
    """Marker interface for the bibliography tool
    """

class IBibliographyToolFolder(Interface):

    """Marker interface for folderish tool components
    """

class IBibliographyToolComponent(Interface):

    """Marker interface for non-folderish tool components
    """

class IBibliographyParser(IBibliographyToolComponent):
    
    """Marker interface for bibliographic parsers
    """
        
class IBibliographyIdCooker(IBibliographyToolComponent):
    
    """Marker interface for bibliographic id cookers
    """

class IBibliographyParserFolder(IBibliographyToolFolder):
    
    """Marker interface for bibliographic parsers folder
    """
        
class IBibliographyIdCookerFolder(IBibliographyToolFolder):
    
    """Marker interface for bibliographic id cookers folder
    """




