import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GObject


class Main(Gtk.Grid):
	def __init__(self):
		Gtk.Grid.__init__(self)
		self.set_row_spacing(20)
