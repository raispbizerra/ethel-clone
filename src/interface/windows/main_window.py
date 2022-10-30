# Third party imports
from src.interface.handlers.main_window_handler import Handler
from src.interface.builder import Builder
from gi.repository import Gtk, Gdk
import gi
gi.require_version('Gtk', '3.0')

# Local imports


class MainWindow(Gtk.ApplicationWindow):
    """This class implements Main Window
    """

    def __init__(self, app):
        # Init Gtk.ApplicationWindow class
        super(MainWindow, self).__init__(title='ETHEL', application=app)
        self.set_decorated(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_icon_from_file('media/logo_small.png')
        self.app = app

        # Assign builder
        builder = Builder('src/interface/glade/main_window.glade')

        # Get glade objects
        # Boxes
        box = builder.get_object('box')
        self.static_exam_box = builder.get_object('static_exam_box')
        self.dynamic_exam_box = builder.get_object('dynamic_exam_box')
        self.exams_list = builder.get_object('exams_list')
        # Grids
        self.los_grid = builder.get_object('los_grid')
        self.metrics_grid = builder.get_object('metrics_grid')
        self.exam_grid = builder.get_object('exam_grid')
        # Buttons
        self.start_static_exam_button = builder.get_object(
            'start_static_exam_button')
        self.save_static_exam_button = builder.get_object(
            'save_static_exam_button')
        self.start_dynamic_exam_button = builder.get_object(
            'start_dynamic_exam_button')
        self.save_dynamic_exam_button = builder.get_object(
            'save_dynamic_exam_button')
        self.load_static_exam_button = builder.get_object(
            'load_static_exam_button')
        self.load_dynamic_exam_button = builder.get_object(
            'load_dynamic_exam_button')
        # ButtonBoxes
        self.eyes_state = builder.get_object('eyes_state')
        self.foam_state = builder.get_object('foam_state')
        # Labels
        self.statusbar = builder.get_object('statusbar')
        self.patient_label = builder.get_object('patient_label')
        self.battery_label = builder.get_object('battery_label')
        self.connection_label = builder.get_object('connection_label')
        # Menu Itens
        self.edit_patient = builder.get_object('edit_patient')
        self.edit_device = builder.get_object('edit_device')
        self.calibrate_device = builder.get_object('calibrate_device')
        self.disconnect_device = builder.get_object('disconnect_device')
        # Progressbars
        self.progressbar = builder.get_object('progressbar')
        # ScroledWindows
        self.sw0 = builder.get_object('sw0')
        self.sw1 = builder.get_object('sw1')
        self.sw2 = builder.get_object('sw2')
        # Images
        self.connection_image = builder.get_object('connection_image')
        # Entrys
        self.points_entry = builder.get_object('points_entry')
        # Paneds
        self.paned = builder.get_object('paned')
        # Notebooks
        self.notebook = builder.get_object('notebook')
        self.static_notebook = builder.get_object('static_notebook')
        # Liststores
        self.static_list_store = builder.get_object('static_list_store')
        self.dynamic_list_store = builder.get_object('dynamic_list_store')
        # TreeViews
        self.static_exams_tree = builder.get_object('static_exams_tree')
        # Dialogs
        self.dialog = builder.get_object('dialog')
        self.dialog.connect('delete-event', self.app.on_delete_event)
        self.dialog.set_transient_for(self)
        self.add(box)

        # Assign builder
        self.handler = Handler(self)
        builder.connect_signals(self.handler)

        # Set fullscreen
        self.fullscreen()

        # Connect signals
        self.connect('show', self.handler.on_show)
        self.connect('destroy', self.app.on_quit)

        self.verify_connection = self.handler.verify_connection
