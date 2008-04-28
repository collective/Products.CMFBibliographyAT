## Script (Python) "getAuthorDataFromMember"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=author
##title=
##

authorschema = author.Schema()
fname = ''
if authorschema.has_key('firstname'):
    fname = getattr(author, authorschema['firstname'].accessor)()
elif authorschema.has_key('given_name'):
    fname = getattr(author, authorschema['given_name'].accessor)()

mname = ''
if authorschema.has_key('middlename'):
    mname = getattr(author, authorschema['middlename'].accessor)()

lname = ''
if authorschema.has_key('lastname'):
    lname = getattr(author, authorschema['lastname'].accessor)()
elif authorschema.has_key('surname'):
    lname = getattr(author, authorschema['surname'].accessor)()

hpage = ''
if authorschema.has_key('homepage'):
    hpage = getattr(author, authorschema['homepage'].accessor)()
elif authorschema.has_key('home_page'):
    hpage = getattr(author, authorschema['home_page'].accessor)()
else:
    hpage = '/'+context.portal_url.getRelativeContentURL(author)

if not fname and not lname:
    if authorschema.has_key('fullname'):
        fullname = getattr(author, authorschema['fullname'].accessor)().split(' ')
        fname = ' '.join(fullname[:-1])
        lname = ' '.join(fullname[-1:])

return lname and {'firstname':fname, 'middlename':mname, 'lastname':lname, 'homepage':hpage} or None
