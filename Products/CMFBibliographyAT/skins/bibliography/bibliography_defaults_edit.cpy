## Controller Python Script "bibliography_defaults_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

from Products.CMFBibliographyAT import CMFBibMessageFactory as _

request = container.REQUEST
RESPONSE =  request.RESPONSE

state = context.portal_form_controller.getState(script, is_validator=0)

if request.has_key('form.button.Save'):
    new_status = "success"
    button = "Save"
    message = _("Defaults updated")
else:
    new_status = "failure"
    button = "More"
    message = _(u"Next link enabled")

links = request.get('links', [])
link = request.get('nextlink', None)
top =  request.get('top', [])

if link: links.append(link)

if links:
    context.processAuthorUrlList(links)
    if request.form.has_key('nextlink'):
        del request.form['nextlink']

if top: context.setTop(top)

context.plone_utils.addPortalMessage(message)
return state.set(status=new_status, button=button, context=context)

