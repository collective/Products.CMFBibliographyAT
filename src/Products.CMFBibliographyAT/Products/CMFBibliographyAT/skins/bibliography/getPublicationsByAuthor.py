## Script (Python) "getPublicationsByAuthor"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id=None
##title=
##
if id is None:
   member = context.portal_membership.getAuthenticatedMember()
else:
   member = context.portal_membership.getMemberById(id)
return member and member.getBRefs('authorOf') or []
