## Controller Python Script "prefs_bibliography_memberrefsupport"
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
if not REQUEST.has_key('member_types'):
    REQUEST.set('member_types', ())
context.portal_bibliography.manage_changeProperties(REQUEST)

context.plone_utils.addPortalMessage(_(u'bibliography_tool_updated_memberreferencesupport',
                                       default=u'Updated Bibliography Settings - Member Referencing Support.'))
return state.set(context=context)
