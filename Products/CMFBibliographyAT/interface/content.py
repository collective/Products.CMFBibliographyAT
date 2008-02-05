from zope.interface import Interface

class IBibliographyFolder(Interface):

    """Marker interface for the bibliography folder
       Contains bibliographic items
    """

class ILargeBibliographyFolder(Interface):

    """Marker interface for the btree-based bibliography folder
       Contains bibliographic items
    """

class IBibliographicItem(Interface):

    """Marker interface for bibliogaphic items
       Used to hold the meta data of a publication
       Contained in bibliography folders
    """

class IArticleReference(IBibliographicItem):

    """Marker interface for bibliographic items
       referencing an article
    """

class IBookReference(IBibliographicItem):

    """Marker interface for bibliographic items
       referencing a book
    """

class IBookletReference(IBibliographicItem):

    """Marker interface for bibliographic items
       referencing a booklet
    """

class IConferenceReference(IBibliographicItem):

    """Marker interface for bibliographic items
       referencing a conference (proceedings) volume
    """

class IInBookReference(IBibliographicItem):

    """Marker interface for bibliographic items
       referencing a part in a book
    """

class IInCollectionReference(IBibliographicItem):

    """Marker interface for bibliographic items 
       referencing a part of a collection
    """

class IInProceedingsReference(IBibliographicItem):

    """Marker interface for bibliographic items
       referencing a contribution to a proceedings volume
    """

class IManualReference(IBibliographicItem):

    """Marker interface for bibliographic items 
       referencing a manual
    """

class IMastersthesisReference(IBibliographicItem):

    """Marker interface for bibliographic items
       referencing a masters thesis
    """

class IMiscReference(IBibliographicItem):

    """Marker interface for bibliographic items
       referencing a miscellaneous item
    """

class IPhdthesisReference(IBibliographicItem):

    """Marker interface for bibliographic items
       referencing a Phd thesis
    """

class IPreprintReference(IBibliographicItem):

    """Marker interface for bibliographic items
       referencing a preprint
    """

class IProceedingsReference(IBibliographicItem):

    """Marker interface for bibliographic items
       referencing a proceedings volume
    """

class ITechReportReference(IBibliographicItem):

    """Marker interface for bibliographic items
       referencing a technical report
    """


class IUnpublishedReference(IBibliographicItem):

    """Marker interface for bibliographic items
       referencing unpublished work
    """


class IWebpublishedReference(IBibliographicItem):

    """Marker interface for bibliographic items
       referencing an item published on the web
    """


class IPdfFolder(Interface):

    """Marker interface for specific folders holding PDFs of publications
       within a bibliography folder
    """


class IPdfFile(Interface):

    """Marker interface for items within a PdfFolder
       Used to hold PDFs of publications
    """



