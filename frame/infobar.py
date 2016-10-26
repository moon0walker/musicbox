import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GdkPixbuf
import os.path
import math
from tools.lang import _

MG = (1366, 768)
g_iter_first = None
__g_audio_ext__ = ['.mp3', '.wav', 'midi', '.mid']
__g_video_ext__ = ['.avi', '.mp4', '.flv', '.3gp', '.mkv']


class TreeViewScroll(Gtk.Overlay):
	def __init__(self, store, columns):
		Gtk.Overlay.__init__(self)
		self.set_hexpand(True)
		self.set_vexpand(False)
		self.treeview = Gtk.TreeView(store)
		self.treeview.set_headers_visible(False)
		self.treeview.set_name('OrderedSong')
		for i, column_title in enumerate(columns):
			if i == 0:
				column = Gtk.TreeViewColumn(column_title, Gtk.CellRendererPixbuf(), pixbuf=i)
			elif i == 1:
				column = Gtk.TreeViewColumn(column_title, Gtk.CellRendererText(), text=i)
				column.set_fixed_width(250)
			self.treeview.append_column(column)
		self.add_overlay(self.treeview)


class OrderedList(Gtk.Grid):
	def __init__(self):
		Gtk.Grid.__init__(self)
		self.set_column_homogeneous(True)
		self.set_row_homogeneous(True)
		self.count = 0
		self.store = Gtk.ListStore(GdkPixbuf.Pixbuf, str)
		self.tree = TreeViewScroll(self.store, ['#', 'song'])
		self.attach(self.tree, 0, 0, 1, 1)


class OrderedSongs(Gtk.VBox):
	def __init__(self):
		Gtk.VBox.__init__(self, vexpand=False, halign=Gtk.Align.START)
		# self.player_list = [self.pixbuf_ordered, None]
		self.pixbuf_ordered = GdkPixbuf.Pixbuf.new_from_file_at_scale('/home/user/musicbox/data/ordered.png', 16, 24, False)
		self.player_list = [self.pixbuf_ordered, None]

		self.set_size_request(300, 100)
		self.max_cnt = 0

		self.label = Gtk.Label(_('ORDERED')+' ', name='OrderedSong')
		self.songs = OrderedList()
		self.count_label = Gtk.Label(self.songs.count, name='OrderedSong')
		self.order_list = []

		self.hbox = Gtk.HBox()
		self.hbox.pack_start(self.label, False, True, 0)
		self.hbox.pack_start(self.count_label, False, True, 0)
		self.add(self.hbox)
		self.add(self.songs)


	def add_order(self, full_path):
		if full_path in self.order_list:
			# print('This track already ordered! Choose another!')
			return False
		if not os.path.exists(full_path):
			return False
		self.order_list.append(full_path)
		self.reload_order()
		return True

	def path2track(self, full_path):
		track_name = full_path[full_path.rfind('/')+1:]
		if track_name[-4:].lower() in __g_audio_ext__+__g_video_ext__:
			track_name = track_name[:-4]
		return track_name

	def remove_first(self):
		self.songs.count = len(self.order_list)
		if len(self.songs.store) > 0:
			if len(self.songs.store) == 1:
				self.clear_row(0)
			else:
				self.songs.store.remove(self.songs.store[0].iter)

	def reload_order(self):
		self.songs.count = len(self.order_list)
		for i, full_path in enumerate(self.order_list):
			self.player_list[1] = self.path2track(full_path)
			if self.get_cell_value(i, 0) != self.pixbuf_ordered:
				self.set_cell_value(i, 0, self.pixbuf_ordered)

			if self.set_cell_value(i, 1, self.player_list[1]):
				pass
				# print('set_value', self.player_list[1])
			else:
				# print('append', self.player_list[1])
				self.songs.store.append(self.player_list)

	def set_cell_value(self, row, column, value):
		if row < len(self.songs.store):
			self.songs.store.set_value(self.songs.store[row].iter, column, value)
			return True
		return False

	def get_cell_value(self, row, column):
		if row < len(self.songs.store):
			return self.songs.store.get_value(self.songs.store[row].iter, column)
		return None

	def clear_row(self, row):
		self.set_cell_value(row, 0, None)
		self.set_cell_value(row, 1, None)


