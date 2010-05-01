from AccessControl import ClassSecurityInfo
from ComputedAttribute import ComputedAttribute
from ZPublisher.HTTPRequest import FileUpload
from Products.Archetypes.public import *

simplememberschema = BaseSchema.copy() + Schema((
    StringField('fullname',
                widget = StringWidget(description = "Enter a contact person.")
                ),
    ))

memberschema = BaseSchema.copy() + Schema((
    StringField('memberId',
                widget = StringWidget(description = "Member ID.")
                ),
    StringField('firstname',
                widget = StringWidget(description = "Firstname.")
                ),
    StringField('middlename',
                widget = StringWidget(description = "Middlename.")
                ),
    StringField('lastname',
                widget = StringWidget(description = "Lastname.")
                ),
    StringField('homepage',
                widget = StringWidget(description = "Homepage.")
                ),
    ))

TEXT = 'file data'

class File(FileUpload):
    '''Dummy upload object
       Used to fake uploaded files.
    '''
    __allow_access_to_unprotected_subobjects__ = 1
    filename = 'dummy.txt'
    data = TEXT
    headers = {}

    def __init__(self, filename=None, data=None, headers=None):
        if filename is not None:
            self.filename = filename
            if data is not None:
                self.data = data
            if headers is not None:
                self.headers = headers

    def seek(self, *args): pass
    def tell(self, *args): return 1
    def read(self, *args): return self.data

def getMemberInfo(id):

    return {'fullname': 'Fullname', 'id': 'Member ID', 'homepage': 'home page','email': 'email address'}

class SimpleTestMemberType(BaseContent):
    """A simple test type"""

    id = 'simple_test_member_type'
    schema = simplememberschema
    meta_type = 'Simple Test Member Type'

    security = ClassSecurityInfo()

registerType(SimpleTestMemberType)

class TestMemberType(BaseContent):
    """A test type"""

    id = 'test_member_type'
    schema = memberschema
    meta_type = 'Test Member Type'

    security = ClassSecurityInfo()

    def Authors(self):
        if self.getMiddlename():
            return '%s, %s %s' % (self.getLastname(), self.getFirstname(), self.getMiddlename())
        else:
            return '%s, %s' % (self.getLastname(), self.getFirstname())

    getAuthors = ComputedAttribute('Authors')

registerType(TestMemberType)
