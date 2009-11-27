from setuptools import setup, find_packages

version = '0.9.3.1'

setup(name='Products.CMFBibliographyAT',
      version=version,
      description="Bibliographic references in Plone",
      long_description=open("Products/CMFBibliographyAT/README.txt").read(),
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
      url='http://plone.org/products/cmfbibliographyat',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.ATExtensions',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [zope2.initialize]
      Products.CMFBibliographyAT = Products.CMFBibliographyAT:initialize
      """,
      )
