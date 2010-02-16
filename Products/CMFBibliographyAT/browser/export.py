from zope import component

from bibliograph.rendering.interfaces import IBibliographyRenderer



class BibliographyExportView(object):
    """ """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        """ """

        output_encoding = self.request.get('output_encoding', 'utf-8')
        eol_style = self.request.get('eol_style', 0)
        format = self.request.get('format', 'bibtex')
        response = self.request.response
        renderer = self._getRenderer(format)
        # Hotfix: suffix for Endnote must be  '.enw', not '.end'
        suffix = renderer.target_format == 'end' and 'enw' or renderer.target_format
        response.setHeader('Content-Type', 'application/octet-stream')
        response.setHeader('Content-Disposition',
                           'attachment; filename=%s.%s' % (self.__name__, suffix))
        return self.export(format, output_encoding, eol_style)

    def export(self, format, output_encoding='utf-8', eol_style=0):
        """ """
        renderer = self._getRenderer(format)
        return renderer.render(self.context, output_encoding=output_encoding, msdos_eol_style=eol_style)

    def _getRenderer(self, format):
        utils = component.getAllUtilitiesRegisteredFor(IBibliographyRenderer)
        for renderer in utils:
            if renderer.available and renderer.enabled:
                if format.lower() == renderer.__name__.lower():
                    return renderer
                elif format.lower() == renderer.target_format.lower():
                    return renderer
        return None
