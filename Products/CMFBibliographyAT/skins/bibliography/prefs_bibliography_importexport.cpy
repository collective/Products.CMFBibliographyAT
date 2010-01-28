## Controller Python Script "prefs_bibliography_importexport"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Reconfigure the Bibliography Tool

REQUEST=context.REQUEST

parser_enabled_settings = []
renderer_enabled_settings = []

bib_tool = context.portal_bibliography


for key in REQUEST.keys():
    if key.startswith('parser_enabled_'):
        parser_enabled_settings.append(key)
    if key.startswith('renderer_enabled_'):
        renderer_enabled_settings.append(key)

# enabled / disabled
for setting in parser_enabled_settings:

    parser_name = setting.split('_')[-1]
    parser_property = '_'.join(setting.split('_')[:-1])
    bib_tool.updateSheetProperty(parser_name, parser_property, bool(REQUEST.get(setting)))

for setting in renderer_enabled_settings:

    renderer_name = setting.split('_')[-1]
    renderer_property = '_'.join(setting.split('_')[:-1])
    bib_tool.updateSheetProperty(renderer_name, renderer_property, bool(REQUEST.get(setting)))

return state.set(portal_status_message=context.translate(domain='cmfbibliographyat', msgid='bibliography_tool_updated_importexport', default='Updated Bibliography Settings - Import / Export.'))
