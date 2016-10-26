from gi.repository import Gtk
# from settings import SettingsManager
import css
import widgets
from tools.lang import _

class PreferenceWindow(Gtk.Window):
	(COLUMN_NAME, COLUMN_VALUE) = range(2)

	def __init__(self, mainwindow=None):
		Gtk.Window.__init__(self)

		self.mainwindow = mainwindow
		self.settings = mainwindow.settings

		# Config Main Window
		self.config_main_window()

		# Main Frame
		self.main_frame = main_frame = Gtk.Frame()
		main_frame.set_name('PrefrerenceFrame_' + self.settings.get_option('preferences/theme'))
		self.add(main_frame)

		# Main VBox
		self.main_vbox = main_vbox = Gtk.VBox(homogeneous=False, spacing=5)
		main_frame.add(main_vbox)
		
		# Top Label
		self.label_frame = label_frame = Gtk.Frame()
		label_frame.set_name('LabelFrame_' + self.settings.get_option('preferences/theme'))
		main_vbox.pack_start(label_frame, False, True, 5)
		# main_vbox.add(label_frame)

		self.label = label = Gtk.Label(label='')
		label_frame.add(label)

		# Main HBox with tables
		self.main_hbox = main_hbox = Gtk.HBox(homogeneous=False, spacing=20)
		main_vbox.pack_start(main_hbox, True, True, 5)
		# main_vbox.add(main_hbox)

		widgets.create_frames(self, self.settings)

		# List with settings
		self.ControlPanelFrame = widgets.widgets.ControlPanelFrame
		main_hbox.add(self.ControlPanelFrame)
		# main_hbox.pack_start(self.ControlPanelFrame, True, True, 20)

		# List with values
		self.ValuesFrame = widgets.widgets.ValuesFrame
		main_hbox.add(self.ValuesFrame)
		# main_hbox.pack_start(self.ValuesFrame, True, True, 20)

		# Statistic vbox
		stat_vbox = Gtk.HBox(homogeneous=False, spacing=3)
		stat_vbox.set_name('StatVBox')
		self.stat_label11 = Gtk.Label(label=_('All orders:'))
		self.stat_label11.set_halign(1)
		# stat_vbox.pack_start(self.stat_label1, False, True, 5)
		self.stat_label12 = Gtk.Label(label=_('Date started:'))
		self.stat_label12.set_halign(1)
		# stat_vbox.pack_start(self.stat_label2, False, True, 5)
		stat_hbox1 = Gtk.VBox(homogeneous=False, spacing=3)
		stat_hbox1.pack_start(self.stat_label11, False, True, 0)
		stat_hbox1.pack_start(self.stat_label12, False, True, 0)
		stat_vbox.pack_start(stat_hbox1, False, True, 0)

		stat_hbox2 = Gtk.VBox(homogeneous=False, spacing=3)
		stat_alignment1 = Gtk.Alignment(xalign=0, yalign=0.5, xscale=0.5, yscale=0.5)
		stat_alignment1.set_padding(0,0,0,0)
		stat_hbox2.pack_start(stat_alignment1, True, True, 0)
		stat_alignment2 = Gtk.Alignment(xalign=0, yalign=0.5, xscale=0.5, yscale=0.5)
		stat_alignment2.set_padding(0,0,0,0)	
		stat_hbox2.pack_start(stat_alignment2, True, True, 0)
		self.stat_label21 = Gtk.Label(label=str(self.settings.get_option('statistic/orders')))
		self.stat_label22 = Gtk.Label(label=self.settings.get_option('statistic/start_date'))
		stat_alignment1.add(self.stat_label21)
		stat_alignment2.add(self.stat_label22)
		stat_vbox.pack_start(stat_hbox2, False, True, 3)

		main_vbox.pack_start(stat_vbox, False, True, 3)

		self.setup_hotkeys()

		css.add_css(self, '/home/user/musicbox/css/preferences.css')
		self.show_all()

	def setup_hotkeys(self):
		hotkeys = (
			('A', self.ControlPanelFrame._on_settings_list_up),
			('Z', self.ControlPanelFrame._on_settings_list_down),
			('D', self.ValuesFrame._on_settings_value_up),
			('C', self.ValuesFrame._on_settings_value_down),
			('X', self.ValuesFrame._on_save_value),
			('V', self.disable_keys),
			('S', self.disable_keys)
		)
		self.accel_group = Gtk.AccelGroup()
		for key, function in hotkeys:
			key, mod = Gtk.accelerator_parse(key)
			self.accel_group.connect(key, mod, Gtk.AccelFlags.VISIBLE, function)
		self.add_accel_group(self.accel_group)

	def disable_keys(self, *_e):
		return True

	def config_main_window(self):
		self.set_name('PreferenceWindow')
		self.set_title('Settings')
		self.set_border_width(10)
		self.fullscreen()
		# self.connect('destroy', Gtk.main_quit)

	def save_settings(self):
		for labels in self.ControlPanelFrame.treeview_settings.get_model():
			obj = self.ValuesFrame.get_data_obj(widgets.data, labels[0])
			if type(obj) == widgets.widgets.ControlPanelRowNumerical:
				self.settings.set_option('preferences/' + obj.name, labels[1])
			else:
				if obj.name == 'banner':
					if obj.get_value(labels[1]) != None:
						self.settings.set_option('preferences/' + obj.name, '')
					else:
						self.settings.set_option('preferences/' + obj.name, labels[1])
				elif obj.name not in [None, 'theme', 'update', 'equalizer', 'statistics', 'exit', 'media_files']:
					value = obj.get_value(labels[1])
					# print(value)
					if value == None:
						self.settings.set_option('preferences/' + obj.name, labels[1])
					elif value == '':
						self.settings.set_option('preferences/' + obj.name, '')
					else: 
						self.settings.set_option('preferences/' + obj.name, value)

		self.settings.save()

		# Set to mainwindow
		self.mainwindow.set_cost( self.settings.get_option('preferences/order') )
		self.mainwindow.set_karaoke_cost( self.settings.get_option('preferences/karaoke_order') )
		self.mainwindow.set_cost_currency( self.settings.get_option('preferences/currency') )
		if self.settings.get_option('preferences/banner') != '':
			self.mainwindow.set_banner_image( '/home/user/musicbox/data/banner/' + self.settings.get_option('preferences/banner') )
		else:
			self.mainwindow.set_banner_image( '' )
		self.mainwindow.set_media_path( self.settings.get_option('preferences/media_path') )

	def refresh_folders(self):
		if self.settings.get_option('preferences/changed') == True:
			self.mainwindow.refresh_folders()
			self.settings.set_option('preferences/changed', False, save=True)

	def quit(self, save=False):
		if save:
			self.save_settings()
		self.mainwindow.set_player_volume( self.settings.get_option('preferences/volumediff') )
		self.mainwindow.set_demo_folder( self.settings.get_option('preferences/demo_folders') )
		self.refresh_folders()
		self.destroy()
		
win_pref = None
def main(window=None):
	win_pref = PreferenceWindow(window)
	win_pref.set_size_request(1024, 768)
	# Gtk.main()

def destroy():
	if win_pref != None:
		win_pref.destroy()

if __name__ == '__main__':
	main()
