import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkX11
from gi.repository import GObject, Gdk

import frame.main, frame.infobar, frame.songbar, frame.banner


__all__ = ['main', 'infobar', 'songbar', 'banner']

screen = Gtk.Window.get_screen(Gtk.Window())
width = screen.get_width()
height = screen.get_height()

main = frame.main.Main()
infobar = frame.infobar.InfoBar(width, height)
songbar = frame.songbar.SongBar(width, height)
banner = frame.banner.Banner(width, height)
