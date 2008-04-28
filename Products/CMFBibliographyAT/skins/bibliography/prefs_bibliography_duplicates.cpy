## Controller Python Script "prefs_bibliography_duplicates"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Reconfigure the Bibliography Tool

REQUEST=context.REQUEST
context.portal_bibliography.manage_changeProperties(REQUEST)

return state.set(portal_status_message=context.translate(domain='cmfbibliographyat', msgid='bibliography_tool_updated_duplicates', default='Updated Bibliography Settings - Duplicates Management.'))
