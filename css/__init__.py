from gi.repository import Gtk, Gio
import os

base_path = os.path.abspath(os.path.dirname(__file__))
resource_path = os.path.join(base_path, '/home/user/musicbox/css/gio.gresource')
resource = Gio.Resource.load(resource_path)
resource._register()

def add_css(widget, css):
	style_provider = Gtk.CssProvider()
	# print(css)
	giobytes = Gio.resources_lookup_data(css, 0)
	style_provider.load_from_data(giobytes.get_data())
	def apply_css(widget, style_provider):
		Gtk.StyleContext.add_provider(widget.get_style_context(),
									  style_provider,
									  Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		if isinstance(widget, Gtk.Container):
			widget.forall(apply_css, style_provider)
	apply_css(widget, style_provider)


	
