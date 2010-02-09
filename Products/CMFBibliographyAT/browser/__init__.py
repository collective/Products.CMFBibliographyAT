# Init of browser package

from bibliograph.core.interfaces import IBibliographyExport
from Products.CMFBibliographyAT.interface import IBibliographicItem

class isBibliographyExportable(object):
    
    def __call__(self):
        return IBibliographyExport.providedBy(self.context) or IBibliographicItem.providedBy(self.context)
