## Script (Python) "get_bibliography_import_ftests"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Use case "Bibliography Import"

"""
Member adds bibfolder and imports a reference (two times)
(extended from 'usecase_login')
"""

selenium = context.portal_selenium
suite = selenium.getSuite()
target_language = 'en'
suite.setTargetLanguage(target_language)
selenium.addUser(id='sampleadmin',
                 fullname='Sample Admin',
                 roles=['Member', 'Manager',])
selenium.addUser(id='samplemember',
                 fullname='Sample Member',
                 roles=['Member',])

suite.addTests(
    "Bibliography import",
    "Login as member",
    suite.open("/logout"),
    suite.open('/'),
    suite.verifyElementPresent('portlet-login'),
    suite.verifyElementPresent('__ac_name'),
    suite.verifyElementPresent('__ac_password'),
    suite.type("__ac_name", 'samplemember'),
    suite.type("__ac_password", "admin"),
    suite.clickAndWait("submit"), # Should be name=login
    suite.verifyTextPresent("You are now logged in"),
    suite.verifyElementNotPresent("portlet-login"),
    "Add bibliography folder",
    suite.open("/Members/samplemember/createObject?type_name=BibliographyFolder&id=test_bib_folder"),
    suite.verifyTextPresent("Bibliography Folder has been created."),
    suite.type("title", "selenium test"),
    suite.clickAndWait("form_submit"),
    suite.verifyTextPresent("Changes saved."),
    "Import a reference",
    suite.open("/Members/samplemember/test_bib_folder/bibliography_importForm"),
    suite.type("up_text", """@Book{Lutz2001,
  author =       {Mark Lutz},
  authorURLs =   {http://home.rmi.net/~lutz/},
  title =        {Programming Python.},
  URL =          {http://home.rmi.net/~lutz/about-pp2e.html},
  abstract =     {This edition has been updated for Python version 2.
  More significantly, it is also an almost entirely new advanced Python topics
  book--a complete rewrite from the ground up. Very roughly, this edition includes:

    * 240 pages (4 chapters) on Systems Programming
    * 260 pages (4 chapters) on GUI Programming
    * 400 pages (6 chapters) on Internet Scripting
    * 150 pages (3 chapters) on Databases, Objects, and Text
    * 100 pages (2 chapters) on Python/C Integration

  To give you some idea of this edition's scope, it spans 1256 pages in its final
  published format, and includes some 446 program file examples, and 302 screen
shots
  (broken down here). See the table of contents link above for more content details.

  The book also includes a brand new CD-ROM with book examples, Python version 2.x
  release packages and installers, and related open source packages (NumPy, SWIG, PIL,
  PMW, and so on). Among other things, the book examples distribution on CD includes
  self-launching and Python-coded clocks, text editors, image viewers, email clients,
  calculators, and more.},
  publisher =    {O'Reilly},
  year =         2001,
  address =      {Sebastoplol, CA},
  edition =      {3rd}
  }"""),
    suite.clickAndWait("form.button.import"),
    suite.verifyTextPresent("Processed Entries: 1. Errors: 0."),
    "Import same reference again",
    suite.type("up_text", """@Book{Lutz2001,
  author =       {Mark Lutz},
  authorURLs =   {http://home.rmi.net/~lutz/},
  title =        {Programming Python.},
  URL =          {http://home.rmi.net/~lutz/about-pp2e.html},
  abstract =     {This edition has been updated for Python version 2.
  More significantly, it is also an almost entirely new advanced Python topics
  book--a complete rewrite from the ground up. Very roughly, this edition includes:

    * 240 pages (4 chapters) on Systems Programming
    * 260 pages (4 chapters) on GUI Programming
    * 400 pages (6 chapters) on Internet Scripting
    * 150 pages (3 chapters) on Databases, Objects, and Text
    * 100 pages (2 chapters) on Python/C Integration

  To give you some idea of this edition's scope, it spans 1256 pages in its final
  published format, and includes some 446 program file examples, and 302 screen
shots
  (broken down here). See the table of contents link above for more content details.

  The book also includes a brand new CD-ROM with book examples, Python version 2.x
  release packages and installers, and related open source packages (NumPy, SWIG, PIL,
  PMW, and so on). Among other things, the book examples distribution on CD includes
  self-launching and Python-coded clocks, text editors, image viewers, email clients,
  calculators, and more.},
  publisher =    {O'Reilly},
  year =         2001,
  address =      {Sebastoplol, CA},
  edition =      {3rd}
  }"""),
    suite.clickAndWait("form.button.import"),
    suite.verifyTextPresent("Processed Entries: 0. Errors: 1."),
    "Manage duplicates",
    suite.open("/Members/samplemember/test_bib_folder/bibliography_manage_duplicates"),
    suite.verifyTextPresent("Reference Duplication Management"),
    suite.test_delete_object(folder='/Members/samplemember',id='test_bib_folder'),
  )

return suite
