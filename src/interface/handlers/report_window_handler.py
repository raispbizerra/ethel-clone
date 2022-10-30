# Default imports
import src.utilities.report as rpt
import src.utilities.calculos as calc
from src.database.static_exam_dao import StaticExamDao
from src.database.patient_dao import PatientDao
from gi.repository import Gtk
import datetime

# Third party imports
import gi
gi.require_version('Gtk', '3.0')

# Local imports

LIMIT = 3


class Handler():
    """This class implements Load Patient Window Handler
    """

    def __init__(self, window):
        self.window = window
        self.patient_dao = PatientDao()
        self.static_exam_dao = StaticExamDao()
        self.fill_metrics()

    def on_show(self, window):
        self.patients = []
        patients = self.patient_dao.list_patients()
        for patient in patients:
            exams = {}
            for condition in ('ON', 'CN', 'OF', 'CF'):
                exams[condition] = self.static_exam_dao.check(
                    patient.cod, condition)
                if len(exams[condition]) >= LIMIT:
                    self.patients.append(patient)
                    break

        self.fill_patients()

    def on_cell_toggled(self, cell_renderer, path):
        if self.window.patients_treeview.get_column(0).cell_get_position(cell_renderer):
            self.window.patients_selection = []
            selection = self.window.patients_selection
            liststore = self.window.patients_liststore
            box = self.window.patient_box
        else:
            self.window.metrics_selection = []
            selection = self.window.metrics_selection
            liststore = self.window.metrics_liststore
            box = self.window.metrics_box

        liststore[path][0] = not liststore[path][0]

        for row in liststore:
            if row[0]:
                selection.append(row[1])
        self.window.set_page_complete(box, bool(selection))

    def on_select_all(self, column):
        button = column.get_widget()
        button.set_active(not button.get_active())
        if column.get_tree_view() == self.window.patients_treeview:
            self.window.patients_selection = []
            liststore = self.window.patients_liststore
            selection = self.window.patients_selection
            box = self.window.patient_box
        else:
            self.window.metrics_selection = []
            selection = self.window.metrics_selection
            liststore = self.window.metrics_liststore
            box = self.window.metrics_box

        for row in liststore:
            row[0] = button.get_active()
            if row[0]:
                selection.append(row[1])
        self.window.set_page_complete(box, bool(selection))

    def fill_metrics(self):
        metrics = [
            'AP_', 'ML_', 'dis_media', 'dis_mediaAP',
            'dis_mediaML', 'dis_rms_total', 'dis_rms_AP',
            'dis_rms_ML', 'totex_total', 'totex_AP', 'totex_ML',
            'mvelo_total', 'mvelo_AP', 'mvelo_ML', 'amplitude_total',
            'amplitude_AP', 'amplitude_ML'
        ]
        self.window.metrics_liststore.clear()
        # Fill liststore
        for metric in metrics:
            self.window.metrics_liststore.append((False, metric))

    def fill_patients(self):
        self.window.patients_liststore.clear()
        for patient in self.patients:
            self.window.patients_liststore.append(
                (False, patient.cod, patient.name))

    def on_close(self, window):

        for pat_cod in self.window.patients_selection:
            report = {'ON': [], 'CN': [], 'OF': [], 'CF': []}
            for condition in report.keys():
                exams = self.static_exam_dao.check(pat_cod, condition)[:LIMIT]
                for exam in exams:
                    metrics_ = calc.computes_metrics(exam.aps, exam.mls)
                    metrics = {}
                    for m in self.window.metrics_selection:
                        metrics[m] = metrics_[m]
                    report[condition].insert(0, metrics)

            date = datetime.date.today().isoformat()
            name = self.patient_dao.read_patient(pat_cod).name
            rpt.generate_report(name, report, date)

        window.hide()

    def on_cancel(self, window):
        window.hide()
