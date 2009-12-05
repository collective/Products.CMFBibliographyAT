from Products.CMFBibliographyAT.config import CMFBAT_USES_LINGUAPLONE
if CMFBAT_USES_LINGUAPLONE:
    from Products.LinguaPlone.public import StringField, StringWidget
    from Products.LinguaPlone.public import BooleanField, BooleanWidget
else:
    from Products.Archetypes.public import StringField, StringWidget
    from Products.Archetypes.public import BooleanField, BooleanWidget


journalField = StringField('journal',
                searchable=1,
                required=0,
                default='',
                is_duplicates_criterion=True,
                widget=StringWidget(label="Journal",
                    label_msgid="label_journal",
                    description="A journal name (should be the full journal name).",
                    description_msgid="help_journal",
                    i18n_domain="cmfbibliographyat",),
                )

volumeField = StringField('volume',
                searchable=1,
                required=0,
                default='',
                is_duplicates_criterion=True,
                widget=StringWidget(label="Volume",
                    label_msgid="label_volume",
                    description="The volume of a journal, multivolume book work etc. In most cases it should suffice to use a simple number as the volume identifier.",
                    description_msgid="help_volume",
                    i18n_domain="cmfbibliographyat",),
                )

numberField = StringField('number',
                searchable=1,
                required=0,
                default='',
                is_duplicates_criterion=True,
                widget=StringWidget(label="Number",
                    label_msgid="label_number",
                    description="The number of a journal, proceedings, technical report etc. Issues of journals, proceedings etc. are usually identified by volume and number; however, issues of the same volume will often be numbered preceedingly which often makes the specification of a number optional. With technical reports, the issuing organization usually also gives it a number.",
                    description_msgid="help_number",
                    i18n_domain="cmfbibliographyat",),
                )

pagesField = StringField('pages',
                searchable=1,
                required=0,
                default='',
                is_duplicates_criterion=True,
                widget=StringWidget(label="Pages",
                    label_msgid="label_pages",
                    description="A page number or range of numbers such as '42-111'; you may also have several of these, separating them with commas: '7,41,73-97'.",
                    description_msgid="help_pages",
                    i18n_domain="cmfbibliographyat",),
                )

howpublishedField = StringField('howpublished',
                searchable=1,
                required=0,
                default='',
                is_duplicates_criterion=True,
                widget=StringWidget(label="How published",
                    label_msgid="label_howpublished",
                    description="For publications without a publisher. e.g., an 'Institute Report'.",
                        description_msgid="help_howpublished",
                        i18n_domain="cmfbibliographyat",),
                )

publisherField = StringField('publisher',
                searchable=1,
                required=0,
                default='',
                is_duplicates_criterion=True,
                widget=StringWidget(label="Publisher",
                    label_msgid="label_publisher",
                    description="The publisher's name.",
                    description_msgid="help_publisher",
                    size=60,
                    i18n_domain="cmfbibliographyat",),
                )

addressField = StringField('address',
                searchable=1,
                required=0,
                default='',
                is_duplicates_criterion=True,
                widget=StringWidget(label="Address",
                    label_msgid="label_address",
                    description="Publisher's address. For major publishing houses, just the city is given. For small publishers, you can help the reader by giving the complete address.",
                    description_msgid="help_address",
                    size=60,
                    i18n_domain="cmfbibliographyat",),
                )

editionField = StringField('edition',
                searchable=1,
                required=0,
                default='',
                is_duplicates_criterion=True,
                widget=StringWidget(label="Edition",
                    label_msgid="label_edition",
                    description="The edition of a book - for example: 'II', '2' or 'second', depending on your preference. Numbers will be turned into ordinal numerals.",
                    description_msgid="help_edition",
                    size=60,
                    i18n_domain="cmfbibliographyat",),
                )

booktitleField = StringField('booktitle',
                searchable=1,
                required=0,
                default='',
                is_duplicates_criterion=True,
                widget=StringWidget(label="Book Title",
                       label_msgid="label_booktitle",
                       description="Title of the book, collection or proceedings, that the cited resource is part of.",
                       description_msgid="help_booktitle",
                       i18n_domain="cmfbibliographyat",),
                )

editorField = StringField('editor',
                searchable=1,
                required=0,
                default='',
                is_duplicates_criterion=True,
                widget=StringWidget(label="Editor",
                    label_msgid="label_editor",
                    description="Name(s) of editor(s). Opposed to the 'author' field, the 'editor' field should contain the editor of the book, collection or proceeding that the reference appears in.",
                    description_msgid="help_editor",
                    i18n_domain="cmfbibliographyat",),
                )

seriesField = StringField('series',
                searchable=1,
                required=0,
                default='',
                is_duplicates_criterion=True,
                widget=StringWidget(label="Series",
                    label_msgid="label_series",
                    description="The name of a series or set of books. When citing an entire book, the 'title' field gives its title and this optional 'series' field gives the name of a series in which the book is published.",
                    description_msgid="help_series",
                    i18n_domain="cmfbibliographyat",),
                )

chapterField = StringField('chapter',
                searchable=0,
                required=0,
                default='',
                is_duplicates_criterion=True,
                widget=StringWidget(label="Chapter",
                    label_msgid="label_chapter",
                    description="A chapter number.",
                    description_msgid="help_chapter",
                    i18n_domain="cmfbibliographyat",),
                )

organizationField = StringField('organization',
                searchable=1,
                required=0,
                default='',
                is_duplicates_criterion=True,
                widget=StringWidget(label="Organization",
                    label_msgid="label_organization",
                    description="The organization sponsoring a conference, issuing a technical report etc.",
                    description_msgid="help_organization",
                    i18n_domain="cmfbibliographyat",),
                )

schoolField = StringField('school',
                required=0,
                searchable=1,
                default='',
                is_duplicates_criterion=True,
                widget=StringWidget(label="School",
                    label_msgid="label_school",
                    description="The name of the school (college, university etc.) where a thesis was written.",
                    description_msgid="help_school",
                    i18n_domain="cmfbibliographyat",),
                )

institutionField = StringField('institution',
                required=0,
                searchable=1,
                default='',
                is_duplicates_criterion=True,
                widget=StringWidget(label="Institution",
                    label_msgid="label_institution",
                    description="The institution that published the work.",
                    description_msgid="help_institution",
                    i18n_domain="cmfbibliographyat",),
                )

typeField = StringField('publication_type',
                required=0,
                searchable=1,
                default='',
                is_duplicates_criterion=True,
                widget=StringWidget(label="Type",
                    label_msgid="label_publication_type",
                    description="The type of a technical report, PhD thesis etc. - for example, 'Research Note' or 'Doktorarbeit'.",
                    description_msgid="help_publication_type",
                    i18n_domain="cmfbibliographyat",),
                )

editor_flagField = BooleanField('editor_flag',
                default=0,
                required=0,
                is_duplicates_criterion=True,
                widget=BooleanWidget(label="Editor Flag",
                    label_msgid="label_editor_flag",
                    description="Check here if the author(s) specified above are actually the editor(s) of the book.",
                    description_msgid="help_editor_flag",
                    i18n_domain="cmfbibliographyat",)
                )

isbnField = StringField('isbn',
                searchable=1,
                default='',
                accessor='getIsbnOld',
                is_duplicates_criterion=True,
                widget=StringWidget(
                    label="ISBN Number",
                    label_msgid="label_isbn",
                    description="The ISBN number of this publication.",
                    description_msgid="help_isbn",
                    visible={'edit': 'invisible', 'view': 'invisible',}, # invisible because of the 'identifiers' field
                    i18n_domain="cmfbibliographyat",)
                )
