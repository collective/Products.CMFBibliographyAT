from  bibtex import  BibtexParser, manage_addBibtexParser
from  pyblbibtex import  PyBlBibtexParser, manage_addPyBlBibtexParser
from  medline import  MedlineParser, manage_addMedlineParser
from  ibss import IBSSParser, manage_addIBSSParser
from  isbn import ISBNParser, manage_addISBNParser
from  xml import XMLParser, manage_addXMLParser
from  ris import RISParser, manage_addRISParser
from  endnote import EndNoteParser, manage_addEndNoteParser
from citationmanager import CitationManagerParser, \
     manage_addCitationManagerParser

def initialize(context):
    context.registerClass(BibtexParser,
                          constructors = (manage_addBibtexParser,),
                          )
    context.registerClass(PyBlBibtexParser,
                          constructors = (manage_addPyBlBibtexParser,),
                          )
    context.registerClass(MedlineParser,
                          constructors = (manage_addMedlineParser,),
                          )
    context.registerClass(IBSSParser,
                          constructors = (manage_addIBSSParser,),
                          )
    context.registerClass(EndNoteParser,
                          constructors = (manage_addEndNoteParser,),
                          )
    context.registerClass(RISParser,
                          constructors = (manage_addRISParser,),
                          )
    context.registerClass(XMLParser,
                          constructors = (manage_addXMLParser,),
                          )
    context.registerClass(ISBNParser,
                          constructors = (manage_addISBNParser,),
                          )
    context.registerClass(CitationManagerParser,
                          constructors = (manage_addCitationManagerParser,),
                          )