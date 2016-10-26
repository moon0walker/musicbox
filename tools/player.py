import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkX11, GObject
import time, os, os.path, ctypes, subprocess
from . import vlc
import alsaaudio


__g_audio_ext__ = ['.mp3', '.wav', 'midi', '.mid']
__g_video_ext__ = ['.avi', '.mp4', '.flv', '.3gp', '.mkv']
__g_mixer__ = alsaaudio.Mixer('Master')

def is_karafun(full_path):
	if os.path.exists(full_path) and os.path.isfile(full_path) and len(full_path) > 4 and full_path[-4:] == '.mp3':
		karafun_path = full_path[:-4] + '.cdg'
		if os.path.exists(karafun_path) and os.path.isfile(karafun_path):
			return True
	return False


class MediaPlayer(object):
	def __init__(self, cb_end, frame_player=None):
		self.frame_player = frame_player
		self.cb_end = cb_end
		self.instance = vlc.Instance()
		self.event_manager = None
		self.xid = None
		self.tracks = []
		self.idx = 0
		self.count = 0
		self.volume = 100
		
		self.player = self.instance.media_player_new()
		self.media_list = self.instance.media_list_new()
		self.media_list_player = self.instance.media_list_player_new()
		self.media_list_player.set_media_list(self.media_list)
		self.media_list_player.set_media_player(self.player)
		# self.media_list_player.set_playback_mode(vlc.PlaybackMode.loop)

		self.event_manager = self.player.event_manager()
		try:	self.volume = __g_mixer__.getvolume()[0]
		except:	pass

	def init_player(self):
		# self.event_manager.event_detach(vlc.EventType.MediaPlayerEndReached)
		# self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.on_end_track)
		self.set_volume_low()

	def add(self, media_path):
		if os.path.exists(media_path):
			self.tracks.append(media_path)
			media = self.instance.media_new(media_path)
			self.media_list.lock()
			self.media_list.add_media(media)
			if media_path[-4:].lower() in __g_video_ext__ or is_karafun(media_path):
				media_path_fake = '/home/user/musicbox/data/fake.mp3'
				media_fake = self.instance.media_new(media_path_fake)
				self.media_list.add_media(media_fake)
				self.tracks.append(media_path_fake)
			self.media_list.unlock()
			self.count = len(self.tracks)

	def reload(self):
		self.tracks = []
		self.count = 0
		self.idx = 0

	def get_count(self):
		return self.count

	def play(self):
		if self.is_playing() != True and self.idx < len(self.tracks):
			track = self.tracks[self.idx]
			if os.path.exists(track):
				self.init_player()
				if track[-4:].lower() in __g_video_ext__ or is_karafun(track):
					self.xinit()
				# self.play_audio()
				return True
			else:
				self.tracks.remove(track)
				self.cb_end()
		return False

	def print(self):
		for i in range(10):
			it = self.media_list.item_at_index(i)
			if it:
				print('%d' % i, 'item =', it.get_mrl())

	def play_audio(self):
		if self.media_list_player.is_playing() != True:
			self.set_volume_low()
			self.media_list_player.play()

	def pause(self):
		if self.media_list_player.is_playing() == True:
			self.media_list_player.pause()

	def stop(self):
		self.media_list_player.stop()

	def is_playing(self):
		return self.media_list_player.is_playing()

	def volume_up(self):
		self.volume_grow(5)
		return True

	def volume_down(self):
		self.volume_grow(-5)
		return True

	def volume_grow(self, diff):
		volume_new = self.volume + diff
		if volume_new >= 0 and volume_new <= 100:
			self.set_volume(volume_new)

	def set_volume(self, volume):
		if volume > 100: volume = 100
		elif volume < 0: volume = 0
		self.volume = volume

	def set_volume_low(self):
		# print('set_volume_low =', self.volume)
		channel = alsaaudio.MIXER_CHANNEL_ALL
		__g_mixer__.setvolume(self.volume, channel)

	def xinit(self):
		self.player.set_fullscreen(True)
		if self.xid:
			self.player.set_xwindow(self.xid)
		if self.frame_player:
			self.frame_player.set_name('FramePlayerShow')

	def set_xid(self, xid):
		self.xid = xid


