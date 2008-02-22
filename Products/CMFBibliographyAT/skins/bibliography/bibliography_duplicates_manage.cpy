## Script (Python) "bibliography_export"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

request = container.REQUEST
logs = context.handleAction(REQUEST=request)

context.plone_utils.addPortalMessage(logs)
return state.set(status='success', context=context)
