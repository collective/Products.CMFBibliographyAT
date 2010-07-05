import pkg_resources

dist = pkg_resources.get_distribution('Plone')
if dist.version.startswith('3'):
    import html2bibaware_plone3
    from html2bibaware_plone3 import HTMLToBibaware, register, initialize
else:
    import html2bibaware_plone4
    from html2bibaware_plone4 import HTMLToBibaware, register, initialize
