from Products.CMFBibliographyAT.config import CMFBAT_USES_LINGUAPLONE
if CMFBAT_USES_LINGUAPLONE:
    from Products.LinguaPlone.public import StringField, StringWidget
    from Products.LinguaPlone.public import BooleanField, BooleanWidget
else:
    from Products.Archetypes.public import StringField, StringWidget
    from Products.Archetypes.public import BooleanField, BooleanWidget

from Products.CMFBibliographyAT import CMFBibMessageFactory as _

journalField = StringField('journal',
                searchable=1,
                required=0,
                default='',
                is_duplicates_criterion=True,
                widget=StringWidget(
                    label=_(u"label_journal",
                            default=u"Journal"),
                    description=_(u"help_journal",
                                  default=u"A journal name (should be the full journal name)."),
                    ),
                )

volumeField = StringField('volume',
                searchable=1,
                required=0,
                default='',
                is_duplicates_criterion=True,
                widget=StringWidget(
                    label=_(u"label_volume",
                            default=u"Volume"),
                    description=_(u"help_volume",
                                  default=u"The volume of a journal, multivolume book work etc. In most cases it should suffice to use a simple number as the volume identifier."),
                    ),
                )

numberField = StringField('number',
                searchable=1,
                required=0,
                default='',
                is_duplicates_criterion=True,
                widget=StringWidget(
                    label=_(u"label_number",
                            default=u"Number"),
                    description=_(u"help_number",
                                  default=u"The number of a journal, proceedings, technical report etc. Issues of journals, proceedings etc. are usually identified by volume and number; however, issues of the same volume will often be numbered preceedingly which often makes the specification of a number optional. With technical reports, the issuing organization usually also gives it a number."),
                    ),
                )

pagesField = StringField('pages',
                searchable=1,
                required=0,
                default='',
                is_duplicates_criterion=True,
                widget=StringWidget(
                    label=_(u"label_pages",
                            default=u"Pages"),
                    description=_(u"help_pages",
                                  default=u"A page number or range of numbers such as '42-111'; you may also have several of these, separating them with commas: '7,41,73-97'."),
                    ),
                )

howpublishedField = StringField('howpublished',
                searchable=1,
                required=0,
                default='',
                is_duplicates_criterion=True,
                widget=StringWidget(
                    label=_(u"label_howpublished",
                             default=u"How published"),
                    description=_(u"help_howpublished",
                                  default=u"For publications without a publisher. e.g., an 'Institute Report'."),
                    ),
                )

publisherField = StringField('publisher',
                searchable=1,
                required=0,
                default='',
                is_duplicates_criterion=True,
                widget=StringWidget(
                    label=_(u"label_publisher",
                            default=u"Publisher"),
                    description=_(u"help_publisher",
                                  default=u"The publisher's name."),
                    ),
                )

addressField = StringField('address',
                searchable=1,
                required=0,
                default='',
                is_duplicates_criterion=True,
                widget=StringWidget(
                    label=_(u"label_address",
                             default=u"Address"),
                    description=_(u"help_address",
                                  default=u"Publisher's address. For major publishing houses, just the city is given. For small publishers, you can help the reader by giving the complete address."),
                    ),
                )

editionField = StringField('edition',
                searchable=1,
                required=0,
                default='',
                is_duplicates_criterion=True,
                widget=StringWidget(
                    label=_(u"label_edition",
                            default=u"Edition"),
                    description=_(u"help_edition",
                                  default=u"The edition of a book - for example: 'II', '2' or 'second', depending on your preference. Numbers will be turned into ordinal numerals."),
                    ),
                )

booktitleField = StringField('booktitle',
                searchable=1,
                required=0,
                default='',
                is_duplicates_criterion=True,
                widget=StringWidget(
                    label=_(u"label_booktitle",
                            default=u"Book Title"),
                    description=_(u"help_booktitle",
                                  default=u"Title of the book, collection or proceedings, that the cited resource is part of."),
                    ),
                )

editorField = StringField('editor',
                searchable=1,
                required=0,
                default='',
                is_duplicates_criterion=True,
                widget=StringWidget(
                    label=_(u"label_editor",
                            default=u"Editor"),
                    description=_(u"help_editor",
                                  default=u"Name(s) of editor(s). Opposed to the 'author' field, the 'editor' field should contain the editor of the book, collection or proceeding that the reference appears in."),
                    ),
                )

seriesField = StringField('series',
                searchable=1,
                required=0,
                default='',
                is_duplicates_criterion=True,
                widget=StringWidget(
                    label=_(u"label_series",
                            default=u"Series"),
                    description=_(u"help_series",
                                  default=u"The name of a series or set of books. When citing an entire book, the 'title' field gives its title and this optional 'series' field gives the name of a series in which the book is published."),
                    ),
                )

chapterField = StringField('chapter',
                searchable=0,
                required=0,
                default='',
                is_duplicates_criterion=True,
                widget=StringWidget(
                    label=_(u"label_chapter",
                            default=u"Chapter"),
                    description=_(u"help_chapter",
                                  default=u"A chapter number."),
                    ),
                )

organizationField = StringField('organization',
                searchable=1,
                required=0,
                default='',
                is_duplicates_criterion=True,
                widget=StringWidget(
                    label=_(u"label_organization",
                            default=u"Organization"),
                    description=_(u"help_organization",
                                  default=u"The organization sponsoring a conference, issuing a technical report etc."),
                    ),
                )

schoolField = StringField('school',
                required=0,
                searchable=1,
                default='',
                is_duplicates_criterion=True,
                widget=StringWidget(
                    label=_(u"label_school",
                            default=u"School"),
                    description=_(u"help_school",
                                  default=u"The name of the school (college, university etc.) where a thesis was written."),
                    ),
                )

institutionField = StringField('institution',
                required=0,
                searchable=1,
                default='',
                is_duplicates_criterion=True,
                widget=StringWidget(
                    label=_(u"label_institution",
                            default=u"Institution"),
                    description=_(u"help_institution",
                                  default=u"The institution that published the work."),
                    ),
                )

typeField = StringField('publication_type',
                required=0,
                searchable=1,
                default='',
                is_duplicates_criterion=True,
                widget=StringWidget(
                    label=_(u"label_publication_type",
                            default=u"Type"),
                    description=_(u"help_publication_type",
                                  default=u"The type of a technical report, PhD thesis etc. - for example, 'Research Note' or 'Doktorarbeit'."),
                    ),
                )

editor_flagField = BooleanField('editor_flag',
                default=0,
                required=0,
                is_duplicates_criterion=True,
                widget=BooleanWidget(
                    label=_(u"label_editor_flag",
                            default=u"Editor Flag"),
                    description=_(u"help_editor_flag",
                                  default=u"Check here if the author(s) specified above are actually the editor(s) of the book."),
                    )
                )

isbnField = StringField('isbn',
                searchable=1,
                default='',
                is_duplicates_criterion=True,
                widget=StringWidget(
                    label=_(u"label_isbn",
                             default=u"ISBN Number"),
                    description=_(u"help_isbn",
                                  default=u"The ISBN number of this publication."),
                    )
                )
