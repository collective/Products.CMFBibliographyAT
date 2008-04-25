## Controller Python Script "bibliography_entry_addOwnerToLocalRoles"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=memberId=None
##title=
##

from Products.CMFCore.permissions import ModifyPortalContent

bib_tool = context.portal_bibliography
mtool = context.portal_membership

if memberId is not None:

    # only applicable to bibliography reference items and if authenticated member is owner of item!!!
    if context.portal_type in bib_tool.getReferenceTypes() and mtool.checkPermission(ModifyPortalContent, context):

        pdf_file = context.getPdf_file()
        bibfolder = context.getBibFolder()
        if pdf_file and bibfolder.getSynchronizePdfFileAttributes():
            pdf_file.manage_addLocalRoles(memberId, ('Owner',))