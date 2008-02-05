from  bibtex import  BibtexRenderer, manage_addBibtexRenderer
from  pdf import  PDFRenderer, manage_addPDFRenderer
from  xml import  XMLRenderer, manage_addXMLRenderer
from  endnote import  EndRenderer, manage_addEndRenderer
from  ris import  RISRenderer, manage_addRISRenderer
# from  MedlineRenderer import  MedlineRenderer, manage_addMedlineRenderer

def initialize(context):
    context.registerClass(BibtexRenderer,
                          constructors = (manage_addBibtexRenderer,),
                          )
    context.registerClass(RISRenderer,
                          constructors = (manage_addRISRenderer,),
                          )
    context.registerClass(EndRenderer,
                          constructors = (manage_addEndRenderer,),
                          )
    context.registerClass(XMLRenderer,
                          constructors = (manage_addXMLRenderer,),
                          )
    context.registerClass(PDFRenderer,
                          constructors = (manage_addPDFRenderer,),
                          )
##     context.registerClass(MedlineRenderer,
##                           constructors = (manage_addMedlineRenderer,),
##                           )
