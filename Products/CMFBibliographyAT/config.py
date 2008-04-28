import os
from zLOG import LOG, PROBLEM
from Products.CMFCore.permissions import AddPortalContent

try:
    from Products.LinguaPlone.public import registerType
    CMFBAT_USES_LINGUAPLONE=True
except:
    CMFBAT_USES_LINGUAPLONE=False
# manually disable here
CMFBAT_USES_LINGUAPLONE=False

ADD_CONTENT_PERMISSION = AddPortalContent
PROJECTNAME = "CMFBibliographyAT"
SKINS_DIR = 'skins'

USE_EXTERNAL_STORAGE = True
EXTERNAL_STORAGE_PATH = 'files'

ENTRY_TYPES = 'bibtex_types'
FOLDER_TYPES = ('BibliographyFolder',
                'LargeBibliographyFolder',
                )
PREPRINT_SERVERS = ('None:',
                    'arXiv:http://arxiv.org',
                    'CogPrints:http://cogprints.ecs.soton.ac.uk/',
                    )

## Old way to define possible bibliographical content types
#types = os.listdir(os.path.dirname(__file__)+'/'+ ENTRY_TYPES)
#types = [type[:-3] for type in types \
#          if (type.endswith('.py') \
#              and not type.startswith('__'))]
#REFERENCE_TYPES = tuple(types)

## New way (since product reorganization)
REFERENCE_TYPES = (
    'ArticleReference',
    'BookletReference',
    'BookReference',
    'ConferenceReference',
    'InbookReference',
    'IncollectionReference',
    'InproceedingsReference',
    'ManualReference',
    'MastersthesisReference',
    'MiscReference',
    'PhdthesisReference',
    'PreprintReference',
    'ProceedingsReference',
    'TechreportReference',
    'UnpublishedReference',
    'WebpublishedReference',
    )

ZOPE_TEXTINDEXES = (
    'TextIndex',
    'ZCTextIndex',
    'TextIndexNG2',
    'TextIndexNG3',
)
if USE_EXTERNAL_STORAGE:
    try:
        import Products.ExternalStorage
    except ImportError:
        LOG('CMFBibliographyAT',
            PROBLEM, 'ExternalStorage N/A, falling back to AnnotationStorage')
        USE_EXTERNAL_STORAGE = False
