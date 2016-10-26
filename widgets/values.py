from gi.repository import Gtk
from . import widgets, files
from tools.lang import _
from tools.equalizer import Equalizer
from tools.updater import Updater
import css, os, sys

class ValuesFrame(Gtk.Frame):
	(COLUMN_NAME, COLUMN_VALUE) = range(2)

	def __init__(self, parent, data, settings):
		Gtk.Frame.__init__(self)
		self.set_label(_('Value').upper())
		self.set_size_request(150,10)
		self.parent = parent
		self.data = data
		self.settings = settings
		self.alignment_values = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0.5, yscale=0.2)
		self.alignment_values.set_padding(0,0,0,0)
		self.add(self.alignment_values)

	def get_data_obj(self, data, label):
		return list(filter(lambda x: x.label == label, data))[0]

	def set_value_list(self, label, value):
		# for widget in widgets.ValuesFrame.alignment_values.get_children():
		# 	widgets.ValuesFrame.alignment_values.remove(widget)
		widgets.ValuesFrame.set_size_request(300,300)
		for widget in self.alignment_values.get_children():
			self.alignment_values.remove(widget)

		data = self.get_data_obj(self.data, label)
		if type(data) == widgets.ControlPanelRowNumerical:
			self.label_value = label_value = Gtk.Label(label='')
			# widgets.ValuesFrame.alignment_values.add(label_value)
			self.alignment_values.add(label_value)
			label_value.set_name('LabelValue')
			label_value.set_label(value)
			css.add_css(label_value, '/home/user/musicbox/css/preferences.css')
			label_value.show()
		elif type(data) == widgets.ControlPanelRowList:
			if len(data.values) > 0:
				self.model_values = model_values = Gtk.ListStore(str)
				for row in data.values:
					model_values.append([row[0],])

				renderer = Gtk.CellRendererText()
				renderer.set_alignment(0.5, 0)
				column = Gtk.TreeViewColumn("Value", renderer, text=self.COLUMN_NAME)
				# column.set_fixed_width(300)
				# column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
				column.set_alignment(0.5)
				
				self.treeview_value = treeview_value = Gtk.TreeView()
				treeview_value.set_name('TreeValue')
				# widgets.ValuesFrame.alignment_values.add(treeview_value)
				self.alignment_values.add(treeview_value)
				treeview_value.set_model(model_values)
				treeview_value.set_headers_visible(False)
				treeview_value.append_column(column)
				# treeview_value.connect('cursor-changed', self._on_move_cursor_on_values)
				css.add_css(treeview_value, '/home/user/musicbox/css/preferences.css')
				treeview_value.show()

				treeview_value.set_cursor(Gtk.TreePath(0))
				treeview_value.grab_focus()

		widgets.ValuesFrame.set_label(_('Value').upper())

	##########################################################################
	### Hotkeys in Main Window ###############################################
	##########################################################################
	def get_selected_value(self, selection, index):
		(model, path) = selection.get_selected()
		return model.get_value(path,index)

	def get_selected_index(self, selection):
		(model, path) = selection.get_selected_rows()
		return path[0].get_indices()[0]

	### X ###
	def _on_save_value(self, *_e):
		value = ''
		label = self.get_selected_value(widgets.ControlPanelFrame.treeview_settings.get_selection(), 0)
		if type(self.get_data_obj(self.data, label)) == widgets.ControlPanelRowNumerical:
			value = self.label_value.get_label()
		elif type(self.get_data_obj(self.data, label)) == widgets.ControlPanelRowList:
			value = self.get_selected_value(self.treeview_value.get_selection(), 0)

		obj = self.get_data_obj(self.data, label)

		if obj.name == 'exit':
			# self.parent.mainwindow.frame_songbar.on_artist_row_changed()
			self.make_exit(obj, value)
		else:
			if obj.name == 'theme':
				self.set_main_theme(obj, value)
			if obj.name == 'banner':
				if value.lower() == _('Select path').lower():
					settings_option = 'preferences/' + obj.name
					self.file_window = files.FileWindow( window_type=widgets.BANNER_WINDOW,
														 settings=self.settings,
														 settings_option=settings_option,
														 parent=self.parent,
														 path='/media/usb0',
														 # path='/home/user/Pictures', ###############################
														 values=[_('Open folder/Add file'), _('Exit')] )
				else:
					(model, path) = widgets.ControlPanelFrame.treeview_settings.get_selection().get_selected()
					model.set_value(path, self.COLUMN_VALUE, value)
			elif obj.name == 'demo_folders':
				if value.lower() == _('Select path').lower():
					settings_option = 'preferences/' + obj.name
					self.file_window = files.FileWindow( window_type=widgets.DEMO_WINDOW,
														 settings=self.parent.settings,
														 settings_option=settings_option,
														 parent=self.parent,
														 path=self.settings.get_option('preferences/media_path'),
														 values=[_('Add folder'), _('Exit')] )
				else:
					(model, path) = widgets.ControlPanelFrame.treeview_settings.get_selection().get_selected()
					model.set_value(path, self.COLUMN_VALUE, value)	
			elif obj.name == 'media_files':
				settings_option = 'preferences/' + obj.name
				if value.lower() == _('Add').lower():
					self.file_window = files.FileWindow( window_type=widgets.MEDIA_WINDOW,
														 settings=self.settings,
														 settings_option=settings_option,
														 parent=self.parent,
														 # path='/media/usb0',
														 path='/home/user/M', ###############################
														 values=[_('Add folder'), _('Exit with saving'), _('Exit without saving')] )
				elif value.lower() == _('Remove').lower():
					self.file_window = files.FileWindow( window_type=widgets.MEDIA_WINDOW,
														 settings=self.settings,
														 settings_option=settings_option,
														 parent=self.parent,
														 path=self.settings.get_option('preferences/media_path'),
														 values=[_('Remove folder'), _('Exit with saving'), _('Exit without saving')] )
				else:
					(model, path) = widgets.ControlPanelFrame.treeview_settings.get_selection().get_selected()
					model.set_value(path, self.COLUMN_VALUE, value)
			elif obj.name == 'language':
				(model, path) = widgets.ControlPanelFrame.treeview_settings.get_selection().get_selected()
				model.set_value(path, self.COLUMN_VALUE, value)
				value = obj.get_value(value)
				self.settings.set_option('preferences/' + obj.name, value, save=True)
				self.parent.mainwindow.stop_all()
				python = sys.executable
				self.parent.save_settings()
				os.execl(python, python, '/home/user/musicbox/start.py')
			elif obj.name == 'update':
				upd = Updater('/media') ###############################
				if upd.check_usb():
					if upd.find_file():
						self.parent.mainwindow.stop_all()
						upd.unpack_update()
						upd.start_update()
					else:
						files.DialogWindow(message=_('Insert media storage!'), color=self.settings.get_option('preferences/theme'))
				else:
					files.DialogWindow(message=_('Insert media storage!'), color=self.settings.get_option('preferences/theme'))
			elif obj.name == 'equalizer':
				Equalizer(self.settings, self.parent.mainwindow.player , self.parent.mainwindow.demo_player)
			elif obj.name == 'statistics':
				path = '/home/user/musicbox/data/stat_ordered.json'
				if value.lower() == _('Show').lower():
					self.file_window = files.FileWindow( window_type=widgets.STATISTICS_WINDOW,
													 	 settings=self.settings,
													 	 settings_option=None,
													 	 parent=self.parent,
													 	 path=path,
													 	 values=[] )
				elif value.lower() == _('Clear').lower():
					if os.path.exists( path ): os.remove( path )
					files.DialogWindow(message=_('Statistics is cleared'), color=self.settings.get_option('preferences/theme'))
			else:
				(model, path) = widgets.ControlPanelFrame.treeview_settings.get_selection().get_selected()
				model.set_value(path, self.COLUMN_VALUE, value)

			# if obj.name != None:
			# 	self.settings.set_option('preferences/' + obj.name, value, save=True)

		return True

	def make_exit(self, obj, value):
		if obj.get_value(value) == 0:
			self.parent.quit(save=False)
		elif obj.get_value(value) == 1:
			self.parent.quit(save=True)

	def rewrite_css(self, widget, value, css_class):
		# print(widget.get_name())
		# print(widget.get_name().split('_')[0] + '_' + value)
		widget.set_name( widget.get_name().split('_')[0] + '_' + value )
		css.add_css(widget, css_class)

	def set_main_theme(self, obj, value):
		value = obj.get_value(value)
		self.rewrite_css(self.parent.mainwindow.mainframe, value, '/home/user/musicbox/css/musicbox.css')
		# self.rewrite_css(self.parent.mainwindow.frame_songbar.artists, value, '/home/user/musicbox/css/musicbox.css')
		# self.rewrite_css(self.parent.mainwindow.frame_songbar.sings,   value, '/home/user/musicbox/css/musicbox.css')
		self.rewrite_css(self.parent.main_frame,  value, '/home/user/musicbox/css/preferences.css')
		self.rewrite_css(self.parent.label_frame, value, '/home/user/musicbox/css/preferences.css')
		if obj.name != None:
			self.settings.set_option('preferences/' + obj.name, value, save=True)

	### D ###
	def _on_settings_value_up(self, *_e):
		widget, obj = self.get_widget_for_step()
		if type(obj) == widgets.ControlPanelRowNumerical:
			if type(obj.step) == float:
				new_value = float(widget.get_label()) + obj.step
				if new_value > obj.maximum:
					widget.set_label(str(obj.maximum))
				else:
					widget.set_label(str(round(new_value,1)))
			else:
				new_value = int(widget.get_label()) + obj.step
				if new_value > obj.maximum:
					widget.set_label(str(obj.maximum))
				else:
					widget.set_label(str(new_value))
			self._on_save_value()
		elif type(obj) == widgets.ControlPanelRowList:
			selected_index = self.get_selected_index(self.treeview_value.get_selection())
			if selected_index > 0:
				row = selected_index-1
				self.treeview_value.row_activated(Gtk.TreePath(row), Gtk.TreeViewColumn(None))
				self.treeview_value.set_cursor(Gtk.TreePath(row))
				label = self.get_selected_value(widgets.ControlPanelFrame.treeview_settings.get_selection(), 0)
				if self.get_data_obj(self.data, label).name in ['karaoke_order', 'currency', 'theme']:
					self._on_save_value()

		return True

	### C ###
	def _on_settings_value_down(self, *_e):
		widget, obj = self.get_widget_for_step()
		if type(obj) == widgets.ControlPanelRowNumerical:	
			if type(obj.step) == float:
				new_value = float(widget.get_label()) - obj.step
				if new_value < obj.minimum:
					widget.set_label(str(obj.minimum))
				else:
					widget.set_label(str(round(new_value,1)))
			else:
				new_value = int(widget.get_label()) - obj.step
				if new_value < obj.minimum:
					widget.set_label(str(obj.minimum))
				else:
					widget.set_label(str(new_value))
			self._on_save_value()
		elif type(obj) == widgets.ControlPanelRowList:
			selected_index = self.get_selected_index(self.treeview_value.get_selection())
			if selected_index < len(self.model_values):
				row = selected_index+1
				self.treeview_value.row_activated(Gtk.TreePath(row), Gtk.TreeViewColumn(None))
				self.treeview_value.set_cursor(Gtk.TreePath(row)) 
				label = self.get_selected_value(widgets.ControlPanelFrame.treeview_settings.get_selection(), 0)
				if self.get_data_obj(self.data, label).name in ['karaoke_order', 'currency', 'theme']:
					self._on_save_value()

		return True

	def get_widget_for_step(self):
		widg, obj = None, None
		for widget in self.alignment_values.get_children():
			if (type(widget) == Gtk.Label and widget.get_label() != self.get_label()) or type(widget) == Gtk.TreeView:
				label = self.get_selected_value(widgets.ControlPanelFrame.treeview_settings.get_selection(), 0)
				obj = self.get_data_obj(self.data, label)
				widg = widget
		return widg, obj
