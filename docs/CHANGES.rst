
Changelog
=========

1.1.4 (2013-09-16)
------------------

* packaging problem with 1.1.3 [jensens]

1.1.3 (2013-09-16)
------------------

* Added a zope3 vocabulary factory grabbing all reference types

* fix id cooker control panel string parsing issue.

* added way to let subscriber add at least minor info to the log
  and some code formatting
  [jensens]

* fix migration [kiorky]

* fix some broken asumption about month [kiorky]

* handle some utf-8 decode problems [kiorky]

* fix schema access in subclasses (fix conferences atleast) [kiorky]

* Allow PDF Files, in pdf folders [kiorky]

1.1.2 (2011/07/11)
------------------

* throw an event for each imported entry.
  [jensens]

* fixed import report on write too. Same problem with fullname: it can be 
  unicode.

* fixed import report: for some reason the new report might be uniocde, (maybe in
  Plone 4 username or email is unicode?) but merging it with the old report 
  before storing it failed: old report is utf8 so convert unicode to utf8 if 
  necessary.
  [jensens]

* removed strange (used undefined variables) and superfluos (unused) code. 
  [jensens]

* added a formatter view for the single result-item. this can be overruled by a 
  layer-bond view if one needs a different view on a result item.
  [jensens]  

* moved bibliography_importForm from ControllerPageTemplate to view-class. 
  [jensens]

* added self-contained buildout with test setup. [jensens]

* cleanup import code and other parts of content/folder.py to enable 
  import into subclassed types. [jensens]

1.1.1 (2010/08/22)
------------------
* compatiblity with Plone 4.0rc1

1.1.0 (2010/07/05)
------------------
* final 1.1.0 release

1.1.0b8 (2010/07/05)
--------------------
* fixed handling of non-ascii characters in author names due to incompatible
  Plone API changes in normalizeString(). Now using the unicodedata.normalize()
  functionality which may result in a slightly different id generation.

1.1.0b7 (2010/07/05)
--------------------
* another Plone 3/4 fix incompatibility in transforms/*

1.1.0b6 (2010/06/10)
--------------------
* fixed another Plone 3/4 incompatibility in transforms/*

1.1.0b5 (2010/06/10)
--------------------
* fixed another Plone 3/4 incompatibility in transforms/*

1.1.0b4 (2010/06/10)
--------------------
* fixed Plone 3/4 incompatibility in transforms/*

1.1.0b3 (2010/06/10)
--------------------
* fixed import

1.1.0b2 (2010/05/10)
--------------------
* fixed missing import

1.1.0b1 (2010/05/10)
--------------------
* compatibility with Plone 3 + Plone 4 

1.0.5 (2010-04-22)
------------------
* fixed handling of the 'note' field on the export adapter level

1.0.4 (2010-04-12)
------------------
* removed stupid filtering from bibliography_view making this view completely 
  useless for anonymous visitors

1.0.3 (2010-04-07)
------------------
* exposing installed Bibutils version within the Plone UI (import/export tab of the 
  bibliography management configlet)

1.0.2 (2010-04-01)
------------------
* checking minimum Bibutils version and logging it during the Zope
  startup phase

1.0.1 (2010-03-22)
------------------
* removed stupid role check from bibliograph_search.pt which made
  the bibliographic search unusable for anonymous users

1.0.0 (2010-03-19)
------------------
* final release

1.0.0c2 (2010-03-09)
--------------------
* fixed COINS data for article reference (jtitle -> title)

1.0.0c1 (2010-03-03)
--------------------
* release candidate

1.0.0b13 (2010-02-16)
---------------------
* suffix for generated Endnote exports must be '.enw', not '.end'

1.0.0b12 (2010-02-09)
---------------------
* fix interface decl. for @@export

1.0.0b11 (2010-02-09)
---------------------
* #87 - PDF reference popup did not work
* re-hacked support for support the export of single bibliographic items

1.0.0b10 (2010-02-03)
---------------------
* fixed all unittests
* #81 - fixed strange filtering for anonymous in bibliography_view

1.0.0b9 (2010-01-30)
--------------------
* moved encoding checks directly into checkEncoding()
* handling UTF-8 BOM properly
* removed encoding guessing code - explicit is better than implicit

1.0.0b8 (2010-01-29)
--------------------
* minor but critical bugfix in input encoding checker

1.0.0b7 (2010-01-29)
--------------------
* re-added selection for input encoding on the import form
* added through-the-ZMI property portal_properties -> extensions_properties -> available_input_encodings
* added strong encoding check for uploaded data

1.0.0b6 (2010-01-28)
--------------------
* using UTF-8 output encoding for all renderers except BibTeX (ASCII/LaTeX notation)
* cleanup (internal/UI) of encoding related issues

1.0.0b5 (2010-01-25)
--------------------
* fixed installation/uninstallation issues in setuphandler.py and
  exportimport handler

1.0.0b4 (2010-01-22)
--------------------
* fixed issues related to the input encoding of RIS files
* added note on input encodings related to RIS files to the input form 

1.0.0b3 (2010-01-20)
--------------------
* fixed API name clash for getProperty()

1.0.0b2 (2010-01-20)
--------------------

* removed "docs" tab from configuration panel (since it was empty)
* added portal_properties/cmfbibat_properties as replacement for persistent 
  perferences for parsers/renderers (#82)
* added updateProperty(), getProperty(), isParserEnabled(), isRendererEnabled()
  methods to portal_bibliography
* fixed several forms dealing with the parser/renderer preferences

1.0.0b1 (2010-01-10)
--------------------

* 1.0.0 beta 1 release

1.0.0a7 (2009-12-19)
--------------------

* fix for error #36

1.0.0a6 (2009-12-19)
--------------------

* added support for using portal_factory


1.0.0a5 (2009-12-18)
--------------------

* fixed Amazon link for ISBN-13 numbers

1.0.0a4 (2009-12-18)
--------------------

* BibTeX export adapter did not provide 'publication_month' 

1.0.0a3 (2009-12-18)
--------------------

* fixed bug in PMI migration code
* increased the length of some string fields for better usability
* migration code for PMID
* relaxed some test due to test failures (XML BOM)


1.0.0a1 (2009-12-12)
--------------------

* added 'pyisbn' dependency
* added ISBN validation support to the 'identifiers' field
* made orginal 'isbn' field invisible
* added 0.9 -> 1.0 migration code for copying the 'isbn' field
  value into the 'identifiers' field
* the filename generated by the @@export view now ends with
  the proper suffix according to the selected export format
* the export adapter did work with keywords (using 'subject'
  instead of 'keywords')

