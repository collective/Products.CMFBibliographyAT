## Script (Python) "DefaultSource"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
return context.meta_type[:-9] + "." # expecting something like '...Reference'
