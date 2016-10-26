from gi.repository import Gtk, GObject, GLib
from gi.repository import GdkPixbuf
import os
import stat
import shutil
import css
import time
from . import widgets
from tools.lang import _
import json
import collections


class FileWindow(Gtk.Window):
	def __init__(self, window_type, settings, settings_option, parent=None, values=None, path='/home'):
		Gtk.Window.__init__(self)
		
		self.window_type     = window_type
		self.settings        = settings
		self.settings_option = settings_option
		self.parent          = parent
		self.values          = values
		self.path            = path

		try:
			if (os.path.exists(self.path) and os.path.isdir(self.path) and len(os.listdir(self.path)) > 0) or (self.window_type == widgets.STATISTICS_WINDOW and os.path.exists(self.path)):
				# Config window
				self.config_main_window()

				self.hbox = hbox = Gtk.HBox(homogeneous=False, spacing=20)
				self.add(hbox)

				# Left frame
				self.file_frame = None
				if self.window_type == widgets.STATISTICS_WINDOW:
					self.parse_stat_json()
					self.values.append(_('Exit'))
					self.file_frame = StatisticsFrame(parent=self, color=self.settings.get_option('preferences/theme'), date=self.values[0], songlist=self.statistics)
				else:
					self.file_frame = FileFrame(parent=self, path=self.path, color=self.settings.get_option('preferences/theme'))
				hbox.add(self.file_frame)

				# Right frame
				self.menu_frame = MenuFrame(parent=self, values=self.values, color=self.settings.get_option('preferences/theme'))
				hbox.add(self.menu_frame)
				if window_type == widgets.STATISTICS_WINDOW:
					self.menu_frame.set_size_request(100, 600)	

				self.setup_hotkeys()

				self.set_app_paintable(True)
				self.connect("draw", self.area_draw)
				css.add_css(self, '/home/user/musicbox/css/preferences.css')
				self.show_all()

				self.add_list = {}
				self.delete_list = set()
				self.selected_rows = set()
				self.current_index = 0
				self.menu_frame.treeview_menu.get_selection().select_path(Gtk.TreePath(self.current_index))
				self.file_frame.fileSystemTreeView.get_selection().select_path(Gtk.TreePath(self.current_index))
			else:
				if self.window_type == widgets.BANNER_WINDOW or self.window_type == widgets.MEDIA_WINDOW:
					DialogWindow(message=_('Insert media storage musicbox!'), color=self.settings.get_option('preferences/theme'))
				else:
					DialogWindow(message=_('Cant find path!'), color=self.settings.get_option('preferences/theme'))
		except Exception as err:
			if self.window_type == widgets.BANNER_WINDOW or self.window_type == widgets.MEDIA_WINDOW:
				DialogWindow(message=_('Insert media storage musicbox!') + ':\n' + str(err), color=self.settings.get_option('preferences/theme'))
			else:
				DialogWindow(message=_('Cant find path!'), color=self.settings.get_option('preferences/theme'))					

	def area_draw(self, widget, cr):
		import cairo
		cr.set_source_rgba(.2, .2, .2, 0)
		cr.set_operator(cairo.OPERATOR_SOURCE)
		cr.paint()
		cr.set_operator(cairo.OPERATOR_OVER)

	def config_main_window(self):
		self.set_name('FileWindow')
		self.set_decorated(False)
		self.set_border_width(5)
		self.set_size_request(800, 600)
		self.set_modal(True)
		self.set_position(Gtk.WindowPosition.CENTER)
		self.screen = self.get_screen()
		self.visual = self.screen.get_rgba_visual()
		if self.visual != None and self.screen.is_composited():
			self.set_visual(self.visual)
		# self.connect('destroy', Gtk.main_quit)

	def parse_stat_json(self):
		if os.path.exists(self.path):
			fd = open(self.path, 'r')
			try:	self.statistics = json.loads(fd.read())
			except:	pass
			fd.close()
			for key in self.statistics:
				self.values.append(key)
			self.values.sort()
			# self.statistics = collections.OrderedDict( sorted( self.statistics.items, key=lambda t: t[0] ) )

	def setup_hotkeys(self):
		hotkeys = (
			('A', self._on_file_list_up),
			('Z', self._on_file_list_down),
			('D', self._on_menu_list_up),
			('C', self._on_menu_list_down),
			('X', self._on_menu_list_exit),
			('S', self._block_key),
			('V', self._block_key)
		)
		self.accel_group = Gtk.AccelGroup()
		for key, function in hotkeys:
			key, mod = Gtk.accelerator_parse(key)
			self.accel_group.connect(key, mod, Gtk.AccelFlags.VISIBLE, function)
		self.add_accel_group(self.accel_group)

	##########################################################################
	### Hotkes in Main Window ################################################
	##########################################################################

	### S, V ###
	def _block_key(self, *_e):
		return True

	### X ###
	def _on_menu_list_exit(self, *_e):
		selection = self.menu_frame.treeview_menu.get_selection()
		(allmodel, allpath) = selection.get_selected()
		value = allmodel.get_value(allpath, 0)

		if value.lower() == _('Exit with saving').lower():
			# Remove folders
			if len(self.delete_list) > 0:
				DialogWindow(
					self.parent,
					_('Wait...'), 
					False, 
					self.settings.get_option('preferences/theme'),
					shutil.rmtree, 
					self.delete_list)
				self.parent.mainwindow.remove_media_path_list(self.delete_list)
				self.settings.set_option('preferences/changed', True, save=True)

			# Add folders
			if len(self.add_list) > 0:
				DialogWindow(
					self.parent,
					_('Wait...'), 
					False, 
					self.settings.get_option('preferences/theme'),
					shutil.copytree, 
					self.add_list)
				self.parent.mainwindow.add_media_path_list()
				self.settings.set_option('preferences/changed', True, save=True)

			self.add_list.clear()
			self.delete_list.clear()
			self.selected_rows.clear()
			self.destroy()
		elif value.lower() == _('Exit without saving').lower():
			self.add_list.clear()
			self.delete_list.clear()
			self.selected_rows.clear()
			self.destroy()
		elif value.lower() == _('Exit').lower():
			self.add_list.clear()
			self.delete_list.clear()
			self.selected_rows.clear()
			self.destroy()
		else:
			if self.window_type == widgets.BANNER_WINDOW:
				if _('Add file').lower() in value.lower():
					model = self.file_frame.fileSystemTreeView.get_model()
					path = model.get_iter(Gtk.TreePath(self.current_index))
					if path != None:
						filepath = model.get_value(path, 2)
						if os.path.isdir(filepath):
							pass
							# if self.file_frame.fileSystemTreeView.expand_row(path, open_all=False):
							# 	self.file_frame.onRowExpanded( self.file_frame.fileSystemTreeView, model.get_iter(path[0]), path[0] )
							# else:
							# 	self.file_frame.onRowCollapsed( self.file_frame.fileSystemTreeView, model.get_iter(path[0]), path[0] )
						else:
							# copy banner to tmp dir
							if not os.path.exists('/home/user/musicbox/data/banner'):
								os.makedirs('/home/user/musicbox/data/banner')
							filepath_new = os.path.join( '/home/user/musicbox/data/banner', filepath.split('/')[-1] )
							shutil.copyfile(filepath, filepath_new)
							# set banner path
							(model, path) = widgets.ControlPanelFrame.treeview_settings.get_selection().get_selected()
							if path != None:
								model.set_value(path, self.parent.COLUMN_VALUE, filepath.split('/')[-1])
								# Show dialog window
								DialogWindow(message=_('Selected'), color=self.settings.get_option('preferences/theme'))
			if self.window_type == widgets.DEMO_WINDOW:
				if _('Add folder').lower() in value.lower():
					model = self.file_frame.fileSystemTreeView.get_model()
					path = model.get_iter(Gtk.TreePath(self.current_index))
					if path != None:
						filepath = model.get_value(path, 2)
						if os.path.isdir(filepath):
							# self.settings.set_option(self.settings_option, filepath, save=True)
							(model, path) = widgets.ControlPanelFrame.treeview_settings.get_selection().get_selected_rows()
							path = path[0] if len(path) > 0 else None
							if path != None:
								model.set_value(model.get_iter(path), self.parent.COLUMN_VALUE, filepath)
								# Show dialog window
								DialogWindow(message=_('Selected'), color=self.settings.get_option('preferences/theme'))
			if self.window_type == widgets.MEDIA_WINDOW:
				if _('Add folder').lower() in value.lower():
					model = self.file_frame.fileSystemTreeView.get_model()
					path = model.get_iter(Gtk.TreePath(self.current_index))
					if path != None:
						filepath = model.get_value(path, 2)
						if os.path.isdir(filepath):
							fpath = filepath.split('/')
							if self.current_index not in self.selected_rows:
								self.add_list[filepath] = self.settings.get_option('preferences/media_path') + '/' + fpath[len(fpath)-1]
								self.selected_rows.add(self.current_index)
								self.mark_selection()
								# DialogWindow(message=_('Selected'), color=self.settings.get_option('preferences/theme'))
							else:
								del self.add_list[filepath]
								self.selected_rows.remove(self.current_index)
								self.mark_selection()
								# DialogWindow(message=_('Unselected'), color=self.settings.get_option('preferences/theme'))

				if _('Remove folder').lower() in value.lower():
					model = self.file_frame.fileSystemTreeView.get_model()
					path = model.get_iter(Gtk.TreePath(self.current_index))
					if path != None:
						filepath = model.get_value(path, 2)
						if os.path.isdir(filepath):
							if self.current_index not in self.selected_rows:
								self.delete_list.add(filepath)
								self.selected_rows.add(self.current_index)
								self.mark_selection()
								# DialogWindow(message=_('Selected'), color=self.settings.get_option('preferences/theme'))
							else:
								self.delete_list.remove(filepath)
								self.selected_rows.remove(self.current_index)
								self.mark_selection()
								# DialogWindow(message=_('Unselected'), color=self.settings.get_option('preferences/theme'))
							
		# elif 'Save'.lower() in value.lower():
		# 	self.settings.save()
		# 	self.hide()
			# Gtk.main_quit()

		return True

	def mark_selection(self):
		self.file_frame.fileSystemTreeView.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
		for ind in self.selected_rows:
			self.file_frame.fileSystemTreeView.get_selection().select_path(Gtk.TreePath(ind))

	### A ###
	def _on_file_list_up(self, *_e):
		self.file_frame.fileSystemTreeView.get_selection().unselect_path(Gtk.TreePath(self.current_index))
		if self.current_index == 0:
			self.file_frame.fileSystemTreeView.get_selection().select_path(Gtk.TreePath(self.current_index))
		elif self.current_index > 0:
			self.current_index -= 1
			self.file_frame.fileSystemTreeView.get_selection().select_path(Gtk.TreePath(self.current_index))
		self.file_frame.fileSystemTreeView.set_cursor(Gtk.TreePath(self.current_index))
		self.mark_selection()

		return True

	### Z ###
	def _on_file_list_down(self, *_e):
		self.file_frame.fileSystemTreeView.get_selection().unselect_path(Gtk.TreePath(self.current_index))

		if self.current_index < len(self.file_frame.fileSystemTreeView.get_model())-1:
			self.current_index += 1

		self.file_frame.fileSystemTreeView.get_selection().select_path(Gtk.TreePath(self.current_index))
		self.file_frame.fileSystemTreeView.set_cursor(Gtk.TreePath(self.current_index))
		self.mark_selection()

		return True

	### D ###
	def _on_menu_list_up(self, *_e):
		selection = self.menu_frame.treeview_menu.get_selection()
		(model, path) = selection.get_selected_rows()
		if len(path) > 0:
			selected_index = path[0].get_indices()[0]
			
			if selected_index > 0:
				row = selected_index-1
				self.menu_frame.treeview_menu.row_activated(Gtk.TreePath(row), Gtk.TreeViewColumn(None))
				self.menu_frame.treeview_menu.set_cursor(Gtk.TreePath(row)) 

				if self.window_type == widgets.STATISTICS_WINDOW:
					selection = self.menu_frame.treeview_menu.get_selection()
					(allmodel, allpath) = selection.get_selected()
					date = allmodel.get_value(allpath, 0)
					if date !=_('Exit'):
						self.current_index = 0
						self.file_frame.fileSystemTreeView.row_activated(Gtk.TreePath(self.current_index), Gtk.TreeViewColumn(None))
						self.file_frame.fileSystemTreeView.set_cursor(Gtk.TreePath(self.current_index)) 
						self.file_frame.refresh_frame(date)
		return True

	### C ###
	def _on_menu_list_down(self, *_e):
		selection = self.menu_frame.treeview_menu.get_selection()
		(model, path) = selection.get_selected_rows()
		if len(path) > 0:
			selected_index = path[0].get_indices()[0]

			if selected_index < len(self.menu_frame.model_menu):
				row = selected_index+1
				self.menu_frame.treeview_menu.row_activated(Gtk.TreePath(row), Gtk.TreeViewColumn(None))
				self.menu_frame.treeview_menu.set_cursor(Gtk.TreePath(row)) 

				if self.window_type == widgets.STATISTICS_WINDOW:
					selection = self.menu_frame.treeview_menu.get_selection()
					(allmodel, allpath) = selection.get_selected()
					date = allmodel.get_value(allpath, 0)
					if date !=_('Exit'):
						self.current_index = 0
						self.file_frame.fileSystemTreeView.row_activated(Gtk.TreePath(self.current_index), Gtk.TreeViewColumn(None))
						self.file_frame.fileSystemTreeView.set_cursor(Gtk.TreePath(self.current_index)) 
						self.file_frame.refresh_frame(date)
		return True


