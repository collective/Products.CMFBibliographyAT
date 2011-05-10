from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class Formatter(BrowserView):
    
    template = ViewPageTemplateFile('listitemformatter.pt')

    def __call__(self, item=None):
        self.item = item
        return self.template()