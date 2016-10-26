import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GdkPixbuf
from os import listdir
from os.path import exists, isfile, isdir
from collections import OrderedDict
import json, time


pixbuf_folder = GdkPixbuf.Pixbuf.new_from_file_at_scale('/home/user/musicbox/data/folder.png', 24, 16, False)
pixbuf_music = GdkPixbuf.Pixbuf.new_from_file_at_scale('/home/user/musicbox/data/music.png', 24, 24, False)
pixbuf_karaoke = GdkPixbuf.Pixbuf.new_from_file_at_scale('/home/user/musicbox/data/karaoke.png', 24, 24, False)
pixbuf_ordered = GdkPixbuf.Pixbuf.new_from_file_at_scale('/home/user/musicbox/data/order_mark.png', 24, 16, False)

__g_audio_ext__ = ['.mp3', '.wav', 'midi', '.mid']
__g_video_ext__ = ['.avi', '.mp4', '.flv', '.3gp', '.mkv']


def is_karafun(full_path):
	if exists(full_path) and isfile(full_path) and len(full_path) > 4 and full_path[-4:] == '.mp3':
		karafun_path = full_path[:-4] + '.cdg'
		if exists(karafun_path) and isfile(karafun_path):
			return True
	return False


def name_central_making(name):
	chrs = 17
	name_central = name
	if len(name) > chrs*2:
		name_central = '%s\n%s\n%s' % (name[:chrs], name[chrs:chrs*2], name[chrs*2:])
	elif len(name) > chrs and len(name) <= chrs*2:
		name_central = '%s\n%s\n' % (name[:chrs], name[chrs:])
	else:
		name_central = '\n%s\n' % name
	return name_central

def list_store_making(name_raw, idx_raw, pixes):
	name = name_raw.upper()
	if len(name) > 4 and name[-4:].lower() in __g_audio_ext__+__g_video_ext__:
		name = name[:-4]
	name_central = name_central_making(name)
	idx = '%03d' % idx_raw

	list_store = [idx, pixes[0], name, pixes[1], 'tahoma 10']
	list_store_central = [idx, pixes[0], name_central, pixes[1], 'tahoma 10']
	return (list_store, list_store_central)

def update_file_statistic(artist_dir, song_name, is_karaoke):
	ordered_path = '/home/user/musicbox/data/stat_ordered.json'
	if exists(artist_dir) and isdir(artist_dir):
		artist = artist_dir[artist_dir.rfind('/')+1:]
		song = song_name[:song_name.rfind('.')]
		tm = '%04d.%02d' % (time.gmtime().tm_year, time.gmtime().tm_mon)

		ordered = {}
		if exists(ordered_path):
			fd = open(ordered_path, 'r')
			try:	ordered = json.loads(fd.read())
			except:	pass
			fd.close()

		ordered_tm = ordered.get(tm, [])
		if ordered_tm:
			is_exists = False
			for item in ordered_tm:
				if item[0].lower() == artist.lower() and item[1].lower() == song.lower():
					is_exists = True
					item[2] = is_karaoke
					item[3] += 1
					break
			if not is_exists:
				ordered_tm.append( [artist, song, is_karaoke, 1] )
		else:
			ordered_tm.append( [artist, song, is_karaoke, 1] )
		ordered[tm] = ordered_tm
		# print(ordered)
		open(ordered_path, 'w').write(json.dumps(ordered))


class Track(object):
	def __init__(self, name, idx, is_karaoke=False):
		self.name = name
		self.idx = idx
		self.is_karaoke = is_karaoke
		self.is_ordered = False
		self.list_store = []
		self.list_store_central = []

	def list_store_making(self):
		pixes = [pixbuf_music, None]
		if self.is_karaoke == True: pixes[0] = pixbuf_karaoke
		if self.is_ordered == True: pixes[1] = pixbuf_ordered
		self.list_store, self.list_store_central = list_store_making(self.name, self.idx, pixes)


class Media(object):
	def __init__(self, full_path, idx):
		self.full_path = full_path
		self.name = full_path.split('/')[-1]
		self.tracks = OrderedDict()
		self.count = 0
		self.idx = idx
		self.imgframe = None
		self.is_karaoke = False
		self.list_store = []
		self.list_store_central = []

	def list_store_making(self):
		pixes = [pixbuf_folder, None]
		if self.is_karaoke:
			pixes[1] = pixbuf_karaoke
		self.list_store, self.list_store_central = list_store_making(self.name, self.idx, pixes)


class MediaLibrary(object):
	def __init__(self):
		self.media_path = '/home/user/Music'
		self.library = OrderedDict()
		self.count = 0
		self.ls()

	def ls(self):
		self.ls_media()
		for idx in self.library:
			m = self.library.get(idx, None)
			if not m:
				self.library[idx] = None

		self.count = 0
		library_new = OrderedDict()
		for idx in self.library:
			m = self.library.get(idx, None)
			if m:
				self.count += 1
				m.idx = self.count
				library_new[self.count] = m
		self.library = library_new

		for idx in self.library:
			m = self.library.get(idx, None)
			self.ls_track(m)

	def ls_media(self):
		try:
			if not exists(self.media_path): return
			for name in sorted(listdir(self.media_path)):
				try:
					full_path = '%s/%s' % (self.media_path, name)
					if isdir(full_path):
						self.count += 1
						self.library[self.count] = Media(full_path, self.count)
				except:
					pass
		except:
			pass

	def ls_track(self, media):
		try:
			if not media: return
			for name in sorted(listdir(media.full_path)):
				try:
					full_path = '%s/%s' % (media.full_path, name)
					is_karaoke = False
					if isfile(full_path):
						if full_path[-4:].lower() in __g_video_ext__:
							media.is_karaoke = is_karaoke = True
						elif is_karafun(full_path):
							media.is_karaoke = is_karaoke = True
						if full_path[-4:].lower() in __g_audio_ext__ or is_karaoke:
							media.count += 1
							t = Track(name, media.count, is_karaoke)
							t.list_store_making()
							media.tracks[media.count] = t
				except:
					pass
			try:
				imgframe_path = '%s/img.jpeg' % media.full_path
				if not exists(imgframe_path): imgframe_path = '/home/user/musicbox/data/artist_default.png'
				media.imgframe = GdkPixbuf.Pixbuf.new_from_file_at_scale(imgframe_path, 170, 150, False)
				media.list_store_making()
			except:
				pass
		except:
			pass

	def set_media_path(self, media_path):
		if exists(media_path) and isdir(media_path):
			self.media_path = media_path

	def add_media(self, media_path):
		if exists(media_path) and isdir(media_path):
			self.count += 1
			m = Media(media_path, self.count)
			self.ls_track(m)
			self.library[self.count] = m

	def remove_media_path(self, media_path):
		idx = 0
		if exists(media_path) and isdir(media_path):
			for i in self.library:
				if l.library[i].full_path == media_path:
					idx = i
					break
		if idx:
			del l.library[idx]
			self.__init__()
