## Controller Python Script "prefs_bibliography_memberrefsupport"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Reconfigure the Bibliography Tool

REQUEST=context.REQUEST
if not REQUEST.has_key('member_types'):
    REQUEST.set('member_types', ())
context.portal_bibliography.manage_changeProperties(REQUEST)

return state.set(portal_status_message=context.translate(domain='cmfbibliographyat', msgid='bibliography_tool_updated_memberreferencesupport', default='Updated Bibliography Settings - Member Referencing Support.'))
