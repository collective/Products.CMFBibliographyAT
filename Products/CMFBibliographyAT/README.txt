
CMFBibliographyAT is the Archetypes based version of CMFBibliograhy.
It enables handling of references to (scientific) publications
in Plone. It provides a 'Bibliography Folder' content type dedicated
to holding reference objects of various kinds, like for 'articles',
'books', 'preprints', 'techreports', contributions to collections, ...
The folder supports import/export of BibTeX formated files.

In addition the package adds a 'bibliography' action to the portal tabs
and it provides a BibliographyTool called 'portal_bibliography'
through which you can manage the renderers and parsers for the
import/export functionality.


  INSTALL

    * Untar it into your .../Products or .../lib/python/Products folder

    * If you upgrade from a previous version make sure you read the
      "Known Issues" section first.


  CMF/Plone 'AWARIZATION'

    Make sure you have Archetypes installed. Then

    * Use the QickInstaller (available under 'plone_setup' - from plone 2.0 on)

    OR

    * Create an external method at your Plone's root with the
      following information::

      id: install_bibliography

      title: Whatever you want

      module: CMFBibliographyAT.Install

      function: install

    * Click the test tab of this External Method and ensure the
      execution is correct.
      Double check messages prefixed by '***', they may indicate an error.


  What it does

    CMFBibliography provides various new content types:

     o Bibliography Entries: Highly structured content objects to
       hold bibliographic data referencing a publication. The schema
       is derived from BibTeX (LaTeX's bibliography handling modul).

     o Bibliography Folder: Enhanced 'Skinned Folder' with some
       import/import functionality (available through the 'import' tab).

       Allowed content types are restricted to reference types.

       Currently supported import formats are 'BibTeX' and 'Medline'.
       Check out the accompanying files in 'import_samples' to see
       this in action.

       Currently supported export formats: BibTeX (but see below)

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


  KNOWN ISSUES

  * There is no migration path from the old CMFBibliography (not
    AT based) to the new one (AT based; CMFBibliographyAT) yet.

  * If you upgrade to Archetypes 1.3.x you should also upgrade
    CMFBibliographyAT to a version newer than Mai 25th 2004
    (from the CVS 0.4 version) or the meta and portal types
    might be wrong.

  * CMFBibliographyAT is known not to work with Plone's
    'portal_factory' due to the way in which the 'More Authors'
    feature is implemented (you will lose the author information
    if you use 'portal_factory' - XXX: I think this was fixed by
    moving to ATExtensions for the authors field.


  DEPENDENCIES

  * ATExtensions (hard dependency) (from plone.org/products/atextensions)

  * bibutils (optional) http://www.scripps.edu/~cdputnam/software/bibutils
    to extend the range of supported import/output formats


  EXTENSIONS

  * ATBiblioList: An add-on to CMFBibliographyAT that lets organise
    bibliographical references into selection lists and have them
    printed in a "ready to publish" style.

  * AmazonTool: Supports import of bibliographic data from Amazon's
    database by calling their web service per ISBN provided.

  TODO

  * make the schemata TTW configurable (AT's job ;-)

  * improve import capabilities
    (I'm sure the parsers can be fooled)

  * add further XML support (and OAI-MHP in particular)


Enjoy,

  Raphael Ritz

