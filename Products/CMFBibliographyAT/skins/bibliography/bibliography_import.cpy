## Controller Python Script "bibliography_import"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=up_text=None,file=None,format='bib',span_of_search=None,input_encoding='utf-8'
##title=
##

from Products.Archetypes import PloneMessageFactory as _
from Products.Archetypes.utils import addStatusMessage
from Products.CMFBibliographyAT.tool.bibliography import ImportParseError

REQUEST = context.REQUEST

start_time = context.ZopeTime().timeTime()
if up_text:
    source = up_text
else:
    if file is None:
        filename=None
    else:
        filename=getattr(file, 'filename', None)
    if not filename:
        state.setError('file', 'You must import a file.')
        addStatusMessage(REQUEST,_(u"Please correct the indicated errors."))
        return state.set(status='failure',
                         portal_status_message='Please correct the indicated errors.')
    # make sure the path entered in the field matches a file
    try:
        source = file.filename.read()
    except:
        source = file.read()
    if not source or not same_type(source,''):
        msg = "Could not read the file '%s'." %file.filename
        addStatusMessage(REQUEST,_(unicode(msg)))
        state.setError('file', msg)
        return state.set(status='failure',
                         portal_status_message='Please correct the indicated errors.')

# skip DOS line breaks
source = source.replace('\r','')

# get parsed entries from the Bibliography Tool
bibtool = context.portal_bibliography
try:
    # FIXME - produce StringIO and factorize code here & in folder.py
    if file:
        entries = bibtool.getEntries(source, format, file.filename, input_encoding=input_encoding)
    else:
        entries = bibtool.getEntries(source, format, input_encoding=input_encoding)
except ImportParseError:
    state.setError('format', 'Select an appropriate format for your file.')
    msg = """%s Parser's 'checkFormat' and guessing the format""" \
          """ from the file name '%s' failed.""" % (format, file.filename)
    addStatusMessage(REQUEST,_(unicode(msg)))
    return state.set(status='failure',
                     portal_status_message=msg)
except UnicodeError:
    state.setError('input_encoding', 'Improper input encoding selection.')
    msg = """The choosen input encoding does not match the real encoding of """ \
          """your input data in order to convert it to unicode internally."""
    addStatusMessage(REQUEST,_(unicode(msg)))
    return state.set(status='failure',
                     portal_status_message=msg)

except RuntimeError,e:
    addStatusMessage(REQUEST,_(unicode(e)))
    return state.set(status='failure',
                     portal_status_message=e)

# debug message if entries is not a python list
if not entries or not same_type(entries, []):
    state.setError('file', "Here is what came as entries: %s." % entries)
    msg = "There must be something wrong with the parser"
    addStatusMessage(REQUEST,_(unicode(msg)))
    return state.set(status='failure',
                     portal_status_message=msg)

# start building the report
mtool  = context.portal_membership
member = mtool.getAuthenticatedMember()
member_id = member.getId()
fullname = member.getProperty('fullname', None)
if not fullname:
    fullname = 'unknown fullname'
import_date = context.ZopeTime()
if file:
    tmp_report = '[%s] Imported by %s (%s) from file %s:\n\n' \
                 %(import_date, member_id, fullname, file.filename)
else:
    tmp_report = '[%s] Imported by %s (%s):\n\n' \
                 %(import_date, member_id, fullname)

# process import for each entry
processedEntries = 0
importErrors = 0
for entry in entries:

    # Workaround for #36 where an entry represents
    # an error from parser instead of a dict containing
    # importable data
    if not same_type(entry, {}):
        continue

    if entry.get('title'):
        upload = context.processSingleImport(entry,
                                             span_of_search=span_of_search)
        if upload[1] == 'ok':
            processedEntries += 1
        else:
            importErrors += 1
        tmp_report = tmp_report + upload[0]

#context.manage_changeProperties(import_report=report)
context.logImportReport(tmp_report)

# set the portal status message up
msg = "Processed %i entries. There were %i errors. Import processed in %f seconds. See import report below." \
      %(processedEntries, importErrors, context.ZopeTime().timeTime()-start_time)

addStatusMessage(REQUEST, _(unicode(msg)))
state.set(portal_status_message=msg)

# allow import report display in import form
state.set(processed_import=1)

if state.getErrors():
    msg = 'Please correct the indicated errors.'
    addStatusMessage(REQUEST, _(unicode(msg)))
    return state.set(status='failure',
                     portal_status_message=msg)
else:
    return state
