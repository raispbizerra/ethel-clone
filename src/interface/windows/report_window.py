# Third party imports
from src.interface.handlers.report_window_handler import Handler
from src.interface.builder import Builder
from gi.repository import Gtk, Gdk, GLib
import gi
gi.require_version('Gtk', '3.0')
# Local imports


class ReportWindow(Gtk.Assistant):
    """This class implements Report Window
    """

    def __init__(self, app):
        # Init Gtk.Window class
        super(ReportWindow, self).__init__(
            title='Report Window', use_header_bar=True, application=app)
        self.set_modal(True)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_icon_from_file('media/logo_small.png')
        self.app = app
        self.set_transient_for(self.app.main_window)

        # Assign builder
        builder = Builder('src/interface/glade/report.glade')

        # Get glade objects
        # Boxes
        self.patient_box = builder.get_object('patient_box')
        self.metrics_box = builder.get_object('metrics_box')
        # TreeViews
        self.patients_treeview = builder.get_object('patients_treeview')
        self.metrics_treeview = builder.get_object('metrics_treeview')
        # Liststores
        self.patients_liststore = builder.get_object('patients_liststore')
        self.metrics_liststore = builder.get_object('metrics_liststore')
        # Checkbuttons
        self.patients_checkbutton = builder.get_object('patients_checkbutton')
        self.metrics_checkbutton = builder.get_object('metrics_checkbutton')

        label = Gtk.Label('Geração de Relatórios do ETHEL')
        self.append_page(label)
        self.set_page_type(label, Gtk.AssistantPageType.INTRO)
        self.set_page_complete(label, True)
        self.append_page(self.patient_box)
        self.set_page_type(self.patient_box, Gtk.AssistantPageType.CONTENT)
        self.set_page_title(self.patient_box, 'Selecionar Pacientes')
        self.append_page(self.metrics_box)
        self.set_page_type(self.metrics_box, Gtk.AssistantPageType.CONFIRM)
        self.set_page_title(self.metrics_box, 'Selecionar Métricas')

        handler = Handler(self)
        builder.connect_signals(handler)
        self.connect('show', handler.on_show)
        self.connect('escape', handler.on_cancel)
        self.connect('cancel', handler.on_cancel)
        self.connect('close', handler.on_close)
        self.connect('delete-event', self.app.on_delete_event)
