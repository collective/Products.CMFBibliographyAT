import os
from setuptools import setup, find_packages

version = '1.1.0b6'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

desc = read('Products', 'CMFBibliographyAT', 'README.txt')
changes = read('docs', 'CHANGES.txt')
long_desc = desc + '\n\nChanges\n=======\n\n' + changes

setup(name='Products.CMFBibliographyAT',
      version=version,
      description="Bibliographic references in Plone",
      long_description=long_desc,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords=(
          'web application server zope zope2 cmf plone bibliography'),
      author='Raphael Ritz',
      author_email='raphael.ritz@incf.org',
      maintainer='Andreas Jung',
      maintainer_email='info@zopyx.com',
      url='http://plone.org/products/cmfbibliographyat',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'bibliograph.core',
          'bibliograph.parsing',
          'bibliograph.rendering',
          'Products.ATExtensions',
          'pyisbn',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [zope2.initialize]
      Products.CMFBibliographyAT = Products.CMFBibliographyAT:initialize
      """,
      )
