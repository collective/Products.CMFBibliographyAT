README.txt
==========

You can find in this directory the Selenium Tests for CMFBibliography

Launching the Selenium Tests
----------------------------

Install Selenium Product

Install Selenium in your Plone via QuickInstaller.

You should be able to launch them by running a browser :

http://INSTANCE_URL/PLONE_SITE_URL/TestRunner.html?test=CMFBibliographyTest.html

if this fails CMFBibliographySelenium.html will do the job (code
duplication):

http://INSTANCE_URL/PLONE_SITE_URL/CMFBibliographySelenium.html

*ATTENTION* : make sure you are logged out of Zope/Plone to test.

ps. add "?auto=true" for Selenium to launch all tests automatically.

Modifications for it to work :
------------------------------

the Member space of the user if hardcoded (for the moment) in the
test, thus modify "arthur" to match your plone username.

Documentation sources
---------------------

Thanks to Grig Gheorghiu :
http://agiletesting.blogspot.com/2005/04/using-selenium-to-test-plone-site-part.html


--
Arthur Lutz - Logilab 2005
http://www.logilab.org  -  contact@logilab.fr