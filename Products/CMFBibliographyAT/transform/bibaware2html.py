import pkg_resources

dist = pkg_resources.get_distribution('Plone')
if dist.version.startswith('3'):
    import bibaware2html_plone3
    from bibaware2html_plone3 import HTMLToBibaware, register, initialize
else:
    import bibaware2html_plone4
    from bibaware2html_plone4 import HTMLToBibaware, register, initialize
