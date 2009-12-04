from zope import component

from bibliograph.rendering.interfaces import IBibliographyRenderer



class BibliographyExportView(object):
    """ """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        """ """

        format = self.request.get('format', 'bibtex')
        response = self.request.response
        renderer = self._getRenderer(format)
        response.setHeader('Content-Type', 'application/octet-stream')
        response.setHeader('Content-Disposition',
                           'attachment; filename=%s.%s' % (self.__name__, renderer.target_format))
        return self.export(format)

    def export(self, format):
        """ """
        renderer = self._getRenderer(format)
        return renderer.render(self.context)

    def _getRenderer(self, format):
        utils = component.getAllUtilitiesRegisteredFor(IBibliographyRenderer)
        for renderer in utils:
            if renderer.available and renderer.enabled:
                if format.lower() == renderer.__name__.lower():
                    return renderer
                elif format.lower() == renderer.target_format.lower():
                    return renderer
        return None
