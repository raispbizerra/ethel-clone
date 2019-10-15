# Default imports
from datetime import datetime

# Third party imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Local imports
from src.database.patient_dao import PatientDao
from src.database.static_exam_dao import StaticExamDao
from src.database.dynamic_exam_dao import DynamicExamDao
import src.utilities.utils as utils

class Handler():
	"""This class implements Load Patient Window Handler
	"""

	def __init__(self, window):
		self.window = window
		self.patient_dao = PatientDao()
		self.static_exam_dao = StaticExamDao()
		self.dynamic_exam_dao = DynamicExamDao()

		# List store (treeview's model)
		self.list_store = Gtk.ListStore(int, str, str, str, int, float, float)
		
		# Treeview
		self.treeview = Gtk.TreeView(self.list_store)
		
		# Fill treeview with list store
		for i, col_title in enumerate(['Cod', 'Nome', 'Sexo', 'Nascimento', 'Altura (cm)', 'Peso (kg)', 'IMC']):
			renderer = Gtk.CellRendererText()
			column = Gtk.TreeViewColumn(col_title, renderer, text=i)
			column.set_sort_column_id(i)
			self.treeview.append_column(column)

		# Connect signal for change in selection
		row_selection = self.treeview.get_selection()
		row_selection.connect('changed', self.on_row_selection_changed)

		# Add treeview to window
		self.window.treeview_box.add(self.treeview)
		self.window.treeview_box.reorder_child(self.treeview, 1)

	def fill_liststore(self, name):
		"""
		This method fills liststore with patient data

		Parameters
		----------
		window : Gtk.Window
			The window
		"""

		# Clear liststore
		self.list_store.clear()

		# Recover all patients stored at database
		patients = list()
		if self.patient_list:
			for patient in self.patient_list:
				if name in patient.get_name():
					patients.append(patient)

		# Fill liststore with patients
		for patient in patients:
			data = patient.get_patient()
			data[3] = utils.date_to_str(data[3])
			self.list_store.append(data)

	def on_show(self, window):
		"""
		This method handles window show

		Parameters
		----------
		window : Gtk.Window
			The window
		"""
		self.window.search.set_text('')
		self.window.search.grab_focus()
		self.patient_list = self.patient_dao.list_patients() # Patient list
		self.fill_liststore('')
		self.window.load_button.set_sensitive(False)
		self.window.show_all()

	def on_row_selection_changed(self, selection):
		"""
		This method handles selection change

		Parameters
		----------
		selection : Gtk.TreeSelection
			The selection
		"""
		# Get selection model (liststore)
		model, i = selection.get_selected()

		# Assign patient cod variable
		self.patient_cod = model[i][0]

		self.window.load_button.set_sensitive(True)

	def on_search_changed(self, entry):
		"""
		This method handles the change in search

		Parameters
		----------
		entry : Gtk.Entry
			The entry
		"""
		self.window.load_button.set_sensitive(False)
		self.fill_liststore(entry.get_text().upper())

	def on_cancel_clicked(self, button : Gtk.Button):
		"""
		This method handles the click in cancel button

		Parameters
		----------
		button : Gtk.Button
			The button
		"""
		# Hiding the window
		self.window.hide()

	def load_static_exams(self):
		# Clear liststore
		self.window.app.main_window.static_list_store.clear()

		# Recover all exams from patient
		self.window.app.static_exam_list = self.static_exam_dao.read_exams_from_patient(self.window.app.patient.get_cod())
			
		# Fill liststore with exams
		for exam in self.window.app.static_exam_list:
			data = list()
			data.append(exam.get_cod())
			data.append(exam.get_type())
			for d in utils.datetime_to_str(exam.get_date()).split(' '):
				data.append(d)
			self.window.app.main_window.static_list_store.append(data)

	def load_dynamic_exams(self):
		self.window.app.main_window.dynamic_list_store.clear()

		# Recover all exams from patient
		self.window.app.dynamic_exam_list = self.dynamic_exam_dao.read_exams_from_patient(self.window.app.patient.get_cod())
			
		# Fill liststore with exams
		for exam in self.window.app.dynamic_exam_list:
			data = list()
			data.append(exam.get_cod())
			for d in utils.datetime_to_str(exam.get_date()).split(' '):
				data.append(d)
			self.window.app.main_window.dynamic_list_store.append(data)

	def on_load_clicked(self, button : Gtk.Button):
		"""
		This method handles the click in load button

		Parameters
		----------
		button : Gtk.Button
			The button
		"""
		# Assign patient
		self.window.app.patient = self.patient_dao.read_patient(self.patient_cod)

		# txt = "Nome: {}\tAltura (cm): {}".format(self.window.app.patient.get_name(), self.window.app.patient.get_height())
		# self.window.app.patient_label.set_text(txt)
		self.window.app.patient_label.set_text(self.window.app.patient.get_name())
		self.window.app.statusbar.set_text("Paciente carregado.")

		self.window.app.main_window.edit_patient.set_sensitive(True)

		self.load_static_exams()
		self.load_dynamic_exams()

		# Hiding the window
		self.window.app.connection_flags['patient'] = True
		self.window.hide()