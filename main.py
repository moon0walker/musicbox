import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GdkX11
from gi.repository import GObject, Gdk
import preferences, frame, css
from tools import hotkeys, player, equalizer, settings, vlc, media
import os, time
import alsaaudio


GObject.threads_init()
Gdk.threads_init()

__g_mixer__ = alsaaudio.Mixer('Master')

class MainWindow(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, title='musicbox', name='MainWindow', border_width=10)
		self.stopped = False
		self.settings = settings.SettingsManager("/home/user/musicbox/settings.ini")

		self.mainoverlay = Gtk.Overlay()

		self.mainframe = Gtk.Frame(vexpand=True, valign=Gtk.Align.FILL)
		self.maingrid = Gtk.Grid()
		self.maingrid.set_row_spacing(10)

		self.frame_infobar = frame.infobar
		self.frame_songbar = frame.songbar
		self.frame_banner = frame.banner
		self.frame_player = Gtk.Frame(name='FramePlayerHide')
		self.player = player.MediaPlayerWidget(self.on_end_track_player, self.frame_player)

		self.maingrid.attach(self.frame_infobar, 0, 0, 1, 1)
		self.maingrid.attach_next_to(self.frame_songbar, self.frame_infobar, Gtk.PositionType.BOTTOM, 1, 10)
		self.maingrid.attach_next_to(self.frame_banner, self.frame_songbar, Gtk.PositionType.BOTTOM, 1, 2)
		self.maingrid.attach_next_to(self.player, self.frame_banner, Gtk.PositionType.RIGHT, 1, 1)
		self.mainframe.add(self.maingrid)

		self.mainoverlay.add_overlay(self.mainframe)
		self.mainoverlay.add_overlay(self.frame_player)
		self.add(self.mainoverlay)
		self.fullscreen()

		self.microphone = equalizer.Microphone()
		self.microphone.start()
		self.demo_player = player.DemoPlayer(self.on_end_track_demo)
		self.key_manager = hotkeys.HotkeyManager(self)

		self.init_signals()
		self.init_settings()
		self.frame_infobar.set_demo_player_track(self.demo_player.get_current_track())
		css.add_css(self, '/home/user/musicbox/css/musicbox.css')

	def init_signals(self):
		self.hotkeys = {
				'a':self.frame_songbar.on_artist_move_up,
				'z':self.frame_songbar.on_artist_move_down,
				'd':self.frame_songbar.on_song_move_up,
				'c':self.frame_songbar.on_song_move_down,
				's':self.add_credit,
				'x':self.make_order,
				'q':self.player.p.volume_up,
				'e':self.player.p.volume_down,
				'v':self.preferences_start,
		}
		self.key_manager.register_hotkeys(self.hotkeys)
		self.frame_songbar.ordered = self.frame_infobar.ordered

	def init_settings(self):
		self.set_cost( self.settings.get_option('preferences/order') )
		self.set_karaoke_cost( self.settings.get_option('preferences/karaoke_order') )
		self.set_cost_currency( self.settings.get_option('preferences/currency') )
		
		# self.set_mediaplayer_volume()
		# self.set_demoplayer_volume( self.settings.get_option('preferences/volumediff') )
		self.set_player_volume( self.settings.get_option('preferences/volumediff') )
		
		self.set_demo_folder( self.settings.get_option('preferences/demo_folders') )
		self.set_theme( self.settings.get_option('preferences/theme') )

		if self.settings.get_option('preferences/banner') != '':
			self.set_banner_image( '/home/user/musicbox/data/banner/' + self.settings.get_option('preferences/banner') )
		self.set_media_path( self.settings.get_option('preferences/media_path') )

		self.set_first_start( self.settings.get_option('statistic/first_start') )
		self.set_credit( self.settings.get_option('statistic/credit') )
		# self.set_bands([int(float(self.settings.get_option('equalizer/band%d'%x))) for x in range(10)])

	def preferences_start(self):
		preferences.main(self)

	def set_cost(self, value):
		self.frame_songbar.set_cost_value(value)

	def set_karaoke_cost(self, value):
		self.frame_songbar.set_karaoke_cost(value)

	def set_cost_currency(self, value):
		self.frame_songbar.set_cost_currency(value)

	def set_demo_folder(self, demo_folder):
		self.demo_player.set_demo_folder(demo_folder)
		if not self.player.p.is_playing():
			self.demo_player.play()
			self.frame_infobar.set_demo_player_track(self.demo_player.get_current_track())

	def set_theme(self, color):
		self.mainframe.set_name('MainFrame_'+color)

	def set_player_volume(self, diff):
		volume = 50
		try:	volume = __g_mixer__.getvolume()[0]
		except:	pass
		__g_mixer__.setvolume(volume)
		if self.player.p.is_playing():
			self.player.p.set_volume(volume)
			self.demo_player.set_volume(volume-int(diff))
			self.player.p.set_volume_low()
		else:
			self.player.p.set_volume(volume+int(diff))
			self.demo_player.set_volume(self.player.p.volume-int(diff))
			self.demo_player.set_volume_low()

	def set_banner_image(self, img_path):
		self.frame_banner.set_image(img_path)

	def set_media_path(self, media_path):
		self.frame_songbar.set_media_path(media_path)

	def set_first_start(self, is_first):
		if not is_first:
			self.settings.set_option('statistic/first_start', True, True)
			self.settings.set_option('statistic/start_date', time.strftime('%Y.%m.%d'), True)
			self.settings.set_option('statistic/orders', 0, True)

	def set_credit(self, value):
		self.frame_infobar.credit.set_left(value)

	def set_credit_value(self):
		self.settings.set_option('statistic/credit', self.frame_infobar.credit.left, True)

	def set_order_increment(self):
		x = self.settings.get_option('statistic/orders')
		self.settings.set_option('statistic/orders', x+1, True)

	def set_bands(self, values):
		self.player.set_bands(values)

	def add_media_path_list(self):
		print('add_media_path_list')
		self.demo_player.set_demo_folder_on_add()
		if not self.player.p.is_playing():
			self.demo_player.play()

	def remove_media_path_list(self, media_path_list):
		print('remove_media_path', media_path_list)
		for media_path in media_path_list:
			# self.frame_songbar.remove_media_path(media_path)
			self.demo_player.set_demo_folder_on_remove(media_path)

	def refresh_folders(self):
		self.frame_songbar.refresh_folders()

	def add_credit(self):
		self.frame_infobar.credit.set_left(1)
		self.set_credit_value()
		return True

	def make_order(self):
		artist_dir = self.frame_songbar.get_artist_dir()
		song_name = self.frame_songbar.get_active_song()
		cost_value = self.frame_songbar.get_cost_value()
		is_karaoke = self.frame_songbar.is_karaoke()
		full_path = '%s/%s' % (artist_dir, song_name)
		if is_karaoke:
			karaoke_cost = self.frame_songbar.get_karaoke_cost()
			if karaoke_cost >= 1:
				cost_value *= karaoke_cost
			else:
				return
		if self.frame_infobar.make_order(full_path, cost_value) == True:
			self.set_order_increment()
			self.set_credit_value()
			self.frame_songbar.songs.mark_as_ordered()
			self.demo_player.pause()
			self.player.push(full_path)
			self.player.p.play()
			self.player.p.play_audio()
			self.update_file_statistic(artist_dir, song_name, is_karaoke)

	def update_file_statistic(self, artist_dir, song_name, is_karaoke):
		media.update_file_statistic(artist_dir, song_name, is_karaoke)

	def on_end_track_player(self):
		# print('on_end_track_player')
		track_ended = self.frame_infobar.on_end_track()
		self.frame_songbar.mark_as_unordered(track_ended)

		if not self.frame_infobar.ordered.order_list:
			self.player.p.reload()
			self.frame_infobar.set_demo_player_track(self.demo_player.get_current_track())
			self.demo_player.play()

	def on_end_track_demo(self):
		self.frame_infobar.set_demo_player_track(self.demo_player.get_current_track())

	def stop_all(self):
		self.stopped = True
		self.microphone.stop()
		self.player.p.stop()
		self.demo_player.stop()
		self.frame_songbar.ml.library.clear()
		preferences.destroy()
		self.destroy()

	def _destroy(self, window, event):
		self.stopped = True
		self.microphone.stop()
		Gtk.main_quit()


if __name__ == '__main__':
	win = MainWindow()
	win.connect("delete-event", win._destroy)
	win.show_all()
	win.frame_songbar.on_artist_move_up()
	win.frame_songbar.on_artist_move_down()
	win.set_size_request(1024, 768)
	win.player.p.set_xid(win.get_window().get_xid())

	Gtk.main()
