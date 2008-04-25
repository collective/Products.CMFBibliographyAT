## Script (Python) "getISBNLink"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=isbn=None
##title=
##
if not isbn: return ("", "")
isbn = isbn.replace('-', '').strip()
return ("Link to Amazon", "http://www.amazon.com/exec/obidos/tg/detail/-/%s" % isbn)
