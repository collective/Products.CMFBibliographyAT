##########################################################################
#                                                                        #
#           copyright (c) 2005 ITB, Humboldt-University Berlin           #
#           written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                        #
##########################################################################

from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.Marshall import Marshaller

class BibtexMarshaller(Marshaller):

    security = ClassSecurityInfo()
    security.declareObjectPrivate()
    security.setDefaultAccess('deny')

    def demarshall(self, instance, data, **kwargs):
        if kwargs.has_key('file'):
            if not data:
                data = kwargs['file'].read()
            del kwargs['file']
        bibtool = getToolByName(instance, 'portal_bibliography')
        entry = bibtool.getEntries(data, 'bib')[0]
        instance.setAuthors(entry.get('authors',[]))
        instance.edit(**entry)

    def marshall(self, instance, **kwargs):
        bibtool = getToolByName(instance, 'portal_bibliography')
        data = bibtool.render(instance, 'bib')
        length = len(data)
        content_type = 'application/x-bibtex'
        return (content_type, length, data)

InitializeClass(BibtexMarshaller)

