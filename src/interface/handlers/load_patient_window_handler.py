# Default imports
import datetime as dt

# Third party imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

# Local imports
from src.database.patient_dao import PatientDao
from src.database.static_exam_dao import StaticExamDao
from src.database.dynamic_exam_dao import DynamicExamDao
import src.utilities.utils as utils
import src.utilities.calculos as calc

class Handler():
    """This class implements Load Patient Window Handler
    """

    def __init__(self, window):
        self.window = window
        self.patient_dao = PatientDao()
        self.static_exam_dao = StaticExamDao()
        self.dynamic_exam_dao = DynamicExamDao()

        # # List store (treeview's model)
        # self.window.liststore = Gtk.ListStore(int, str, str, str, int, float, float)
        
        # # Treeview
        # self.treeview = Gtk.TreeView(self.window.liststore)
        
        # # Fill treeview with list store
        # for i, col_title in enumerate(['Cod', 'Nome', 'Sexo', 'Nascimento', 'Altura (cm)', 'Peso (kg)', 'IMC']):
        #     renderer = Gtk.CellRendererText()
        #     column = Gtk.TreeViewColumn(col_title, renderer, text=i)
        #     column.set_sort_column_id(i)
        #     self.treeview.append_column(column)

        # # Connect signal for change in selection
        # row_selection = self.treeview.get_selection()
        # row_selection.connect('changed', self.on_row_selection_changed)

        # # Add treeview to window
        # self.window.treeview_box.add(self.treeview)
        # self.window.treeview_box.reorder_child(self.treeview, 1)

    def fill_liststore(self, name):
        """
        This method fills liststore with patient data

        Parameters
        ----------
        window : Gtk.Window
            The window
        """

        # Clear liststore
        self.window.liststore.clear()

        # Recover all patients stored at database
        patients = list()
        if self.patient_list:
            for patient in self.patient_list:
                if name in patient.name:
                    patients.append(patient)

        # Fill liststore with patients
        for patient in patients:
            data = [patient.cod, patient.name, patient.sex, dt.datetime.strftime(patient.birth, '%d-%m-%Y'), patient.height, patient.weight, patient.imc]
            data.append(dt.datetime.strftime(patient.birth, '%Y-%m-%d'))
            self.window.liststore.append(data)

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
        try:
            self.patient_cod = model[i][0]
        except TypeError as e:
            pass

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
        self.window.app.static_exam_list = self.static_exam_dao.read_exams_from_patient(self.window.app.patient.cod)
            
        # Fill liststore with exams
        for exam in self.window.app.static_exam_list:
            data = list()
            data.append(exam.cod)
            if exam.state == 'ON':
                exam.state = 'OA'
            elif exam.state == 'OF':
                exam.state = 'OAE'
            elif exam.state == 'CN':
                exam.state = 'OF'
            else:
                exam.state = 'OFE'
            data.append(exam.state)
            for d in dt.datetime.strftime(exam.date, '%d-%m-%Y %H:%M:%S').split(' '):
                data.append(d)
            data.append(dt.datetime.strptime(data[-2], '%d-%m-%Y').strftime('%Y-%m-%d'))
            # print(data)
            self.window.app.main_window.static_list_store.append(data)

    def load_dynamic_exams(self):
        self.window.app.main_window.dynamic_list_store.clear()

        # Recover all exams from patient
        self.window.app.dynamic_exam_list = self.dynamic_exam_dao.read_exams_from_patient(self.window.app.patient.cod)
            
        # Fill liststore with exams
        for exam in self.window.app.dynamic_exam_list:
            data = list()
            data.append(exam.cod)
            for d in dt.datetime.strftime(exam.date, '%d-%m-%Y %H:%M:%S').split(' '):
                data.append(d)
            self.window.app.main_window.dynamic_list_store.append(data)

    def fill_grid(self, top, condition):
        grid_ap = self.window.app.main_window.exam_grid.get_child_at(1, top)
        grid_ml = self.window.app.main_window.exam_grid.get_child_at(2, top)
        grid_vm = self.window.app.main_window.exam_grid.get_child_at(3, top)
        mean_ap, mean_ml, mean_vm = 0., 0., 0.
        for i in range(3):
            metrics = calc.computes_metrics(condition[i].aps, condition[i].mls)
            grid_ap.get_child_at(i, 0).set_text(f"{round(metrics['amplitude_AP'], 2)}")
            grid_ml.get_child_at(i, 0).set_text(f"{round(metrics['amplitude_ML'], 2)}")
            grid_vm.get_child_at(i, 0).set_text(f"{round(metrics['mvelo_total'], 2)}")
            mean_ap += metrics['amplitude_AP']
            mean_ml += metrics['amplitude_ML']
            mean_vm += metrics['mvelo_total']
        mean_ap /= 3
        mean_ml /= 3
        mean_vm /= 3
        grid_ap.get_child_at(3, 0).set_text(f"{round(mean_ap, 2)}")
        grid_ml.get_child_at(3, 0).set_text(f"{round(mean_ml, 2)}")
        grid_vm.get_child_at(3, 0).set_text(f"{round(mean_vm, 2)}")

    def fill_exams(self):

        if self.window.app.static_exam_list:

            on = list()
            cn = list()
            of = list()
            cf = list()
            for exam in self.window.app.static_exam_list:
                if exam.state == 'ON':
                    on.append(exam)
                elif exam.state == 'CN':
                    cn.append(exam)
                elif exam.state == 'OF':
                    of.append(exam)
                else: 
                    cf.append(exam)
            
            for i, c in enumerate((on, cn, of, cf)):
                self.fill_grid(i+2, c)

    def get_patient_age(self):
        age = int((dt.datetime.now().date() - self.window.app.patient.birth).days / 365)
        return f"{age} anos"

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

        # txt = "Nome: {}\tAltura (cm): {}".format(self.window.app.patient.name, self.window.app.patient.height)
        # self.window.app.patient_label.set_text(txt)
        self.window.app.patient_label.set_text(f"{self.window.app.patient.name}\t{self.get_patient_age()}")
        self.window.app.statusbar.set_text("Paciente carregado.")

        self.window.app.main_window.edit_patient.set_sensitive(True)

        self.window.app.main_window.handler.clear_static_charts()
        self.window.app.main_window.handler.clear_static_metrics()
        self.window.app.main_window.handler.clear_dynamic_chart()
        self.window.app.main_window.handler.clear_dynamic_metrics()
        self.window.app.main_window.handler.clear_exam_grid()
        self.load_static_exams()
        self.load_dynamic_exams()
        # self.fill_exams()

        self.window.app.main_window.handler.exam_counter = {'ON': 0, 'CN': 0, 'OF': 0, 'CF': 0}
        self.window.app.main_window.handler.exams = {'ON': [None]*3, 'CN': [None]*3, 'OF': [None]*3, 'CF': [None]*3}
        self.window.app.main_window.handler.on_state_changed(self.window.app.main_window.eyes_state.get_children()[0])

        # Hiding the window
        self.window.app.connection_flags['patient'] = True
        self.window.hide()

    def on_patients_tree_button_press_event(self, treeview, event):
        if event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS and event.button == 1:
            selection = treeview.get_selection()
            model, i = selection.get_selected()
            if i == None: #note 3
                return True
            model = treeview.get_model()
            self.patient_cod = model[i][0]
            self.on_load_clicked(self.window.load_button)