class StatisticsFrame(Gtk.Frame):
	def __init__(self, parent, date, songlist, color):
		Gtk.Frame.__init__(self)
		self.set_size_request(450, 600)	
		self.parent = parent
		self.date   = date
		self.songlist = songlist
		self.set_name('FileTreeFrame_' + color)
		self.pb = GdkPixbuf.Pixbuf.new_from_file_at_scale('/home/user/musicbox/data/karaoke.png', 30, 30, True)
		self.create_file_list()

	def refresh_frame(self, date):
		self.date = date		
		for widget in self.get_children():
			self.remove(widget)
		self.create_file_list()
		css.add_css(self, '/home/user/musicbox/css/preferences.css')
		self.show_all()

	def create_file_list(self):
		self.create_model()
		self.fileSystemTreeView = Gtk.TreeView(model=self.model_stat)
		self.scrollView = Gtk.ScrolledWindow()
		# self.scrollView.set_size_request(480, 600)
		self.scrollView.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
		self.scrollView.add(self.fileSystemTreeView)
		self.add(self.scrollView)

		self.fileSystemTreeView.set_headers_visible(False)
		self.add_columns()

	def get_data_row(self, row):
		pb = None
		if row[2]:
			pb = self.pb
		return [ row[0].upper(),
				 row[1].upper(),
				 pb,
				 row[3] ]

	def create_model(self):
		self.model_stat = Gtk.ListStore(str, str, GdkPixbuf.Pixbuf, int)
		for row in self.songlist[self.date]:
			self.model_stat.append(self.get_data_row(row))

	def add_columns(self):
		renderer = Gtk.CellRendererText()
		renderer.set_property("wrap-width", 200) 
		renderer.set_property("wrap-mode", Gtk.WrapMode.WORD) 
		column = Gtk.TreeViewColumn("Song name", renderer, text=0)
		column.set_fixed_width(200)
		self.fileSystemTreeView.append_column(column)

		renderer = Gtk.CellRendererText()
		renderer.set_property("wrap-width", 400) 
		renderer.set_property("wrap-mode", Gtk.WrapMode.WORD) 
		column = Gtk.TreeViewColumn("Song name", renderer, text=1)
		column.set_fixed_width(400)
		self.fileSystemTreeView.append_column(column)

		renderer = Gtk.CellRendererPixbuf()
		renderer.set_alignment(0.5, 0.5)
		column = Gtk.TreeViewColumn("Is karaoke", renderer, pixbuf=2)
		column.set_alignment(1)
		column.set_fixed_width(30)
		self.fileSystemTreeView.append_column(column)

		renderer = Gtk.CellRendererText()
		renderer.set_alignment(1, 0)
		column = Gtk.TreeViewColumn("Count", renderer, text=3)
		column.set_alignment(1)
		column.set_fixed_width(70)
		self.fileSystemTreeView.append_column(column)		

