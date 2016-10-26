from gi.repository import Gtk
from . import widgets
from tools.lang import _


class ControlPanelFrame(Gtk.Frame):
	(COLUMN_NAME, COLUMN_VALUE) = range(2)

	def __init__(self, parent, data, settings):
		Gtk.Frame.__init__(self)
		self.set_label(_('Control Panel').upper())
		self.parent = parent
		self.data = data
		self.settings = settings
		self.setup_settings_list()

	def setup_settings_list(self):
		self.create_model()
		self.treeview_settings = treeview_settings = Gtk.TreeView(model=self.model_settings)
		# treeview_settings.set_rules_hint(True)
		treeview_settings.set_headers_visible(False)
		treeview_settings.connect('cursor-changed', self._on_move_cursor_on_settings)
		self.add(treeview_settings)
		self.add_columns()

	def get_data_row(self, label):
		obj = widgets.ValuesFrame.get_data_obj(self.data, label)
		value = ''
		if obj.name != None:
			if type(obj) == widgets.ControlPanelRowNumerical:
				value = self.settings.get_option('preferences/' + obj.name)
			else:
				value = obj.get_label( self.settings.get_option('preferences/' + obj.name) )
				if value == None:
					value = self.settings.get_option('preferences/' + obj.name)
		return [label, value]

	def create_model(self):
		self.model_settings = Gtk.ListStore(str,str)
		for row in self.data:
			self.model_settings.append(self.get_data_row(row.label))

	def add_columns(self):
		renderer = Gtk.CellRendererText()
		renderer.set_property("wrap-width", 325) 
		renderer.set_property("wrap-mode", Gtk.WrapMode.WORD) 
		column = Gtk.TreeViewColumn("Name", renderer, text=self.COLUMN_NAME)
		column.set_fixed_width(325)
		self.treeview_settings.append_column(column)

		renderer = Gtk.CellRendererText()
		renderer.set_alignment(1, 0)
		# renderer.set_property("wrap-width", 200) 
		# renderer.set_property("wrap-mode", Gtk.WrapMode.WORD) 
		column = Gtk.TreeViewColumn("Value", renderer, text=self.COLUMN_VALUE)
		column.set_fixed_width(300)
		column.set_alignment(1)
		self.treeview_settings.append_column(column)

	def _on_move_cursor_on_settings(self, *_e):
		self.treeview_settings.grab_focus()
		(model, path) = self.treeview_settings.get_selection().get_selected()
		label = model.get_value(path,0)
		self.parent.label.set_label('\n'+label+'\n')
		value = model.get_value(path,1)

		###############################
		# select value in value tree
		widgets.ValuesFrame.set_value_list(label, value)

	##########################################################################
	### Hotkes in Main Window ################################################
	##########################################################################
	### A ###
	def _on_settings_list_up(self, *_e):
		selection = self.treeview_settings.get_selection()
		(model, path) = selection.get_selected_rows()
		selected_index = path[0].get_indices()[0]
		if selected_index > 0:
			row = selected_index-1
			self.treeview_settings.row_activated(Gtk.TreePath(row), Gtk.TreeViewColumn(None))
			self.treeview_settings.set_cursor(Gtk.TreePath(row)) 
		return True
		
	### Z ###
	def _on_settings_list_down(self, *_e):
		selection = self.treeview_settings.get_selection()
		(model, path) = selection.get_selected_rows()
		selected_index = path[0].get_indices()[0]
		if selected_index < len(self.model_settings):
			row = selected_index+1
			self.treeview_settings.row_activated(Gtk.TreePath(row), Gtk.TreeViewColumn(None))
			self.treeview_settings.set_cursor(Gtk.TreePath(row)) 
		return True