class OrderBar(Gtk.Frame):
	def __init__(self):
		Gtk.Frame.__init__(self, hexpand=False)
		self.set_halign(Gtk.Align.CENTER)
		self.set_valign(Gtk.Align.START)
		self.set_name('OrderButton')

		self.label = Gtk.Label(label=_('ORDER'))
		self.add(self.label)


class Credit(Gtk.HBox):
	def __init__(self):
		Gtk.HBox.__init__(self)
		self.set_hexpand(True)
		self.set_vexpand(True)
		self.left = 0

		self.paid_label = Gtk.Label(label=_('PAID'), name='CreditLeft', halign=Gtk.Align.END, valign=Gtk.Align.START)
		self.left_label = Gtk.Label(label='0.0', name='CreditLeftValue')
		self.vbox= Gtk.VBox(valign=Gtk.Align.CENTER)
		self.vbox.add(self.left_label)

		self.image = Gtk.Image()
		pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale('/home/user/musicbox/data/coin.png', MG[0]*0.09, MG[0]*0.09, False)
		self.image.set_from_pixbuf(pixbuf)

		self.overlay = Gtk.Overlay(hexpand=True, vexpand=True)
		self.overlay.add_overlay(self.image)
		self.overlay.add_overlay(self.vbox)

		self.pack_end(self.paid_label, False, True, 0)
		self.pack_end(self.overlay, False, True, 0)
		fake_label = ' '*15 if self.paid_label.get_text() == 'PAID' else ' '*10
		self.pack_end(Gtk.Label(label=fake_label), False, True, 0)

	def set_left(self, diff):
		self.left += diff
		if math.modf(self.left)[0] == 0:
			self.left = int(self.left)
		self.left_label.set_text(str(self.left))


class InfoBar(Gtk.Grid):
	def __init__(self, mon_width, mon_height):
		Gtk.Grid.__init__(self)
		self.pixbuf_ordered_demo = GdkPixbuf.Pixbuf.new_from_file_at_scale('/home/user/musicbox/data/ordered_demo.png', 16, 24, False)
		self.demo_list = [self.pixbuf_ordered_demo, None]

		global MG
		MG = (mon_width, mon_height)
		# self.set_hexpand(True)
		self.set_vexpand(False)
		self.set_column_homogeneous(True)

		self.ordered = OrderedSongs()
		self.orderbar = OrderBar()
		self.credit = Credit()

		self.attach(self.ordered, 0, 0, 4, 1)
		self.attach_next_to(self.orderbar, self.ordered, Gtk.PositionType.RIGHT, 3, 1)
		# self.attach(self.orderbar, 0, 0, 1, 1)
		self.attach_next_to(self.credit, self.orderbar, Gtk.PositionType.RIGHT, 4, 1)
		# self.attach_next_to(self.credit, self.ordered, Gtk.PositionType.RIGHT, 2, 1)

	def make_order(self, full_path, cost_value):
		ret = False
		if (self.credit.left - cost_value) >= 0 and full_path:
			if self.ordered.add_order(full_path) == True:
				self.credit.set_left(-cost_value)
				ret = True
			self.ordered.count_label.set_text(str(self.ordered.songs.count))
		return ret

	def on_end_track(self):
		track_ended = None
		if self.ordered.order_list:
			track_ended = self.ordered.order_list.pop(0)
		self.ordered.remove_first()
		self.ordered.count_label.set_text(str(self.ordered.songs.count))
		return track_ended

	def is_ordered(self, full_path):
		return (full_path in self.ordered.order_list)

	def set_demo_player_track(self, full_path):
		# print('set_demo_player_track', full_path)
		if full_path:
			track_name = full_path[full_path.rfind('/')+1:]
			if len(track_name) > 4 and track_name[-4:].lower() in __g_audio_ext__:
				track_name = track_name[:-4]
			self.demo_list[1] = track_name
			# print('set_cell_value')
			if self.ordered.get_cell_value(0, 0) != self.pixbuf_ordered_demo:
				self.ordered.set_cell_value(0, 0, self.pixbuf_ordered_demo)
			if self.ordered.set_cell_value(0, 1, track_name):
				pass
				# print('set_value')
			else:
				# print('append')
				self.ordered.songs.store.append(self.demo_list)
		else:
			# print('clear_row')
			self.ordered.clear_row(0)
		# print('end   set_demo_player_track')