class FileFrame(Gtk.Frame):
	def __init__(self, parent, path, color):
		Gtk.Frame.__init__(self)
		
		self.parent = parent
		self.path   = path
		self.set_name('FileTreeFrame_' + color)

		# Make TreeView
		self.fileSystemTreeView = Gtk.TreeView()
		self.fileSystemTreeView.set_headers_visible(False)
		treeViewCol = Gtk.TreeViewColumn("File")
		colCellText = Gtk.CellRendererText()
		colCellImg  = Gtk.CellRendererPixbuf()
		treeViewCol.pack_start(colCellImg,  False)
		treeViewCol.pack_start(colCellText, True)
		treeViewCol.add_attribute(colCellText, "text",   0)
		treeViewCol.add_attribute(colCellImg,  "pixbuf", 1)
		self.fileSystemTreeView.append_column(treeViewCol)

		# self.fileSystemTreeView.can_focus = True
		# self.fileSystemTreeView.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)

		self.scrollView = Gtk.ScrolledWindow()
		self.scrollView.add(self.fileSystemTreeView)
		self.add(self.scrollView)

		self.make_filetree()

	def make_filetree(self):
		self.fileSystemTreeStore = Gtk.TreeStore(str, GdkPixbuf.Pixbuf, str)
		self.populateFileSystemTreeStore(self.fileSystemTreeStore, self.path)

		self.fileSystemTreeView.set_model(self.fileSystemTreeStore)
		# self.fileSystemTreeView.connect("row-expanded", self.onRowExpanded)
		# self.fileSystemTreeView.connect("row-collapsed", self.onRowCollapsed)
		# self.fileSystemTreeView.connect("expand-collapse-cursor-row", self.parent._on_menu_list_exit)

	def populateFileSystemTreeStore(self, treeStore, path, parent=None):
		itemCounter = 0
		listing = sorted(os.listdir(path))
		for item in listing:
			itemFullname = os.path.join(path, item)
			itemMetaData = os.stat(itemFullname)
			itemIsFolder = stat.S_ISDIR(itemMetaData.st_mode)
			if item[0] != '.':
				if self.parent.window_type == widgets.BANNER_WINDOW:
					if itemIsFolder or '.JPEG' in item or '.JPG' in item or '.jpeg' in item or '.jpg' in item or '.png' in item or '.bmp' in item or '.gif' in item:
						itemIcon = Gtk.IconTheme.get_default().load_icon("folder" if itemIsFolder else "insert-image", 22, 0)
						currentIter = treeStore.append(parent, [item, itemIcon, itemFullname])
						if itemIsFolder: 
							treeStore.append(currentIter, [None, None, None])
						itemCounter += 1
				if self.parent.window_type == widgets.DEMO_WINDOW:
					if itemIsFolder or '.mp3' in item or '.midi' in item:
						itemIcon = Gtk.IconTheme.get_default().load_icon("folder" if itemIsFolder else "insert-image", 22, 0)
						currentIter = treeStore.append(parent, [item, itemIcon, itemFullname])
						if itemIsFolder: 
							treeStore.append(currentIter, [None, None, None])
						itemCounter += 1		
				if self.parent.window_type == widgets.MEDIA_WINDOW:
					if itemIsFolder or '.mp3' in item or '.midi' in item or '.avi' in item:
						itemIcon = Gtk.IconTheme.get_default().load_icon("folder" if itemIsFolder else "insert-image", 22, 0)
						currentIter = treeStore.append(parent, [item, itemIcon, itemFullname])
						if itemIsFolder: 
							treeStore.append(currentIter, [None, None, None])
						itemCounter +=1
		self.fileSystemTreeView.set_model(treeStore)
		# if itemCounter < 1: treeStore.append(parent, [None, None, None])

	def onRowExpanded(self, treeView, treeIter, treePath):
		treeStore = treeView.get_model()
		if treeStore.iter_children(treeIter) != None:
			newPath = treeStore.get_value(treeIter, 2)
			self.populateFileSystemTreeStore(treeStore, newPath, treeIter)
			treeStore.remove(treeStore.iter_children(treeIter))
		self.fileSystemTreeView.set_model(treeStore)

	def onRowCollapsed(self, treeView, treeIter, treePath):
		treeStore = treeView.get_model()
		if treeStore.iter_children(treeIter) != None:
			currentChildIter = treeStore.iter_children(treeIter)
			while currentChildIter:
				treeStore.remove(currentChildIter)
				currentChildIter = treeStore.iter_children(treeIter)
			treeStore.append(treeIter, [None, None, None])
		self.fileSystemTreeView.set_model(treeStore)


