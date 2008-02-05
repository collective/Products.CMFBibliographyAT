## Controller Python Script "bibliography_pdffile_cookId"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=with_disabled=False
##title=
##

from Products.CMFCore.permissions import ModifyPortalContent

bib_tool = context.portal_bibliography
types_tool = context.portal_types
plone_utils = context.plone_utils
mtool = context.portal_membership

if context.portal_type in bib_tool.getReferenceTypes() and mtool.checkPermission(ModifyPortalContent, context):

    bibfolder = context.aq_inner.aq_parent
    pdf_folder = bibfolder.getPdfFolder()
    pdf_file = context.getPdf_file()

    # id cooking for associated PDF files
    if pdf_file and bibfolder.getSynchronizePdfFileAttributes():

        if pdf_file.getId() != '%s.pdf' % context.getId():

            # only if the IDs of BibRefItem and PDF file differ, we have to get into action
            pdf_file_id = context.getId() + '.pdf'
            if pdf_folder.hasObject(pdf_file_id):
                # arggghhh... this should not happen!!!
                # let us try to cook an id that resembles the bibrefitem's ID (the least we can do)
                new_id = bib_tool.cookReferenceId(ref=context, idcooker_id=bibfolder.getReferenceIdCookingMethod(), with_disabled=with_disabled)
                if new_id != 'nobody1000':
                    while pdf_folder.hasObject(new_id) and new_id != context.getPdf_file().getId():
                        new_id = pdf_folder.nextId(new_id)
                pdf_file_id = new_id + '.pdf'

            bib_tool.transaction_savepoint(optimistic=True)

            # we need to explicitly add 'PDF File' content type as allowed type to 'PDF Folder' content type
            # even for pdf_file.setId (picky Plone!!!)
            pdf_folder.allowPdfFileCreation()

            # set new id for PDF file
            pdf_file.setId(value=pdf_file_id)

            # restore PDF folder fti
            pdf_folder.disallowPdfFileCreation()
