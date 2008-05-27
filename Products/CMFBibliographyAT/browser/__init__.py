# Init of browser package

from bibliograph.core.interfaces import IBibliographyExport

class isBibliographyExportable(object):
    
    def __call__(self):
        return IBibliographyExport.providedBy(self.context)