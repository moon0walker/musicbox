import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio


class HotkeyManager(object):
	def __init__(self, window):
		self.accel_group = Gtk.AccelGroup()
		window.add_accel_group(self.accel_group)
		self.hotkeys = None

	def register_hotkeys(self, hotkeys):
		self.hotkeys = hotkeys
		for key in self.hotkeys:
			self.register(key)

	def register(self, accelerator):
		key, mod_type = Gtk.accelerator_parse(accelerator)
		self.accel_group.connect(key, mod_type, Gtk.AccelFlags.VISIBLE, self.process_key)

	def process_key(self, accel_group, widget, key, mod_type):
		self.hotkeys[chr(key).lower()]()
		return True
