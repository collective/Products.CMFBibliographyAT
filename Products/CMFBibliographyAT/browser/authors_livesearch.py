from Products.Five.browser import BrowserView

class AuthorListView(BrowserView):

    data = """hauser
natea
mateola
jchamm
ree
ree_
martior
dcnoye
jonstahl
SteveM
grahamperrin
ErikRose
heureso
cbcunc
enzo
esteele
geojeff
wildintellect
Gogo
aclark
zenwryly
SnarfBot
siebo
siebo_
DigitalD
place
plate
plural
plone
apostle
april
apple"""

    def __call__(self):
        return self.data
        