# inspired from PlacelessTranslation - utils.py
#    Copyright (C) 2001, 2002, 2003 Lalo Martins <lalo@laranja.org>,

from types import UnicodeType
from zLOG import LOG, INFO, BLATHER, PROBLEM, WARNING
from urllib import urlencode

from AccessControl import ModuleSecurityInfo
security = ModuleSecurityInfo('Products.CMFBibliographyAT.utils')

def log(msg, severity=INFO, detail='', error=None):
    if type(msg) is UnicodeType:
        msg = msg.encode(sys.getdefaultencoding(), 'replace')
    if type(detail) is UnicodeType:
        detail = detail.encode(sys.getdefaultencoding(), 'replace')
    LOG('CMFBibliographyAT', severity, msg, detail, error)

# added some more routines...

## a poor-mans approach to fixing unicode issues :-(
_default_encoding = 'utf-8'

def _encode(s, encoding=_default_encoding):
    try:
        return s.encode(encoding)
    except (TypeError, UnicodeDecodeError, ValueError):
        return s

def _decode(s, encoding=_default_encoding):
    try:
        return unicode(s, encoding)
    except (TypeError, UnicodeDecodeError, ValueError):
        return s

def _getCoinsString(self, coinsData):
    """
    Create a COinS microformat string.
    """
    
    coinsString = "ctx_ver=Z39.88-2004"
    for (key, value) in coinsData.items():
        if value:
            if type(value) == list:
                for v in value:
                    coinsString += "&%s" % urlencode({key: v})
            else:
                coinsString += "&%s" % urlencode({key: value})
    
    return coinsString