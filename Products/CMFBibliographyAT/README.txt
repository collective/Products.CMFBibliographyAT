CMFBibliographyAT
=================

CMFBibliographyAT is the Archetypes based version of CMFBibliograhy.  It
enables handling of references to (scientific) publications in Plone. It
provides a 'Bibliography Folder' content type dedicated to holding reference
objects of various kinds, like for 'articles', 'books', 'preprints',
'techreports', contributions to collections, ...  The folder supports
import/export of BibTeX formated files.

In addition the package adds a 'bibliography' action to the portal tabs and it
provides a BibliographyTool called 'portal_bibliography' through which you can
manage the renderers and parsers for the import/export functionality.


Installation
------------

* Add ``Products.CMFBibliographyAT`` to the ``eggs`` option of your
  buildout.cfg file and re-run buildout.

* Either choose the ``CMFBibliographyAT`` extension profile while
  creating a new Plone site or install it through the add-on 
  control panel within the Plone UI


What it does
------------

CMFBibliography provides various new content types:

* Bibliography Entries: Highly structured content objects to
  hold bibliographic data referencing a publication. The schema
  is derived from BibTeX (LaTeX's bibliography handling modul).

* Bibliography Folder: Enhanced 'Skinned Folder' with some
  import/import functionality (available through the 'import' tab).

Allowed content types are restricted to reference types.

Currently supported import formats are 'BibTeX', 'Endnote', 'RIS',  'Medline'
and XML/MODS.  Check out the accompanying files in 'import_samples' to see this
in action.

Currently supported export formats: BibTeX (but see below), 'Endnote', 'RIS'
and 'XML/MODS'.


Under the folder's 'defaults' tab you can (i) specify default
links for authors of references with the folder and (ii) define
a ranking for the references within the folder. Through the
ranking it is possible to control which references will be
returned when "asking" the folder for its 'Top(n)' references
(see the bibliography folder's source code for more).

In addition CMFBibliographyAT adds two field indexes ('Authors'
and 'publication_year') and three meta data fields ('Authors',
'publication_year', and 'Source') to the portal catalog (if not
present) to provide the 'bibliography' action which is added
to the portal tabs (if you don't want this, go to
'portal_bibliography > Actions' and tick off its visibility).


Dependencies
------------

* Bibutils (optional) http://www.scripps.edu/~cdputnam/software/bibutils
  to extend the range of supported import/output formats. Bibutils is
  mandatory for any kind of export/import. Minimum version is Bibutils 4.6.

Resources
---------

* Bugtracker: http://plone.org/products/cmfbibliographyat/issues
* For questions or for giving feedback: please ask on the plone-biblio
  mailing list: https://mail.das-netzwerkteam.de/mailman/listinfo/plone-biblio


Author
------
* Raphael Ritz (original author)
* Andreas Jung (current maintainer)

Credits
-------
* The CMFBiblibgraphyAT 1.0 release has been made possible with funding of the Humboldt University, Berlin
