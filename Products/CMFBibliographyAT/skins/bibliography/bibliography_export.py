## Script (Python) "bibliography_export"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=format='BibTex', output_encoding=None, eol_style=False
##title=
##
request = container.REQUEST
RESPONSE =  request.RESPONSE

if not format: return None

RESPONSE.setHeader('Content-Type', 'application/octet-stream')
RESPONSE.setHeader('Content-Disposition',
                   'attachment; filename=%s' %\
                   context.getId() + '.' + format)

bibtool = context.portal_bibliography
return bibtool.render(context, format=format, output_encoding=output_encoding, msdos_eol_style=eol_style)
