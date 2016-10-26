#!/bin/bash
# cd ..
# xgettext --language=Python --keyword=_ --from-code=utf-8 --output=strings.pot preferences.py widgets/*.py frame/*.py
# mv strings.pot locale/strings.pot
# cd locale

# msginit --locale=en_US --input=strings.pot
# msginit --locale=ru --input=strings.pot
# msginit --locale=uk --input=strings.pot
# msginit --locale=pl --input=strings.pot

msgfmt en_US.po -o en_US/LC_MESSAGES/musicbox.mo
msgfmt ru.po -o ru/LC_MESSAGES/musicbox.mo
msgfmt uk.po -o uk/LC_MESSAGES/musicbox.mo
msgfmt pl.po -o pl/LC_MESSAGES/musicbox.mo
