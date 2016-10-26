import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GdkPixbuf

from os.path import exists


MG = (1024, 768)

class Banner(Gtk.Frame):
	def __init__(self, mon_width, mon_height):
		Gtk.Frame.__init__(self)
		global MG
		MG = (mon_width, mon_height)
		self.set_vexpand(True)
		self.set_hexpand(True)
		self.set_name('BannerBar')
		self.label_text = 'MusicBox'

		self.banner_box = Gtk.HBox()
		self.overlay = Gtk.Overlay()

		self.image = Gtk.Image()
		self.label = Gtk.Label(label=self.label_text)
		self.overlay.add_overlay(self.image)
		self.overlay.add_overlay(self.label)

		self.banner_box.add(self.overlay)
		self.add(self.banner_box)

	def set_image(self, img_path):
		if exists(img_path):
			self.label.set_text('')
			if img_path[-4:] == '.gif':
				try:
					pixbuf = GdkPixbuf.PixbufAnimation.new_from_file(img_path)
					self.image.set_from_animation(pixbuf)
				except:
					self.label.set_text(self.label_text)
			else:
				pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(img_path, 970, 93, False)
				self.image.set_from_pixbuf(pixbuf)
		else:
			self.image.clear()
			self.label.set_text(self.label_text)
