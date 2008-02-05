############################################################################
#                                                                          #
#             copyright (c) 2004 ITB, Humboldt-University Berlin           #
#             written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                          #
############################################################################


"""PDFRenderer class"""


# Python stuff
import os, tempfile, shutil


# Zope stuff
from Globals import InitializeClass
from App.Dialogs import MessageDialog


# CMF stuff
from Products.CMFCore.utils import getToolByName
from bibtex import _entity_mapping


from Products.CMFBibliographyAT.encodings import _utf8enc2latex_mapping


from Products.CMFBibliographyAT.utils import _encode, _decode


# Bibliography stuff
from Products.CMFBibliographyAT.tool.renderers.base \
     import IBibliographyRenderer, BibliographyRenderer


DEFAULT_TEMPLATE = r"""
\documentclass[english,12pt,a4paper]{article}
\usepackage[T1]{fontenc}
\usepackage[latin9]{inputenc}
\usepackage{bibmods}
\usepackage{bibnames}
\usepackage{showtags}
\renewcommand{\refname}{~}


\begin{document}
\begin{center}
{\large \bf %s}\\
(URL: %s)
\end{center}


~\hfill \today


\nocite{*}
\bibliographystyle{abbrv}
\bibliography{references}


\end{document}
"""


class PDFRenderer(BibliographyRenderer):
    """
    A renderer that produces a PDF document containing bibliographical references. The PDF export is rendered by PDFLaTeX.
    """


    __implements__ = (IBibliographyRenderer ,)


    meta_type = "PDF Renderer"


    format = {'name':'PDF',
              'extension':'pdf'}
    template = ''


    _properties = tuple([ prop for prop in BibliographyRenderer._properties
                          if prop['id'] != 'default_output_encoding' ]) + \
    (
            {'id':'template',
             'type':'text',
             'mode':'w'},
    )


    def __init__(self,
                 id = 'pdf',
                 title = "PDF renderer (via latex/bibtex)"):
        """
        initializes id, title and the default LaTeX template
        """
        self.id = id
        self.title = title
        self.template = DEFAULT_TEMPLATE


    def isAvailable(self):
        """ test the availability of the following commands on the server's filesystem:


                latex, pdflatex, bibtex


        """
        # still TODO
        return True


    def initializeDefaultOutputEncoding(self, portal_instance=None):
        """ not needed for PDF renderer
        """
        pass


    def getDefaultOutputEncoding(self):
        """ not needed for PDF renderer
        """
        return None


    def getAvailableEncodings(self):
        """ not needed for PDF renderer
        """
        return []


    def _normalize(self, text):
        text = self._resolveEntities(text)
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
        return text


    def _escapeSpecialCharacters(self, text):
        """
        latex escaping some (not all) special characters
        """
        escape = ['~', '#', '&', '%', '_']
        for c in escape:
            text = text.replace(c, '\\' + c )
        return text


    def render(self, objects, **kwargs):
        """
        renders a bibliography object in PDF format
        """
        if not isinstance(objects, (list, tuple)):
            objects =[objects]
        bib_tool = getToolByName(objects[0], 'portal_bibliography')
        ref_types = bib_tool.getReferenceTypes()
        bibtex_source = ''
        container_object = objects[0]
        for object in objects:
            bibtex_source = bibtex_source + bib_tool.render(object,
                                                            format='BibTex',
                                                            output_encoding='latin-1',
                                                            title_force_uppercase=True)


        return self.processSource(bibtex_source,
                                  container_object.title_or_id(),
                                  container_object.absolute_url())


    def processSource(self, source, title, url):
        """
        use latex/bibtex/pdflatex to generate the pdf
        from the passed in BibTeX file in 'source' using
        the (LaTeX) source tempalte from the renderer's
        'template' property
        """
        template = self.getProperty('template', DEFAULT_TEMPLATE)
        template = template % (unicode(self._normalize(title), 'utf-8').encode('latin-1'), unicode(self._normalize(url), 'utf-8').encode('latin-1'))
        wd = self.getWorkingDirectory()
        tex_path = os.path.join(wd, 'template.tex')
        bib_path = os.path.join(wd, 'references.bib')
        tex_file = open(tex_path, 'w')
        bib_file = open(bib_path, 'w')
        tex_file.write(template)
        bib_file.write(source)
        tex_file.close()
        bib_file.close()
        os.system("cd %s; latex %s"% (wd, tex_path))
        os.system("cd %s; bibtex %s"% (wd, 'template'))
        os.system("cd %s; latex %s"% (wd, 'template.tex'))
        os.system("cd %s; pdflatex %s"% (wd, tex_path))
        pdf_file= open(os.path.join(wd, "template.pdf"), 'r')
        pdf = pdf_file.read()
        pdf_file.close()
        self.clearWorkingDirectory(wd)
        return pdf




    def getWorkingDirectory(self):
        """
        returns the full path to a newly created
        temporary working directory
        """
        tmp_dir = tempfile.mkdtemp()
        renderer_dir = '/'.join(os.path.split(__file__)[:-1])
        resource_dir = os.path.join(renderer_dir, 'latex_resources')
        for file in os.listdir(resource_dir):
            source = os.path.join(resource_dir, file)
            destination = os.path.join(tmp_dir, file)
            if os.path.isfile(source):
                shutil.copy(source, destination)
        return tmp_dir


    def clearWorkingDirectory(self, wd):
        """
        removes the temporary working directory
        """
        for file in os.listdir(wd):
            try:
                path = os.path.join(wd, file)
                os.remove(path)
            except OSError:
                pass
        os.rmdir(wd)


InitializeClass(PDFRenderer)




def manage_addPDFRenderer(self, REQUEST=None):
    """ """
    ## self._setObject('pdf', PDFRenderer())
    try:
        self._setObject('pdf', PDFRenderer())
    except:
        return MessageDialog(
            title='Bibliography tool warning message',
            message='The renderer you attempted to add already exists.',
            action='manage_main')
    return self.manage_main(self, REQUEST)