class MenuFrame(Gtk.Frame):
	(COLUMN_NAME, COLUMN_VALUE) = range(2)

	def __init__(self, parent, values, color):
		Gtk.Frame.__init__(self)
		
		self.parent = parent
		self.parent = values
		self.set_name('FileMenuFrame_' + color)
		
		self.model_menu = model_menu = Gtk.ListStore(str)
		for row in values:
			model_menu.append([row,])

		renderer = Gtk.CellRendererText()
		renderer.set_alignment(0.5, 0)
		column = Gtk.TreeViewColumn("Name", renderer, text=0)
		# column.set_fixed_width(300)
		# column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
		column.set_alignment(0.5)
		
		self.treeview_menu = treeview_menu = Gtk.TreeView()
		treeview_menu.set_name('TreeMenu')
		self.alignment_menu = alignment_menu = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0.5, yscale=0.2)
		# widgets.ValuesFrame.alignment_menu.add(treeview_menu)
		alignment_menu.add(treeview_menu)

		treeview_menu.set_model(model_menu)
		treeview_menu.set_headers_visible(False)
		treeview_menu.append_column(column)
		# treeview_menu.connect('cursor-changed', self._on_move_cursor_on_values)
		# css.add_css(treeview_menu, '/home/user/musicbox/css/preferences.css')
		# treeview_menu.show()

		treeview_menu.set_cursor(Gtk.TreePath(0))
		treeview_menu.grab_focus()
		self.add(alignment_menu)


