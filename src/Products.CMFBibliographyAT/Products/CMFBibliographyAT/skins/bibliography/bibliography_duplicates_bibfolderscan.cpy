## Script (Python) "bibliography_check_duplicates"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

request = container.REQUEST

sort_on = request.get('sort_on', 'modified')
sort_order = request.get('sort_order_reverse', False) and 'reverse' or None
span_of_search = request.get('span_of_search', None) or 'local'

msg = context.updateDuplicatesFolder(sort_on=sort_on, sort_order=sort_order, span_of_search=span_of_search)
return state.set(status='success', portal_status_message='%s' % msg)
