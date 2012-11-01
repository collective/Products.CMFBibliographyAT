# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.Archetypes import PloneMessageFactory as _
from Products.Archetypes.utils import addStatusMessage
from bibliograph.core.utils import _encode
from Products.CMFBibliographyAT.tool.bibliography import ImportParseError
import logging
logger = logging.getLogger('CMFBibliographyAT import')


class ImportView(BrowserView):

    template = ViewPageTemplateFile('import.pt')

    def __call__(self):
        self.processed = False
        self.errors = {}
        start_time = self.context.ZopeTime().timeTime()
        if not self.request.form.get('form.submitted'):
            return self.template()

        # fetch value from request
        input_encoding = self.request.form.get('input_encoding', 'utf-8')
        span_of_search = self.request.form.get('span_of_search', None)
        format = self.request.form.get('format', 'bib')

        # process source
        filename = None
        source = self.request.form.get('up_text')
        if not source:
            upfile = self.request.form.get('file')
            filename = upfile and getattr(upfile, 'filename', None)
            if not filename:
                self.errors['file'] = _(u'You must import a file or enter a'
                                         ' text.')
                addStatusMessage(self.request,
                                 _(u"Please correct the indicated errors."))
                return self.template()
            source = upfile.read()
            if not source or not isinstance(source, basestring):
                msg = "Could not read the file '%s'." % filename
                self.errors['file'] = msg
                addStatusMessage(self.request, _(unicode(msg)))
                return self.template()

        # skip DOS line breaks
        source = source.replace('\r', '')

        # get parsed entries from the Bibliography Tool
        bibtool = getToolByName(self.context, 'portal_bibliography')
        try:
            entries = bibtool.getEntries(source, format, filename,
                                         input_encoding=input_encoding)
        except ImportParseError:
            msg = """%s Parser's 'checkFormat' and guessing the format""" \
                  """ from the file name '%s' failed.""" % (format,
                                                            filename)
            self.errors['format'] = msg
            addStatusMessage(self.request, _(unicode(msg)))
            return self.template()
        except UnicodeError:
            msg = """The choosen input encoding does not match the real  """ \
                  """encoding of your input data in order to convert it to """\
                  """unicode internally."""
            self.errors['input_encoding'] = msg
            addStatusMessage(self.request, _(unicode(msg)))
            return self.template()
        except RuntimeError, e:
            addStatusMessage(self.request, _(unicode(e)))
            return self.template()

        # debug message if entries is not a python list
        if not entries or not isinstance(entries, (list, tuple)):
            msg = "There must be something wrong with the parser"
            addStatusMessage(self.request, _(unicode(msg)))
            return self.template()

        # start building the report
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        fullname = member.getProperty('fullname', None)
        if fullname:
            username = '%s (%s)' % (_encode(fullname), _encode(member.getId()))
        else:
            username = _encode(member.getId())
        tmp_report = '[%s] Imported by %s' % (self.context.ZopeTime(),
                                              username)
        if filename is not None:
            tmp_report += ' from file %s' % _encode(filename)
        tmp_report += ':\n\n'

        # process import for each entry
        processedEntries = 0
        importErrors = 0

        logger.info('Start import of %s raw entries.' % len(entries))
        counter = 0

        for entry in entries:
            counter += 1
            count = '#%05i: ' % counter
            logger.info(count + 'processing entry')
            # Workaround for #36 where an entry represents
            # an error from parser instead of a dict containing
            # importable data
            if isinstance(entry, basestring):
                msg = 'Entry could not be parsed! %s' % _encode(entry)
                upload = (msg, 'error')
                logger.error(count + msg)
            elif entry.get('title'):
                logger.info(count + 'Normal processing')
                upload = self.context.processSingleImport(entry,
                                                 span_of_search=span_of_search)
            else:
                formated = '; '.join(['%s=%s' % (key, entry[key])
                                      for key in sorted(entry.keys())
                                      if key == key.lower()])
                upload = ('Found entry without title: %s\n' % formated,
                          'error')
                logger.error(count + upload[0])
            if upload[1] == 'ok':
                processedEntries += 1
            else:
                importErrors += 1
            state, msg = _encode(upload[1].upper()), _encode(upload[0])
            tmp_report += '%s: %s\n' % (state, msg)
        self.context.logImportReport(tmp_report)
        self.processed = True
        # set the portal status message up
        msg = "Processed %i entries. There were %i errors. "\
              "Import processed in %f seconds. See import report below." \
              % (processedEntries, importErrors,
                 self.context.ZopeTime().timeTime() - start_time)
        logger.info(msg)
        addStatusMessage(self.request, _(unicode(msg)))
        return self.template()
