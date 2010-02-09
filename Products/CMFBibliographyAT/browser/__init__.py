# Init of browser package

from bibliograph.core.interfaces import IBibliographyExport
from Products.CMFBibliographyAT.interface import IBibliographicItem

class isBibliographyExportable(object):
    
    def __call__(self):
        # This check is completely bullshit: it does not take export
        # adapters into account nor does it work with the old-style
        # IBibliographyExport interface as used in base.py
        return IBibliographyExport.providedBy(self.context) or IBibliographicItem.providedBy(self.context)
