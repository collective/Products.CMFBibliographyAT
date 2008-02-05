## Script (Python) "isBibliographyExportable"
##title=Formats the history diff
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=obj=None

from Products.CMFCore.utils import getToolByName
iface = getToolByName(context, 'portal_interface')

return iface.objectImplements(obj, 'Products.CMFBibliographyAT.interfaces.IBibliographyExport')
