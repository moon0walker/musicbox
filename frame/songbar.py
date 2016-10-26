import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from os import listdir
from os.path import exists
import os.path
from tools.lang import _
from tools import media


MG = (1024, 768)
__g_count_showed__ = 13
__g_idx_central__ = int(__g_count_showed__/2)


def ring_tree_manage(elem, count):
	count_full = __g_count_showed__
	idx_center = __g_idx_central__
	ls = [0 for x in range(count_full)]
	if elem > count or elem < 1 or count < 1:
		return ls
	ls[idx_center] = elem

	elem_next = elem
	elem_next_end = 0
	count_current = min(count,count_full)
	for x in range(idx_center+1, idx_center+int(count_current/2)+1):
		elem_next = elem_next + 1
		if elem_next > count: elem_next = 1
		ls[x] = elem_next
		elem_next_end = elem_next

	elem_prev = elem
	for x in range(idx_center-1,-1,-1):
		elem_prev = elem_prev-1
		if elem_prev <= 0:	elem_prev = count
		if elem_prev == elem_next_end: break
		if elem_prev == ls[__g_idx_central__]: break
		ls[x] = elem_prev
	return ls


class TreeViewIcon(Gtk.TreeView):
	def __init__(self, store, columns):
		Gtk.TreeView.__init__(self, hexpand=True, vexpand=True)
		self.set_model(store)
		self.set_headers_visible(False)
		for i, column_title in enumerate(columns):
			if i == 1 or i == 3:
				column = Gtk.TreeViewColumn(column_title, Gtk.CellRendererPixbuf(), pixbuf=i)
				column.set_fixed_width(MG[0]*0.03)
			else:
				if i == 0:
					column = Gtk.TreeViewColumn(column_title, Gtk.CellRendererText(), text=i, font=4)
					column.set_fixed_width(MG[0]*0.04)
				else:
					column = Gtk.TreeViewColumn(column_title, Gtk.CellRendererText(), text=i)
					column.set_fixed_width(MG[0]*0.28)
			self.append_column(column)


class RingPanel(Gtk.Frame):
	def __init__(self, label):
		Gtk.Frame.__init__(self, hexpand=False)
		self.count = 0
		self.idx = 1
		self.ml_instance = None

		self.store = Gtk.ListStore(str, GdkPixbuf.Pixbuf, str, GdkPixbuf.Pixbuf, str)
		self.tree = TreeViewIcon(self.store, ['#', 'Icon', 'Title', 'Icon2'])

		self.box = Gtk.VBox()
		self.label = Gtk.Label(label=label, halign=Gtk.Align.START)
		self.label_count = Gtk.Label(label='0', halign=Gtk.Align.END, margin_right=10)

		self.label_box = Gtk.HBox()
		self.label_box.pack_start(self.label, False, True, 10)
		self.label_box.add(self.label_count)

		self.box.pack_start(self.label_box, False, True, 10)
		self.box.add(self.tree)
		self.add(self.box)

	def init(self):
		self.idx = 1
		self.ring_ordering()
		self.label_count.set_text(str(self.count))

	def clear(self):
		self.store.clear()

	def append_row(self, idx, idx_central, ml_item):
		list_store = []
		if ml_item:
			if idx != idx_central:
				list_store = ml_item.list_store
			else:
				list_store = ml_item.list_store_central
		self.store.append(list_store)

	def ring_ordering(self):
		self.store.clear()
		ls = ring_tree_manage(self.idx, self.count)
		for idx in ls:
			item = self.ml_instance.get(idx, None)
			self.append_row(idx, ls[__g_idx_central__], item)
		self.tree.set_cursor(Gtk.TreePath(__g_idx_central__))

	def get_active_row(self):
		(model, pathlist) = self.tree.get_selection().get_selected_rows()
		return model.get_iter(pathlist[0])

	def get_active(self):
		return self.ml_instance[self.idx].name if self.idx in self.ml_instance else None

	def get_iskaraoke(self):
		return self.ml_instance[self.idx].is_karaoke if self.idx in self.ml_instance else None


class Artist(RingPanel):
	def __init__(self, ml):
		RingPanel.__init__(self, _('ARTISTS'))
		self.set_name('RingPanel_Artist')
		self.ml_instance = ml.library
		self.count = ml.count
		self.init()

	def get_active(self):
		return self.ml_instance[self.idx].full_path


class Songs(RingPanel):
	def __init__(self):
		RingPanel.__init__(self, _('SONGS'))
		self.set_name('RingPanel_Songs')
		self.pixbuf_order_mark = GdkPixbuf.Pixbuf.new_from_file_at_scale('/home/user/musicbox/data/order_mark.png', 24, 24, False)
		self.order_list = []

	def mark_as_ordered(self):
		item = self.ml_instance[self.idx]
		item.is_ordered = True
		item.list_store_making()
		self.set_img_path(self.pixbuf_order_mark)

	def set_img_path(self, pixbuf=None):
		self.store.set_value(self.get_active_row(), 3, pixbuf)


