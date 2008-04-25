## Controller Python Script "prefs_bibliography_idcooking"
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

idcookers_enabled_settings = []

for key in REQUEST.keys():
    if key.startswith('idcooker_enabled_'):
        idcookers_enabled_settings.append(key)

# enabled / disabled
for setting in idcookers_enabled_settings:

    idcooker_id = string.split(setting, '_')[-1]
    idcooker_property = '_'.join(string.split(setting, '_')[:-1])
    idcooker = context.portal_bibliography.getIdCooker(idcooker_id=idcooker_id, with_disabled=True)
    if context.portal_bibliography.getDefaultIdCooker(with_disabled=True).getId() != idcooker_id:
        idcooker.manage_changeProperties({idcooker_property: REQUEST.get(setting),})
    else:
        idcooker.manage_changeProperties({idcooker_property: 1,})

return state.set(portal_status_message=context.translate(domain='cmfbibliographyat', msgid='bibliography_tool_updated_idcooking', default='Updated Bibliography Settings - Reference ID Cooking.'))
