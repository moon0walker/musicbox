
import locale
import gettext

locale.setlocale(locale.LC_ALL, '')
gettext.textdomain('musicbox')
gettext.bindtextdomain('musicbox', '/home/user/musicbox/locale')
_ = gettext.gettext