class DialogWindow(Gtk.Window):
	def __init__(self, parent=None, message='None', apply_key=True, color=None, clbck=None, *clbck_args):
		Gtk.Window.__init__(self)
		# GObject.threads_init()
		self.parent = parent
		self.color = color
		self.message = message
		self.set_name('DialogWindow')
		self.set_decorated(False)
		self.set_app_paintable(True)
		# self.set_border_width(3)
		self.set_modal(True)
		self.set_size_request(300, 150)
		self.set_position(Gtk.WindowPosition.CENTER)
		self.screen = self.get_screen()
		self.visual = self.screen.get_rgba_visual()
		if self.visual != None and self.screen.is_composited():
			self.set_visual(self.visual)
		# self.connect('destroy', Gtk.main_quit)

		dialogBox = Gtk.Box(homogeneous=False, spacing=1)
		self.add(dialogBox)
		
		# Dialog frame
		dialogFrame = Gtk.Frame()
		dialogFrame.set_name( 'DialogFrame_' + color )
		dialogBox.pack_start(dialogFrame, True, True, 1)

		# Dialog labels
		self.dialogVBox = Gtk.VBox(homogeneous=False, spacing=5)
		dialogFrame.add(self.dialogVBox)
		self.dialogLabel1 = Gtk.Label(label=self.message)
		self.dialogVBox.add(self.dialogLabel1)

		if apply_key:
			dialogLabel2 = Gtk.Label(label=_('(Press X)'))
			self.dialogVBox.add(dialogLabel2)
			self.hotkeys_config()
		
		self.connect("draw", self.area_draw)
		css.add_css(self, '/home/user/musicbox/css/preferences.css')
		self.show_all()
		# time.sleep(1)

		if clbck != None:
			import threading
			self.thread = threading.Thread(target=self.file_thread, args=(clbck, clbck_args))
			self.thread.daemon = True
			self.thread.start()

	def hotkeys_config(self):
		hotkeys = (
			('X', self.close_dialog),
		)
		self.accel_group = Gtk.AccelGroup()
		for key, function in hotkeys:
			key, mod = Gtk.accelerator_parse(key)
			self.accel_group.connect(key, mod, Gtk.AccelFlags.VISIBLE, function)
		self.add_accel_group(self.accel_group)

	def file_thread(self, clbck, *clbck_args):
		self.make_file_op(clbck, *list(*clbck_args))
		GLib.idle_add(self.change_label)
		self.reboot()
		# self.change_label()

	def reboot(self):
		import sys
		self.parent.mainwindow.stop_all()
		python = sys.executable
		self.parent.save_settings()
		os.execl(python, python, '/home/user/musicbox/start.py')

	def make_file_op(self, clbck, *clbck_args):
		try:
			if type(*clbck_args) == dict:
				data = dict(*clbck_args)
				for it in data:
					if not os.path.exists(data[it]):
						clbck(it, data[it])
			elif type(*clbck_args) == set:
				for it in list(*clbck_args):
					clbck(it)
		except Exception as e:
			print( str(e) )

	def change_label(self):
		# time.sleep(1)
		self.dialogLabel1.set_label(_('Done'))
		dialogLabel2 = Gtk.Label(label=_('(Press X)'))
		self.dialogVBox.add(dialogLabel2)
		css.add_css(self, '/home/user/musicbox/css/preferences.css')
		dialogLabel2.show()
		self.hotkeys_config()
		
	def area_draw(self, widget, cr):
		import cairo
		cr.set_source_rgba(.2, .2, .2, 0)
		cr.set_operator(cairo.OPERATOR_SOURCE)
		cr.paint()
		cr.set_operator(cairo.OPERATOR_OVER)

	def close_dialog(self, *_e):
		self.destroy()	
		return True
