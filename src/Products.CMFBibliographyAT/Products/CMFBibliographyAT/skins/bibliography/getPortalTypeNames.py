## Script (Python) "getPortalTypeNames"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
type_ids = context.portal_types.listTypeTitles().keys()
type_ids.sort()
return type_ids