class MediaPlayerWidget(Gtk.DrawingArea):
	def __init__(self, cb_end, frame_player):
		Gtk.DrawingArea.__init__(self, hexpand=False, vexpand=False)
		self.xid = None
		self.p = MediaPlayer(cb_end, frame_player)
		self.p.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.on_end_track)

	def on_end_track(self, event, is_karaoke=False):
		# print('player on_end_track')
		track = None
		if self.p.idx < len(self.p.tracks):
			track = self.p.tracks[self.p.idx]
			# print('ENDED: ', track)
			self.p.idx += 1

		if self.p.idx >= len(self.p.tracks):
			self.p.media_list.lock()
			while True:
				if self.p.media_list.remove_index(0) == -1:
					break
			self.p.media_list.unlock()

		if self.p.frame_player.get_name() == 'FramePlayerShow':
			self.p.frame_player.set_name('FramePlayerHide')
		if track != '/home/user/musicbox/data/fake.mp3':
			self.p.cb_end()
		self.p.play()

	def push(self, media_path):
		self.p.add(media_path)

	def get_count(self):
		return self.p.count


class DemoPlayer(MediaPlayer):
	def __init__(self, cb_end):
		self.demo_folder = ''
		self.volume = 20
		MediaPlayer.__init__(self, cb_end)
		self.init_player()

	def init_player(self):
		if self.demo_folder != 'disable':
			self.player = self.instance.media_player_new()
			self.event_manager = self.player.event_manager()
			self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.on_end_track)
			self.media_list = self.instance.media_list_new()
			self.media_list_player = self.instance.media_list_player_new()
			self.media_list_player.set_media_list(self.media_list)
			self.media_list_player.set_media_player(self.player)
			self.media_list_player.set_playback_mode(vlc.PlaybackMode.loop)
			# self.set_volume_low()

	def push(self):
		self.media_list.lock()
		for x in self.tracks:
			media = self.instance.media_new(x)
			self.media_list.add_media(media)
		self.media_list.unlock()

	def play(self):
		if self.media_list_player.is_playing() != True and self.demo_folder.lower() != 'disable':
			self.set_volume_low()
			self.media_list_player.play()

	def pause(self):
		if self.media_list_player.is_playing() == True:
			self.media_list_player.pause()

	def stop(self):
		self.media_list_player.stop()
		self.player.stop()

	def is_playing(self):
		return self.media_list_player.is_playing()

	def on_end_track(self, event):
		# print('demo on_end_track')
		self.idx += 1
		if self.idx == len(self.tracks):
			self.idx = 0
		self.cb_end()

	def ls_folder(self):
		try:
			# print('ls_folder demo', self.demo_folder)
			if os.path.exists(self.demo_folder) and os.path.isdir(self.demo_folder):
				for name in os.listdir(self.demo_folder):
					try:
						full_path = '%s/%s' % (self.demo_folder, name)
						if os.path.isfile(full_path):
							if full_path[-4:].lower() in __g_audio_ext__ and not is_karafun(full_path):
								self.tracks.append(full_path)
						else:
							tmp_path = self.demo_folder
							self.demo_folder = full_path
							self.ls_folder()
							self.demo_folder = tmp_path
					except:
						pass
		except:
			pass
		self.count = len(self.tracks)

	def reload_media_list(self):
		self.stop()
		self.reload()
		self.init_player()
		self.ls_folder()
		self.push()

	def set_demo_folder(self, demo_folder):
		if self.demo_folder == '/home/user/Music' and demo_folder == 'all_library':
			return
		if self.demo_folder != demo_folder:
			self.demo_folder = demo_folder
			if demo_folder == 'all_library':
				self.demo_folder = '/home/user/Music'
			self.reload_media_list()

	def set_demo_folder_on_add(self, media_path=None):
		if self.demo_folder in ['/home/user/Music']:
			self.reload_media_list()

	def set_demo_folder_on_remove(self, media_path):
		is_played = self.is_playing()
		# print('set_demo_folder_on_remove', media_path, self.demo_folder)
		if self.demo_folder in [media_path, '/home/user/Music']:
			self.reload_media_list()
			if is_played:
				self.play()

	def get_current_track(self):
		if self.demo_folder.lower() != 'disable' and self.tracks:
			if self.idx >= len(self.tracks):
				self.idx = 0
			if os.path.exists(self.tracks[self.idx]):
				return self.tracks[self.idx]
		return None
