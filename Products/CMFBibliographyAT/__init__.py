##########################################################################
#                                                                        #
#           copyright (c) 2003, 2006 ITB, Humboldt-University Berlin     #
#           written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                        #
##########################################################################

"""package installer"""

import sys

from Products.CMFCore import utils as CMFutils
from Products.CMFCore.DirectoryView import registerDirectory

from Products.Archetypes.public import process_types, listTypes

from config import SKINS_DIR, PROJECTNAME
from config import ADD_CONTENT_PERMISSION, ENTRY_TYPES

import content
from tool import bibliography, idcookers

tools = ( bibliography.BibliographyTool, )

GLOBALS = globals()
registerDirectory('skins', GLOBALS)

def initialize(context):
    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)
    CMFutils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)
    CMFutils.ToolInit(
        'Bibliography Tool',
        tools=tools,
        icon='bibliography_tool.png',
        ).initialize(context)
    idcookers.initialize(context)

# module aliases for backward compatibility

from content import base
sys.modules['Products.CMFBibliographyAT.BaseEntry'] = base
from content import folder
sys.modules['Products.CMFBibliographyAT.BibliographyFolder'] = folder

import content
sys.modules['Products.CMFBibliographyAT.bibtex_types'] = content
import DuplicatesCriteria
sys.modules['Products.CMFBibliographyAT.ImportCriterias'] = DuplicatesCriteria

old_path = 'Products.CMFBibliographyAT.bibtex_types.'
from content import article, booklet, book, inbook, incollection, \
     inproceedings, manual, mastersthesis, misc, phdthesis, preprint, \
     proceedings, techreport, unpublished, webpublished
sys.modules[old_path + 'ArticleReference'] = article
sys.modules[old_path + 'BookletReference'] = booklet
sys.modules[old_path + 'BookReference'] = book
sys.modules[old_path + 'InbookReference'] = inbook
sys.modules[old_path + 'IncollectionReference'] = incollection
sys.modules[old_path + 'InproceedingsReference'] = inproceedings
sys.modules[old_path + 'ManualReference'] = manual
sys.modules[old_path + 'MastersthesisReference'] = mastersthesis
sys.modules[old_path + 'MiscReference'] = misc
sys.modules[old_path + 'PhdthesisReference'] = phdthesis
sys.modules[old_path + 'PreprintReference'] = preprint
sys.modules[old_path + 'ProceedingsReference'] = proceedings
sys.modules[old_path + 'TechreportReference'] = techreport
sys.modules[old_path + 'UnpublishedReference'] = unpublished
sys.modules[old_path + 'WebpublishedReference'] = webpublished

from tool import bibliography
sys.modules['Products.CMFBibliographyAT.BibliographyTool'] = bibliography

# check Bibutils version
from bibliograph.core.version_check import checkBibutilsVersion
import logging
LOG = logging.getLogger('Products.CMFBibliographyAT')

try:
    bibutils_version = checkBibutilsVersion()
    LOG.info('Installed Bibutils version: %s' % bibutils_version)
except RuntimeError, e:
    bibutils_version = None
    LOG.warn(e)


