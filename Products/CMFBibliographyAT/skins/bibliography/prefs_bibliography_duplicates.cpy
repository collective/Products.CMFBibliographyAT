## Controller Python Script "prefs_bibliography_duplicates"
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

context.plone_utils.addPortalMessage(_(u'bibliography_tool_updated_duplicates',
                                       default=u'Updated Bibliography Settings - Duplicates Management.'))
return state.set(context=context)
