import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import os, subprocess
import css
from . import hotkeys
import alsaaudio
import collections
import multiprocessing


class Scale(Gtk.VBox):
	def __init__(self, limit_min=0, limit_max=100, val='', mutable=True):
		Gtk.VBox.__init__(self)
		# self.set_hexpand(True)
		# self.set_vexpand(True)

		diff = 100
		mid = 50
		init_values = (mid, limit_min, limit_max, 1, 1, 1)
		self.mutable = mutable

		self.scale = Gtk.VScale()
		self.scale.set_digits(0)

		self.scale.set_inverted(True)
		# self.scale.add_mark(0, Gtk.PositionType.LEFT, mark)
		self.scale.set_size_request(42, 450)
		self.adj = Gtk.Adjustment(*init_values)
		self.scale.set_adjustment(self.adj)
		# self.label_text = '{0} {1}'.format(val, herz_marker)
		self.mixer_name = val
		self.val = val
		if len(self.val) > 3:
			self.val = self.val[:3]

		self.label_text = self.val+'\n[   ]' if self.mutable else self.val+'\n[ X ]'
		# if val == 'Volume':
		# 	self.label_text = self.val+'\nPlayer'

		self.label = Gtk.Label(label=self.label_text, justify=Gtk.Justification.CENTER)
		self.pack_start(self.scale, True, True, 3)
		self.pack_start(self.label, False, True, 3)

	def grow_up(self):
		value_new = self.adj.get_value() + self.adj.get_step_increment()
		self.adj.set_value(value_new)

	def grow_down(self):
		value_new = self.adj.get_value() - self.adj.get_step_increment()
		self.adj.set_value(value_new)

	def get_value(self):
		return self.adj.get_value()

	def set_value(self, value):
		return self.adj.set_value(value)


class Microphone(object):
	def __init__(self):
		self.module_id = 0

	def start(self):
		os.system("pactl unload-module $(pactl list short modules | awk '$2 ==\"module-loopback\" { print $1 }' - )")
		ret = subprocess.check_output(['pactl', 'load-module', 'module-loopback', 'latency_msec=1'])
		self.module_id = int(ret.decode('utf-8').strip('\n'))
		# alsaaudio.Mixer( 'Capture', cardindex=0 ).setvolume(50, alsaaudio.MIXER_CHANNEL_ALL)
		# print('self.module_id =', self.module_id)

	def stop(self):
		# os.system("pactl unload-module $(pactl list short modules | awk '$2 ==\"module-loopback\" { print $1 }' - )")
		os.system('pactl unload-module %d' % self.module_id)
		self.module_id = 0


