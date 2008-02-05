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
renderer_encoding_settings = []

for key in REQUEST.keys():
    if key.startswith('parser_enabled_'):
        parser_enabled_settings.append(key)
    if key.startswith('renderer_enabled_'):
        renderer_enabled_settings.append(key)
    if key.startswith('renderer_encoding_'):
        renderer_encoding_settings.append(key)

# enabled / disabled
for setting in parser_enabled_settings:

    parser_name = string.split(setting, '_')[-1]
    parser_property = '_'.join(string.split(setting, '_')[:-1])
    parser = context.portal_bibliography.getParser(format=parser_name, with_unavailables=True, with_disabled=True)
    parser.manage_changeProperties({parser_property: REQUEST.get(setting),})

for setting in renderer_enabled_settings:

    renderer_name = string.split(setting, '_')[-1]
    renderer_property = '_'.join(string.split(setting, '_')[:-1])
    renderer = context.portal_bibliography.getRenderer(format=renderer_name, with_unavailables=True, with_disabled=True)
    renderer.manage_changeProperties({renderer_property: REQUEST.get(setting),})

# output encodings
for setting in renderer_encoding_settings:

    renderer_name = string.split(setting, '_')[-1]
    renderer_property = 'default_output_encoding'
    renderer = context.portal_bibliography.getRenderer(format=renderer_name, with_unavailables=True, with_disabled=True)
    renderer.manage_changeProperties({renderer_property: REQUEST.get(setting),})

return state.set(portal_status_message=context.translate(domain='cmfbibliographyat', msgid='bibliography_tool_updated_importexport', default='Updated Bibliography Settings - Import / Export.'))
