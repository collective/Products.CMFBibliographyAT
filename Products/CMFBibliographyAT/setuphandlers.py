from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from Products.MimetypesRegistry import MimeTypeItem

from Products.CMFBibliographyAT.migrations import *


def importVarious(context):
    """
    Import various settings.

    Provisional handler that does initialization that is not yet taken
    care of by other handlers.
    """

    if context.readDataFile('cmfbib-tool.txt') is None:
        return

    site = context.getSite()
    logger = context.getLogger('bibliography')
    out = StringIO()
    install_transform(site, out)
    autoMigrate(site, out)
    logger.info(out.getvalue())

    return 'Various settings from CMFBibliographyAT imported.'


def install_transform(self, out):
    try:
        print >>out, "Adding new mimetype"
        mimetypes_tool = getToolByName(self, 'mimetypes_registry')
        newtype = MimeTypeItem.MimeTypeItem('HTML with inline citations',
            ('text/x-html-bibaware',), ('html-bib',), 0)
        mimetypes_tool.register(newtype)

        print >>out,"Add transform"
        transform_tool = getToolByName(self, 'portal_transforms')
        try:
            transform_tool.manage_delObjects(['html-to-bibaware'])
        except: # XXX: get rid of bare except
            pass
        transform_tool.manage_addTransform('html-to-bibaware',
                                           'Products.CMFBibliographyAT.transform.html2bibaware')
        if 'bibaware-to-html' not in transform_tool.objectIds():
            transform_tool.manage_addTransform('bibaware-to-html',
                                               'Products.CMFBibliographyAT.transform.bibaware2html')
        addPolicy(transform_tool, out)
    except (NameError,AttributeError):
        print >>out, "No MimetypesRegistry, bibaware text not supported."

def addPolicy(tool, out):
    target = 'text/x-html-safe'
    transform = 'html-to-bibaware'
    policies = tool.listPolicies()
    policy_keys = [p[0] for p in policies]
    if target not in policy_keys:
        print >>out, "Adding transformation policy for bibliographic " \
              "awareness of the 'text/x-html-safe' type."
        tool.manage_addPolicy(target,
                              (transform,),
                              )
    else:
        transforms = [p[1] for p in policies if p[0] == target][0]
        if transform not in transforms:
            transforms += (transform,)
            ## no API for changing a policy :-(
            tool.manage_delPolicies((target,))
            tool.manage_addPolicy(target, transforms)
            print >>out, "Adding the bibliographic transformation to " \
                  "the 'text/x-html-safe' policy."
        else:
            print >>out, "Checked transformation policy"

def autoMigrate(self, out):
    migrations = (
        cmfbib07to08.Migration(self, out),
        cmfbib08to09.Migration(self, out),
        cmfbib09to10.Migration(self, out),
    )
    for migration in migrations:
        migration.migrate()
