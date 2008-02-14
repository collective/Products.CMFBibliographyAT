## Controller Python Script "prefs_bibliography_general"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Reconfigure the Bibliography Tool

from Products.CMFBibliographyAT import CMFBibMessageFactory as _

REQUEST=context.REQUEST
context.portal_bibliography.manage_changeProperties(REQUEST)

return state.set(portal_status_message=context.translate(_(u'bibliography_tool_updated_general', default=u'Updated Bibliography Settings - General.')))