class CentralBar(Gtk.Grid):
	def __init__(self):
		Gtk.Grid.__init__(self, hexpand=True, vexpand=True, halign=Gtk.Align.CENTER)
		self.set_row_spacing(5)
		self.pixbuf_karaoke_center = GdkPixbuf.Pixbuf.new_from_file_at_scale('/home/user/musicbox/data/karaoke2.png', 89, 89, False)

		self.cost_value = 2.0
		self.cost_currency = 'USD'
		self.karaoke_order = 1

		self.cost_box = Gtk.Grid(halign=Gtk.Align.CENTER, valign=Gtk.Align.START)
		self.cost_label = Gtk.Label(label=_('ORDER')+'\n'+_('COST'), name='CostLabels', justify=Gtk.Justification.CENTER)
		self.cost_value_label = Gtk.Label(label='1.5 usd', name='CostValueLabels')
		self.cost_box.attach(self.cost_label, 0, 0, 1, 1)
		self.cost_box.attach(self.cost_value_label, 0, 1, 1, 1)

		self.karaoke_image = Gtk.Image()

		self.attach(self.cost_box, 0, 0, 1, 1)
		self.attach(self.karaoke_image, 0, 1, 1, 1)

	def set_karaoke_cost(self, value):
			self.karaoke_order = int(value)
			pixbuf = None
			if self.karaoke_order > 0:
				pixbuf = self.pixbuf_karaoke_center
			self.karaoke_image.set_from_pixbuf(pixbuf)

	def get_karaoke_cost(self):
		return self.karaoke_order


class ImgFrame(Gtk.Frame):
	def __init__(self):
		Gtk.Frame.__init__(self, hexpand=True, halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER)
		# self.set_margin_top(52)
		self.set_margin_top(32)
		self.set_name('ImgFrame')
		self.set_size_request(215, 180)
		self.song_image = Gtk.Image()
		self.add(self.song_image)


class SongBar(Gtk.Overlay):
	def __init__(self, mon_width, mon_height):
		Gtk.Overlay.__init__(self)
		global MG, __g_count_showed__, __g_idx_central__ 
		MG = (mon_width, mon_height)
		self.ml = media.MediaLibrary()

		self.ordered = None
		self.artists = Artist(self.ml)
		self.songs = Songs()
		self.centralbar = CentralBar()

		self.songgrid = Gtk.Grid(vexpand=True, column_spacing=1)
		self.songgrid.attach(self.artists, 0, 0, 3, 1)
		self.songgrid.attach_next_to(self.centralbar, self.artists, Gtk.PositionType.RIGHT, 1, 1)
		self.songgrid.attach_next_to(self.songs, self.centralbar, Gtk.PositionType.RIGHT, 3, 1)
		self.imgframe = ImgFrame()

		self.add_overlay(self.songgrid)
		self.add_overlay(self.imgframe)

	def get_artist_dir(self):
		return self.artists.get_active()

	def get_active_song(self):
		return self.songs.get_active()

	def is_karaoke(self):
		return self.songs.get_iskaraoke()

	def get_cost_value(self):
		return self.centralbar.cost_value

	def set_cost_value(self, value):
		self.centralbar.cost_value = float(value)
		cost_value_label = '%.1f %s' % (self.centralbar.cost_value, self.centralbar.cost_currency)
		self.centralbar.cost_value_label.set_text(cost_value_label)

	def set_cost_currency(self, value):
		self.centralbar.cost_currency = value
		cost_value_label = '%.1f %s' % (self.centralbar.cost_value, self.centralbar.cost_currency)
		self.centralbar.cost_value_label.set_text(cost_value_label)

	def set_karaoke_cost(self, value):
		self.centralbar.set_karaoke_cost(value)

	def get_karaoke_cost(self):
		return self.centralbar.get_karaoke_cost()

	def set_media_path(self, media_path):
		self.ml.set_media_path(media_path)

	def add_media_path(self, media_path):
		self.ml.add_media_path(media_path)

	def remove_media_path(self, media_path):
		self.ml.remove_media_path(media_path)

	def refresh_folders(self):
		self.ml.__init__()
		self.artists.ml_instance = self.ml.library
		self.artists.count = self.ml.count
		self.artists.init()
		for x in self.ordered.order_list:
			self.mark_as_ordered_restore(x)

	def find_track_by_full_path(self, full_path):
		if full_path:
			for i, m in self.artists.ml_instance.items():
				if m.full_path == full_path[:full_path.rfind('/')]:
					for j, t in m.tracks.items():
						if t.name == full_path.split('/')[-1]:
							return t

	def mark_as_unordered(self, full_path):
		# print('mark_as_unordered', full_path)
		t = self.find_track_by_full_path(full_path)
		if t:
			t.is_ordered = False
			t.list_store_making()

	def mark_as_ordered_restore(self, full_path):
		# print('mark_as_ordered_restore', full_path)
		t = self.find_track_by_full_path(full_path)
		if t:
			t.is_ordered = True
			t.list_store_making()

	def on_artist_row_changed(self):
		self.artists.ring_ordering()
		self.songs.order_list = self.ordered.order_list
		self.songs.ml_instance = self.artists.ml_instance[self.artists.idx].tracks
		self.songs.count = len(self.songs.ml_instance)
		self.songs.init()
		self.imgframe.song_image.set_from_pixbuf(self.artists.ml_instance[self.artists.idx].imgframe)
		return True

	def on_artist_move_up(self):
		if self.artists.idx-1 <= 0:
			self.artists.idx = self.artists.count
		else:
			self.artists.idx -= 1
		return self.on_artist_row_changed()

	def on_artist_move_down(self):
		if self.artists.idx+1 > self.artists.count:
			self.artists.idx = 1
		else:
			self.artists.idx += 1
		return self.on_artist_row_changed()

	def on_song_row_changed(self):
		self.songs.order_list = self.ordered.order_list
		self.songs.ml_instance = self.artists.ml_instance[self.artists.idx].tracks
		self.songs.count = len(self.songs.ml_instance)
		self.songs.ring_ordering()
		return True

	def on_song_move_up(self):
		if self.songs.idx-1 <= 0:
			self.songs.idx = self.songs.count
		else:
			self.songs.idx -= 1
		return self.on_song_row_changed()

	def on_song_move_down(self):
		if self.songs.idx+1 > self.songs.count:
			self.songs.idx = 1
		else:
			self.songs.idx += 1
		return self.on_song_row_changed()
