# inspired from PlacelessTranslation - utils.py
#    Copyright (C) 2001, 2002, 2003 Lalo Martins <lalo@laranja.org>,

from types import UnicodeType
from zLOG import LOG, INFO, BLATHER, PROBLEM, WARNING
from urllib import urlencode
from bibliograph.core.utils import _encode

from AccessControl import ModuleSecurityInfo
security = ModuleSecurityInfo('Products.CMFBibliographyAT.utils')

def log(msg, severity=INFO, detail='', error=None):
    # XXX is this used somewhere?
    LOG('CMFBibliographyAT', severity, _encode(msg), _encode(detail), error)

# added some more routines...

def _getCoinsString(self, coinsData):
    """
    Create a COinS microformat string.
    """
    
    coinsString = "ctx_ver=Z39.88-2004"
    for (key, value) in coinsData.items():
        if value:
            if isinstance(value, (tuple, list)):
                for v in value:
                    coinsString += "&%s" % urlencode({key: v})
            else:
                coinsString += "&%s" % urlencode({key: value})
    
    return coinsString

import zope.deferredimport
zope.deferredimport.deprecated(
    'Utility methods were factored out to bibliograph.core.utils. Import from here may become '
    'unsupported',
    _encode='bibliograph.core',
    _decode='bibliograph.core',
    _default_encoding='bibliograph.core',
    )

