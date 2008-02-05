############################################################################
#                                                                          #
#             copyright (c) 2003 ITB, Humboldt-University Berlin           #
#             written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                          #
############################################################################

"""BibtexRenderer class"""

# Python stuff
import re, string

# Zope stuff
from Globals import InitializeClass
from App.Dialogs import MessageDialog
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2Base

# Archetypes stuff
from Products.Archetypes.utils import shasattr

# Bibliography stuff
from Products.CMFBibliographyAT.tool.renderers.base \
     import IBibliographyRenderer, BibliographyRenderer
from Products.CMFBibliographyAT.config import FOLDER_TYPES as BIBFOLDER_TYPES

from Products.CMFCore.utils import getToolByName
from Products.CMFBibliographyAT.utils import _encode
from Products.CMFBibliographyAT.utils import _decode
from Products.CMFBibliographyAT.encodings import _utf8enc2latex_mapping
from Products.CMFBibliographyAT.encodings import UNICODE_ENCODINGS


_entity_mapping = {'&mdash;':'{---}',
                   '&ndash;':'{--}',
                   }

class BibtexRenderer(BibliographyRenderer):
    """
    A specific renderer to export bibliographical references in BiBTeX format.
    Note: If the output encoding of the BiBTeX renderer is not unicode capable,
    all non-ASCII characters will be resolved to LaTeX entities.
    """

    __implements__ = (IBibliographyRenderer ,)

    meta_type = "Bibtex Renderer"

    format = {'name':'BibTeX',
              'extension':'bib'}

    def __init__(self,
                 id = 'bibtex',
                 title = "BibTeX renderer"):
        """
        initializes only id and title
        """
        self.id = id
        self.title = title

    def render(self, objects, output_encoding=None, title_force_uppercase=False, msdos_eol_style=False, **kwargs):
        """
        renders a bibliography object in BiBTex format
        """
        resolve_unicode = output_encoding not in UNICODE_ENCODINGS

        if not isinstance(objects, (list, tuple)):
            objects = [objects]
        bib_tool = getToolByName(objects[0], 'portal_bibliography')
        ref_types = bib_tool.getReferenceTypes()
        filter = {'portal_type' : ref_types}
        # processing a BibFolder's contents
        if objects[0].portal_type in BIBFOLDER_TYPES:
            # tim2p: Begin some memory optimization for BTree-ish folder types.
            # There is an element of hack to this. While it relies on a public
            # method, that method is on a private ('_tree') attribute.
            # Well, it saves me 90MB of RAM for my c.700 ref database, so I'm happy :).
            if isinstance(objects[0], BTreeFolder2Base):
                with_btree_memory_efficiency = True
                entries = objects[0]._tree.itervalues()
            else:
                with_btree_memory_efficiency = False
                entries = objects[0].contentValues(filter=filter)
            rendered = []
            for entry in entries:
                # The first condition is just a minor performance tweak. If we are not
                # using btree_memory_efficiency, then the wrong portal types will already
                # be filtered by the contentValues call above.
                if with_btree_memory_efficiency and entry.portal_type not in ref_types:
                    continue
                if with_btree_memory_efficiency:
                    # _tree.itervalues() returns unwrapped objects, but renderEntry needs
                    # context-aware objects, so we wrap it.
                    # Check to see if the object has been changed (elsewhere in the
                    # current transaction/request.
                    changed = getattr(entry, '_p_changed', False)
                    deactivate = not changed
                    entry = entry.__of__(objects[0])
                bibtex_string = self.renderEntry(entry,
                                                 resolve_unicode=resolve_unicode,
                                                 title_force_uppercase=title_force_uppercase,
                                                 msdos_eol_style=msdos_eol_style,
                                                )
                rendered.append(bibtex_string)
                if with_btree_memory_efficiency and deactivate:
                    # We now 'unload' the entry from the ZODB object cache to reclaim its memory.
                    # See http://wiki.zope.org/ZODB/UnloadingObjects for details.
                    # XXX In fact, there are probably no bad side-effects to making this call
                    # even if not with_btree_memory_effiency. However, I want my patch to be
                    # as non-intrusive as possible, so I don't do that now.
                    entry._p_deactivate()
            return self._convertToOutputEncoding(''.join(rendered),
                                                 output_encoding=output_encoding)
        
        # processing a single or a list of BibRef Items
        else:
            rendered = []
            for object in objects:
                if object.portal_type in ref_types:
                    bibtex = self.renderEntry(object,
                                              resolve_unicode=resolve_unicode,
                                              title_force_uppercase=title_force_uppercase,
                                              msdos_eol_style=msdos_eol_style)
                    rendered.append(bibtex)
            return self._convertToOutputEncoding(''.join(rendered),
                                                 output_encoding=output_encoding)        
            
        return ''

    def renderEntry(self, entry, resolve_unicode=False, title_force_uppercase=False, msdos_eol_style=False):
        """
        renders a BibliographyEntry object in BiBTex format
        """
        bib_key = self._validKey(entry)
        bibtex = "\n@%s{%s," % \
                 (entry.meta_type[:-9], bib_key)
        # [:-9] assumes we have a "...Reference" type
        if shasattr(entry, 'editor_flag') and \
               entry.getFieldValue('editor_flag'):
            bibtex += "\n  editor = {%s}," % \
                      entry.Authors(sep=' and ',
                                    lastsep=' and ',
                                    format="%L, %F %M",
                                    abbrev=0,
                                    lastnamefirst=0)
        else:
            bibtex += "\n  author = {%s}," % \
                      entry.Authors(sep=' and ',
                                    lastsep=' and ',
                                    format="%L, %F %M",
                                    abbrev=0,
                                    lastnamefirst=0)
        aURLs = self.AuthorURLs(entry)
        if aURLs.find('http') > -1:
            bibtex += "\n  authorURLs = {%s}," % aURLs
        if title_force_uppercase:
            bibtex += "\n  title = {%s}," % self._braceUppercase(entry.Title())
        else:
            bibtex += "\n  title = {%s}," % entry.Title()
        bibtex += "\n  year = {%s}," % entry.getPublication_year()
        url = entry.aq_base.getURL()
        if url: bibtex += "\n  URL = {%s}," % url
        bibtex += "\n  abstract = {%s}," % entry.getAbstract()

        if hasattr(entry, 'source_fields') and entry.source_fields:
            source_fields = list(entry.source_fields)
            field_values = [entry.getFieldValue(name) \
                            for name in source_fields]
            if 'publication_type' in source_fields:
                source_fields[source_fields.index('publication_type')] = 'type'
            for key, value in zip(source_fields, field_values):
                if value:
                    bibtex += "\n  %s = {%s}," % (key, value)

        kws = ', '.join(entry.Subject())
        if kws:
            bibtex += "\n  keywords = {%s}," % kws
        note = entry.getNote()
        if note:
            bibtex += "\n  note = {%s}," % note
        annote = entry.getAnnote()
        if annote:
            bibtex += "\n  annote = {%s}," % annote
        if bibtex[-1] == ',':
            bibtex = bibtex[:-1] # remove the trailing comma
        bibtex += "\n}\n"
        bibtex = self._normalize(bibtex, resolve_unicode=resolve_unicode)

        # leave these lines to debug _utf8enc2latex_mapping problems (for now)
        try:
            if resolve_unicode: debug = _decode(bibtex).encode('latin-1')
        except UnicodeEncodeError:
            print 'UnicodeEncodeError (latin-1): caused by object with ID: %s' % bib_key

        if msdos_eol_style:
            bibtex = bibtex.replace('\n', '\r\n')
        return bibtex

    def _validKey(self, entry):
        """
        uses the Zope object id but
        removes characters not allowed in BibTeX keys
        """
        raw_id = entry.getId()
        # This substitution is based on the description of cite key restrictions at
        # http://bibdesk.sourceforge.net/manual/BibDesk%20Help_2.html
        return re.sub('[ "@\',\\#}{~%&$^]', '', raw_id)

    def AuthorURLs(self, entry):
        """a string with all the known author's URLs;
        helper method for bibtex output"""
        a_list = entry.getAuthors()
        a_URLs = ''
        for a in a_list:
            url = a.get('homepage', ' ')
            a_URLs += "%s and " % url
        return a_URLs[:-5]

    def _normalize(self, text, resolve_unicode=True):
        text.replace('\\', '\\\\')
        text = self._resolveEntities(text)
        if resolve_unicode:
            text = self._resolveUnicode(text)
        text = self._escapeSpecialCharacters(text)
        return text

    def _resolveEntities(self, text):
        for entity in _entity_mapping.keys():
            text = text.replace(entity, _entity_mapping[entity])
        return text

    def _resolveUnicode(self, text):
        for unichar in _utf8enc2latex_mapping.keys():
            text = _encode(_decode(text).replace(unichar, _utf8enc2latex_mapping[unichar]))
        text = _encode(_decode(text).replace(r'$}{$',''))
        return text

    def _braceUppercase(self, text):
        for uc in string.uppercase:
            text = text.replace(uc, r'{%s}' % uc)
        return text

    def _escapeSpecialCharacters(self, text):
        """
        latex escaping some (not all) special characters
        """
        text.replace('\\', '\\\\')
        escape = ['~', '#', '&', '%', '_']
        for c in escape:
            text = text.replace(c, '\\' + c )
        return text

InitializeClass(BibtexRenderer)


def manage_addBibtexRenderer(self, REQUEST=None):
    """ """
    try:
        self._setObject('bibtex', BibtexRenderer())
    except:
        return MessageDialog(
            title='Bibliography tool warning message',
            message='The renderer you attempted to add already exists.',
            action='manage_main')
    return self.manage_main(self, REQUEST)
