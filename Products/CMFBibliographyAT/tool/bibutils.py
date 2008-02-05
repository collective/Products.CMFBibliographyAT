##########################################################################
#                                                                        #
#           copyright (c) 2005 ITB, Humboldt-University Berlin           #
#           written by: Raphael Ritz, r.ritz@biologie.hu-berlin.de       #
#                                                                        #
##########################################################################

"""
mixin class to support 'bibutils' based transformations

bibutils are written and maintained by Chris Putnam at Scripps
http://www.scripps.edu/~cdputnam/software/bibutils/bibutils.html
"""

import sys, os, os.path
from Globals import InitializeClass
from zLOG import LOG, ERROR
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View

commands = {'bib2xml':'bib2xml',
            'copac2xml':'copac2xml',
            'end2xml':'end2xml',
            'isi2xml':'isi2xml',
            'med2xml':'med2xml',
            'ris2xml':'ris2xml',
            'xml2bib':'xml2bib',
            'xml2end':'xml2end',
            'xml2ris':'xml2ris',
            'copac2bib':'copac2xml | xml2bib ',
            'end2bib':'end2xml | xml2bib ',
            'isi2bib':'isi2xml | xml2bib ',
            'med2bib':'med2xml | xml2bib ',
            'ris2bib':'ris2xml | xml2bib ',
            'bib2end':'bib2xml | xml2end ',
            'bib2ris':'bib2xml | xml2ris ',
            'copac2end':'copac2xml | xml2end ',
            'isi2end':'isi2xml | xml2end ',
            'med2end':'med2xml | xml2end ',
            'ris2end':'ris2xml | xml2end ',
            'end2ris':'end2xml | xml2ris ',
            'copac2ris':'copac2xml | xml2ris ',
            'isi2ris':'isi2xml | xml2ris ',
            'med2ris':'med2xml | xml2ris ',
            }

def _getKey(source_format, target_format):
    return '2'.join([source_format, target_format])

class BibUtils:
    """mixin class to support bibutils based transformations"""

    security = ClassSecurityInfo()

    def __init__(self):
        pass

    security.declareProtected(View, 'isTransformable')
    def isTransformable(self, source_format, target_format):
        """
        test if a transform from source_format to target_format 
        would be feasible
        """
        key = _getKey(source_format, target_format)
        command = commands.get(key, None)
        if command is None:
            return False
        commandlist = [ c.strip() for c in command.split('|') ]

        # open each command once
        transformable = True
        for c in commandlist:

            pass

        return transformable

    security.declareProtected(View, 'transform')
    def transform(self, data, source_format, target_format):
        """
        calling 'bibutils' to transform data from 'source_format'
        to 'target_format'
        """
        key = _getKey(source_format, target_format)
        command = commands.get(key, None)
        if command is None:
            raise ValueError, "No transformation from '%s' to '%s' found." \
                  % (source_format, target_format)

        (fi, fo, fe) = os.popen3(command, 't')
        fi.write(data)
        fi.close()
        result = fo.read()
        fo.close()
        error = fe.read()
        fe.close()
        if error:
            # command could be like 'ris2xml', or 'ris2xml | xml2bib'. It
            # seems unlikely, but we'll code for an arbitrary number of
            # pipes...
            command_list = command.split(' | ')
            for each in command_list:
                if each in error and not result:
                    result = self._callFallback(data,
                                                source_format,
                                                target_format)
        return result

    def _callFallback(self, data, source_format, target_format):

        # call a service somewhere else
        # not implemented yet; for now just log and blow up
        key = _getKey(source_format, target_format)
        command = commands.get(key, None)
        msg = "'%s' not found. Make sure 'bibutils' is installed." \
              % command
        LOG('CMFBibliographyAT.tool.bibutils',
            ERROR,
            msg,
            )
        # XXX I don't think NameError is strictly the right exception,
        # but I can't think of a better one off the top of my head.
        # Perhaps OSError?
        raise NameError, msg

InitializeClass(BibUtils)

