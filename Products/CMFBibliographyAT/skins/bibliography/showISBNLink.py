## Script (Python) "showISBNLink"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
site_default = context.portal_bibliography.getProperty('show_isbn_link', None)
return context.getProperty('show_isbn_link', site_default)
