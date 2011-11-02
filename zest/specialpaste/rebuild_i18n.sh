#!/bin/sh
# Run this script to update the translations.
i18ndude rebuild-pot --pot locales/zest.specialpaste.pot --create zest.specialpaste .
i18ndude rebuild-pot --pot locales/zest.specialpaste.pot --merge locales/manual.pot --create zest.specialpaste .

i18ndude sync --pot locales/zest.specialpaste.pot $(find . -name 'zest.specialpaste.po')
