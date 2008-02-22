## Controller Python Script "validate_bibliography_import"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=up_text='',file=None,format="bib"
##title=Validate folder renaming
##

from Products.CMFBibliographyAT import CMFBibMessageFactory as _

filename=None
if file is not None:
    filename=getattr(file, 'filename', None)
if not filename and up_text == '':
    state.setError('file', _(u'You must upload a file.'))
if filename and up_text != '':
    state.setError('file', _(u'You should import from clipboard OR file (not both).'))

if state.getErrors():
    context.plone_utils.addPortalMessage(_(u'Please correct the indicated errors.'))
    return state.set(status='failure', context=context)
else:
    return state