class Equalizer(Gtk.Window):
	def __init__(self, settings, media_player, demo_player):
		Gtk.Window.__init__(self, title='Equalizer')
		self.set_decorated(False)

		self.settings = settings
		self.player = media_player
		self.demo_player = demo_player

		self.set_name('Equalizer')
		self.set_size_request(500, 500)
		self.set_modal(True)
		self.set_position(Gtk.WindowPosition.CENTER)
		self.screen = self.get_screen()
		self.visual = self.screen.get_rgba_visual()
		if self.visual != None and self.screen.is_composited():
			self.set_visual(self.visual)
		self.set_app_paintable(True)
		
		self.mainhbox = Gtk.HBox(homogeneous=False, spacing=3)

		# menu model
		self.model_menu = model_menu = Gtk.ListStore(str)

		renderer = Gtk.CellRendererText()
		renderer.set_alignment(0.5, 0)
		column = Gtk.TreeViewColumn("Name", renderer, text=0)
		column.set_fixed_width(170)
		# column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
		column.set_alignment(0.5)
		
		self.treeview_menu = treeview_menu = Gtk.TreeView()
		treeview_menu.set_name('EqualizerTreeMenu')

		self.menuframe = Gtk.Frame()
		self.menuframe.set_name('EqualizerFrame_' + self.settings.get_option('preferences/theme'))
		self.menuframe.set_size_request(175, 500)
		
		self.alignment_menu = alignment_menu = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0.5, yscale=0.2)

		treeview_menu.set_model(model_menu)
		treeview_menu.set_headers_visible(False)
		treeview_menu.append_column(column)
		
		treeview_menu.set_cursor(Gtk.TreePath(0))
		treeview_menu.grab_focus()
		
		# mixers
		self.mixerframe = Gtk.Frame()
		self.mixerframe.set_name('EqualizerFrame_' + self.settings.get_option('preferences/theme'))

		self.maingrid = Gtk.Grid()
		# self.maingrid.set_column_homogeneous(True)

		self.chain = []
		x = 0 
		self.alsa_mixers = {}
		self.mixers = collections.OrderedDict()
		self.mixers['Volume'] = Scale(0, 101, 'Volume', mutable=True)
		self.alsa_mixers['Volume'] = alsaaudio.Mixer('Master')
		model_menu.append(['Volume',])
		self.maingrid.attach(self.mixers['Volume'], 0, 0, 50, 1)
		self.chain.append(self.mixers['Volume'])
		x+=1
		for mixer in alsaaudio.mixers( cardindex=0 ):
			if mixer not in ['Mix', 'Mix Mono', 'Capture'] and len(alsaaudio.Mixer( mixer, cardindex=0 ).getvolume()) != 0:
				mutable = False if len(alsaaudio.Mixer( mixer, cardindex=0 ).getvolume()) == 0 else True
				self.mixers[mixer] = Scale(0, 101, mixer, mutable)
				self.alsa_mixers[mixer] = alsaaudio.Mixer( mixer, cardindex=0 )
				model_menu.append([mixer,])
				if x == 0:
					self.maingrid.attach(self.mixers[mixer], 0, 0, 50, 1)
				else:
					self.maingrid.attach_next_to(self.mixers[mixer], self.chain[x-1], Gtk.PositionType.RIGHT, 50, 1)
				self.chain.append(self.mixers[mixer])
				x+=1

		mixer = 'Capture'
		self.alsa_mixers[mixer] = alsaaudio.Mixer(mixer)
		self.mixers[mixer] = Scale(0, 101, mixer, False)
		model_menu.append([mixer,])
		self.maingrid.attach_next_to(self.mixers[mixer], self.chain[x-1], Gtk.PositionType.RIGHT, 50, 1)

		model_menu.append(['Exit',])

		self.active_mixer = self.mixers['Volume']
		self.active_mixer_name = 'Volume'

		# print(self.alsa_mixers)
		
		# self.active_mixer = self.mixers['Master']
		# self.active_mixer_name = 'Master'

		self.get_mixers_from_settings(first=True)

		self.hotkeys = {
				'a':self.on_widget_prev,
				'z':self.on_widget_next,
				'c':self.on_down,
				'd':self.on_up,
				'x':self.on_saveNexit,
				'v':self._block_key,
				's':self._block_key
		}

		# add all elements
		self.add(self.mainhbox)
		self.mainhbox.add(self.menuframe)
		self.menuframe.add(alignment_menu)
		self.alignment_menu.add(treeview_menu)
		self.mainhbox.add(self.mixerframe)
		self.mixerframe.add(self.maingrid)

		self.hotkey_manager = hotkeys.HotkeyManager(self)
		self.hotkey_manager.register_hotkeys(self.hotkeys)
		self.set_app_paintable(True)
		self.connect("draw", self.area_draw)
		css.add_css(self, '/home/user/musicbox/css/preferences.css')
		self.show_all()
		self.active_mixer.label.set_markup('<b><u>'+self.active_mixer.label_text+'</u></b>')

	def area_draw(self, widget, cr):
		import cairo
		cr.set_source_rgba(.2, .2, .2, 0)
		cr.set_operator(cairo.OPERATOR_SOURCE)
		cr.paint()
		cr.set_operator(cairo.OPERATOR_OVER)

	def _block_key(self):
		return True

	def get_mixers_from_settings(self, first=False):
		for mixer in self.mixers:
			alsamixer = None
			if mixer == 'Volume':
				alsamixer = alsaaudio.Mixer( 'Master' )
			elif mixer == 'Capture':
				alsamixer = alsaaudio.Mixer( mixer )
			else:
				alsamixer = alsaaudio.Mixer( mixer, cardindex=0 )

			# alsamixer = self.alsa_mixers[mixer]

			if mixer == 'Capture':
				if first:
					self.mixers[mixer].set_value( int(self.settings.get_option( 'equalizer/' + mixer ) ))
					self.mixers[mixer].label_text = self.mixers[mixer].val+'\n[ X ]'
					self.mixers[mixer].label.set_label( self.mixers[mixer].label_text )
					alsamixer.setvolume( int(self.settings.get_option( 'equalizer/' + mixer )), alsaaudio.MIXER_CHANNEL_ALL )
			else:
				try:
					self.mixers[mixer].set_value( alsamixer.getvolume()[0] )
					if alsamixer.getmute()[0] == 1:
						self.mixers[mixer].label_text = self.mixers[mixer].val+'\n[ M ]'
					elif alsamixer.getmute()[0] == 0:
						self.mixers[mixer].label_text = self.mixers[mixer].val+'\n[   ]'
					self.mixers[mixer].label.set_label( self.mixers[mixer].label_text )
				except:
					pass
			
	### X ###
	def on_saveNexit(self):
		selection = self.treeview_menu.get_selection()
		(model, path) = selection.get_selected()
		mixer = model.get_value(path, 0)
		if mixer != 'Exit':
			self.change_mixer_mute( mixer=self.active_mixer )
		else:
			self.settings.set_option( 'equalizer/capture', self.mixers['Capture'].get_value(), True )
			self.destroy()

	def change_mixer_mute(self, mixer):
		alsamixer = None
		if mixer.mixer_name == 'Volume':
			alsamixer = alsaaudio.Mixer( 'Master' )
		elif mixer.mixer_name == 'Capture':
			alsamixer = alsaaudio.Mixer( mixer.mixer_name )
		else:
			alsamixer = alsaaudio.Mixer( mixer.mixer_name, cardindex=0 )

		# alsamixer = self.alsa_mixers[mixer.mixer_name]

		if mixer.mutable:
			try:
				channel = alsaaudio.MIXER_CHANNEL_ALL
				if alsamixer.getmute()[0] == 1:
					alsamixer.setmute(0, channel)
					# self.mixers[mixer.mixer_name].label_text = self.mixers[mixer.mixer_name].val+'\n[   ]'
				elif alsamixer.getmute()[0] == 0:
					alsamixer.setmute(1, channel)
					# self.mixers[mixer.mixer_name].label_text = self.mixers[mixer.mixer_name].val+'\n[ M ]'
				self.get_mixers_from_settings()
				self.mixers[mixer.mixer_name].label.set_label( self.mixers[mixer.mixer_name].label_text )
				self.active_mixer.label.set_markup('<b><u>'+self.active_mixer.label_text+'</u></b>')
			except alsaaudio.ALSAAudioError:
				pass


	def change_mixer_volume(self, mixer_name, value):
		alsamixer= None
		if mixer_name == 'Volume':
			alsamixer = alsaaudio.Mixer( 'Master' )
		elif mixer_name == 'Capture':
			alsamixer = alsaaudio.Mixer( mixer_name )
		else:
			alsamixer = alsaaudio.Mixer( mixer_name, cardindex=0 )
		
		# alsamixer = self.alsa_mixers[mixer_name]

		try:
			alsamixer.setvolume( value, alsaaudio.MIXER_CHANNEL_ALL )
		except alsaaudio.ALSAAudioError:
			pass

	def on_widget_next(self):
		selection = self.treeview_menu.get_selection()
		(model, path) = selection.get_selected_rows()
		selected_index = path[0].get_indices()[0]
		if selected_index < len(model):
			row = selected_index+1
			self.treeview_menu.row_activated(Gtk.TreePath(row), Gtk.TreeViewColumn(None))
			self.treeview_menu.set_cursor(Gtk.TreePath(row)) 
			(model, path) = selection.get_selected()
			mixer = model.get_value(path, 0)
			if mixer != 'Exit':
				tmp_scale = self.active_mixer
				tmp_scale.label.set_markup(tmp_scale.label_text)
				self.active_mixer = self.mixers[mixer]
				self.active_mixer_name = mixer
				scale = self.active_mixer
				scale.label.set_markup('<b><u>'+scale.label_text+'</u></b>')

	def on_widget_prev(self):
		selection = self.treeview_menu.get_selection()
		(model, path) = selection.get_selected_rows()
		selected_index = path[0].get_indices()[0]
		if selected_index > 0:
			row = selected_index-1
			self.treeview_menu.row_activated(Gtk.TreePath(row), Gtk.TreeViewColumn(None))
			self.treeview_menu.set_cursor(Gtk.TreePath(row)) 
			(model, path) = selection.get_selected()
			mixer = model.get_value(path, 0)
			tmp_scale = self.active_mixer
			tmp_scale.label.set_markup(tmp_scale.label_text)
			self.active_mixer = self.mixers[mixer]
			self.active_mixer_name = mixer
			scale = self.active_mixer
			scale.label.set_markup('<b><u>'+scale.label_text+'</u></b>')

	def on_up(self):
		if self.active_mixer_name not in ['Capture','Volume']:
			if alsaaudio.Mixer( self.active_mixer_name , cardindex=0 ).getvolume()[0] < 0:
				return
		self.active_mixer.grow_up()
		vol = alsaaudio.Mixer( 'Master' ).getvolume()[0]
		self.change_mixer_volume( mixer_name=self.active_mixer_name, value=int(self.active_mixer.get_value()) )
		if alsaaudio.Mixer( 'Master' ).getvolume()[0] != vol:
			if self.active_mixer_name in ['Volume', 'Master', 'PCM']:
				self.get_mixers_from_settings()

	def on_down(self):
		if self.active_mixer_name not in ['Capture','Volume']:
			if alsaaudio.Mixer( self.active_mixer_name , cardindex=0 ).getvolume()[0] < 0:
				return
		self.active_mixer.grow_down()
		vol = alsaaudio.Mixer( 'Master' ).getvolume()[0]
		self.change_mixer_volume( mixer_name=self.active_mixer_name, value=int(self.active_mixer.get_value()) )
		if alsaaudio.Mixer( 'Master' ).getvolume()[0] != vol:
			if self.active_mixer_name in ['Volume', 'Master', 'PCM']:
				self.get_mixers_from_settings()
