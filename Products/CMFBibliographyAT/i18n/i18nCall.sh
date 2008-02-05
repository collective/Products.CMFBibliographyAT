#!/bin/bash
cd ..
i18ndude rebuild-pot --pot i18n/cmfbibliographyat-generated.pot --create cmfbibliographyat --merge i18n/cmfbibliographyat-manual.pot ./skins
cp i18n/plone-manual.pot i18n/plone-generated.pot
cd i18n