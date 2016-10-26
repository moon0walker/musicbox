#!/usr/bin/python3
import os
import sys
import time
#import subprocess
from tools import settings

if __name__ == '__main__':
	# os.system( 'xrandr --output Virtual1 --primary --mode 1024x768 --pos 0x0 --panning 1024x768' )
	os.system( 'xrandr --output VGA1 --primary --mode 1024x768 --pos 0x0 --panning 1024x768' )

	os.system( 'xset s off' )
	os.system( 'xset -dpms' )
	os.system( 'xset s noblank' )
	os.system( 'xset s noexpose' )
	os.system( 'setterm --blank 0 --powersave off' )

	os.system( 'cp /home/user/musicbox/data/settings.ini.bak /home/user/musicbox/settings.ini' )
	os.system( 'cp -r /home/user/musicbox/data/banner_bak/* /home/user/musicbox/data/banner/*' )
	os.system( 'glib-compile-resources /home/user/musicbox/css/gio.gresource.xml' )

	settings = settings.SettingsManager( "/home/user/musicbox/settings.ini" )
	locale = settings.get_option("preferences/language")
	python = sys.executable

	os.system( 'LANG={0}.utf8 {1} /home/user/musicbox/main.py'.format(locale, python) )
	#time.sleep(1)
