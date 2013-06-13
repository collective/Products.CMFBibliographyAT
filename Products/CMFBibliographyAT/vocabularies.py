#!/usr/bin/env python
# -*- coding: utf-8 -*-
__docformat__ = 'restructuredtext en'
from zope import interface
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.interfaces import IVocabularyFactory


from plone.i18n.normalizer.base import baseNormalize
from Products.CMFCore.utils import getToolByName

def uniquify(t):
    s = []
    [s.append(i) for i in t if not i in s]
    return s


class RefsTypesF(object):
    """vocabulary to use with plone.app.registry"""
    interface.implements(IVocabularyFactory)

    def __call__(self, context):
        """list available reference types for use in schema field
        """
        bib_tool = getToolByName(context, 'portal_bibliography')
        terms = [SimpleTerm(baseNormalize(ref_type),
                            baseNormalize(ref_type),
                            ref_type)
                 for ref_type in bib_tool.getReferenceTypes()]
        return SimpleVocabulary(terms)

RefsTypes = RefsTypesF()

# vim:set et sts=4 ts=4 tw=80:
